"""Power blocks: blk.pwr-vsys-lv (TPS62136), blk.pwr-3v3-sys (TPS62827), blk.vdd-cpu (TPS62869)
and blk.pmic (RK809-5)."""

from __future__ import annotations

import library
from draw import corner_notes, decouple, gnd, hpart, link, link_variants, tp, two_pin_h, two_pin_v, vpart
from parts import PARTS, fields


def _inductor(s, key, x, y, net_l, net_r):
    return two_pin_h(s, key, x, y, net_l, net_r, s.block, prefix="L")


def _ic(s, lib, name, x, y, extra=None):
    sym = library.load(lib, name)
    ref = s.next_ref("U")
    f = {"Block": s.block}
    f.update(extra or {})
    pl = s.place(sym, ref, x, y, fields=f)
    return pl


# ---------------------------------------------------------------------- 3.8 V pre-regulator

def sheet_vsys_lv(proj):
    return proj.sheet("pwr-vsys-lv.kicad_sch", "blk.pwr-vsys-lv", "3.8 V pre-regulator",
                      "VSYS (2S battery or charger, 6.0-8.8 V) to the always-on VSYS_LV 3.8 V rail, 4 A", "A4")


def draw_vsys_lv(s, variants):
    """Hand-wired: the VSYS rail across the top, ground symbols on one baseline (CRAFT-83)."""
    blk = s.block
    m0 = s.mark()
    yr, yg = 45.72, 101.6                      # VSYS rail, ground baseline
    X, Y = 101.6, 73.66
    pl = _ic(s, "texas-instruments", "TPS62136RGXR", X, Y,
             {"Second_Source": "Texas Instruments TPS62136RGXT (same part, 250-piece reel; BOM v1 line 113)",
              "Manufacturer_2": "Texas Instruments", "MPN_2": "TPS62136RGXT"})
    P = {k: pl.pos(pl.pin(k)) for k in ("8", "10", "11", "9", "2", "6", "5", "4", "7", "1", "3")}
    # input: VSYS, CIN, EN tied to VSYS
    s.group_box("Input", 22.86, 35.56, 50.8, 76.2)
    s.power("VSYS", 30.48, yr)
    s.wire((30.48, yr), (P["1"][0], yr))
    s.wire(P["1"], (P["1"][0], yr))
    ct, cb = vpart(s, "C_22u_0805_25V", 53.34, 63.5)
    s.wire((53.34, yr), ct)
    s.junction(53.34, yr)
    s.wire(cb, (53.34, yg))
    gnd(s, 53.34, yg)
    s.flag_at(53.34, yg - 7.62, "left", 7.62)   # GND: no output pin drives it
    s.wire(P["8"], (78.74, P["8"][1]), (78.74, yr))
    s.junction(78.74, yr)
    # converter: MODE and VSEL low, soft start, ground
    s.group_box("Converter (SLVSDV2)", 76.2, 35.56, 43.18, 76.2)
    s.wire(P["10"], (81.28, P["10"][1]), (81.28, yg))
    s.wire(P["11"], (81.28, P["11"][1]))
    s.junction(81.28, P["11"][1])
    gnd(s, 81.28, yg)
    st, sb = vpart(s, "C_3n3_0402", 86.36, 95.25, text="right")   # its text below the body
    s.wire(P["9"], (86.36, P["9"][1]), st)
    s.wire(sb, (86.36, yg))
    gnd(s, 86.36, yg)
    s.wire(P["3"], (P["3"][0], yg))
    gnd(s, P["3"][0], yg)
    s.nc(*P["4"])
    # PG: down inside the converter group, so its label never reaches the next group
    s.wire(P["7"], (116.84, P["7"][1]), (116.84, P["7"][1] + 2.54))
    s.point("VSYS_LV_PG", 116.84, P["7"][1] + 2.54, "down", "bi")
    # output: inductor, VOS, divider, output capacitors, PG pull-up
    s.group_box("Output and feedback", 121.92, 35.56, 83.82, 76.2)   # the PG pull-up text inside
    yo = P["2"][1]
    xl = 233.68                                  # measurement link
    ll, lr = hpart(s, "L_XGL4020_152", 129.54, yo, prefix="L")   # its rating inside the group
    s.wire(P["2"], ll)
    s.point("VSYS_LV_SW", round((P["2"][0] + ll[0]) / 2 / 1.27) * 1.27, yo, "up")   # switch node (SW_NODE)
    s.wire(lr, (xl - 11.43, yo))
    s.wire(P["6"], (134.62, P["6"][1]), (134.62, yo))
    s.junction(134.62, yo)
    rt, rb = vpart(s, "R_442k", 144.78, 76.2)
    s.wire((144.78, yo), rt)
    s.junction(144.78, yo)
    r2t, r2b = vpart(s, "R_100k", 144.78, 91.44)
    s.wire(rb, r2t)
    s.junction(144.78, 83.82)
    s.wire(P["5"], (139.7, P["5"][1]), (139.7, 83.82), (144.78, 83.82))
    s.wire(r2b, (144.78, yg))
    gnd(s, 144.78, yg)
    for cx in (157.48, 172.72):
        c1, c2 = vpart(s, "C_22u_0805_16V", cx, 78.74)
        s.wire((cx, yo), c1)
        s.junction(cx, yo)
        gnd(s, *c2)
    pt, pb = vpart(s, "R_470k", 190.5, 76.2)
    s.wire((190.5, yo), pt)
    s.junction(190.5, yo)
    s.wire(pb, (190.5, 95.25))
    s.junction(190.5, 93.98)
    s.wire((190.5, 93.98), (185.42, 93.98))
    tp(s, 185.42, 93.98, "VSYS_LV_PG", text="left")
    s.point("VSYS_LV_PG", 190.5, 95.25, "down", "pas")
    # measurement link #5 (H5, kept in every variant), then the rail
    link(s, "LINK_H5", xl, yo, None, "VSYS_LV", link_variants("LINK_H5", variants),
         tp_names=("VSYS_LV_SRC", "VSYS_LV"), title="Link #5")
    s.shift(m0, 0, 10.16)
    s.iface_rows = [
        ["VSYS", "Supply in", "Not applicable: the block is never omitted (BRD-049)"],
        ["VSYS_LV", "Supply out", "Not applicable: always on; feeds the PMIC, vdd_cpu and vcc3v3_sys"],
    ]
    s.rail_rows = [["VSYS", "22 µF 25 V 0805", "CIN 10 µF nominal (SLVSDV2 §10.1.4.2); 3 µF effective minimum (§7.3): 3.9 µF at 8.8 V (BOM v1.18 item 1)"],
                   ["VSYS_LV", "2 x 22 µF 16 V 0805", "COUT 47 µF nominal with 1.5 µH (SLVSDV2 Table 2)"]]
    corner_notes(s, [
        "1. Function: TI TPS62136RGXR, VSYS (6.0-8.8 V, 2S) to VSYS_LV 3.8 V, 4 A. Every part",
        "   on VSYS_LV is rated 5.5 V or less (ADR 0014; BOM v1 line 113).",
        "2. Absent state: not applicable. EN tied to VSYS: always on (feature blocks #10).",
        "3. Output: R1 442 kΩ / R2 100 kΩ with VFB 0.7 V: 3.794 V (SLVSDV2 Eq. 8).",
        "   L: XGL4020-152MEC 1.5 µH (BOM v1 line 114). CSS 3.3 nF, PG 470 kΩ (Table 1).",
        "4. MODE low (auto PFM/PWM), VSEL low (FB2 unused): capture choices, never floating.",
        "5. Link H5 5 mΩ in every variant (BOM line 137); feedback on its source side.",
        "6. PWR_FLAG: VSYS and GND here until blk.charger is drawn; VSYS_LV at the link.",
        "7. Constraints: PCB-P-02, -07, -08. Unless noted: resistors 1 % 0402.",
    ])


