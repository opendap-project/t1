"""The faceplate interface, host side: blk.fp-connector (#21), blk.fp-display (#22),
blk.fp-backlight (#23), blk.fp-controls (#24) and blk.mic-main (#26).

Sources: t1 faceplate interface v1 and t1 ADR 0005 (supply classes and fault ceilings); BOM v1
lines 51-53, 71, 75, 145, 146 and the v1.11 changes (BC4); power tree v0 §2, §3, §4.5; pinout v1
§3 (Faceplate, expander P00, P12-P14) and §8.2 (contact positions); feature blocks records 21-26;
TI SLVS791E (TPS61160), SLVSFJ2B (TPS22950), SLVS832D (TPS22945); the parts-lib sheets."""

from __future__ import annotations

from blocks_audio import grp, ic_group, link_group, two_pin_box
from blocks_charger import rail_probe
from draw import Flow, Group, corner_notes, ic, part, prow, side_collector, tp
from sch import snap


def sheets(proj):
    conn = proj.sheet("fp-connector.kicad_sch", "blk.fp-connector", "Faceplate connector",
                      "FH35C-51S contacts, low-speed ESD, and the current-limited FP_3V3 and FP_1V8 switches", "A3")
    disp = proj.sheet("fp-display.kicad_sch", "blk.fp-display", "Faceplate display supply",
                      "FP_VCI current-limited switch after RK809 LDO4; DSI lanes pass to the connector", "A4")
    bl = proj.sheet("fp-backlight.kicad_sch", "blk.fp-backlight", "Faceplate backlight",
                    "TPS61160 boost LED driver, 60 mA, open-LED threshold below 30 V", "A4")
    ctl = proj.sheet("fp-controls.kicad_sch", "blk.fp-controls", "Faceplate controls",
                     "I2C3, SPI/DBI and interrupt pulls on FP_3V3, the touch address strap", "A4")
    mic = proj.sheet("mic-main.kicad_sch", "blk.mic-main", "Microphone supply",
                     "MIC_1V8 current-limited switch and the PDM clock series resistor", "A4")
    return conn, disp, bl, ctl, mic


# Contacts of the FH35C-51S (pinout v1 §8.2): contact -> net (None: reserved, no-connect)
CONTACTS = {
    1: "GND", 2: "FP_DSI_D3_P", 3: "FP_DSI_D3_N", 4: "GND", 5: "FP_DSI_D2_P", 6: "FP_DSI_D2_N", 7: "GND",
    8: "FP_DSI_D1_P", 9: "FP_DSI_D1_N", 10: "GND", 11: "FP_DSI_D0_P", 12: "FP_DSI_D0_N", 13: "GND",
    14: "FP_DSI_CLK_P", 15: "FP_DSI_CLK_N", 16: "GND", 17: "FP_I2C_SCL", 18: "FP_I2C_SDA", 19: "FP_SPI_SCLK",
    20: "FP_SPI_MOSI", 21: "FP_SPI_MISO", 22: "FP_SPI_CS_N", 23: "FP_DBI_DC", 24: "FP_TP_INT", 25: "FP_TP_RST_N",
    26: "FP_LCD_RST_N", 27: "FP_LCD_TE", 28: "FP_HID_INT_N", 29: "FP_ALS_INT_N", 30: "LED_R", 31: "LED_G",
    32: "LED_B", 33: "GND", 34: "PDM_CLK0_FP", 35: "PDM_DATA0", 36: "FP_DET_N", 37: "FP_GPIO0", 38: "FP_GPIO1",
    39: "GND", 40: "MIC_1V8_FP", 41: "FP_1V8", 42: "FP_3V3", 43: "FP_3V3", 44: "FP_VCI", 45: "BL_LEDK",
    46: "BL_LEDA", 47: None, 48: None, 49: None, 50: None, 51: None,
}
LOW_SPEED = [CONTACTS[c] for c in range(17, 39) if CONTACTS[c] not in ("GND",)]   # 21 lines (BOM v1 line 75)


def switch_group(s, title, part_name, pins, rows, extra=None):
    return ic_group(s, title, "texas-instruments", part_name, pins, rows=rows, extra=extra)


# ---------------------------------------------------------------------- blk.fp-connector

