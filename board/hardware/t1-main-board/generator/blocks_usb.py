"""The two USB ports and their power: blk.usb-c (#9), blk.pwr-5v1 (#14), blk.usb-vbus-out (#16),
blk.hat-5v (#15) and blk.hat-signals (#19).

Sources: BOM v1 lines 41, 44, 61-70, 91, 92, 102, 121; power tree v0 §2, §4.6, §4.7; pinout v1
(USB balls, SARADC_VIN2/VIN3, expander P01-P03, P15-P17, USBC_INT_N, HAT_PD_INT_N); feature blocks
records 9, 14-16, 19; hat-standard interface v2 §9.2; RFC 0014, RFC 0015; RK3566 HDG 1.1 pp. 55-56;
the libs generator data (FUSB302BMPX, TPD8S300ARUKR, TPD4E05U06DQAR, TVS2200DRVR, TPS259470ARPWR,
TPS62903RPJR)."""

from __future__ import annotations

from blocks_audio import grp, ic_group, two_pin_box
from blocks_charger import rail_probe
from draw import Flow, Group, corner_notes, ic, part, prow, side_collector, tp
from sch import snap


def sheets(proj):
    usbc = proj.sheet("usb-c.kicad_sch", "blk.usb-c", "Main USB-C port",
                      "USB4105 receptacle, VBUS TVS, CC/SBU protection, D± ESD and the FUSB302B port controller", "A3")
    p5v1 = proj.sheet("pwr-5v1.kicad_sch", "blk.pwr-5v1", "5.1 V source",
                      "TPS62903 buck from VSYS for the HAT and USB-C sources, enabled by either port", "A3")
    vout = proj.sheet("usb-vbus-out.kicad_sch", "blk.usb-vbus-out", "USB-C source path",
                      "eFuse #D, the shared 5.1 V limiter, and eFuse #C to the USB-C VBUS", "A3")
    hat5v = proj.sheet("hat-5v.kicad_sch", "blk.hat-5v", "HAT port VBUS and USB PD",
                       "eFuse #A to the HAT VBUS, the FUSB302B01 port controller and the VBUS discharge", "A3")
    hats = proj.sheet("hat-signals.kicad_sch", "blk.hat-signals", "HAT USB port",
                      "DF40C-50 flat-cable receptacle: USB 3 with AC coupling, USB 2, CC, VBUS and GND", "A3")
    return usbc, p5v1, vout, hat5v, hats


def efuse_group(s, title, vin, vout, en, rilm, flt, imon):
    """A TPS259470A eFuse: RILM sets the limit and gives the current monitor; ITIMER and DVDT open
    (BOM v1 line 44); OVLO to GND (no overvoltage lockout, the active-low enable held on); FLT open
    drain to its pull-up; IMON through 10 kΩ to the SARADC's 1 nF, so the ILM node sees little
    capacitance (< 50 pF, SLVSFC9C p. 35)."""
    rows = [[("C_1u_0402_25V", vin, "GND"), ("C_1u_0402_25V", vout, "GND"), (rilm, f"{imon}_ILM", "GND")]]
    if imon.startswith("EFUSE_5V"):
        rows.append([])
    else:
        rows.append([("C_1n_0402", imon, "GND")])
    pins = {"IN": vin, "OUT": vout, "EN/UVLO": en, "OVLO": "GND", "AUXOFF": None, "FLT": flt,
            "DVDT": None, "ITIMER": None, "ILM": f"{imon}_ILM", "GND": "GND"}
    g = Group(s, title)
    u = ic(s, "texas-instruments", "TPS259470ARPWR", 101.6, 101.6, pins, extra={"Constraints": "PCB-P-11"})
    g.add(u.bbox)
    rx, ry = u.bbox[2] + 5.08, u.bbox[1] + 12.7
    b = g.add(prow(s, rx, ry, rows[0]))
    if rows[1]:
        g.add(two_pin_box(s, "R_10k", rx + 10.16, b[3] + 7.62, f"{imon}_ILM", imon))
        g.add(prow(s, rx + 55.88, b[3] + 22.86, rows[1]))
    else:
        tp(s, rx + 7.62, b[3] + 10.16, f"{imon}_ILM", text="left")
        s.point(f"{imon}_ILM", rx + 7.62, b[3] + 10.16, "down", "pas")
        g.add((rx, b[3] + 2.54, rx + 12.7, b[3] + 25.4))
    return g.close()


