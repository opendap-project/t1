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
    led = proj.sheet("status-led.kicad_sch", "blk.status-led", "Status LED driver",
                     "LP5521 RGB LED driver on I2C2 at 0x32: charge pump, LED_R/G/B to the faceplate, link #22", "A4")
    dbg = proj.sheet("debug.kicad_sch", "blk.debug", "Test and debug access",
                     "Debug UART, I2S/DSD and bring-up pads, spare GPIO pads and rail test pads", "A3")
    cov = proj.sheet("cover-detect.kicad_sch", "blk.cover-detect", "Cover detect",
                     "Back-cover detect input: board-edge contact pads, pull-up, ESD", "A4")
    amb = proj.sheet("mic-ambient.kicad_sch", "blk.mic-ambient", "Ambient microphone",
                     "IM73D122 PDM microphone on PDM CLK1 and SDI1, on its own MIC_1V8 branch (link #35)", "A4")
    return cmon, led, dbg, cov, amb


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


# ---------------------------------------------------------------------- blk.status-led

def draw_status_led(s, variants):
    """blk.status-led (#25): LP5521 (BOM v1 line 105) on the main board, LED_R, LED_G, LED_B to the
    faceplate status LED (line 79) through the faceplate connector (ESD there, line 75)."""
    from blocks_audio import link_group
    from blocks_should import column
    f = Flow(s)
    pins = {"VDD": "LED_VDD", "EN": "vcca1v8_pmu", "SCL": "I2C2_SCL", "SDA": "I2C2_SDA", "ADDR_SEL0": "",
            "ADDR_SEL1": "", "TRIG": "", "CLK_32K": "", "CFLY1P": "LED_CFLY1P", "CFLY1N": "LED_CFLY1N",
            "CFLY2P": "LED_CFLY2P", "CFLY2N": "LED_CFLY2N", "VOUT": "LED_VOUT", "R": "LED_R", "G": "LED_G",
            "B": "LED_B", "INT": None, "GPO": None, "NC": None, "GND": "GND", "EP": "GND"}

    def driver():
        g = Group(s, "LP5521 at I2C2 0x32 (BOM v1 line 105; SNVS441I Figure 26)")
        u = ic(s, "Texas_Instruments", "LP5521YQX", 101.6, 101.6, pins)
        g.add(u.bbox)
        # ADDR_SEL0, ADDR_SEL1 (0x32), TRIG and CLK_32K (internal clock) on one ground collector; its
        # symbol hangs off the top row, clear of the flying-capacitor labels below
        ends = sorted((u.pos(u.pin(k)) for k in ("20", "21", "7", "5")), key=lambda e: e[1])
        xc = snap(ends[0][0] - 5.08)
        for ex, ey in ends:
            s.wire((ex, ey), (xc, ey))
        s.wire((xc, ends[0][1]), (xc, ends[-1][1]))
        for _, ey in ends[1:-1]:
            s.junction(xc, ey)
        xg = snap(xc - 5.08)
        s.junction(xc, ends[0][1])
        s.wire((xc, ends[0][1]), (xg, ends[0][1]), (xg, ends[0][1] + 2.54))
        s.power("GND", xg, ends[0][1] + 2.54)
        g.add((xg - 2.54, ends[0][1], xc, ends[0][1] + 7.62))
        rx, ry = u.bbox[2] + 5.08, u.bbox[1]
        for r in [[("C_1u_0402", "LED_VDD", "GND"), ("C_1u_0402_10V", "LED_VOUT", "GND")],
                  [("C_470n_0402", "LED_CFLY1P", "LED_CFLY1N"), ("C_470n_0402", "LED_CFLY2P", "LED_CFLY2N")]]:
            b = g.add(prow(s, rx, snap(ry + row_need(r) + 3.81), r))
            ry = b[3] + 2.54
        return g.close()
    grp(f, driver)
    col = column(s, f)
    grp(col, lambda: link_group(s, "LINK_M", "VSYS_LV", "LED_VDD", variants, "Link #22"))
    s.iface_rows = [
        ["I2C2_SCL, I2C2_SDA", "Bidirectional", "0x32 (ADDR_SEL0, ADDR_SEL1 low); pull-ups on blk.soc-pmuio. Unfitted: 0x32 free"],
        ["LED_R, LED_G, LED_B", "Output", "Open: nothing drives or back-powers them; in use, current sources up to 25.5 mA to contacts 30-32"],
    ]
    s.rail_rows = [
        ["LED_VDD", "1 µF", "SNVS441I p. 37: CIN 1 µF"],
        ["LED_VOUT", "1 µF 10 V", "SNVS441I p. 37: COUT 1 µF, 10 V for DC bias"],
        ["LED_CFLY1, LED_CFLY2", "2 x 470 nF", "SNVS441I p. 37: CFLY1, CFLY2 470 nF"],
    ]
    corner_notes(s, [
        "1. Function: LP5521 RGB driver for the faceplate status LED (FPT-003, FPT-016 must; FPT-025",
        "   should): three current sources with PWM and program engines; mainline leds-lp5521 (DKMS).",
        "2. Absent state: faceplate detached: the outputs are open, nothing back-powers. Unfitted:",
        "   0x32 free, LED lines open. Standby 1 µA with EN high and CHIP_EN = 0 (SNVS441I p. 6).",
        "3. EN on vcca1v8_pmu: always enabled, and the I2C levels follow EN (1.8 V, I2C2). VDD from",
        "   VSYS_LV 3.8 V through link #22, 0.1 Ω (power tree §4.12: 0.1 A est., 10 mV).",
        "4. Internal clock: CLK_32K to GND; TRIG to GND (SNVS441I §7.3.5.3, §7.3.5.5); INT and GPO",
        "   open (no SoC line in pinout v1). The R channel runs from VDD (R_TO_BATT, BOM line 105).",
        "5. Each channel is capped at 20 mA in the devicetree (80 % of the LED's 25 mA IF, line 79).",
    ])


