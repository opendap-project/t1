"""blk.audio and its children (feature blocks #27-34), the headphone jacks (#35, #36) and the
audio host-side parts on blk.soc-vccio-b.

Sources: board ADRs 0001, 0010, 0012, 0015, 0019; BOM v1 lines 18-37, 107-111, 116-119, 133-135,
137, 139-141; power tree v0 §2, §3, §4.12, §5, §6.2-6.3; pinout v1 §3 (audio balls, expander
lines); feature blocks §3.5; PCB design constraints PCB-A-01 to A-19; the parts-lib sheets.
Circuits are wired through labels at the IC pins; small networks are hand-wired."""

from __future__ import annotations

import library
from draw import (Flow, Group, corner_notes, divider, hbox, hpart, ic, link, link_variants, part, prow, row_need,
                  two_pin_h, two_pin_v, under, vpart)
from sch import snap, snap_up

KIDS = ["audio-supply", "mclk", "dac-l", "dac-r", "hpa-rails", "hpa-se", "hpa-bal"]
RAIL_KIDS = ["hpa-rails-pre", "hpa-rails-ldo"]
BAL_KIDS = ["hpa-bal-l", "hpa-bal-r"]


def reading_order():
    """blk.audio's sheets in reading order: each parent followed by its own sub-sheets."""
    out = []
    for k in KIDS:
        out.append(k)
        out += {"hpa-rails": RAIL_KIDS, "hpa-bal": BAL_KIDS}.get(k, [])
    return out


def sheets(proj):
    parent = proj.sheet("audio.kicad_sch", "blk.audio", "Audio", "The audio converter boundary: DAC supplies, "
                        "master clocks, two CS43198, the amplifier rails and both output stages", "A4")
    kids = {
        "audio-supply": proj.sheet("audio-supply.kicad_sch", "blk.audio-supply", "Audio: DAC supplies",
                                   "DAC_VP and DAC_DIG_1V8 load switches and the AUDIO_2V2 pre-buck, with their links", "A3"),
        "mclk": proj.sheet("mclk.kicad_sch", "blk.mclk", "Audio: master clocks",
                           "Two oscillators at twice the MCLK, their LDOs and interlock, one divider per DAC (ADR 0019)", "A3"),
        "dac-l": proj.sheet("dac-l.kicad_sch", "blk.dac-l", "Audio: DAC left",
                            "CS43198 for the left channel in mono mode, its VA LDO and serial-port series parts", "A3"),
        "dac-r": proj.sheet("dac-r.kicad_sch", "blk.dac-r", "Audio: DAC right",
                            "CS43198 for the right channel in mono mode, its VA LDO and serial-port series parts", "A3"),
        "hpa-rails": proj.sheet("hpa-rails.kicad_sch", "blk.hpa-rails", "Audio: amplifier rails",
                                "+-7 V pre-rails and the paired +-6 V LDOs of the output stages (ADR 0015)", "A4"),
        "hpa-rails-pre": proj.sheet("hpa-rails-pre.kicad_sch", "blk.hpa-rails-pre", "Amplifier rails: +-7 V pre-rails",
                                    "+7 V TPS65131 boost, -7 V LMR33630C inverting buck-boost and its enable shifter", "A3"),
        "hpa-rails-ldo": proj.sheet("hpa-rails-ldo.kicad_sch", "blk.hpa-rails-ldo", "Amplifier rails: +-6 V LDOs",
                                    "Two LT3045 and two LT3094 in parallel with trace ballasts (ADR 0015 item 3)", "A3"),
        "hpa-se": proj.sheet("hpa-se.kicad_sch", "blk.hpa-se", "Audio: single-ended output stage",
                             "Two OPA1622 with paralleled halves, one per channel, difference amplifiers (ADR 0012)", "A3"),
        "hpa-bal": proj.sheet("hpa-bal.kicad_sch", "blk.hpa-bal", "Audio: balanced output stage",
                              "Four OPA1622 with paralleled halves, one per leg, and the links of their rails (ADR 0012)", "A4"),
        "hpa-bal-l": proj.sheet("hpa-bal-l.kicad_sch", "blk.hpa-bal-l", "Balanced output stage: left channel",
                                "Two OPA1622 with paralleled halves for the L+ and L- legs", "A3"),
        "hpa-bal-r": proj.sheet("hpa-bal-r.kicad_sch", "blk.hpa-bal-r", "Balanced output stage: right channel",
                                "Two OPA1622 with paralleled halves for the R+ and R- legs", "A3"),
    }
    jse = proj.sheet("jack-se.kicad_sch", "blk.jack-se", "3.5 mm headphone jack",
                     "Single-ended output jack with ESD, plug detect and the reference net ties", "A4")
    jbal = proj.sheet("jack-bal.kicad_sch", "blk.jack-bal", "4.4 mm headphone jack",
                      "Balanced output jack (JEITA RC-8141C) with ESD and plug detect", "A4")
    return parent, kids, jse, jbal


def cap(s, key, x, y, top, bottom="GND", **kw):
    return two_pin_v(s, key, x, y, top, bottom, s.block, **kw)


def two_pin_box(s, key, x, y, a, b, **kw):
    """A horizontal two-pin part between nets a and b; returns its bbox."""
    two_pin_h(s, key, x, y, a, b, s.block, **kw)
    return hbox(x, y, key, a, b, kw.get("stub", 2.54))


# ---------------------------------------------------------------------- blk.audio (parent)

def draw_parent(s):
    corner_notes(s, [
        "1. Function: the audio converter boundary (feature blocks #27): DAC supplies, master clocks,",
        "   two CS43198 in dual mono, the amplifier rails and both OPA1622 output stages. Another",
        "   variant may replace any sub-sheet behind this interface (RFC 0011 rule 6).",
        "2. Absent state: never omitted (T1-040). Unpowered: every enable pulled off on the host side",
        "   (blk.soc-vccio-b, PCB-A-13); I2C2 reaches the DACs only through the SN74LVC2G66 there (G2).",
        "3. Interface buses: AUDIO_I2S (I2S1 and DSD), AUDIO_CTL (enables, reset, interrupt, the",
        "   isolated DAC I2C), HP_SE and HP_BAL (outputs and references to the jacks).",
        "4. Decisions: ADR 0001, 0010, 0012, 0015, 0019. Constraints: PCB-A-01 to PCB-A-19.",
    ])


# ---------------------------------------------------------------------- group helpers

def grp(flow, draw, newline=False):
    """Draw one group (draw() returns its bbox) and let the flow place it."""
    m = flow.sheet.mark()
    return flow.place(m, draw(), newline=newline)


def ic_group(s, title, lib, name, pins, rows=(), extra=None, value=None, x=101.6, y=101.6, pad_left=0.0, prefix="U",
             rows_dx=0.0):
    """An IC with passive rows under it, in a titled group. Returns the group bbox. pad_left
    reserves room left of the IC for a label the project staggers out (Project.stagger_labels)."""
    g = Group(s, title)
    u = ic(s, lib, name, x, y, pins, extra=extra, value=value, prefix=prefix)
    g.add(u.bbox)
    if pad_left:
        g.add((u.bbox[0] - pad_left, u.bbox[1], u.bbox[0], u.bbox[1]))
    rx = u.bbox[2] + 5.08 + rows_dx             # passive rows to the right of the IC, top-aligned
                                                # (rows_dx clears a long value above the IC)
    ry = u.bbox[1]
    for r in rows:
        b = g.add(prow(s, rx, snap(ry + row_need(r) + 3.81), r))
        ry = b[3] + 2.54
    return g.close()


def link_group(s, key, src, load, variants, title, x=101.6, y=101.6):
    link(s, key, x, y, src, load, link_variants(key, variants), title=title)
    return s.last_box


