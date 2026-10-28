import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import geometry as g
import occupancy


def test_part_class():
    assert occupancy.part_class("J4601", 3.3) == "E"
    assert occupancy.part_class("L1", 2.1) == "T"
    assert occupancy.part_class("U1", 1.2) == "B"
    assert occupancy.part_class("C1", 0.5) == "F"


def test_speaker_shelf_is_low_back_area_not_band():
    """The speaker stands on a case shelf (PCB-Z-09): its footprint leaves the band and takes no area."""
    zr = {"POWER": {"F": [], "B": [(-g.HX, -g.HY, g.HX, g.POCKET[1])]}}
    occ = occupancy.placed_occupancy({}, zr)
    sp = (g.SPEAKER[2] - g.SPEAKER[0]) * (g.SPEAKER[3] - g.SPEAKER[1])
    full = 2 * g.HX * (g.POCKET[1] + g.HY)
    assert occ["POWER"]["band"]["courtyard_mm2"] == 0
    assert abs(occ["POWER"]["band"]["area_mm2"] - round(full - sp, 1)) < 0.11
    assert occupancy.SPEAKER_SHADOW == 0


class Tests(unittest.TestCase):
    pass


for _n, _f in list(globals().items()):
    if _n.startswith("test_") and callable(_f):
        setattr(Tests, _n, (lambda f: lambda self: f())(_f))
del _n, _f
