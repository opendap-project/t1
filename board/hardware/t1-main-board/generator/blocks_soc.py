"""blk.soc: the RK3566, drawn as one parent sheet and one sub-sheet per IO domain or function.

Every ball takes the net of pinout v1 (hardware/pinout/pinout-v1.csv); unused balls take a
no-connect flag. Support parts that set an absent state or a strap sit here, on the host side
(feature-blocks spec §1)."""

from __future__ import annotations

import library
from draw import corner_notes, decouple, gnd, vpart, flow_units, link, link_variants, notes, rail_table, iface_table, two_pin_h, two_pin_v
from parts import PARTS, fields
import pinout
from sch import snap, snap_up

SOC_FIELDS = {"Block": "blk.soc", "Constraints": "PCB-I-05"}

SUBS = [
    # name, role, title, purpose, units
    ("soc-pmuio", "blk.soc-pmuio", "SoC: PMU IO domains, clock, reset and SARADC",
     "RK3566 units on PMUIO0-2 and the SARADC, with the 24 MHz crystal, reset, straps and bus pull-ups", [4, 5, 19]),
    ("soc-ddr", "blk.soc-ddr", "SoC: LPDDR4X interface",
     "RK3566 DDR PHY units: channels A and B, reset and ZQ calibration", [1, 2, 3]),
    ("soc-vccio-a", "blk.soc-vccio-a", "SoC: VCCIO1 to VCCIO4",
     "RK3566 IO banks VCCIO1-4: eMMC, microSD, the radio SDIO and UART, and spare GPIO", [6, 7, 8, 9]),
    ("soc-vccio-b", "blk.soc-vccio-b", "SoC: VCCIO5 to VCCIO7",
     "RK3566 IO banks VCCIO5-7: faceplate and audio lines", [10, 11, 12]),
    ("soc-phy", "blk.soc-phy", "SoC: USB, PCIe, MIPI, HDMI and eDP PHYs",
     "RK3566 PHY units: USB 2.0 and USB 3, multi-PHY, MIPI CSI RX, MIPI DSI TX0 and TX1, HDMI and eDP", [13, 14, 15, 16, 17, 18]),
    ("soc-power", "blk.soc-power", "SoC: supplies and decoupling",
     "RK3566 supply units with the decoupling of the hardware design guide, grouped by rail", [20, 21, 22]),
    ("soc-ground", "blk.soc-ground", "SoC: ground",
     "RK3566 ground balls", [23, 24, 25]),
]

def build(proj, variants):
    soc_sym = library.load("Rockchip", "RK3566")
    pins = pinout.load()
    nets = {ball: d["net"] for ball, d in pins.items()}
    parent = proj.sheet("soc.kicad_sch", "blk.soc", "SoC", "The RK3566 application processor, one sub-sheet per IO domain or function", "A3")
    subs = {}
    for name, role, title, purpose, units in SUBS:
        s = proj.sheet(name + ".kicad_sch", role, title, purpose, "A3")
        s.units = units
        subs[name] = s
    return parent, subs, soc_sym, nets


def draw(proj, parent, subs, soc_sym, nets, variants):
    ref = parent.next_ref("U")
    flds = dict(SOC_FIELDS)
    flds["Block"] = "blk.soc"
    corner_notes(parent, [
        "1. Function: the RK3566 SoC (board ADR 0003), drawn as one sub-sheet per IO domain or function",
        "   (CRAFT-126): each sub-sheet holds the RK3566 units of that domain and their support parts.",
        "2. Absent state: not applicable. No variant omits the SoC; another SoC is another board (RFC 0011 §3).",
        "3. Sub-sheet IDs (blk.soc-*) are sheets of blk.soc: their parts carry Block = blk.soc-* so the",
        "   craft check can resolve them; the catalog block is blk.soc (feature-blocks spec #1).",
        "4. Constraints: PCB-I-05 (LPDDR4X), PCB-I-06 (eMMC); decoupling per RK3566 HDG 1.1 pp. 35-41.",
        "5. Decisions: ADR 0003 (RK3566), ADR 0021 (vdd_cpu), ADR 0022 (single-rank LPDDR4X).",
    ])
    for name, role, title, purpose, units in SUBS:
        s = subs[name]
        f = dict(flds)
        f["Block"] = role
        W = 420.0
        bottom = flow_units(s, soc_sym, ref, units, nets, f, 25.4, 30.48 if name not in ("soc-power",) else 38.1,
                            W - 25.4, value="RK3566")
        s.circuit_bottom = bottom
        globals()["_" + name.replace("-", "_")](s, bottom, variants)
    return ref