def parts_group(s, title, rows, x_max=None):
    """A group of passive rows (each a prow spec list), side by side up to x_max, then wrapped."""
    g = Group(s, title)
    x, y = 101.6, 101.6
    row_bottom = y
    for r in rows:
        box = prow(s, x, snap(y + row_need(r) + 3.81 - 6.35), r)
        if x_max and box[2] > x_max and x > 101.6:
            pass
        g.add(box)
        x = box[2] + 5.08
        row_bottom = max(row_bottom, box[3])
    return g.close()


# ---------------------------------------------------------------------- blk.audio-supply

def draw_supply(s, variants):
    blk = s.block
    f = Flow(s)
    grp(f, lambda: ic_group(s, "DAC_VP switch", "texas-instruments", "TPS22919DCKR",
                            {"IN": "VSYS_LV_AUDIO", "ON": "DAC_VP_EN", "NC": None, "VOUT": "DAC_VP", "QOD": "DAC_VP",
                             "GND": "GND"}, rows=[[("C_1u_0402", "VSYS_LV_AUDIO", "GND")]]))
    grp(f, lambda: ic_group(s, "DAC_DIG_1V8 switch", "texas-instruments", "TPS22919DCKR",
                            {"IN": "vcc_1v8", "ON": "DAC_DIG_EN", "NC": None, "VOUT": "DAC_DIG_1V8_SRC",
                             "QOD": "DAC_DIG_1V8_SRC", "GND": "GND"}, rows=[[("C_1u_0402", "vcc_1v8", "GND")]]))
    grp(f, lambda: link_group(s, "LINK_L1", "DAC_DIG_1V8_SRC", "DAC_DIG_1V8", variants, "Link #25"))

    def buck():
        g = Group(s, "AUDIO_2V2 pre-buck (TPS62840)")
        u = ic(s, "texas-instruments", "TPS62840DLCR", 101.6, 101.6,
               {"VIN": "VSYS_LV_AUDIO", "EN": "AUDIO_LN_EN", "MODE": "GND", "STOP": "GND", "VSET": "AUDIO_VSET",
                "SW": "AUDIO_SW", "VOS": "AUDIO_2V2_SRC", "GND": "GND"})
        g.add(u.bbox)
        g.add(two_pin_box(s, "L_DFE201610E_2R2", u.bbox[2] + 22.86, 93.98, "AUDIO_SW", "AUDIO_2V2_SRC", prefix="L"))
        g.add(under(s, u.bbox, [("C_4u7_0402_10V", "VSYS_LV_AUDIO", "GND"), ("R_4k32", "AUDIO_VSET", "GND"),
                                ("C_10u_0402_4V", "AUDIO_2V2_SRC", "GND")], x=u.bbox[0] + 2.54))
        return g.close()
    grp(f, buck, newline=True)
    grp(f, lambda: link_group(s, "LINK_L1", "AUDIO_2V2_SRC", "AUDIO_2V2", variants, "Link #26"))
    s.iface_rows = [
        ["DAC_VP_EN, DAC_DIG_EN", "Input", "Pulled down on the host side (blk.soc-vccio-b): switches off"],
        ["AUDIO_LN_EN", "Input", "Pulled down on the host side: TPS62840 off, output discharged"],
    ]
    s.rail_rows = [
        ["VSYS_LV_AUDIO", "1 µF; 4.7 µF 10 V (TPS62840 VIN)", "TPS22919 CIN 1 µF (SLVSEN5B §10); TPS62840 CI 4.7 µF (SLVSEC6D Table 2)"],
        ["vcc_1v8", "1 µF", "TPS22919 CIN 1 µF (SLVSEN5B §10)"],
        ["AUDIO_2V2", "10 µF 4 V", "TPS62840 CO 10 µF (SLVSEC6D Table 2); each LDO adds 1 µF"],
    ]
    corner_notes(s, [
        "1. Function: DAC_VP (TPS22919 from VSYS_LV: VP of both CS43198), DAC_DIG_1V8 (TPS22919 from",
        "   vcc_1v8: VD, VL, VCP, the I2C2 switch controls, the MCLK interlock) and AUDIO_2V2 (TPS62840",
        "   at 2.2 V, VSET 4.32 kΩ, SLVSEC6D Table 1) for the VA and MCLK_1V8 LDOs (power tree §2, §3).",
        "2. Absent state: enables pulled down on the host side; QOD tied to VOUT empties DAC_VP and",
        "   DAC_DIG_1V8 at switch-off (SLVSEN5B §8.3.3); the TPS62840 discharges its output via VOS.",
        "3. Sequence (power tree §6.2): DAC_VP_EN first, then DAC_DIG_EN and AUDIO_LN_EN; VP off last.",
        "4. TPS62840 MODE and STOP low: power save (SLVSEC6D p. 5); MODE high is the fallback if",
        "   bursts are audible (UNVERIFIED, BOM v1 line 27). Links L1 #25, #26 (0 Ω in production).",
        "5. VSYS_LV_AUDIO: the audio branch of VSYS_LV behind the 0x41 INA236 shunt (blk.current-monitors).",
        "6. Unless noted: resistors 1 % 0402; capacitors X5R/X7R rated at least twice the rail.",
    ])


# ---------------------------------------------------------------------- blk.mclk

