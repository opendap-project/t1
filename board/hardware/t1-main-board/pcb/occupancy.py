"""Area budget and occupancy of the placed board (pure Python).

Two views:

1. `floorplan_budget`: floorplan v1's method (docs/specs/floorplan-v1.md §2.1,
   hardware/studies/floorplan/floorplan.py) on the floorplan's zones, with every part's real
   courtyard instead of the study's estimates: classes T (> 1.5 mm, bands only), E (edge parts:
   jacks, USB-C), B (1.0-1.5 mm, back), F (<= 1.0 mm), placement factor 1.7 (1.2 for edge parts);
   tall and edge parts take the band, B parts the back, F parts the back's remainder and then the
   front. The speaker stands on a case shelf (PCB-Z-09, ADR 0025): it takes no board area, and the
   shelf's footprint counts as low back area (parts up to the shelf clearance), not as band. This is
   the number to compare with the floorplan's 205 % / 139 % / 112 % / 106 %.
2. `placed_occupancy`: the placed board as it is, courtyard area over region area, per zone and
   side, with the back split into low area (pocket and shelf) and band (no factor).
"""

from __future__ import annotations

import geometry as g
import zones as zmod

FACTOR, FACTOR_EDGE = 1.7, 1.2
SPEAKER_SHADOW = 0.0       # the speaker on its case shelf takes no board area (PCB-Z-09)
LOW_BACK = (g.POCKET, g.SPEAKER)     # back areas limited to 1.5 mm: the pocket and the speaker shelf
EDGE_PARTS = ("J3401", "J4001", "J4601")       # jacks and USB-C (the study's class E)


def rect_area(r):
    return max(0.0, r[2] - r[0]) * max(0.0, r[3] - r[1])


def clip_area(r, rects):
    return sum(rect_area(i) for q in rects for i in [zmod.intersect(r, q)] if i)


def hole_rings():
    return [(hx - 2.5, hy - 2.5, hx + 2.5, hy + 2.5) for hx, hy in g.HOLES]


def _areas(rects_f, rects_b):
    """front, back, back pocket, back band areas of rectangle sets, less the hole rings (as the study)."""
    rings = hole_rings()
    front = sum(rect_area(r) for r in rects_f) - sum(clip_area(q, rects_f) for q in rings)
    back = sum(rect_area(r) for r in rects_b) - sum(clip_area(q, rects_b) for q in rings)
    pocket = sum(rect_area(p) for p in low_parts(rects_b))
    return front, back, pocket, back - pocket


def band_parts(rects):
    """rects less the low back areas (pocket, shelf)."""
    for low in LOW_BACK:
        rects = [p for r in rects for p in zmod.subtract(r, low)]
    return rects


def low_parts(rects):
    """The parts of rects inside the low back areas (pocket, shelf), without double counting."""
    out = [i for r in rects for i in [zmod.intersect(r, g.POCKET)] if i]
    rest = [p for r in rects for p in zmod.subtract(r, g.POCKET)]
    return out + [i for r in rest for i in [zmod.intersect(r, g.SPEAKER)] if i]


def part_class(ref, h):
    if ref in EDGE_PARTS:
        return "E"
    if h > g.H_BACK_POCKET:
        return "T"
    if h > g.H_FRONT_DISPLAY:
        return "B"
    return "F"


def floorplan_budget(nl, geom, heights, zone_of_block, faceplate_refs, rings=None):
    """Floorplan v1's §2.1 table recomputed with real courtyards on the floorplan's zones. A shield
    frame (rings: ref -> its courtyard ring) counts its ring once, without the routing factor: the
    land and keep-out take board area, and tracks pass under them on the inner layers."""
    need = {z: {"F": 0.0, "B": 0.0, "T": 0.0, "E": 0.0} for z in g.ZONES}
    rings = rings or {}
    for ref, c in nl.components.items():
        z = "FACEPLATE" if ref in faceplate_refs else zone_of_block.get(c.block, "CORE")
        if ref in rings:
            need[z]["B"] += sum(rect_area(q) for q in rings[ref]) / FACTOR
            continue
        cy = geom[c.footprint]["courtyard"]
        need[z][part_class(ref, heights[ref])] += rect_area(cy)
    res = {}
    for z in g.ZONES:
        rf, rb = g.zone_rects(z, "F"), g.zone_rects(z, "B")
        front, back, pocket, band = _areas(rf, rb)
        n = need[z]
        bn = {k: v * (FACTOR_EDGE if k == "E" else FACTOR) for k, v in n.items()}
        band_need = bn["T"] + bn["E"]
        back_left = max(0.0, back - band_need - bn["B"])
        f_back = min(bn["F"], back_left)
        f_front = bn["F"] - f_back
        res[z] = {
            "courtyard_mm2": {k: round(v, 1) for k, v in n.items()},
            "need_mm2": round(sum(bn.values()), 1),
            "front_area_mm2": round(front, 1), "back_area_mm2": round(back, 1), "band_area_mm2": round(band, 1),
            "band_use_pct": round(100 * band_need / band, 1) if band else None,
            "back_use_pct": round(100 * (band_need + bn["B"] + f_back) / back, 1) if back else None,
            "front_use_pct": round(100 * f_front / front, 1) if front else None,
        }
    return res


def placed_occupancy(placed_rects, zone_rects):
    """placed_rects: ref -> (zone, side, rect). zone_rects: zone -> side -> rects (with deltas)."""
    res = {}
    for z, sides in zone_rects.items():
        row = {}
        for s in ("F", "B"):
            rects = sides[s]
            area = sum(rect_area(r) for r in rects)
            used = sum(clip_area(r, rects) for zz, ss, r in placed_rects.values() if ss == s and zz == z)
            row[s] = {"area_mm2": round(area, 1), "courtyard_mm2": round(used, 1),
                      "use_pct": round(100 * used / area, 1) if area else None}
            if s == "B":
                band_rects = band_parts(rects)
                band = sum(rect_area(r) for r in band_rects)
                bused = sum(clip_area(r, band_rects) for zz, ss, r in placed_rects.values() if ss == "B")
                row["band"] = {"area_mm2": round(band, 1), "courtyard_mm2": round(bused, 1),
                               "use_pct": round(100 * bused / band, 1) if band else None}
        res[z] = row
    return res
