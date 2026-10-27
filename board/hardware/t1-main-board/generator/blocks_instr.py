"""Instrumentation, indicators, boot and debug access: blk.current-monitors (#18), blk.status-led
(#25), blk.mic-ambient (#38), blk.maskrom (#48), blk.debug (#49) and blk.cover-detect (#50).

Sources: BOM v1 lines 34, 35, 54, 74, 78, 79, 86-89, 97, 98, 105, 136, 137, 143; power tree v0
§4.12 (links and INA236 positions); pinout v1 §3 and the ball table; feature blocks records 18,
25, 38, 48-50 and G10-G12, G22; TI SBOSA81D (INA236), SNVS441I (LP5521), SBVS050N (TPS3808),
SCES414P / SCES415N (SN74LVC1G57 / 1G58); Infineon IM73D122V01 data sheet v1.00; Vishay doc
30100 (WSL); the parts-lib sheets."""

from __future__ import annotations

from blocks_audio import grp, two_pin_box
from draw import Flow, Group, corner_notes, ic, prow, row_need
from sch import snap


def sheets(proj):
    cmon = proj.sheet("current-monitors.kicad_sch", "blk.current-monitors", "Current monitors",
                      "Five INA236 on I2C1 and their shunts: VSYS, audio (VSYS_LV and VSYS sides), display, HAT",
                      "A3")
    return cmon


# ---------------------------------------------------------------------- blk.current-monitors

# Power tree §4.12 INA236 positions (G11) and BOM v1 lines 54, 136: address, A0 strap (SBOSA81D
# Table 7-1), supply-side net, load-side net, shunt part, title.
CHANNELS = [
    ("0x40", "INA236AIDDFR", "GND", "VSYS_SRC", "VSYS", "R_SHUNT_10m_2512",
     "VSYS at 0x40: BQ25798 SYS output, 10 mΩ (line 54)"),
    ("0x41", "INA236AIDDFR", "vcc3v3_sys", "VSYS_LV", "VSYS_LV_AUDIO", "R_SHUNT_20m_1206",
     "Audio, VSYS_LV side, at 0x41: 20 mΩ (line 54, G11)"),
    ("0x42", "INA236AIDDFR", "I2C1_SDA", "VSYS_LV", "VSYS_LV_BL", "R_SHUNT_100m_1206",
     "Display at 0x42: TPS61160 VIN, 100 mΩ (line 54)"),
    ("0x43", "INA236AIDDFR", "I2C1_SCL", "VSYS", "VSYS_P5V1", "R_SHUNT_20m_2010",
     "HAT at 0x43: 5.1 V buck input, 20 mΩ (line 54)"),
    ("0x48", "INA236BIDDFR", "GND", "VSYS", "VSYS_AUDIO", "R_SHUNT_20m_1206",
     "Audio, VSYS side, at 0x48: LMR33630C VIN, 20 mΩ (line 136)"),
]


def channel(s, title, mpn, a0, src, load, key):
    """One INA236 with its VS bypass and its shunt below it. IN+ takes the supply side, IN- the
    load side (SBOSA81D Table 5-1); the load-side net is fed through the shunt only, so it takes
    its PWR_FLAG on the shunt's load-side wire, outside the IC's text (CRAFT-85)."""
    def draw():
        g = Group(s, title)
        u = ic(s, "Texas_Instruments", mpn, 101.6, 101.6,
               {"IN+": src, "IN-": load, "VS": "vcc3v3_sys", "GND": "GND", "SCL": "I2C1_SCL",
                "SDA": "I2C1_SDA", "A0": a0, "ALERT": None})
        g.add(u.bbox)
        r = [("C_100n_0402", "vcc3v3_sys", "GND")]
        g.add(prow(s, u.bbox[2] + 5.08, snap(u.bbox[1] + row_need(r) + 3.81), r))
        y = snap(u.bbox[3] + 12.7)
        x = snap(u.bbox[0] + 30.48)
        g.add(two_pin_box(s, key, x, y, src, load, stub=7.62, extra={"Constraints": "PCB-T-02"}))
        s.flag_at(snap(x + 3.81 + 5.08), y, "down", 2.54)
        g.add((x, y, x + 12.7, y + 12.7))
        return g.close()
    return draw


def draw_current_monitors(s, variants):
    f = Flow(s)
    for k, (addr, mpn, a0, src, load, key, title) in enumerate(CHANNELS):
        grp(f, channel(s, title, mpn, a0, src, load, key), newline=(k == 3))
    s.iface_rows = [
        ["I2C1_SCL, I2C1_SDA", "Bidirectional", "0x40-0x43 (INA236A) and 0x48 (INA236B) free; pull-ups on blk.soc-pmuio"],
        ["VSYS_SRC, VSYS, VSYS_LV", "Supply in", "The shunts stay in circuit (power tree §5); VSYS_SRC from the BQ25798 SYS"],
        ["VSYS_LV_AUDIO, VSYS_AUDIO", "Supply out", "Through their shunts: blk.audio-supply, blk.mclk, blk.hpa-rails-pre"],
        ["VSYS_LV_BL, VSYS_P5V1", "Supply out", "Through their shunts: TPS61160 VIN (blk.fp-backlight), TPS62903 VIN (blk.pwr-5v1)"],
    ]
    s.rail_rows = [["vcc3v3_sys", "100 nF per INA236", "SBOSA81D §8.3: 0.1 µF at VS"]]
    corner_notes(s, [
        "1. Function: power instrumentation (T1-026, must): five INA236 on I2C1 at 1.8 V (VIH 0.9 V at any",
        "   VS, SBOSA81D §6.5), VS on vcc3v3_sys; positions and shunts per power tree §4.12 (G11).",
        "2. Absent state: an INA236 unfitted leaves its shunt in circuit and its address free (power tree",
        "   §5). The parts power up converting (MODE 111b, 0.3 mA each): Blackbird OS writes power-down.",
        "3. Shunts (Vishay WSL, doc 30100): 10 mΩ 2512 1 W (VSYS: 58 mW at 2.4 A, 0.36 W at the 6 A",
        "   BATFET rating); 20 mΩ 2010 0.5 W (HAT, line 54 asks for 0.5 W or more); 20 mΩ 1206 (audio);",
        "   100 mΩ 1206 (display: 11 mW at 0.33 A). Full scale 81.92 mV / R: 8.2, 4.1, 0.82 A.",
        "4. A0: GND, VS, SDA, SCL for 0x40-0x43 (SBOSA81D Table 7-1). A0 = SDA needs 100 ns more hold on",
        "   the address MSB (p. 16): the RK3566 I2C1 against it is UNVERIFIED (bring-up check at 0x42).",
        "5. ALERT open (may float, SBOSA81D Table 5-1). Kelvin traces from IN+ and IN- to the shunt pads",
        "   (SBOSA81D §8.4.1); never issue a general-call reset on I2C1 (it resets all five, p. 18).",
    ])

