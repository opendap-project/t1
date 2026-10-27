"""The T1 main board project: sheet tree, net resolution into labels and sheet pins, and the files
KiCad reads (schematic sheets, project file, library tables)."""

from __future__ import annotations

import json
import os
import re
import tomllib

import library
from sch import DATE, HOLDER, PAPER, PROJECT, RAILS, REV, G, Sheet, eff, snap, uid
from sexpr import n, q

RAIL_LIKE = re.compile(r"^(V[A-Z0-9_]*|.*\d+V\d*.*)$", re.I)
# a name with a voltage in it that is a control or sense line, not a supply (HAT5V_EN, EFUSE_5V_FLT_N)
CONTROL_LIKE = re.compile(r"_(EN|N|ON|IMON|ILM|DISCH)$")
LABEL_JUST = {"right": "left", "left": "right", "up": "left", "down": "right"}
LABEL_ANGLE = {"right": 0, "up": 90, "left": 180, "down": 270}


def natural(s):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


class Project:
    def __init__(self):
        self.sheets = []
        self.parts = []
        self.power_count = {"#PWR": 0, "#FLG": 0}
        self.root = None
        self.order = {}          # net -> sort key for sheet-pin order
        self.rails_used = set()  # rails connected anywhere
        self.driven = set()      # rails with a power-output pin on them
        self.flag_points = []    # (sheet, net, mark, side): flags placed after layout (draw.local_flags)
        self.aliases = {}        # bus alias -> member nets (written to the project file)

    def sheet(self, name, role, title, purpose, paper="A4", block=None):
        s = Sheet(self, name, role, title, purpose, paper, block)
        self.sheets.append(s)
        if self.root is None:
            self.root = s
        return s

    def next_power(self, prefix):
        self.power_count[prefix] += 1
        return f"{prefix}{self.power_count[prefix]:04d}"

    # ------------------------------------------------------------------ hierarchy helpers
    def subtree(self, s):
        out = {s}
        for c in s.children:
            out |= self.subtree(c.sheet)
        return out

    def number(self, reading_order):
        """Page numbers in reading order (CRAFT-111); reference blocks of 100 per page (CRAFT-116)."""
        for i, s in enumerate(reading_order, 1):
            s.page = str(i)
        assert set(reading_order) == set(self.sheets), "every sheet needs a page"

    # ------------------------------------------------------------------ net resolution
    def resolve(self):
        uses = {}
        for s in self.sheets:
            for p in s.points:
                uses.setdefault(p.net, set()).add(s)
        self.uses = uses
        subtrees = {s: self.subtree(s) for s in self.sheets}

        def inside(s, net):
            return bool(uses.get(net, set()) & subtrees[s])

        def outside(s, net):
            return bool(uses.get(net, set()) - subtrees[s])

        def shape(s, net):
            kinds = {p.ptype for t in subtrees[s] for p in t.points if p.net == net}
            act = kinds - {"pas"}
            if not act:
                return "passive"
            if act == {"in"}:
                return "input"
            if act == {"out"}:
                return "output"
            return "bidirectional"

        for s in self.sheets:
            s.hl_names = set()
            for p in s.points:
                p.kind = "hier" if (s is not self.root and outside(s, p.net)) else "label"
                if p.kind == "hier":
                    p.shape = shape(s, p.net)
                    s.hl_names.add(p.net)
            for cs in s.children:
                c = cs.sheet
                nets = sorted({net for net in uses if inside(c, net) and outside(c, net)}, key=self.pin_key)
                cs.pins = []
                for net in nets:
                    sh = shape(c, net)
                    if RAIL_LIKE.match(net) and net not in RAILS and not CONTROL_LIKE.search(net):
                        # a supply-like interface net (CRAFT-113): output on the right, else on top
                        cs.pins.append([net, sh, "right" if sh == "output" else "top"])
                        continue
                    if sh == "input":
                        side = cs.sides.get(net, "left")
                    elif sh == "output":
                        side = cs.sides.get(net, "right")
                    else:
                        side = cs.sides.get(net, cs.sides.get("*", "left"))
                    cs.pins.append([net, sh, side])
                cs.outer = {net: (s is not self.root and outside(s, net)) for net in nets}
                cs.shape_parent = {net: shape(s, net) for net in nets}

    def apply_aliases(self):
        """Interface nets that belong to a bus alias cross the hierarchy as one bus sheet pin
        `{ALIAS}`; inside each sheet the members keep local labels at their pins and one
        hierarchical label `{ALIAS}` on a bus stub carries them (CRAFT-84 groups, CRAFT-154)."""
        member = {m: a for a, ms in self.aliases.items() for m in ms}
        for s in self.sheets:
            s.bus_hier = getattr(s, "bus_hier", {})
            for p in s.points:
                a = member.get(p.net)
                if a and p.kind == "hier":
                    p.kind = "label"
                    s.bus_hier.setdefault(a, p)
            for cs in s.children:
                new, seen = [], {}
                for pin in cs.pins:
                    a = member.get(pin[0])
                    if not a:
                        new.append(pin)
                        continue
                    name = "{" + a + "}"
                    if name not in seen:
                        seen[name] = [name, "bidirectional", pin[2]]
                        new.append(seen[name])
                        cs.outer[name] = False
                        cs.shape_parent[name] = "bidirectional"
                    cs.outer[name] = cs.outer[name] or cs.outer.get(pin[0], False)
                cs.pins = new

    def pin_key(self, net):
        return self.order.get(net, (9999, natural(net)))

    # ------------------------------------------------------------------ sheet symbols
    def layout_children(self):
        """Size every sheet symbol from its pin names (CHAR mm per character): left and right
        names never meet, and top pins start right of the left names and of the sheet name, so a
        vertical pin, its name and the sheet's heading never overlap."""
        from draw import CHAR
        for s in self.sheets:
            for cs in s.children:
                left = [p for p in cs.pins if p[2] == "left"]
                right = [p for p in cs.pins if p[2] == "right"]
                top = [p for p in cs.pins if p[2] == "top"]
                gaps_l = dict(cs.sides.get("_gaps_left", {}))
                gaps_r = dict(cs.sides.get("_gaps_right", {}))
                outer = getattr(cs, "outer", {})
                for lst, gaps in ((left, gaps_l), (right, gaps_r)):
                    # a local label's text sits above its wire: a free row between it and a
                    # hierarchical label (centred on its wire) above it
                    for a, b in zip(lst, lst[1:]):
                        if outer.get(a[0]) and not outer.get(b[0]):
                            gaps[b[0]] = max(gaps.get(b[0], 0), 1)
                rows = max(len(left) + sum(gaps_l.values()), len(right) + sum(gaps_r.values()), 3)
                ln = max([len(p[0]) for p in left] or [0]) * CHAR
                rn = max([len(p[0]) for p in right] or [0]) * CHAR
                tn = max([len(p[0]) for p in top] or [0]) * CHAR
                title = len(cs.sheet.title) * CHAR
                off0 = snap(max(ln + 3.81, title + 3.81 if top else 0, 5.08))
                off = off0
                for p in top:
                    p.append(off)
                    off += 2.54
                last = off - 2.54 if top else 0
                w = max(ln + rn + 7.62, last + 2.54 + rn + 2.54, title + 2.54, cs.w or 0, 30.48)
                cs.w = snap(w + G / 2)
                for lst, gaps in ((left, gaps_l), (right, gaps_r)):
                    off = 2.54
                    for p in lst:
                        off += 2.54 * gaps.get(p[0], 0)
                        p.append(off)
                        off += 2.54
                h = max((rows + 1) * 2.54, tn + 5.08 if top else 0)
                cs.h = snap(max(h, 12.7))
                cs.ext = {  # space the outside stubs and labels take: left, right, top
                    "left": (len(left) and max(len(p[0]) for p in left) * CHAR + 3.81) or 0,
                    "right": (len(right) and max(len(p[0]) for p in right) * CHAR + 3.81) or 0,
                    "top": (len(top) and tn + 3.81) or 0,
                }

    def render_children(self, s):
        """Sheet symbols on sheet s, with a stub and a label (or a straight wire) per sheet pin."""
        ends = {}
        for cs in s.children:
            c = cs.sheet
            x, y, w, h = cs.x, cs.y, cs.w, cs.h
            out = [f"(sheet (at {n(x)} {n(y)}) (size {n(w)} {n(h)}) (exclude_from_sim no) (in_bom yes) (on_board yes) "
                   f"(dnp no) (fields_autoplaced yes) (stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0.0000)) "
                   f"(uuid {q(c.sheet_uuid)})",
                   f"  (property \"Sheetname\" {q(c.title)} (at {n(x)} {n(y - 0.7116)} 0) {eff(justify='left bottom')})",
                   f"  (property \"Sheetfile\" {q(c.name)} (at {n(x)} {n(y + h + 0.5884)} 0) {eff(justify='left top')})"]
            if c.block:
                out.append(f"  (property \"Block\" {q(c.block)} (at {n(x)} {n(y + h + 3.1284)} 0) {eff(justify='left top', hide=True)})")
            for net, shape, side, off in cs.pins:
                if side == "left":
                    px, py, a, j, d = x, y + off, 180, "left", (-1, 0)
                elif side == "top":
                    px, py, a, j, d = x + off, y, 90, "right", (0, -1)
                else:
                    px, py, a, j, d = x + w, y + off, 0, "right", (1, 0)
                out.append(f"  (pin {q(net)} {shape} (at {n(px)} {n(py)} {a}) {eff(justify=j)} "
                           f"(uuid {q(uid(c.name, 'sp', net))}))")
                ends.setdefault(net, []).append((px, py, d, cs))
            out.append(f"  (instances (project {q(PROJECT)} (path {q(s.inst_path)} (page {q(c.page)}))))")
            out.append(")")
            s.add("\n".join(out))
        own = {p.net for p in s.points}
        for net, lst in ends.items():
            if net.startswith("{"):
                self._render_bus(s, net, lst)
                continue
            direct = (len(lst) == 2 and net not in own and lst[0][1] == lst[1][1] and lst[0][2] != lst[1][2]
                      and not any(cs.outer.get(net) for _, _, _, cs in lst) and self._clear(s, lst))
            if direct:
                (x1, y1, _, _), (x2, y2, _, _) = lst
                s.wire((x1, y1), (x2, y2))
                continue
            for px, py, d, cs in lst:
                ex, ey = px + d[0] * 2.54, py + d[1] * 2.54
                s.wire((px, py), (ex, ey))
                dname = {(-1, 0): "left", (1, 0): "right", (0, -1): "up"}[d]
                if cs.outer.get(net):
                    s.hlabel_at(net, cs.shape_parent[net], ex, ey, dname)
                else:
                    s.label_at(net, ex, ey, dname)

    @staticmethod
    def _clear(s, lst):
        """Two facing sheet pins may be joined directly only if the route (a straight wire, or the
        bus's orthogonal dog-leg at the midpoint) meets no other sheet symbol with its outside
        labels, sheet name and file name."""
        (x1, y1, _, a), (x2, y2, _, b) = sorted(lst, key=lambda e: e[0])
        xm = snap((x1 + x2) / 2)
        segs = [((x1, y1), (x2, y2))] if y1 == y2 else [((x1, y1), (xm, y1)), ((xm, y1), (xm, y2)), ((xm, y2), (x2, y2))]
        for cs in s.children:
            if cs is a or cs is b:
                continue
            ext = getattr(cs, "ext", {"left": 0.0, "right": 0.0, "top": 0.0})
            rx0, ry0 = cs.x - ext["left"], cs.y - 3.81 - ext["top"]
            rx1, ry1 = cs.x + cs.w + ext["right"], cs.y + cs.h + 5.08
            for (ax, ay), (bx, by) in segs:
                if min(ax, bx) < rx1 and max(ax, bx) > rx0 and min(ay, by) <= ry1 and max(ay, by) >= ry0:
                    return False
        return True

    def _render_bus(self, s, net, lst):
        """A bus sheet pin: two ends on this sheet that face each other are joined by an
        orthogonal bus; otherwise each end takes a bus stub and a label (hierarchical where the
        bus leaves this sheet), and same-named bus labels join on the sheet."""
        if len(lst) == 2 and not any(cs.outer.get(net) for *_, cs in lst) and lst[0][2][0] != lst[1][2][0] \
                and lst[0][2][1] == 0 and lst[1][2][1] == 0 and self._clear(s, lst):
            (x1, y1, d1, _), (x2, y2, d2, _) = sorted(lst, key=lambda e: e[0])
            if d1 == (1, 0) and d2 == (-1, 0):
                xm = snap((x1 + x2) / 2)
                pts = [(x1, y1), (xm, y1), (xm, y2), (x2, y2)] if y1 != y2 else [(x1, y1), (x2, y2)]
                s.bus(*pts)
                return
        for px, py, d, cs in lst:
            ex, ey = px + d[0] * 5.08, py + d[1] * 5.08
            s.bus((px, py), (ex, ey))
            dname = {(-1, 0): "left", (1, 0): "right", (0, -1): "up"}[d]
            if cs.outer.get(net):
                s.hlabel_at(net, "bidirectional", ex, ey, dname)
            else:
                s.label_at(net, ex, ey, dname)

    # ------------------------------------------------------------------ files
    def stagger_labels(self, s):
        """A local label sits above its wire, a hierarchical label centred on it: a local label
        one 2.54 mm row below a hierarchical label in the same pin column would meet its text
        (CRAFT-175). The hierarchical label, and the run of hierarchical labels above it, moves
        up half a row on a short dogleg, which clears the local label below and keeps the row
        above clear (a local label's text sits above its own wire)."""
        key = lambda p: (round(p.x, 2), round(p.y, 2), p.direction)
        hier = {key(p): p for p in s.points if p.kind == "hier" and p.direction in ("left", "right")}
        local = {key(p) for p in s.points if p.kind != "hier" and p.direction in ("left", "right")}
        move = set()
        for k, h in hier.items():
            if (k[0], round(k[1] + 2.54, 2), k[2]) in local:
                y = k[1]
                while (k[0], round(y, 2), k[2]) in hier:
                    move.add((k[0], round(y, 2), k[2]))
                    y -= 2.54
        for k in sorted(move):  # a set: sort, so the output does not follow the hash seed
            p = hier[k]
            d = 1 if p.direction == "right" else -1
            x1 = p.x + d * 1.27
            s.wire((p.x, p.y), (x1, p.y), (x1, p.y - 1.27), (p.x + d * 2.54, p.y - 1.27))
            p.x, p.y = p.x + d * 2.54, p.y - 1.27

    def render(self, s):
        self.stagger_labels(s)
        for p in s.points:
            if p.kind == "hier":
                s.hlabel_at(p.net, p.shape, p.x, p.y, p.direction)
            else:
                s.label_at(p.net, p.x, p.y, p.direction)
        y_free = getattr(s, "tables_top", 200.0) - 5.08
        aliases = sorted(getattr(s, "bus_hier", {}))
        # group outlines with their titles: the bus ports never sit on one
        import re as _re
        rects = []
        for it in s.items:
            m = _re.match(r"\(rectangle \(start (\S+) (\S+)\) \(end (\S+) (\S+)\) \(stroke \(width 0\) \(type dash\)", it)
            if m:
                x0, y0, x1, y1 = map(float, m.groups())
                rects.append((x0 - 1.27, y0 - 5.08, x1 + 1.27, y1 + 1.27))

        def layout(per, low=0.0):
            out = []
            for i, alias in enumerate(aliases):
                out.append((45.72 + (i % per) * 30.48, snap(y_free + low - (i // per) * 7.62), "left") if per
                           else (45.72, snap(y_free + low - i * 5.08), "left"))
            return out

        def clear(pos):
            for alias, (x, y, _d) in zip(aliases, pos):
                box = (x - 2.54 - (len(alias) + 2) * 1.16, y - 1.27, x + 5.08, y + 1.27)
                if any(box[0] < r[2] and r[0] < box[2] and box[1] < r[3] and r[1] < box[3] for r in rects):
                    return False
            return True
        # a column above the interface table, clear of the circuit; rows when the column would
        # reach a group (or when the sheet asks for rows: bus_row)
        # a row may come one grid step lower, 1.27 mm clear of the table title, when a group's
        # outline reaches the usual height
        per = getattr(s, "bus_row", 0)
        tries = [(per, 0.0)] + [(alt, 0.0) for alt in (8, 6, 4)] + [(alt, 2.54) for alt in (8, 6, 4)]
        for alt, low in tries:
            pos = layout(alt, low)
            if clear(pos):
                break
        if aliases and not clear(pos):
            raise SystemExit(f"generator: {s.name}: no place for the bus ports clear of the groups")
        for i, alias in enumerate(aliases):
            x, y, d = getattr(s, "bus_ports", {}).get(alias, pos[i])
            dx, dy = {"left": (1, 0), "right": (-1, 0), "up": (0, 1), "down": (0, -1)}[d]
            s.bus((x, y), (x + dx * 5.08, y + dy * 5.08))
            s.hlabel_at("{" + alias + "}", "bidirectional", x, y, d)
        self.render_children(s)
        tb = [f"(title {q(s.title)})", f"(date {q(DATE)})", f"(rev {q(REV)})", f"(company {q(HOLDER)})",
              f"(comment 1 {q(s.role)})", f"(comment 2 {q(s.purpose)})"]
        out = ["(kicad_sch (version 20260306) (generator \"eeschema\") (generator_version \"10.0\")",
               f"(uuid {q(s.uuid)})", f"(paper {q(s.paper)})", "(title_block " + " ".join(tb) + ")",
               "(lib_symbols " + "\n".join(s.lib[k] for k in sorted(s.lib)) + ")"]
        out += [it.replace("@PATH@", q(s.inst_path)) for it in s.items]
        if s is self.root:
            out.append("(sheet_instances (path \"/\" (page \"1\")))")
        out.append("(embedded_fonts no))")
        return "\n".join(out) + "\n"

    def assign_paths(self):
        self.root.inst_path = "/" + self.root.uuid

        def walk(s):
            for cs in s.children:
                cs.sheet.inst_path = s.inst_path + "/" + cs.sheet.sheet_uuid
                walk(cs.sheet)
        walk(self.root)


def _label_at(self, net, x, y, direction):
    self.add(f"(label {q(net)} (at {n(x)} {n(y)} {LABEL_ANGLE[direction]}) "
             f"{eff(justify=LABEL_JUST[direction] + ' bottom')} (uuid {q(uid(self.name, 'l', net, x, y))}))")


def _hlabel_at(self, net, shape, x, y, direction):
    self.add(f"(hierarchical_label {q(net)} (shape {shape}) (at {n(x)} {n(y)} {LABEL_ANGLE[direction]}) "
             f"{eff(justify=LABEL_JUST[direction])} (uuid {q(uid(self.name, 'hl', net, x, y))}))")


Sheet.label_at = _label_at
Sheet.hlabel_at = _hlabel_at


# ---------------------------------------------------------------------- project file

ERC_ERRORS = ["endpoint_off_grid", "four_way_junction", "pin_not_connected", "label_dangling",
              "hier_label_mismatch", "power_pin_not_driven", "unresolved_variable", "unannotated",
              "duplicate_reference", "missing_power_pin", "multiple_net_names", "similar_labels",
              "similar_power", "similar_label_and_power", "same_local_global_label",
              "same_local_global_power", "no_connect_connected", "no_connect_dangling",
              "wire_dangling", "unconnected_wire_endpoint", "pin_not_driven", "undefined_netclass",
              "ground_pin_not_ground"]


def netclasses(toml_path, patterns):
    """Project net classes from hardware/rules/netclasses.toml, and their assignment patterns."""
    with open(toml_path, "rb") as fh:
        data = tomllib.load(fh)
    classes = []
    for i, c in enumerate(data.get("class", [])):
        k = {"name": c["name"], "priority": i, "schematic_color": "rgba(0, 0, 0, 0.000)",
             "pcb_color": "rgba(0, 0, 0, 0.000)"}
        if "width_outer_um" in c:
            w = c["width_outer_um"] / 1000.0
            if "differential_ohm" in c:
                k["diff_pair_width"] = w
                k["diff_pair_gap"] = c.get("gap_outer_um", 100.0) / 1000.0
            k["track_width"] = w
        classes.append(k)
    names = {c["name"] for c in classes}
    pats = []
    for cls, plist in patterns.items():
        if cls not in names:
            raise SystemExit(f"generator: pattern class {cls} is not in {toml_path}")
        for p in plist:
            pats.append({"netclass": cls, "pattern": p})
    return classes, pats


def project_file(classes, patterns, wks, aliases=None, base_variant="full"):
    sev = {k: "error" for k in ERC_ERRORS}
    sev.update({"lib_symbol_issues": "warning", "lib_symbol_mismatch": "warning", "footprint_link_issues": "warning",
                "footprint_filter": "ignore", "single_global_label": "warning", "isolated_pin_label": "warning",
                "missing_input_pin": "warning", "missing_bidi_pin": "warning", "missing_unit": "warning",
                "net_not_bus_member": "warning", "pin_to_pin": "warning", "simulation_model_issue": "ignore",
                "bus_definition_conflict": "error", "bus_entry_needed": "error", "bus_to_bus_conflict": "error",
                "bus_to_net_conflict": "error", "different_unit_footprint": "error", "different_unit_net": "error",
                "duplicate_sheet_names": "error", "extra_units": "error", "label_multiple_wires": "warning",
                "unit_value_mismatch": "error", "stacked_pin_name": "warning", "field_name_whitespace": "warning"})
    default = {"name": "Default", "priority": 2147483647, "wire_width": 6, "bus_width": 12, "clearance": 0.2,
               "track_width": 0.2, "via_diameter": 0.6, "via_drill": 0.3, "microvia_diameter": 0.3,
               "microvia_drill": 0.1, "diff_pair_width": 0.2, "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25,
               "line_style": 0, "pcb_color": "rgba(0, 0, 0, 0.000)", "schematic_color": "rgba(0, 0, 0, 0.000)"}
    fields = ("Manufacturer", "MPN", "Spec", "Block", "Constraints", "Manufacturer_2", "MPN_2", "Alternate",
              "Second_Source", "Checked")
    pro = {
        "meta": {"filename": PROJECT + ".kicad_pro", "version": 3},
        "erc": {"erc_exclusions": [], "meta": {"version": 0}, "rule_severities": sev},
        "schematic": {
            "page_layout_descr_file": wks,
            "connection_grid_size": 50.0,
            "annotate_start_num": 0,
            # unit notation ".A": a unit reads "U3501.System", not "U3501System" (kicad-lib craft standard §9.4)
            "subpart_id_separator": 46,
            "subpart_first_id": 65,
            "drawing": {"default_text_size": 50.0, "default_line_thickness": 6.0, "default_wire_thickness": 6.0,
                        "default_bus_thickness": 12.0, "default_junction_size": 40.0, "junction_size_choice": 3,
                        "label_size_ratio": 0.3, "pin_symbol_size": 25.0, "text_offset_ratio": 0.3,
                        "intersheets_ref_show": True, "intersheets_ref_short": False,
                        "intersheets_ref_prefix": "[", "intersheets_ref_suffix": "]",
                        "intersheets_ref_own_page": False,
                        "field_names": [{"name": f, "url": False, "visible": f == "Spec"} for f in fields]},
            "meta": {"version": 1},
            "bus_aliases": {k: list(v) for k, v in (aliases or {}).items()},
        },
        # The board is at its placement stage (pcb/, docs/specs/placement-v1.md): nothing is routed, so
        # KiCad's unconnected-items check reports every connection. It is a warning until routing
        # starts, so DRC errors stay the placement's own; the routing stage sets it back to error.
        "board": {"design_settings": {"rule_severities": {"unconnected_items": "warning"}}},
        "net_settings": {"classes": [default] + classes, "meta": {"version": 4}, "netclass_assignments": None,
                         "netclass_patterns": patterns},
        "text_variables": {"OPENDAP_PROJECT": "OpenDAP T1", "OPENDAP_BOARD": "main board",
                           "OPENDAP_LICENCE": "CERN-OHL-S-2.0", "OPENDAP_SOURCE": "github.com/opendap-project/board",
                           "OPENDAP_BASE_VARIANT": base_variant},
        "sheets": [],
        "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
    }
    return json.dumps(pro, indent=2) + "\n"


def _sym_table():
    rows = []
    for nick, (_path, kind) in library.LIBS.items():
        if kind == "opendap":
            uri, descr = f"${{KIPRJMOD}}/../lib/opendap/kicad/symbols/{nick}.kicad_sym", "kicad-lib"
        elif kind == "local":
            uri, descr = f"${{KIPRJMOD}}/../lib/symbols/{nick}.kicad_sym", "Project-only symbols, written by generator/"
        else:
            uri, descr = f"${{KICAD10_SYMBOL_DIR}}/{nick}.kicad_sym", "KiCad stock library"
        rows.append(f'  (lib (name "{nick}")(type "KiCad")(uri "{uri}")(options "")(descr "{descr}"))')
    return "(sym_lib_table\n  (version 7)\n" + "\n".join(rows) + "\n)\n"


# Footprint libraries: kicad-lib's, the project's, then KiCad's stock ones the parts use.
# every footprint library of the pinned kicad-lib, so a part added there needs no edit here
FP_OPENDAP = sorted(n[:-len(".pretty")] for n in os.listdir(os.path.join(library.KICAD_LIB, "footprints"))
                    if n.endswith(".pretty"))
FP_STOCK = ["Capacitor_SMD", "Resistor_SMD", "Inductor_SMD", "Crystal", "TestPoint", "NetTie", "Package_SON",
            "Package_TO_SOT_SMD", "Diode_SMD", "Fuse", "Button_Switch_SMD",
            "Fiducial"]   # board-only fiducials of the layout (pcb/plan.py, PCB-M-09)


def _fp_table():
    rows = [f'  (lib (name "{n}")(type "KiCad")(uri "${{KIPRJMOD}}/../lib/opendap/kicad/footprints/{n}.pretty")(options "")(descr "kicad-lib"))'
            for n in FP_OPENDAP]
    rows.append('  (lib (name "T1_Main_Board")(type "KiCad")(uri "${KIPRJMOD}/../lib/footprints/T1_Main_Board.pretty")'
                '(options "")(descr "Project-only footprints, written by generator/"))')
    rows += [f'  (lib (name "{n}")(type "KiCad")(uri "${{KICAD10_FOOTPRINT_DIR}}/{n}.pretty")(options "")(descr "KiCad stock library"))'
             for n in FP_STOCK]
    return "(fp_lib_table\n  (version 7)\n" + "\n".join(rows) + "\n)\n"


SYM_TABLE = _sym_table()
FP_TABLE = _fp_table()
