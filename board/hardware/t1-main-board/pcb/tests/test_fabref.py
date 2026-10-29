import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import fabref


def square(x, y, half):
    return (x - half, y - half, x + half, y + half)


class Fit(unittest.TestCase):
    """fabref.fit: every fab reference inside its own courtyard, so neighbours' texts never meet."""

    def test_test_pads_at_their_pitch(self):
        # 1.0 mm test pads (KiCad TestPoint_Pad_D1.0mm, courtyard 1.5 mm square) side by side, courtyards touching:
        # the library's text, 1 mm high below each pad, ran into the next one (TP6403 and TP6404 on the T1)
        pads = [("TP6403", square(0.0, 0.0, 0.75)), ("TP6404", square(1.5, 0.0, 0.75))]
        boxes = []
        for ref, cy in pads:
            x, y, a, h = fabref.fit(cy, len(ref))
            box = fabref.text_box(x, y, a, h, len(ref))
            self.assertTrue(fabref.inside(box, cy), (ref, box, cy))
            self.assertGreaterEqual(h, fabref.MIN_H)
            boxes.append((ref, "F", box))
        self.assertEqual(fabref.overlaps(boxes), [])

    def test_large_part_keeps_the_library_size(self):
        self.assertEqual(fabref.fit((0, 0, 12, 12), 5)[3], fabref.MAX_H)

    def test_tall_courtyard_turns_the_text(self):
        x, y, a, h = fabref.fit((0, 0, 0.8, 4.0), 5)
        self.assertEqual((x, y, a), (0.4, 2.0, 90))
        self.assertTrue(fabref.inside(fabref.text_box(x, y, a, h, 5), (0, 0, 0.8, 4.0)))

    def test_centred(self):
        x, y, _, _ = fabref.fit((10, 20, 14, 22), 4)
        self.assertEqual((x, y), (12, 21))

    def test_floor_height(self):
        self.assertEqual(fabref.fit((0, 0, 0.3, 0.3), 6)[3], fabref.MIN_H)


class Overlaps(unittest.TestCase):
    def test_finds_a_pair_on_one_side_only(self):
        a, b = square(0, 0, 0.5), square(0.6, 0, 0.5)
        self.assertEqual(fabref.overlaps([("A", "F", a), ("B", "F", b)]), [("A", "B")])
        self.assertEqual(fabref.overlaps([("A", "F", a), ("B", "B", b)]), [])

    def test_touching_is_not_overlap(self):
        self.assertEqual(fabref.overlaps([("A", "F", square(0, 0, 0.5)), ("B", "F", square(1, 0, 0.5))]), [])


if __name__ == "__main__":
    unittest.main()
