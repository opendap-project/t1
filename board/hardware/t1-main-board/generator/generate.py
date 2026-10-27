#!/usr/bin/env python3
"""Generate the T1 main board's KiCad 10 schematic project from the board's data.

Run from anywhere with Python 3.11 or later:

    python3 hardware/t1-main-board/generator/generate.py

Inputs (all in this repository): the pinout (hardware/pinout/pinout-v1.csv), the net classes
(hardware/rules/netclasses.toml), the variant files (hardware/variants/*.toml), kicad-lib (submodule
hardware/lib/opendap) and the block definitions in this folder (blocks_*.py, parts.py), whose
values cite the board documents and data sheets. Outputs, written into hardware/t1-main-board/:
the .kicad_pro, every .kicad_sch, sym-lib-table, fp-lib-table, the [schematic] table of
t1-main-board.craft.toml (the craft check configuration), and the project-local library in hardware/lib/.
Edit the generator, never the outputs, and run it again.
"""

from __future__ import annotations

import glob
import os
import sys
import tomllib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import blocks_audio  # noqa: E402
import blocks_charger  # noqa: E402
import blocks_faceplate  # noqa: E402
import blocks_io  # noqa: E402
import blocks_should  # noqa: E402
import blocks_mem  # noqa: E402
import blocks_power  # noqa: E402
import blocks_radio  # noqa: E402
import blocks_soc  # noqa: E402
import blocks_usb  # noqa: E402
import localparts  # noqa: E402
import overview  # noqa: E402
from draw import finalize_tables, local_flags  # noqa: E402
from library import HW, PROJECT as PROJECT_DIR  # noqa: E402
from project import FP_TABLE, SYM_TABLE, Project, netclasses, project_file  # noqa: E402
from sch import RAILS, snap  # noqa: E402

# Net-class assignment patterns, per class of hardware/rules/netclasses.toml. Only nets drawn today
# are assigned; the other classes exist in the project and get their patterns with their blocks.
PATTERNS = {
    "PWR_BAT": ["VBAT", "*BAT_F", "*BAT_P", "BAT_N"],
    "BAT_SENSE": ["*BAT_MID", "*BAT_NTC"],
    "PWR_VSYS": ["VSYS"],
    "PWR_VBUS": ["USBC_VBUS", "VBUS_CHG", "*CHG_PMID"],
    "PWR_5V1": ["*P5V1_SRC", "*P5V1_LIM"],
    "PWR_HAT5V": ["HAT_5V"],
    "SW_NODE": ["*_SW"],
    "DDR_50SE": ["*DDR_DQ?_?", "*DDR_DQ??_?", "*DDR_DM?_?", "*DDR_A?_?", "*DDR_CS0_?_N", "*DDR_CKE0_?",
                 "*DDR_ODT0_CA_?"],
    "DDR_100D": ["*DDR_DQS?P_?", "*DDR_DQS?N_?", "*DDR_CLKP_?", "*DDR_CLKN_?"],
    "EMMC_SD_50SE": ["*EMMC_CLK*", "*EMMC_CMD*", "*EMMC_D?", "*EMMC_DS", "*SD_CLK", "*SD_CMD", "*SD_D?", "*SD_CLK_M", "*SD_CMD_M", "*SD_D?_M", "SD_CLK_C", "SD_CMD_C", "SD_D?_C"],
    "USB2_90D": ["*USBC_DP", "*USBC_DM", "*USBC_DP_C", "*USBC_DM_C", "*HAT_USB3_DP", "*HAT_USB3_DM", "*HAT_DP_C",
                 "*HAT_DM_C"],
    "USB3_90D": ["*HAT_USB3_SS*", "*HAT_SSTX_C_?"],
    "RF_50SE": ["*WL_ANT?", "*WL_ANT?_J", "*WL_BT_IN"],
    "MIPI_100D": ["*FP_DSI_*"],
    "PWR_AMP": ["AUDIO_P7V0", "AUDIO_N7V0", "*HPA_P6V0*", "*HPA_N6V0*", "*HPA_P6_A", "*HPA_P6_B", "*HPA_N6_A",
                "*HPA_N6_B"],
    "PWR_AUDIO": ["DAC1_VA", "DAC2_VA", "DAC_VP", "DAC_DIG_1V8", "AUDIO_2V2", "MCLK_3V1", "MCLK_1V8",
                  "*DAC?_VA_IN", "*MCLK3V1_IN", "*MCLK1V8_IN"],
    "AUDIO_ANALOG": ["*DAC?_AOUT_?", "*HPS_*", "*HPB_*", "*HPSE_L", "*HPSE_R", "*HPBAL_?_?"],
    "AUDIO_REF": ["*HPSE_REF_?"],
    "MCLK_50SE": ["*MCLK_OSC", "*MCLK_L", "*MCLK_R", "*DIV?_Q"],
    "I2S_50SE": ["*I2S_BCLK", "*I2S_LRCK", "*I2S_SDO0", "*DAC?_SCLK", "*DAC?_LRCK", "*DAC?_SDIN"],
}


