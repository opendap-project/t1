"""Check packer.transform against pcbnew (run with KiCad's Python; exit status 1 on a mismatch)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pcbnew  # noqa: E402

import packer  # noqa: E402
import libtable  # noqa: E402


def main():
    lib = libtable.read()["Package_TO_SOT_SMD"]
    b = pcbnew.BOARD()
    bad = 0
    for side in "FB":
        for rot in (0, 90, 180, 270):
            fp = pcbnew.FootprintLoad(lib, "SOT-23-5")
            b.Add(fp)
            loc = {p.GetNumber(): (pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)) for p in fp.Pads()}
            fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(100), pcbnew.FromMM(100)))
            if side == "B":
                fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
            fp.SetOrientationDegrees(rot)
            for p in fp.Pads():
                got = (pcbnew.ToMM(p.GetPosition().x) - 100, 100 - pcbnew.ToMM(p.GetPosition().y))
                exp = packer.transform(*loc[p.GetNumber()], side, rot)
                if abs(got[0] - exp[0]) > 1e-6 or abs(got[1] - exp[1]) > 1e-6:
                    bad += 1
                    print("mismatch", side, rot, p.GetNumber(), got, exp)
    print("transform check:", "ok" if not bad else "%d mismatches" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
