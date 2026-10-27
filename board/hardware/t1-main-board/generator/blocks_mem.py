"""blk.lpddr4x and blk.emmc."""

from __future__ import annotations

import re

import library
from draw import (corner_notes, decouple, iface_table, link, link_variants, put_unit, rail_table, two_pin_h,
                  two_pin_v)
from parts import fields
from sch import snap, snap_up

# ---------------------------------------------------------------------- LPDDR4X


def sheet_lpddr4x(proj):
    return proj.sheet("lpddr4x.kicad_sch", "blk.lpddr4x", "LPDDR4X memory",
                      "4 GB LPDDR4X on both RK3566 channels, its 0.6 V VDDQ regulator and supply links", "A3")


def dram_net(name):
    """DRAM ball name -> board net: the same-named SoC ball (HDG 1.1 p. 22; pinout v1)."""
    m = re.fullmatch(r"CA(\d)_([AB])", name)
    if m:
        return f"DDR_A{m[1]}_{m[2]}"
    m = re.fullmatch(r"DQ(\d+)_([AB])", name)
    if m:
        return f"DDR_DQ{m[1]}_{m[2]}"
    m = re.fullmatch(r"DMI(\d)_([AB])", name)
    if m:
        return f"DDR_DM{m[1]}_{m[2]}"
    m = re.fullmatch(r"DQS(\d)_([tc])_([AB])", name)
    if m:
        return f"DDR_DQS{m[1]}{'P' if m[2] == 't' else 'N'}_{m[3]}"
    m = re.fullmatch(r"CK_([tc])_([AB])", name)
    if m:
        return f"DDR_CLK{'P' if m[1] == 't' else 'N'}_{m[2]}"
    m = re.fullmatch(r"CS0_([AB])", name)
    if m:
        return f"DDR_CS0_{m[1]}_N"
    m = re.fullmatch(r"CKE0_([AB])", name)
    if m:
        return f"DDR_CKE0_{m[1]}"
    m = re.fullmatch(r"ODT_CA_([AB])", name)
    if m:
        return f"DDR_ODT0_CA_{m[1]}"
    return {"RESET_n": "DDR_RESET_N", "ZQ0": "DDR_ZQ0", "VDD1": "vcc1v8_ddr", "VDD2": "vcc_ddr",
            "VDDQ": "vcc0v6_ddr", "VSS": "GND", "NC": None, "DNU": None}[name]