def ddr_order():
    """Sheet-pin order for the LPDDR4X interface: channel A, then B, each CA then byte lanes."""
    order = {}
    k = 0
    for ch in ("A", "B"):
        names = [f"DDR_A{i}_{ch}" for i in range(6)] + [f"DDR_CS0_{ch}_N", f"DDR_CKE0_{ch}", f"DDR_ODT0_CA_{ch}",
                                                       f"DDR_CLKP_{ch}", f"DDR_CLKN_{ch}"]
        for lane in (0, 1):
            names += [f"DDR_DQ{lane * 8 + i}_{ch}" for i in range(8)]
            names += [f"DDR_DM{lane}_{ch}", f"DDR_DQS{lane}P_{ch}", f"DDR_DQS{lane}N_{ch}"]
        for nm in names:
            order[nm] = (0, k)
            k += 1
    order["DDR_RESET_N"] = (0, k)
    k += 1
    for nm in ["EMMC_CLK", "EMMC_CMD"] + [f"EMMC_D{i}" for i in range(8)] + ["EMMC_RST_N", "EMMC_DS"]:
        order[nm] = (1, k)
        k += 1
    return order


def bus_aliases():
    """Project bus aliases (CRAFT-84): each LPDDR4X channel, the eMMC bus, each I2C bus and the
    control lines between the SoC and each block cross the hierarchy as one bus; inside a sheet
    the members keep local labels at their pins. DDR_RESET_N, the DRAM's one reset, rides with
    channel A."""
    order = sorted(ddr_order().items(), key=lambda kv: kv[1])
    return {"DDR_CHA": [n for n, (g, _) in order if g == 0 and n.endswith("_A") or n.endswith("_A_N")]
            + ["DDR_RESET_N"],
            "DDR_CHB": [n for n, (g, _) in order if g == 0 and n.endswith("_B") or n.endswith("_B_N")],
            "EMMC": [n for n, (g, _) in order if g == 1],
            "I2C0": ["I2C0_SCL", "I2C0_SDA"],
            "I2C1": ["I2C1_SCL", "I2C1_SDA"],
            "I2C2": ["I2C2_SCL", "I2C2_SDA"],
            "AUDIO_I2S": ["I2S_BCLK", "I2S_LRCK", "I2S_SDO0", "DSD_L", "DSD_R"],
            "AUDIO_CTL": ["DAC_I2C_SCL", "DAC_I2C_SDA", "DAC_RST_N", "DAC_INT_N", "DAC_VP_EN", "DAC_DIG_EN",
                          "AUDIO_LN_EN", "MCLK441_EN", "MCLK48_EN", "MCLK_DIV_RUN", "HPA_RAIL_EN", "HPA_LDO_EN",
                          "HPA_SE_EN", "HPA_BAL_EN"],
            "HP_SE": ["HPSE_L", "HPSE_R", "HPSE_REF_L", "HPSE_REF_R"],
            "DAC_L_OUT": ["DACL_AOUT_P", "DACL_AOUT_N"],
            "DAC_R_OUT": ["DACR_AOUT_P", "DACR_AOUT_N"],
            "HP_BAL": ["HPBAL_L_P", "HPBAL_L_N", "HPBAL_R_P", "HPBAL_R_N"],
            "PMIC_CTL": ["CLK32K_PMIC", "PMIC_INT_N", "PMIC_SLEEP", "SOC_RESET_N"],
            "USB": ["USBC_DP", "USBC_DM", "USBC_VBUSDET", "HAT_USB3_SSTX_P", "HAT_USB3_SSTX_N", "HAT_USB3_SSRX_P",
                    "HAT_USB3_SSRX_N", "HAT_USB3_DP", "HAT_USB3_DM"],
            "IO_IRQ": ["CHG_INT_N", "USBC_INT_N", "HAT_PD_INT_N", "EXP_INT_N", "IMU_INT1"],
            "IMON": ["EFUSE_VBUS_IMON", "EFUSE_HAT5V_IMON"],
            "WL": ["WL_SD_CLK", "WL_SD_CMD", "WL_SD_D0", "WL_SD_D1", "WL_SD_D2", "WL_SD_D3", "BT_UART_TXD",
                   "BT_UART_RXD", "BT_UART_CTS", "BT_UART_RTS", "WL_WAKE_OUT", "BT_WAKE_OUT", "BT_WAKE_IN"],
            "FP": [f"FP_DSI_{l}_{p}" for l in ("CLK", "D0", "D1", "D2", "D3") for p in ("P", "N")]
            + ["FP_I2C_SCL", "FP_I2C_SDA", "FP_SPI_SCLK", "FP_SPI_MOSI", "FP_SPI_MISO", "FP_SPI_CS_N", "FP_DBI_DC",
               "FP_TP_INT", "FP_TP_RST_N", "FP_LCD_RST_N", "FP_LCD_TE", "FP_HID_INT_N", "FP_ALS_INT_N", "BL_PWM",
               "MIC_EN", "PDM_CLK0", "PDM_DATA0"],
            "EXP_IO": ["FP_IO_EN", "HAT_VBUS_DISCH", "HAT5V_EN", "USB_SRC_ON", "HAPTIC_EN", "NFC_PWR_EN", "WL_PWR_EN",
                       "WL_PD_HOLD_N", "HP_DET_SE", "HP_DET_BAL", "FP_DET_N", "FP_GPIO0", "FP_GPIO1",
                       "EFUSE_HAT5V_FLT_N", "EFUSE_5V_FLT_N", "EFUSE_VBUS_FLT_N"],
            "SDMMC0": ["SD_CLK", "SD_CMD", "SD_D0", "SD_D1", "SD_D2", "SD_D3", "SD_DET_N"],
            "SPK_I2S": ["SPK_BCLK", "SPK_LRCK", "SPK_SDIN", "SPK_SD_MODE"],
            # the root's SoC symbol stays within its row: control lines of the I2C2 and button blocks
            "KEYS": ["PWRON_N", "SARADC_VOLUP", "VOLDN_N", "ACTION_BTN_N"],
            "NFC": ["NFC_FD_N", "NFC_VEN", "NFC_DWL_REQ", "NFC_IRQ"],
            "TPM": ["TPM_RST_N", "TPM_PIRQ_N"],
            "RP": ["RP_UART_TX", "RP_UART_RX", "RP_IRQ", "RP_RUN", "RP_SWCLK", "RP_SWDIO", "RP_BOOTSEL_DRV",
                   "RP_PWR_EN", "RP_USB_DP", "RP_USB_DM"]}