# ---------------------------------------------------------------------- blk.usb-c

def draw_usbc(s, variants):
    f = Flow(s)
    grp(f, lambda: ic_group(
        s, "Receptacle: GCT USB4105-GF-A (BOM v1 line 61)", "gct", "USB4105-GF-A",
        {"VBUS": "USBC_VBUS", "GND": "GND", "CC1": "USBC_C_CC1", "CC2": "USBC_C_CC2", "Dp1": "USBC_DP_C",
         "Dn1": "USBC_DM_C", "Dp2": "USBC_DP_C", "Dn2": "USBC_DM_C", "SBU1": "USBC_C_SBU1", "SBU2": "USBC_C_SBU2"},
        extra={"Constraints": "PCB-I-01"}, prefix="J"))
    grp(f, lambda: ic_group(
        s, "VBUS TVS, 22 V flat clamp (line 64)", "texas-instruments", "TVS2200DRVR",
        {"IN": "USBC_VBUS", "GND": "GND"}))
    grp(f, lambda: ic_group(
        s, "CC and SBU protection: TPD8S300A (line 63)", "texas-instruments", "TPD8S300ARUKR",
        {"C_CC1": "USBC_C_CC1", "C_CC2": "USBC_C_CC2", "RPD_G1": "USBC_C_CC1", "RPD_G2": "USBC_C_CC2",
         "CC1": "USBC_CC1", "CC2": "USBC_CC2", "C_SBU1": "USBC_C_SBU1", "C_SBU2": "USBC_C_SBU2",
         "SBU1": "USBC_SBU1", "SBU2": "USBC_SBU2", "VBIAS": "USBC_VBIAS", "VPWR": "vcc3v3_pmu",
         "FLT": "USBC_PROT_FLT_N", "D1": "GND", "D2": "GND", "D3": "GND", "D4": "GND", "GND": "GND"},
        rows=[[("C_100n_0603_50V", "USBC_VBIAS", "GND"), ("C_1u_0402", "vcc3v3_pmu", "GND"),
               ("R_10k", "vcc3v3_pmu", "USBC_PROT_FLT_N")]]))
    grp(f, lambda: ic_group(
        s, "D± ESD, 0.5 pF (line 62)", "texas-instruments", "TPD4E05U06DQAR",
        {"D1+": "USBC_DP_C", "D1-": "USBC_DM_C", "D2+": None, "D2-": None, "NC": None, "GND": "GND"}))

    def probes():
        g = Group(s, "SBU and fault test pads")
        for i, net in enumerate(("USBC_SBU1", "USBC_SBU2", "USBC_PROT_FLT_N")):
            x = 116.84 + i * 30.48
            tp(s, x, 101.6, net, text="left")
            s.point(net, x, 101.6, "down", "pas")
            g.add((x - 2.54 - len(net) * 1.16, 93.98, x + 2.54, 101.6 + 2.54 + len(net) * 1.16))
        return g.close()
    grp(f, probes)

    grp(f, lambda: ic_group(
        s, "Port controller: FUSB302B at I2C1 0x22 (line 41)", "onsemi", "FUSB302BMPX",
        {"CC1": "USBC_CC1", "CC2": "USBC_CC2", "VBUS": "USBC_VBUS", "VDD": "vcc3v3_pmu", "INT_N": "USBC_INT_N",
         "SCL": "I2C1_SCL", "SDA": "I2C1_SDA", "VCONN": None, "GND": "GND"},
        rows=[[("C_1u_0402", "vcc3v3_pmu", "GND"), ("C_100n_0402", "vcc3v3_pmu", "GND")]]))


    def series():
        g = Group(s, "D± series 2.2 Ω (HDG p. 56); VBUSDET divider (HDG Figure 2-43)")
        g.add(two_pin_box(s, "R_2R2", 101.6, 101.6, "USBC_DP_C", "USBC_DP"))
        g.add(two_pin_box(s, "R_2R2", 101.6, 111.76, "USBC_DM_C", "USBC_DM"))
        g.add(prow(s, 134.62, 109.22, [("R_10k", "USBC_VBUS", "USBC_VBUSDET"), ("R_15k", "USBC_VBUSDET", "GND")]))
        return g.close()
    grp(f, series)
    s.iface_rows = [
        ["USBC_VBUS", "Supply in / out", "Sink to the TPS2121 IN1 (blk.charger); source from eFuse #C"],
        ["USBC_DP, USBC_DM", "Bidirectional", "OTG0, 2.2 Ω here; MaskROM download port"],
        ["USBC_VBUSDET", "Output", "OTG0 VBUSDET, 10 kΩ / 15 kΩ from VBUS"],
        ["USBC_INT_N", "Output", "FUSB302B INT_N, open drain; pull-up on blk.soc-pmuio"],
        ["I2C1_SCL, I2C1_SDA", "Bidirectional", "FUSB302B at 0x22"],
    ]
    s.rail_rows = [["vcc3v3_pmu", "1 µF + 100 nF (FUSB302B); 1 µF (TPD8S300A VPWR)", "Datasheets: TPD8S300A §10"],
                   ["USBC_VBIAS", "100 nF 50 V", "TPD8S300A §9.2.2.1: ≥ 35 V rated"]]
    corner_notes(s, [
        "1. Function: the main USB-C receptacle: USB 2.0 OTG0 and USB PD sink (5-12 V into the TPS2121)",
        "   or source (5 V from eFuse #C); FUSB302B with the mainline fusb302 + tcpm drivers.",
        "2. Absent state: never omitted. Dead battery: TPD8S300A RPD_Gx tied to C_CCx so a source",
        "   sees Rd with the protection unpowered (§9.2.2.2); its CC FETs pass once vcc3v3_pmu is up.",
        "3. D±: TPD4E05U06 (0.5 pF) at the receptacle; the TPD8S300A D1-D4 clamps are grounded as",
        "   unused (§9.2.2.6). Common-mode choke footprint (HDG Figure 2-44): not fitted, open item.",
        "4. VBUSDET: HDG divider 10 kΩ / 15 kΩ (3.0 V at 5 V); the pin's rating at 9-12 V VBUS is",
        "   UNVERIFIED (BOM §7 item 41): bench item before a PD contract above 5 V is enabled.",
        "5. VCONN not sourced (no e-marked cable supply): VCONN pins open, UNVERIFIED termination.",
        "6. SBU to test pads (debug UART option, feature blocks #9); the TPD8S300A FLT on a test pad.",
    ])


