"""Write the T1 main board's .kicad_pcb from a board spec (run with KiCad's Python).

    $KICAD_PY kicad_write.py <spec.json> <out.kicad_pcb>

The spec (written by build.py) holds everything decided: outline, holes, rule areas, drawings,
texts, the title block and every footprint with its library id, position, rotation, side, fields,
schematic path and pad nets. This script only turns it into KiCad objects; pcbnew's Python cannot
reach the board stackup, so the stackup block is written into the saved file's setup section
(`insert_stackup`) and checked by reading the board back.
"""

import json
import os
import re
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import libtable  # noqa: E402

OX, OY = 100.0, 100.0


def mm(v):
    return int(round(v * 1e6))


def P(x, y):
    return pcbnew.VECTOR2I(mm(OX + x), mm(OY - y))


def lid(board, name):
    """Layer id from a canonical name (KiCad 10 resolves "B.Silkscreen", not "B.SilkS")."""
    i = board.GetLayerID(name)
    if i < 0:
        i = getattr(pcbnew, name.replace(".", "_"))
    return i


def layer_set(board, names):
    ls = pcbnew.LSET()
    for n in names:
        ls.AddLayer(lid(board, n))
    return ls


def rect_shape(board, r, layer, width):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_RECT)
    s.SetStart(P(r[0], r[3]))
    s.SetEnd(P(r[2], r[1]))
    s.SetLayer(lid(board, layer))
    s.SetWidth(mm(width))
    board.Add(s)


def text(board, t):
    tx = pcbnew.PCB_TEXT(board)
    tx.SetText(t["text"])
    tx.SetPosition(P(t["x"], t["y"]))
    tx.SetLayer(lid(board, t["layer"]))
    tx.SetTextSize(pcbnew.VECTOR2I(mm(t["size"]), mm(t["size"])))
    tx.SetTextThickness(mm(t.get("stroke", 0.15)))
    if t["layer"].startswith("B."):
        tx.SetMirrored(True)
    if t.get("left"):
        tx.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    board.Add(tx)


def rule_area(board, a):
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetZoneName(a["name"])
    z.SetLayerSet(layer_set(board, a["layers"]))
    z.SetDoNotAllowTracks(a.get("no_tracks", False))
    z.SetDoNotAllowVias(a.get("no_vias", False))
    z.SetDoNotAllowPads(a.get("no_pads", False))
    z.SetDoNotAllowFootprints(a.get("no_footprints", False))
    z.SetDoNotAllowZoneFills(a.get("no_fills", False))
    o = z.Outline()
    o.NewOutline()
    x0, y0, x1, y1 = a["rect"]
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        o.Append(P(x, y))
    board.Add(z)


def net(board, name, cache):
    if name not in cache:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        cache[name] = n
    return cache[name]


def placeholder(board, f):
    """A courtyard-only footprint for a part whose land is not drawn yet."""
    fp = pcbnew.FOOTPRINT(board)
    x0, y0, x1, y1 = f["placeholder"]["courtyard"]
    for layer, w in (("F.CrtYd", 0.05), ("F.Fab", 0.1)):
        s = pcbnew.PCB_SHAPE(fp)
        s.SetShape(pcbnew.SHAPE_T_RECT)
        s.SetStart(pcbnew.VECTOR2I(mm(x0), mm(y0)))
        s.SetEnd(pcbnew.VECTOR2I(mm(x1), mm(y1)))
        s.SetLayer(lid(board, layer))
        s.SetWidth(mm(w))
        fp.Add(s)
    fp.SetAttributes(pcbnew.FP_SMD)
    return fp


def footprint(board, libs, f, nets):
    if f.get("placeholder"):
        fp = placeholder(board, f)
    else:
        lib, name = f["fpid"].split(":", 1)
        fp = pcbnew.FootprintLoad(libs[lib], name)
    fp.SetFPIDAsString(f["fpid"])
    fp.SetReference(f["ref"])
    fp.SetValue(f.get("value", ""))
    board.Add(fp)
    fp.SetPosition(P(f["x"], f["y"]))
    if f["side"] == "B":
        fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    fp.SetOrientationDegrees(f["rot"])
    for k, v in sorted(f.get("fields", {}).items()):
        if k in ("Reference", "Value", "Footprint"):
            continue
        fp.SetField(k, v)
        fp.GetField(k).SetVisible(False)
    # reference designators stay on the fabrication layer (${REFERENCE}); the silk legend is placed
    # at a later stage (CRAFT-10, Q2)
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    if f.get("path"):
        fp.SetPath(pcbnew.KIID_PATH(f["path"]))
    if f.get("sheetname"):
        fp.SetSheetname(f["sheetname"])
    if f.get("sheetfile"):
        fp.SetSheetfile(f["sheetfile"])
    attrs = fp.GetAttributes()
    if f.get("dnp"):
        attrs |= pcbnew.FP_DNP
    if f.get("exclude_bom"):
        attrs |= pcbnew.FP_EXCLUDE_FROM_BOM
    if f.get("board_only"):
        attrs |= pcbnew.FP_BOARD_ONLY
    fp.SetAttributes(attrs)
    pins = f.get("pins", {})
    for pd in fp.Pads():
        n = pins.get(pd.GetNumber())
        if n:
            pd.SetNet(net(board, n, nets))
    return fp


