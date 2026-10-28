import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import variants  # noqa: E402

SCH = '''(symbol (lib_id "Device:R") (at 1 1 0)
  (property "Reference" "R1" (at 0 0 0))
  (instances (project "p" (path "/a/b" (reference "R1") (unit 1) (variant (name "production") (field (name "Value") (value "0 \\u03a9"))))))
)
(symbol (lib_id "Device:R") (at 1 1 0)
  (instances (project "p" (path "/a/b" (reference "A1") (unit 1) (variant (name "production") (dnp yes)) (variant (name "lab") (dnp no)))))
)
(symbol (lib_id "power:GND") (at 1 1 0)
  (instances (project "p" (path "/a/b" (reference "#PWR01") (unit 1))))
)
'''

PCB = '''(kicad_pcb
\t(version 20250000)
\t(footprint "Lib:R"
\t\t(layer "F.Cu")
\t\t(property "Reference" "R1"
\t\t\t(at 0 0 0)
\t\t)
\t\t(pad "1" smd rect (at 0 0) (size 1 1))
\t)
\t(footprint "Lib:A"
\t\t(property "Reference" "A1"
\t\t\t(at 0 0 0)
\t\t)
\t)
\t(footprint "Lib:C"
\t\t(property "Reference" "C1")
\t)
)
'''


class Variants(unittest.TestCase):
    def test_reads_instance_data(self):
        d = variants.sch_variants([SCH])
        self.assertEqual(sorted(d), ["A1", "R1"])
        self.assertEqual(sorted(d["A1"]), ["lab", "production"])
        self.assertTrue(d["A1"]["production"].endswith("(dnp yes))"))

    def test_writes_root_and_footprints_and_is_idempotent(self):
        d = variants.sch_variants([SCH])
        once = variants.write_pcb(PCB, d, {"production": "Commercial", "lab": "Bench"})
        self.assertIn('\t(variants\n\t\t(variant (name "lab") (description "Bench"))\n'
                      '\t\t(variant (name "production") (description "Commercial"))\n\t)\n\t(footprint "Lib:R"', once)
        a1 = once[once.index('(footprint "Lib:A"'):once.index('(footprint "Lib:C"')]
        self.assertIn('\t\t(variant (name "lab") (dnp no))\n\t\t(variant (name "production") (dnp yes))\n\t)', a1)
        c1 = once[once.index('(footprint "Lib:C"'):]
        self.assertNotIn("(variant", c1)
        self.assertEqual(variants.write_pcb(once, d, {"production": "Commercial", "lab": "Bench"}), once)
        self.assertEqual(variants.write_pcb(once, {}, {}), PCB)       # no data: nothing left behind


if __name__ == "__main__":
    unittest.main()