def _tp(s, x, y, net):
    tsym = library.load("Connector", "TestPoint")
    ref = s.next_ref("TP")
    pl = s.place(tsym, ref, x, y, fields=fields("TP", s.block), value=net, in_bom=False,
                 ref_at=(x + 1.27, y - 5.08), val_at=(x + 1.27, y - 2.54))
    s.connect(pl, "1", net, stub=2.54)
    return ref


# ---------------------------------------------------------------------- 3.3 V system rail

def sheet_3v3(proj):
    return proj.sheet("pwr-3v3-sys.kicad_sch", "blk.pwr-3v3-sys", "3.3 V system rail",
                      "VSYS_LV to the always-on vcc3v3_sys 3.3 V rail, 4 A", "A4")


def draw_3v3(s, variants):
    """Hand-wired as the pre-regulator: VSYS_LV across the top, ground on one baseline."""
    blk = s.block
    m0 = s.mark()
    yr, yg = 45.72, 101.6
    X, Y = 101.6, 73.66
    pl = _ic(s, "texas-instruments", "TPS62827DMQR", X, Y,
             {"Second_Source": "Texas Instruments TPS62826DMQR (3 A, same land, only while the peak stays <= 2.4 A; BOM v1 line 6)",
              "Manufacturer_2": "Texas Instruments", "MPN_2": "TPS62826DMQR"})
    P = {k: pl.pos(pl.pin(k)) for k in ("1", "5", "3", "2", "6", "4")}
    s.group_box("Input", 22.86, 35.56, 50.8, 76.2)
    s.power("VSYS_LV", 30.48, yr)
    s.wire((30.48, yr), (P["6"][0], yr))
    s.wire(P["6"], (P["6"][0], yr))
    ct, cb = vpart(s, "C_4u7_0603_X7R", 53.34, 63.5)
    s.wire((53.34, yr), ct)
    s.junction(53.34, yr)
    s.wire(cb, (53.34, yg))
    gnd(s, 53.34, yg)
    s.group_box("Converter (SLVSEF9I)", 76.2, 35.56, 43.18, 76.2)
    s.wire(P["1"], (86.36, P["1"][1]), (86.36, yr))
    s.junction(86.36, yr)
    s.wire(P["4"], (P["4"][0], yg))
    gnd(s, P["4"][0], yg)
    s.wire(P["2"], (116.84, P["2"][1]), (116.84, P["2"][1] + 2.54))
    s.point("VCC3V3_SYS_PG", 116.84, P["2"][1] + 2.54, "down", "bi")
    s.group_box("Output and feedback", 121.92, 35.56, 83.82, 76.2)   # the PG pull-up text inside
    yo = P["5"][1]
    xl = 233.68
    ll, lr = hpart(s, "L_XGL4015_471", 129.54, yo, prefix="L")   # its rating inside the group
    s.wire(P["5"], ll)
    s.point("VCC3V3_SYS_SW", round((P["5"][0] + ll[0]) / 2 / 1.27) * 1.27, yo, "up")   # switch node (SW_NODE)
    s.wire(lr, (xl - 11.43, yo))
    rt, rb = vpart(s, "R_453k", 142.24, 76.2)
    s.wire((142.24, yo), rt)
    s.junction(142.24, yo)
    r2t, r2b = vpart(s, "R_100k", 142.24, 91.44)
    s.wire(rb, r2t)
    s.junction(142.24, 82.55)
    s.wire(P["3"], (137.16, P["3"][1]), (137.16, 82.55), (142.24, 82.55))
    s.wire(r2b, (142.24, yg))
    gnd(s, 142.24, yg)
    ft, fb = vpart(s, "C_120p_0402", 154.94, 76.2)
    s.wire((154.94, yo), ft)
    s.junction(154.94, yo)
    s.wire(fb, (154.94, 83.82), (142.24, 83.82))
    s.junction(142.24, 83.82)
    for cx, key in ((170.18, "C_22u_0603_10V"), (182.88, "C_10u_0603")):   # clear of the 120 pF rating
        c1, c2 = vpart(s, key, cx, 78.74)
        s.wire((cx, yo), c1)
        s.junction(cx, yo)
        gnd(s, *c2)
    pt, pb = vpart(s, "R_100k", 195.58, 76.2)
    s.wire((195.58, yo), pt)
    s.junction(195.58, yo)
    s.wire(pb, (195.58, 95.25))
    s.junction(195.58, 93.98)
    s.wire((195.58, 93.98), (190.5, 93.98))
    tp(s, 190.5, 93.98, "VCC3V3_SYS_PG", text="left")
    s.point("VCC3V3_SYS_PG", 195.58, 95.25, "down", "pas")
    link(s, "LINK_H5", xl, yo, None, "vcc3v3_sys", link_variants("LINK_H5", variants),
         tp_names=("VCC3V3_SYS_SRC", "vcc3v3_sys"), title="Link #4")
    s.shift(m0, 0, 10.16)
    s.iface_rows = [
        ["VSYS_LV", "Supply in", "Not applicable: never omitted"],
        ["vcc3v3_sys", "Supply out", "Not applicable: always on (EN = VSYS_LV)"],
    ]
    s.rail_rows = [["VSYS_LV", "4.7 µF 6.3 V X7R 0603", "C1 4.7 µF (SLVSEF9I Fig. 8-2); >= 3 µF effective (p. 14)"],
                   ["vcc3v3_sys", "22 µF + 10 µF 0603", ">= 20 µF effective for the TPS62827 (p. 14; BOM D26); DC bias UNVERIFIED"]]
    corner_notes(s, [
        "1. Function: TI TPS62827DMQR, VSYS_LV to vcc3v3_sys 3.3 V, 4 A, always on (BOM v1",
        "   line 6): RK809 VCC5-9, eMMC, SoC IO banks, radio switch (power tree §3).",
        "2. Absent state: not applicable. EN tied to VSYS_LV (RK809 EXT_EN unused).",
        "3. Feedback: 453 kΩ / 100 kΩ with VFB 0.6 V: 3.318 V (SLVSEF9I Eq. 4; the 450 kΩ",
        "   of Eq. 4 is not an E96 value). C3 120 pF = 12 µs / R2 (Eq. 5).",
        "4. L: Coilcraft XGL4015-471MEC 0.47 µH, 1.5 mm (compaction study, 2026-10-27; was",
        "   Würth 744373240047 of BOM v1 line 106, 1.8 mm, kept as the other-land alternate).",
        "5. Link H5 5 mΩ in every variant (power tree §4.12 #4); feedback on its source side.",
        "6. Unless noted: resistors 1 % 0402; capacitors X5R/X7R, at least twice the rail.",
    ])


