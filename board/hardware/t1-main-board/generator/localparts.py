"""Project-local library parts the board needs and libs kicad/ does not carry yet (hardware/lib/).

Each part is drawn from its datasheet, to the craft standard's symbol rules (§9.3):
2.54 mm pins on the 2.54 mm grid, no hidden pins, supply in at the left (converter), output at the
right, ground at the bottom."""

from __future__ import annotations

import os
import sys

import library
from library import HW
from sexpr import n, q

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pcb"))
import shields  # noqa: E402  (pcb/shields.py: the frames of ../shields.toml)

SYM_PATH = os.path.join(HW, "lib", "symbols", "T1_Main_Board.kicad_sym")
FP_DIR = os.path.join(HW, "lib", "footprints", "T1_Main_Board.pretty")


def _eff(hide=False, justify=None):
    j = f" (justify {justify})" if justify else ""
    return f"(effects (font (size 1.27 1.27)){j})" + (" (hide yes)" if hide else "")


def _pin(kind, x, y, angle, name, number):
    return (f"\t\t\t(pin {kind} line (at {n(x)} {n(y)} {angle}) (length 2.54) "
            f"(name {q(name)} {_eff()}) (number {q(number)} {_eff()}))")


def tps7a1006():
    """TI TPS7A1006PDSER, 0.6 V LDO with bias input, WSON-6 DSE0006A (SBVS314B p. 3,
    p. 24 Figure 45). Pin 2 is NC: visible, it takes a no-connect flag (CRAFT-125)."""
    props = [
        ("Reference", "U", (-7.62, 7.62), False, "left"),
        ("Value", "TPS7A1006PDSER", (7.62, 7.62), False, "right"),
        ("Footprint", "Package_SON:WSON-6_1.5x1.5mm_P0.5mm", (0, -12.7), True, None),
        ("Datasheet", "https://www.ti.com/lit/ds/symlink/tps7a10.pdf", (0, -15.24), True, None),
        ("Description", "LDO regulator, 0.6 V fixed, 200 mA, with bias input, WSON-6 1.5 x 1.5 mm (DSE)", (0, -17.78), True, None),
        ("Manufacturer", "Texas Instruments", (0, -20.32), True, None),
        ("MPN", "TPS7A1006PDSER", (0, -22.86), True, None),
        ("ki_keywords", "LDO regulator bias LPDDR4X VDDQ", (0, 0), True, None),
    ]
    out = ['\t(symbol "TPS7A1006PDSER" (pin_names (offset 0.508)) (exclude_from_sim no) (in_bom yes) (on_board yes)']
    for k, v, (x, y), hide, just in props:
        out.append(f"\t\t(property {q(k)} {q(v)} (at {n(x)} {n(y)} 0) {_eff(hide, just)})")
    out.append('\t\t(symbol "TPS7A1006PDSER_0_1" (rectangle (start -7.62 5.08) (end 7.62 -7.62) '
               "(stroke (width 0.254) (type default)) (fill (type background))))")
    pins = [
        _pin("power_in", -10.16, 2.54, 0, "IN", "6"),
        _pin("power_in", -10.16, 0, 0, "BIAS", "4"),
        _pin("input", -10.16, -2.54, 0, "EN", "3"),
        _pin("no_connect", -10.16, -5.08, 0, "NC", "2"),
        _pin("power_out", 10.16, 2.54, 180, "OUT", "1"),
        _pin("power_in", 0, -10.16, 90, "GND", "5"),
    ]
    out.append('\t\t(symbol "TPS7A1006PDSER_1_1"\n' + "\n".join(pins) + ")")
    out.append("\t\t(embedded_fonts no))")
    return "\n".join(out)


