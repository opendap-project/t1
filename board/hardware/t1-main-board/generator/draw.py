"""Drawing helpers shared by the block sheets: IC units wired to nets, decoupling groups, pulls,
series parts, measurement links, rail tables and notes."""

from __future__ import annotations

import os

import library
from parts import PARTS, fields
from sch import G, RAILS, snap, snap_down, snap_up

CHAR = 1.16          # mm per character of 1.27 mm stroke text (upper case, measured on plots)


def label_len(net):
    return 0 if net is None or net in RAILS else len(net) * CHAR + 2.54


def unit_extent(sym, unit, nets):
    """Space a unit needs around its body: (left, right, top, bottom) beyond the pin ends, mm:
    stub, then a label (its text) or a power symbol (its value)."""
    from sch import field_side
    left = right = 0.0
    top = bottom = 0.0
    n_top = sum(1 for p in sym.unit_pins(unit) if p.side() == "top")
    for p in sym.unit_pins(unit):
        net = nets.get(p.number)
        if net is None or net in ("__missing__", ""):
            continue
        s = p.side()
        text = len(net) * CHAR
        if s in ("left", "right"):
            need = 2.54 + (2.54 + text if net in RAILS and net != "GND" else (5.08 if net == "GND" else 1.27 + text))
            if s == "left":
                left = max(left, need)
            else:
                right = max(right, need)
        elif s == "top":
            if net in RAILS and net != "GND":
                # a run of the rail on that edge takes a collector and a 2.54 mm riser first; then
                # the symbol and its value (upright when the edge is crowded)
                run = sum(1 for q in sym.unit_pins(unit) if q.side() == "top" and nets.get(q.number) == net) > 1
                need = (5.08 if run else 2.54) + 3.81 + (text + (1.27 if run else 0.0) if n_top > 1 else 1.27)
            else:
                need = 2.54 + 1.27 + text
            top = max(top, need)
        else:
            need = 2.54 + (6.35 if net in RAILS else 1.27 + text)
            bottom = max(bottom, need)
    side = field_side(sym, unit)      # reference and value: two lines of text on that side
    if side == "left":
        left = max(left, (len(sym.name) + 4) * CHAR + 2.54)
    elif side == "right":
        right = max(right, (len(sym.name) + 4) * CHAR + 2.54)
    elif side == "top":
        top = max(top, 7.62)
    elif side == "bottom":
        bottom = max(bottom, 7.62)
    return left, right, top, bottom


def unit_box(sym, unit):
    """Pin-end bounding box of a unit in schematic offsets from its origin: (x0, y0, x1, y1)."""
    pins = sym.unit_pins(unit)
    bx0, by0, bx1, by1 = sym.body(unit)
    xs = [p.x for p in pins] + [bx0, bx1]
    ys = [-p.y for p in pins] + [-by0, -by1]
    return min(xs), min(ys), max(xs), max(ys)


def place_unit(sheet, sym, ref, unit, x, y, nets, flds, value=None, collect=True):
    """Place a unit with its origin at (x, y) and wire every pin to its net (None: no-connect)."""
    pl = sheet.place(sym, ref, x, y, unit=unit, fields=flds, value=value)
    mapping = {p.number: nets.get(p.number, "__missing__") for p in sym.unit_pins(unit)}
    missing = [k for k, v in mapping.items() if v == "__missing__"]
    if missing:
        raise SystemExit(f"generator: {ref} unit {unit}: pins without a net: {missing[:8]}")
    sheet.connect_all(pl, mapping, collect=collect)
    return pl


def put_unit(sheet, sym, ref, unit, x_left, y_top, nets, flds, value=None):
    """Place a unit so that its labels start at x_left and its top symbols at y_top.
    Returns (x_right, y_bottom) of the space it takes, labels and symbols included."""
    bx0, by0, bx1, by1 = unit_box(sym, unit)
    left, right, top, bottom = unit_extent(sym, unit, nets)
    ox = snap(x_left + left - bx0)
    oy = snap(y_top + top - by0)
    place_unit(sheet, sym, ref, unit, ox, oy, nets, flds, value=value)
    return ox + bx1 + right, oy + by1 + bottom