# ---------------------------------------------------------------------- vdd_cpu

def sheet_vdd_cpu(proj):
    return proj.sheet("vdd-cpu.kicad_sch", "blk.vdd-cpu", "CPU core supply",
                      "vdd_cpu 0.85-1.15 V for the RK3566 CPU cluster, I2C DVS on I2C0 at 0x42, 6 A", "A3")


def draw_vdd_cpu(s, variants):
    """Hand-wired: VSYS_LV across the top; the VOS sense network below the output (ADR 0021)."""
    blk = s.block
    m0 = s.mark()
    yr, yg = 45.72, 101.6
    X, Y = 116.84, 73.66
    pl = _ic(s, "texas-instruments", "TPS6286910CRQYR", X, Y,
             {"Manufacturer_2": "Texas Instruments", "MPN_2": "TPS628691ARQYR", "Constraints": "PCB-P-07"})
    P = {k: pl.pos(pl.pin(k)) for k in ("4", "5", "6", "7", "8", "9", "3", "1", "2")}
    # input
    s.group_box("Input", 20.32, 35.56, 48.26, 72.39)
    s.power("VSYS_LV", 25.4, yr)
    s.wire((25.4, yr), (P["3"][0], yr))
    s.wire(P["3"], (P["3"][0], yr))
    for cx, key in ((30.48, "C_100n_0402"), (43.18, "C_10u_0603_X7R"), (55.88, "C_10u_0603_X7R")):
        c1, c2 = vpart(s, key, cx, 63.5)
        s.wire((cx, yr), c1)
        s.junction(cx, yr)
        s.wire(c2, (cx, yg))
        gnd(s, cx, yg)
    # enable: 51 kΩ from vcc3v3_pmu, 100 nF to ground (item 5); I2C0
    s.group_box("Enable, control", 71.12, 35.56, 66.04, 72.39)    # the IC value inside
    et, eb = vpart(s, "R_51k", 78.74, 60.96, text="left")
    s.power("vcc3v3_pmu", 78.74, 53.34)
    s.wire((78.74, 53.34), et)
    s.wire(eb, (78.74, P["4"][1]), P["4"])
    ct, cb = vpart(s, "C_100n_0402", 86.36, 83.82)
    s.wire((86.36, P["4"][1]), ct)
    s.junction(86.36, P["4"][1])
    s.wire(cb, (86.36, yg))
    gnd(s, 86.36, yg)
    for k, net in (("5", "I2C0_SDA"), ("6", "I2C0_SCL")):
        s.wire(P[k], (P[k][0] - 2.54, P[k][1]))
        s.point(net, P[k][0] - 2.54, P[k][1], "left", "bi" if k == "5" else "in")
    ya = 96.52                                     # AGND joins PGND at the pins (one ground, CRAFT-85)
    s.wire(P["1"], (P["1"][0], ya), (P["2"][0], ya))
    s.wire(P["2"], (P["2"][0], yg))
    s.junction(P["2"][0], ya)
    gnd(s, P["2"][0], yg)
    xp = P["9"][0] + 2.54                          # PG leaves downward, clear of the VOS route
    s.wire(P["9"], (xp, P["9"][1]), (xp, 88.9))
    s.point("VDD_CPU_PG", xp, 88.9, "down", "bi")
    # output, VOS sense network, link
    s.group_box("Output and sense", 139.7, 35.56, 88.9, 72.39)
    yo = P["7"][1]
    xl = 254.0
    ll, lr = hpart(s, "L_XGL4012_221", 147.32, yo, prefix="L")   # its text inside the group
    s.wire(P["7"], ll)
    s.point("VDD_CPU_SW", round((P["7"][0] + ll[0]) / 2 / 1.27) * 1.27, yo, "up")   # switch node (SW_NODE)
    s.wire(lr, (xl - 11.43, yo))
    for cx in (152.4, 167.64):                    # pitch: the rating clears the next capacitor and ground
        c1, c2 = vpart(s, "C_22u_0603", cx, 76.2)
        s.wire((cx, yo), c1)
        s.junction(cx, yo)
        gnd(s, *c2)
    yv = 91.44                                     # VOS node: inside the output group, apart from ya
    xv = 140.97
    s.wire(P["8"], (xv, P["8"][1]), (xv, yv), (212.09 - 2.54, yv))
    for cx, key, extra, dnp in ((182.88, "R_100", None, False),
                                (193.04, "R_0_0402", {"Alternate": "vos-local-sense"}, True)):
        rt, rb = vpart(s, key, cx, 80.01, extra=extra, dnp=dnp)
        s.wire((cx, yo), rt)
        s.junction(cx, yo)
        s.wire(rb, (cx, yv))
        s.junction(cx, yv)
    vt, vb = vpart(s, "C_100n_0402", 200.66, 97.79)
    s.wire((200.66, yv), vt)
    s.junction(200.66, yv)
    s.wire(vb, (200.66, yg))
    gnd(s, 200.66, yg)
    s.junction(205.74, yv)
    s.wire((205.74, yv), (205.74, 86.36))
    tp(s, 205.74, 86.36, "VDD_CPU_VOS")
    nsym = library.load("Device", "NetTie_2")
    nref = s.next_ref("NT")
    f = fields("NT", blk)
    f["Constraints"] = "PCB-P-07"
    npl = s.place(nsym, nref, 212.09, yv, fields=f, value="NetTie", in_bom=False,
                  ref_at=(212.09, yv + 3.81), val_at=(212.09, yv + 6.35))
    s.wire(npl.pos(npl.pin("2")), (222.25, yv), (222.25, 76.2))
    s.power("vdd_cpu", 222.25, 76.2)
    link(s, "LINK_H5", xl, yo, None, "vdd_cpu", link_variants("LINK_H5", variants),
         tp_names=("VDD_CPU_SRC", "vdd_cpu"), title="Link #1")
    s.shift(m0, 0, 5.08)
    s.iface_rows = [
        ["I2C0_SDA, I2C0_SCL", "Bidirectional", "Not applicable (never omitted); pull-ups on blk.soc-pmuio"],
        ["VSYS_LV", "Supply in", "Not applicable"],
        ["vdd_cpu", "Supply out", "Not applicable"],
    ]
    s.rail_rows = [["VSYS_LV", "2 x 10 µF X7R 0603 + 100 nF", "ADR 0021 item 3; >= 8 µF effective (SLVSFS3B p. 23)"],
                   ["VDD_CPU_SRC", "2 x 22 µF 0603", "ADR 0021 item 3; with the SoC set 97.4 µF nominal (one 22 µF added, note 6)"]]
    _vdd_cpu_pg(s)
    corner_notes(s, [
        "1. Function: TI TPS6286910CRQYR, 6 A, I2C0 0x42, 0.9 V start-up, from VSYS_LV (ADR 0021).",
        "2. Absent state: not applicable (never omitted). EN from vcc3v3_pmu through 51 kΩ",
        "   and 100 nF (item 5): vdd_cpu follows VCC3V3_PMU (HDG p. 34); on in suspend.",
        "3. Sense (item 4): VOS takes its own trace (net tie) from the 22 µF at the SoC, load side",
        "   of the link; 100 Ω to the converter-side output, 100 nF to AGND. The DNP 0 Ω",
        "   (Alternate vos-local-sense) returns to local sense if the load-step check fails.",
        "4. PG (item 6): monitor only, never a reset. DNP 86.6 kΩ 1 %: the TPS628691ARQYR",
        "   same-land alternate (0x41, VSET; Alternate tps628691a).",
        "5. L XGL4012-221MEC 0.22 µH (item 2), land of the 4020 family (UNVERIFIED). At the SoC",
        "   2 x 22 µF + 2 x 4.7 µF (blk.soc-power): 97.4 µF nominal with the 2 x 22 µF here.",
        "6. BRD-049 safety limit: devicetree regulator-max-microvolt = <1100000> (no 1800 MHz /",
        "   1150 mV point) until bring-up shows DC top + load-step peak <= 1.170 V at the SoC.",
        "   The converter accepts up to 1.675 V over I2C: the kernel and U-Boot limits are the ceiling.",
        "7. Link H5 5 mΩ in every variant, inside the VOS loop (power tree §4.12 #1). Groups:",
        "   ADR 0021 items 1-6. Constraints: PCB-P-07, -08. Unless noted: resistors 1 % 0402.",
    ])


