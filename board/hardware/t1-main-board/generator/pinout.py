"""The RK3566 ball-to-net map from pinout v1 (hardware/pinout/pinout-v1.csv)."""

from __future__ import annotations

import csv
import os

from library import HW

CSV = os.path.join(HW, "pinout", "pinout-v1.csv")

def load():
    """ball -> dict(net, block, function, notes); net None for balls left unconnected (NC, RSVD_*)."""
    out = {}
    with open(CSV, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            net = row["net"]
            net = None if net == "NC" or net.startswith("RSVD_") else net   # reserved: no-connect
            out[row["ball"]] = dict(net=net, block=row["block"], function=row["function"], notes=row["notes"],
                                    domain=row["domain"])
    return out