def base_variant():
    """The name of the base design's variant: the variant file of kind "full" (CRAFT-147). The title
    block shows it as Variant on a plot of the base design (kicad-lib's drawing sheet reads the
    project text variable OPENDAP_BASE_VARIANT when KiCad's ${VARIANT} is empty)."""
    for p in sorted(glob.glob(os.path.join(HW, "variants", "*.toml"))):
        with open(p, "rb") as fh:
            d = tomllib.load(fh)
        if d.get("kind") == "full":
            return d["name"]
    raise SystemExit("generator: no variant file of kind \"full\" in hardware/variants/")


def variant_files():
    out = {}
    for p in sorted(glob.glob(os.path.join(HW, "variants", "*.toml"))):
        with open(p, "rb") as fh:
            d = tomllib.load(fh)
        if d.get("kind") != "full":       # the base design is the full variant (CRAFT-147)
            out[d["name"]] = d
    return out


def main():
    localparts.write()
    variants = variant_files()
    proj = Project()
    proj.order = ddr_order()
    proj.aliases = bus_aliases()
    root = proj.sheet("t1-main-board.kicad_sch", "root", "Block diagram",
                      "The main board's blocks in signal-flow order, with the power and interconnect overviews", "A3")
    power = proj.sheet("power.kicad_sch", "power", "Power overview",
                       "Rails of the main board drawn so far: source, switch, consumers, net class and measurement", "A3")
    inter = proj.sheet("interconnect.kicad_sch", "interconnect", "Interconnect overview",
                       "External connections of the main board: one pin map per connector", "A4")
    charger, ckids, gauge = blocks_charger.sheets(proj)
    vsys_lv = blocks_power.sheet_vsys_lv(proj)
    v3v3 = blocks_power.sheet_3v3(proj)
    pmic = blocks_power.sheet_pmic(proj)
    vcpu = blocks_power.sheet_vdd_cpu(proj)
    soc, subs, soc_sym, nets = blocks_soc.build(proj, variants)
    ddr = blocks_mem.sheet_lpddr4x(proj)
    emmc = blocks_mem.sheet_emmc(proj)
    audio, akids, jse, jbal = blocks_audio.sheets(proj)
    usbc, p5v1, vout, hat5v, hats = blocks_usb.sheets(proj)
    radio, rkids, ant = blocks_radio.sheets(proj)
    fpc, fpd, fpb, fpk, mic = blocks_faceplate.sheets(proj)
    exp, bid, imu, spk, sd = blocks_io.sheets(proj)
    hap, tpm, tag, rdr, rp = blocks_should.sheets(proj)
    btn = blocks_io.sheets_buttons(proj)

    # the root in reading rows (CRAFT-111): overviews in the top row; then power blocks as power
    # flows; then the SoC and its memories. A list stacks its sheets in one column.
    rows = [("Overviews, then the power blocks in the order power flows",
             [power, inter, charger, gauge, vsys_lv, v3v3, pmic, vcpu]),
            ("SoC, memory and the coprocessor; audio, from the DACs to the jacks", [soc, [ddr, emmc], audio, [jse, jbal], rp]),
            ("USB ports (the 5.1 V source, USB-C, the HAT port) and the radio",
             [p5v1, vout, usbc, hats, hat5v, radio, ant]),
            ("Faceplate interface; control, storage and sensors", [[fpc, fpd, fpk], [fpb, mic, spk], [exp, bid, sd], [imu, hap, tpm], [tag], [rdr], [btn]])]

    kids = {charger: [ckids[k] for k in blocks_charger.KIDS], soc: [subs[n] for n, *_ in blocks_soc.SUBS],
            audio: [akids[k] for k in blocks_audio.reading_order()],
            rp: [rp.kids["rp2354-core"], rp.kids["rp2354-power"]], radio: [rkids[k] for k in blocks_radio.KIDS]}
    # page numbers follow the root's reading order, each parent's sub-sheets right after it
    reading = [root] + [x for b in overview.reading_order(rows) for x in [b] + kids.get(b, [])]
    proj.number(reading)
    for s in proj.sheets:
        s.base = int(s.page) * 100
    for s in subs.values():            # blk.soc's sub-sheets share the SoC's hundred-block
        s.base, s.counters = soc.base, soc.counters
    for s in rp.kids.values():       # one RP2354A reference over its sub-sheets, as the SoC's
        s.base, s.counters = rp.base, rp.counters

    blocks_charger.draw_parent(charger)
    blocks_charger.draw_input(ckids["charger-input"], variants)
    blocks_charger.draw_core(ckids["charger-core"], variants)
    blocks_charger.draw_battery(ckids["charger-battery"], variants)
    blocks_charger.draw_gauge(gauge, variants)
    blocks_power.draw_vsys_lv(vsys_lv, variants)
    blocks_power.draw_3v3(v3v3, variants)
    blocks_power.draw_pmic(pmic, variants)
    blocks_power.draw_vdd_cpu(vcpu, variants)
    blocks_soc.draw(proj, soc, subs, soc_sym, nets, variants)
    blocks_mem.draw_lpddr4x(ddr, variants)
    blocks_mem.draw_emmc(emmc, variants)
    blocks_audio.draw_parent(audio)
    blocks_audio.draw_supply(akids["audio-supply"], variants)
    blocks_audio.draw_mclk(akids["mclk"], variants)
    blocks_audio.draw_dac(akids["dac-l"], variants, "L")
    blocks_audio.draw_dac(akids["dac-r"], variants, "R")
    blocks_audio.draw_rails_parent(akids["hpa-rails"])
    blocks_audio.draw_rails(akids["hpa-rails-pre"], variants)
    blocks_audio.draw_ldos(akids["hpa-rails-ldo"], variants)
    blocks_audio.draw_stage(akids["hpa-se"], variants, "se")
    blocks_audio.draw_bal_parent(akids["hpa-bal"], variants)
    blocks_audio.draw_stage(akids["hpa-bal-l"], variants, "bal", "L")
    blocks_audio.draw_stage(akids["hpa-bal-r"], variants, "bal", "R")
    blocks_audio.draw_jack_se(jse, variants)
    blocks_audio.draw_jack_bal(jbal, variants)
    blocks_usb.draw_pwr_5v1(p5v1, variants)
    blocks_usb.draw_usbc(usbc, variants)
    blocks_usb.draw_usb_vbus_out(vout, variants)
    blocks_usb.draw_hat_5v(hat5v, variants)
    blocks_usb.draw_hat_signals(hats, variants)
    blocks_radio.draw_parent(radio)
    blocks_radio.draw_module(rkids["radio-module"], variants)
    blocks_radio.draw_power(rkids["radio-power"], variants)
    blocks_radio.draw_antennas(ant, variants)
    blocks_faceplate.draw_connector(fpc, variants)
    blocks_faceplate.draw_display(fpd, variants)
    blocks_faceplate.draw_backlight(fpb, variants)
    blocks_faceplate.draw_controls(fpk, variants)
    blocks_faceplate.draw_mic(mic, variants)
    blocks_io.draw_expander(exp, variants)
    blocks_io.draw_board_id(bid, variants)
    blocks_io.draw_microsd(sd, variants)
    blocks_io.draw_imu(imu, variants)
    blocks_io.draw_speaker(spk, variants)
    blocks_should.draw_haptics(hap, variants)
    blocks_should.draw_tpm(tpm, variants)
    blocks_should.draw_tag(tag, variants)
    blocks_io.draw_buttons(btn, variants)
    blocks_should.draw_reader(rdr, variants)
    blocks_should.draw_rp2354(rp, variants)
    for s in proj.sheets:
        if s.role.startswith("blk."):
            finalize_tables(s)
            local_flags(s)
    overview.draw_power(power)
    overview.draw_interconnect(inter)

    for s in [power, inter, charger, gauge, vsys_lv, v3v3, pmic, vcpu, soc, ddr, emmc, audio, jse, jbal,
              p5v1, usbc, vout, hat5v, hats, radio, ant, fpc, fpd, fpb, fpk, mic, exp, bid, sd, imu, spk, hap, tpm, tag, rdr, btn, rp]:
        root.child(s, 0, 0, w=25.4)
    for name, *_ in blocks_soc.SUBS:
        soc.child(subs[name], 0, 0, w=76.2)
    for k in blocks_radio.KIDS:
        radio.child(rkids[k], 0, 0, w=50.8)
    for k in blocks_charger.KIDS:
        charger.child(ckids[k], 0, 0, w=50.8)
    for k in ("rp2354-core", "rp2354-power"):
        rp.child(rp.kids[k], 0, 0, w=50.8)
    for k in blocks_audio.KIDS:
        audio.child(akids[k], 0, 0, w=50.8)
    for k in blocks_audio.RAIL_KIDS:
        akids["hpa-rails"].child(akids[k], 0, 0, w=50.8)
    for k in blocks_audio.BAL_KIDS:
        akids["hpa-bal"].child(akids[k], 0, 0, w=50.8)
    proj.resolve()
    proj.apply_aliases()
    auto_sides(proj, root, soc, [ddr, emmc])
    proj.layout_children()
    overview.layout_rows(root, rows)
    overview.check_reading(root)
    overview.layout_column(soc, start=27.94, x=25.4, y_max=160.0)
    overview.layout_column(radio, start=27.94, x=25.4, y_max=160.0)
    overview.layout_column(charger, start=27.94, x=25.4, y_max=160.0)
    overview.layout_column(rp, start=27.94, x=25.4, y_max=160.0)
    overview.layout_column(audio, start=27.94, x=25.4, y_max=160.0)
    overview.layout_column(akids["hpa-rails"], start=27.94, x=25.4, y_max=160.0)
    overview.layout_column(akids["hpa-bal"], start=27.94, x=25.4, y_max=160.0)
    proj.assign_paths()
    overview.draw_root(root)

    for s in proj.sheets:
        with open(os.path.join(PROJECT_DIR, s.name), "w", encoding="utf-8") as fh:
            fh.write(proj.render(s))
    classes, pats = netclasses(os.environ.get("T1_NETCLASSES") or os.path.join(HW, "rules", "netclasses.toml"),
                               PATTERNS)
    with open(os.path.join(PROJECT_DIR, "t1-main-board.kicad_pro"), "w", encoding="utf-8") as fh:
        fh.write(project_file(classes, pats, "${KIPRJMOD}/../lib/opendap/drawing-sheets/opendap.kicad_wks",
                              proj.aliases, base_variant()))
    with open(os.path.join(PROJECT_DIR, "sym-lib-table"), "w", encoding="utf-8") as fh:
        fh.write(SYM_TABLE)
    with open(os.path.join(PROJECT_DIR, "fp-lib-table"), "w", encoding="utf-8") as fh:
        fh.write(FP_TABLE)
    write_craft_config(proj)
    # the sheet zones (CRAFT-170, -174): groups, tables, notes, title block and frame apart
    import overlaps
    bad = [(s.name, f) for s in proj.sheets for f in overlaps.zones(os.path.join(PROJECT_DIR, s.name))]
    for name, f in bad:
        print(f"zones: {name}: {f}")
    if bad:
        raise SystemExit(f"generator: {len(bad)} zone collision(s)")
    print(f"generated {len(proj.sheets)} sheets, {sum(1 for _ in proj.parts)} placed units")


