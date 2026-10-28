"""blk.shields: the shield-can frames (BOM v1 line 90; feature blocks, the entry after #50).

One frame part per frame of ../shields.toml (read through pcb/shields.py, the same data the
placement reserves): its land to ground, not fitted in either variant (fitted only if EMC or audio
measurements require it, BOM v1 line 90). Sources: PCB-T-06, PCB-EMC-03, PCB-Z-01, PCB-Z-03,
amended T1-038 (made-to-order parts), board placement v1 decision 15."""

from __future__ import annotations

import library
from blocks_audio import grp
from draw import Flow, Group, corner_notes, unit_box, unit_extent
from localparts import shields
from sch import snap, snap_up

DRAWING = "https://github.com/opendap-project/board/blob/main/hardware/t1-main-board/shields.toml"


def sheet(proj):
    return proj.sheet("shields.kicad_sch", "blk.shields", "Shield-can frames",
                      "Etched two-piece shield-can frames on the back: SoC and LPDDR4X, radio module "
                      "(not fitted)", "A4")


def _frames(s, frames, variants):
    """The frame parts side by side in one group, sized from them (CRAFT-174): each frame is one
    small symbol, so a group per frame would take its width from its title, not its contents."""
    g = Group(s, "Frames")
    x = 101.6
    for f in frames:
        box = _frame(s, f, variants, x, 101.6)
        g.add(box)
        x = snap(box[2] + 7.62 - (box[0] - x))
    return g.close()


def _frame(s, f, variants, x, y):
    """One frame part: placed like draw.ic, not fitted (dnp). Returns its bbox."""
    sym = library.load("T1_Main_Board", "Shield_Frame")
    ref = s.next_ref("A")   # A: a separable assembly (frame and lid); H* is the mounting holes' in the rules
    w, h = f["size"]
    fields = {
        "Block": s.block,
        "Footprint": "T1_Main_Board:" + f["footprint"],
        "Datasheet": DRAWING,
        "Description": "Shield-can frame %s, two-piece etched (frame + lid), %s x %s mm land outside, "
                       "%s mm with the lid, parts inside up to %s mm; made to order (T1-038)"
                       % (f["id"], _n(w), _n(h), _n(f["height"]), _n(f["max_h"])),
        "Manufacturer": "Made to order (etched)",
        "MPN": "T1-SHIELD-%s" % f["id"],
        "Alternate": "shield-fit",          # a not-fitted footprint, fitted on measurement (CRAFT-147)
    }
    # KiCad variant data: not fitted in every variant whose file says so (the base design is `full`)
    kv = {name: {"dnp": True} for name, v in variants.items()
          if v.get("kind") != "full" and v.get("blocks", {}).get(s.block, {}).get("state") == "dnp"}
    pl = s.place(sym, ref, x, y, fields=fields, value="Shield_Frame_" + f["id"], dnp=True, variants=kv)
    mapping = {"1": "GND"}
    s.connect_all(pl, mapping)
    bx0, by0, bx1, by1 = unit_box(sym, 1)
    l_, r_, t_, b_ = unit_extent(sym, 1, mapping)
    box = (snap(x + bx0 - l_), snap(y + by0 - t_), snap(x + bx1 + r_), snap_up(y + by1 + b_))
    for tx0, ty, tx1, _ in getattr(pl, "texts", []):
        box = (min(box[0], snap(tx0 - 1.27)), min(box[1], snap(ty - 2.54)), max(box[2], snap_up(tx1 + 1.27)),
               max(box[3], snap_up(ty + 1.27)))
    return box


def _n(v):
    return ("%.2f" % v).rstrip("0").rstrip(".")


def draw(s, variants):
    frames = shields.frames()
    f = Flow(s)
    grp(f, lambda: _frames(s, frames, variants))
    d = frames[0]
    s.iface_rows = [["GND", "Ground", "Each frame land is one ground pad ring (pad 1)"]]
    s.rail_rows = [["(none)", "-", "No supply on this sheet"]]
    corner_notes(s, [
        "1. Function: shield-can frames on the back (PCB-T-06, PCB-EMC-03), one per frame of",
        "   shields.toml: " + "; ".join(fr["title"] for fr in frames) + ".",
        "2. Absent state: dnp in both variants: fitted only if EMC or audio measurements require",
        "   (BOM v1 line 90); the lands and keep-outs stay on the board either way.",
        "3. Two-piece, etched to the board's outline (amended T1-038): frame soldered, lid clipped.",
        "   Height with lid %s mm (PCB-Z-01, the back pocket); lid %s mm and %s mm clearance leave"
        % (_n(d["height"]), _n(d["lid"]), _n(d["clearance"])),
        "   %s mm for the parts inside. None on the front (PCB-Z-03)." % _n(d["max_h"]),
        "4. Geometry: hardware/t1-main-board/shields.toml: land %s mm, keep-out %s mm outside"
        % (_n(d["land"]), _n(d["keepout"])),
        "   (PCB-T-06) and %s mm inside; lid, clearance, land and the inner keep-out UNVERIFIED" % _n(d["keepout_in"]),
        "   until the maker's drawing.",
    ])
