"""Footprint geometry from the libraries, read with pcbnew (KiCad's Python).

For each footprint used by the netlist: the courtyard bounding box, the pad bounding box and
whether any pad is a through hole, in the footprint's own frame (front side, rotation 0, mm, KiCad
y down). The placement (pure Python) works on these boxes; `geometry_cache()` writes them to a
JSON file so the tests and the occupancy report can run without pcbnew.
"""

from __future__ import annotations

import json
import os

import pcbnew

import libtable


def _bbox(items):
    xs, ys = [], []
    for b in items:
        xs += [pcbnew.ToMM(b.GetLeft()), pcbnew.ToMM(b.GetRight())]
        ys += [pcbnew.ToMM(b.GetTop()), pcbnew.ToMM(b.GetBottom())]
    if not xs:
        return None
    return [min(xs), min(ys), max(xs), max(ys)]


def measure(fp) -> dict:
    """Geometry of a footprint placed at the origin, rotation 0, front side."""
    fp.SetPosition(pcbnew.VECTOR2I(0, 0))
    fp.SetOrientationDegrees(0)
    cy = fp.GetCourtyard(pcbnew.F_CrtYd)
    court = None
    if cy.OutlineCount():
        court = _bbox([cy.BBox()])
    pads = _bbox([p.GetBoundingBox() for p in fp.Pads()])
    if court is None:          # no courtyard drawn: pads grown by 0.25 mm (IPC-7351 nominal excess)
        court = [pads[0] - 0.25, pads[1] - 0.25, pads[2] + 0.25, pads[3] + 0.25] if pads else [-0.5, -0.5, 0.5, 0.5]
    # through holes reach the other side: every plated or unplated hole (connector pins, shell
    # stakes, pegs, and the thermal vias of exposed pads), as its pad's box grown by PCB-V-01's
    # 0.13 mm
    holes = []
    pad_pos = {}
    for p in fp.Pads():
        num = p.GetNumber()
        if num and num not in pad_pos:
            pad_pos[num] = [round(pcbnew.ToMM(p.GetPosition().x), 4), round(pcbnew.ToMM(p.GetPosition().y), 4)]
        if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
            b = _bbox([p.GetBoundingBox()])
            holes.append([round(b[0] - 0.13, 4), round(b[1] - 0.13, 4), round(b[2] + 0.13, 4), round(b[3] + 0.13, 4)])
    models = [{"file": m.m_Filename, "offset_z": m.m_Offset.z, "scale_z": m.m_Scale.z,
               "rot_x": m.m_Rotation.x, "rot_y": m.m_Rotation.y} for m in fp.Models() if m.m_Show]
    return {"courtyard": [round(v, 4) for v in court], "pads": [round(v, 4) for v in pads] if pads else None,
            "holes": holes, "pad_pos": pad_pos, "pad_count": len(fp.Pads()), "models": models}


def load(libs: dict, fpid: str):
    lib, name = fpid.split(":", 1)
    path = libs.get(lib)
    if path is None or not os.path.exists(os.path.join(path, name + ".kicad_mod")):
        return None
    fp = pcbnew.FootprintLoad(path, name)
    if fp is not None:
        fp.SetFPIDAsString(fpid)
    return fp


def geometry_cache(fpids, out_path: str) -> dict:
    libs = libtable.read()
    res = {}
    for fpid in sorted(set(fpids)):
        fp = load(libs, fpid)
        res[fpid] = measure(fp) if fp is not None else None
    with open(out_path, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
        fh.write("\n")
    return res


def main():
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import netlist
    nl = netlist.load(sys.argv[1])
    geometry_cache([c.footprint for c in nl.components.values()] + sys.argv[3:], sys.argv[2])


if __name__ == "__main__":
    main()