def draw_lpddr4x(s, variants):
    blk = s.block
    sym = library.load("Micron", "MT53E1G32D2FW-046")
    ref = s.next_ref("U")
    nets = {p.number: dram_net(p.name) for p in sym.pins}
    f = {"Block": blk, "Constraints": "PCB-I-05",
         "Second_Source": "CXMT CXDB5CBAM-MA-B (same land; after one qualification build, board ADR 0022 item 2)",
         "Manufacturer_2": "CXMT", "MPN_2": "CXDB5CBAM-MA-B"}
    # top band: the two channels, the calibration/reset unit and the unused balls
    xr, _ = put_unit(s, sym, ref, 2, 25.4, 27.94, nets, f)
    xr, _ = put_unit(s, sym, ref, 3, xr + 10.16, 27.94, nets, f)
    xc, yc = put_unit(s, sym, ref, 1, xr + 10.16, 27.94, nets, f)
    s.group_box("ZQ calibration (ADR 0022)", xr + 7.62, yc + 7.62, 48.26, 27.94)   # title clear of the unit
    two_pin_v(s, "R_240", xr + 25.4, yc + 20.32, "vcc0v6_ddr", "DDR_ZQ0", blk)
    put_unit(s, sym, ref, 6, xc + 25.4, 27.94, nets, f)
    # middle band: supplies and ground
    xp, yp = put_unit(s, sym, ref, 4, 25.4, 132.08, nets, f)
    put_unit(s, sym, ref, 5, xp + 12.7, 132.08, nets, f)
    rows = []
    # lower band: VDD2 decoupling, in placement order
    y = 205.74
    refs = []
    xe = decouple(s, "vcc_ddr", ["C_100n_0402"] * 10 + ["C_1u_0402", "C_22u_0603_10V", "C_22u_0603_10V"],
                  27.94, y, blk, refs_out=refs)      # the rail's value inside the group
    s.group_box("vcc_ddr (VDD2) decoupling", 22.86, y - 10.16, snap(xe - 22.86), 27.94)
    rows.append(["vcc_ddr", f"{refs[0][0]}-{refs[-1][0]}: 10 x 100 nF, 1 µF, 2 x 22 µF",
                 "Radxa ZERO 3W v1.12 reference set (BOM v1 §5)"])
    # upper right: TPS7A1006, IN = vcc_ddr, BIAS = vcc1v8_ddr, EN = vcc_ddr (BOM v1 line 9)
    lx, ly = 266.7, 43.18
    s.group_box("VDDQ 0.6 V regulator (BOM v1 line 9)", lx - 7.62, ly - 12.7, 101.6, 53.34)   # ground texts inside
    ldo = library.load("T1_Main_Board", "TPS7A1006PDSER")
    uref = s.next_ref("U")
    pl = s.place(ldo, uref, lx + 35.56, ly + 7.62, fields={"Block": blk})
    s.connect(pl, "6", "vcc_ddr", stub=10.16)
    s.connect(pl, "4", "vcc1v8_ddr", stub=10.16)
    s.connect(pl, "3", "vcc_ddr", stub=10.16)
    s.connect(pl, "2", None)
    s.connect(pl, "1", "VCC0V6_DDR_SRC", stub=5.08)
    s.connect(pl, "5", "GND")
    two_pin_v(s, "C_4u7_0402", lx - 2.54, ly + 27.94, "vcc_ddr", "GND", blk)
    two_pin_v(s, "C_100n_0402", lx + 12.7, ly + 27.94, "vcc1v8_ddr", "GND", blk)
    two_pin_v(s, "C_4u7_0402", lx + 76.2, ly + 27.94, "VCC0V6_DDR_SRC", "GND", blk)
    rows.append(["vcc0v6_ddr", "4.7 µF at IN, 100 nF at BIAS, 4.7 µF at OUT",
                 "CIN >= 2.2 µF, CBIAS 0.1 µF, COUT 2.2-22 µF; 4.7 µF per the worked example (SBVS314B §8.2.2)"])
    # links: vcc_ddr (#3, H5), vcc0v6_ddr (#6, H20), vcc1v8_ddr (#13, M); power tree §4.12
    ky = 101.6
    link(s, "LINK_H5", 266.7, ky, "VCC_DDR_SRC", "vcc_ddr", link_variants("LINK_H5", variants), title="Link #3")
    link(s, "LINK_H20", 266.7, ky + 25.4, "VCC0V6_DDR_SRC", "vcc0v6_ddr", link_variants("LINK_H20", variants),
         title="Link #6")
    link(s, "LINK_M", 353.06, ky, "vcca1v8_pmu", "vcc1v8_ddr", link_variants("LINK_M", variants),
         title="Link #13")
    rows.append(["vcc1v8_ddr", "none drawn", "VDD1 decoupling not given by the DRAM data sheet (UNVERIFIED)"])
    s.iface_rows = [
        ["DDR_*_A, DDR_*_B", "SoC to DRAM", "Not applicable: blk.lpddr4x is never omitted"],
        ["DDR_RESET_N", "Input", "Not applicable"],
        ["VCC_DDR_SRC", "Supply in", "RK809 BUCK3 output (blk.pmic), before the link"],
    ]
    s.rail_rows = rows
    corner_notes(s, [
        "1. Function: 4 GB LPDDR4X, Micron MT53E1G32D2FW-046 IT:C (WT:C accepted), two 16 Gb dies, one",
        "   per channel, single rank (board ADR 0022 item 1).",
        "2. Open part, one land: the part choice stays open between Micron and the CXMT CXDB5CBAM-MA-B",
        "   second source (ADR 0022, DRAM sourcing matrix); it plugs in only through this symbol and",
        "   the kicad-lib land, sized for both bodies (10 x 15 mm envelope, 1.1 mm maximum height).",
        "3. Single rank: the RK3566 CS1, CKE1 and ODT1_CA outputs carry no-connect flags (blk.soc-ddr) and",
        "   ball A8 (ZQ1 on dual-rank parts) has no resistor. A dual-rank part needs a new decision and",
        "   a symbol change (ADR 0022 item 4).",
        "4. Absent state: not applicable (never omitted; BRD-037). Supplies: VDD1 vcc1v8_ddr (always on),",
        "   VDD2 vcc_ddr (on in suspend), VDDQ vcc0v6_ddr from the TPS7A1006 (power tree §4.8).",
        "5. Every ball goes to the same-named SoC ball, order not swapped (HDG 1.1 p. 22). ZQ0: 240 Ω",
        "   1 % to VDDQ (Micron z42n p. 33). Constraints: PCB-I-05.",
        "6. Links: shunt in full, 0 Ω in production except H5 (BOM v1 line 137). FB3 senses vcc_ddr.",
        "7. Open: VDD1 and VDDQ decoupling at the DRAM (data sheet silent, UNVERIFIED); the DNP",
        "   TPS7A2018 vcc1v8_ddr option of BOM v1 line 132 is not drawn yet.",
        "8. Unless noted: capacitors 0402 X5R/X7R rated at least twice the rail; resistors 1 %.",
    ])


