import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import itertools

import geometry as g
import zones


def area(r):
    return (r[2] - r[0]) * (r[3] - r[1])


def test_subtract_keeps_area():
    a = (0, 0, 10, 10)
    b = (2, 3, 5, 12)
    parts = zones.subtract(a, b)
    assert abs(sum(area(p) for p in parts) - (100 - 3 * 7)) < 1e-9
    for p, q in itertools.combinations(parts, 2):
        assert zones.intersect(p, q) is None


def test_zones_do_not_overlap_on_any_layer():
    zl = zones.zone_layer_rects()
    for layer in zones.CU:
        rects = [(z, r) for z in zl for r in zl[z][layer]]
        for (za, a), (zb, b) in itertools.combinations(rects, 2):
            if za != zb:
                i = zones.intersect(a, b)
                assert i is None or area(i) < 1e-6, (layer, za, zb, a, b)


def test_faceplate_area_front_is_faceplate_only():
    zl = zones.zone_layer_rects()
    for z in zl:
        if z == "FACEPLATE":
            continue
        for r in zl[z]["F.Cu"]:
            i = zones.intersect(r, g.FP)
            assert i is None or area(i) < 1e-6, z


def test_corridors_straddle_two_zones():
    zl = zones.zone_layer_rects()
    for name, r in zones.corridors().items():
        touched = {z for z in zl for q in zl[z]["B.Cu"] + zl[z]["F.Cu"] if zones.intersect(r, q)}
        assert len(touched) >= 2, name


class Tests(unittest.TestCase):
    pass


for _n, _f in list(globals().items()):
    if _n.startswith("test_") and callable(_f):
        setattr(Tests, _n, (lambda f: lambda self: f())(_f))
del _n, _f
