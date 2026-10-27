"""The RK3566 ball-to-net map from pinout v1 (hardware/pinout/pinout-v1.csv)."""

from __future__ import annotations

import csv
import os

from library import HW

CSV = os.path.join(HW, "pinout", "pinout-v1.csv")

def load():
    """ball -> dict(net, block, function, notes); net None for balls left unconnected (NC, RSVD_*, and
    the spares pinout v1 leaves without a pad)."""
    out = {}
    with open(CSV, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            net = row["net"]
            net = None if net == "NC" or net.startswith("RSVD_") else net   # reserved: no-connect
            if net and net.startswith("SPARE_") and "left unconnected" in row["notes"]:
                net = None          # a spare the pinout leaves without a pad (no stub beside I2S1, FSPI)
            out[row["ball"]] = dict(net=net, block=row["block"], function=row["function"], notes=row["notes"],
                                    domain=row["domain"])
    return out
