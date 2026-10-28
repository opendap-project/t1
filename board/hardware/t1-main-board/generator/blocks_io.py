"""IO blocks on I2C2 and the storage socket: blk.gpio-expander (#6), blk.board-id (#5),
blk.imu (#43), blk.speaker (#37) and blk.microsd (#4).

Sources: BOM v1 lines 11, 32, 33, 59, 73, 93 and the v1.8 changes (G1, G15, G16); pinout v1 §3
(Power path and expander, Storage, Audio, Radio and sensors) and the expander port table; feature
blocks records 4-6, 37, 43; TI SCPS194F (TCA6416A), Microchip 8871F (AT24C02D), ST DS13510
(LSM6DSV16X), Analog Devices MAX98357A Rev 11, RK3566 HDG 1.1 p. 52; the libs generator data."""

from __future__ import annotations

from blocks_audio import grp, ic_group, link_group, tvs_group, two_pin_box
from draw import Flow, Group, corner_notes, part, prow, tp
from sch import snap, snap_up


def sheets_buttons(proj):
    return proj.sheet("buttons.kicad_sch", "blk.buttons", "Side buttons",
                      "Power, Action, Vol+ and Vol-, each with its ESD diode", "A4")


def sheets(proj):
    exp = proj.sheet("gpio-expander.kicad_sch", "blk.gpio-expander", "GPIO expander",
                     "TCA6416A on I2C2: slow enables with their off-state pulls, detects and fault inputs", "A3")
    bid = proj.sheet("board-id.kicad_sch", "blk.board-id", "Board EEPROM",
                     "AT24C02D board identity EEPROM on I2C2 at 0x50", "A4")
    imu = proj.sheet("imu.kicad_sch", "blk.imu", "Motion sensor",
                     "LSM6DSV16X on I2C2 at 0x6A, INT1 wake on motion, always on", "A4")
    spk = proj.sheet("speaker.kicad_sch", "blk.speaker", "Speaker amplifier",
                     "MAX98357A on I2S3, SD_MODE shutdown, speaker spring-contact pads", "A4")
    sd = proj.sheet("microsd.kicad_sch", "blk.microsd", "microSD socket",
                    "DM3AT socket, SDMMC0 series resistors, card detect and ESD", "A4")
    return exp, bid, imu, spk, sd


# ---------------------------------------------------------------------- blk.gpio-expander

PORTS = {"P00": "FP_IO_EN", "P01": "HAT_VBUS_DISCH", "P02": "HAT5V_EN", "P03": "USB_SRC_ON", "P04": "HAPTIC_EN",
         "P05": None, "P06": "WL_PWR_EN", "P07": "WL_PD_HOLD_N", "P10": "HP_DET_SE", "P11": "HP_DET_BAL",
         "P12": "FP_DET_N", "P13": "FP_GPIO0", "P14": "FP_GPIO1", "P15": "EFUSE_HAT5V_FLT_N",
         "P16": "EFUSE_5V_FLT_N", "P17": "EFUSE_VBUS_FLT_N"}


