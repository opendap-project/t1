import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import plan

LIBS_MODELS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "lib", "opendap", "kicad", "3dmodels")


class ModelFor(unittest.TestCase):
    """plan.model_for: libs envelopes for the stock lands that ship no KiCad 10 model."""

    def test_stock_lands_without_a_model(self):
        for fpid in plan.MODEL_BY_FOOTPRINT:
            self.assertTrue(plan.model_for(fpid, "").endswith(".step"))

    def test_xxl4020_by_height(self):
        self.assertIn("_H1.2.step", plan.model_for("Inductor_SMD:L_Coilcraft_XxL4020", "XGL4012-221MEC"))
        self.assertIn("_H1.5.step", plan.model_for("Inductor_SMD:L_Coilcraft_XxL4020", "XGL4015-471MEC"))
        self.assertIn("_H2.1.step", plan.model_for("Inductor_SMD:L_Coilcraft_XxL4020", "XAL4020-102MEC"))

    def test_xxl4020_unknown_part_refused(self):
        with self.assertRaises(ValueError):
            plan.model_for("Inductor_SMD:L_Coilcraft_XxL4020", "XGL4030-102MEC")

    def test_other_lands_keep_their_own(self):
        self.assertIsNone(plan.model_for("Resistor_SMD:R_0402_1005Metric", "RC0402FR-0710KL"))

    def test_every_envelope_exists_in_the_pinned_libs(self):
        paths = set(plan.MODEL_BY_FOOTPRINT.values()) | set(plan.MODEL_BY_MPN.values())
        for p in sorted(paths):
            with self.subTest(model=p):
                f = p.replace("${OPENDAP_KICAD_3DMODELS}", LIBS_MODELS)
                self.assertTrue(os.path.exists(f), "missing %s: bump the libs submodule" % f)


if __name__ == "__main__":
    unittest.main()