def draw_mclk(s, variants):
    blk = s.block
    f = Flow(s)
    grp(f, lambda: ic_group(s, "Interlock (G3)", "texas-instruments", "SN74LVC1G57DCKR",
                            {"In0": "vcca1v8_pmu", "In1": "AUDIO_LN_EN", "In2": "DAC_DIG_1V8", "Y": "MCLK_3V1_EN",
                             "VCC": "vcca1v8_pmu", "GND": "GND"}, rows=[[("C_100n_0402", "vcca1v8_pmu", "GND")]]))
    grp(f, lambda: link_group(s, "LINK_L1", "VSYS_LV_AUDIO", "MCLK3V1_IN", variants, "Link #27"))
    grp(f, lambda: ic_group(s, "MCLK_3V1 LDO", "texas-instruments", "TPS7A2031PDBVR",
                            {"IN": "MCLK3V1_IN", "EN": "MCLK_3V1_EN", "N/C": None, "OUT": "MCLK_3V1", "GND": "GND"},
                            rows=[[("C_1u_0402", "MCLK3V1_IN", "GND"), ("C_1u_0402", "MCLK_3V1", "GND")]]))
    grp(f, lambda: link_group(s, "LINK_L1", "AUDIO_2V2", "MCLK1V8_IN", variants, "Link #36"))
    grp(f, lambda: ic_group(s, "MCLK_1V8 LDO (ADR 0019 item 3)", "texas-instruments", "TPS7A2018PDBVR",
                            {"IN": "MCLK1V8_IN", "EN": "DAC_DIG_1V8", "N/C": None, "OUT": "MCLK_1V8", "GND": "GND"},
                            rows=[[("C_1u_0402", "MCLK1V8_IN", "GND"), ("C_1u_0402", "MCLK_1V8", "GND")]]))

    def oscillators():
        g = Group(s, "Oscillators (ADR 0019 item 1)")
        for i, (mpn, fam, en, val) in enumerate((("NSC5083D-45.158M", "441", "MCLK441_EN", "45.1584 MHz"),
                                                 ("NSC5083D-49.152M", "48", "MCLK48_EN", "49.152 MHz"))):
            x, y = 101.6 + i * 106.68, 101.6
            sym = library.load("ndk", mpn)
            pl = s.place(sym, s.next_ref("Y"), x + 38.1, y, fields={"Block": blk}, value=val)
            s.connect_all(pl, {"4": "MCLK_3V1", "2": "GND"})
            st, out = pl.pos(pl.pin("1")), pl.pos(pl.pin("3"))
            ll, lr = hpart(s, "R_0_0402", st[0] - 7.62, y)          # ST through a 0 Ohm footprint
            s.wire(lr, st)
            s.wire(ll, (ll[0] - 2.54, y))
            s.point(en, ll[0] - 2.54, y, "left", "pas")
            ol, orr = hpart(s, "R_33", out[0] + 7.62, y)             # 33 Ohm into the shared net
            s.wire(out, ol)
            s.wire(orr, (orr[0] + 2.54, y))
            s.point("MCLK_OSC", orr[0] + 2.54, y, "right", "pas")
            g.add((ll[0] - 2.54 - len(en) * 1.16 - 1.27, y - 25.4, orr[0] + 2.54 + 11.0, y + 20.32))
        return g.close()
    grp(f, oscillators)
    grp(f, lambda: parts_group(s, "Pulls and bypass", [
        [("R_100k", "MCLK441_ST", "GND"), ("R_100k", "MCLK48_ST", "GND"), ("R_100k", "MCLK_OSC", "GND"),
         ("R_100k", "MCLK_DIV_RUN", "GND"), ("C_10n_0402", "MCLK_3V1", "GND"), ("C_10n_0402", "MCLK_3V1", "GND")]]))

    def dividers():
        g = Group(s, "Dividers by two (ADR 0019 item 2)")
        x = 101.6
        for i, side in enumerate(("L", "R")):
            u = ic(s, "texas-instruments", "SN74AUC1G74DCUR", x, 101.6,
                   {"D": f"DIV{side}_QN", "CLK": "MCLK_OSC", "~{PRE}": "MCLK_1V8", "~{CLR}": "MCLK_DIV_RUN",
                    "Q": "", "~{Q}": f"DIV{side}_QN", "VCC": "MCLK_1V8", "GND": "GND"})
            q = u.pos(u.pin("Q"))
            # Q through 27 Ohm to XTI; the resistor past the Q-bar label one row below
            rl, rr = hpart(s, "R_27", snap_up(q[0] + 2.54 + len(f"DIV{side}_QN") * 1.16 + 1.27 + 5.08), q[1])
            s.wire(q, rl)
            s.wire(rr, (rr[0] + 2.54, q[1]))
            s.point(f"MCLK_{side}", rr[0] + 2.54, q[1], "right", "out")
            g.add(u.bbox)
            g.add((u.bbox[0], u.bbox[1], rr[0] + 2.54 + 10.16, u.bbox[3]))
            x = rr[0] + 48.26
        g.add(prow(s, x - 20.32, 93.98, [("C_100n_0402", "MCLK_1V8", "GND"), ("C_100n_0402", "MCLK_1V8", "GND")]))
        return g.close()
    grp(f, dividers)
    s.iface_rows = [
        ["MCLK441_EN, MCLK48_EN", "Input", "100 kΩ pull-down after the 0 Ω: both oscillators tri-stated"],
        ["MCLK_DIV_RUN", "Input", "100 kΩ pull-down: dividers held clear"],
        ["MCLK_L, MCLK_R", "Output", "Low while the dividers are held or unpowered (G3)"],
    ]
    s.rail_rows = [
        ["vcca1v8_pmu", "100 nF", "Gate VCC bypass (capture choice; SCES414P gives none)"],
        ["MCLK_3V1", "1 µF + 2 x 10 nF", "TPS7A20 COUT 1 µF (SBVS338H Fig. 7-4); 0.01 µF per oscillator (NZ2520SDA p. 1)"],
        ["MCLK_1V8", "1 µF + 2 x 100 nF", "TPS7A20 COUT 1 µF; 100 nF per divider (BOM v1 line 140)"],
        ["LDO inputs", "1 µF each", "TPS7A20 CIN 1 µF (SBVS338H Fig. 7-4)"],
    ]
    corner_notes(s, [
        "1. Function: NDK NSC5083D at 45.1584 / 49.152 MHz on MCLK_3V1 (TPS7A2031), one at a time,",
        "   33 Ω each into MCLK_OSC (100 kΩ pull-down); one SN74AUC1G74 per DAC divides by two (Q-bar",
        "   to D, PRE-bar high), Q through 27 Ω to its XTI (ADR 0019; BOM v1 lines 20, 21, 29, 139, 140).",
        "2. Absent state: ST pulled down, dividers held by MCLK_DIV_RUN. MCLK_3V1 EN = AUDIO_LN_EN AND",
        "   DAC_DIG_1V8 (SN74LVC1G57 with In0 high: Y = In1 AND In2, SCES414P Table 1) and MCLK_1V8",
        "   EN = DAC_DIG_1V8, so no clock reaches an unpowered XTI (G3).",
        "3. Start (ADR 0019 item 6): ST and CLR-bar low before the rails; CLR-bar released while",
        "   MCLK_OSC is low; then one ST high. Family change: DACs to the RCO, CLR-bar low, swap ST.",
        "4. Layout (item 5): one cluster; oscillator to divider <= 10 mm, divider to XTI <= 15 mm.",
        "5. Open: ST rating at 3.3 V drive into a 3.1 V or unpowered oscillator (pinout O11);",
        "   the 45.1584 MHz value on an NDK document (UNVERIFIED). Links L1 #27, #36.",
        "6. Unless noted: resistors 1 % 0402; capacitors X7R.",
    ])


# ---------------------------------------------------------------------- blk.dac-l, blk.dac-r