def draw_expander(s, variants):
    f = Flow(s)
    pins = dict(PORTS)
    pins.update({"SCL": "I2C2_SCL", "SDA": "I2C2_SDA", "INT": "EXP_INT_N", "RESET": "EXP_RESET_N",
                 "ADDR": "vcc3v3_sys", "VCCI": "vcca1v8_pmu", "VCCP": "vcc3v3_sys", "GND": "GND", "EP": "GND"})
    grp(f, lambda: ic_group(
        s, "TCA6416A at I2C2 0x21 (BOM v1 line 93)", "texas-instruments", "TCA6416ARTWR", pins,
        rows=[[("C_100n_0402", "vcca1v8_pmu", "GND"), ("C_100n_0402", "vcc3v3_sys", "GND"),
               ("R_10k", "vcca1v8_pmu", "EXP_RESET_N")]], pad_left=15.24))

    def pulls():
        g = Group(s, "Off-state pull-downs and input pull-ups (PCB-P-18)")
        b = g.add(prow(s, 101.6, 109.22, [("R_100k", "HAT5V_EN", "GND"), ("R_100k", "USB_SRC_ON", "GND"),
                                          ("R_100k", "HAPTIC_EN", "GND")]))
        g.add(prow(s, 101.6, b[3] + 22.86, [("R_10k", "vcc3v3_sys", "HP_DET_SE"), ("R_10k", "vcc3v3_sys", "HP_DET_BAL"),
                                            ("R_10k", "vcc3v3_sys", "EFUSE_HAT5V_FLT_N"),
                                            ("R_10k", "vcc3v3_sys", "EFUSE_5V_FLT_N"),
                                            ("R_10k", "vcc3v3_sys", "EFUSE_VBUS_FLT_N")]))
        return g.close()
    grp(f, pulls)
    s.iface_rows = [
        ["I2C2_SCL, I2C2_SDA", "Bidirectional", "Pull-ups on blk.soc-pmuio (vcca1v8_pmu)"],
        ["EXP_INT_N", "Output", "Open drain; 4.7 kΩ pull-up on blk.soc-pmuio"],
        ["P00-P07 outputs", "Output", "Ports power up as inputs: each output's board pull-down holds it off"],
        ["P10-P17 inputs", "Input", "Jack detects, faceplate detect and spares, eFuse faults"],
    ]
    s.rail_rows = [["vcca1v8_pmu, vcc3v3_sys", "100 nF at VCCI and VCCP", "SCPS194F (value: capture choice)"]]
    corner_notes(s, [
        "1. Function: TCA6416A, the slow enables and detects (pinout v1 expander table); VCCI on",
        "   vcca1v8_pmu, VCCP on vcc3v3_sys; outputs hold through suspend.",
        "2. Absent state: never omitted. At power-up every port is an input: P02-P04 pulled down here;",
        "   P00 on blk.fp-connector, P01 on blk.hat-5v, P06, P07 on blk.radio.",
        "3. ADDR to VCCP: address 0x21 (SCPS194F). RESET 10 kΩ to VCCI (not driven by the SoC).",
        "4. Input pull-ups to VCCP: jack detects (HP_DET_*, the jack switch pulls low) and the eFuse",
        "   faults (open drain), 10 kΩ: capture choices.",
        "5. P05 spare, no-connect (was NFC_PWR_EN: the NFC reader removed, maintainer decision 2026-10-27);",
        "   the driver sets it as an output, low.",
    ])


# ---------------------------------------------------------------------- blk.board-id

def draw_board_id(s, variants):
    f = Flow(s)
    grp(f, lambda: ic_group(
        s, "AT24C02D at I2C2 0x50", "microchip", "AT24C02D-STUM-T",
        {"SCL": "I2C2_SCL", "SDA": "I2C2_SDA", "WP": "GND", "VCC": "vcca1v8_pmu", "GND": "GND"},
        rows=[[("C_100n_0402", "vcca1v8_pmu", "GND")]]))
    s.iface_rows = [["I2C2_SCL, I2C2_SDA", "Bidirectional", "0x50; pull-ups on blk.soc-pmuio"]]
    s.rail_rows = [["vcca1v8_pmu", "100 nF", "8871F (value: capture choice)"]]
    corner_notes(s, [
        "1. Function: the board identity EEPROM (board revision, variant, serial), read by Blackbird OS.",
        "2. Absent state: never omitted. Supply vcca1v8_pmu, as the rest of I2C2 (G16 proposal).",
        "3. WP tied low: writable; write protection by software. The supply rail is the G16 proposal,",
        "   not stated in the BOM.",
    ])


# ---------------------------------------------------------------------- blk.imu