# ---------------------------------------------------------------------- blk.pwr-5v1

def draw_pwr_5v1(s, variants):
    f = Flow(s)
    grp(f, lambda: ic_group(
        s, "TPS62903, 5.1 V, 2.5 MHz (BOM v1 lines 91, 92, 121)", "texas-instruments", "TPS62903RPJR",
        {"VIN": "VSYS_P5V1", "EN": "P5V1_EN", "MODE/S-CONF": "P5V1_MODE", "SS/TR": "P5V1_SS", "SW": "P5V1_SW",
         "VOS": "P5V1_SRC", "FB/VSET": "P5V1_VSET", "PG": "P5V1_PG", "GND": "GND"},
        rows=[[("R_95k3", "P5V1_VSET", "GND"), ("R_26k1", "P5V1_MODE", "GND"), ("C_10n_0402", "P5V1_SS", "GND"),
               ("R_100k", "P5V1_EN", "GND")],
              [("C_22u_0805_25V", "VSYS_P5V1", "GND"), ("C_22u_0805_25V", "P5V1_SRC", "GND"),
               ("C_22u_0805_25V", "P5V1_SRC", "GND")]],
        extra={"Constraints": "PCB-P-07"}))

    def stage():
        g = Group(s, "Inductor and enable OR (BOM v1 line 91)")
        g.add(two_pin_box(s, "L_XGL4015_102", 109.22, 101.6, "P5V1_SW", "P5V1_SRC", prefix="L"))
        for i, src in enumerate(("HAT5V_EN", "USB_SRC_ON")):
            y = 121.92 + i * 15.24
            from blocks_charger import or_diode      # text above the body, labels on stubs clear of it
            g.add(or_diode(s, 116.84, y, src, "P5V1_EN"))
        return g.close()
    grp(f, stage)

    def probe():
        g = Group(s, "Test pads")
        g.add(rail_probe(s, "P5V1_SRC", 116.84, 101.6, True))   # driven through the inductor
        tp(s, 152.4, 101.6, "P5V1_PG", text="left")
        s.point("P5V1_PG", 152.4, 101.6, "down", "pas")
        g.add((140.0, 93.98, 155.0, 115.0))
        return g.close()
    grp(f, probe)
    s.iface_rows = [
        ["VSYS_P5V1", "Supply in", "VSYS through the HAT INA236 shunt (0x43, blk.current-monitors)"],
        ["HAT5V_EN, USB_SRC_ON", "Input", "Expander P02, P03, pulled down: the buck off"],
        ["P5V1_SRC", "Supply out", "Off, discharged (output discharge on, MODE 26.1 kΩ)"],
    ]
    s.rail_rows = [["VSYS_P5V1", "22 µF 25 V", "SLVSES3A Table 8-1; 3 µF effective minimum (§6.3): 3.9 µF at 8.8 V (BOM v1.18 item 1)"],
                   ["P5V1_SRC", "2 x 22 µF 25 V 0805", "BOM v1 line 121: ≥ 12 µF effective at 5.1 V: 13.5 µF (BOM v1.18 item 5)"]]
    corner_notes(s, [
        "1. Function: TPS62903 VSYS (VSYS_P5V1) to 5.1 V, 1.6 A design (53 % of 3 A), for the HAT VBUS and the",
        "   USB-C source through eFuse #D (ADR 0014; power tree §4.6).",
        "2. Absent state: EN pulled down (100 kΩ): off, output discharged.",
        "3. EN = HAT5V_EN OR USB_SRC_ON in hardware: one BAT54J from each (BOM v1 line 91).",
        "4. VSET 95.3 kΩ (5.1 V), MODE/S-CONF 26.1 kΩ (2.5 MHz, discharge on, auto PFM/PWM, Table 7-1),",
        "   SS 10 nF: capture choice (ISS 2.5 µA). Phase margin at VSYS 6.0 V: bench item (§7 item 27).",
    ])