def hole(board, h):
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(h["ref"])
    fp.SetValue("MountingHole_%.1fmm" % h["d"])
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    fp.SetPosition(P(h["x"], h["y"]))
    fp.SetAttributes(pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_BOARD_ONLY)
    pad = pcbnew.PAD(fp)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
    pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    pad.SetSize(pcbnew.VECTOR2I(mm(h["d"]), mm(h["d"])))
    pad.SetDrillSize(pcbnew.VECTOR2I(mm(h["d"]), mm(h["d"])))
    pad.SetLayerSet(pad.UnplatedHoleMask())
    pad.SetPosition(P(h["x"], h["y"]))
    fp.Add(pad)
    board.Add(fp)


def stackup_block(st):
    """KiCad's (stackup ...) s-expression from the spec's layer list."""
    out = ["\t\t(stackup"]
    for L in st["layers"]:
        parts = ['(layer "%s"' % L["name"], '(type "%s")' % L["type"]]
        if "thickness" in L:
            parts.append("(thickness %s)" % _num(L["thickness"]))
        if "material" in L:
            parts.append('(material "%s")' % L["material"])
        if "epsilon_r" in L:
            parts.append("(epsilon_r %s)" % _num(L["epsilon_r"]))
            parts.append("(loss_tangent 0)")
        out.append("\t\t\t" + " ".join(parts) + ")")
    out.append('\t\t\t(copper_finish "%s")' % st["finish"])
    out.append("\t\t\t(dielectric_constraints no)")
    out.append("\t\t)")
    return "\n".join(out)


def _num(v):
    return ("%.4f" % v).rstrip("0").rstrip(".")


def insert_stackup(path, st):
    with open(path, encoding="utf-8") as fh:
        text_ = fh.read()
    text_ = re.sub(r"\n\t\t\(stackup\n.*?\n\t\t\)\n", "\n", text_, flags=re.S)
    m = re.search(r"\n\t\(setup\n", text_)
    if not m:
        raise SystemExit("no setup section in " + path)
    text_ = text_[:m.end()] + stackup_block(st) + "\n" + text_[m.end():]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text_)


def main():
    spec_path, out = sys.argv[1], sys.argv[2]
    with open(spec_path) as fh:
        spec = json.load(fh)
    pcbnew.KIID.SeedGenerator(spec.get("seed", 1))
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(spec["copper_layers"])
    ds = board.GetDesignSettings()
    ds.SetBoardThickness(mm(spec["stackup"]["thickness"]))
    tb = board.GetTitleBlock()
    for k, v in spec["title_block"].items():
        if k.startswith("comment"):
            tb.SetComment(int(k[7:]) - 1, v)
        else:
            getattr(tb, "Set" + k.capitalize())(v)
    rect_shape(board, spec["outline"], "Edge.Cuts", 0.05)
    for d in spec["drawings"]:
        rect_shape(board, d["rect"], d["layer"], d.get("width", 0.1))
    for t in spec["texts"]:
        text(board, t)
    for a in spec["rule_areas"]:
        rule_area(board, a)
    libs = libtable.read()
    nets = {}
    for f in spec["footprints"]:
        footprint(board, libs, f, nets)
    for h in spec["holes"]:
        hole(board, h)
    board.SetModified()
    pcbnew.SaveBoard(out, board)
    insert_stackup(out, spec["stackup"])
    # read back: the stackup parses and the footprint count holds
    b2 = pcbnew.LoadBoard(out)
    n = len(b2.GetFootprints())
    th = pcbnew.ToMM(b2.GetDesignSettings().GetBoardThickness())
    print("wrote %s: %d footprints, %d nets, %.3f mm" % (out, n, b2.GetNetCount(), th))


if __name__ == "__main__":
    main()