def draw_dac(s, variants, side):
    """Both DAC sheets come from this function, mirrored by reference block (CRAFT-87)."""
    blk = s.block
    master = side == "L"
    n = f"DAC{side}"
    va = "DAC1_VA" if master else "DAC2_VA"
    f = Flow(s)

    def serial():
        g = Group(s, "Serial port (BOM v1 lines 134, 141)")
        rows = [("I2S_SDO0", f"{n}_SDIN", "R_0_0402"),
                ("I2S_BCLK", f"{n}_SCLK", "R_22" if master else "R_0_0402"),
                ("I2S_LRCK", f"{n}_LRCK", "R_22" if master else "R_0_0402"),
                (f"DSD_{side}", f"{n}_DSDA", "R_0_0402"),
                ("I2S_BCLK", f"{n}_DSDCLK", "R_0_0402")]
        for i, (a_, b_, key) in enumerate(rows):
            g.add(two_pin_box(s, key, 101.6, 101.6 + i * 15.24, a_, b_))
        if not master:
            g.add(prow(s, 101.6 - 3.81, 101.6 + 5 * 15.24 + 5.08, [("R_4k99", f"{n}_ADR", "GND")]))
        return g.close()
    grp(f, serial)
    pins = {"SCL": "DAC_I2C_SCL", "SDA": "DAC_I2C_SDA", "ADR": "GND" if master else f"{n}_ADR",
            "RESET": "DAC_RST_N", "SDIN1": f"{n}_SDIN", "SCLK1": f"{n}_SCLK", "LRCK1": f"{n}_LRCK",
            "DSDA/SDIN2": f"{n}_DSDA", "DSDB/LRCK2": None, "DSDCLK/SCLK2": f"{n}_DSDCLK",
            "XTI/MCLK": f"MCLK_{side}", "XTO": None, "HP_DETECT": "GND",
            "AOUTA": f"{n}_AOUT_P", "REFA": f"HPSE_REF_{side}", "AOUTB": f"{n}_AOUT_N", "REFB": f"HPSE_REF_{side}",
            "INT": "DAC_INT_N", "CLKOUT": None, "TSO": None,
            "FILT+": f"{n}_FILTP", "FILT-": f"{n}_FILTN", "-VA": f"{n}_NVA", "FLYP_VA": f"{n}_FLYP_VA",
            "FLYN_VA": f"{n}_FLYN_VA", "VCP_FILT+": f"{n}_VCPF_P", "VCP_FILT-": f"{n}_VCPF_N",
            "FLYP_VCP": f"{n}_FLYP_VCP", "FLYC_VCP": f"{n}_FLYC_VCP", "FLYN_VCP": f"{n}_FLYN_VCP",
            "VA": va, "VCP": "DAC_DIG_1V8", "VP": "DAC_VP", "VD": "DAC_DIG_1V8", "VL": "DAC_DIG_1V8",
            "GNDA": "GND", "GNDCP": "GND", "GNDD": "GND", "EP": "GND"}
    grp(f, lambda: ic_group(s, "CS43198 in mono mode (DS1156F2 Fig. 2-2)", "cirrus-logic", "CS43198-CNZR", pins,
                            extra={"Constraints": "PCB-A-01 PCB-A-02 PCB-A-04 PCB-A-05"}))
    # the VA supply (link, LDO) as a column beside the converter; the wide capacitor group below
    from blocks_should import column
    col = column(s, f)
    grp(col, lambda: link_group(s, "LINK_L1", "AUDIO_2V2", f"{n}_VA_IN", variants, f"Link #{28 if master else 29}"))
    grp(col, lambda: ic_group(s, "VA LDO (TPS7A2018)", "texas-instruments", "TPS7A2018PDBVR",
                            {"IN": f"{n}_VA_IN", "EN": "AUDIO_LN_EN", "N/C": None, "OUT": va, "GND": "GND"},
                            rows=[[("C_1u_0402", f"{n}_VA_IN", "GND"), ("C_1u_0402", va, "GND")]]))
    grp(f, lambda: parts_group(s, "Supplies and charge pumps (Fig. 2-1)", [
        [("C_100n_0402", "DAC_DIG_1V8", "GND"), ("C_100n_0402", "DAC_DIG_1V8", "GND"),
         ("C_2u2_0402", "DAC_DIG_1V8", "GND"), ("C_100n_0402", "DAC_VP", "GND"), ("C_4u7_0603_10V", "DAC_VP", "GND")],
        [("C_2u2_0402", va, "GND"), ("C_15u_0603", va, f"{n}_FILTP"), ("C_2u2_0402", f"{n}_NVA", "GND"),
         ("C_15u_0603", f"{n}_NVA", f"{n}_FILTN")],
        [("C_2u2_0402", f"{n}_FLYP_VA", f"{n}_FLYN_VA"), ("C_2u2_0402", f"{n}_VCPF_P", "GND"),
         ("C_2u2_0402", f"{n}_VCPF_N", "GND")],
        [("C_2u2_0402", f"{n}_FLYP_VCP", f"{n}_FLYC_VCP"), ("C_2u2_0402", f"{n}_FLYC_VCP", f"{n}_FLYN_VCP")]]))
    from blocks_should import pads           # the I2S/DSD pads are on blk.debug (BOM v1 line 88)
    grp(col, pads(s, "MCLK test pad (BOM v1 line 88)", (f"MCLK_{side}",)))
    s.iface_rows = [
        ["I2S_SDO0, I2S_BCLK, I2S_LRCK, DSD_x", "Bidirectional", "Series parts here; the SoC parks the lines low (G2, G21)"],
        ["DAC_I2C_SCL, DAC_I2C_SDA", "Bidirectional", "Isolated on the host side while DAC_DIG_1V8 is off (G2)"],
        ["DAC_RST_N", "Input", "Pulled down on the host side: converter in reset (PCB-A-13)"],
        ["DAC_INT_N", "Output", "Open drain; pull-up on DAC_DIG_1V8 on the host side"],
        [f"MCLK_{side}", "Input", "Low while the dividers are held or off"],
        [f"{n}_AOUT_P, {n}_AOUT_N", "Output", "Into both output stages"],
        [f"HPSE_REF_{side}", "Passive", "REFA, REFB to the 3.5 mm sleeve through its net tie (PCB-A-03, -16)"],
    ]
    s.rail_rows = [
        ["DAC_DIG_1V8", "VL, VD 100 nF each; VCP 2.2 µF", "DS1156F2 Fig. 2-1"],
        ["DAC_VP", "100 nF + 4.7 µF 10 V", "DS1156F2 Fig. 2-1"],
        [va, "2.2 µF; FILT+ 15 µF to VA; LDO 1 µF", "DS1156F2 Fig. 2-1; SBVS338H Fig. 7-4"],
        ["-VA, VCP_FILT±", "2.2 µF each; flying 2.2 µF x 3", "DS1156F2 Fig. 2-1, internal VCP_FILT (EXT_VCPFILT = 0)"],
    ]
    corner_notes(s, [
        f"1. Function: Cirrus Logic CS43198 for the {'left' if master else 'right'} channel in mono mode (dual mono, BOM v1",
        "   line 18): AOUTA and AOUTB a differential pair into both output stages; I2C2 address "
        + ("0x30 (ADR to ground)." if master else "0x31 (ADR 4.99 kΩ to ground)."),
        "2. Absent state: never omitted (T1-040). RESET held low by the host-side pull-down; INT pulled",
        "   up only on DAC_DIG_1V8; I2C isolated while DAC_DIG_1V8 is off (G2).",
        "3. " + ("Clock master: SCLK1 and LRCK1 drive I2S_BCLK and I2S_LRCK through 22 Ω (HDG p. 70)."
                 if master else "Clock slave: SCLK1 and LRCK1 from the left DAC through 0 Ω."),
        "   XTI/MCLK from its own divider (blk.mclk); XTO, CLKOUT, TSO and DSDB/LRCK2 unused.",
        "   DSD: DSDA from DSD_x, DSDCLK from I2S_BCLK (native DSD reserved, blackbird-os ADR 0006).",
        "4. HP_DETECT tied low: plug detection is on the jacks (expander P10, P11).",
        "5. VA from its own TPS7A2018 (EN = AUDIO_LN_EN) behind link L1; VL, VD, VCP on DAC_DIG_1V8;",
        "   VP on DAC_VP (PCB-A-05). GNDA, GNDCP, GNDD and the pad in one ground (PCB-A-01, -02).",
        "6. Open: series values other than 0 Ω (bring-up, G2); CS43198 pins fail-safe unpowered (UNVERIFIED).",
    ])


# ---------------------------------------------------------------------- blk.hpa-rails

def draw_rails_parent(s):
    corner_notes(s, [
        "1. Function: the amplifier rails (feature blocks #32), drawn on two sub-sheets: the +-7 V",
        "   pre-rails with the -7 V enable shifter, and the paired +-6 V LDOs (ADR 0015).",
        "2. Absent state: HPA_RAIL_EN and HPA_LDO_EN pulled down: every rail off.",
        "3. Sub-sheet IDs (blk.hpa-rails-*) are sheets of blk.hpa-rails, as the SoC's sub-sheets.",
    ])


