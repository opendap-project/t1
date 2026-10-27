"""Schematic writer for the T1 main board: sheets, placed symbols, nets resolved into labels.

Blocks connect pins to nets by name. A net used on one sheet only gets local labels; a net used on
several sheets crosses the hierarchy through hierarchical labels and sheet pins, which are worked
out here from where each net is used. Rails connect through power symbols named as the power tree.
"""

from __future__ import annotations

import uuid

import library
from library import outward, rotate
from sexpr import n, q

NS = uuid.UUID("2f7c0a52-5b9e-4c51-9a3e-7d1f3c0b2a11")
G = 1.27
DATE = "2026-10-25"
REV = "A"
HOLDER = "The OpenDAP Project"
PROJECT = "t1-main-board"
PAPER = {"A4": (297.0, 210.0), "A3": (420.0, 297.0)}

# Rails of the power tree (power tree v0.5, rail table and §3.1). Every power symbol names one.
RAILS = [
    "GND", "VSYS", "VSYS_LV", "vcc3v3_sys", "vdd_cpu", "vdd_logic", "vdd_gpu", "vdd_npu", "vcc_ddr",
    "vcc0v6_ddr", "vcc1v8_ddr", "vcc_1v8", "vccio6_1v8", "vdda0v9_image", "vdda_0v9", "vdda0v9_pmu",
    "FP_VCI", "vccio_sd", "vcc3v3_pmu", "vcca_1v8", "vcca1v8_pmu", "vcca1v8_image", "vcc3v3_sd",
    # audio (power tree §2, §3)
    "DAC_VP", "DAC_DIG_1V8", "AUDIO_2V2", "DAC1_VA", "DAC2_VA", "MCLK_3V1", "MCLK_1V8",
    "AUDIO_P7V0", "AUDIO_N7V0", "HPA_P6V0", "HPA_N6V0",
    # input, charger and battery path (power tree §2, §4.7)
    "USBC_VBUS", "HAT_5V", "VBUS_CHG", "VBAT", "BAT_N",
    # faceplate supplies (power tree §2, §3; faceplate interface v1)
    "FP_3V3", "FP_1V8", "MIC_1V8", "FP_VCI_SRC",
    # radio (power tree §2, v0.2)
    "vcc3v3_wl", "vcc1v8_wl",
    # NFC controller and coprocessor (power tree v0.2 §3)
    "NFC_VBAT", "RP_3V3", "RP_IOVDD_1V8",
    # the branches the INA236 shunts measure (power tree §4.12, G11): supply side of the VSYS shunt
    # (BQ25798 SYS), then the load side of each branch shunt
    "VSYS_SRC", "VSYS_LV_AUDIO", "VSYS_AUDIO", "VSYS_LV_BL", "VSYS_P5V1",
    # the faceplate microphone branch behind link #34 (power tree §4.12, G10)
    "MIC_1V8_FP",
]


def uid(*parts):
    return str(uuid.uuid5(NS, "/".join(map(str, parts))))


def snap(v):
    return round(round(v / G) * G, 4)


def snap_down(v):
    """Down to the grid point at or before v: a box that must stay inside an edge."""
    import math
    return round(math.floor(round(v / G, 6)) * G, 4)


def snap_up(v):
    """Up to the next grid point: a spacing that must clear text never rounds down (CRAFT-175)."""
    import math
    return round(math.ceil(round(v / G, 6)) * G, 4)


def eff(size=1.27, hide=False, justify=None, bold=False):
    font = f"(font (size {n(size)} {n(size)}){' (bold yes)' if bold else ''})"
    j = f" (justify {justify})" if justify else ""
    return f"(effects {font}{j})" + (" (hide yes)" if hide else "")


DIR = {(1, 0): "right", (-1, 0): "left", (0, -1): "up", (0, 1): "down"}
LABEL_ANGLE = {"right": 0, "up": 90, "left": 180, "down": 270}
PIN_DIRECTION = {"output": "out", "power_out": "out", "input": "in", "power_in": "in",
                 "bidirectional": "bi", "tri_state": "bi", "open_collector": "bi", "open_emitter": "bi",
                 "passive": "pas", "unspecified": "pas", "free": "pas", "no_connect": "pas"}