def draw_connector(s, variants):
    f = Flow(s)
    pins = {str(c): n for c, n in CONTACTS.items()}

    def connector():
        g = Group(s, "FH35C-51S-0.3SHW, contacts per pinout v1 §8.2 (BOM v1 line 71)")
        gnd = [k for k, v in pins.items() if v == "GND"]
        u = ic(s, "hirose", "FH35C-51S-0.3SHW", 101.6, 101.6, {**pins, **{k: "" for k in gnd}}, prefix="J",
               extra={"Constraints": "PCB-I-04"})
        left = [k for k in gnd if u.out(u.pin(k))[0] < 0]
        right = [k for k in gnd if u.out(u.pin(k))[0] > 0]
        side_collector(s, u, left, "GND", 25.4)
        side_collector(s, u, right, "GND", 25.4)
        g.add((u.bbox[0] - 7.62, u.bbox[1], u.bbox[2] + 7.62, u.bbox[3] + 7.62))
        return g.close()
    grp(f, connector)

    def esd():
        g = Group(s, "Low-speed ESD: 6 x TPD4E05U06, 21 lines (BOM v1 line 75)")
        lines = LOW_SPEED + [None] * (24 - len(LOW_SPEED))
        for i in range(6):
            a, b, c, d = lines[4 * i:4 * i + 4]
            u = ic(s, "texas-instruments", "TPD4E05U06DQAR", 101.6 + (i % 3) * 60.96, 101.6 + (i // 3) * 48.26,
                   {"D1+": a, "D1-": b, "D2+": c, "D2-": d, "NC": None, "GND": "GND"})
            g.add(u.bbox)
        return g.close()
    grp(f, esd)

    def detect():
        g = Group(s, "Detect, spares (P12-P14)")
        g.add(prow(s, 101.6, 109.22, [("R_10k", "vcc3v3_sys", "FP_DET_N"), ("R_100k", "FP_GPIO0", "GND"),
                                      ("R_100k", "FP_GPIO1", "GND")]))
        return g.close()
    grp(f, detect)

    grp(f, lambda: switch_group(
        s, "FP_3V3: TPS22950, RILIM 3.57 kΩ, 0.22-0.38 A (BOM v1 line 145)", "TPS22950YBHR",
        {"VIN": "vcc3v3_sys", "VOUT": "FP_3V3_SRC", "ON": "FP_IO_EN", "ILIM": "FP3V3_ILIM", "FLT": None, "GND": "GND"},
        rows=[[("C_1u_0402", "vcc3v3_sys", "GND"), ("C_1u_0402", "FP_3V3_SRC", "GND"), ("R_3k57", "FP3V3_ILIM", "GND"),
               ("R_100k", "FP_IO_EN", "GND")]]), newline=True)
    # the links in a column between the switches; their Kelvin pads are the rail test pads (PCB-T-02)
    col = Flow(s, x0=snap(f.x + 0.0), y0=f.y)
    col.x_max = col.x0 + 80.0
    grp(col, lambda: link_group(s, "LINK_M", "FP_3V3_SRC", "FP_3V3", variants, "Link #23"))
    grp(col, lambda: link_group(s, "LINK_L1", "FP_1V8_SRC", "FP_1V8", variants, "Link #31"))
    f.x = snap(col.x_right + f.gap)
    f.row_h = max(f.row_h, col.bottom() - f.y)
    grp(f, lambda: switch_group(
        s, "FP_1V8: TPS22945, 100-200 mA (BOM v1 line 146)", "TPS22945DCKR",
        {"VIN": "vcc_1v8", "VOUT": "FP_1V8_SRC", "ON": "FP_IO_EN", "OC": None, "GND": "GND"},
        rows=[[("C_1u_0402", "vcc_1v8", "GND"), ("C_1u_0402", "FP_1V8_SRC", "GND"), ("R_10k", "FP_1V8_SRC", "GND")]]))

    s.iface_rows = [
        ["FP_DSI_*", "Output", "From blk.fp-display (DSI0 D-PHY, 100 Ω)"],
        ["FP_I2C_*, FP_SPI_*, FP_TP_*, FP_LCD_*, FP_*_INT_N", "Bidirectional", "From blk.fp-controls"],
        ["LED_R, LED_G, LED_B", "Output", "From blk.status-led (LP5521 current sources): open with the LP5521 unfitted"],
        ["PDM_CLK0_FP, PDM_DATA0", "Bidirectional", "blk.mic-main: clock through 22 Ω; data to the SoC"],
        ["FP_IO_EN", "Input", "Expander P00, 100 kΩ pull-down here: both switches off"],
        ["FP_DET_N, FP_GPIO0, FP_GPIO1", "Bidirectional", "Expander P12-P14; detect pulled up: absent"],
        ["FP_VCI, MIC_1V8_FP, BL_LEDA, BL_LEDK", "Supply", "From blk.fp-display, blk.mic-main, blk.fp-backlight"],
    ]
    s.rail_rows = [["vcc3v3_sys, FP_3V3_SRC", "1 µF at VIN and VOUT", "SLVSFJ2B (value: capture choice)"],
                   ["vcc_1v8, FP_1V8_SRC", "1 µF at IN and OUT", "SLVS832D (value: capture choice)"]]
    corner_notes(s, [
        "1. Function: the FH35C-51S faceplate connector (t1 faceplate interface v1): DSI, I2C3, SPI/DBI,",
        "   touch, panel, interrupts, status LED, PDM, detect, spares, power; 5 contacts reserved.",
        "2. Absent state: faceplate detached: FP_DET_N reads high (absent); FP_IO_EN low keeps FP_3V3",
        "   (TPS22950 QOD) and FP_1V8 (10 kΩ discharge, the TPS22945 has none) off.",
        "3. Fault ceilings (t1 ADR 0005): FP_3V3 0.4 A (ILIM 0.22-0.38 A, UNVERIFIED at 3.57 kΩ),",
        "   FP_1V8 0.2 A (100-200 mA at 3.3 V; limit at 1.8 V UNVERIFIED, SLVS832D §7.5).",
        "4. FP_DET_N 10 kΩ pull-up and the spares' 100 kΩ pull-downs: capture choices. The TPS22950",
        "   FLT output is left open (auto-retry; the fault shows as FP_3V3 low): open item.",
        "5. Contacts 47-51 reserved (47, next to BL_LEDA, never a logic line). Contact numbering",
        "   against the Hirose drawing: pinout v1 §8.1.",
        "6. Links (power tree §4.12): #23 FP_3V3, 0.1 Ω (80 mA, 8 mV); #31 FP_1V8, 1 Ω (5 mA, 5 mV).",
    ])


# ---------------------------------------------------------------------- blk.fp-display

def draw_display(s, variants):
    f = Flow(s)
    grp(f, lambda: switch_group(
        s, "FP_VCI: TPS22945 after RK809 LDO4 (BOM v1 line 146)", "TPS22945DCKR",
        {"VIN": "FP_VCI_SRC", "VOUT": "FP_VCI_OUT", "ON": "FP_IO_EN", "OC": None, "GND": "GND"},
        rows=[[("C_1u_0402", "FP_VCI_SRC", "GND"), ("C_1u_0402", "FP_VCI_OUT", "GND"), ("R_10k", "FP_VCI_OUT", "GND")]]))
    grp(f, lambda: link_group(s, "LINK_M", "FP_VCI_OUT", "FP_VCI", variants, "Link #24"))

    s.iface_rows = [
        ["FP_VCI_SRC", "Supply in", "RK809 LDO4, 2.8 V (DT-adjustable)"],
        ["FP_IO_EN", "Input", "Expander P00 (pull-down on blk.fp-connector)"],
        ["FP_VCI", "Supply out", "Contact 44: off with FP_IO_EN low, whatever the LDO4 OTP state"],
        ["FP_DSI_CLK_P/N, FP_DSI_D0-D3_P/N", "Output", "DSI0 from blk.soc-phy straight to the connector"],
    ]
    s.rail_rows = [["FP_VCI_SRC, FP_VCI_OUT", "1 µF at IN and OUT", "SLVS832D (value: capture choice)"]]
    corner_notes(s, [
        "1. Function: the panel supply FP_VCI through a 100-200 mA switch, since the RK809 states no LDO4",
        "   trip and its OTP start-up state is unknown (power tree §2, v0.5); DSI0 lanes to contacts 2-15.",
        "2. Absent state: FP_IO_EN low: FP_VCI off, discharged by 10 kΩ; panel RST low and TE pulled",
        "   down by the SoC pulls (pinout v1).",
        "3. Blackbird OS opens the switch before LDO4 goes down (no reverse blocking, SLVS832D §9.1.3).",
        "4. Open: the DSI common-mode filter positions (PCB-EMC-01) wait for the layout study.",
        "5. Link #24, 0.1 Ω, after the switch (power tree §4.12: 0.1 A design, 10 mV); its Kelvin pads",
        "   are the rail test pads (PCB-T-02).",
    ])


# ---------------------------------------------------------------------- blk.fp-backlight

def draw_backlight(s, variants):
    f = Flow(s)
    grp(f, lambda: ic_group(
        s, "TPS61160, RSET 3.32 Ω for 60 mA (BOM v1 line 51)", "texas-instruments", "TPS61160DRVR",
        {"VIN": "VSYS_LV_BL", "CTRL": "BL_PWM", "SW": "BL_SW", "FB": "BL_LEDK", "COMP": "BL_COMP", "GND": "GND", "EP": "GND"},
        rows=[[("C_4u7_0603_10V", "VSYS_LV_BL", "GND"), ("C_220n_0402", "BL_COMP", "GND"),
               ("R_3R32", "BL_LEDK", "GND")]],
        extra={"Constraints": "PCB-P-07"}))

    def stage():
        g = Group(s, "Inductor, rectifier, output capacitor (lines 52, 53)")
        g.add(two_pin_box(s, "L_LQH3NPN220", 109.22, 101.6, "VSYS_LV_BL", "BL_SW", prefix="L"))
        part(s, "Diode", "PMEG6010CEH", 116.84, 116.84, {"1": "BL_LEDA", "2": "BL_SW"}, key="D_PMEG6010CEH", angle=180,
             prefix="D", ref_at=(116.84, 116.84 - 6.35), val_at=(116.84, 116.84 - 3.81), stub=5.08)
        g.add((96.52, 106.68, 137.16, 119.38))
        g.add(prow(s, 101.6, 137.16, [("C_1u_0603_50V", "BL_LEDA", "GND")]))
        return g.close()
    grp(f, stage)
    s.iface_rows = [
        ["VSYS_LV_BL", "Supply in", "VSYS_LV 3.8 V through the display INA236 shunt (0x42, blk.current-monitors)"],
        ["BL_PWM", "Input", "PWM8_M0, SoC pull-down: off"],
        ["BL_LEDA, BL_LEDK", "Output", "Contacts 46, 45: the LED string between them"],
    ]
    s.rail_rows = [["VSYS_LV_BL", "4.7 µF", "BOM v1 §8 (CIN 4.7 µF); SLVS791E §8.2.1.2.5: 1-4.7 µF"],
                   ["BL_LEDA", "1 µF 50 V", "BOM v1 §8; SLVS791E: 0.47-10 µF"]]
    corner_notes(s, [
        "1. Function: TPS61160 boost LED driver from VSYS_LV_BL, 60.2 mA (RSET 3.32 Ω, VFB 200 mV); strings",
        "   up to 22 V; open-LED threshold 25-27 V at SW keeps BL_LEDA below 30 V (SLVS791E §6.5).",
        "2. Absent state: CTRL low (SoC pull-down): off; an open string is bounded by the threshold.",
        "3. COMP 220 nF as the datasheet's typical application (SLVS791E Figure 15); inductor 22 µH",
        "   LQH3NPN220MMEL (Murata sheet not retrieved, rating UNVERIFIED); PMEG6010CEH rectifier.",
        "4. Software: pwm-backlight on CTRL (PWM 5-100 kHz, SLVS791E §6.3).",
    ])


# ---------------------------------------------------------------------- blk.fp-controls

def draw_controls(s, variants):
    f = Flow(s)

    def pulls():
        g = Group(s, "Pull-ups on FP_3V3 (G8; BOM v1.11)")
        g.add(prow(s, 101.6, 109.22, [("R_2k2", "FP_3V3", "FP_I2C_SCL"), ("R_2k2", "FP_3V3", "FP_I2C_SDA"),
                                      ("R_4k7", "FP_3V3", "FP_HID_INT_N"), ("R_4k7", "FP_3V3", "FP_ALS_INT_N"),
                                      ("R_10k", "FP_3V3", "FP_SPI_CS_N")]))
        return g.close()
    grp(f, pulls)

    def strap():
        g = Group(s, "Touch address strap footprint (G9)")
        g.add(prow(s, 101.6, 109.22, [("R_10k", "FP_TP_INT", "GND")], dnp=True, extra={"Alternate": "gt911-strap"}))
        return g.close()
    grp(f, strap)
    s.iface_rows = [
        ["FP_I2C_SCL, FP_I2C_SDA", "Bidirectional", "I2C3_M1 at 3.3 V; pulled to FP_3V3, so nothing back-powers"],
        ["FP_HID_INT_N, FP_ALS_INT_N", "Output", "Open drain on the faceplate; read low while FP_3V3 is off"],
        ["FP_SPI_*, FP_DBI_DC, FP_TP_*, FP_LCD_*", "Bidirectional", "SPI1_M1 and GPIO on VCCIO5; SoC pulls"],
    ]
    corner_notes(s, [
        "1. Function: the faceplate control bus and its interrupts (record 24): I2C3 at 400 kHz with",
        "   2.2 kΩ (≤ 100 pF from the faceplate), HID_INT (wake) and ALS_INT 4.7 kΩ, all on FP_3V3.",
        "2. Absent state: FP_3V3 off: the pull-ups are unpowered, no faceplate part is back-powered;",
        "   the interrupts read low and are masked by software.",
        "3. SPI CS 10 kΩ pull-up (inactive at faceplate power-up, pinout v1): value a capture choice.",
        "4. GT911 address strap: a DNP pull-down footprint on FP_TP_INT (Alternate gt911-strap); the SoC",
        "   pull-down sets the default address.",
    ])


# ---------------------------------------------------------------------- blk.mic-main

def draw_mic(s, variants):
    f = Flow(s)
    grp(f, lambda: switch_group(
        s, "MIC_1V8: TPS22945, 100-200 mA (BOM v1 line 146)", "TPS22945DCKR",
        {"VIN": "vcc_1v8", "VOUT": "MIC_1V8", "ON": "MIC_EN", "OC": None, "GND": "GND"},
        rows=[[("C_1u_0402", "vcc_1v8", "GND"), ("C_1u_0402", "MIC_1V8", "GND"), ("R_10k", "MIC_1V8", "GND")]]))

    def series():
        g = Group(s, "PDM clock series (HDG p. 72)")
        g.add(two_pin_box(s, "R_22", 101.6, 101.6, "PDM_CLK0", "PDM_CLK0_FP"))
        return g.close()
    grp(f, series)
    grp(f, lambda: link_group(s, "LINK_L10", "MIC_1V8", "MIC_1V8_FP", variants, "Link #34"))

    def probes():
        g = Group(s, "Test pad (PCB-T-02)")
        g.add(rail_probe(s, "MIC_1V8", 116.84, 101.6))
        return g.close()
    grp(f, probes)
    s.iface_rows = [
        ["MIC_EN", "Input", "GPIO4_C0, SoC pull-down: off"],
        ["MIC_1V8, MIC_1V8_FP", "Supply out", "Off with MIC_EN low; MIC_1V8_FP to contact 40, MIC_1V8 also to blk.mic-ambient"],
        ["PDM_CLK0, PDM_CLK0_FP", "Output", "PDM_CLK0_M1, parked low while MIC_1V8 is off (G10)"],
    ]
    s.rail_rows = [["vcc_1v8, MIC_1V8", "1 µF at IN and OUT", "SLVS832D (value: capture choice)"]]
    corner_notes(s, [
        "1. Function: MIC_1V8 for the faceplate microphone through a 100-200 mA switch (≤ 0.2 A ceiling).",
        "2. Absent state: MIC_EN low: MIC_1V8 off, discharged by 10 kΩ; PDM clock parked low.",
        "3. Link #34 (L10, 10 Ω) on the faceplate branch, MIC_1V8_FP; the ambient branch takes link #35",
        "   on blk.mic-ambient (power tree §4.12, G10).",
        "4. Open: the privacy-LED gate (BOM v1 line 35: DMG1012T, gate = MIC_1V8, LED anode from",
        "   FP_3V3) has no faceplate contact in pinout v1 §8.2; it is drawn when the LED's place is set.",
    ])
