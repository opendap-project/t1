import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import geometry as g  # noqa: E402
import shields  # noqa: E402

FIXTURE = {
    "defaults": {"side": "B", "height": 1.5, "lid": 0.1, "clearance": 0.1, "land": 0.4, "keepout": 0.5,
                 "keepout_in": 0.3},
    "frame": [{"id": "X", "title": "Fixture", "inside": [0.0, 0.0, 10.0, 6.0]},
              {"id": "Y", "inside": [20.0, 0.0, 24.0, 4.0], "land": 0.6}],
}


def area(r):
    return (r[2] - r[0]) * (r[3] - r[1])


class Frames(unittest.TestCase):
    def test_geometry(self):
        x, y = shields.frames(data=FIXTURE)
        self.assertEqual(x["land_in"], (-0.3, -0.3, 10.3, 6.3))
        self.assertEqual(x["land_out"], (-0.7, -0.7, 10.7, 6.7))
        self.assertEqual(x["court_out"], (-1.2, -1.2, 11.2, 7.2))
        self.assertEqual(x["centre"], (5.0, 3.0))
        self.assertAlmostEqual(x["max_h"], 1.3)
        self.assertEqual(x["footprint"], "Shield_Frame_X_11.4x7.4mm")
        self.assertEqual(y["land_out"], (19.1, -0.9, 24.9, 4.9))     # a frame's own land overrides the default

    def test_ring_covers_the_band_once(self):
        x = shields.frames(data=FIXTURE)[0]
        ring = shields.ring(x["court_out"], x["inside"])
        self.assertAlmostEqual(sum(area(r) for r in ring), area(x["court_out"]) - area(x["inside"]))
        for i, a in enumerate(ring):
            for b in ring[i + 1:]:
                ox = min(a[2], b[2]) - max(a[0], b[0])
                oy = min(a[3], b[3]) - max(a[1], b[1])
                self.assertFalse(ox > 1e-9 and oy > 1e-9, (a, b))

    def test_refusals(self):
        bad = {"defaults": dict(FIXTURE["defaults"]), "frame": [{"id": "Z", "inside": [5, 0, 1, 4]}]}
        with self.assertRaises(ValueError):
            shields.frames(data=bad)
        tall = {"defaults": dict(FIXTURE["defaults"], lid=1.0, clearance=0.5), "frame": [{"id": "Z", "inside": [0, 0, 1, 1]}]}
        with self.assertRaises(ValueError):
            shields.frames(data=tall)
        dup = {"defaults": FIXTURE["defaults"], "frame": [FIXTURE["frame"][0], FIXTURE["frame"][0]]}
        with self.assertRaises(ValueError):
            shields.frames(data=dup)
        with self.assertRaises(ValueError):
            shields.ring((0, 0, 1, 1), (0, 0, 2, 2))


class BoardFrames(unittest.TestCase):
    """The board's frames (../shields.toml) against the constraints they cite."""

    def test_back_pocket_only(self):
        for f in shields.frames():
            self.assertEqual(f["side"], "B", f["id"])                  # PCB-Z-03: none under the display
            self.assertLessEqual(f["height"], g.H_BACK_POCKET, f["id"])  # PCB-Z-01, can included
            c = f["court_out"]
            self.assertTrue(-g.HX <= c[0] and c[2] <= g.HX and -g.HY <= c[1] and c[3] <= g.HY, f["id"])

    def test_required_frames(self):
        # PCB-T-06 asks for frames around the SoC and DDR and around the radio; the audio frame was
        # dropped (placement v1 decision 16)
        self.assertEqual({f["id"] for f in shields.frames()}, {"SOC", "RADIO"})

    def test_frames_apart(self):
        fr = shields.frames()
        for i, a in enumerate(fr):
            for b in fr[i + 1:]:
                p, q = a["court_out"], b["court_out"]
                self.assertFalse(min(p[2], q[2]) > max(p[0], q[0]) and min(p[3], q[3]) > max(p[1], q[1]),
                                 (a["id"], b["id"]))


if __name__ == "__main__":
    unittest.main()