class NetPoint:
    """A place where a net leaves a wire end: rendered later as a label or hierarchical label."""

    def __init__(self, sheet, net, x, y, direction, ptype):
        self.sheet, self.net, self.x, self.y = sheet, net, x, y
        self.direction, self.ptype = direction, ptype


class Placed:
    def __init__(self, sheet, sym, ref, unit, x, y, angle):
        self.sheet, self.sym, self.ref, self.unit = sheet, sym, ref, unit
        self.x, self.y, self.angle = x, y, angle

    def pin(self, key):
        """A pin of this unit by number, or by name when unique."""
        try:
            return self.sym.pin(key, self.unit)
        except KeyError:
            ps = self.sym.pins_named(key, self.unit)
            if len(ps) != 1:
                raise KeyError(f"{self.ref}: pin {key!r} not found or ambiguous ({len(ps)})")
            return ps[0]

    def pos(self, p):
        dx, dy = rotate(p.x, -p.y, self.angle)
        return round(self.x + dx, 4), round(self.y + dy, 4)

    def out(self, p):
        return outward(p, self.angle)


class Sheet:
    def __init__(self, project, name, role, title, purpose, paper="A4", block=None):
        self.project, self.name, self.role = project, name, role
        self.title, self.purpose, self.paper = title, purpose, paper
        self.block = block or (role if role.startswith("blk.") else None)
        self.uuid = uid(PROJECT, "sheet-file", name)
        self.sheet_uuid = uid(PROJECT, "sheet-symbol", name)
        self.items, self.lib = [], {}
        self.points = []           # NetPoints
        self.children = []         # ChildSheet
        self.parent = None
        self.page = None
        self.placed = []           # Placed symbols (for the BOM / checks)
        self.counters = {}
        self.base = None
        self.inst_path = None
        self.junctions = set()
        self.rails_here = set()    # rails with a power symbol on this sheet (zone net classes)

    # ------------------------------------------------------------------ basics
    def use(self, sym):
        self.lib[sym.lib_id] = sym.text

    def add(self, s):
        self.items.append(s)

    def wire(self, *pts):
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            if (x1, y1) == (x2, y2):
                continue
            self.add(f"(wire (pts (xy {n(x1)} {n(y1)}) (xy {n(x2)} {n(y2)})) (stroke (width 0) (type default)) "
                     f"(uuid {q(uid(self.name, 'w', x1, y1, x2, y2))}))")

    def bus(self, *pts):
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            if (x1, y1) == (x2, y2):
                continue
            self.add(f"(bus (pts (xy {n(x1)} {n(y1)}) (xy {n(x2)} {n(y2)})) (stroke (width 0) (type default)) "
                     f"(uuid {q(uid(self.name, 'b', x1, y1, x2, y2))}))")

    def junction(self, x, y):
        key = (round(x, 3), round(y, 3))
        if key in self.junctions:
            return
        self.junctions.add(key)
        self.add(f"(junction (at {n(x)} {n(y)}) (diameter 0) (color 0 0 0 0) (uuid {q(uid(self.name, 'j', *key))}))")

    def nc(self, x, y):
        self.add(f"(no_connect (at {n(x)} {n(y)}) (uuid {q(uid(self.name, 'nc', x, y))}))")

    def text(self, s, x, y, size=1.27, bold=False):
        self.add(f"(text {q(s)} (exclude_from_sim no) (at {n(x)} {n(y)} 0) {eff(size, justify='left bottom', bold=bold)} "
                 f"(uuid {q(uid(self.name, 't', s[:60], x, y))}))")

    def text_box(self, s, x, y, w, h=None):
        if h is None:
            h = G * -(-(len(s.split("\n")) * 2.2 + 3.81) // G)
        self.add(f"(text_box {q(s)} (exclude_from_sim no) (at {n(x)} {n(y)} 0) (size {n(w)} {n(h)}) "
                 "(margins 1.905 1.905 1.905 1.905) (stroke (width 0) (type default)) (fill (type none)) "
                 f"{eff(justify='left top')} (uuid {q(uid(self.name, 'tb', s[:60]))}))")
        return h

    def group_box(self, title, x, y, w, h):
        self.add(f"(rectangle (start {n(x)} {n(y)}) (end {n(x + w)} {n(y + h)}) (stroke (width 0) (type dash)) "
                 f"(fill (type none)) (uuid {q(uid(self.name, 'r', title, x, y))}))")
        self.text(title, x + G, y - G, size=2.54)

    def table(self, x, y, widths, rows, key, title=None):
        """A KiCad table (CRAFT-176); the first row is the header. Each row is as tall as its
        longest wrapped cell (text_lines). Returns its height."""
        if title:
            self.text(title, x, y - G, size=2.54)
        heights = [row_height(row, widths) for row in rows]
        cells = []
        cy = y
        for r, row in enumerate(rows):
            cx = x
            for ci, cell in enumerate(row):
                w = widths[ci]
                cells.append(f"(table_cell {q(cell)} (exclude_from_sim no) (at {n(cx)} {n(cy)} 0) (size {n(w)} {n(heights[r])}) "
                             f"(margins 0.9525 0.9525 0.9525 0.9525) (span 1 1) (fill (type none)) "
                             f"{eff(justify='left top', bold=(r == 0))} (uuid {q(uid(self.name, key, r, ci))}))")
                cx += w
            cy += heights[r]
        self.add(f"(table (column_count {len(widths)}) (border (external yes) (header yes) (stroke (width 0) (type solid))) "
                 f"(separators (rows yes) (cols yes) (stroke (width 0) (type solid))) "
                 f"(column_widths {' '.join(n(w) for w in widths)}) (row_heights {' '.join(n(h) for h in heights)}) "
                 f"(cells {' '.join(cells)}))")
        return sum(heights)

    def mark(self):
        return len(self.items), len(self.points)

    def shift(self, mark, dx, dy):
        """Move everything drawn since `mark` by (dx, dy): lays a hand-wired circuit out on the page."""
        import re as _re
        i0, p0 = mark

        def mv(m):
            return f"({m.group(1)} {n(float(m.group(2)) + dx)} {n(float(m.group(3)) + dy)}"
        pat = _re.compile(r"\((at|xy|start|end) (-?[\d.]+) (-?[\d.]+)")
        for i in range(i0, len(self.items)):
            it = self.items[i]
            if it.startswith(("(symbol", "(wire", "(bus ", "(junction", "(no_connect", "(rectangle", "(text ")):
                self.items[i] = pat.sub(mv, it)
        for p in self.points[p0:]:
            p.x, p.y = round(p.x + dx, 4), round(p.y + dy, 4)
        jre = _re.compile(r"\(junction \(at (-?[\d.]+) (-?[\d.]+)\)")
        self.junctions = set()
        for it in self.items:
            m = jre.match(it)
            if m:
                self.junctions.add((round(float(m.group(1)), 3), round(float(m.group(2)), 3)))

    # ------------------------------------------------------------------ references
    def next_ref(self, prefix):
        c = self.counters.get(prefix, 0) + 1
        self.counters[prefix] = c
        return f"{prefix}{self.base + c}"

    # ------------------------------------------------------------------ symbols
    def place(self, sym, ref, x, y, unit=1, angle=0, fields=None, shown=None, ref_at=None, val_at=None,
              in_bom=True, on_board=True, dnp=False, variants=None, value=None):
        """Place one unit of a symbol. fields: hidden fields; shown: extra shown fields (Spec)."""
        self.use(sym)
        x, y = snap(x), snap(y)
        pl = Placed(self, sym, ref, unit, x, y, angle)
        f = {k: v for k, v in sym.props.items() if not k.startswith("ki_") and k not in ("Reference", "Value")}
        f.update(fields or {})
        val_text = value if value is not None else sym.props.get("Value", sym.name)
        self.project.parts.append((self, pl, f, val_text, in_bom, dnp, variants or {}))
        x0, y0, x1, y1 = sym.body(unit)
        # fields (rotation 0, unless given): on a side of the body with no pins, value above the
        # reference so that a unit name after the reference never meets it
        if ref_at is None and angle in (0, 180):
            side = field_side(sym, unit)
            ref_label = ref + (sym.unit_names.get(unit, "") if len(sym.units) > 1 else "")
            if side == "top":
                tops = [p.x for p in sym.unit_pins(unit) if p.side() == "top"]
                fx = x + (max(tops) + G if tops else x0)      # right of the top pins, clear of their wires
                ref_at, val_at = (fx, y - y1 - 2 * G), val_at or (fx, y - y1 - 4 * G)
            elif side == "bottom":
                ref_at, val_at = (x + x0, y - y0 + 4 * G), val_at or (x + x0, y - y0 + 2 * G)
            elif side == "left":
                wmax = max(len(ref_label), len(value or sym.name)) * 1.16
                ref_at, val_at = (x + x0 - 1.27 - wmax, y - y1 + 2 * G), val_at or (x + x0 - 1.27 - wmax, y - y1)
            else:
                ref_at, val_at = (x + x1 + 1.27, y - y1 + 2 * G), val_at or (x + x1 + 1.27, y - y1)
        elif ref_at is None:
            ref_at = (x + 2.54, y - G)
        if val_at is None:
            val_at = (ref_at[0], ref_at[1] + 2 * G) if angle not in (0, 180) else (ref_at[0], ref_at[1] - 2 * G)
        is_power = ref.startswith("#")
        fa = angle if angle in (90, 270) else 0
        props = [("Reference", ref, ref_at, is_power), ("Value", val_text, val_at, False)]
        sx, sy = val_at[0], val_at[1] + 2 * G if angle in (90, 270) else val_at[1] + 2 * G
        for k, v in (shown or {}).items():
            props.append((k, v, (sx, sy), False))
            sy += 2 * G
        # the shown fields' text extents (horizontal, left-justified), for the callers' bboxes
        pl.texts = [(px, py, px + len(str(v)) * 1.16, py) for k, v, (px, py), hide in props
                    if not hide and fa == 0]
        body = [f"(symbol (lib_id {q(sym.lib_id)}) (at {n(x)} {n(y)} {angle}) (unit {unit}) (body_style 1) "
                f"(exclude_from_sim no) (in_bom {'yes' if in_bom else 'no'}) (on_board {'yes' if on_board else 'no'}) "
                f"(dnp {'yes' if dnp else 'no'}) (uuid {q(uid(self.name, 's', ref, unit))})"]
        for k, v, (px, py), hide in props:
            body.append(f"  (property {q(k)} {q(v)} (at {n(px)} {n(py)} {fa}) "
                        f"{eff(hide=hide, justify=None if fa else 'left')})")
        for k, v in f.items():
            body.append(f"  (property {q(k)} {q(v)} (at {n(x)} {n(y)} 0) {eff(hide=True)})")
        for p in sym.unit_pins(unit):
            body.append(f"  (pin {q(p.number)} (uuid {q(uid(self.name, 'p', ref, unit, p.number))}))")
        body.append("  (instances (project {} (path @PATH@ (reference {}) (unit {}){})))".format(
            q(PROJECT), q(ref), unit, "".join(_variant(name, v) for name, v in (variants or {}).items())))
        body.append(")")
        self.add("\n".join(body))
        self.placed.append(pl)
        return pl

    def power(self, rail, x, y, angle=0, flag=False, vertical=False):
        """A power symbol whose pin is at (x, y): GND points down, rails point away (angle)."""
        if flag:
            sym = library.load("power", "PWR_FLAG")
            ref = self.project.next_power("#FLG")
            value = "PWR_FLAG"
        else:
            sym = library.load("power", "GND" if rail == "GND" else "VCC")
            ref = self.project.next_power("#PWR")
            value = rail
            self.rails_here.add(rail)
            if rail == "GND":
                angle = 0
        self.use(sym)
        up = rail != "GND" and not flag
        vx, vy = x, y - 3.81 if up else (y + 5.08 if flag and angle == 180 else y + 3.81)
        if up and angle == 180:            # a rail pointing down: its value below the symbol
            vy = y + 4.445
        if angle in (90, 270):
            vx, vy = (x - 2.54 if angle == 90 else x + 2.54), y
        fa = angle if angle in (90, 270) else 0
        just = "right" if angle == 90 else ("left" if angle == 270 else None)
        self.add("\n".join([
            f"(symbol (lib_id {q(sym.lib_id)}) (at {n(x)} {n(y)} {angle}) (unit 1) (body_style 1) (exclude_from_sim no) "
            f"(in_bom yes) (on_board yes) (dnp no) (uuid {q(uid(self.name, 'pw', ref))})",
            f"  (property \"Reference\" {q(ref)} (at {n(x)} {n(y)} {fa}) {eff(hide=True)})",
            (f"  (property \"Value\" {q(value)} (at {n(x)} {n(y - 3.81)} 90) {eff(justify='left')})" if vertical and angle == 0 and up else
             f"  (property \"Value\" {q(value)} (at {n(vx)} {n(vy)} {(360 - angle) % 360 if angle in (90, 270) else 0}) {eff(justify=just)})"),
            f"  (property \"Footprint\" \"\" (at {n(x)} {n(y)} 0) {eff(hide=True)})",
            f"  (property \"Datasheet\" \"\" (at {n(x)} {n(y)} 0) {eff(hide=True)})",
            f"  (pin \"1\" (uuid {q(uid(self.name, 'pwp', ref))}))",
            f"  (instances (project {q(PROJECT)} (path @PATH@ (reference {q(ref)}) (unit 1))))",
            ")"]))

    # ------------------------------------------------------------------ connections
    def point(self, net, x, y, direction, ptype="pas"):
        """A net leaves at (x, y) going `direction` (left/right/up/down): label decided later."""
        self.points.append(NetPoint(self, net, x, y, direction, ptype))

    def attach(self, net, x, y, direction, ptype="pas", vertical=False):
        """Connect (x, y), a wire end facing `direction`, to `net`: power symbol, no-connect or label."""
        if net is None:
            self.nc(x, y)
        elif net in RAILS:
            self.project.rails_used.add(net)
            if net == "GND":
                self.power("GND", x, y)
            else:
                self.power(net, x, y, angle={"up": 0, "left": 90, "down": 180, "right": 270}[direction],
                           vertical=vertical)
        else:
            self.point(net, x, y, direction, ptype)

    def connect(self, pl, key, net, stub=2.54, vertical=False):
        """Connect one pin to a net through a stub wire leaving the body. net None: no-connect flag."""
        p = pl.pin(key)
        x, y = pl.pos(p)
        dx, dy = pl.out(p)
        done = pl.__dict__.setdefault("done", set())
        if (x, y) in done:        # stacked pins (one land, two numbers) connect once
            return
        done.add((x, y))
        if net in RAILS:
            self.project.rails_used.add(net)
            if p.etype == "power_out":
                self.project.driven.add(net)
        if net is None:
            self.nc(x, y)
            return
        if dx and net in RAILS and pl.unit is not None and len(pl.sym.pins) > 2:
            # a rail on a side pin of an IC: its symbol upright at the stub end (GND down, a rail up).
            # The symbol and its value take the two rows on that side, so it moves out past what
            # those rows hold: a label's text, or the wire and arrow of a rail drawn there.
            rows = {round(pl.pos(q)[1], 3): q for q in pl.sym.unit_pins(pl.unit) if pl.out(q) == (dx, dy)}
            sgn = 1 if net == "GND" else -1
            netmap = getattr(pl, "netmap", {})
            ends = pl.__dict__.setdefault("side_ends", {})
            if net != "GND" and any(netmap.get(getattr(rows.get(round(y + k * 2.54, 3)), "number", None))
                                    not in (None, "GND") and
                                    netmap.get(getattr(rows.get(round(y + k * 2.54, 3)), "number", None)) in RAILS
                                    for k in (-1, 1)):
                # a column of rails (a PMIC's LDO outputs): each symbol turned outward, its value
                # on its own row, as a label would be
                ex = x + dx * stub
                self.wire((x, y), (ex, y))
                self.attach(net, ex, y, "right" if dx > 0 else "left")
                ends[(dx, round(y, 3))] = stub + 2.54 + len(net) * 1.16
                reach = pl.__dict__.setdefault("reach", {})
                reach[dx] = max(reach.get(dx, 0.0), ends[(dx, round(y, 3))])
                return
            half = 1.27 if net == "GND" else len(net) * 0.58
            need = 0.0
            for k in (1, 2):
                yk = round(y + sgn * 2.54 * k, 3)
                if (dx, yk) in ends:
                    reach = ends[(dx, yk)]
                else:
                    nb = rows.get(yk)
                    if nb is None:
                        continue
                    other = netmap.get(nb.number)
                    if other is None:         # a no-connect flag at the pin end, the pin number inside
                        reach = 0.75
                    elif not other:
                        continue
                    else:
                        # a rail below a ground may be drawn turned outward with its value (a
                        # column of rails): reserve the room of its text, as for a label
                        reach = (2.54 + 0.75 if other in RAILS and net != "GND"
                                 else 2.54 + len(other) * 1.16 + 1.27)
                need = max(need, reach + 1.27 + (half if k == 2 or net == "GND" else 0.0), reach + 1.27)
                if k == 1 and net != "GND":
                    need = max(need, reach + 1.27 + half)
            if net != "GND":
                # the value is centred on the symbol: it never reaches back over the body's edge or
                # the fields above it, even on the side's top row
                need = max(need, half + 1.27)
            if need:
                stub = snap(max(stub, need + (half if net == "GND" else 0.0)))
                stub = stub if abs(stub / 1.27 - round(stub / 1.27)) < 1e-6 else snap(stub + 1.27)
            ends[(dx, round(y, 3))] = stub + 0.75
            # what the symbol's value takes beyond the pin end, for the part's bbox
            reach = pl.__dict__.setdefault("reach", {})
            reach[dx] = max(reach.get(dx, 0.0), stub + half + 0.5)
            ex = x + dx * stub
            self.wire((x, y), (ex, y))
            self.project.rails_used.add(net)
            self.power(net, ex, y)
            return
        if net == "GND" and (dx, dy) != (0, 1) and stub < 5.08:
            stub = 5.08
        ex, ey = x + dx * stub, y + dy * stub
        self.wire((x, y), (ex, ey))
        self.attach(net, ex, ey, DIR[(dx, dy)], PIN_DIRECTION.get(p.etype, "pas"), vertical=vertical)

    def connect_all(self, pl, mapping, stub=2.54, collect=True):
        """Connect every pin of the unit: mapping pin key -> net (None: no-connect). Runs of
        neighbouring pins on the same edge with the same rail share one collector and one symbol."""
        pl.netmap = {pl.pin(k).number: v for k, v in mapping.items()}
        pins = []
        for key, net in mapping.items():
            if net == "":                 # wired by hand by the caller
                continue
            p = pl.pin(key)
            pins.append((p, net))
        if collect:
            done = self._collect_rails(pl, pins, stub)
        else:
            done = set()
        crowded = sum(1 for p, _ in pins if pl.out(p) == (0, -1)) > 1
        # side pins top to bottom: a rail's symbol moves out past what the rows above it hold
        pins.sort(key=lambda t: (pl.out(t[0]), pl.pos(t[0])[1]) if pl.out(t[0])[0] else ((9, 9), 0))
        for p, net in pins:
            if id(p) not in done:
                self.connect(pl, p.number, net, stub, vertical=crowded and pl.out(p) == (0, -1))

    def _collect_rails(self, pl, pins, stub):
        done = set()
        by_edge = {}
        for p, net in pins:                     # top and bottom edges: runs of any net share a collector
            if net is not None:
                d = pl.out(p)
                if d in ((0, -1), (0, 1)):
                    by_edge.setdefault(d, []).append((p, net))
        for p, net in pins:
            if net in RAILS:
                self.project.rails_used.add(net)
                if p.etype == "power_out":
                    self.project.driven.add(net)
        for p, net in pins:                     # side edges: runs of a rail join on a vertical collector
            if net in RAILS and pl.out(p) in ((-1, 0), (1, 0)):
                by_edge.setdefault(pl.out(p), []).append((p, net))
        for d, lst in by_edge.items():
            if d[0]:
                done |= self._collect_side(pl, d, lst, stub)
                continue
            lst.sort(key=lambda t: pl.pos(t[0])[0])
            # runs: consecutive pins with the same net, 2.54 mm apart or across one empty grid slot
            # (an even pin count leaves the centre of its edge empty)
            runs, cur = [], [lst[0]]
            for a in lst[1:]:
                if a[1] == cur[-1][1] and pl.pos(a[0])[0] - pl.pos(cur[-1][0])[0] < 5.08 + 1e-3:
                    cur.append(a)
                else:
                    runs.append(cur)
                    cur = [a]
            runs.append(cur)
            for run in runs:
                if len(run) < 2:
                    continue
                net = run[0][1]
                xs = [pl.pos(p)[0] for p, _ in run]
                y0 = pl.pos(run[0][0])[1]
                yc = y0 + d[1] * stub
                for p, _ in run:
                    px, py = pl.pos(p)
                    self.wire((px, py), (px, yc))
                    done.add(id(p))
                self.wire((xs[0], yc), (xs[-1], yc))
                for x in xs[1:-1]:
                    self.junction(x, yc)
                # one symbol per run, taken off the run's first end (a T, never a four-way)
                ext = (xs[0], yc + d[1] * 2.54)
                self.wire((xs[0], yc), ext)
                self.junction(xs[0], yc)
                self.attach(net, ext[0], ext[1], DIR[d], vertical=d == (0, -1))
        return done

    def _collect_side(self, pl, d, lst, stub):
        """Neighbouring pins on a side edge with the same rail: stubs to one vertical collector,
        one symbol at its end (GND below the run, a rail above it)."""
        done = set()
        lst.sort(key=lambda t: pl.pos(t[0])[1])
        runs, cur = [], [lst[0]]
        for a in lst[1:]:
            if a[1] == cur[-1][1] and abs(pl.pos(a[0])[1] - pl.pos(cur[-1][0])[1] - 2.54) < 1e-3:
                cur.append(a)
            else:
                runs.append(cur)
                cur = [a]
        runs.append(cur)
        side_ys = {round(pl.pos(p)[1], 3) for p in pl.sym.unit_pins(pl.unit) if pl.out(p) == d}
        for run in runs:
            if len(run) < 2:
                continue
            net = run[0][1]
            # a rail's value is centred on the collector: far enough out to clear the body's edge
            reach = stub if net == "GND" else max(stub, snap_up(len(net) * 0.58 + 1.27))
            xc = pl.pos(run[0][0])[0] + d[0] * reach
            ys = [pl.pos(p)[1] for p, _ in run]
            beyond = ys[-1] + 2.54 if net == "GND" else ys[0] - 2.54
            if round(beyond, 3) in side_ys:     # the symbol would sit on a neighbour's row: one per pin
                continue
            # its value text takes the next row too: past that neighbour's label when it is taken
            sgn = 1 if net == "GND" else -1
            two = (ys[-1] if net == "GND" else ys[0]) + sgn * 5.08
            nb = {round(pl.pos(p)[1], 3): p for p in pl.sym.unit_pins(pl.unit) if pl.out(p) == d}.get(round(two, 3))
            other = None if nb is None else getattr(pl, "netmap", {}).get(nb.number)
            if (other or (nb is not None and other is None)) and net != "GND":
                # its value text would reach that neighbour's label or pin number (a no-connect
                # pin): the symbol turns outward on a stub off the run's first row instead
                for p, _ in run:
                    px, py = pl.pos(p)
                    self.wire((px, py), (xc, py))
                    done.add(id(p))
                self.wire((xc, ys[0]), (xc, ys[-1]))
                for y in ys[1:-1]:
                    self.junction(xc, y)
                self.junction(xc, ys[0])
                self.wire((xc, ys[0]), (xc + d[0] * 2.54, ys[0]))
                self.attach(net, xc + d[0] * 2.54, ys[0], "left" if d[0] < 0 else "right")
                # the turned symbol's value reads outward from the stub end: the part's bbox holds it
                far = pl.__dict__.setdefault("reach", {})
                far[d[0]] = max(far.get(d[0], 0.0), reach + 2.54 + len(net) * 1.16 + 1.27)
                continue
            for p, _ in run:
                px, py = pl.pos(p)
                self.wire((px, py), (xc, py))
                done.add(id(p))
            for y in ys[1:-1]:
                self.junction(xc, y)
            if net == "GND" and nb is not None and other != "GND":
                # a pin two rows below: the ground symbol and its text further out, clear of that
                # pin's no-connect flag and number, or past its label's text
                out = 2.54 if other is None else snap_up(2.54 + len(other) * 1.16 + 2.54)
                xg = xc + d[0] * out
                self.wire((xc, ys[0]), (xc, ys[-1]), (xg, ys[-1]), (xg, ys[-1] + 2.54))
                self.junction(xc, ys[-1])
                self.attach(net, xg, ys[-1] + 2.54, "down")
            elif net == "GND":
                self.wire((xc, ys[0]), (xc, ys[-1] + 2.54))
                self.junction(xc, ys[-1])
                self.attach(net, xc, ys[-1] + 2.54, "down")
            else:
                self.wire((xc, ys[0] - 2.54), (xc, ys[-1]))
                self.junction(xc, ys[0])
                self.attach(net, xc, ys[0] - 2.54, "up")
        return done

    def flag_mid(self, pl, key, direction):
        """A PWR_FLAG on a branch from the middle of a pin's stub: for a rail driven through a
        passive part (inductor, measurement link) or from a block not drawn yet (ERC)."""
        p = pl.pin(key)
        x, y = pl.pos(p)
        dx, dy = pl.out(p)
        mx, my = x + dx * 1.27, y + dy * 1.27
        ox, oy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[direction]
        ex, ey = mx + ox * 5.08, my + oy * 5.08
        self.junction(mx, my)
        self.wire((mx, my), (ex, ey))
        self.power(None, ex, ey, angle={"up": 0, "left": 90, "down": 180, "right": 270}[direction], flag=True)

    def flag_net(self, net, x=None, y=None, since=None, side=None):
        """A PWR_FLAG for a net fed through a passive part (inductor, link, filter resistor) or from a
        block not drawn yet, always on a branch of the net's own wire outside the groups' text
        (CRAFT-85): at (x, y), a point inside one of its wires; or, for a part drawn inside a group
        that moves later, on the stub of the net's label that leaves the feeding part: the first
        label of the net drawn after the mark `since` (Sheet.mark()[1]) whose direction is `side`
        (draw.local_flags places it once the groups are laid out). KiCad 10.0.7's ERC reports a
        flag on an island of power symbols as pin_not_connected, so a flag cannot sit on the power
        overview; and a local net cannot reach another sheet."""
        if x is not None:
            self.flag_at(x, y, "down", 2.54)
        elif since is not None and side:
            self.project.flag_points.append((self, net, since, side))
        else:
            raise SystemExit(f"generator: {self.name}: a PWR_FLAG for {net} needs a wire to hang from")

    def flag_at(self, x, y, direction, length=5.08):
        """A PWR_FLAG on a branch from (x, y), a point inside an existing wire. The flag hangs
        below the branch end, so its text reads horizontally."""
        ox, oy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}[direction]
        ex, ey = x + ox * length, y + oy * length
        self.junction(x, y)
        self.wire((x, y), (ex, ey))
        self.power(None, ex, ey, angle=180, flag=True)

    def two_pin(self, sym, ref, x, y, net1, net2, angle=0, fields=None, shown=None, stub=2.54, **kw):
        """A two-pin part with each pin taken to a net through a short stub."""
        pl = self.place(sym, ref, x, y, angle=angle, fields=fields, shown=shown, **kw)
        for key, net in (("1", net1), ("2", net2)):
            self.connect(pl, key, net, stub)
        return pl

    # ------------------------------------------------------------------ hierarchy
    def child(self, sheet, x, y, w=None, sides=None):
        sheet.parent = self
        cs = ChildSheet(sheet, x, y, w, sides or {})
        self.children.append(cs)
        return cs