# ---------------------------------------------------------------------- blk.usb-vbus-out

def draw_usb_vbus_out(s, variants):
    f = Flow(s)
    grp(f, lambda: efuse_group(s, "eFuse #D, shared limiter, RILM 1.47 kΩ (BOM v1 line 44, v1.14)", "P5V1_SRC", "P5V1_LIM",
                               "P5V1_SRC", "R_1k47", "EFUSE_5V_FLT_N", "EFUSE_5V_IMON"))
    grp(f, lambda: efuse_group(s, "eFuse #C, USB-C source, RILM 1.87 kΩ (line 44)", "P5V1_LIM", "USBC_VBUS",
                               "USB_SRC_ON", "R_1k87", "EFUSE_VBUS_FLT_N", "EFUSE_VBUS_IMON"))
    s.iface_rows = [
        ["P5V1_SRC", "Supply in", "From blk.pwr-5v1"],
        ["P5V1_LIM", "Supply out", "To eFuse #A (blk.hat-5v)"],
        ["USB_SRC_ON", "Input", "Expander P03, pulled down: #C off"],
        ["EFUSE_5V_FLT_N, EFUSE_VBUS_FLT_N", "Output", "Open drain to expander P16, P17 (pull-ups there)"],
        ["EFUSE_VBUS_IMON", "Output", "SARADC_VIN3, 1 nF at the ball"],
    ]
    s.rail_rows = [["P5V1_SRC, P5V1_LIM, USBC_VBUS", "1 µF 25 V at each IN and OUT", "SLVSFC9C §8.3"]]
    corner_notes(s, [
        "1. Function: eFuse #D limits the 5.1 V source for both ports together (2.021 / 2.268 / 2.520 A);",
        "   eFuse #C sources the USB-C VBUS (1.589 / 1.783 / 1.981 A) under USB_SRC_ON (RFC 0015).",
        "2. Absent state: USB_SRC_ON pulled down: #C off, TPS2121 OV1 released.",
        "3. #D EN/UVLO on its own input: on with the buck. OVLO to GND: no overvoltage lockout.",
        "4. ITIMER and DVDT open (fastest response, BOM v1 line 44). IMON through 10 kΩ, keeping the",
        "   1 nF of the SARADC off the ILM node (< 50 pF, SLVSFC9C p. 35); #D IMON on a test pad.",
    ])