def draw_rails(s, variants):
    blk = s.block
    f = Flow(s)

    def boost():
        g = Group(s, "+7 V pre-rail: TPS65131 boost (ADR 0015 item 2)")
        u = ic(s, "texas-instruments", "TPS65131RGER", 101.6, 101.6,
               {"VIN": "HPA_BOOST_VIN", "INP": "HPA_BOOST_SW", "INN": "VSYS_LV_AUDIO", "ENP": "HPA_RAIL_EN",
                "PSP": "HPA_BOOST_VIN", "ENN": "GND", "PSN": "GND", "NC": None,
                "VPOS": "AUDIO_P7V0", "FBP": "HPA_BOOST_FB", "CP": "HPA_BOOST_CP", "OUTN": None, "VNEG": "GND",
                "FBN": "GND", "CN": None, "VREF": "HPA_BOOST_VREF", "BSW": None,
                "PGND": "GND", "AGND": "GND", "EP": "GND"})
        g.add(u.bbox)
        x0 = u.bbox[2] + 5.08
        s.flag_net("HPA_BOOST_VIN", since=s.mark()[1], side="right")   # fed through the 100 Ω filter
        g.add(two_pin_box(s, "R_100", x0 + 17.78, u.bbox[1] + 7.62, "VSYS_LV_AUDIO", "HPA_BOOST_VIN"))
        g.add(two_pin_box(s, "L_DFE252012F_4R7", x0 + 17.78, u.bbox[1] + 22.86, "VSYS_LV_AUDIO", "HPA_BOOST_SW", prefix="L"))
        yd = u.bbox[1] + 38.1
        d = part(s, "Diode", "PMEG2010AEH", x0 + 22.86, yd, {"2": "", "1": ""}, key="D_PMEG2010AEH", angle=180,
                 prefix="D")
        da, dk = d.pos(d.pin("2")), d.pos(d.pin("1"))
        s.wire(da, (da[0] - 7.62, yd))
        s.point("HPA_BOOST_SW", da[0] - 7.62, yd, "left", "pas")
        s.wire(dk, (dk[0] + 10.16, yd))
        s.flag_at(dk[0] + 5.08, yd, "down", 2.54)
        s.attach("AUDIO_P7V0", dk[0] + 10.16, yd, "right")
        g.add((x0, yd - 7.62, dk[0] + 25.4, yd + 10.16))
        dv = g.add(divider(s, x0 + 15.24, yd + 25.4, "AUDIO_P7V0", "HPA_BOOST_FB", "GND", "R_475k", "R_100k_0603",
                           cff="C_15p_0402"))
        g.add(prow(s, max(x0 + 50.8, snap_up(dv[2] + 5.08)), yd + 33.02, [("C_10n_0402_C0G", "HPA_BOOST_CP", "GND"),
                                              ("C_220n_0402", "HPA_BOOST_VREF", "GND")]))
        g.add(prow(s, u.bbox[0] + 2.54, u.bbox[3] + 15.24, [("C_100n_0402", "HPA_BOOST_VIN", "GND"),
                                                           ("C_4u7_0402", "VSYS_LV_AUDIO", "GND"), ("C_4u7_0402", "VSYS_LV_AUDIO", "GND"),
                                                           ("C_4u7_0805_25V", "AUDIO_P7V0", "GND"),
                                                           ("C_4u7_0805_25V", "AUDIO_P7V0", "GND"),
                                                           ("C_4u7_0805_25V", "AUDIO_P7V0", "GND"),
                                                           ("C_4u7_0805_25V", "AUDIO_P7V0", "GND")]))
        return g.close()
    grp(f, boost)

    def inverter():
        g = Group(s, "-7 V pre-rail: LMR33630C inverting buck-boost (ADR 0015 item 1)")
        u = ic(s, "texas-instruments", "LMR33630CRNXR", 101.6, 101.6,
               {"VIN": "VSYS_AUDIO", "EN": "HPA_N7_EN", "NC": None, "SW": "HPA_N7_SW", "BOOT": "HPA_N7_BOOT",
                "VCC": "HPA_N7_VCC", "FB": "HPA_N7_FB", "PG": None, "PGND": "AUDIO_N7V0", "AGND": "AUDIO_N7V0"})
        g.add(u.bbox)
        x0 = u.bbox[2] + 5.08
        g.add(two_pin_box(s, "L_XGL4020_222", x0 + 17.78, u.bbox[1] + 7.62, "HPA_N7_SW", "GND", prefix="L"))
        g.add(divider(s, x0 + 15.24, u.bbox[1] + 33.02, "AUDIO_N7V0", "HPA_N7_FB", "GND", "R_16k5", "R_100k_0603",
                      cff="C_22p_0402", cff_on="bottom", flag_top=True))
        g.add(prow(s, x0 + 50.8, u.bbox[1] + 33.02, [("C_100n_0402", "HPA_N7_BOOT", "HPA_N7_SW"),
                                                    ("C_1u_0402", "HPA_N7_VCC", "AUDIO_N7V0")]))
        g.add(prow(s, u.bbox[0] + 2.54, u.bbox[3] + 15.24, [("C_10u_0805_25V", "VSYS_AUDIO", "AUDIO_N7V0"),
                                                           ("C_10u_0805_25V", "VSYS_AUDIO", "AUDIO_N7V0"),
                                                           ("C_4u7_0805_25V", "VSYS_AUDIO", "GND"),
                                                           ("C_22u_1206_16V", "AUDIO_N7V0", "GND"),
                                                           ("C_22u_1206_16V", "AUDIO_N7V0", "GND"),
                                                           ("C_22u_1206_16V", "AUDIO_N7V0", "GND")]))
        return g.close()
    grp(f, inverter)

    def shifter():
        g = Group(s, "-7 V enable level shifter (SNVA856B Fig. 7-1)")
        g.add(prow(s, 101.6, 109.22, [("R_100k", "HPA_RAIL_EN", "GND")]))
        q1 = part(s, "Transistor_FET", "DMG1012T", 127.0, 116.84, {"1": "HPA_RAIL_EN", "3": "HPA_N7_LS_G", "2": "GND"},
                  key="Q_DMG1012T", prefix="Q")
        g.add((114.3, 101.6, 139.7, 129.54))
        g.add(prow(s, 147.32, 109.22, [("R_100k", "VSYS_AUDIO", "HPA_N7_LS_G")]))
        part(s, "Transistor_FET", "DMP3099L", 175.26, 116.84, {"1": "HPA_N7_LS_G", "3": "VSYS_AUDIO", "2": "HPA_N7_LS_D"},
             key="Q_DMP3099L", prefix="Q")
        g.add((160.02, 101.6, 190.5, snap_up(124.46 + len("HPA_N7_LS_D") * 1.16 + 2.54)))   # the drain label below
        g.add(prow(s, 200.66, 109.22, [("R_100k", "HPA_N7_LS_D", "HPA_N7_EN"), ("R_100k", "HPA_N7_EN", "AUDIO_N7V0")]))
        return g.close()
    grp(f, shifter)

    s.iface_rows = [
        ["HPA_RAIL_EN", "Input", "100 kΩ pull-down here: both pre-rails off"],
        ["AUDIO_P7V0, AUDIO_N7V0", "Supply out", "Off; the LDOs behind them off first (power tree §6.3)"],
    ]
    s.rail_rows = [
        ["VSYS_LV_AUDIO", "2 x 4.7 µF (INP, INN); 100 nF at VIN behind 100 Ω", "SLVS493E Fig. 8-1, Table 8-1"],
        ["AUDIO_P7V0", "4 x 4.7 µF 25 V X7R; 15 pF feed-forward", "BOM v1 line 111 (SLVS493E Eq. 7, 11)"],
        ["VSYS_AUDIO (-7 V IC)", "2 x 10 µF 25 V to -7 V; 4.7 µF 25 V to GND", "BOM v1 line 118 (SNVA856B Fig. 3-1)"],
        ["AUDIO_N7V0", "3 x 22 µF 16 V X7R 1206; 22 pF feed-forward", "BOM v1 line 118"],
    ]
    corner_notes(s, [
        "1. Function: AUDIO_P7V0 (TPS65131 boost from VSYS_LV_AUDIO, 475 kΩ / 100 kΩ: 6.97 V), AUDIO_N7V0",
        "   (LMR33630C inverting buck-boost from VSYS_AUDIO, IC ground = -7 V, 100 kΩ / 16.5 kΩ: -7.06 V), then",
        "   HPA_P6V0 / HPA_N6V0 from two LT3045 and two LT3094 in parallel (ADR 0015; BOM lines 22-26, 116-119).",
        "2. Absent state: HPA_RAIL_EN and HPA_LDO_EN pulled down: both pre-rails and the LDOs off.",
        "3. TPS65131 inverter half unused: ENN, PSN, VNEG, FBN to ground, OUTN and CN open, INN on",
        "   VSYS_LV_AUDIO with 4.7 µF (BOM line 22; no single-output case in SLVS493E, UNVERIFIED).",
        "4. LMR33630C: EN through the two-FET shifter of SNVA856B Fig. 7-1; PG and NC unused.",
        "5. LDOs: SET tied, 2 x 60.4 kΩ (6.04 V), 2 x 0.47 µF (≈ 65 ms); RILIM 523 Ω / 13.0 kΩ; PGFB to",
        "   IN; PG open; OUT and OUTS joined, then a 20 mΩ trace ballast (net tie) to the shared rail.",
        "6. Sequence: HPA_LDO_EN at least 10 ms after HPA_RAIL_EN (power tree §6.2).",
        "7. Constraints: PCB-A-06, -14, -15. Unless noted: resistors 1 % 0402; X7R capacitors.",
    ])