class ChildSheet:
    def __init__(self, sheet, x, y, w, sides):
        self.sheet, self.x, self.y, self.w, self.sides = sheet, x, y, w, sides
        self.pins = []   # (net, shape, side, offset), filled by the resolver
        self.h = None


TABLE_CHAR = 1.1      # mm per character of 1.27 mm table text (mixed case, with margin)
LINE = 2.032          # mm between wrapped lines of 1.27 mm text


def text_lines(s, width):
    """Lines a cell's text takes when KiCad wraps it at word boundaries in `width` mm."""
    cpl = max(1, int((width - 1.905) / TABLE_CHAR))
    lines, cur = 1, 0
    for word in str(s).split():
        k = len(word)
        if cur and cur + 1 + k > cpl:
            lines, cur = lines + 1, k
        else:
            cur = cur + 1 + k if cur else k
    return lines


def row_height(row, widths):
    lines = max(text_lines(c, w) for c, w in zip(row, widths))
    return snap(5.08 + (lines - 1) * LINE + 0.6) if lines > 1 else 5.08


def field_side(sym, unit):
    """The side of a unit's body where its reference and value go: the first of top, bottom,
    left, right with no pins (top when every side has pins)."""
    sides = {p.side() for p in sym.unit_pins(unit)}
    for s in ("top", "bottom", "left", "right"):
        if s not in sides:
            return s
    return "top"


def _variant(name, v):
    parts = [f"(variant (name {q(name)})"]
    if v.get("dnp"):
        parts.append("(dnp yes)")
    for k, val in v.get("fields", {}).items():
        parts.append(f"(field (name {q(k)}) (value {q(val)}))")
    return " " + " ".join(parts) + ")"
