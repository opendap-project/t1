"""Fixture tests of the compaction matrices (python3 -m unittest discover hardware/studies/compaction/tests)."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import compaction as c  # noqa: E402

RULES = {"inductor_peak_max": 0.70, "inductor_limit_max": 1.00, "h_front": 1.0, "h_back": 1.5,
         "mlcc_rating_min": 2.0, "tp_signal_min": 0.8, "tp_power_min": 1.0}
POS = {"refs": ["L1"], "converter": "buck", "l_uh": 1.0, "peak_a": 3.0, "limit_a": 6.5, "continuous_a": 2.0,
       "current": "TALL"}
PARTS = {
    "TALL": {"mpn": "TALL", "l_uh": 1.0, "dcr_mohm": 10.0, "isat30_a": 8.0, "irms_a": 8.0, "h_mm": 2.1,
             "land4020": True, "sourcing": "pass"},
    "LOW": {"mpn": "LOW", "l_uh": 1.0, "dcr_mohm": 15.0, "isat30_a": 7.0, "irms_a": 6.0, "h_mm": 1.5,
            "land4020": True, "sourcing": "pass"},
    "LOW_WEAK": {"mpn": "LOW_WEAK", "l_uh": 1.0, "dcr_mohm": 12.0, "isat30_a": 6.3, "irms_a": 6.0, "h_mm": 1.2,
                 "land4020": True, "sourcing": "pass"},
    "OTHER_L": {"mpn": "OTHER_L", "l_uh": 2.2, "dcr_mohm": 1.0, "isat30_a": 20.0, "irms_a": 20.0, "h_mm": 1.0,
                "land4020": True, "sourcing": "pass"},
}


class Inductors(unittest.TestCase):
    def test_same_inductance_only(self):
        rows = c.inductor_rows(POS, PARTS, RULES)
        self.assertEqual({r["mpn"] for r in rows}, {"TALL", "LOW", "LOW_WEAK"})

    def test_limit_gate(self):
        rows = {r["mpn"]: r for r in c.inductor_rows(POS, PARTS, RULES)}
        self.assertEqual(rows["LOW_WEAK"]["limit_pct"], 103)          # 6.5 / 6.3
        self.assertEqual(rows["LOW_WEAK"]["gates"]["limit"], "fail")
        self.assertEqual(rows["LOW"]["gates"]["limit"], "pass")       # 6.5 / 7.0 = 93 %
        self.assertEqual(rows["TALL"]["gates"]["height"], "fail")

    def test_dcr_loss(self):
        rows = {r["mpn"]: r for r in c.inductor_rows(POS, PARTS, RULES)}
        self.assertEqual(rows["LOW"]["dcr_loss_mw"], 20.0)            # 2 A^2 x 5 mOhm

    def test_choice(self):
        self.assertEqual(c.choose_inductor(c.inductor_rows(POS, PARTS, RULES)), "LOW")
        only_tall = {"TALL": PARTS["TALL"]}
        self.assertEqual(c.choose_inductor(c.inductor_rows(POS, only_tall, RULES)), "TALL")


class Sourcing(unittest.TestCase):
    def test_open_ranks_as_conditional(self):
        self.assertEqual(c.worst("pass", "open"), "conditional")
        self.assertEqual(c.worst("open", "fail"), "fail")


class Capacitors(unittest.TestCase):
    def test_lifecycle(self):
        pos = {"mpn": "C0", "value": "10 uF", "count": 1, "h_mm": 1.25, "rail_v": 5.0}
        cands = [{"mpn": "A", "replaces": "C0", "h_mm": 0.85, "lifecycle": "obsolete", "sourcing": "pass", "dc_bias": "UNVERIFIED"},
                 {"mpn": "B", "replaces": "C0", "h_mm": 0.85, "lifecycle": "active", "sourcing": "pass", "dc_bias": "checked"},
                 {"mpn": "D", "replaces": "C9", "h_mm": 0.5, "lifecycle": "active", "sourcing": "pass", "dc_bias": "checked"}]
        rows = {r["mpn"]: r for r in c.mlcc_rows(pos, cands, RULES)}
        self.assertEqual(set(rows), {"A", "B"})
        self.assertEqual(rows["A"]["verdict"], "fail")
        self.assertEqual(rows["B"]["verdict"], "pass")


class Heights(unittest.TestCase):
    def test_gates(self):
        data = {"rules": RULES, "height": [
            {"refs": ["J1"], "mpn": "TALL", "function": "f", "h_mm": 1.68, "land": "stock", "same_function": True,
             "sourcing": "pass", "current": True},
            {"refs": ["J1"], "mpn": "LOWNEW", "function": "g", "h_mm": 1.42, "land": "none", "same_function": False,
             "sourcing": "pass"}]}
        rows = {r["mpn"]: r for r in c.height_rows(data)}
        self.assertEqual(rows["TALL"]["verdict"], "fail")
        self.assertEqual(rows["LOWNEW"]["verdict"], "conditional")


class Courtyard(unittest.TestCase):
    def test_circle(self):
        with tempfile.NamedTemporaryFile("w", suffix=".kicad_mod", delete=False) as fh:
            fh.write('(footprint "x" (fp_circle (center 0 0) (end 0.9 0) (stroke (width 0.05)) (layer "F.CrtYd")))')
        self.assertAlmostEqual(c.courtyard_area(fh.name), 3.24)
        os.unlink(fh.name)

    def test_silk_circle_ignored(self):
        # KiCad's multi-line layout: a silk circle before the courtyard circle
        with tempfile.NamedTemporaryFile("w", suffix=".kicad_mod", delete=False) as fh:
            fh.write('(footprint "x"\n\t(fp_circle\n\t\t(center 0 0)\n\t\t(end 0 0.7)\n\t\t(layer "F.SilkS")\n\t)\n'
                     '\t(fp_circle\n\t\t(center 0 0)\n\t\t(end 1 0)\n\t\t(layer "F.CrtYd")\n\t)\n)')
        self.assertAlmostEqual(c.courtyard_area(fh.name), 4.0)
        os.unlink(fh.name)


if __name__ == "__main__":
    unittest.main()