def dfe252012f():
    """Murata DFE252012F land: two pads 0.8 x 2.0 mm, 1.2 mm apart, 2.8 mm overall
    (Murata J(E)TE243A-0017B-01 p. 5); no copper or vias under the body (p. 7, notice 2)."""
    return "\n".join([
        '(footprint "L_Murata_DFE252012F" (version 20241229) (generator "t1-main-board-generator")',
        '\t(layer "F.Cu")',
        '\t(descr "Murata DFE252012F power inductor, 2.5 x 2.0 mm; land per J(E)TE243A-0017B-01 p. 5; no vias or copper under the body")',
        '\t(tags "inductor Murata DFE252012F")',
        '\t(attr smd)',
        '\t(property "Reference" "REF**" (at 0 -2.2 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        '\t(property "Value" "L_Murata_DFE252012F" (at 0 2.2 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        '\t(fp_rect (start -1.25 -1.0) (end 1.25 1.0) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))',
        '\t(fp_rect (start -1.65 -1.35) (end 1.65 1.35) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))',
        '\t(fp_line (start -0.45 -1.1) (end 0.45 -1.1) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))',
        '\t(fp_line (start -0.45 1.1) (end 0.45 1.1) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))',
        '\t(pad "1" smd rect (at -1.0 0) (size 0.8 2.0) (layers "F.Cu" "F.Paste" "F.Mask"))',
        '\t(pad "2" smd rect (at 1.0 0) (size 0.8 2.0) (layers "F.Cu" "F.Paste" "F.Mask"))',
        '\t(embedded_fonts no)',
        ')',
    ]) + "\n"


def dfe201610e():
    """Murata DFE201610E land: two pads 0.8 x 1.8 mm, 0.8 mm apart, 2.4 mm overall
    (Murata J(E)TE243A-0001 p. 5, "Recommended PCB pattern"); body 2.0 x 1.6 mm."""
    return "\n".join([
        '(footprint "L_Murata_DFE201610E" (version 20241229) (generator "t1-main-board-generator")',
        '\t(layer "F.Cu")',
        '\t(descr "Murata DFE201610E power inductor, 2.0 x 1.6 mm; land per J(E)TE243A-0001 p. 5")',
        '\t(tags "inductor Murata DFE201610E")',
        '\t(attr smd)',
        '\t(property "Reference" "REF**" (at 0 -1.9 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        '\t(property "Value" "L_Murata_DFE201610E" (at 0 1.9 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        '\t(fp_rect (start -1.0 -0.8) (end 1.0 0.8) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))',
        '\t(fp_rect (start -1.45 -1.15) (end 1.45 1.15) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))',
        '\t(fp_line (start -0.25 -0.95) (end 0.25 -0.95) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))',
        '\t(fp_line (start -0.25 0.95) (end 0.25 0.95) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))',
        '\t(pad "1" smd rect (at -0.8 0) (size 0.8 1.8) (layers "F.Cu" "F.Paste" "F.Mask"))',
        '\t(pad "2" smd rect (at 0.8 0) (size 0.8 1.8) (layers "F.Cu" "F.Paste" "F.Mask"))',
        '\t(embedded_fonts no)',
        ')',
    ]) + "\n"


def aota_b201610():
    """Abracon AOTA-B201610S3R3-101-T land: two pads 1.0 x 1.6 mm, 1.0 mm apart, 3.0 mm overall
    (Abracon Rev A p. 4 "Recommended Land Pattern"); body 2.0 x 1.6 mm. Pad 1 is
    the polarity-dot (+) terminal, marked on the silk (RP2350 DS Figure 28)."""
    return "\n".join([
        '(footprint "L_Abracon_AOTA-B201610" (version 20241229) (generator "t1-main-board-generator")',
        '\t(layer "F.Cu")',
        '\t(descr "Abracon AOTA-B201610 molded power inductor, 2.0 x 1.6 mm, polarity dot at pad 1; land per Rev A p. 4")',
        '\t(tags "inductor Abracon AOTA RP2350 VREG")',
        '\t(attr smd)',
        '\t(property "Reference" "REF**" (at 0 -1.9 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        '\t(property "Value" "L_Abracon_AOTA-B201610" (at 0 1.9 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        '\t(fp_rect (start -1.0 -0.8) (end 1.0 0.8) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))',
        '\t(fp_rect (start -1.75 -1.05) (end 1.75 1.05) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))',
        '\t(fp_line (start -0.35 -0.95) (end 0.35 -0.95) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))',
        '\t(fp_line (start -0.35 0.95) (end 0.35 0.95) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))',
        '\t(fp_circle (center -1.95 -0.95) (end -1.85 -0.95) (stroke (width 0.2) (type solid)) (fill yes) (layer "F.SilkS"))',
        '\t(pad "1" smd rect (at -1.0 0) (size 1.0 1.6) (layers "F.Cu" "F.Paste" "F.Mask"))',
        '\t(pad "2" smd rect (at 1.0 0) (size 1.0 1.6) (layers "F.Cu" "F.Paste" "F.Mask"))',
        '\t(embedded_fonts no)',
        ')',
    ]) + "\n"


def testpoint_d08():
    """Round SMD test pad 0.8 mm for signal nets (PCB-D-06, source [JD] of the PCB design constraints: the minimum for signal
    nets; power and ground nets keep KiCad's 1.0 mm pad). Drawn as KiCad's TestPoint_Pad_D1.0mm:
    courtyard 0.5 mm around the pad, silk ring 0.2 mm outside it, no pad fabrication property (as KiCad's)."""
    return "\n".join([
        '(footprint "TestPoint_Pad_D0.8mm" (version 20241229) (generator "t1-main-board-generator")',
        '\t(layer "F.Cu")',
        '\t(descr "SMD pad as test point, diameter 0.8 mm (signal nets, PCB-D-06)")',
        '\t(tags "test point SMD pad")',
        '\t(attr exclude_from_pos_files exclude_from_bom)',
        '\t(property "Reference" "REF**" (at 0 -1.35 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        '\t(property "Value" "TestPoint_Pad_D0.8mm" (at 0 1.35 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        '\t(fp_circle (center 0 0) (end 0 0.6) (stroke (width 0.12) (type solid)) (fill no) (layer "F.SilkS"))',
        '\t(fp_circle (center 0 0) (end 0.9 0) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))',
        '\t(fp_text user "${REFERENCE}" (at 0 -1.35 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        '\t(pad "1" smd circle (at 0 0) (size 0.8 0.8) (layers "F.Cu" "F.Mask"))',
        '\t(embedded_fonts no)',
        ')',
    ]) + "\n"


def sw_ck_pts815():
    """C&K PTS815 tactile switch land (PTS 815 Series data sheet, 8 Apr 21, p. B-44, "P.C.B LAND
    DIMENSION"): four pads 1.0 x 0.7 mm ((5.5 - 3.5) / 2 wide, 0.7 high), inner edges 3.5 mm and outer
    edges 5.5 mm apart across, pad centres 2.15 mm apart along. Body 4.2 x 3.2 mm, 4.6 mm over the
    J terminals, 2.5 +-0.2 mm high (same page). The circuit diagram (same page) joins terminals 1-2
    and 3-4 and switches between the pairs: terminals 1 and 2 are pad 1, terminals 3 and 4 pad 2, the
    two pins of KiCad's SW_Push. Courtyard 0.25 mm around the pads and terminals; no silk (the land
    stands 0.1 mm from the board edge, PCB-D-05), the reference on the fabrication layer."""
    pads = [("1", -2.25, -1.075), ("1", 2.25, -1.075), ("2", -2.25, 1.075), ("2", 2.25, 1.075)]
    out = [
        '(footprint "SW_CK_PTS815" (version 20241229) (generator "t1-main-board-generator")',
        '\t(layer "F.Cu")',
        '\t(descr "C&K PTS815 SMT tactile switch, 4.2 x 3.2 x 2.5 mm; land per the PTS 815 data sheet (8 Apr 21) p. B-44; terminals 1-2 pad 1, 3-4 pad 2")',
        '\t(tags "switch tactile push C&K PTS815")',
        '\t(attr smd)',
        '\t(property "Reference" "REF**" (at 0 -2.4 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        '\t(property "Value" "SW_CK_PTS815" (at 0 2.4 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        '\t(fp_rect (start -2.1 -1.6) (end 2.1 1.6) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))',
        '\t(fp_rect (start -3.0 -1.85) (end 3.0 1.85) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))',
        '\t(fp_text user "${REFERENCE}" (at 0 0 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
    ]
    out += ['\t(pad "%s" smd rect (at %s %s) (size 1.0 0.7) (layers "F.Cu" "F.Paste" "F.Mask"))' % (n_, n(x), n(y))
            for n_, x, y in pads]
    out += ['\t(embedded_fonts no)', ')']
    return "\n".join(out) + "\n"


# Vishay WSL lands (doc 30100, Rev. 23-Nov-2023, p. 2, "Solder pad dimensions"): a = pad length
# along the part, b = pad width, l = gap between the pads, by model and resistance range; body L x W.
WSL_LANDS = [
    # name, model and range as the table prints it, a, b, l, L, W
    ("R_Vishay_WSL1206_2m-5m9", "WSL1206, 0.002 to 0.0059 Ohm", 1.78, 1.93, 1.55, 3.20, 1.60),
    ("R_Vishay_WSL1206_6m-200m", "WSL1206, 0.006 to 0.20 Ohm", 1.65, 1.93, 1.80, 3.20, 1.60),
    ("R_Vishay_WSL2010_7m-500m", "WSL2010, 0.007 to 0.5 Ohm", 1.40, 3.05, 3.30, 5.08, 2.54),
    ("R_Vishay_WSL2512_7m-500m", "WSL2512, 0.007 to 0.5 Ohm", 1.65, 3.68, 4.06, 6.35, 3.18),
]


def wsl(name, model, a, b, l, bl, bw):
    """A Vishay WSL metal-strip shunt land from the doc 30100 pad table: two pads a x b, l apart.
    Courtyard 0.25 mm around the pads (KLC F5.3, as KiCad's resistor lands); no silk (the pads
    reach past the body), the reference on the fabrication layer. The sense traces leave each pad's inner
    edge (doc 30100 p. 2, "Typical sensing traces"; SBOSA81D §8.4.1)."""
    x = (l + a) / 2
    cx = (l / 2 + a) + 0.25
    cy = max(b, bw) / 2 + 0.25
    return "\n".join([
        f'(footprint "{name}" (version 20241229) (generator "t1-main-board-generator")',
        '\t(layer "F.Cu")',
        f'\t(descr "Vishay {model} metal-strip resistor; land per doc 30100 (Rev. 23-Nov-2023) p. 2: a {n(a)}, b {n(b)}, l {n(l)} mm")',
        '\t(tags "resistor shunt current sense Vishay WSL")',
        '\t(attr smd)',
        f'\t(property "Reference" "REF**" (at 0 {n(-cy - 0.6)} 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        f'\t(property "Value" "{name}" (at 0 {n(cy + 0.6)} 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        f'\t(fp_rect (start {n(-bl / 2)} {n(-bw / 2)}) (end {n(bl / 2)} {n(bw / 2)}) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))',
        f'\t(fp_rect (start {n(-cx)} {n(-cy)}) (end {n(cx)} {n(cy)}) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))',
        '\t(fp_text user "${REFERENCE}" (at 0 0 0) (layer "F.Fab") (effects (font (size 0.5 0.5) (thickness 0.08))))',
        f'\t(pad "1" smd rect (at {n(-x)} 0) (size {n(a)} {n(b)}) (layers "F.Cu" "F.Paste" "F.Mask"))',
        f'\t(pad "2" smd rect (at {n(x)} 0) (size {n(a)} {n(b)}) (layers "F.Cu" "F.Paste" "F.Mask"))',
        '\t(embedded_fonts no)',
        ')',
    ]) + "\n"


def xfl3012():
    """Coilcraft XFL3012 land (Document 747-1, revised 03/10/26, "Recommended Land Pattern"): two
    pads 1.0 x 2.90 mm with 2.03 mm between them, 4.03 mm overall; body 3.0 x 3.0 mm, 1.3 mm
    maximum height (same page). Pad 1 is the start lead (the dot; "Connect high dv/dt here for
    lowest EMI", same page): the switch node, marked by the chamfer on the fabrication outline."""
    return "\n".join([
        '(footprint "L_Coilcraft_XFL3012" (version 20241229) (generator "t1-main-board-generator")',
        '\t(layer "F.Cu")',
        '\t(descr "Coilcraft XFL3012 shielded power inductor, 3.0 x 3.0 x 1.3 mm max; land per Document 747-1 (03/10/26); pad 1 = start lead (dot)")',
        '\t(tags "inductor Coilcraft XFL3012")',
        '\t(attr smd)',
        '\t(property "Reference" "REF**" (at 0 -2.4 0) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        '\t(property "Value" "L_Coilcraft_XFL3012" (at 0 2.4 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        '\t(fp_poly (pts (xy -1.0 -1.5) (xy 1.5 -1.5) (xy 1.5 1.5) (xy -1.5 1.5) (xy -1.5 -1.0)) (stroke (width 0.1) (type solid)) (fill no) (layer "F.Fab"))',
        '\t(fp_rect (start -2.27 -1.75) (end 2.27 1.75) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))',
        '\t(fp_line (start -0.8 -1.62) (end 0.8 -1.62) (stroke (width 0.15) (type solid)) (layer "F.SilkS"))',
        '\t(fp_line (start -0.8 1.62) (end 0.8 1.62) (stroke (width 0.15) (type solid)) (layer "F.SilkS"))',
        '\t(fp_text user "${REFERENCE}" (at 0 0 0) (layer "F.Fab") (effects (font (size 0.6 0.6) (thickness 0.09))))',
        '\t(pad "1" smd rect (at -1.515 0) (size 1.0 2.9) (layers "F.Cu" "F.Paste" "F.Mask"))',
        '\t(pad "2" smd rect (at 1.515 0) (size 1.0 2.9) (layers "F.Cu" "F.Paste" "F.Mask"))',
        '\t(embedded_fonts no)',
        ')',
    ]) + "\n"


def shield_frame():
    """Shield-can frame (blk.shields): one pin, the frame land, to ground. Footprint, part number
    and description are per frame (blocks_shields.py), from ../shields.toml."""
    props = [
        ("Reference", "A", (-5.08, 5.08), False, "left"),
        ("Value", "Shield_Frame", (5.08, 5.08), False, "right"),
        ("Footprint", "", (0, -10.16), True, None),
        ("Datasheet", "", (0, -12.7), True, None),
        ("Description", "Shield-can frame, two-piece (frame soldered to the board, lid clipped over it)", (0, -15.24), True, None),
        ("Manufacturer", "", (0, -17.78), True, None),
        ("MPN", "", (0, -20.32), True, None),
        ("ki_keywords", "shield can frame EMC", (0, 0), True, None),
    ]
    out = ['\t(symbol "Shield_Frame" (pin_names (offset 0.508)) (exclude_from_sim yes) (in_bom yes) (on_board yes)']
    for k, v, (x, y), hide, just in props:
        out.append(f"\t\t(property {q(k)} {q(v)} (at {n(x)} {n(y)} 0) {_eff(hide, just)})")
    out.append('\t\t(symbol "Shield_Frame_0_1" (rectangle (start -5.08 2.54) (end 5.08 -5.08) '
               "(stroke (width 0.254) (type default)) (fill (type background))))")
    out.append('\t\t(symbol "Shield_Frame_1_1"\n' + _pin("passive", 0, -7.62, 90, "GND", "1") + ")")
    out.append("\t\t(embedded_fonts no))")
    return "\n".join(out)


def shield_frame_fp(f):
    """The land of one shield frame (../shields.toml through pcb/shields.py): a closed rectangular
    ring of copper, as four SMD pads numbered 1 (the frame's ground), `land` wide; the courtyard is
    the ring from the inside area (`keepout_in` inside the land) to `keepout` beyond the land (two nested rectangles); the
    fabrication layer shows the land outline. Origin at the centre of the inside area (+y down)."""
    li, lo, co, ins = f["land_in"], f["land_out"], f["court_out"], f["inside"]
    cx, cy = f["centre"]

    def r(b):                       # device frame (+y up) to footprint frame (+y down), centred
        return (round(b[0] - cx, 4), round(cy - b[3], 4), round(b[2] - cx, 4), round(cy - b[1], 4))
    li, lo, co, ins = r(li), r(lo), r(co), r(ins)
    pads = [(lo[0], lo[1], lo[2], li[1]), (lo[0], li[3], lo[2], lo[3]),      # top and bottom strips
            (lo[0], li[1], li[0], li[3]), (li[2], li[1], lo[2], li[3])]      # left and right strips
    w, h = f["size"]
    lines = [
        f'(footprint {q(f["footprint"])} (version 20241229) (generator "t1-main-board-generator")',
        '\t(layer "F.Cu")',
        f'\t(descr {q("Shield-can frame land %s (%s): %s x %s mm outside, land %s mm, keep-out %s mm outside and %s mm "
                         "inside, parts inside up to %s mm (../shields.toml)" % (f["id"], f["title"], n(w), n(h), n(f["land"]),
                                                                              n(f["keepout"]), n(f["keepout_in"]), n(f["max_h"])))})',
        '\t(tags "shield can frame EMC")',
        '\t(attr smd)',
        f'\t(property "Reference" "REF**" (at {n(lo[0] + 2.0)} {n(lo[1] - 1.0)} 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12)) (justify left)))',
        f'\t(property "Value" {q(f["footprint"])} (at {n(lo[0] + 2.0)} {n(lo[3] + 1.0)} 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12)) (justify left)))',
    ]
    for b, layer, wd in ((lo, "F.Fab", 0.1), (li, "F.Fab", 0.1), (co, "F.CrtYd", 0.05), (ins, "F.CrtYd", 0.05)):
        lines.append(f'\t(fp_rect (start {n(b[0])} {n(b[1])}) (end {n(b[2])} {n(b[3])}) (stroke (width {n(wd)}) (type solid)) (fill no) (layer "{layer}"))')
    for b in pads:
        x, y = round((b[0] + b[2]) / 2, 4), round((b[1] + b[3]) / 2, 4)
        lines.append(f'\t(pad "1" smd rect (at {n(x)} {n(y)}) (size {n(round(b[2] - b[0], 4))} {n(round(b[3] - b[1], 4))}) '
                     '(layers "F.Cu" "F.Paste" "F.Mask"))')
    lines += ['\t(embedded_fonts no)', ')']
    return "\n".join(lines) + "\n"


# 3D models of the project lands: libs kicad/ envelopes (generator/envelopes.toml, libs v0.3.3).
MODELS = {
    "L_Murata_DFE252012F": ("murata", "L_Murata_DFE252012F"),
    "L_Murata_DFE201610E": ("murata", "L_Murata_DFE201610E"),
    "L_Abracon_AOTA-B201610": ("abracon", "L_Abracon_AOTA-B201610"),
    "SW_CK_PTS815": ("ck", "SW_CK_PTS815"),
    "L_Coilcraft_XFL3012": ("coilcraft", "L_Coilcraft_XFL3012"),
    "R_Vishay_WSL1206_2m-5m9": ("vishay", "R_Vishay_WSL1206"),
    "R_Vishay_WSL1206_6m-200m": ("vishay", "R_Vishay_WSL1206"),
    "R_Vishay_WSL2010_7m-500m": ("vishay", "R_Vishay_WSL2010"),
    "R_Vishay_WSL2512_7m-500m": ("vishay", "R_Vishay_WSL2512"),
}


def with_model(text, name):
    """The footprint text with its libs envelope model, the shield frames' from their own library."""
    key, step = ("shield-frames", name) if name.startswith("Shield_Frame_") else MODELS[name]
    model = ('\t(model "${OPENDAP_KICAD_3DMODELS}/%s.3dshapes/%s.step" (offset (xyz 0 0 0)) '
             '(scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))\n' % (key, step))
    body = text.rstrip("\n")
    assert body.endswith(")")
    return body[:-1] + model + ")\n"


def _fp(name, text):
    with open(os.path.join(FP_DIR, name + ".kicad_mod"), "w", encoding="utf-8") as fh:
        fh.write(with_model(text, name) if (name in MODELS or name.startswith("Shield_Frame_")) else text)


def write():
    os.makedirs(os.path.dirname(SYM_PATH), exist_ok=True)
    with open(SYM_PATH, "w", encoding="utf-8") as fh:
        fh.write('(kicad_symbol_lib (version 20251024) (generator "t1-main-board-generator") (generator_version "10.0")\n'
                 + tps7a1006() + "\n" + shield_frame() + "\n)\n")
    os.makedirs(FP_DIR, exist_ok=True)
    _fp("L_Murata_DFE252012F", dfe252012f())
    _fp("L_Murata_DFE201610E", dfe201610e())
    _fp("L_Abracon_AOTA-B201610", aota_b201610())
    _fp("TestPoint_Pad_D0.8mm", testpoint_d08())
    _fp("SW_CK_PTS815", sw_ck_pts815())
    _fp("L_Coilcraft_XFL3012", xfl3012())
    for land in WSL_LANDS:
        _fp(land[0], wsl(*land))
    for old in os.listdir(FP_DIR):             # a frame whose size changed leaves no stale land
        if old.startswith("Shield_Frame_"):
            os.remove(os.path.join(FP_DIR, old))
    for f in shields.frames():
        _fp(f["footprint"], shield_frame_fp(f))
    library.reset_local()