def draw_ldos(s, variants):
    blk = s.block
    f = Flow(s)

    def ldo_pair(title, name, vin, vout, setn, rlim, cin, sign):
        g = Group(s, title)
        x = 101.6
        for i in range(2):
            tag = f"HPA_{sign}6_{'AB'[i]}"
            pins = {"IN": vin, "EN/UV": "HPA_LDO_EN", "PGFB": vin, "ILIM": f"{tag}_ILIM", "SET": setn,
                    "OUT": tag, "OUTS": tag, "PG": None, "GND": "GND"}
            if name == "LT3094EDD":
                pins["VIOC"] = None
            u = ic(s, "analog-devices", name, x, 101.6, pins)
            g.add(u.bbox)
            nt = two_pin_box(s, "NT_BALLAST", u.bbox[2] + 7.62, u.bbox[1] + 7.62, tag, vout, stub=5.08, above=True)
            g.add(nt)
            if i == 0:
                s.flag_at(u.bbox[2] + 7.62 + 2.54 + 2.54, u.bbox[1] + 7.62, "down", 2.54)
            g.add(prow(s, u.bbox[0] + 2.54, u.bbox[3] + 20.32, [(rlim, f"{tag}_ILIM", "GND"), (cin, vin, "GND"),
                                                               ("C_10u_0805_X7R", tag, "GND")]))
            # pitch: the first ballast's rail text clears the second device's upright IN rail
            x = snap(x + 83.82)
        row = [("R_60k4_TF", setn, "GND"), ("R_60k4_TF", setn, "GND"), ("C_470n_0603", setn, "GND"),
               ("C_470n_0603", setn, "GND")]
        # below the row above, its label clear of that row's ground symbols
        g.add(prow(s, 101.6, snap(max(b[3] for b in g.boxes) + 2.54 + row_need(row) + 3.81), row))
        return g.close()
    grp(f, lambda: ldo_pair("+6 V: two LT3045 in parallel (ADR 0015 item 3)", "LT3045EDD", "AUDIO_P7V0", "HPA_P6V0",
                            "HPA_P6_SET", "R_523", "C_4u7_0805_X7R", "P"))
    grp(f, lambda: ldo_pair("-6 V: two LT3094 in parallel (ADR 0015 item 3)", "LT3094EDD", "AUDIO_N7V0", "HPA_N6V0",
                            "HPA_N6_SET", "R_13k", "C_10u_0805_X7R", "N"))
    s.iface_rows = [
        ["HPA_LDO_EN", "Input", "Pulled down on the host side: the four LDOs off"],
        ["AUDIO_P7V0, AUDIO_N7V0", "Supply in", "From blk.hpa-rails-pre"],
        ["HPA_P6V0, HPA_N6V0", "Supply out", "Off with HPA_LDO_EN low; OPA1622 EN low first (power tree §6.3)"],
    ]
    s.rail_rows = [
        ["AUDIO_P7V0", "4.7 µF per LT3045", "BOM v1 line 110 (LT3045 Rev. D pp. 16-21)"],
        ["AUDIO_N7V0", "10 µF per LT3094", "BOM v1 line 110 (LT3094 Rev. B pp. 15, 20-25)"],
        ["HPA_P6V0, HPA_N6V0", "10 µF per device at OUT, before the ballast", "BOM v1 line 110; ESR < 20 / 30 mΩ"],
    ]
    corner_notes(s, [
        "1. Function: HPA_P6V0 from two LT3045 and HPA_N6V0 from two LT3094 in parallel, as both ADI",
        "   datasheets describe (LT3045 p. 21 Fig. 7, LT3094 p. 25 Fig. 15; ADR 0015 item 3).",
        "2. Absent state: HPA_LDO_EN pulled down: the four LDOs off; enabled >= 10 ms after HPA_RAIL_EN.",
        "3. SET tied per rail, RSET 2 x 60.4 kΩ (200 µA x 30.2 kΩ = 6.04 V), CSET 2 x 0.47 µF (≈ 65 ms);",
        "   RILIM 523 Ω (LT3045) / 13.0 kΩ (LT3094) per device: pair limits 516-631 / 519-646 mA.",
        "4. PGFB tied to IN (fast start-up off), PG open; OUT and OUTS joined at each device, then a",
        "   20 mΩ PCB trace ballast (net tie) to the shared rail. LT3094 exposed pad is IN (-7 V).",
        "5. Constraints: PCB-A-06, PCB-A-14. Unless noted: resistors 1 % 0603, capacitors X7R.",
    ])


# ---------------------------------------------------------------------- output stages

def _branch(s, x, y, inp, out, ret):
    """One input of a difference amplifier on row y: label inp at x, 1.00 kΩ to the node, the node
    on to label out; from the node 1.62 kΩ // 100 pF down to ret (GND, or a label to the left)."""
    ll, lr = hpart(s, "R_1k_TF", x + 7.62, y)
    s.point(inp, x, y, "left", "pas")
    s.wire((x, y), ll)
    n = x + 17.78
    s.wire(lr, (n, y), (x + 43.18, y))
    s.point(out, x + 43.18, y, "right", "pas")
    s.junction(n, y)
    t1, b1 = vpart(s, "R_1k62_TF", n, y + 8.89, text="left")
    t2, b2 = vpart(s, "C_100p_0603", n + 12.7, y + 8.89)
    s.wire((n, y), t1)
    s.wire(t1, t2)
    s.junction(*t1)
    s.wire(b1, b2)
    s.wire(b1, (n, y + 15.24))
    s.junction(*b1)
    s.wire((n, y + 15.24), (n, y + 17.78))
    if ret == "GND":
        s.power("GND", n, y + 17.78)
    else:
        s.wire((n, y + 17.78), (n - 5.08, y + 17.78))
        s.point(ret, n - 5.08, y + 17.78, "left", "pas")


def diff_half(s, x, y, inp, inn, ref, tag, half):
    """One half's difference amplifier (BOM v1 lines 37, 108; SBOS727B Fig. 52 topology): R3
    1.00 kΩ inp -> +IN with R4 1.62 kΩ // C2 100 pF to ref; R1 1.00 kΩ inn -> -IN with R2 1.62 kΩ //
    C1 100 pF to the half's own output (feedback before the ballast). Returns its bbox."""
    _branch(s, x, y, inp, f"{tag}_P{half}", ref)
    _branch(s, x, y + 30.48, inn, f"{tag}_N{half}", f"{tag}_O{half}")
    w = max(len(inp), len(inn)) * 1.16 + 2.54
    return (x - w, y - 10.16, x + 43.18 + len(f"{tag}_P{half}") * 1.16 + 2.54, y + 30.48 + 22.86)