def auto_sides(proj, root, soc, memories):
    """On the root, a bidirectional or passive sheet pin faces the block it connects to. The SoC
    keeps its right edge for the memory buses, wired pin for pin; its other links go left."""
    xs = {cs.sheet: cs.x for cs in root.children}
    mem_nets = {p[0] for cs in root.children if cs.sheet in memories for p in cs.pins}
    for cs in root.children:
        for pin in cs.pins:
            net, shape = pin[0], pin[1]
            if shape in ("bidirectional", "passive") and pin[2] != "top":
                if cs.sheet is soc:
                    pin[2] = "right" if net in mem_nets else "left"
                    continue
                partners = [o for o in root.children if o is not cs and any(p[0] == net for p in o.pins)]
                if partners:
                    pin[2] = "right" if max(xs[o.sheet] for o in partners) > cs.x else "left"


MARK = "# ---- [schematic]: written by generator/generate.py from the drawn sheets; edit the generator, not below."


def write_craft_config(proj):
    """The [schematic] table of the craft check configuration (rails and each block's interface,
    CRAFT-85, -112), written into t1-main-board.craft.toml below MARK. Everything above MARK (the
    target level and the mirrored blocks) is kept as written by hand."""
    path = os.path.join(PROJECT_DIR, "t1-main-board.craft.toml")
    with open(path, encoding="utf-8") as fh:
        head = fh.read().split(MARK)[0].rstrip("\n")
    lines = [head, "", MARK, "[schematic]",
             "rails = [" + ", ".join(f'"{r}"' for r in RAILS) + "]",
             'netclasses = "../rules/netclasses.toml"', ""]
    for s in proj.sheets:
        if s.role.startswith("blk.") and s.parent is not None:
            cs = next(c for c in s.parent.children if c.sheet is s)
            names = [p[0] for p in cs.pins]
            lines += ["[[schematic.block]]", f'id = "{s.role}"',
                      "interface = [" + ", ".join(f'"{x}"' for x in names) + "]", ""]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

if __name__ == "__main__":
    main()