def draw_imu(s, variants):
    f = Flow(s)
    grp(f, lambda: ic_group(
        s, "LSM6DSV16X at I2C2 0x6A (BOM v1 line 59)", "stmicroelectronics", "LSM6DSV16XTR",
        {"SDA": "I2C2_SDA", "SCL": "I2C2_SCL", "CS": "IMU_VDD", "SDO/SA0": "GND", "INT1": "IMU_INT1",
         "INT2": None, "SDx/AH1/Qvar1": "GND", "SCx/AH2/Qvar2": "GND", "OCS_Aux": None, "SDO_Aux": None,
         "Vdd": "IMU_VDD", "Vdd_IO": "IMU_VDD", "GND": "GND"},
        rows=[[("C_100n_0402", "IMU_VDD", "GND"), ("C_100n_0402", "IMU_VDD", "GND")]]))
    grp(f, lambda: link_group(s, "LINK_L10", "vcca1v8_pmu", "IMU_VDD", variants, "Link #32"))
    s.iface_rows = [["I2C2_SCL, I2C2_SDA", "Bidirectional", "0x6A (SA0 low); pull-ups on blk.soc-pmuio"],
                    ["IMU_INT1", "Output", "GPIO0_C5 (PMUIO2), wake on motion; SoC pull-down: no wake unfitted"]]
    s.rail_rows = [["IMU_VDD", "100 nF at Vdd, 100 nF at Vdd_IO", "DS13510 §6 (C1, C2)"]]
    corner_notes(s, [
        "1. Function: LSM6DSV16X 6-axis IMU, wake on motion through INT1 (BRD-032, should).",
        "2. Absent state: unfitted: INT1 pulled down by the SoC, 0x6A free. Always on (vcca1v8_pmu, G1).",
        "3. CS to Vdd_IO selects I2C; SA0 low; SDx, SCx to GND (analog hub and Qvar off); OCS_Aux and",
        "   SDO_Aux open (internal pull-ups, DS13510 Table 23); INT2 open.",
        "4. Vdd and Vdd_IO from vcca1v8_pmu through link #32, 10 Ω (BOM v1 lines 59, 137; power tree",
        "   §4.12: 0.65 mA, 6.5 mV).",
    ])


# ---------------------------------------------------------------------- blk.speaker

def draw_speaker(s, variants):
    f = Flow(s)
    grp(f, lambda: ic_group(
        s, "MAX98357A, I2S3 (BOM v1 line 32)", "analog-devices", "MAX98357AETE",
        {"DIN": "SPK_SDIN", "BCLK": "SPK_BCLK", "LRCLK": "SPK_LRCK", "SD_MODE": "SPK_SD", "GAIN_SLOT": "SPK_GAIN",
         "OUTP": "SPK_P", "OUTN": "SPK_N", "VDD": "SPK_VDD", "NC": None, "GND": "GND", "EP": "GND"},
        rows=[[("C_10u_0603", "SPK_VDD", "GND"), ("C_100n_0402", "SPK_VDD", "GND"), ("R_100k", "SPK_VDD", "SPK_GAIN")]]))
    grp(f, lambda: link_group(s, "LINK_M", "VSYS_LV", "SPK_VDD", variants, "Link #17"))

    def mode():
        g = Group(s, "SD_MODE select position (DS Figure 5)")
        g.add(two_pin_box(s, "R_0_0402", 101.6, 101.6, "SPK_SD_MODE", "SPK_SD"))
        return g.close()
    grp(f, mode)

    def pads():
        g = Group(s, "Speaker spring-contact pads (BOM v1 line 33)")
        for i, net in enumerate(("SPK_P", "SPK_N")):
            x = 116.84 + i * 17.78
            tp(s, x, 101.6, net, text="left", key="TP")   # spring-contact pad
            s.point(net, x, 101.6, "down", "pas")
            g.add((x - 2.54 - len(net) * 1.16, 93.98, x + 2.54, 101.6 + 2.54 + len(net) * 1.16))
        return g.close()
    grp(f, pads)
    s.iface_rows = [["SPK_BCLK, SPK_LRCK, SPK_SDIN", "Input", "I2S3_M0 at 3.3 V; 22 Ω at the SoC for the clocks"],
                    ["SPK_SD_MODE", "Input", "GPIO3_A6, SoC pull-down and the 100 kΩ internal pull-down: shutdown"]]
    s.rail_rows = [["SPK_VDD", "10 µF + 100 nF", "MAX98357A Rev 11 p. 33"]]
    corner_notes(s, [
        "1. Function: MAX98357A mono class-D amplifier for the internal speaker (0.7 W, BOM line 33).",
        "2. Absent state: SD_MODE low: shutdown (0.6 µA).",
        "3. GAIN_SLOT 100 kΩ to VDD: 3 dB, the lowest gain (Rev 11 Table 8), with the Blackbird OS",
        "   limiter keeping the speaker inside its rating; the gain is a capture choice.",
        "4. SD_MODE driven at 3.3 V selects the left channel; the 0 Ω position takes the select",
        "   resistor of Figure 5 if (L+R)/2 is wanted (pinout v1 B8).",
        "5. VDD from VSYS_LV through link #17, 0.1 Ω (power tree §4.12: 0.3 A peak, 30 mV).",
    ])