def opa_cell(s, title, tag, inp, inn, ref, en, vpos, vneg, leg):
    """One OPA1622 with both halves in parallel: networks for half A and B side by side, the
    amplifier to their right, a 1.0 Ω ballast per half joined at the leg. Returns the group bbox."""
    g = Group(s, title)
    x, y = 101.6, 101.6
    ba = g.add(diff_half(s, x, y, inp, inn, ref, tag, "A"))
    bb = g.add(diff_half(s, snap(ba[2] + 2.54 + len(inp) * 1.16 + 2.54), y, inp, inn, ref, tag, "B"))
    u = ic(s, "texas-instruments", "OPA1622IDRCR", snap(bb[2] + 22.86), y + 15.24,
           {"+INA": f"{tag}_PA", "-INA": f"{tag}_NA", "+INB": f"{tag}_PB", "-INB": f"{tag}_NB", "EN": en,
            "OUTA": "", "OUTB": "", "V+": vpos, "V-": "", "GND": "GND", "EP": ""},
           extra={"Constraints": "PCB-A-08 PCB-A-09 PCB-A-14 PCB-A-15"})
    g.add(u.bbox)
    # V- and the thermal pad either side of GND: each to its label, turned outward
    for name in ("V-", "EP"):
        px, py = u.pos(u.pin(name))
        gx = u.pos(u.pin("GND"))[0]
        d = -1 if px < gx else 1
        s.wire((px, py), (px, py + 2.54), (px + d * 2.54, py + 2.54))
        s.point(vneg, px + d * 2.54, py + 2.54, "left" if d < 0 else "right", "pas")
    xa, ya = u.pos(u.pin("OUTA"))
    xb, yb = u.pos(u.pin("OUTB"))
    xr = 0.0
    for half, (px, py) in (("A", (xa, ya)), ("B", (xb, yb))):
        jx = px + 5.08
        ll, lr = hpart(s, "R_1R0", px + 12.7, py, text="above" if py == min(ya, yb) else "below")
        s.wire((px, py), (jx, py), ll)
        s.junction(jx, py)
        up = py == min(ya, yb)
        s.wire((jx, py), (jx, py - 2.54 if up else py + 2.54))
        s.point(f"{tag}_O{half}", jx, py - 2.54 if up else py + 2.54, "up" if up else "down", "pas")
        xr = lr[0] + 2.54
        s.wire(lr, (xr, py))
    s.wire((xr, ya), (xr, yb))
    top = min(ya, yb)
    s.wire((xr, top), (xr + 5.08, top))
    s.junction(xr, top)
    s.point(leg, xr + 5.08, top, "right", "pas")
    xe = xr + 5.08 + len(leg) * 1.16 + 2.54
    g.add((xa, u.bbox[1], xe, u.bbox[3]))
    g.add(prow(s, snap(xe + 5.08), snap(ya + 2.54), [("C_100n_0402", vpos, "GND"), ("C_100n_0402", vneg, "GND")]))
    return g.close()


def stage_cells(kind, side=None):
    bal = kind == "bal"
    if bal:
        cells = {"L": [("LP", "DACL_AOUT_P", "DACL_AOUT_N", "GND", "HPBAL_L_P"),
                       ("LN", "DACL_AOUT_N", "DACL_AOUT_P", "GND", "HPBAL_L_N")],
                 "R": [("RP", "DACR_AOUT_P", "DACR_AOUT_N", "GND", "HPBAL_R_P"),
                       ("RN", "DACR_AOUT_N", "DACR_AOUT_P", "GND", "HPBAL_R_N")]}[side]
    else:
        cells = [("L", "DACL_AOUT_P", "DACL_AOUT_N", "HPSE_REF_L", "HPSE_L"),
                 ("R", "DACR_AOUT_P", "DACR_AOUT_N", "HPSE_REF_R", "HPSE_R")]
    return cells


def draw_stage(s, variants, kind, side=None):
    """blk.hpa-se (two packages, one per channel) or a blk.hpa-bal sub-sheet (two legs of one channel)."""
    bal = kind == "bal"
    tagbase = "HPB" if bal else "HPS"
    vp, vn = f"HPA_P6V0_{'BAL' if bal else 'SE'}", f"HPA_N6V0_{'BAL' if bal else 'SE'}"
    en = "HPA_BAL_EN" if bal else "HPA_SE_EN"
    f = Flow(s)
    for i, (leg, inp, inn, ref, out) in enumerate(stage_cells(kind, side)):
        title = (f"Leg {leg[0]}{'+' if leg[1] == 'P' else '-'}" if bal else f"Channel {leg}") + " (OPA1622, halves in parallel)"
        grp(f, lambda: opa_cell(s, title, f"{tagbase}_{leg}", inp, inn, ref, en, vp, vn, out), newline=i > 0)
    if not bal:                     # the links of the stage's rails in a column right of the channels
        col = Flow(s, x0=snap(f.x_right + 7.62))
        col.x_max = col.x0 + 90.0
        grp(col, lambda: link_group(s, "LINK_H20", "HPA_P6V0", vp, variants, "Link #7"))
        grp(col, lambda: link_group(s, "LINK_H20", "HPA_N6V0", vn, variants, "Link #8"))
    if bal:
        _stage_tables(s, kind, en, vp, vn, None, None)
        return
    _stage_tables(s, kind, en, vp, vn, 7, 8)


def draw_bal_parent(s, variants):
    f = Flow(s, x0=165.1)               # the sub-sheet column takes the left of the page
    grp(f, lambda: link_group(s, "LINK_H20", "HPA_P6V0", "HPA_P6V0_BAL", variants, "Link #9"))
    grp(f, lambda: link_group(s, "LINK_H20", "HPA_N6V0", "HPA_N6V0_BAL", variants, "Link #10"))
    _stage_tables(s, "bal", "HPA_BAL_EN", "HPA_P6V0_BAL", "HPA_N6V0_BAL", 9, 10, parent=True)


def _stage_tables(s, kind, en, vp, vn, first, second, parent=False):
    bal = kind == "bal"
    s.iface_rows = [
        ["DACx_AOUT_P, DACx_AOUT_N", "Input", "Both stages load the DAC pins; a stage left fitted but unpowered still loads them"],
        [en, "Input", "Pulled down on the host side: packages in shutdown (5 µA per channel)"],
        ["HPBAL_x_P / _N" if bal else "HPSE_L, HPSE_R, HPSE_REF_x", "Output",
         "A disabled OPA1622 output is not high-impedance (SBOS727B §7.4.1)"],
    ]
    if first:
        s.rail_rows = [[vp + ", " + vn, "100 nF per supply pin, after the links",
                        "SBOS727B §10.1; the H20 links sit before them (power tree §4.12)"]]
    else:
        s.rail_rows = [[vp + ", " + vn, "100 nF per supply pin", "SBOS727B §10.1; links #9, #10 on blk.hpa-bal"]]
    if parent:
        corner_notes(s, [
            "1. Function: four OPA1622, one per leg (L+, L-, R+, R-) of the 4.4 mm output, drawn on two",
            "   sub-sheets (left and right channel); this sheet carries the H20 links #9 and #10 of their",
            "   rails, before the local capacitors (power tree §4.12; ADR 0012).",
            "2. Absent state: HPA_BAL_EN pulled down on the host side: shutdown. A disabled output is not",
            "   high-impedance: never fitted but unpowered while the other stage plays (feature blocks #34).",
            "3. Sub-sheet IDs (blk.hpa-bal-*) are sheets of blk.hpa-bal, as the SoC's sub-sheets.",
        ])
        return
    corner_notes(s, [
        "1. Function: " + ("two OPA1622, one per leg of the " + ("left" if "L" in s.block else "right") +
                           " channel of the 4.4 mm output" if bal else
                           "two OPA1622, one per channel of the 3.5 mm output") + "; each half its own",
        "   difference amplifier (R1 = R3 1.00 kΩ, R2 = R4 1.62 kΩ, gain 1.62, 100 pF across R2 and R4),",
        "   feedback at the half's pin, 1.0 Ω ballast to the leg (ADR 0012; BOM v1 lines 19, 37, 107, 108).",
        "2. Absent state: " + en + " pulled down on the host side: shutdown. A disabled output is not",
        "   high-impedance: never fitted but unpowered while the other stage plays (feature blocks #33-34).",
        "3. " + ("R4 returns to ground; the jack's ground pin joins it at the jack." if bal else
                 "R4 returns to HPSE_REF_x, the same 3.5 mm sleeve sense as the DAC's REFA and REFB (PCB-A-16)."),
        "4. Thermal pad (EP) to V- (PCB-A-08). Halves of a package symmetric, legs symmetric (PCB-A-09, -10).",
        ("5. Links H20 #7, #8 on each rail branch, before the local capacitors (power tree §4.12)." if not bal else
         "5. Rails from blk.hpa-bal, after links H20 #9 and #10 (power tree §4.12)."),
        "6. Unless noted: network resistors 0.1 % 0603 thin film, network capacitors C0G 50 V 0603;",
        "   ballast 1 % 0603; decoupling X7R 0402. Mute shunt footprints (BOM v1 line 100): open item.",
    ])