# ---------------------------------------------------------------------- blk.hat-5v

def draw_hat_5v(s, variants):
    f = Flow(s)
    grp(f, lambda: efuse_group(s, "eFuse #A, HAT VBUS source, RILM 1.87 kΩ (line 44)", "P5V1_LIM", "HAT_5V",
                               "HAT5V_EN", "R_1k87", "EFUSE_HAT5V_FLT_N", "EFUSE_HAT5V_IMON"))
    grp(f, lambda: ic_group(
        s, "Port controller: FUSB302B01 at I2C1 0x23 (line 41)", "onsemi", "FUSB302B01MPX",
        {"CC1": "HAT_CC", "CC2": None, "VBUS": "HAT_5V", "VDD": "vcc3v3_pmu", "INT_N": "HAT_PD_INT_N",
         "SCL": "I2C1_SCL", "SDA": "I2C1_SDA", "VCONN": None, "GND": "GND"},
        rows=[[("C_1u_0402", "vcc3v3_pmu", "GND"), ("C_100n_0402", "vcc3v3_pmu", "GND")]]))

    def discharge():
        g = Group(s, "VBUS discharge (BOM v1.13 changes item 3)")
        q = part(s, "Transistor_FET", "DMG1012T", 121.92, 109.22, {"1": "HAT_VBUS_DISCH", "3": "HAT_DISCH_D", "2": "GND"},
                 key="Q_DMG1012T", prefix="Q")
        g.add((snap(116.84 - 2.54 - 1.27 - len("HAT_VBUS_DISCH") * 1.16 - 2.54), 96.52, 134.62, 121.92))   # gate label
        g.add(prow(s, 142.24, 104.14, [("R_100_0805", "HAT_5V", "HAT_DISCH_D"), ("R_100k", "HAT_VBUS_DISCH", "GND")]))
        return g.close()
    grp(f, discharge)
    s.iface_rows = [
        ["P5V1_LIM", "Supply in", "From eFuse #D (blk.usb-vbus-out)"],
        ["HAT_5V", "Supply in / out", "HAT VBUS: source through #A, sink into the TPS2121 IN2 (blk.charger)"],
        ["HAT5V_EN, HAT_VBUS_DISCH", "Input", "Expander P02, P01, pulled down: source off, no discharge"],
        ["HAT_CC", "Bidirectional", "To the HAT connector (blk.hat-signals); Rd present unpowered"],
        ["HAT_PD_INT_N", "Output", "Open drain; 4.7 kΩ pull-up to vcc3v3_pmu on blk.soc-pmuio"],
        ["EFUSE_HAT5V_IMON", "Output", "SARADC_VIN2, 1 nF at the ball"],
    ]
    s.rail_rows = [["vcc3v3_pmu", "1 µF + 100 nF", "FUSB302B/D"],
                   ["P5V1_LIM, HAT_5V", "1 µF 25 V at IN and OUT", "SLVSFC9C §8.3"]]
    corner_notes(s, [
        "1. Function: the HAT port's VBUS under USB PD (hat-standard interface v2, RFC 0014): eFuse #A",
        "   sources 5 V (TCPM vbus-supply on HAT5V_EN), the TPS2121 IN2 sinks 5 V from a source HAT.",
        "2. Absent state: HAT5V_EN low, VBUS discharged; the FUSB302B01 presents Rd on CC, also",
        "   unpowered (dead-battery support), so a source HAT can feed the T1.",
        "3. One CC (the pogo field is keyed): CC2 open; VCONN not sourced, open (UNVERIFIED termination).",
        "4. Discharge: DMG1012T with 100 Ω (50 mA at 5 V), gate on HAT_VBUS_DISCH after the source is off;",
        "   the value against the PD discharge time and the port capacitance is UNVERIFIED (§7 item 47).",
        "5. The VBUS TVS and the ESD arrays sit on the device-side piece at the pogo field (BOM lines 65, 68, 69).",
    ])


# ---------------------------------------------------------------------- blk.hat-signals

