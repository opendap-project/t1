"""Project-local library parts the board needs and kicad-lib does not carry yet (hardware/lib/).

Each part is drawn from its parts-lib spec sheet, to the craft standard's symbol rules (§9.3):
2.54 mm pins on the 2.54 mm grid, no hidden pins, supply in at the left (converter), output at the
right, ground at the bottom."""

from __future__ import annotations

import os

import library
from library import HW
from sexpr import n, q

SYM_PATH = os.path.join(HW, "lib", "symbols", "T1_Main_Board.kicad_sym")
FP_DIR = os.path.join(HW, "lib", "footprints", "T1_Main_Board.pretty")


def _eff(hide=False, justify=None):
    j = f" (justify {justify})" if justify else ""
    return f"(effects (font (size 1.27 1.27)){j})" + (" (hide yes)" if hide else "")


def _pin(kind, x, y, angle, name, number):
    return (f"\t\t\t(pin {kind} line (at {n(x)} {n(y)} {angle}) (length 2.54) "
            f"(name {q(name)} {_eff()}) (number {q(number)} {_eff()}))")


def tps7a1006():
    """TI TPS7A1006PDSER, 0.6 V LDO with bias input, WSON-6 DSE0006A (parts-lib sheet: SBVS314B p. 3,
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
    """Murata DFE252012F land: two pads 0.8 x 2.0 mm, 1.2 mm apart, 2.8 mm overall (parts-lib sheet,
    Murata J(E)TE243A-0017B-01 p. 5); no copper or vias under the body (p. 7, notice 2)."""
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
    """Murata DFE201610E land: two pads 0.8 x 1.8 mm, 0.8 mm apart, 2.4 mm overall (parts-lib sheet,
    Murata J(E)TE243A-0001 p. 5, "Recommended PCB pattern"); body 2.0 x 1.6 mm."""
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
    (parts-lib sheet, Abracon Rev A p. 4 "Recommended Land Pattern"); body 2.0 x 1.6 mm. Pad 1 is
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
    """Round SMD test pad 0.8 mm for signal nets (PCB-D-06: the JLCPCB DFT guide's minimum for signal
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


def write():
    os.makedirs(os.path.dirname(SYM_PATH), exist_ok=True)
    with open(SYM_PATH, "w", encoding="utf-8") as fh:
        fh.write('(kicad_symbol_lib (version 20251024) (generator "t1-main-board-generator") (generator_version "10.0")\n'
                 + tps7a1006() + "\n)\n")
    os.makedirs(FP_DIR, exist_ok=True)
    with open(os.path.join(FP_DIR, "L_Murata_DFE252012F.kicad_mod"), "w", encoding="utf-8") as fh:
        fh.write(dfe252012f())
    with open(os.path.join(FP_DIR, "L_Murata_DFE201610E.kicad_mod"), "w", encoding="utf-8") as fh:
        fh.write(dfe201610e())
    with open(os.path.join(FP_DIR, "L_Abracon_AOTA-B201610.kicad_mod"), "w", encoding="utf-8") as fh:
        fh.write(aota_b201610())
    with open(os.path.join(FP_DIR, "TestPoint_Pad_D0.8mm.kicad_mod"), "w", encoding="utf-8") as fh:
        fh.write(testpoint_d08())
    library.reset_local()
