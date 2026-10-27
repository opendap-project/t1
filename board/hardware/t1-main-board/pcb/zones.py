"""Zone rectangles per copper layer: floorplan v1's zones with the placement deltas (pure Python)."""

from __future__ import annotations

import geometry as g
import plan

CU = ["F.Cu", "In1.Cu", "In2.Cu", "In3.Cu", "In4.Cu", "B.Cu"]
LAYER_SPEC = {
    None: CU,
    "front": ["F.Cu", "In1.Cu"],
    "back": ["B.Cu"],
    "not_back": CU[:-1],
    "inner_back": CU[2:],
}
SIDE_LAYER = {"F": "F.Cu", "B": "B.Cu"}


def intersect(a, b):
    r = (max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]))
    return r if r[2] > r[0] + 1e-9 and r[3] > r[1] + 1e-9 else None


def subtract(a, b):
    """a minus b as up to four rectangles."""
    i = intersect(a, b)
    if not i:
        return [a]
    out = []
    if i[1] > a[1]:
        out.append((a[0], a[1], a[2], i[1]))
    if i[3] < a[3]:
        out.append((a[0], i[3], a[2], a[3]))
    if i[0] > a[0]:
        out.append((a[0], i[1], i[0], i[3]))
    if i[2] < a[2]:
        out.append((i[2], i[1], a[2], i[3]))
    return out


def zone_layer_rects():
    """zone -> copper layer -> rectangles."""
    res = {z: {L: [] for L in CU} for z in g.ZONES}
    for z, rects in g.ZONES.items():
        for r, spec in rects:
            for L in LAYER_SPEC[spec]:
                res[z][L].append(tuple(r))
    # The faceplate connection area carries the FH35C and its ESD only (ADR 0016 item 1): on the
    # front layers it belongs to the faceplate zone alone (floorplan v1's I/O rectangle overlaps it)
    for z in res:
        if z != "FACEPLATE":
            for L in LAYER_SPEC["front"]:
                res[z][L] = [p for r in res[z][L] for p in subtract(r, g.FP)]
    for zone, rect, spec, _ in plan.ZONE_DELTAS:
        for L in LAYER_SPEC[spec]:
            for z in res:
                if z != zone:
                    res[z][L] = [p for r in res[z][L] for p in subtract(r, rect)]
            res[zone][L].append(tuple(rect))
    return res


def rule_areas():
    """(zone, rect, [layers]): one rule area per rectangle, layers merged where the rectangle is the same."""
    zl = zone_layer_rects()
    out = []
    for z in g.ZONES:
        by_rect = {}
        for L in CU:
            for r in zl[z][L]:
                key = tuple(round(v, 4) for v in r)
                by_rect.setdefault(key, []).append(L)
        for r, layers in sorted(by_rect.items()):
            out.append((z, r, layers))
    return out


def corridors():
    res = dict(g.CORRIDORS)
    for k, (r, _) in plan.CORRIDOR_DELTAS.items():
        res[k] = r
    return res