# ---------------------------------------------------------------------- jacks

def tvs_group(s, title, nets):
    """One TPD1E10B06 per net, signal on top, ground below, text to the right. Returns the bbox."""
    g = Group(s, title)
    x = 101.6
    for net in nets:
        # bidirectional: pin 2 up to the signal; the text centred right of the body (rotated fields
        # take no justification)
        part(s, "Device", "D_TVS", x, 101.6, {"2": net, "1": "GND"}, key="D_TPD1E10B06", angle=90, prefix="D",
             ref_at=(x + 2.54 + 2.9, 100.33), val_at=(x + 2.54 + 5.8, 102.87))
        x += 22.86
    g.add((101.6 - 5.08, 101.6 - 7.62 - len(max(nets, key=len)) * 1.16, x - 2.54, 101.6 + 12.7))
    return g.close()


def draw_jack_se(s, variants):
    blk = s.block
    f = Flow(s)

    def jack():
        g = Group(s, "3.5 mm jack (SJ2-35954D)")
        u = ic(s, "same-sky", "SJ2-35954D-SMT-TR", 101.6, 101.6, prefix="J", pins=
               {"2": "HPSE_L", "3": "HPSE_R", "4": "GND", "1": "GND", "10": "HP_DET_SE", "11": None},
               extra={"Constraints": "PCB-A-11 PCB-A-17"})
        g.add(u.bbox)
        return g.close()
    grp(f, jack)

    def ties():
        g = Group(s, "Reference net ties at the sleeve (PCB-A-03, -16)")
        g.add(two_pin_box(s, "NT_SENSE", 101.6, 101.6, "HPSE_REF_L", "GND"))
        g.add(two_pin_box(s, "NT_SENSE", 101.6, 114.3, "HPSE_REF_R", "GND"))
        return g.close()
    grp(f, ties)
    grp(f, lambda: tvs_group(s, "ESD and detect (BOM v1 line 36)", ("HPSE_L", "HPSE_R", "HP_DET_SE")))
    s.iface_rows = [
        ["HPSE_L, HPSE_R", "Input", "Not applicable: never omitted (BRD-011)"],
        ["HPSE_REF_L, HPSE_REF_R", "Passive", "Join ground at the sleeve pin only"],
        ["HP_DET_SE", "Output", "Pull-up on the host side; reads the tip switch"],
    ]
    corner_notes(s, [
        "1. Function: 3.5 mm TRRS jack used as TRS (tip L, ring 1 R, ring 2 and sleeve ground; BOM v1",
        "   line 30); TPD1E10B06 on each output and the detect line (line 36).",
        "2. Absent state: passive. Plug detect: the tip switch (pin 10, normally closed to the tip,",
        "   UNVERIFIED by text) on HP_DET_SE, read by expander P10 with its pull-up on the host side.",
        "3. HPSE_REF_L and _R (DAC REFA, REFB and the SE references) each a separate trace joining",
        "   ground at the sleeve pin through a net tie (PCB-A-03, PCB-A-16, PCB-A-17).",
        "4. Open: RF filter footprints near the jack (PCB-A-19, Q2); the detect polarity (sample).",
    ], w=None)


def draw_jack_bal(s, variants):
    blk = s.block
    f = Flow(s)

    def jack():
        g = Group(s, "4.4 mm jack (GT-3321667P-01)")
        u = ic(s, "g-switch", "GT-3321667P-01", 101.6, 101.6, prefix="J", pins=
               {"7": "HPBAL_L_P", "8": "HPBAL_L_P", "6": "HPBAL_L_N", "4": "HPBAL_R_P", "5": "HPBAL_R_P",
                "2": "HPBAL_R_N", "3": "HPBAL_R_N", "10": "HP_DET_BAL", "9": "GND", "1": "GND"},
               extra={"Constraints": "PCB-A-10 PCB-A-11"})
        g.add(u.bbox)
        return g.close()
    grp(f, jack)
    grp(f, lambda: tvs_group(s, "ESD (BOM v1 line 36)",
                             ("HPBAL_L_P", "HPBAL_L_N", "HPBAL_R_P", "HPBAL_R_N", "HP_DET_BAL")))
    s.iface_rows = [
        ["HPBAL_L_P, _L_N, _R_P, _R_N", "Input", "Not applicable: never omitted (BRD-024)"],
        ["HP_DET_BAL", "Output", "Pull-up on the host side; reads the detect switch"],
    ]
    corner_notes(s, [
        "1. Function: 4.4 mm 5-pole jack (L+, L-, R+, R-, GND; JEITA RC-8141C, BOM v1 line 31);",
        "   TPD1E10B06 on each leg and the detect line (line 36).",
        "2. Absent state: passive. Detect: pin 10 to HP_DET_BAL, pin 9 to ground (switch state",
        "   UNVERIFIED on the drawing), read by expander P11 with its pull-up on the host side.",
        "3. Pin-to-pad assignment UNVERIFIED (kicad-lib note): check against a sample before boards.",
        "4. Open: RF filter footprints near the jack (PCB-A-19, Q2); the Pentaconn alternate land.",
    ])


# ---------------------------------------------------------------------- host side (blk.soc-vccio-b)

def draw_host(s, y0, variants, y_right=None):
    """Absent-state and isolation parts of blk.audio on the host side (feature blocks §1). The
    isolation group starts at y0, the pulls group at y_right (default y0)."""
    blk = s.block
    s.group_box("DAC I2C isolation (BOM v1 line 133, G2)", 25.4, y0, 132.08, 63.5)
    cap(s, "C_100n_0402", 33.02, y0 + 25.4, "vcca1v8_pmu")
    ic(s, "texas-instruments", "SN74LVC2G66DCUR", 83.82, y0 + 33.02,
       {"1A": "I2C2_SCL", "1B": "DAC_I2C_SCL", "1C": "DAC_DIG_1V8", "2A": "I2C2_SDA", "2B": "DAC_I2C_SDA",
        "2C": "DAC_DIG_1V8", "VCC": "vcca1v8_pmu", "GND": "GND"})
    for i, (net, alt) in enumerate((("SCL", "I2C2_SCL"), ("SDA", "I2C2_SDA"))):
        two_pin_v(s, "R_4k7", 116.84 + i * 15.24, y0 + 20.32, "DAC_DIG_1V8", f"DAC_I2C_{net}", blk)   # rail values apart
        two_pin_h(s, "R_0_0402", 129.54, y0 + 45.72 + i * 10.16, alt, f"DAC_I2C_{net}", blk,
                  extra={"Alternate": "dac-i2c-bypass"}, dnp=True)
    y0 = y0 if y_right is None else y_right
    s.group_box("Audio pulls and RX clock option (B9; pinout v1)", 170.18, y0, 226.06, 63.5)
    pulls = [("R_4k7", "DAC_DIG_1V8", "DAC_INT_N")] + [
        ("R_100k", net, "GND") for net in ("DAC_RST_N", "DAC_VP_EN", "DAC_DIG_EN", "AUDIO_LN_EN", "HPA_SE_EN",
                                           "HPA_BAL_EN", "HPA_LDO_EN")]
    for i, (key, a, b) in enumerate(pulls):
        two_pin_v(s, key, 180.34 + i * 17.78, y0 + 20.32, a, b, blk)
    for i, (a, b) in enumerate((("I2S_BCLK_RX", "I2S_BCLK"), ("I2S_LRCK_RX", "I2S_LRCK"))):
        two_pin_h(s, "R_0_0402", 205.74 + i * 66.04, y0 + 48.26, a, b, blk,
                  extra={"Alternate": "i2s-rx-clocks"}, dnp=True)