# ---------------------------------------------------------------------- sub-sheets

def _soc_pmuio(s, y0, variants):
    blk = s.block
    s.bus_row = 8               # fourteen bus ports: two rows above the tables, clear of the SARADC group
    y = max(y0 + 12.7, 130.81)
    x = 30.48
    s.group_box("24 MHz crystal (HDG 1.1 pp. 16-17)", 25.4, y - 5.08, 104.14, 45.72)
    ysym = library.load("OpenDAP_Device", "Crystal_GND24")
    yref = s.next_ref("Y")
    p = PARTS["Y_24M"]
    pl = s.place(ysym, yref, 76.2, y + 17.78, fields=fields("Y_24M", blk), value=p["value"],
                 ref_at=(80.01, y + 12.7), val_at=(80.01, y + 24.13))
    s.connect(pl, "1", "XIN24M")
    s.connect(pl, "3", "XTAL24M_OUT")
    s.connect(pl, "2", "GND")
    s.connect(pl, "4", "GND")
    two_pin_h(s, "R_1M", 50.8, y + 5.08, "XIN24M", "XOUT24M", blk)
    two_pin_h(s, "R_22", 101.6, y + 5.08, "XOUT24M", "XTAL24M_OUT", blk)
    two_pin_v(s, "C_18p_0402", 45.72, y + 27.94, "XIN24M", "GND", blk)
    two_pin_v(s, "C_18p_0402", 116.84, y + 27.94, "XTAL24M_OUT", "GND", blk)

    xr = 142.24
    s.group_box("Reset and boot strap", xr - 5.08, y - 5.08, 63.5, 45.72)
    # reset node: pull-up from the top, 100 nF to ground, the label to the right (HDG pp. 17-18)
    rt, rb = vpart(s, "R_10k", xr + 15.24, y + 7.62)
    s.power("vcc3v3_pmu", *rt)
    yn = y + 15.24
    ct, cb = vpart(s, "C_100n_0402", xr + 5.08, y + 22.86)
    s.wire(rb, (xr + 15.24, yn))
    s.wire(ct, (xr + 5.08, yn), (xr + 25.4, yn))
    s.junction(xr + 15.24, yn)
    s.point("SOC_RESET_N", xr + 25.4, yn, "right", "pas")
    gnd(s, *cb)
    two_pin_v(s, "R_10k", xr + 48.26, y + 7.62, "vcc3v3_pmu", "FLASH_VOL_SEL", blk)

    xp = 213.36
    pulls = [("R_2k2", "vcca1v8_pmu", "I2C0_SCL"), ("R_2k2", "vcca1v8_pmu", "I2C0_SDA"),
             ("R_2k2", "vcca1v8_pmu", "I2C1_SCL"), ("R_2k2", "vcca1v8_pmu", "I2C1_SDA"),
             ("R_2k2", "vcca1v8_pmu", "I2C2_SCL"), ("R_2k2", "vcca1v8_pmu", "I2C2_SDA"),
             ("R_4k7", "vcca1v8_pmu", "CLK32K_PMIC"), ("R_10k", "vcc3v3_pmu", "PMIC_INT_N"),
             ("R_4k7", "vcca1v8_pmu", "ACTION_BTN_N"), ("R_4k7", "vcca1v8_pmu", "CHG_INT_N"),
             ("R_4k7", "vcca1v8_pmu", "USBC_INT_N"), ("R_4k7", "vcca1v8_pmu", "EXP_INT_N"),
             ("R_4k7", "vcca1v8_pmu", "NFC_FD_N"), ("R_4k7", "vcc3v3_pmu", "HAT_PD_INT_N")]
    s.group_box("Bus and interrupt pull-ups (host side)", xp - 7.62, y - 5.08, 187.96, 76.2)   # rail values inside
    for i, (key, rail, net) in enumerate(pulls):
        cx = xp + (i % 8) * 22.86
        cy = y + 6.35 + (i // 8) * 35.56
        two_pin_v(s, key, cx, cy, rail, net, blk)

    xs = 25.4
    ys = y + 55.88
    s.group_box("SARADC inputs (HDG 1.1 p. 60)", xs, ys - 5.08, 132.08, 40.64)   # ground texts inside
    two_pin_v(s, "R_10k", xs + 7.62, ys + 7.62, "vcca_1v8", "SARADC_VOLUP", blk)
    for i, net in enumerate(["SARADC_VOLUP", "VOLDN_N", "EFUSE_HAT5V_IMON", "EFUSE_VBUS_IMON"]):
        two_pin_v(s, "C_1n_0402", xs + 30.48 + i * 25.4, ys + 22.86, net, "GND", blk)

    corner_notes(s, [
        "1. Function: RK3566 PMUIO0 (crystal), PMUIO1 (3.3 V fixed: reset, PMIC and HAT port interrupts),",
        "   PMUIO2 (1.8 V: I2C0-2, wake inputs, debug UART) and the SARADC (pinout v1 §1, §3).",
        "2. Absent state: not applicable (the SoC is never omitted). The pull-ups here hold every",
        "   open-drain interrupt and bus of the blocks they serve, so those blocks may be unfitted.",
        "3. Crystal: 2 x 18 pF, 1 MΩ, 22 Ω per HDG 1.1 pp. 16-17; the X322524MOB4SI load capacitance",
        "   is UNVERIFIED (BOM v1 line 15), so 18 pF is matched to it at bring-up.",
        "4. Pull-ups: I2C 2.2 kΩ (BOM v1 §5); interrupts 4.7 kΩ (pinout v1 B9); PMIC_INT_N 10 kΩ",
        "   (RK809 DS Fig. 1-1); SOC_RESET_N and FLASH_VOL_SEL 10 kΩ: capture choice, HDG gives none.",
        "5. A net with one pin by design ends in a local label (ERC warning isolated_pin_label).",
        "6. Unless noted: resistors 1 % 0402; capacitors 0402 X7R, C0G where marked.",
    ])
    s.rail_rows = [["vcca_1v8", "4 x 1 nF on VIN0-VIN3", "1 nF per input; 10 kΩ on VIN0 (HDG 1.1 p. 60)"]]


def _soc_ddr(s, y0, variants):
    blk = s.block
    y = y0 + 12.7                # the group title clears the units above
    s.group_box("DDR calibration", 25.4, y - 5.08, 50.8, 30.48)     # the label below inside
    two_pin_v(s, "R_120", 45.72, y + 7.62, "vcc_ddr", "DDR_RZQ", blk)
    corner_notes(s, [
        "1. Function: RK3566 DDR PHY, channels A and B and the common unit (DS 1.1 Table 2-1).",
        "2. Absent state: not applicable (blk.lpddr4x is never omitted).",
        "3. Every LPDDR4X ball goes to the same-named DRAM ball in the Rockchip template order, which",
        "   may not be swapped (HDG 1.1 p. 22; pinout v1 CSV). DDR_RZQ: 120 Ω 1 % to vcc_ddr (HDG p. 25).",
        "4. Rank-1 outputs (CS1, CKE1, ODT1_CA of both channels) take a no-connect flag: the DRAM is single",
        "   rank (board ADR 0022 item 4). DDR_VREFOUT is not used with LPDDR4X (HDG p. 25).",
        "5. Constraints: PCB-I-05 (net classes DDR_50SE, DDR_100D).",
        "6. Net names as pinout v1; active low ends in _N, upper case (CRAFT-84).",
    ])
    s.rail_rows = [["vcc_ddr", "R (ZQ) only", "Decoupling of DDR_VDDQ is on blk.soc-power"]]


def _soc_vccio_a(s, y0, variants):
    blk = s.block
    y = y0 + 12.7                # the group title clears the units above
    s.group_box("Pull-up (pinout v1 B9)", 25.4, y - 5.08, 38.1, 33.02)     # the label below inside
    two_pin_v(s, "R_4k7", 38.1, y + 7.62, "vcc_1v8", "TPM_PIRQ_N", blk)
    corner_notes(s, [
        "1. Function: RK3566 IO banks VCCIO1 (3.3 V), VCCIO2 (1.8 V, eMMC), VCCIO3 (vccio_sd, microSD) and",
        "   VCCIO4 (1.8 V, radio SDIO and UART) (pinout v1 §1).",
        "2. Absent state: not applicable (the SoC is never omitted). Balls with no function take a",
        "   no-connect flag; unused-pin handling per RK3566_PinOut is open (pinout v1 O2).",
        "3. Series parts of HDG 1.1 (22 Ω on SDMMC0, eMMC CLK) sit on the sheets of their blocks.",
        "4. A net with one pin by design ends in a local label (ERC warning isolated_pin_label).",
    ])


def _soc_vccio_b(s, y0, variants):
    import blocks_audio
    # each group starts below the units above its own span (the group title clears them)
    def below(x0, x1):
        return snap(max([b[3] for b in s.unit_boxes if b[0] < x1 and x0 < b[2]] + [30.48]) + 12.7)
    blocks_audio.draw_host(s, below(25.4, 157.48), variants, y_right=below(170.18, 396.24))
    corner_notes(s, [
        "1. Function: RK3566 IO banks VCCIO5 (3.3 V, faceplate), VCCIO6 (vccio6_1v8, audio) and VCCIO7",
        "   (3.3 V, audio clock and amplifier enables) (pinout v1 §1). HATs are USB only (RFC 0014):",
        "   no IO bank carries HAT lines; the freed balls are spare GPIO.",
        "2. Absent state: not applicable (the SoC is never omitted).",
        "3. Audio host side (feature blocks §1): the SN74LVC2G66 isolates I2C2 from both DACs while",
        "   DAC_DIG_1V8 is off (BOM v1 line 133, G2; 0 Ω bypasses DNP), DAC_INT_N pulled up on",
        "   DAC_DIG_1V8, every audio enable and DAC_RST_N pulled down (B9, PCB-A-13; 100 kΩ capture",
        "   choice); DNP 0 Ω RX-clock fallbacks (pinout v1). I2S series parts sit at the DACs.",
        "4. A net with one pin by design ends in a local label (ERC warning isolated_pin_label).",
    ])


def _soc_phy(s, y0, variants):
    corner_notes(s, [
        "1. Function: RK3566 PHY units: MIPI DSI TX0 (faceplate), DSI TX1, HDMI and eDP; DSI1, HDMI",
        "   and eDP are unused in the T1 (pinout v1 O2). Units 13 (USB) and 14 (multi-PHY: USB3 HOST1)",
        "   are placed with blk.usb-c and blk.hat-signals, the blocks that drive their inputs. PCIe and",
        "   unit 15 (CSI RX) have no consumer (RFC 0014: HATs are USB only); their balls are NC.",
        "2. Absent state: not applicable (the SoC is never omitted).",
        "3. USB 2 series resistors (2.2 Ω, HDG 1.1 p. 59) and the USB 3 SSTX AC capacitors sit on the",
        "   sheets of their blocks (blk.usb-c, blk.hat-signals).",
        "4. A net with one pin by design ends in a local label (ERC warning isolated_pin_label).",
    ])


# HDG 1.1 pp. 35-41 (Figs. 2-17 to 2-26), the parts-lib RK3566 sheet: near-SoC decoupling.
SOC_DECOUPLING = [
    ("vdd_cpu", ["C_4u7_0402", "C_4u7_0402", "C_22u_0603", "C_22u_0603"],
     "2 x 4.7 µF 0402 + 22 µF 0603 (HDG Fig. 2-17; ADR 0021 item 3), plus one 22 µF 0603 for the load-release "
     "overshoot under the BRD-049 limit (blk.vdd-cpu note 6); VOS senses at one 22 µF capacitor"),
    ("vdd_logic", ["C_100n_0201", "C_4u7_0402", "C_4u7_0402", "C_4u7_0402", "C_22u_0603"],
     "100 nF 0201, 3 x 4.7 µF 0402, 22 µF 0603 (HDG Fig. 2-18)"),
    ("vdd_gpu", ["C_100n_0201", "C_4u7_0402", "C_22u_0603"], "100 nF 0201, 4.7 µF 0402, 22 µF 0603 (HDG Fig. 2-19)"),
    ("vdd_npu", ["C_100n_0201", "C_22u_0603"], "100 nF 0201, 22 µF 0603 (HDG Fig. 2-20)"),
    ("vcc_ddr", ["C_100n_0201", "C_100n_0201", "C_100n_0201", "C_4u7_0402", "C_10u_0603"],
     "DDR_VDDQ: 3 x 100 nF 0201, 4.7 µF 0402, 10 µF 0603, under the SoC (HDG Fig. 2-26)"),
    ("vcc0v6_ddr", ["C_100n_0201", "C_100n_0201", "C_100n_0201", "C_4u7_0402", "C_4u7_0402"],
     "DDR_VDDQL: 3 x 100 nF 0201, 2 x 4.7 µF 0402, under the SoC (HDG Fig. 2-26)"),
    ("vdda_0v9", ["C_100n_0402", "C_1u_0402"], "SYSPLL_AVDD_0V9: 1 µF + 100 nF (HDG p. 35)"),
    ("vcca_1v8", ["C_100n_0402", "C_1u_0402"], "SYSPLL_AVDD_1V8: 1 µF + 100 nF (HDG p. 35)"),
    ("vcc3v3_sys", ["C_100n_0402"] * 4, "VCCIO1, VCCIO5 (2 balls), VCCIO7: 100 nF per supply ball (HDG p. 32)"),
    ("vcc_1v8", ["C_100n_0402"] * 2, "VCCIO2, VCCIO4: 100 nF per supply ball (HDG p. 32)"),
    ("vccio_sd", ["C_100n_0402"], "VCCIO3: 100 nF (HDG p. 32)"),
    ("vccio6_1v8", ["C_100n_0402"] * 2, "VCCIO6 balls 1L4, 1L5: 100 nF each (HDG p. 32; BOM v1 line 141)"),
    ("vcc3v3_pmu", ["C_100n_0402"], "PMUIO1: 100 nF at the ball (HDG p. 32)"),
    ("vcca1v8_pmu", ["C_100n_0402"] * 2, "PMUIO2 and PMUPLL_AVDD_1V8 (PMUIO0): 100 nF each (HDG p. 32)"),
]


def _soc_power(s, y0, variants):
    blk = s.block
    x, y = 25.4, y0 + 15.24
    rows = []
    col_w = 0
    for rail, keys, req in SOC_DECOUPLING:
        longest = max(max(len(PARTS[k]["value"]), len(PARTS[k].get("spec") or ""), 5) for k in keys)
        pitch = max(10.16, -(-(longest * 1.16 + 3.81) // 2.54) * 2.54)
        width = 5.08 + len(keys) * pitch + 5.08
        if x + width > 254:
            x, y = 25.4, y + 30.48
        refs = []
        decouple(s, rail, keys, x, y, blk, refs_out=refs)
        rows.append([rail, ", ".join(f"{r} {v}" for r, v in refs), req])
        x += width + 2.54
    # vdd_logic measurement link #2 (power tree §4.12): BUCK1 output to the SoC, inside FB1
    yl = snap(y + 35.56)          # its title clears the last row's ground symbols; the group the frame
    link(s, "LINK_H5", 76.2, yl, "VDD_LOGIC_SRC", "vdd_logic", link_variants("LINK_H5", variants),
         title="Link #2 (vdd_logic)")
    # after the link's rail symbol and its text, then room for vcc_1v8's symbol and text
    from draw import net_text
    bx = snap_up(s.last_box[2] + net_text("vcc_1v8") + 2.54)
    s.group_box("VCCIO6 branch", bx, yl - 10.16, 27.94, 20.32)
    two_pin_h(s, "R_0_0603", bx + 19.05, yl, "vcc_1v8", "vccio6_1v8", blk, stub=12.7)
    s.flag_net("vccio6_1v8", bx + 34.29, yl)     # outside the group, as a link's
    s.rail_rows = rows
    s.tables_at = (264.16, 101.6, 133.35)
    corner_notes(s, [
        "1. Function: RK3566 supply units and their decoupling, grouped by rail in placement order",
        "   (smallest value nearest the balls). Values: RK3566 HDG 1.1 pp. 32-41, as in the rail table.",
        "2. Absent state: not applicable (the SoC is never omitted).",
        "3. The capacitors of vdd_cpu, vdd_logic, vdd_gpu, vdd_npu and the DDR rails go on the back,",
        "   under the SoC, ground pads solid (HDG pp. 36-40, 92-93). None may be removed (HDG).",
        "4. vdd_logic link R: H5 5 mΩ in every variant (BOM v1 line 137); FB1 of the RK809 senses",
        "   vdd_logic on its load side, so the drop is regulated out (power tree §4.12).",
        "5. PHY analog supplies (vdda_0v9 PHY balls, USB 3.3 V) have no value in the HDG transcription:",
        "   their decoupling is open (UNVERIFIED) until RK3566_PinOut and HDG Fig. 2-22 are read.",
        "6. Unless noted: capacitors X5R/X7R, rated at least twice the rail.",
    ])
    s.rail_rows = rows


def _soc_ground(s, y0, variants):
    corner_notes(s, [
        "1. Function: RK3566 ground balls, all on GND.",
        "2. Absent state: not applicable (the SoC is never omitted).",
        "3. Every GND ball has its own via to the adjacent ground plane; balls joined by a # pattern of",
        "   0.254 mm traces on the top layer (HDG 1.1 pp. 92-93).",
    ])