# ---------------------------------------------------------------------- eMMC


def sheet_emmc(proj):
    return proj.sheet("emmc.kicad_sch", "blk.emmc", "eMMC storage",
                      "32 GB eMMC 5.1 on the RK3566 eMMC interface, HS200, with its supply links", "A3")


EMMC_NETS = {"CLK": "EMMC_CLK_DEV", "CMD": "EMMC_CMD", "DAT0": "EMMC_D0", "DAT1": "EMMC_D1", "DAT2": "EMMC_D2",
             "DAT3": "EMMC_D3", "DAT4": "EMMC_D4", "DAT5": "EMMC_D5", "DAT6": "EMMC_D6", "DAT7": "EMMC_D7",
             "Data Strobe": "EMMC_DS", "RSTN": "EMMC_RST_N", "VDDI": "EMMC_VDDI", "VDDF": "EMMC_VCC", "VDD": "EMMC_VCCQ",
             "VSS": "GND", "VSSQ": "GND", "NC": None, "RFU": None}


def draw_emmc(s, variants):
    blk = s.block
    sym = library.load("Samsung", "KLMBG2JETD-B041")
    ref = s.next_ref("U")
    nets = {}
    for p in sym.pins:
        key = p.name if p.name in EMMC_NETS else re.sub(r"_\d+$", "", p.name)
        if key not in EMMC_NETS:
            raise SystemExit(f"generator: eMMC pin {p.number} {p.name} has no net")
        nets[p.number] = EMMC_NETS[key]
    f = {"Block": blk, "Constraints": "PCB-I-06",
         "Second_Source": "Micron, Kioxia, Longsys FORESEE (BOM v1 line 10; land UNVERIFIED)"}
    alt = {"emmc-16gb": {"Value": "KLMAG1JETD-B041", "MPN": "KLMAG1JETD-B041",
                         "Description": "eMMC 5.1, 16 GB, FBGA-153 (BOM v1 line 138; same land UNVERIFIED)"}}
    vv = {}
    for name, v in variants.items():
        b = v.get("blocks", {}).get(blk, {})
        if b.get("state") == "alternate" and b.get("alternate") in alt:
            vv[name] = {"fields": alt[b["alternate"]]}
    s.emmc_variants = vv
    # bus unit with the SoC-side parts in front of it; each group box sized from what it holds
    x1, y1 = 25.4, 33.02
    two_pin_h(s, "R_22", x1 + 20.32, y1 + 7.62, "EMMC_CLK", "EMMC_CLK_DEV", blk)
    two_pin_v(s, "R_10k", x1 + 45.72, y1 + 22.86, "vcc_1v8", "EMMC_CMD", blk)
    two_pin_v(s, "R_10k", x1 + 58.42, y1 + 22.86, "vcc_1v8", "EMMC_D0", blk)
    two_pin_v(s, "R_10k", x1 + 71.12, y1 + 22.86, "EMMC_DS", "GND", blk)
    xb, yb = put_unit_variant(s, sym, ref, 1, x1 + 88.9, y1 + 2.54, nets, f, vv)
    xc, yc = put_unit_variant(s, sym, ref, 2, x1 + 88.9, yb + 5.08, nets, f, vv)
    w = snap_up(max(165.1, max(xb, xc) + 2.54 - (x1 - 2.54)))
    hb = snap_up(max(78.74, yc + 2.54 - (y1 - 5.08)))
    s.group_box("Bus (HDG 1.1 p. 26)", x1 - 2.54, y1 - 5.08, w, hb)
    # supplies, below the bus
    x2, y2 = 25.4, snap(y1 - 5.08 + hb + 12.7)   # its title clear of the bus box
    lv = link_variants("LINK_M", variants)
    link(s, "LINK_M", x2 + 25.4, y2 + 10.16, "vcc3v3_sys", "EMMC_VCC", lv)     # source labels inside the box
    link(s, "LINK_M", x2 + 25.4, y2 + 35.56, "vcc_1v8", "EMMC_VCCQ", lv)
    two_pin_v(s, "C_2u2_0402", x2 + 55.88, y2 + 58.42, "EMMC_VDDI", "GND", blk)
    xd, yd = put_unit_variant(s, sym, ref, 3, x2 + 76.2, y2 + 2.54, nets, f, vv)
    xe, ye = put_unit_variant(s, sym, ref, 4, x2 + 76.2, max(y2 + 50.8, snap_up(yd + 5.08)), nets, f, vv)
    s.group_box("Supplies (power tree §4.12 #14, #15)", x2 - 2.54, y2 - 5.08,
                w, snap_up(max(78.74, ye + 2.54 - (y2 - 5.08))))
    # unused balls (NC and RFU), each with a no-connect flag
    xr, yr = put_unit_variant(s, sym, ref, 5, 228.6, 35.56, nets, f, vv)
    xs_, ys_ = put_unit_variant(s, sym, ref, 6, xr + 25.4, 35.56, nets, f, vv)
    s.group_box("Unused balls (NC, RFU: no connection)", 215.9, 27.94, 177.8,
                snap_up(max(yr, ys_) + 2.54 - 27.94))
    s.iface_rows = [
        ["EMMC_CLK", "Input", "Not applicable: blk.emmc is never omitted for boot (BRD-043)"],
        ["EMMC_CMD, EMMC_D0-D7", "Bidirectional", "Pull-ups on CMD and D0 here (HDG p. 26)"],
        ["EMMC_DS", "Output", "Pull-down here (HDG p. 26)"],
        ["EMMC_RST_N", "Input", "SoC ball pull-down at reset (pinout v1)"],
    ]
    corner_notes(s, [
        "1. Function: internal storage, Samsung KLMBG2JETD-B041 eMMC 5.1, 32 GB, 8-bit HS200 (BOM v1",
        "   line 10; BRD-037, BRD-043). Variant: production open between 16 and 32 GB; the 16 GB part",
        "   (KLMAG1JETD-B041, line 138) is a field override of this symbol, written from the variant files.",
        "2. Absent state: not applicable (never omitted). With an empty eMMC the BootROM falls",
        "   through to microSD or MaskROM (BRD-043).",
        "3. EMMC_CLK: 22 Ω in series at the SoC; CMD and D0 10 kΩ pull-ups; a DS pull-down",
        "   (HDG 1.1 p. 26). The DS pull-down value (10 kΩ) is a capture choice: the HDG gives none.",
        "4. VDDi: 2.2 µF (HDG 1.1 p. 26; CReg value not in the Samsung data sheet, UNVERIFIED).",
        "5. Links M (0.1 Ω full, 0 Ω production) on VCC and VCCQ (power tree §4.12 #14, #15).",
        "6. Open: VCC and VCCQ decoupling at the eMMC (not in the data sheet, UNVERIFIED).",
        "   RFU balls: 'do not use for any usage' (Samsung DS p. 5): no connection, as NC.",
        "7. Constraints: PCB-I-06 (EMMC_SD_50SE). The MaskROM pull on D0 belongs to blk.maskrom.",
    ])
    s.rail_rows = [["EMMC_VCC", "none drawn", "Decoupling not in the data sheet (UNVERIFIED)"],
                   ["EMMC_VCCQ", "none drawn", "As EMMC_VCC"],
                   ["EMMC_VDDI", "2.2 µF", "HDG 1.1 p. 26"]]


def put_unit_variant(s, sym, ref, unit, x, y, nets, f, vv):
    from draw import unit_box, unit_extent, place_unit
    from sch import snap
    bx0, by0, bx1, by1 = unit_box(sym, unit)
    left, right, top, bottom = unit_extent(sym, unit, nets)
    ox = snap(x + left - bx0)
    oy = snap(y + top - by0)
    pl = s.place(sym, ref, ox, oy, unit=unit, fields=f, variants=vv)
    mapping = {p.number: nets[p.number] for p in sym.unit_pins(unit)}
    s.connect_all(pl, mapping)
    return ox + bx1 + right, oy + by1 + bottom