# ---------------------------------------------------------------------- blk.microsd

def draw_microsd(s, variants):
    f = Flow(s)
    grp(f, lambda: ic_group(
        s, "DM3AT-SF-PEJM5 socket (BOM v1 line 11)", "hirose", "DM3AT-SF-PEJM5",
        {"VDD": "SD_VDD", "CD/DAT3": "SD_D3_C", "CMD": "SD_CMD_C", "CLK": "SD_CLK_C", "DAT0": "SD_D0_C",
         "DAT1": "SD_D1_C", "DAT2": "SD_D2_C", "DET_A": "SD_DET_C", "DET_B": "GND", "VSS": "GND", "SHIELD": "GND"},
        rows=[[("C_10u_0603", "SD_VDD", "GND"), ("C_100n_0402", "SD_VDD", "GND")]], prefix="J"))

    def series():
        g = Group(s, "Series resistors (HDG p. 52)")
        for i, n in enumerate(("CLK", "CMD", "D0", "D1", "D2", "D3")):
            g.add(two_pin_box(s, "R_22", 101.6, 101.6 + i * 10.16, f"SD_{n}", f"SD_{n}_C"))
        g.add(two_pin_box(s, "R_100", 101.6, 101.6 + 6 * 10.16, "SD_DET_N", "SD_DET_C"))
        return g.close()
    grp(f, series)

    def esd():
        from draw import ic
        g = Group(s, "ESD: 2 x TPD4E05U06 (BOM v1 line 73)")
        x = 101.6
        for a, b, c, d in (("SD_CLK_C", "SD_CMD_C", "SD_D0_C", "SD_D1_C"), ("SD_D2_C", "SD_D3_C", None, None)):
            u = ic(s, "texas-instruments", "TPD4E05U06DQAR", x, 101.6,
                   {"D1+": a, "D1-": b, "D2+": c, "D2-": d, "NC": None, "GND": "GND"})
            g.add(u.bbox)
            x = snap(x + (u.bbox[2] - u.bbox[0]) + 7.62)     # the next one 7.62 mm clear of this one's text
        return g.close()
    col = Flow(s, x0=snap(f.x_right + f.gap), gap=2.54)   # ESD above the link, inside the circuit band
    col.x_max = col.x0 + 100.0
    grp(col, esd)
    grp(col, lambda: link_group(s, "LINK_M", "vcc3v3_sd", "SD_VDD", variants, "Link #16"))
    s.iface_rows = [
        ["SD_CLK, SD_CMD, SD_D0-D3", "Bidirectional", "SDMMC0 on VCCIO3 (vccio_sd, 1.8 / 3.3 V)"],
        ["SD_DET_N", "Output", "SDMMC0_DET boot strap: SoC pull-up = no card; the socket switch pulls low"],
        ["vcc3v3_sd", "Supply in", "RK809 SWOUT2"],
    ]
    s.rail_rows = [["SD_VDD", "10 µF + 100 nF", "Capture choice (socket datasheet silent)"]]
    corner_notes(s, [
        "1. Function: microSD socket on SDMMC0 (UHS-I SDR104 at 1.8 V signalling).",
        "2. Absent state: card absent is normal: SD_DET_N high through the SoC pull-up; while it is",
        "   high SDMMC0 carries UART2/JTAG M1 (HDG p. 20).",
        "3. 22 Ω series on every line, 100 Ω on detect (HDG p. 52); TPD4E05U06 (0.5 pF) at the socket.",
        "4. Detect switch wiring (DET_A to the line, DET_B to GND) against the Hirose drawing: UNVERIFIED.",
        "5. VDD from vcc3v3_sd through link #16, 0.1 Ω (power tree §4.12: 0.2 A, 20 mV).",
    ])


