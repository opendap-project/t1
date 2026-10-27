"""Placement on a small synthetic netlist: every part placed, inside its zone, no overlap."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import checks
import netlist
import placement

NET = '''(export (version "E")
 (components
  (comp (ref "U900") (value "IC") (footprint "Lib:QFN") (fields (field (name "Block") "blk.tpm")) (tstamps "a"))
  (comp (ref "C900") (value "100 nF") (footprint "Lib:C0402") (fields (field (name "Block") "blk.tpm")) (tstamps "b"))
  (comp (ref "C901") (value "100 nF") (footprint "Lib:C0402") (fields (field (name "Block") "blk.tpm")) (tstamps "c"))
  (comp (ref "C902") (value "10 uF") (footprint "Lib:C0805") (fields (field (name "Block") "blk.gauge")) (tstamps "d"))
  (comp (ref "TP900") (value "TP") (footprint "Lib:TP") (fields (field (name "Block") "blk.tpm")) (tstamps "e")))
 (nets
  (net (code "1") (name "GND") (node (ref "U900") (pin "1")) (node (ref "C900") (pin "2")) (node (ref "C901") (pin "2")) (node (ref "C902") (pin "2")))
  (net (code "2") (name "/TPM_VDD") (node (ref "U900") (pin "2")) (node (ref "C900") (pin "1")) (node (ref "C901") (pin "1")) (node (ref "TP900") (pin "1")))
  (net (code "3") (name "VSYS") (node (ref "C902") (pin "1")))))
'''

GEOM = {
    "Lib:QFN": {"courtyard": [-2.5, -2.5, 2.5, 2.5], "pad_pos": {"1": [-1.0, 0.0], "2": [1.0, 0.0]}, "holes": []},
    "Lib:C0402": {"courtyard": [-0.95, -0.5, 0.95, 0.5], "pad_pos": {"1": [-0.5, 0], "2": [0.5, 0]}, "holes": []},
    "Lib:C0805": {"courtyard": [-1.75, -1.0, 1.75, 1.0], "pad_pos": {"1": [-0.9, 0], "2": [0.9, 0]}, "holes": []},
    "Lib:TP": {"courtyard": [-1.05, -1.05, 1.05, 1.05], "pad_pos": {"1": [0, 0]}, "holes": []},
}


def test_small_board_places_everything_in_zone():
    nl = netlist.parse(NET)
    heights = {"U900": 0.8, "C900": 0.5, "C901": 0.5, "C902": 1.25, "TP900": 0.04}
    p = placement.Placer(nl, GEOM, heights)
    placed, failed = p.run({})
    assert not failed
    assert set(placed) == set(nl.components)
    assert placed["C902"].side == "B"           # 1.25 mm: back only
    assert placed["TP900"].side == "F"          # test pads on the front (ADR 0016)
    assert placed["C902"].zone == "POWER"
    # decoupling next to its IC
    u, c = placed["U900"], placed["C900"]
    assert ((u.x - c.x) ** 2 + (u.y - c.y) ** 2) ** 0.5 < 6.0
    pl = {r: {"side": q.side, "zone": q.zone, "rect": q.rect, "zones": q.zones} for r, q in placed.items()}
    f = checks.run(pl, heights, p.zone_rects)
    assert not [x for x in f if x[0] in ("courtyard overlap", "PCB-S-16 zone")], f


def test_placement_is_deterministic():
    nl = netlist.parse(NET)
    heights = {"U900": 0.8, "C900": 0.5, "C901": 0.5, "C902": 1.25, "TP900": 0.04}
    a, _ = placement.Placer(nl, GEOM, heights).run({})
    b, _ = placement.Placer(nl, GEOM, heights).run({})
    assert {r: (q.x, q.y, q.rot, q.side) for r, q in a.items()} == {r: (q.x, q.y, q.rot, q.side) for r, q in b.items()}


class Tests(unittest.TestCase):
    pass


for _n, _f in list(globals().items()):
    if _n.startswith("test_") and callable(_f):
        setattr(Tests, _n, (lambda f: lambda self: f())(_f))
del _n, _f
