"""Pinout v1 against the library: every RK3566 ball's pad name in hardware/pinout/pinout-v1.csv equals the
name of that ball in the pinned libs pin list (kicad/generator/bga/rockchip/RK3566-pins.csv, transcribed
from the RK3566 datasheet Table 2-1). The board reads the library's output; the library never reads the
board."""

import csv
import os
import tomllib
import unittest

HW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
PINOUT = os.path.join(HW, "pinout", "pinout-v1.csv")
BGA = os.path.join(HW, "lib", "opendap", "kicad", "generator", "bga", "rockchip")


def lib_pins():
    with open(os.path.join(BGA, "RK3566.toml"), "rb") as fh:
        pins = tomllib.load(fh)["part"]["pins"]
    with open(os.path.join(BGA, pins), newline="") as fh:
        return {r["ball"]: r["name"] for r in csv.DictReader(fh)}


def board_pads():
    with open(PINOUT, newline="", encoding="utf-8") as fh:
        return {r["ball"]: r["pad"] for r in csv.DictReader(fh)}


class Tests(unittest.TestCase):
    def test_pinout_pads_match_the_library_pin_list(self):
        lib, board = lib_pins(), board_pads()
        self.assertEqual(set(board), set(lib), "balls only in one: %s" % sorted(set(board) ^ set(lib))[:10])
        wrong = {b: (board[b], lib[b]) for b in lib if board[b] != lib[b]}
        self.assertEqual(wrong, {}, "pad names differ (board, libs)")


if __name__ == "__main__":
    unittest.main()