def _vdd_cpu_pg(s):
    """PG pull-up, test pad and the A-option resistor, below the input group."""
    y = 134.62
    s.group_box("Power good (item 6)", 25.4, 119.38, 76.2, 30.48)
    s.wire((40.64, y), (91.44, y))
    s.point("VDD_CPU_PG", 40.64, y, "left", "pas")      # its text inside the group
    rt, rb = vpart(s, "R_100k", 55.88, 130.81)
    s.power("vcca1v8_pmu", *rt)
    s.junction(55.88, y)
    s.wire((71.12, y), (71.12, 132.08))
    s.junction(71.12, y)
    tp(s, 71.12, 132.08, "VDD_CPU_PG")
    dt, db = vpart(s, "R_86k6", 91.44, 138.43, extra={"Alternate": "tps628691a"}, dnp=True)
    gnd(s, *db)


# ---------------------------------------------------------------------- RK809-5 PMIC

def sheet_pmic(proj):
    return proj.sheet("pmic.kicad_sch", "blk.pmic", "PMIC",
                      "RK809-5: five bucks, nine LDOs and a switch for the RK3566 domains; RTC, power key, reset", "A3")


BUCKS = [  # (n, SW pin, FB pin, output net, FB net, output capacitors)
    (1, "12", "13", "VDD_LOGIC_SRC", "vdd_logic", ["C_10u_0603", "C_22u_0603"]),
    (2, "9", "8", "vdd_gpu", "vdd_gpu", ["C_10u_0603", "C_22u_0603"]),
    (3, "25", "27", "VCC_DDR_SRC", "VCC_DDR_FB", ["C_22u_0603"]),
    (4, "65", "64", "vdd_npu", "vdd_npu", ["C_10u_0603", "C_22u_0603"]),
    (5, "53", "59", "vcc_1v8", "vcc_1v8", ["C_10u_0603", "C_22u_0603_10V"]),
]
LDOS = {"23": "vdda0v9_image", "21": "vdda_0v9", "20": "vdda0v9_pmu", "28": "FP_VCI_SRC", "29": "vccio_sd",
        "31": "vcc3v3_pmu", "3": "vcca_1v8", "5": "vcca1v8_pmu", "6": "vcca1v8_image", "55": None,
        "58": "vcc3v3_sd"}