def draw_hat_signals(s, variants):
    f = Flow(s)
    pins = {"1": None, "2": None, "49": None, "50": None}
    for n in range(3, 32, 2):
        pins[str(n)] = "HAT_5V"
    for n in range(4, 33, 2):
        pins[str(n)] = "GND"
    pins.update({"33": "GND", "34": "HAT_CC", "35": "HAT_SSTX_C_P", "36": None, "37": "HAT_SSTX_C_N", "38": None,
                 "39": "GND", "40": None, "41": "HAT_USB3_SSRX_P", "42": "GND", "43": "HAT_USB3_SSRX_N",
                 "44": "HAT_DP_C", "45": "GND", "46": "HAT_DM_C", "47": None, "48": "GND"})
    def receptacle():
        # the 15 VBUS contacts (odd, left) and the ground contacts on the right share one vertical
        # collector each, clear of the signal labels, with one symbol at its end (CRAFT-171)
        g = Group(s, "Flat-cable receptacle: DF40C-50DS (BOM v1 line 66; interface v2 §9.2)")
        hand = {k: "" for k, v in pins.items() if v == "HAT_5V" or (v == "GND" and int(k) % 2 == 0)}
        u = ic(s, "hirose", "DF40C-50DS-0.4V(51)", 101.6, 101.6, {**pins, **hand}, prefix="J",
               extra={"Constraints": "PCB-P-20"})
        side_collector(s, u, [k for k in hand if pins[k] == "HAT_5V"], "HAT_5V", 7.62)
        side_collector(s, u, [k for k in hand if pins[k] == "GND"], "GND", 17.78)
        g.add(u.bbox)
        g.add((u.bbox[0] - 10.16, u.bbox[1] - 5.08, u.bbox[2] + 20.32, u.bbox[3] + 7.62))
        return g.close()
    grp(f, receptacle)

    def coupling():
        g = Group(s, "USB 3 TX AC coupling, USB 2 series (lines 70; HDG p. 59)")
        y = 101.6
        for key, a, b in (("C_100n_0201", "HAT_USB3_SSTX_P", "HAT_SSTX_C_P"),
                          ("C_100n_0201", "HAT_USB3_SSTX_N", "HAT_SSTX_C_N"),
                          ("R_2R2", "HAT_USB3_DP", "HAT_DP_C"), ("R_2R2", "HAT_USB3_DM", "HAT_DM_C")):
            box = g.add(two_pin_box(s, key, 101.6, y, a, b))
            y = snap(box[3] + 5.08)          # each part below the previous one's text

        return g.close()
    grp(f, coupling)
    s.iface_rows = [
        ["HAT_USB3_SSTX_P/N, _SSRX_P/N", "Bidirectional", "USB3 HOST1 SuperSpeed (90 Ω)"],
        ["HAT_USB3_DP, HAT_USB3_DM", "Bidirectional", "USB3 HOST1 USB 2 half, 2.2 Ω here"],
        ["HAT_CC", "Bidirectional", "From the FUSB302B01 (blk.hat-5v)"],
        ["HAT_5V", "Supply in / out", "15 contacts, 0.3 A each (interface v2 §9.2)"],
    ]
    s.rail_rows = [["None", "No decoupling: the 100 nF are the TX AC-coupling capacitors", "RK3566 HDG 1.1 p. 59"]]
    corner_notes(s, [
        "1. Function: the HAT USB port on the board end of the flat cable (RFC 0015): USB 3 Gen 1, USB 2,",
        "   CC and VBUS to the device-side piece and its pogo field (hat-standard interface v2).",
        "2. Absent state: HAT or cable absent: no attach; the AC caps keep a dangling cable off the TX pair.",
        "3. Contacts per interface v2 §9.2: VBUS on 3-31 odd, GND on 4-32 even, 33, 39, 42, 45, 48;",
        "   CC 34; SSTX 35/37; SSRX 41/43; D± 44/46; 36, 38, 40, 47 spare; 1, 2, 49, 50 metal fittings.",
        "   Contact numbering against the Hirose drawing is UNVERIFIED (interface v2 §11 item 5).",
        "4. ESD and the VBUS TVS are on the device-side piece, none repeated here (BOM lines 65, 68, 69).",
    ])