# ---------------------------------------------------------------------- blk.debug

def spare_pads():
    """The spare SoC GPIOs pinout v1 puts on a test pad (blk.debug rows whose notes name one)."""
    import pinout
    out = []
    for ball, r in sorted(pinout.load().items(), key=lambda kv: (kv[1]["net"] or "")):
        if r["block"] == "blk.debug" and r["net"] and r["net"].startswith("SPARE_") and "test pad" in r["notes"]:
            out.append(r["net"])
    return out


def gnd_pad(s, x, y):
    """A ground test pad (BOM v1 lines 87, 88: GND beside the signal pads)."""
    from draw import tp
    tp(s, x, y, "GND", text="left")
    s.wire((x, y), (x, y + 2.54))
    s.power("GND", x, y + 2.54)
    return (x - 7.62, y - 7.62, x + 2.54, y + 7.62)


def pad_row(s, title, nets, gnd=False):
    """Signal pads, each with its net hanging below it (blocks_should.pads), and an optional ground pad."""
    from draw import tp

    def draw():
        g = Group(s, title)
        x = 116.84
        for net in nets:
            tp(s, x, 101.6, net, text="left")
            s.point(net, x, 101.6, "down", "pas")
            g.add((x - 2.54 - len(net) * 1.16, 93.98, x + 2.54, 101.6 + 2.54 + len(net) * 1.16))
            x += 17.78
        if gnd:
            g.add(gnd_pad(s, x, 101.6))
        return g.close()
    return draw


def probed(proj, skip):
    """Nets that already carry a test pad on another sheet (its value names the net)."""
    return {val for sh, pl, f, val, *_ in proj.parts if sh is not skip and pl.sym.lib_id == "Connector:TestPoint"}


