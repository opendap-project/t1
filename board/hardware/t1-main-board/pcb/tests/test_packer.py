import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import random

import packer


def brute(free_rows, ncols, w, h):
    out = set()
    for r in range(len(free_rows) - h + 1):
        for c in range(ncols - w + 1):
            if all((free_rows[rr] >> cc) & 1 for rr in range(r, r + h) for cc in range(c, c + w)):
                out.add((c, r))
    return out


def test_feasible_matches_brute_force():
    rnd = random.Random(3)
    ncols, nrows = 23, 17
    rows = [sum((rnd.random() < 0.8) << i for i in range(ncols)) for _ in range(nrows)]
    for w, h in ((1, 1), (2, 3), (5, 2), (7, 7), (4, 9)):
        feas = packer.feasible(rows, w, h)
        got = {(c, r) for r, row in enumerate(feas) for c in range(ncols) if (row >> c) & 1}
        assert got == brute(rows, ncols, w, h), (w, h)


def test_nearest_bit():
    rows = [0, 0, 1 << 10, 0, 1 << 2]
    assert packer.nearest_bit(rows, 3, 4, 20) == (2, 4)
    assert packer.nearest_bit(rows, 9, 1, 20) == (10, 2)
    assert packer.nearest_bit([0, 0], 0, 0, 5) is None


def test_grid_rect_occupancy():
    g = packer.Grid(0, 0, 2, 2)
    span = g.cells((0.5, 0.5, 1.0, 1.0))
    assert span == (10, 20, 10, 20)
    assert not g.any_set(span)
    g.set_rect((0.5, 0.5, 1.0, 1.0))
    assert g.all_set(span)
    assert not g.any_set(g.cells((1.0, 0.5, 1.5, 1.0)))       # touching is free
    assert abs(g.area() - 0.25) < 1e-9


def test_clear_disc():
    g = packer.Grid(-2, -2, 2, 2, fill=True)
    g.clear_disc(0, 0, 1.0)
    assert not g.any_set(g.cells((-0.6, -0.6, 0.6, 0.6)))
    assert g.all_set(g.cells((1.5, 1.5, 1.9, 1.9)))


def test_transform_front_and_back():
    # front, 90 degrees counter-clockwise: +x goes to +y in the device frame (y up)
    assert packer.transform(1.0, 0.0, "F", 90) == (0.0, 1.0)
    # back as build.py places it: the local y is mirrored
    assert packer.transform(1.0, -0.5, "B", 0) == (1.0, -0.5)
    assert packer.transform(1.0, -0.5, "F", 0) == (1.0, 0.5)
    b = packer.box((-1.0, -0.5, 1.0, 0.5), "F", 90)
    assert b == (-0.5, -1.0, 0.5, 1.0)


def test_offsets_sorted_by_distance():
    off = packer.offsets(5.0)
    d = [round((x * x + y * y) ** 0.5, 4) for x, y in off]
    assert d == sorted(d)
    assert off[0] == (0.0, 0.0)


class Tests(unittest.TestCase):
    pass


for _n, _f in list(globals().items()):
    if _n.startswith("test_") and callable(_f):
        setattr(Tests, _n, (lambda f: lambda self: f())(_f))
del _n, _f