def flow_units(sheet, sym, ref, units, nets, flds, x0, y0, x_max, value=None, gap=7.62):
    """Place units left to right from (x0, y0), wrapping to a new row at x_max. Returns the bottom y."""
    x, y, row_h = x0, y0, 0.0
    for u in units:
        bx0, by0, bx1, by1 = unit_box(sym, u)
        left, right, top, bottom = unit_extent(sym, u, nets)
        w = (bx1 - bx0) + left + right
        if x + w > x_max and x > x0:
            x, y, row_h = x0, y + row_h + gap, 0.0
        ox = snap(x + left - bx0)
        oy = snap(y + top - by0)
        place_unit(sheet, sym, ref, u, ox, oy, nets, flds, value=value)
        h = (by1 - by0) + top + bottom
        # each unit's footprint with its labels: a sheet below may start a group under a short unit
        sheet.unit_boxes = getattr(sheet, "unit_boxes", []) + [(x, y, x + w, y + h)]
        x += w + gap
        row_h = max(row_h, (by1 - by0) + top + bottom)
    return y + row_h


def decouple(sheet, rail, keys, x, y, block, refs_out=None, pitch=10.16):
    """A decoupling group: the rail as a power symbol on a horizontal wire, capacitors hanging from
    it in placement order (smallest first, nearest the pins), each to its own ground symbol.
    (x, y) is the rail symbol's pin. Returns the x after the group."""
    csym = library.load("Device", "C")
    x, y = snap(x), snap(y)
    # wide enough for the reference, value and spec to the right of each capacitor
    longest = max(max(len(PARTS[k]["value"]), len(PARTS[k].get("spec") or ""), 5) for k in keys)
    # text from 2.54 mm right of the axis, 0.5 mm clear of the next capacitor's plate (2.032 mm)
    pitch = max(pitch, -(-(longest * CHAR + 5.08) // 2.54) * 2.54)
    xs = [snap(x + 5.08 + i * pitch) for i in range(len(keys))]
    sheet.attach(rail, x, y, "up")
    sheet.project.rails_used.add(rail)
    sheet.wire((x, y), (xs[-1], y))
    for i, (cx, key) in enumerate(zip(xs, keys)):
        p = PARTS[key]
        ref = sheet.next_ref("C")
        cy = y + 6.35
        sheet.wire((cx, y), (cx, cy - 3.81))
        if i < len(xs) - 1:
            sheet.junction(cx, y)
        shown = {"Spec": p["spec"]} if p.get("spec") else None
        sheet.place(csym, ref, cx, cy, fields=fields(key, block), shown=shown, value=p["value"],
                    ref_at=(cx + text_dx("C"), cy - 1.27), val_at=(cx + text_dx("C"), cy + 1.27))
        sheet.wire((cx, cy + 3.81), (cx, cy + 6.35))
        sheet.power("GND", cx, cy + 6.35)
        if refs_out is not None:
            refs_out.append((ref, p["value"]))
    sheet.last_pitch = pitch
    return xs[-1] + pitch


KIND_SYMBOL = {"R": "R", "C": "C", "L": "L", "F": "Fuse", "RT": "Thermistor_NTC"}
KIND_LIB = {"RT": "OpenDAP_Device"}            # stock Device:Thermistor_NTC carries TH (CRAFT-130)


def text_dx(kind):
    """Offset of a vertical two-pin part's text from its axis: clear of the capacitor plates
    (+-2.032 mm) and the thermistor's slanted line (1.778 mm), else 1.27 mm (CRAFT-175)."""
    return 2.54 if kind in ("C", "RT") else 1.27


def kind_symbol(kind):
    return library.load(KIND_LIB.get(kind, "Device"), KIND_SYMBOL.get(kind, "R"))


def two_pin_h(sheet, key, x, y, net_l, net_r, block, extra=None, dnp=False, variants=None, ref=None, stub=2.54,
              prefix=None, above=False):
    """A horizontal two-pin part (resistor, link, net tie) with pin 1 on the left."""
    p = PARTS[key]
    sym = library.load("Device", "NetTie_2") if p["kind"] == "NT" else kind_symbol(p["kind"])
    ref = ref or sheet.next_ref(prefix or p["kind"])
    shown = {"Spec": p["spec"]} if p.get("spec") else None
    f = fields(key, sheet.block)
    f.update(extra or {})
    if p["kind"] == "NT":
        # above: both fields over the tie, so a flag can hang below its stub
        pl = sheet.place(sym, ref, x, y, angle=0, fields=f, value=p["value"], in_bom=False,
                         ref_at=(x - 2.54, y - 6.35 if above else y - 2.54),
                         val_at=(x - 2.54, y - 3.81 if above else y + 3.81))
        for key_, net in (("1", net_l), ("2", net_r)):
            sheet.connect(pl, key_, net, stub)
        return ref
    off = 3.81 if p["kind"] == "C" else 2.54        # a capacitor's plates reach 2.03 mm above and below
    pl = sheet.place(sym, ref, x, y, angle=90, fields=f, shown=shown, value=p["value"], dnp=dnp,
                     variants=variants, ref_at=(x, y - off), val_at=(x, y + off))
    for key_, net in (("1", net_l), ("2", net_r)):
        sheet.connect(pl, key_, net, stub)
    sheet.last = pl
    return ref


def two_pin_v(sheet, key, x, y, net_top, net_bottom, block, extra=None, dnp=False, variants=None, stub=2.54):
    """A vertical two-pin part with pin 1 at the top."""
    p = PARTS[key]
    sym = kind_symbol(p["kind"])
    ref = sheet.next_ref(p["kind"])
    shown = {"Spec": p["spec"]} if p.get("spec") else None
    f = fields(key, sheet.block)
    f.update(extra or {})
    pl = sheet.place(sym, ref, x, y, fields=f, shown=shown, value=p["value"], dnp=dnp, variants=variants,
                     ref_at=(x + text_dx(p["kind"]), y - 1.27), val_at=(x + text_dx(p["kind"]), y + 1.27))
    for key_, net in (("1", net_top), ("2", net_bottom)):
        sheet.connect(pl, key_, net, stub)
    sheet.last = pl
    return ref


def link(sheet, key, x, y, net_src, net_load, variants, tp_names=None, flag=True, title=None):
    """A measurement link (BOM line 137) with its two Kelvin test pads (BOM line 86), in its own
    titled group. The rail on the load side leaves the group to the right; a rail fed through the
    link takes its PWR_FLAG there, on a branch outside the group (CRAFT-85, -174)."""
    p = PARTS[key]
    rsym = library.load("Device", "R")
    tsym = library.load("Connector", "TestPoint")
    ref = sheet.next_ref("R")
    f = fields(key, sheet.block)
    f["Constraints"] = "PCB-T-02"
    pl = sheet.place(rsym, ref, x, y, angle=90, fields=f, shown={"Spec": p["spec"]}, value=p["value"],
                     variants=variants, ref_at=(x - 2.54, y - 3.81), val_at=(x - 2.54, y + 2.54))
    labels = tp_names or (net_src or "Kelvin", net_load or "Kelvin")
    p1, p2 = pl.pos(pl.pin("1")), pl.pos(pl.pin("2"))
    bx0 = snap(min(p1[0] - 7.62, p1[0] - 2.54 - 1.27 - len(labels[0]) * CHAR) - 2.54)
    bx1 = snap(max(p2[0] + 7.62, p2[0] + 2.54 + 1.27 + len(labels[1]) * CHAR) + 2.54)
    if title:
        bx1 = max(bx1, snap(bx0 + len(title) * 2.3 + 2.54))
        sheet.group_box(title, bx0, y - 12.7, bx1 - bx0, 20.32)
    sheet.last_box = (bx0 - 2.54 - net_text(net_src) if net_src else bx0, y - 15.24,
                      bx1 + 12.7 + net_text(net_load), y + 10.16)
    ends = []
    for key_, net, sgn in (("1", net_src, -1), ("2", net_load, 1)):
        pin = pl.pin(key_)
        px, py = pl.pos(pin)
        ex = px + sgn * 7.62
        if title and (sgn > 0 or net is not None):
            ex = bx0 - 2.54 if sgn < 0 else bx1 + 12.7
        sheet.wire((px, py), (ex, py))
        tx = px + sgn * 2.54
        sheet.junction(tx, py)
        sheet.wire((tx, py), (tx, py - 2.54))
        tref = sheet.next_ref("TP")
        label = labels[0 if sgn < 0 else 1]
        sheet.place(tsym, tref, tx, py - 2.54, fields=fields("TP", sheet.block), value=label,
                    in_bom=False, ref_at=(tx - 1.27, py - 7.62) if sgn < 0 else (tx + 1.27, py - 7.62),
                    val_at=(tx - 1.27, py - 5.08) if sgn < 0 else (tx + 1.27, py - 5.08))
        if sgn < 0:
            _justify_right(sheet)
        if net is not None:
            sheet.attach(net, ex, py, "left" if sgn < 0 else "right", "pas")
        if flag and sgn > 0 and net is not None:
            # rail or local net: the flag hangs from the load-side wire, outside the group (CRAFT-85)
            if title:
                sheet.flag_at(bx1 + 7.62, py, "down", 2.54)   # its text clear of the outline
            elif net in RAILS:
                sheet.flag_net(net, ex, py)
            else:
                sheet.flag_at(px + 5.08, py, "down", 2.54)    # between the Kelvin pad and the label
        ends.append((ex, py))
    return ref, ends


def link_variants(key, variant_files):
    """KiCad variant overrides for a measurement link, from the variant files' instrumentation."""
    p = PARTS[key]
    out = {}
    for name, v in variant_files.items():
        if v.get("instrumentation", {}).get("links") == "zero-ohm" and p.get("production"):
            out[name] = {"fields": dict(p["production"])}
    return out


def rail_table(sheet, x, y, rows, w=(30.48, 50.8, 99.06)):
    return sheet.table(x, y, list(w), [["Rail", "Capacitors", "Requirement and source"]] + rows, "rails",
                       title="Rails")


def iface_table(sheet, x, y, rows, w=(38.1, 22.86, 119.38)):
    return sheet.table(x, y, list(w), [["Net", "Direction", "Absent state (block not fitted)"]] + rows, "iface",
                       title="Interface")


def notes(sheet, lines, x, y, w):
    text = "Notes\n" + "\n".join(lines)
    return sheet.text_box(text, x, y, w)


TB = (130.0, 32.0)   # title block of the OpenDAP drawing sheet
MARGIN = 14.0        # page margin 10 mm plus the 4 mm zone band of the frame


def frame(sheet):
    return (420.0, 297.0) if sheet.paper == "A3" else (297.0, 210.0)


def tb_box(sheet):
    """The title block's (x0, y0, x1, y1) on the page."""
    W, H = frame(sheet)
    return W - MARGIN - TB[0], H - MARGIN - TB[1], W - MARGIN, H - MARGIN


def corner_notes(sheet, lines, w=None, y=None, right=None):
    """The Notes text box, right-aligned above the title block (template layout); a sheet whose
    bottom row needs that corner passes the top y of a free band instead."""
    x0, y0, x1, _ = tb_box(sheet)
    text = "Notes\n" + "\n".join(lines)
    h = G * -(-(len(text.split("\n")) * 2.03 + 3.81) // G)    # stroke text pitch 1.6 x 1.27 mm
    w = w or (x1 - x0)
    x = snap_down((x1 if right is None else right) - w)    # never past the right edge
    y = snap(y0 - h - 2.54) if y is None else snap(y)
    sheet.text_box(text, x, y, snap(w), h)
    sheet.notes_top = y
    return y


def finalize_tables(sheet):
    """Interface and rail tables at the lower left, left of the title block (CRAFT-170, -172).
    On A3 they sit side by side, bottom-aligned; on A4 the rail table under the interface table."""
    from sch import row_height
    W, H = frame(sheet)
    x = 22.86
    tx0 = tb_box(sheet)[0]
    width = snap(tx0 - x - 7.62)
    bottom = H - MARGIN - 2.54
    rails = getattr(sheet, "rail_rows", None)
    iface = getattr(sheet, "iface_rows", None)
    rh = ["Rail", "Capacitors", "Requirement and source"]
    ih = ["Net", "Direction", "Absent state (block not fitted)"]
    at = getattr(sheet, "tables_at", None)       # (x, y_top, width): a sheet that keeps its tables elsewhere
    if at:
        tx, ty, tw = at
        if rails:
            rw = [27.94, snap(tw * 0.3), tw - 27.94 - snap(tw * 0.3)]
            ty = ty + 5.08 + sheet.table(tx, ty + 5.08, rw, [rh] + rails, "rails", title="Rails") + 7.62
        if iface:
            iw = [38.1, 22.86, tw - 60.96]
            sheet.table(tx, ty + 5.08, iw, [ih] + iface, "iface", title="Interface")
        sheet.tables_top = H - MARGIN
        return
    if sheet.paper == "A3" and rails and iface:
        wi = snap(width * 0.48)
        wr = snap(width - wi - 7.62)
        iw = [38.1, 22.86, wi - 60.96]
        rw = [27.94, snap(wr * 0.3), wr - 27.94 - snap(wr * 0.3)]
        hi = sum(row_height(r, iw) for r in [ih] + iface)
        hr = sum(row_height(r, rw) for r in [rh] + rails)
        top = snap(bottom - max(hi, hr))
        sheet.table(x, top, iw, [ih] + iface, "iface", title="Interface")
        sheet.table(x + wi + 7.62, top, rw, [rh] + rails, "rails", title="Rails")
        sheet.tables_top = top - 5.08
        return
    y = bottom
    if rails:
        rw = [27.94, snap(width * 0.32), width - 27.94 - snap(width * 0.32)]
        y = snap(y - sum(row_height(r, rw) for r in [rh] + rails))
        sheet.table(x, y, rw, [rh] + rails, "rails", title="Rails")
        y -= 7.62
    if iface:
        iw = [45.72, 25.4, width - 71.12]
        y = snap(y - sum(row_height(r, iw) for r in [ih] + iface))
        sheet.table(x, y, iw, [ih] + iface, "iface", title="Interface")
    sheet.tables_top = y - 5.08


# ---------------------------------------------------------------------- hand wiring

def vpart(sheet, key, x, y, **kw):
    """A vertical two-pin part (pin 1 at the top), not wired: returns its pin ends (top, bottom)."""
    p = PARTS[key]
    sym = kind_symbol(p["kind"])
    ref = kw.pop("ref", None) or sheet.next_ref(p["kind"])
    f = fields(key, sheet.block)
    f.update(kw.pop("extra", None) or {})
    shown = {"Spec": p["spec"]} if p.get("spec") else None
    side = kw.pop("text", "right")
    tx = x + text_dx(p["kind"]) if side == "right" else x - text_dx(p["kind"])
    if p.get("in_bom") is False:
        kw.setdefault("in_bom", False)
    pl = sheet.place(sym, ref, x, y, fields=f, shown=shown, value=p["value"],
                     ref_at=(tx, y - 1.27), val_at=(tx, y + 1.27), **kw)
    if side == "left":
        _justify_right(sheet)
    sheet.last = pl
    return pl.pos(pl.pin("1")), pl.pos(pl.pin("2"))


def hpart(sheet, key, x, y, **kw):
    """A horizontal two-pin part (pin 1 at the left), not wired: returns its pin ends (left, right)."""
    p = PARTS[key]
    sym = kind_symbol(p["kind"])
    ref = kw.pop("ref", None) or sheet.next_ref(kw.pop("prefix", None) or p["kind"])
    f = fields(key, sheet.block)
    f.update(kw.pop("extra", None) or {})
    shown = {"Spec": p["spec"]} if p.get("spec") else None
    above = kw.pop("text", "above") == "above"
    if above:   # reference, value and spec stacked above the part, clear of wires below it
        ref_at, val_at = (x, y - 7.62 if shown else y - 5.08), (x, y - 5.08 if shown else y - 2.54)
    else:
        ref_at, val_at = (x, y + 2.54), (x, y + 5.08)
    pl = sheet.place(sym, ref, x, y, angle=90, fields=f, shown=shown, value=p["value"],
                     ref_at=ref_at, val_at=val_at, **kw)
    sheet.last = pl
    return pl.pos(pl.pin("1")), pl.pos(pl.pin("2"))


def _justify_right(sheet):
    it = sheet.items[-1]
    sheet.items[-1] = it.replace("(justify left)", "(justify right)")


def gnd(sheet, x, y):
    sheet.power("GND", x, y)


def tp(sheet, x, y, net_label=None, text="right"):
    """A test pad whose pin is at (x, y) (BOM v1 line 86); value = the net it probes."""
    tsym = library.load("Connector", "TestPoint")
    ref = sheet.next_ref("TP")
    tx = x + 1.27 if text == "right" else x - 1.27
    sheet.place(tsym, ref, x, y, fields=fields("TP", sheet.block), value=net_label or "TP", in_bom=False,
                ref_at=(tx, y - 5.08), val_at=(tx, y - 2.54))
    if text == "left":
        _justify_right(sheet)
    return ref


def _on_wire(sheet, x, y):
    """(x, y) lies on one of the sheet's wires."""
    import re
    for it in sheet.items:
        m = re.match(r"\(wire \(pts \(xy (\S+) (\S+)\) \(xy (\S+) (\S+)\)\)", it)
        if m:
            x0, y0, x1, y1 = map(float, m.groups())
            if min(x0, x1) - 1e-3 <= x <= max(x0, x1) + 1e-3 and min(y0, y1) - 1e-3 <= y <= max(y0, y1) + 1e-3 \
                    and (abs(x0 - x1) < 1e-3 or abs(y0 - y1) < 1e-3):
                return True
    return False


def local_flags(sheet):
    """PWR_FLAGs deferred by Sheet.flag_net(since=, side=): each on a branch from the middle of the
    stub that leaves the feeding part towards the net's label, once the groups are in place. A
    horizontal stub takes the flag below it; a vertical one, on a branch to the right (the label's
    text reads on the left of a vertical wire)."""
    for s, net, since, side in sheet.project.flag_points:
        if s is not sheet:
            continue
        p = next((p for p in sheet.points[since:] if p.net == net and p.direction == side), None)
        if p is None:
            raise SystemExit(f"generator: {sheet.name}: no {side} label of {net} to hang its PWR_FLAG from")
        dx, dy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[side]
        mx, my = p.x - dx * 1.27, p.y - dy * 1.27
        if not _on_wire(sheet, mx, my):      # the label sits on the pin end itself: branch there
            mx, my = p.x, p.y
        if dy:
            sheet.flag_at(mx, my, "right", 5.08)
        else:
            sheet.flag_at(mx, my, "down", 2.54)


# ---------------------------------------------------------------------- label-wired circuits

def ic(sheet, lib, name, x, y, pins, extra=None, value=None, stub=2.54, collect=True, prefix="U"):
    """Place a one-unit IC and wire every pin: `pins` maps pin numbers or (unique) names to nets
    (None: no-connect flag). Every pin must be listed. Returns the placed symbol."""
    sym = library.load(lib, name)
    ref = sheet.next_ref(prefix)
    f = {"Block": sheet.block}
    f.update(extra or {})
    pl = sheet.place(sym, ref, x, y, fields=f, value=value)
    mapping = {}
    for key, net in pins.items():
        nums = [p.number for p in sym.unit_pins(1) if p.number == key] or \
               [p.number for p in sym.unit_pins(1) if p.name == key]
        if not nums:
            raise SystemExit(f"generator: {name}: no pin {key!r}")
        for nmb in nums:
            mapping[nmb] = net
    missing = [p.number for p in sym.unit_pins(1) if p.number not in mapping]
    if missing:
        raise SystemExit(f"generator: {ref} {name}: pins without a net: {missing}")
    sheet.connect_all(pl, mapping, stub=stub, collect=collect)
    bx0, by0, bx1, by1 = unit_box(sym, 1)
    l_, r_, t_, b_ = unit_extent(sym, 1, mapping)
    reach = getattr(pl, "reach", {})        # a rail moved out past its neighbours' labels
    l_, r_ = max(l_, reach.get(-1, 0.0)), max(r_, reach.get(1, 0.0))
    pl.bbox = (snap(x + bx0 - l_), snap(y + by0 - t_), snap(x + bx1 + r_), snap(y + by1 + b_))
    for tx0, ty, tx1, _ in getattr(pl, "texts", []):     # the reference and value beyond the body
        pl.bbox = (min(pl.bbox[0], snap_down(tx0)), min(pl.bbox[1], snap_down(ty - 1.27)),
                   max(pl.bbox[2], snap_up(tx1 + 1.27)), max(pl.bbox[3], snap_up(ty + 1.27)))
    return pl


def part(sheet, lib, name, x, y, pins, key=None, angle=0, value=None, extra=None, prefix=None, dnp=False,
         ref_at=None, val_at=None, stub=2.54, in_bom=True):
    """A discrete from a library symbol (FET, diode, TVS) with fields from parts.PARTS[key]."""
    sym = library.load(lib, name)
    p = PARTS[key] if key else {}
    ref = sheet.next_ref(prefix or p.get("kind", "U"))
    f = fields(key, sheet.block) if key else {"Block": sheet.block}
    f.update(extra or {})
    shown = {"Spec": p["spec"]} if p.get("spec") else None
    pl = sheet.place(sym, ref, x, y, angle=angle, fields=f, shown=shown, value=value or p.get("value"), dnp=dnp,
                     ref_at=ref_at, val_at=val_at, **({} if in_bom else {"in_bom": False}))
    for k, net in pins.items():
        if net != "":                       # "": the caller wires this pin by hand
            sheet.connect(pl, k, net, stub)
    return pl


def divider(sheet, x, y, top, node, bottom, rtop, rbot, cff=None, cff_on="top", label_dx=12.7, flag_top=False):
    """A vertical divider hand-wired at x: rtop from `top` down to the node, rbot from the node to
    `bottom`; the node leaves to the right as a label. An optional feed-forward capacitor sits
    across the top or the bottom resistor, 7.62 mm to its right."""
    if cff and cff_on == "top":       # the node label clears the capacitor's text
        label_dx = max(label_dx, snap(7.62 + 1.27 + part_text(cff) + 2.54))
    # a capacitor across the top resistor with a rating line: the node one step lower, clear of it
    pitch = 12.7 if cff and cff_on == "top" and PARTS[cff].get("spec") else 10.16
    t1, b1 = vpart(sheet, rtop, x, y, text="left")
    t2, b2 = vpart(sheet, rbot, x, y + pitch, text="left")
    if flag_top:             # a rail no output pin drives: its flag on a stub above the divider
        sheet.wire(t1, (t1[0], t1[1] - 7.62))
        sheet.attach(top, t1[0], t1[1] - 7.62, "up")
        sheet.flag_at(t1[0], t1[1] - 5.08, "right", 7.62)
    else:
        sheet.attach(top, t1[0], t1[1], "up")
    sheet.wire(b1, t2)
    yn = snap((b1[1] + t2[1]) / 2)
    sheet.junction(x, yn)
    sheet.wire((x, yn), (x + label_dx, yn))
    sheet.point(node, x + label_dx, yn, "right", "pas")
    if cff and cff_on == "bottom":    # the capacitor joins the bottom end: the symbol on a stub below
        sheet.wire(b2, (b2[0], b2[1] + 2.54))
        sheet.attach(bottom, b2[0], b2[1] + 2.54, "down")
    else:
        sheet.attach(bottom, b2[0], b2[1], "down")
    if cff:
        cx = x + 7.62
        cy = y if cff_on == "top" else y + pitch
        ct, cb = vpart(sheet, cff, cx, cy)
        end = t1 if cff_on == "top" else b2
        far = ct if cff_on == "top" else cb
        near = cb if cff_on == "top" else ct
        if abs(far[1] - end[1]) > 1e-6:
            sheet.wire(far, (cx, end[1]))
        sheet.wire((cx, end[1]), end)
        sheet.junction(*end)
        sheet.wire(near, (cx, yn))
        sheet.junction(cx, yn)
    return (x - 15.24, y - 3.81 - (15.24 if flag_top else 7.62), x + label_dx + len(node) * CHAR + 2.54,
            y + pitch + 3.81 + 6.35)


# ---------------------------------------------------------------------- layout aids

def net_text(net):
    """Horizontal space (mm) the label or power symbol of `net` takes beyond its wire end."""
    if net is None:
        return 1.27
    if net == "GND":
        return 2.54
    return len(net) * CHAR + 1.27


def part_text(key):
    """Width of the reference, value and spec text beside a vertical two-pin part."""
    p = PARTS[key]
    return max(len(p["value"]), len(p.get("spec") or ""), 5) * CHAR + 2.032  # the pitch keeps 1.27 mm to the next plate


def prow(sheet, x, y, specs, gap=2.54, dnp=False, extra=None):
    """A row of vertical two-pin parts at height y from x: specs are (key, top_net, bottom_net).
    Neighbours with the same top net share one wire and one symbol or label (CRAFT-171); the pitch
    follows each part's text and the next symbol's value. Returns the row's bbox."""
    runs = []
    for spec in specs:
        if runs and spec[1] is not None and runs[-1][-1][1] == spec[1]:
            runs[-1].append(spec)
        else:
            runs.append([spec])
    yt = snap(y - 6.35)
    xs = snap(x)
    right = left = xs
    prev = None          # (x of the last part, its text width, x of its run's symbol, that text width)
    top_need = bot_need = 0.0
    for run in runs:
        a = run[0][1]
        half = net_text(a) / 2 if a in RAILS else 0.0
        if prev is not None:
            lx, lw, sx, sw = prev
            xs = snap_up(max(xs, lx + 1.27 + lw + 1.27 + half, sx + sw + 1.27 + half))
        else:
            left = xs - half
        first = xs
        for j, (key, _a, b_net) in enumerate(run):
            if j and b_net in RAILS and b_net != "GND":     # a rail value below: room for its text
                xs = snap(max(xs, xs_prev + net_text(b_net) + 1.27))
            if (j or prev is not None) and PARTS[key]["kind"] == "RT":   # the thermistor's -t° left of its body
                xs = snap(xs + 3.81)
                if not j:
                    first = xs
            t_, b_ = vpart(sheet, key, xs, y, **({"dnp": True} if dnp else {}), **({"extra": dict(extra)} if extra else {}))
            sheet.wire(t_, (xs, yt))
            if j:
                sheet.wire((xs_prev, yt), (xs, yt))
                sheet.junction(xs_prev, yt)
            if b_net == "GND":
                sheet.wire(b_, (b_[0], b_[1] + 2.54))
                sheet.power("GND", b_[0], b_[1] + 2.54)
            else:
                sheet.attach(b_net, b_[0], b_[1], "down")
            bot_need = max(bot_need, 2.54 + (6.35 if b_net in RAILS else net_text(b_net)))
            if b_net in RAILS and b_net != "GND":      # a rail value centred below the part
                left = min(left, xs - net_text(b_net) / 2)
            xs_prev, lw = xs, part_text(key)
            if b_net in RAILS and b_net != "GND":
                lw = max(lw, net_text(b_net) / 2)
            right = max(right, xs + 1.27 + lw)
            if j < len(run) - 1:
                xs = snap_up(xs + max(lw + 1.27, 5.08) + gap)
        sheet.attach(a, first, yt, "up")
        top_need = max(top_need, 2.54 + (3.81 if a in RAILS else net_text(a)))
        prev = (xs_prev, lw, first, half)
        right = max(right, first + half)
        xs = snap_up(xs + lw + 1.27 + gap)
    return (snap(left - 2.54), snap(y - 3.81 - top_need), snap(right + 1.27), snap(y + 3.81 + bot_need))


class Group:
    """A titled group box drawn around what is placed in it (CRAFT-174): add bboxes, then close."""

    def __init__(self, sheet, title, pad=2.54):
        self.sheet, self.title, self.pad, self.boxes = sheet, title, pad, []

    def add(self, bbox):
        self.boxes.append(bbox)
        return bbox

    def close(self, min_w=0.0):
        x0 = min(b[0] for b in self.boxes) - self.pad
        y0 = min(b[1] for b in self.boxes) - self.pad
        x1 = max(b[2] for b in self.boxes) + self.pad
        y1 = max(b[3] for b in self.boxes) + self.pad
        x1 = max(x1, x0 + min_w, x0 + len(self.title) * 2.3 + 2.54)
        if self.title:          # an untitled group only collects its parts' bbox for an outer group
            self.sheet.group_box(self.title, snap(x0), snap(y0), snap(x1 - x0), snap(y1 - y0))
        return snap(x0), snap(y0), snap(x1), snap(y1)


def hbox(x, y, key, a, b, stub=2.54):
    """bbox of a horizontal two-pin part centred at (x, y) with nets a (left) and b (right)."""
    p = PARTS[key]
    tw = max(len(p["value"]), len(p.get("spec") or "")) * CHAR / 2
    bottom = 5.08 + (1.27 if p["kind"] == "C" else 0.0) + (2.54 if p.get("spec") else 0.0)
    return (snap(x - 3.81 - stub - net_text(a)), y - 7.62, snap(x + 3.81 + stub + net_text(b)), snap_up(y + bottom))


def row_need(specs):
    top = max(2.54 + (3.81 if a in RAILS else net_text(a)) for _, a, _ in specs)
    return top


def under(sheet, bbox, specs, x=None, gap=2.54):
    """A passive row (prow) placed below bbox, left-aligned with it unless x is given."""
    y = snap(bbox[3] + gap + row_need(specs) + 3.81)
    return prow(sheet, (x if x is not None else bbox[0] + 2.54), y, specs)


class Flow:
    """Lays groups out left to right in rows (CRAFT-170 upper band): draw a group anywhere,
    then place(mark, bbox) moves everything drawn since mark to the next free slot."""

    def __init__(self, sheet, x0=22.86, y0=30.48, x_max=None, gap=5.08):
        W, _H = frame(sheet)
        self.sheet, self.x0, self.x, self.y = sheet, x0, x0, y0
        self.x_max = x_max or (W - MARGIN - 3.81)
        self.gap, self.row_h = gap, 0.0

    def place(self, mark, bbox, newline=False):
        x0, y0, x1, y1 = bbox[0], bbox[1] - 5.08, bbox[2], bbox[3]   # room for the group title
        w, h = x1 - x0, y1 - y0
        if (newline or self.x + w > self.x_max) and self.x > self.x0:
            self.x, self.y, self.row_h = self.x0, snap(self.y + self.row_h + self.gap), 0.0
        dx, dy = snap(self.x - x0), snap(self.y - y0)
        self.sheet.shift(mark, dx, dy)
        if os.environ.get("T1_LAYOUT_DEBUG"):
            print(f"layout: {self.sheet.name}: {w:.0f} x {h:.0f} at ({self.x:.0f}, {self.y:.0f})")
        self.x = snap(self.x + w + self.gap)
        self.x_right = max(getattr(self, "x_right", 0.0), x1 + dx)
        self.row_h = max(self.row_h, h)
        return (x0 + dx, y0 + dy, x1 + dx, y1 + dy)

    def bottom(self):
        return snap(self.y + self.row_h)


def side_collector(sheet, pl, keys, net, xoff):
    """Connector contacts on one side with one rail (VBUS, GND): each contact's wire runs out xoff
    past the pin end to one vertical collector clear of the signal labels, with one symbol at its
    end: a rail above the first contact, GND below the last (CRAFT-85, -171). The caller maps
    these contacts to "" in ic(). Returns the collector's x."""
    ends = []
    for k in keys:
        px, py = pl.pos(pl.pin(k))
        side = 1 if pl.out(pl.pin(k))[0] > 0 else -1
        xc = px + side * xoff
        sheet.wire((px, py), (xc, py))
        ends.append((xc, py))
    ys = sorted(y for _, y in ends)
    xc = ends[0][0]
    for y in ys[1:-1]:
        sheet.junction(xc, y)
    if net == "GND":
        if len(ys) > 1:
            sheet.junction(xc, ys[-1])
        sheet.wire((xc, ys[0]), (xc, ys[-1] + 5.08))
        sheet.power(net, xc, ys[-1] + 5.08)
    else:
        if len(ys) > 1:
            sheet.junction(xc, ys[0])
        sheet.wire((xc, ys[-1]), (xc, ys[0] - 5.08))
        sheet.power(net, xc, ys[0] - 5.08)
    return xc

