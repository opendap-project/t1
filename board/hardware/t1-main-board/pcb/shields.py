"""Shield-can frames (blk.shields) from ../shields.toml: the geometry the generator draws the frame
lands from and the placement reserves (placement v1 decision 15).

A frame is given by the area its parts may use inside (`inside`); its land stands `keepout_in`
outside that, `land` wide, and the land's courtyard reaches `keepout` beyond the land's outer edge.
Rectangles are (x0, y0, x1, y1) in the device frame, mm, +y up. Pure Python."""

from __future__ import annotations

import os
import tomllib

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "..", "shields.toml")
KEYS = ("side", "height", "lid", "clearance", "land", "keepout", "keepout_in")


def _grow(r, d):
    return (round(r[0] - d, 4), round(r[1] - d, 4), round(r[2] + d, 4), round(r[3] + d, 4))


def _fmt(v):
    return ("%.2f" % v).rstrip("0").rstrip(".")


def frames(path=SOURCE, data=None):
    """One dict per frame: id, title, side, basis, inside, land_in (inner edge of the land), land_out,
    court_out (outer courtyard), centre, size (land outer, w x h), max_h (tallest part inside),
    height (frame with lid) and the footprint name."""
    if data is None:
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
    d = data.get("defaults", {})
    out = []
    for e in data.get("frame", []):
        keep = {k: e.get(k, d.get(k)) for k in KEYS}
        missing = [k for k, v in keep.items() if v is None]
        if missing:
            raise ValueError("shield frame %s: no %s" % (e.get("id"), ", ".join(missing)))
        inside = tuple(float(v) for v in e["inside"])
        if len(inside) != 4 or not (inside[0] < inside[2] and inside[1] < inside[3]):
            raise ValueError("shield frame %s: inside must be (x0, y0, x1, y1) with x0 < x1, y0 < y1" % e.get("id"))
        max_h = round(keep["height"] - keep["lid"] - keep["clearance"], 4)
        if max_h <= 0:
            raise ValueError("shield frame %s: lid and clearance leave no height inside" % e["id"])
        land_in = _grow(inside, keep["keepout_in"])
        land_out = _grow(land_in, keep["land"])
        court_out = _grow(land_out, keep["keepout"])
        w, h = land_out[2] - land_out[0], land_out[3] - land_out[1]
        out.append({
            "id": e["id"], "title": e.get("title", e["id"]), "side": keep["side"], "basis": e.get("basis", ""),
            "inside": inside, "land_in": land_in, "land_out": land_out, "court_out": court_out,
            "centre": (round((inside[0] + inside[2]) / 2, 4), round((inside[1] + inside[3]) / 2, 4)),
            "size": (round(w, 4), round(h, 4)), "land": keep["land"], "keepout": keep["keepout"], "keepout_in": keep["keepout_in"],
            "max_h": max_h, "height": keep["height"], "lid": keep["lid"], "clearance": keep["clearance"],
            "footprint": "Shield_Frame_%s_%sx%smm" % (e["id"], _fmt(w), _fmt(h)),
        })
    ids = [f["id"] for f in out]
    if len(set(ids)) != len(ids):
        raise ValueError("shield frames: duplicate id")
    return out


def ring(outer, inner):
    """The four rectangles of the band between two nested rectangles: bottom, top, left, right."""
    if not (outer[0] <= inner[0] and outer[1] <= inner[1] and inner[2] <= outer[2] and inner[3] <= outer[3]):
        raise ValueError("ring: the inner rectangle is not inside the outer one")
    return [(outer[0], outer[1], outer[2], inner[1]), (outer[0], inner[3], outer[2], outer[3]),
            (outer[0], inner[1], inner[0], inner[3]), (inner[2], inner[1], outer[2], inner[3])]
