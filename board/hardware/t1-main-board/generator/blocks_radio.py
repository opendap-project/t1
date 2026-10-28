"""blk.radio (feature blocks #39) and blk.antennas (#40): the Murata Type 2EL module, its two rails,
the PDn hold translator, and both antenna paths.

Sources: board ADR 0018; BOM v1 lines 50, 55-58, 129-131, 137 (links 11, 12), 148; power tree v0
§2, §4.12; pinout v1 (SDMMC1, UART1, wake balls, expander P06, P07); feature blocks records 39-40;
Murata E2B-09-1413 Figure 5, Figures 9-10, E2B-54-1953 §4.3.3 (LBES5PL2EL-923)."""

from __future__ import annotations

from blocks_audio import grp, ic_group, link_group, parts_group, two_pin_box
from draw import Flow, Group, corner_notes, ic, prow

MODULE = "LBES5PL2EL-923"


KIDS = ["radio-module", "radio-power"]


def sheets(proj):
    radio = proj.sheet("radio.kicad_sch", "blk.radio", "Wi-Fi and Bluetooth module",
                       "Murata Type 2EL (IW612): SDIO, UART, wake lines, its 3.3 V and 1.8 V rails", "A4")
    kids = {
        "radio-module": proj.sheet("radio-module.kicad_sch", "blk.radio-module", "Radio: module",
                                   "Murata Type 2EL by unit, its decoupling and the SDIO series positions", "A3"),
        "radio-power": proj.sheet("radio-power.kicad_sch", "blk.radio-power", "Radio: rails and PDn hold",
                                  "AVDD33 switch, AVDD18 buck, links #11 and #12, the PDn hold translator", "A3"),
    }
    ant = proj.sheet("antennas.kicad_sch", "blk.antennas", "Antenna feeds",
                     "ANT0 and ANT1 paths as Murata's copy: matching positions, U.FL, the 10 pF shared link", "A3")
    return radio, kids, ant


def module_pins(sym_pins):
    """Net of every module pin, by the pin names of the kicad-lib symbol."""
    nets = {
        "PDn": "WL_PD_N", "AVDD33": "vcc3v3_wl", "AVDD18": "vcc1v8_wl", "VIO": "vcc_1v8", "SD_VIO": "vcc_1v8",
        "ANT0": "WL_ANT0", "ANT1": "WL_ANT1", "BT_15.4_IN": "WL_BT_IN",
        "SD_CMD": "WL_SD_CMD_M", "SD_CLK": "WL_SD_CLK_M", "SD_DAT[0]": "WL_SD_D0_M", "SD_DAT[1]": "WL_SD_D1_M",
        "SD_DAT[2]": "WL_SD_D2_M", "SD_DAT[3]": "WL_SD_D3_M",
        "UART_TX": "BT_UART_TXD", "UART_RX": "BT_UART_RXD", "UART_CTS": "BT_UART_CTS", "UART_RTS": "BT_UART_RTS",
        "CONFIG_HOST[0]": "vcc_1v8", "CONFIG_HOST[1]": "vcc_1v8",
        "WL_WAKE_OUT": "WL_WAKE_OUT", "BT15.4_WAKE_OUT": "BT_WAKE_OUT", "BT15.4_WAKE_IN": "BT_WAKE_IN",
        "GND": "GND",
    }
    out = {}
    for name in sym_pins:
        key = name
        for pfx in ("AVDD33", "AVDD18"):
            if name.startswith(pfx):
                key = pfx
        out[name] = nets.get(key)          # everything else (SPI, PCM, RF_CNTL, reserved, NC) open
    return out


