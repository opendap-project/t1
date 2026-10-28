"""Part heights above the board, from each footprint's 3D model (STEP), pure Python.

The height of a model is the largest z of its STEP points, after the footprint's model offset and
scale (models rotated about x or y take their largest extent). Models are the library's (kicad-lib
or KiCad's stock models) and stand for the part's maximum body; a model's height is checked against
the data sheet when the height decides a zone (`OVERRIDES` records every value set by hand, with its
source).
"""

from __future__ import annotations

import os
import re

import libtable

_POINT = re.compile(r"CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(\s*([-+0-9.Ee]+)\s*,\s*([-+0-9.Ee]+)\s*,\s*([-+0-9.Ee]+)\s*\)")
_UNIT = re.compile(r"SI_UNIT\s*\(\s*\.MILLI\.\s*,\s*\.METRE\.\s*\)|CONVERSION_BASED_UNIT\s*\(\s*'INCH'")

# Heights (mm) set by hand: footprints without a model, or where the data sheet's maximum is
# the value that decides a height zone. Source in the comment of each row.
OVERRIDES = {
    "NetTie:NetTie-2_SMD_Pad0.5mm": (0.04, "copper only"),
    "TestPoint:TestPoint_Pad_D1.0mm": (0.04, "copper only"),
    "T1_Main_Board:TestPoint_Pad_D0.8mm": (0.04, "copper only"),
    "TestPoint:TestPoint_Pad_2.0x2.0mm": (0.04, "copper only"),
    "T1_Main_Board:L_Murata_DFE252012F": (1.2, "Murata DFE252012F: 2.5 x 2.0 x 1.2 mm max (part number code F = 1.2 mm)"),
    "T1_Main_Board:L_Murata_DFE201610E": (1.0, "Murata DFE201610E: 2.0 x 1.6 x 1.0 mm max (code E = 1.0 mm)"),
    "T1_Main_Board:L_Abracon_AOTA-B201610": (1.0, "Abracon AOTA-B201610: 2.0 x 1.6 x 1.0 mm (series code 201610), UNVERIFIED"),
    "T1_Main_Board:L_Murata_LQH3NP_3x3mm": (1.1, "Murata LQH3NPN220MMEL: 3.0 x 3.0 mm, 1.1 mm max (MM code), UNVERIFIED: sheet not retrieved"),
    "T1_Main_Board:L_Wuerth_WE-LHMI_4020": (2.0, "Wuerth WE-LHMI 4020: 4.0 x 4.0 x 2.0 mm (size code), UNVERIFIED: sheet not retrieved"),
    "T1_Main_Board:SW_CK_PTS815": (2.5, "C&K PTS815: height UNVERIFIED (drawing not retrieved), taken as a band part"),
    "Inductor_SMD:L_Coilcraft_XxL4020": (2.1, "Coilcraft XAL4020/XGL4020: 2.1 mm max (PCB-Z-05)"),
    "hirose:Hirose_DF40C-50DS-0.4V_2x25_P0.4mm_Vertical": (1.6, "DF40C-50DS: 1.45 +- 0.15 mm (PCB-Z-05, RFC 0015)"),
    "Fuse:Fuse_Littelfuse-NANO2-451_453": (2.69, "Littelfuse NANO2 451/453 body 6.10 x 2.69 x 2.69 mm, UNVERIFIED (catalog figure, no KiCad model)"),
    "Package_SON:Texas_DPY0002A_0.6x1mm_P0.65mm": (0.4, "TI DPY0002A (X1SON) 0.4 mm maximum package height, no KiCad model"),
    "Package_TO_SOT_SMD:SOT-523": (0.8, "SOT-523 (SC-89) outline 0.8 mm maximum, no KiCad model; UNVERIFIED against each part's sheet"),
    "hirose:Hirose_FH35C-51S-0.3SHW_1x51-1MP_P0.3mm_Horizontal": (1.0, "FH35C: 0.9 +- 0.1 mm (PCB-Z-03, ADR 0016)"),
}


# Heights (mm) by part number, where one footprint carries parts of several heights (the XxL4020
# land takes the 2.1, 1.5 and 1.2 mm Coilcraft lines). Source in each row.
BY_MPN = {
    "XGL4012-221MEC": (1.2, "Coilcraft XGL4012: 1.2 mm max (Document 1718 drawing)"),
    "XEL4012-920NEC": (1.2, "Coilcraft XEL4012-920NE: 4 x 4 x 1.2 mm (SLVSGC5E Table 9-2)"),
    "GRM188R60J476ME15D": (1.0, "Murata SimSurfing product list: 1.0 mm max (2026-10-28)"),
    "XGL4015-102MEC": (1.5, "Coilcraft XGL4015: 1.5 mm max (Document 1660 drawing)"),
    "XGL4015-471MEC": (1.5, "Coilcraft XGL4015: 1.5 mm max (Document 1660 drawing)"),
    "GRM21BR61E226ME44L": (1.45, "Murata SimSurfing product list: 1.45 mm max (2026-10-27)"),
    "GRM219R61C226ME15L": (1.0, "Murata SimSurfing product list: 1.0 mm max (2026-10-27)"),
}


def _expand(path: str) -> str:
    return libtable.expand(path)


_cache = {}


def step_extent(path: str):
    """(zmin, zmax, xymax) of a STEP file's points in mm, or None if unreadable."""
    if path in _cache:
        return _cache[path]
    res = None
    if os.path.exists(path):
        with open(path, encoding="latin-1") as fh:
            text = fh.read()
        scale = 25.4 if "'INCH'" in text and "MILLI" not in text else 1.0
        zs, xy = [], 0.0
        for m in _POINT.finditer(text):
            x, y, z = (float(v) * scale for v in m.groups())
            zs.append(z)
            xy = max(xy, abs(x), abs(y))
        if zs:
            res = (min(zs), max(zs), xy)
    _cache[path] = res
    return res


def height(fpid: str, geom: dict, mpn: str = ""):
    """(height mm, source) of a footprint's part (its part number first, where BY_MPN has it)."""
    if mpn in BY_MPN:
        return BY_MPN[mpn]
    if ":Shield_Frame_" in fpid:          # a shield frame: its height with the lid (../shields.toml)
        import shields
        for f in shields.frames():
            if fpid.endswith(":" + f["footprint"]):
                return f["height"], "shields.toml: frame with lid"
    if fpid in OVERRIDES:
        return OVERRIDES[fpid]
    best = None
    for m in (geom or {}).get("models", []):
        ext = step_extent(_expand(m["file"]))
        if ext is None:
            continue
        zmin, zmax, xy = ext
        if abs(m.get("rot_x", 0)) > 1 or abs(m.get("rot_y", 0)) > 1:
            h = max(zmax, xy)
        else:
            h = zmax * m.get("scale_z", 1.0) + m.get("offset_z", 0.0)
        best = h if best is None else max(best, h)
    if best is None:
        return None, "no model"
    return round(best, 3), "3D model"