# ---------------------------------------------------------------------- blk.buttons

BUTTONS = [("Power (also MaskROM)", "PWRON_N", "SW_PTS815"), ("Vol+ (recovery key)", "SARADC_VOLUP", "SW_PTS815"),
           ("Vol- (MaskROM)", "VOLDN_N", "SW_PTS815"), ("Action", "ACTION_BTN_N", "SW_ACTION")]


def draw_buttons(s, variants):
    """blk.buttons (#47): four switches to ground, one TPD1E10B06 per line (BOM v1 lines 74, 76, 77);
    the pulls sit with the inputs they serve (blk.soc-pmuio, blk.pmic) except Vol-'s, here."""
    f = Flow(s)

    def switches():
        g = Group(s, "Buttons (BOM v1 lines 76, 77)")
        x = 101.6
        for title, net, key in BUTTONS:
            # pin 1 up to the line, pin 2 down to ground; text right of the body
            # the fields of a turned symbol read centred: each centre half its text right of the body
            from parts import PARTS
            vw = len(PARTS[key]["value"]) * 1.16
            part(s, "Switch", "SW_Push", x, 101.6, {"1": net, "2": "GND"}, key=key, angle=270, prefix="SW",
                 ref_at=(snap(x + 2.54 + 3.5), 100.33), val_at=(snap_up(x + 2.54 + vw / 2), 102.87))
            x += max(30.48, snap_up(2.54 + vw + 12.7))
        g.add((101.6 - 5.08, 101.6 - 7.62 - len("SARADC_VOLUP") * 1.27, x - 2.54, 101.6 + 15.24))
        return g.close()
    grp(f, switches)

    def pull():
        g = Group(s, "Vol- pull-up 100 kΩ (pinout v1 §4)")
        g.add(prow(s, 101.6, 109.22, [("R_100k", "vcca1v8_pmu", "VOLDN_N")]))
        return g.close()
    grp(f, pull)
    grp(f, lambda: tvs_group(s, "ESD: 4 x TPD1E10B06 (BOM v1 line 74)", [n for _, n, _ in BUTTONS]), newline=True)
    s.iface_rows = [
        ["PWRON_N", "Output", "RK809 PWRON (blk.pmic, 100 nF there); also blk.maskrom through the BAT54"],
        ["SARADC_VOLUP", "Output", "SARADC_VIN0: 10 kΩ to vcca_1v8 and 1 nF on blk.soc-pmuio; reads released"],
        ["VOLDN_N", "Output", "SARADC_VIN1 and the MaskROM gate: 100 kΩ to vcca1v8_pmu here, 1 nF at the SoC"],
        ["ACTION_BTN_N", "Output", "GPIO0_C2 wake: 4.7 kΩ to vcca1v8_pmu on blk.soc-pmuio; reads released"],
    ]
    corner_notes(s, [
        "1. Function: the four body buttons (T1-014, T1-015; BRD-016, -017, -035, -036): Power to the",
        "   RK809 PWRON, Vol+ and Vol- on their own SARADC inputs, Action on a PMUIO2 wake ball.",
        "2. Absent state: never omitted; released lines read high through their pulls.",
        "3. Vol- is pulled to the always-on vcca1v8_pmu, which also feeds the MaskROM gate: a pull to",
        "   vcca_1v8 would read pressed while that rail is still off (pinout v1 §4, Vol- row).",
        "4. Open: the Action part (BOM v1 line 76; T1-022 deeper travel); KMR221GLFS is the BOM's",
        "   placeholder on the KMR2 land. The PTS815 land (T1_Main_Board:SW_CK_PTS815) is not drawn:",
        "   which terminals are common is not legible in the C&K copy (PTS 815 p. B-44), UNVERIFIED.",
    ])
