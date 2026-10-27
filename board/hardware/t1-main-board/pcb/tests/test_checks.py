import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import checks
import geometry as g
import zones


def zr():
    return {z: {"F": zones.zone_layer_rects()[z]["F.Cu"], "B": zones.zone_layer_rects()[z]["B.Cu"]} for z in g.ZONES}


def test_overlap_and_height_findings():
    placed = {
        "C1": {"side": "F", "zone": "CORE", "rect": (0, 10, 2, 11)},
        "C2": {"side": "F", "zone": "CORE", "rect": (1, 10.5, 3, 11.5)},       # overlaps C1
        "C3": {"side": "B", "zone": "CORE", "rect": (0, 10, 2, 11)},            # other side: no overlap
        "U9": {"side": "F", "zone": "CORE", "rect": (5, 10, 7, 12)},            # too tall for the front
    }
    heights = {"C1": 0.5, "C2": 0.5, "C3": 0.5, "U9": 1.2}
    f = checks.run(placed, heights, zr())
    rules = {(r, ref) for r, ref, _ in f}
    assert ("courtyard overlap", "C1") in rules
    assert ("PCB-Z-03", "U9") in rules
    assert not any(ref == "C3" for _, ref, _ in f)


def test_hole_ring_and_edge():
    hx, hy = g.HOLES[0]
    placed = {
        "C5": {"side": "F", "zone": "CORE", "rect": (hx + 2.0, hy - 0.5, hx + 3.0, hy + 0.5)},
        "R5": {"side": "F", "zone": "CORE", "rect": (g.HX - 0.2, 0, g.HX, 1)},
    }
    f = checks.run(placed, {"C5": 0.5, "R5": 0.3}, zr(), exempt_zone={"C5", "R5"})
    rules = {(r, ref) for r, ref, _ in f}
    assert ("PCB-H-05", "C5") in rules
    assert ("PCB-B-01", "R5") in rules


class Tests(unittest.TestCase):
    pass


for _n, _f in list(globals().items()):
    if _n.startswith("test_") and callable(_f):
        setattr(Tests, _n, (lambda f: lambda self: f())(_f))
del _n, _f