def draw_pmic(s, variants):
    """The four RK809-5 units on the left with labels and power symbols at their pins; each buck's
    output stage as a row on the right; decoupling grouped by rail (CRAFT-171)."""
    blk = s.block
    s.bus_row = 8               # the supply inputs reach down to the tables: bus ports in one row
    sym = library.load("rockchip", "RK809-5")
    ref = s.next_ref("U")
    f = {"Block": blk,
         "Second_Source": "Rockchip RK809-5A (BOM v1 line 2)", "Manufacturer_2": "rockchip", "MPN_2": "RK809-5A"}
    # ---- units
    s.group_box("RK809-5", 22.86, 27.94, 180.34, 165.1)
    u1 = s.place(sym, ref, 68.58, 81.28, unit=1, fields=f)
    m1 = {"11": "VSYS_LV", "10": "VSYS_LV", "24": "VSYS_LV", "66": "VSYS_LV", "54": "vcc3v3_sys", "26": "VCC_DDR_SRC"}
    for n_, sw, fb, out, fbnet, caps in BUCKS:
        m1[sw] = f"PMIC_BUCK{n_}_SW"
        m1[fb] = fbnet
    s.connect_all(u1, m1)
    u2 = s.place(sym, ref, 68.58, 162.56, unit=2, fields=f)   # its upright rails clear unit 1's fields
    m2 = {"22": "vcc3v3_sys", "30": "vcc3v3_sys", "4": "vcc3v3_sys", "57": "vcc3v3_sys"}
    m2.update(LDOS)
    s.connect_all(u2, m2)
    u3 = s.place(sym, ref, 160.02, 81.28, unit=3, fields=f)
    s.connect_all(u3, {"1": "I2C0_SCL", "2": "I2C0_SDA", "49": "PMIC_SLEEP", "52": "PWRON_N", "61": "PMIC_VDC",
                       "50": "PMIC_XIN", "51": "PMIC_XOUT", "56": "PMIC_BATDIV", "62": "PMIC_SNS", "63": "PMIC_SNS",
                       "7": "PMIC_INT_N", "67": "SOC_RESET_N", "68": "CLK32K_PMIC", "60": None,
                       "44": "PMIC_VCC_1P8A", "48": "PMIC_VCC_1P8D", "46": "PMIC_VREF", "45": "PMIC_VCC_RTC",
                       "47": "GND", "EP": "GND"})
    u4 = s.place(sym, ref, 160.02, 154.94, unit=4, fields=f)
    m4 = {k: "GND" for k in ("16", "15", "14", "17", "40")}
    m4.update({k: None for k in ("18", "19", "37", "36", "38", "35", "39", "41", "32", "34", "42", "43")})
    m4["33"] = "VSYS_LV"
    s.connect_all(u4, m4)
    # ---- buck output stages, one row each
    s.group_box("Buck output stages", 208.28, 27.94, 127.0, 124.46)
    mb = s.mark()
    for i, (n_, sw, fb, out, fbnet, caps) in enumerate(BUCKS):
        y = 40.64 + i * 22.86
        s.point(f"PMIC_BUCK{n_}_SW", 215.9, y, "left", "pas")
        ll, lr = hpart(s, "L_DFE252012F_R47", 226.06, y, prefix="L")
        s.wire((215.9, y), ll)
        xend = 279.4
        s.wire(lr, (xend, y))
        for j, ck in enumerate(caps):
            cx = 240.03 + j * 12.7
            c1, c2 = vpart(s, ck, cx, y + 6.35)
            s.wire((cx, y), c1)
            s.junction(cx, y)
            gnd(s, *c2)
        if out in ("VDD_LOGIC_SRC", "VCC_DDR_SRC"):
            s.point(out, xend, y, "right", "pas")
        else:
            s.wire((xend, y), (xend + 5.08, y))
            s.flag_net(out, xend + 2.54, y)
            s.attach(out, xend + 5.08, y, "right")
        if n_ == 3:   # FB3: 47 kΩ / 120 kΩ from vcc_ddr, the load side of the link (power tree §3, §4.12 #3)
            rt, rb = vpart(s, "R_47k", 302.26, y - 2.54)
            s.power("vcc_ddr", *rt)
            r2t, r2b = vpart(s, "R_120k", 302.26, y + 10.16)
            s.wire(rb, r2t)
            s.junction(302.26, y + 3.81)
            s.wire((302.26, y + 3.81), (309.88, y + 3.81))
            s.point("VCC_DDR_FB", 309.88, y + 3.81, "right", "pas")
            gnd(s, *r2b)
    s.shift(mb, 10.16, 0)            # the switch-node labels inside the group
    # ---- control support
    cx0 = 342.9                      # one grid step after the buck group
    # the right edge keeps the flow's margin to the frame (draw.Flow: 3.81 mm inside MARGIN)
    s.group_box("Control support", cx0 - 5.08, 27.94, 63.5, 124.46)
    for i, net in enumerate(["PMIC_VCC_1P8A", "PMIC_VCC_1P8D", "PMIC_VREF", "PMIC_VCC_RTC"]):
        x = cx0 + 5.08 + i * 13.97
        s.point(net, x, 43.18, "up", "pas")
        c1, c2 = vpart(s, "C_1u_0402", x, 49.53)
        s.wire((x, 43.18), c1)
        gnd(s, *c2)
    # PWRON: 100 nF to ground; VDC: 100 kΩ / 22 kΩ from VSYS_LV with 100 nF
    x = cx0 + 5.08
    s.point("PWRON_N", x, 68.58, "up", "pas")
    c1, c2 = vpart(s, "C_100n_0402", x, 74.93)
    s.wire((x, 68.58), c1)
    gnd(s, *c2)
    x = cx0 + 25.4
    rt, rb = vpart(s, "R_100k", x, 72.39)
    s.power("VSYS_LV", *rt)
    r2t, r2b = vpart(s, "R_22k", x, 87.63)
    s.wire(rb, r2t)
    s.junction(x, 80.01)
    s.wire((x, 80.01), (x + 12.7, 80.01))
    c1, c2 = vpart(s, "C_100n_0402", x + 12.7, 87.63)
    s.wire((x + 12.7, 80.01), c1)
    gnd(s, *c2)
    gnd(s, *r2b)
    s.junction(x + 7.62, 80.01)
    s.wire((x + 7.62, 80.01), (x + 7.62, 92.71))
    s.point("PMIC_VDC", x + 7.62, 92.71, "down", "pas")
    # 32.768 kHz crystal (load capacitors open, note 7)
    xsym = library.load("opendap-generic", "Crystal")
    xref = s.next_ref("Y")
    xp = dict(Footprint="Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm", Datasheet="https://www.sii.co.jp/hubfs/SC-32S_Leaflet_e_26.pdf",
              Description="Crystal, 32.768 kHz, 20 ppm, CL 7 pF, 3.2 x 1.5 mm (orderable code UNVERIFIED)",
              Manufacturer="Seiko Instruments", MPN="SC-32S 32.768kHz 20ppm 7pF", Block=blk,
              Second_Source="SC-32S 12.5 pF (load capacitors change with it); Epson FC-135 (BOM v1 line 16)")
    plx = s.place(xsym, xref, cx0 + 27.94, 111.76, fields=xp, value="32.768 kHz",
                  ref_at=(cx0 + 24.13, 106.68), val_at=(cx0 + 24.13, 116.84))
    s.connect(plx, "1", "PMIC_XIN")
    s.connect(plx, "2", "PMIC_XOUT")
    for i, net in enumerate(("PMIC_BATDIV", "PMIC_SNS")):
        x = cx0 + 10.16 + i * 30.48
        tp(s, x, 134.62, net)
        s.wire((x, 134.62), (x, 139.7))
        s.point(net, x, 139.7, "down", "pas")
    # ---- decoupling, grouped by rail
    s.group_box("Supply inputs", 22.86, 200.66, 165.1, 30.48)
    decouple(s, "VSYS_LV", ["C_10u_0603"] * 5, 27.94, 213.36, blk)
    decouple(s, "vcc3v3_sys", ["C_10u_0603"] + ["C_1u_0402"] * 4, 104.14, 213.36, blk)
    s.group_box("LDO and switch outputs", 208.28, 162.56, 190.5, 30.48)
    for i, net in enumerate([v for v in LDOS.values() if v]):
        decouple(s, net, ["C_1u_0402"], 218.44 + i * 17.78, 175.26, blk)   # the first value inside
    s.iface_rows = [
        ["I2C0_SCL, I2C0_SDA", "Bidirectional", "Not applicable (never omitted); pull-ups on blk.soc-pmuio"],
        ["PMIC_INT_N, CLK32K_PMIC, SOC_RESET_N", "Output", "Open drain; pull-ups on blk.soc-pmuio"],
        ["PMIC_SLEEP", "Input", "SoC ball pull-down at reset (pinout v1)"],
        ["VDD_LOGIC_SRC, VCC_DDR_SRC", "Supply out", "BUCK1 and BUCK3 outputs, to their links"],
    ]
    s.rail_rows = [["VSYS_LV", "5 x 10 µF", "VCC1-VCC4 10 µF each, VCC_SPK 10 µF (RK809 DS Fig. 1-1)"],
                   ["vcc3v3_sys", "10 µF + 4 x 1 µF", "VCC9 10 µF; VCC5-VCC8 1 µF each (Fig. 1-1)"],
                   ["Buck outputs", "10 µF + 22 µF (BUCK3 22 µF)", "HDG 1.1 near the source; Fig. 1-1 33 µF / 22 µF"],
                   ["LDO outputs", "1 µF each", "Fig. 1-1"]]
    corner_notes(s, [
        "1. Function: Rockchip RK809-5 (BOM v1 line 2): BUCK1 vdd_logic, BUCK2 vdd_gpu, BUCK3 vcc_ddr,",
        "   BUCK4 vdd_npu, BUCK5 vcc_1v8; LDO1-9 and SWOUT2 per power tree §3. VCC1-4 from VSYS_LV,",
        "   VCC5-9 from vcc3v3_sys (ROCK 3C v1.4). SWOUT1 and EXT_EN unused. I2C0 at 0x20.",
        "2. Absent state: not applicable (never omitted). OTP defaults of the -5 part UNVERIFIED.",
        "3. FB1 senses vdd_logic and FB3 the 47k / 120k divider on vcc_ddr, both on the load side of",
        "   their links (blk.soc-power, blk.lpddr4x); BUCK2, 4, 5 sense their outputs.",
        "4. L: Murata DFE252012F-R47M 0.47 µH (BOM v1 line 5). Output capacitors 10 + 22 µF (HDG",
        "   near the source); BUCK3 22 µF (Fig. 1-1). Fig. 1-1's 33 µF is met as 10 + 22 µF.",
        "5. VDC: 100k / 22k from VSYS_LV with 100 nF as Fig. 1-1 from VCC_SYS: 0.69 V > 0.55 V, so",
        "   the PMIC starts when VSYS_LV first rises (bring-up confirms).",
        "6. Codec unused: MCLK, BCLK, LRCLK, SDI, HP_SNS to GND; outputs and MIC1 open (BOM line 2,",
        "   HDG p. 73). PDMCLK is an output (DS p. 14): left open, not grounded as line 2 lists it.",
        "   VCC_SPK_HP from VSYS_LV with 10 µF (Fig. 1-1).",
        "7. Open: BATDIV and SNSP/SNSN (joined, Fig. 1-1) on test pads until the ROCK 3C sheet 28",
        "   wiring is read (UNVERIFIED); 32.768 kHz load capacitors (22 pF optional in Fig. 1-1) not",
        "   fitted with the 7 pF SC-32S (UNVERIFIED); PWRON_N to blk.buttons and blk.maskrom.",
        "8. Groups follow RK809 DS Fig. 1-1 and power tree §3 (BOM v1 line 5); LDO outputs 1 µF each.",
        "   Constraints: PCB-P-07, PCB-P-08 (PMIC_BUCKn_SW). Unless noted: resistors 1 % 0402.",
    ])