def draw_debug(s, variants):
    """blk.debug (#49): access for bring-up and measurement (BRD-040, BRD-047; T1-026; PCB-T-01,
    -02, -09). Drawn after every other block: the rail pads cover the rails no sheet probes yet."""
    from blocks_charger import rail_probe
    from sch import RAILS
    f = Flow(s)
    grp(f, pad_row(s, "Debug UART2 M0, 1.8 V (BOM v1 line 87; PCB-T-01)", ["DBG_UART_TX", "DBG_UART_RX"], gnd=True))
    grp(f, pad_row(s, "I2S and DSD (BOM v1 line 88; BRD-040)",
                   ["I2S_BCLK", "I2S_LRCK", "I2S_SDO0", "DSD_L", "DSD_R"], gnd=True))
    grp(f, pad_row(s, "Reset, PMIC and power key (PCB-T-09)", ["SOC_RESET_N", "PMIC_INT_N", "PMIC_SLEEP", "PWRON_N"]))
    spares = spare_pads()
    half = (len(spares) + 1) // 2
    grp(f, pad_row(s, "Spare SoC GPIOs (pinout v1; PCB-T-09)", spares[:half]), newline=True)
    grp(f, pad_row(s, "Spare SoC GPIOs, continued", spares[half:]))
    used = sorted(r for r in s.project.rails_used if r != "GND")
    have = probed(s.project, s)
    rails = [r for r in RAILS if r in used and r not in have]

    def rail_pads():
        g = Group(s, "Rail test pads (PCB-T-02, BOM v1 line 86): the rails no other sheet probes")
        per = 8
        for i, net in enumerate(rails):
            x, y = 116.84 + (i % per) * 43.18, 101.6 + (i // per) * 22.86
            g.add(rail_probe(s, net, x, y))
        return g.close()
    if rails:
        grp(f, rail_pads, newline=True)
    s.iface_rows = [
        ["DBG_UART_TX, DBG_UART_RX", "Bidirectional", "Pads only (1.8 V, PMUIO2); the SoC pull-ups hold the idle level"],
        ["I2S_BCLK, I2S_LRCK, I2S_SDO0, DSD_L, DSD_R", "Input", "Pads only on the DAC path (BRD-040); no load"],
        ["SOC_RESET_N, PMIC_INT_N, PMIC_SLEEP, PWRON_N", "Input", "Pads only"],
        ["SPARE_*", "Bidirectional", "Pads only; each ball keeps its reset pull (pinout v1)"],
    ]
    s.rail_rows = [["(none)", "-", "Pads only: no decoupling on this sheet"]]
    corner_notes(s, [
        "1. Function: test and debug access (BRD-040, BRD-047 must; T1-026): the BootROM, TPL and U-Boot",
        "   console on UART2 M0 at 1.8 V (a 1.8 V USB-UART adapter), the I2S/DSD lines at the DAC path,",
        "   reset and PMIC pads, the spare SoC GPIOs, and a pad on every rail no other sheet probes.",
        "2. Absent state: pads only, nothing fitted. The block's measurement links sit on their blocks'",
        "   sheets (power tree §4.12); the RP2354A SWD pads on blk.rp2354-core; one MCLK pad on each DAC sheet.",
        "3. Spares pinout v1 leaves without a pad (the audio-bank balls next to I2S1, FSPI_D3) carry",
        "   no-connect flags on the SoC sheets; GPIO0_A6 is the cover detect input (blk.cover-detect).",
        "4. I2S/DSD pads: BCLK is also the DSD clock (DSDCLK from I2S_BCLK, blk.dac-l/-r); stubs from",
        "   the DAC path at most 1 mm, as the coprocessor taps (PCB-A-12).",
    ])


# ---------------------------------------------------------------------- blk.cover-detect

def draw_cover_detect(s, variants):
    """blk.cover-detect (#50): BOM v1 line 143, PCB-L-10, ADR 0020 item 7, G22 (pinout v1 §7)."""
    from blocks_audio import tvs_group
    from parts import fields
    import library
    f = Flow(s)

    def contact():
        g = Group(s, "Contact pads at the board edge (BOM v1 line 143; PCB-L-10)")
        tsym = library.load("Connector", "TestPoint")
        for i, (net, val) in enumerate((("COVER_DET_N", "COVER"), ("GND", "COVER_GND"))):
            x = 116.84 + i * 25.4
            ref = s.next_ref("TP")
            s.place(tsym, ref, x, 101.6, fields=fields("PAD_COVER", s.block), value=val, in_bom=False,
                    ref_at=(x - 1.27, 96.52), val_at=(x - 1.27, 99.06))
            from draw import _justify_right
            _justify_right(s)
            if net == "GND":
                s.wire((x, 101.6), (x, 104.14))
                s.power("GND", x, 104.14)
            else:
                s.point(net, x, 101.6, "down", "pas")
        g.add((116.84 - 2.54 - 12.0, 93.98, 116.84 + 25.4 + 2.54, 101.6 + 2.54 + len("COVER_DET_N") * 1.16))
        return g.close()
    grp(f, contact)

    def pull():
        g = Group(s, "Pull-up to vcc3v3_pmu")
        g.add(prow(s, 101.6, 109.22, [("R_100k", "vcc3v3_pmu", "COVER_DET_N")]))
        return g.close()
    grp(f, pull)
    grp(f, lambda: tvs_group(s, "ESD at the pad (TPD1E10B06)", ["COVER_DET_N"]))
    s.iface_rows = [
        ["COVER_DET_N", "Output", "GPIO0_A6 reset pull-down reads cover closed; the description omits the input (dnp)"],
    ]
    s.rail_rows = [["(none)", "-", "No supply on this sheet: the pull-up hangs from vcc3v3_pmu"]]
    corner_notes(s, [
        "1. Function: back-cover detect (ADR 0020 item 7, should): low while the cover is closed; on",
        "   a rise Blackbird OS syncs storage and powers off in order (ADR 0017 item 3), before the",
        "   pack can be reached. It protects data, never safety (T1-086 is met without it).",
        "2. Absent state: dnp: the ball's reset pull-down holds the cover-closed level and the device",
        "   description omits the input; no other block depends on it.",
        "3. GPIO0_A6 (PMUIO1, 3.3 V, wake-capable; pinout v1 §7, G22). 100 kΩ to vcc3v3_pmu: 33 µA",
        "   with the cover closed; VIH 2.0 V holds with up to 13 µA of leakage (DS 1.1 Table 3-3).",
        "   Pinctrl turns the ball's 16-43 kΩ pull-down off. Software: gpio-keys (a switch event).",
        "4. Open (case input): the actuator. Two pads, the input and ground, take a conductive bridge",
        "   on the cover or a two-terminal switch on the same lands; pad size UNVERIFIED.",
    ])


# ---------------------------------------------------------------------- blk.mic-ambient

def draw_mic_ambient(s, variants):
    """blk.mic-ambient (#38): IM73D122V01 (BOM v1 line 34) on PDM CLK1 / SDI1 (pinout v1 AK2, 1P2),
    powered from MIC_1V8 through link #35 (power tree §4.12, G10)."""
    from blocks_audio import ic_group, link_group
    from blocks_should import column
    f = Flow(s)
    grp(f, lambda: ic_group(
        s, "IM73D122 bottom-port PDM microphone (BOM v1 line 34)", "Infineon", "IM73D122V01XTMA1",
        {"VDD": "MIC_AMB_VDD", "CLOCK": "MIC_AMB_CLK", "DATA": "PDM_DATA1", "LR": "GND", "GND": "GND"},
        rows=[[("C_1u_0402", "MIC_AMB_VDD", "GND"), ("C_100n_0402", "MIC_AMB_VDD", "GND")]], prefix="MK"))

    def series():
        g = Group(s, "PDM clock series (pinout v1 AK2)")
        g.add(two_pin_box(s, "R_22", 101.6, 101.6, "PDM_CLK1", "MIC_AMB_CLK"))
        return g.close()
    col = column(s, f)
    grp(col, lambda: link_group(s, "LINK_L10", "MIC_1V8", "MIC_AMB_VDD", variants, "Link #35"))
    grp(col, series)
    s.iface_rows = [
        ["PDM_CLK1", "Input", "PDM_CLK1_M1 (GPIO4_A0), parked low while MIC_1V8 is off (G10)"],
        ["PDM_DATA1", "Output", "PDM_SDI1_M1 (GPIO4_A1); its SoC pull-down holds a level (pinout v1 1P2)"],
        ["MIC_1V8", "Supply in", "From blk.mic-main: off with MIC_EN, so the privacy LED covers this microphone"],
    ]
    s.rail_rows = [["MIC_AMB_VDD", "1 µF + 100 nF", "IM73D122 DS v1.00 Table 5 note 4 (1 µF) and §3.5 (100 nF)"]]
    corner_notes(s, [
        "1. Function: ambient-noise microphone on the body (BRD-031, should); the second PDM channel",
        "   of the SoC (PDM CLK1, SDI1), described as a sensor. BRD-027: it shares MIC_1V8 with the",
        "   faceplate microphone, so it never runs without the privacy LED's supply.",
        "2. Absent state: unfitted: SDI1 held by the SoC pull-down, CLK1 parked low.",
        "3. LR to GND: data driven on the falling clock edge (DATA1, DS v1.00 Table 8), the only",
        "   microphone on SDI1. 22 Ω series on the clock at the SoC (pinout v1 AK2).",
        "4. VDD from MIC_1V8 through link #35, 10 Ω (power tree §4.12: 1 mA or less, est.).",
        "5. PCB: 0.8 mm acoustic port under the microphone, ground ring as the land (DS v1.00 Fig. 13).",
    ])
