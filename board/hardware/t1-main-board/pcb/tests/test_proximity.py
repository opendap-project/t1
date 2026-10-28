"""Capacitor proximity (proximity.py): which capacitor serves which pins, the check, and the
placer keeping a converter's and an IC's capacitors within their bounds."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import netlist
import placement
import proximity


def node(ref, pin, func="", typ="passive"):
    return '(node (ref "%s") (pin "%s") (pinfunction "%s") (pintype "%s"))' % (ref, pin, func, typ)


def comp(ref, value, fp, block, extra=""):
    return ('(comp (ref "%s") (value "%s") (footprint "%s") (fields (field (name "Block") "%s")%s) (tstamps "%s"))'
            % (ref, value, fp, block, extra, ref))


# A buck (U1: VIN, SW, GND, FB), its inductor L1, input C1, output C2; an IC (U2) on the output
# with its decoupling C3; C4 marked by the generator on another block's rail (U2's VDD); R1 a
# divider resistor (never checked).
NET = '(export (version "E") (components %s) (nets %s))' % (
    " ".join([
        comp("U1", "BUCK", "Lib:QFN", "blk.p"), comp("L1", "1 uH", "Lib:L", "blk.p"),
        comp("C1", "10 µF", "Lib:C0603", "blk.p"), comp("C2", "22 µF", "Lib:C0603", "blk.p"),
        comp("U2", "IC", "Lib:QFN", "blk.x"), comp("C3", "100 nF", "Lib:C0402", "blk.x"),
        comp("C4", "1 µF", "Lib:C0402", "blk.y", ' (field (name "Decoupling") "VOUT")'),
        comp("R1", "10 kΩ", "Lib:C0402", "blk.p")]),
    " ".join([
        '(net (code "1") (name "VIN") %s %s)' % (node("U1", "1", "VIN_1", "power_in"), node("C1", "1")),
        '(net (code "2") (name "GND") %s %s %s %s %s %s %s)' % (
            node("U1", "3", "GND_3", "power_in"), node("C1", "2"), node("C2", "2"), node("C3", "2"),
            node("C4", "2"), node("U2", "2", "GND_2", "power_in"), node("R1", "2")),
        '(net (code "3") (name "/BUCK_SW") %s %s)' % (node("U1", "2", "SW_2", "power_out"), node("L1", "1")),
        '(net (code "4") (name "VOUT") %s %s %s %s %s %s)' % (
            node("L1", "2"), node("C2", "1"), node("U2", "1", "VDD_1", "power_in"), node("C3", "1"),
            node("C4", "1"), node("U1", "4", "FB_4", "input")),
        '(net (code "5") (name "X") %s)' % node("R1", "1")]))

GEOM = {
    "Lib:QFN": {"courtyard": [-1.5, -1.5, 1.5, 1.5], "pad_pos": {"1": [-1.0, 0.0], "2": [1.0, 0.0],
                                                                  "3": [0.0, 1.0], "4": [0.0, -1.0]}, "holes": []},
    "Lib:L": {"courtyard": [-1.3, -1.1, 1.3, 1.1], "pad_pos": {"1": [-0.8, 0], "2": [0.8, 0]}, "holes": []},
    "Lib:C0603": {"courtyard": [-1.48, -0.73, 1.48, 0.73], "pad_pos": {"1": [-0.8, 0], "2": [0.8, 0]}, "holes": []},
    "Lib:C0402": {"courtyard": [-0.91, -0.46, 0.91, 0.46], "pad_pos": {"1": [-0.5, 0], "2": [0.5, 0]}, "holes": []},
}
HEIGHTS = {"U1": 0.8, "L1": 0.8, "C1": 0.8, "C2": 0.8, "U2": 0.8, "C3": 0.5, "C4": 0.5, "R1": 0.4}


class Assignments(unittest.TestCase):
    def setUp(self):
        self.nl = netlist.parse(NET)
        self.a = proximity.assignments(self.nl, placement.is_switch_node)

    def test_pin_info_read(self):
        self.assertEqual(self.nl.components["U1"].pin_info["1"], ("VIN_1", "power_in"))

    def test_converter_roles(self):
        self.assertEqual(self.a["C1"]["role"], "input")
        self.assertEqual(self.a["C1"]["owner"], "U1")
        self.assertEqual(self.a["C2"]["role"], "output")
        self.assertIn(("L1", "2"), self.a["C2"]["pins"])
        self.assertEqual(self.a["C2"]["owner_pins"], [("L1", "2")])

    def test_decoupling_in_block_and_marked(self):
        self.assertEqual((self.a["C3"]["role"], self.a["C3"]["owner"]), ("decoupling", "U2"))
        # C4's block has no pin on VOUT: the generator's mark sends it to the rail's supply pins
        self.assertEqual(self.a["C4"]["pins"], [("U2", "1")])

    def test_resistor_not_checked(self):
        self.assertNotIn("R1", self.a)


class Check(unittest.TestCase):
    def test_bound_pass_and_fail(self):
        nl = netlist.parse(NET)
        pos = {("U1", "1"): (0, 0), ("U1", "4"): (0, 0), ("C1", "1"): (2.0, 0), ("L1", "2"): (10, 0),
               ("C2", "1"): (16.0, 0), ("U2", "1"): (30, 0), ("C3", "1"): (31, 0), ("C4", "1"): (40, 0)}
        rows = {r["ref"]: r for r in proximity.check(nl, lambda r, p: pos[(r, p)], set(nl.components),
                                                     placement.is_switch_node)}
        self.assertTrue(rows["C1"]["ok"])                       # 2 mm <= 3 mm
        self.assertFalse(rows["C2"]["ok"])                      # 6 mm from L1.2 > 5 mm
        self.assertTrue(rows["C3"]["ok"])
        self.assertFalse(rows["C4"]["ok"])                      # 10 mm > 4 mm
        self.assertEqual(rows["C2"]["nearest"], "L1.2")


class Placer(unittest.TestCase):
    def test_capacitors_placed_within_bounds(self):
        nl = netlist.parse(NET)
        p = placement.Placer(nl, GEOM, HEIGHTS)
        placed, failed = p.run({})
        self.assertFalse(failed)
        rows = proximity.check(nl, p.pad_xy, set(placed), placement.is_switch_node)
        self.assertEqual([r["ref"] for r in rows if not r["ok"]], [])
        self.assertEqual({r["ref"] for r in rows}, {"C1", "C2", "C3", "C4"})


if __name__ == "__main__":
    unittest.main()