def draw_parent(s):
    corner_notes(s, [
        "1. Function: Murata Type 2EL (NXP IW612): Wi-Fi 6 on SDIO 3.0, Bluetooth 5.4 on UART1 with",
        "   flow control (feature blocks #39), drawn on two sub-sheets: the module, and its rails with",
        "   the PDn hold translator.",
        "2. Absent state: WL_PWR_EN low: both module rails off, PDn low, wake lines pulled to no wake.",
        "3. Reserved for a PCIe + USB 2x2 module variant (a block revision): the RK3566 PCIe sideband",
        "   balls and USB HOST3, unconnected (pinout v1, 2026-10-25).",
    ])


def draw_module(s, variants):
    import library
    from draw import flow_units
    f = Flow(s)
    sym = library.load("murata", MODULE)
    names = sorted({p.name for p in sym.pins})
    by_name = module_pins(names)
    nets = {p.number: by_name.get(p.name) for p in sym.pins}

    def module():
        g = Group(s, "Murata Type 2EL, LBES5PL2EL-923 (BOM v1 line 55)")
        ref = s.next_ref("U")
        bottom = flow_units(s, sym, ref, sorted(sym.units), nets, {"Block": s.block, "Constraints": "PCB-R-01"},
                            101.6, 101.6, 101.6 + 250.0)
        g.add((96.52, 96.52, 101.6 + 250.0, bottom))
        return g.close()
    grp(f, module)
    grp(f, lambda: parts_group(s, "Module decoupling (E2B-09-1413 Figure 5)",
                               [[("C_10u_0603", "vcc3v3_wl", "GND"), ("C_10u_0603", "vcc1v8_wl", "GND"),
                                 ("C_10u_0603", "vcc_1v8", "GND"), ("C_100n_0402", "vcc_1v8", "GND")]]), newline=True)

    def sdio():
        g = Group(s, "SDIO series positions (E2B-09-1413 Figure 5 note 3)")
        for i, n in enumerate(("CMD", "CLK", "D0", "D1", "D2", "D3")):
            g.add(two_pin_box(s, "R_0_0402", 101.6 + (i // 3) * 45.72, 101.6 + (i % 3) * 10.16, f"WL_SD_{n}", f"WL_SD_{n}_M"))
        return g.close()
    grp(f, sdio)
    _module_tables(s)


def draw_power(s, variants):
    f = Flow(s)
    grp(f, lambda: ic_group(
        s, "PDn hold translator: SN74AXC1T45 (line 148)", "texas-instruments", "SN74AXC1T45DCKR",
        {"VCCA": "vcc3v3_sys", "VCCB": "vcc1v8_wl", "A": "WL_PD_HOLD_N", "B": "WL_PD_N", "DIR": "vcc3v3_sys",
         "GND": "GND"},
        rows=[[("C_100n_0402", "vcc3v3_sys", "GND"), ("C_100n_0402", "vcc1v8_wl", "GND"),
               ("R_100k", "WL_PD_N", "GND"), ("R_100k", "WL_PD_HOLD_N", "GND")]], pad_left=15.24), newline=True)

    grp(f, lambda: ic_group(
        s, "AVDD33 switch: TPS22916C (line 50)", "texas-instruments", "TPS22916CYFPR",
        {"VIN": "vcc3v3_sys", "ON": "WL_PWR_EN", "VOUT": "WL_3V3_SRC", "GND": "GND"},
        rows=[[("C_1u_0402", "vcc3v3_sys", "GND"), ("R_100k", "WL_PWR_EN", "GND")]]))
    grp(f, lambda: link_group(s, "LINK_H20", "WL_3V3_SRC", "vcc3v3_wl", variants, "Link #11"))
    grp(f, lambda: ic_group(
        s, "AVDD18 buck: TPS62826, 1.8 V (lines 129-131)", "texas-instruments", "TPS62826DMQR",
        {"VIN": "VSYS_LV", "EN": "WL_1V8_EN", "SW": "WL_1V8_SW", "FB": "WL_1V8_FB", "PG": None, "GND": "GND"},
        rows=[[("C_10u_0603_X7R", "VSYS_LV", "GND"), ("C_22u_0603", "WL_1V8_SRC", "GND"),
               ("R_200k_0603", "vcc1v8_wl", "WL_1V8_FB"), ("C_120p_0402", "vcc1v8_wl", "WL_1V8_FB"),
               ("R_100k_0603", "WL_1V8_FB", "GND")],
              [("R_0_0402", "vcc3v3_wl", "WL_1V8_EN"), ("R_100k", "WL_1V8_EN", "GND")]]), newline=True)

    def stage():
        g = Group(s, "Inductor, EN option and discharge positions (lines 130, 131)")
        g.add(two_pin_box(s, "L_XGL4015_471", 109.22, 101.6, "WL_1V8_SW", "WL_1V8_SRC", prefix="L"))
        g.add(two_pin_box(s, "R_0_0402", 109.22, 114.3, "WL_1V8_EN_GPIO", "WL_1V8_EN", dnp=True,
                          extra={"Alternate": "wl-1v8-en-gpio"}))
        g.add(prow(s, 101.6, 134.62, [("R_1k_0603", "vcc3v3_wl", "GND")], dnp=True,
                       extra={"Alternate": "wl-3v3-discharge"}))
        return g.close()
    grp(f, stage)
    grp(f, lambda: link_group(s, "LINK_H20", "WL_1V8_SRC", "vcc1v8_wl", variants, "Link #12"))

    s.iface_rows = [
        ["WL_PWR_EN, WL_PD_HOLD_N", "Input", "Expander P06, P07, 100 kΩ pull-downs here: rails off, PDn low"],
        ["vcc3v3_wl, vcc1v8_wl", "Supply out", "Module AVDD33 and AVDD18 (blk.radio-module)"],
        ["WL_PD_N", "Output", "Module PDn, held low while the radio is off"],
    ]
    s.rail_rows = [
        ["vcc3v3_sys", "1 µF at the switch, 100 nF at VCCA", "SLVSEN5B; SCES882E"],
        ["vcc1v8_wl", "22 µF at the buck; 100 nF at VCCB", "BOM v1 line 131"],
        ["VSYS_LV", "10 µF 10 V X7R", "BOM v1 line 131"],
    ]
    corner_notes(s, [
        "1. Function: the module rails: vcc3v3_wl through a TPS22916C on WL_PWR_EN, vcc1v8_wl from a",
        "   TPS62826 enabled by vcc3v3_wl, links #11 and #12 (power tree §4.12), and the PDn hold.",
        "2. Absent state: WL_PWR_EN low: vcc3v3_wl off and the AVDD18 buck with it (EN from vcc3v3_wl);",
        "   PDn low through the SN74AXC1T45 (its B port unpowered, Ioff).",
        "3. AVDD18: 200 kΩ / 100 kΩ (1.80 V), 120 pF; link #12 inside the feedback (power tree §4.12).",
        "   The DNP 0 Ω from WL_1V8_EN_GPIO and the DNP 1 kΩ discharge are bring-up options (lines 129, 131).",
        "4. Sequencing between AVDD33, AVDD18 and VIO: UNVERIFIED (module datasheet not obtained).",
    ])


def _module_tables(s):
    s.iface_rows = [
        ["WL_SD_CLK, _CMD, _D0-D3", "Bidirectional", "SDMMC1 at 1.8 V (VCCIO4); SoC pulls, parked low"],
        ["BT_UART_TXD, _RXD, _CTS, _RTS", "Bidirectional", "UART1 M0 with flow control (module-side names)"],
        ["WL_WAKE_OUT, BT_WAKE_OUT", "Output", "PMUIO2 wake balls, SoC pull-downs: no wake while off"],
        ["BT_WAKE_IN", "Input", "SoC pull-down"],
        ["WL_PD_N", "Input", "From blk.radio-power"],
        ["WL_ANT0, WL_ANT1, WL_BT_IN", "Passive", "To blk.antennas"],
    ]
    s.rail_rows = [
        ["vcc3v3_wl", "10 µF at AVDD33", "E2B-09-1413 Figure 5"],
        ["vcc1v8_wl", "10 µF at AVDD18", "E2B-09-1413 Figure 5"],
        ["vcc_1v8", "10 µF at SD_VIO, 100 nF at VIO", "E2B-09-1413 Figure 5 (VIO not drawn there: capture choice)"],
    ]
    corner_notes(s, [
        "1. Function: Murata Type 2EL (NXP IW612): Wi-Fi 6 on SDIO 3.0, Bluetooth 5.4 on UART1 with",
        "   flow control; nxpwifi and btnxpuart (DKMS until Linux 7.3). 802.15.4 SPI not wired (T1-077).",
        "2. Absent state: rails off (blk.radio-power), wake lines pulled to no wake by the SoC.",
        "3. CONFIG_HOST[1:0] = 11 (SDIO, UART, SPI hosts; Figure 5 note 2). RF_CNTL, GPIO, PCM, WCI-2,",
        "   reset indicators and reserved pins open (E2B-09-1413 §3.3); module land from Murata's DXF,",
        "   mask and stencil UNVERIFIED (module datasheet not obtained).",
        "4. SDIO series positions fitted with 0 Ω; damping values at bring-up. UART direct.",
    ])


def draw_antennas(s, variants):
    f = Flow(s)

    def path(title, ant, j_net, fitted):
        g = Group(s, title)
        g.add(two_pin_box(s, "R_0_0201", 109.22, 101.6, ant, j_net, dnp=not fitted,
                          **({} if fitted else {"extra": {"Alternate": "ant1-dedicated"}})))
        g.add(prow(s, 101.6, 132.08, [("C_NF_0603", ant, "GND"), ("C_NF_0603", j_net, "GND")], dnp=True,
                       extra={"Alternate": "rf-match"}))
        u = ic(s, "hirose", "U.FL-R-SMT-1", 147.32, 106.68, {"SIG": j_net, "GND": "GND"}, prefix="J",
               extra={"Constraints": "PCB-R-02 PCB-R-03"})
        g.add(u.bbox)
        return g.close()
    grp(f, lambda: path("ANT0: Wi-Fi 2.4 / 5 GHz and Bluetooth (shared, ADR 0018)", "WL_ANT0", "WL_ANT0_J", True))
    grp(f, lambda: path("ANT1: dedicated configuration, not fitted (ADR 0018 item 4)", "WL_ANT1", "WL_ANT1_J", False))

    def link():
        g = Group(s, "Shared link: pin 18 to pin 23, 10 pF (E2B-54-1953 §4.3.3)")
        g.add(two_pin_box(s, "C_10p_0603", 109.22, 101.6, "WL_BT_IN", "WL_ANT1"))
        return g.close()
    grp(f, link)
    s.iface_rows = [["WL_ANT0, WL_ANT1, WL_BT_IN", "Passive", "Module RF pins (blk.radio-module)"]]
    s.rail_rows = [["None", "No supply: RF matching positions and the 10 pF link only", "ADR 0018"]]
    corner_notes(s, [
        "1. Function: both RF paths as Murata's copy (0603 positions, LQP03 / GRM03 class): ANT0 to the",
        "   U.FL of the Molex 146153-0050 (fitted), ANT1 to a second U.FL (not fitted) (ADR 0018).",
        "2. Absent state: passive. Shared configuration: series 0 Ω on ANT0 fitted, shunts DNP; the 10 pF",
        "   link from BT_15.4_IN to ANT1 fitted; the ANT1 path not fitted.",
        "3. Dedicated configuration: fit the ANT1 path and terminate BT_15.4_IN per E2B-09-1413 Figure 10",
        "   (values UNVERIFIED as drawn) instead of the 10 pF link; calibration file per ADR 0018 item 6.",
        "4. RF microstrip 50 Ω, 7-25 mm, ground 230-240 µm below (Murata); ≥ 0.8 mm keep-out under each U.FL.",
    ])
