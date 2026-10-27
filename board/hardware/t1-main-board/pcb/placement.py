"""Constructive placement of the T1 main board (pure Python).

Input: the netlist (netlist.py), each footprint's geometry (fpgeom.py's cache) and height
(heights.py), the plan (plan.py) and the board geometry (geometry.py). Output: a position, rotation
and side for every part, or the reason it found no room.

Method, in order: the fixed parts of the plan; the decoupling of the three BGAs on the front under
their ball fields, each capacitor at the nearest ball of its rail; then zone by zone the other
parts, largest first, each at the nearest free spot (0.05 mm grid, rotations 0/90/180/270, both
sides where its height allows) to the pads it connects to, or to its block's target when nothing it
connects to is placed yet. A spot is free when the part's courtyard lies inside its zone on that
side, inside the height area its height allows, off the mounting-hole rings (PCB-H-01, H-05 for
capacitors), 0.3 mm inside the edge (PCB-B-01; J* and SW* exempt), 2 mm from a BGA's courtyard
(PCB-D-01) and clear of every placed courtyard and of the through holes of the other side's parts.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import geometry as g
import netlist as nlmod
import packer
import plan
import zones

SIDES = ("F", "B")


@dataclass
class Placed:
    ref: str
    x: float
    y: float
    rot: int
    side: str
    zone: str
    rect: tuple            # device-frame courtyard
    zones: tuple = ()      # every zone the part may stand in (test pads: their nets' zones)


class Placer:
    def __init__(self, nl, geom: dict, heights: dict):
        self.nl = nl
        self.geom = geom
        self.h = heights               # ref -> height (mm)
        self.placed = {}
        self.failed = {}
        self.occ = {s: packer.Grid(-g.HX, -g.HY, g.HX, g.HY) for s in SIDES}
        self.bga_keep = {s: packer.Grid(-g.HX, -g.HY, g.HX, g.HY) for s in SIDES}
        self.zone_rects = self._zones()
        self._masks = {}
        self.offsets = packer.offsets()
        self.net_zones = self._net_zones()

    # ---------------------------------------------------------------- zones and masks
    def _zones(self):
        """zone -> side -> rects: the zones on the outer layer of each side (zones.py)."""
        zl = zones.zone_layer_rects()
        return {z: {s: list(zl[z][zones.SIDE_LAYER[s]]) for s in SIDES} for z in zl}

    def zone_of(self, c) -> str:
        if c.ref in plan.PART_ZONE:
            return plan.PART_ZONE[c.ref][0]
        if c.ref in plan.FACEPLATE_REFS:
            return "FACEPLATE"
        return plan.ZONE_OF_BLOCK.get(c.block, "CORE")

    def _net_zones(self):
        res = {}
        for c in self.nl.components.values():
            if c.ref.startswith("TP"):
                continue
            z = self.zone_of(c)
            for n in c.nets:
                res.setdefault(n, set()).add(z)
        return res

    def height_rects(self, side: str, h: float):
        """Rectangles where a part of height h may stand on a side."""
        if side == "F":
            # PCB-Z-04 (6.8 mm outside the display) is UNVERIFIED: the search keeps the front at
            # PCB-Z-03's 1.0 mm everywhere; a part uses Z-04 only as a fixed part of the plan
            return [(-g.HX, -g.HY, g.HX, g.HY)] if h <= g.H_FRONT_DISPLAY else []
        if h <= g.H_BACK_POCKET:
            return [(-g.HX, -g.HY, g.HX, g.HY)]
        if h <= g.H_BACK_BAND:
            return _subtract((-g.HX, -g.HY, g.HX, g.HY), g.POCKET)
        return []

    def mask(self, zones, side: str, h: float, edge_ok: bool, cap: bool):
        key = (tuple(sorted(zones)), side, h > g.H_FRONT_DISPLAY, h > g.H_BACK_POCKET, edge_ok, cap)
        if key in self._masks:
            return self._masks[key]
        inc = []
        hr = self.height_rects(side, h)
        for z in zones:
            for r in self.zone_rects[z][side]:
                for q in hr:
                    i = _intersect(r, q)
                    if i:
                        inc.append(i)
        m = packer.mask_from(-g.HX, -g.HY, g.HX, g.HY, inc)
        if not edge_ok:          # PCB-B-01: 0.3 mm from the edge (+0.05 for the edge line width)
            e = g.B01_EDGE + 0.05
            for r in ((-g.HX, -g.HY, g.HX, -g.HY + e), (-g.HX, g.HY - e, g.HX, g.HY),
                      (-g.HX, -g.HY, -g.HX + e, g.HY), (g.HX - e, -g.HY, g.HX, g.HY)):
                m.set_rect(r, False, grow=0.0)
        ring = g.HOLE_D / 2 + (g.H05_MLCC if cap else g.H01_RING)
        for hx, hy in g.HOLES:      # the ring around each hole (PCB-H-01, H-05 for capacitors)
            m.clear_disc(hx, hy, ring)
        if side == "B":             # the battery-contact window takes battery parts only (PCB-L-02, L-05)
            m.set_rect(g.contact_window(), False, grow=0.0)
            m.set_rect(g.SPEAKER, False, grow=0.0)
        self._masks[key] = m
        return m

    # ---------------------------------------------------------------- geometry of a part
    def local(self, ref):
        c = self.nl.components[ref]
        return self.geom[c.footprint]

    def rect_at(self, ref, x, y, side, rot):
        b = packer.box(self.local(ref)["courtyard"], side, rot)
        return packer.at(b, x, y)

    def holes_at(self, ref, x, y, side, rot):
        return [packer.at(packer.box(hb, side, rot), x, y) for hb in self.local(ref).get("holes", [])]

    def pad_xy(self, ref, pin):
        p = self.placed[ref]
        loc = self.local(ref)["pad_pos"].get(pin)
        if loc is None:
            return p.x, p.y
        dx, dy = packer.transform(loc[0], loc[1], p.side, p.rot)
        return p.x + dx, p.y + dy

    # ---------------------------------------------------------------- commit
    def commit(self, ref, x, y, rot, side, zone, zones_=()):
        r = self.rect_at(ref, x, y, side, rot)
        self.occ[side].set_rect(r)
        other = "B" if side == "F" else "F"
        for hr in self.holes_at(ref, x, y, side, rot):
            self.occ[other].set_rect(hr)
        if ref in plan.REWORK_BGA:
            d = g.D01_BGA
            self.bga_keep[side].set_rect((r[0] - d, r[1] - d, r[2] + d, r[3] + d))
        self.placed[ref] = Placed(ref, x, y, rot, side, zone, r, tuple(zones_) or (zone,))

    def fits(self, ref, x, y, side, rot, m):
        r = self.rect_at(ref, x, y, side, rot)
        span = self.occ[side].cells(r)
        if span is None or not m.all_set(span) or self.occ[side].any_set(span):
            return False
        if ref not in plan.REWORK_BGA and self.bga_keep[side].any_set(span):
            return False
        other = "B" if side == "F" else "F"
        for hr in self.holes_at(ref, x, y, side, rot):
            sp = self.occ[other].cells(hr)
            if sp is None or self.occ[other].any_set(sp):
                return False
        return True

    # ---------------------------------------------------------------- search
    def allowed_sides(self, ref):
        h = self.h[ref]
        if ref.startswith("TP"):
            # flat test pads on the front, for a single-sided fixture (ADR 0016, consequences);
            # contact pads of case parts are fixed parts of the plan (PART_TARGET)
            return ("F",)
        if ref in plan.THERMAL_HOT and h <= g.H_FRONT_DISPLAY:
            # PCB-L-01: no heat source on the back over the battery pocket; a hot part that the
            # front can take goes there (the SoC and the PMIC are fixed parts, ADR 0016)
            return ("F",)
        if h > g.H_FRONT_DISPLAY:
            return ("B",)
        return ("F", "B")

    def search(self, ref, target, sides, zones, rots=(0, 90, 180, 270), radius=60.0):
        """Nearest free spot to the target over the allowed sides and rotations (feasibility maps of
        the free cells, then the nearest feasible position; checked again with fits())."""
        h = self.h[ref]
        edge_ok = ref.startswith(plan.EDGE_OK)
        cap = ref.startswith("C")
        tx, ty = packer.snap(target[0]), packer.snap(target[1])
        best = None
        for s in sides:
            m = self.mask(zones, s, h, edge_ok, cap)
            occ = self.occ[s].rows
            keep = self.bga_keep[s].rows if ref not in plan.REWORK_BGA else None
            free = [a & ~o & ~k for a, o, k in zip(m.rows, occ, keep)] if keep else [a & ~o for a, o in zip(m.rows, occ)]
            shapes = {}
            for rot in rots:
                b = packer.box(self.local(ref)["courtyard"], s, rot)
                span = self.occ[s].cells(packer.at(b, tx, ty))
                if span is None:
                    span = _span_unclipped(self.occ[s], packer.at(b, tx, ty))
                c0, c1, r0, r1 = span
                w, hh = c1 - c0, r1 - r0
                if (w, hh) not in shapes:
                    shapes[(w, hh)] = packer.feasible(free, w, hh)
                feas = shapes[(w, hh)]
                # anchor cell of the target and the top-left offset of this rotation
                tc = int(round((tx - self.occ[s].x0) / packer.RES))
                tr = int(round((ty - self.occ[s].y0) / packer.RES))
                oc, orr = c0 - tc, r0 - tr
                lim = int(radius / packer.RES) if best is None else int(math.sqrt(best[0])) + 1
                hit = packer.nearest_bit(feas, tc + oc, tr + orr, lim)
                if hit is None:
                    continue
                cc, rr = hit
                x = packer.snap(self.occ[s].x0 + (cc - oc) * packer.RES)
                y = packer.snap(self.occ[s].y0 + (rr - orr) * packer.RES)
                d = (x - tx) ** 2 + (y - ty) ** 2
                if best is None or d < best[0] - 1e-9:
                    if self.fits(ref, x, y, s, rot, m):
                        best = (d, x, y, rot, s)
        if best is None:
            return None
        return best[1:]

    def target_of(self, ref):
        """Mean position of the placed pads this part's own pads connect to (weak nets left out
        unless they are all the part has), else its block's target."""
        c = self.nl.components[ref]
        # a converter's switch node pulls hardest: the part goes next to the placed pad of its
        # switch-node net (PCB-P-07, P-08: smallest switch-node copper)
        sw = []
        for pin, net in c.pins.items():
            if is_switch_node(net):
                sw += [self.pad_xy(o, op) for o, op in self.nl.nets.get(net, []) if o != ref and o in self.placed]
        if sw:
            return sum(p[0] for p in sw) / len(sw), sum(p[1] for p in sw) / len(sw)
        # pads of the part's own block first (a decoupling capacitor goes to its IC's pin, not to
        # the mean of a rail's pads over the board)
        own = []
        for pin, net in c.pins.items():
            if nlmod.short(net) == "GND":
                continue
            for oref, opin in self.nl.nets.get(net, []):
                if oref != ref and oref in self.placed and self.nl.components[oref].block == c.block:
                    own.append(self.pad_xy(oref, opin))
        if own:
            return sum(p[0] for p in own) / len(own), sum(p[1] for p in own) / len(own)
        pts = []
        for weak in (False, True):
            for pin, net in c.pins.items():
                short = nlmod.short(net)
                if (short in plan.WEAK_NETS) != weak:
                    continue
                for oref, opin in self.nl.nets.get(net, []):
                    if oref == ref or oref not in self.placed:
                        continue
                    pts.append(self.pad_xy(oref, opin))
            if pts:
                break
        if pts and len(pts) > 12:      # a net with many placed pads: take the nearest few to the block target
            bt = plan.TARGET.get(c.block)
            if bt:
                pts.sort(key=lambda p: math.hypot(p[0] - bt[0], p[1] - bt[1]))
                pts = pts[:6]
        if pts:
            return sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
        return plan.TARGET.get(c.block, (0.0, 0.0))

    # ---------------------------------------------------------------- stages
    def place_fixed(self, edge_rot):
        """edge_rot: ref -> (rotation, courtyard-centre x offset) for edge parts, from build.py."""
        for ref, (x, y, rot, side, _) in plan.FIXED.items():
            if ref not in self.nl.components:
                continue
            zone = self.zone_of(self.nl.components[ref])
            if isinstance(y, str):
                rot = edge_rot[ref]
                b = packer.box(self.local(ref)["courtyard"], side, rot)
                cx = (b[0] + b[2]) / 2
                if y == "edge:bottom":
                    yy = -g.HY - b[1]
                else:
                    yy = g.HY - b[3]
                x, y = packer.snap(x - cx), packer.snap(yy)
                # snapping must not push the courtyard past the edge
                while (y + b[1] < -g.HY - 1e-9) if 'bottom' in str(plan.FIXED[ref][1]) else (y + b[3] > g.HY + 1e-9):
                    y = round(y + (0.05 if 'bottom' in str(plan.FIXED[ref][1]) else -0.05), 2)
            self.commit(ref, x, y, rot, side, zone)
        # battery contacts, rotated 90 so the 7.0 mm pad runs along y (PCB-L-04)
        for c in sorted(self.nl.components.values(), key=lambda c: c.ref):
            if not c.footprint.startswith("kyocera-avx:"):
                continue
            net = nlmod.short(c.pins.get("1", ""))
            for key, slots in plan.CONTACT_ORDER.items():
                if net.endswith(key) and slots:
                    k = slots.pop(0)
                    self.commit(c.ref, g.contact_x(k), g.CONTACT_Y, 90, "B", "POWER")
                    break
            else:
                self.failed[c.ref] = "battery contact net %r not in the contact order" % net

    def place_part(self, ref, target=None, sides=None, zones=None, rots=(0, 90, 180, 270)):
        c = self.nl.components[ref]
        zone = self.zone_of(c)
        if zones is None:
            zones = [zone]
            if ref.startswith("TP"):
                own = set()
                for n in c.nets:
                    own |= self.net_zones.get(n, set())
                zones = sorted((own or {zone}) - {"FACEPLATE"}) or [zone]
        sides = sides or self.allowed_sides(ref)
        target = target or self.target_of(ref)
        res = self.search(ref, target, sides, zones, rots)
        if res is None:
            self.failed[ref] = "no room in %s on %s for %s (h %.2f mm)" % ("/".join(zones), "/".join(sides),
                                                                          c.footprint, self.h[ref])
            return False
        x, y, rot, s = res
        self.commit(ref, x, y, rot, s, zones[0] if len(zones) == 1 else self._zone_at(x, y, s, zones), zones)
        return True

    def _zone_at(self, x, y, side, zones):
        for z in zones:
            for r in self.zone_rects[z][side]:
                if r[0] <= x <= r[2] and r[1] <= y <= r[3]:
                    return z
        return zones[0]

    def place_under_bga(self):
        """BGA decoupling on the front under the ball field, each capacitor at the nearest ball of
        its rail (ADR 0016 item 3; escape study: one ground stack per capacitor next to a rail via)."""
        for block, bga in plan.UNDER_BGA.items():
            if bga not in self.placed:
                continue
            caps = [c for c in self.nl.components.values()
                    if c.block == block and c.ref.startswith("C") and "GND" in {nlmod.short(n) for n in c.nets}
                    and len(c.nets) == 2]
            # small capacitors first (closest to the balls), bulk after
            caps.sort(key=lambda c: (_area(self.local(c.ref)["courtyard"]), c.ref))
            balls = {}
            for pin, net in self.nl.components[bga].pins.items():
                balls.setdefault(net, []).append(pin)
            used = {}
            for c in caps:
                rail = [n for n in c.nets if nlmod.short(n) != "GND"][0]
                pins = balls.get(rail, [])
                if not pins:
                    self.place_part(c.ref, sides=("F",))
                    continue
                # spread the rail's capacitors over its balls
                k = used.get(rail, 0)
                used[rail] = k + 1
                pts = [self.pad_xy(bga, p) for p in sorted(pins)]
                pts.sort(key=lambda p: (p[1], p[0]))
                tgt = pts[(k * 7) % len(pts)] if len(pts) > 1 else pts[0]
                self.place_part(c.ref, target=tgt, sides=("F",))

    def reserve(self):
        """Board-only parts and areas the search keeps free: fiducials and the identity text."""
        k = plan.FIDUCIAL_KEEP / 2
        for ref, x, y, side, _ in plan.FIDUCIALS:
            self.occ[side].set_rect((x - k, y - k, x + k, y + k))
        self.occ[plan.IDENTITY["side"]].set_rect(plan.IDENTITY["rect"])

    def run(self, edge_rot):
        self.place_fixed(edge_rot)
        self.reserve()
        for ref, (tgt, side, _) in plan.PART_TARGET.items():
            if ref in self.nl.components:
                self.place_part(ref, target=tgt, sides=(side,))
        self.place_under_bga()
        # inductors whose switch node reaches a placed converter go next to it before anything else
        for c in sorted(self.nl.components.values(), key=lambda c: c.ref):
            if c.ref.startswith("L") and c.ref not in self.placed and any(
                    is_switch_node(n) and any(o in self.placed for o, _ in self.nl.nets.get(n, []) if o != c.ref)
                    for n in c.nets):
                self.place_part(c.ref)
        rest = [c for c in self.nl.components.values() if c.ref not in self.placed and c.ref not in self.failed]
        zone_order = ["CORE", "FACEPLATE", "AUDIO", "RADIO", "IO", "POWER"]

        def key(c):
            tp = c.ref.startswith("TP")
            h = self.h[c.ref]
            # tall parts first (bands), then parts with through holes (thermal vias need the other
            # side free under their exposed pad), then the converters' inductors, then back-only
            # parts, then the rest
            holes = bool(self.local(c.ref).get("holes"))
            ind = c.ref.startswith("L") and any(is_switch_node(n) for n in c.nets)
            hclass = (0 if h > g.H_BACK_POCKET else 0.5 if holes else
                      (1 if ind else (2 if h > g.H_FRONT_DISPLAY else 3)))
            return (tp, hclass, zone_order.index(self.zone_of(c)), -_area(self.local(c.ref)["courtyard"]), c.ref)

        # ICs and large parts of every zone first, so passives find the pads they serve
        # then the test pads (2.1 mm courtyards, flat, movable), then the small passives, which
        # fill the gaps nearest their pads
        big = [c for c in rest if not c.ref.startswith(("C", "R", "TP", "NT", "FB")) or
               _area(self.local(c.ref)["courtyard"]) > 6.0]
        tps = [c for c in rest if c.ref.startswith("TP") and c not in big]
        small = [c for c in rest if c not in big and c not in tps]
        for group in (big, tps, small):
            for c in sorted(group, key=key):
                self.place_part(c.ref)
        self.repair()
        return self.placed, self.failed

    def uncommit(self, ref):
        p = self.placed.pop(ref)
        self.occ[p.side].set_rect(p.rect, False)
        other = "B" if p.side == "F" else "F"
        for hr in self.holes_at(ref, p.x, p.y, p.side, p.rot):
            self.occ[other].set_rect(hr, False)
        return p

    def repair(self, max_victims=8):
        """Make room for a part that found none: move the nearest movable parts of its zone and
        side (searched, not fixed, <= 1.0 mm and without through holes, so they can also go to the
        other side), one more at a time, then place the part and the moved parts again; undo when a
        moved part finds no new place."""
        for ref in sorted(self.failed):
            c = self.nl.components[ref]
            zone = self.zone_of(c)
            sides = self.allowed_sides(ref)
            tgt = self.target_of(ref)
            cands = [p for p in self.placed.values() if p.side in sides and zone in p.zones
                     and p.ref not in plan.FIXED and p.ref not in plan.PART_TARGET and p.ref not in plan.REWORK_BGA
                     and self.h[p.ref] <= g.H_FRONT_DISPLAY and not self.local(p.ref).get("holes")]
            cands.sort(key=lambda p: ((p.x - tgt[0]) ** 2 + (p.y - tgt[1]) ** 2, p.ref))
            msg = self.failed.pop(ref)
            done = False
            for k in range(1, max_victims + 1):
                victims = cands[:k]
                olds = [self.uncommit(v.ref) for v in victims]
                ok = self.place_part(ref, target=tgt, sides=sides)
                if ok:
                    for v in olds:
                        if not self.place_part(v.ref, target=(v.x, v.y)):
                            ok = False
                            break
                if ok:
                    done = True
                    break
                for r in [ref] + [v.ref for v in olds]:
                    self.failed.pop(r, None)
                    if r in self.placed:
                        self.uncommit(r)
                for v in olds:
                    self.commit(v.ref, v.x, v.y, v.rot, v.side, v.zone, v.zones)
            if not done:
                self.failed[ref] = msg


def is_switch_node(net: str) -> bool:
    """A converter's switch node: named `*_SW`, or KiCad's automatic name from an `SW` pin
    (`Net-(U1201-SW)`, which the SW_NODE class pattern `*_SW` does not match)."""
    n = nlmod.short(net)
    return n.endswith("_SW") or n.endswith("-SW)")


def _span_unclipped(grid, rect):
    x0, y0, x1, y1 = rect
    c0 = math.floor((x0 - packer.GAP - grid.x0) / packer.RES + 1e-9)
    c1 = math.ceil((x1 + packer.GAP - grid.x0) / packer.RES - 1e-9)
    r0 = math.floor((y0 - packer.GAP - grid.y0) / packer.RES + 1e-9)
    r1 = math.ceil((y1 + packer.GAP - grid.y0) / packer.RES - 1e-9)
    return c0, c1, r0, r1


def _area(r):
    return (r[2] - r[0]) * (r[3] - r[1])


_intersect = zones.intersect
_subtract = zones.subtract


def edge_rotation(local: dict, side: str, edge: str) -> int:
    """The rotation that puts a connector's pad-free nose (its mouth) at the edge: the pads' mean
    lies farthest from the courtyard side that faces the edge (floorplan study's rule)."""
    best = None
    pads = list(local["pad_pos"].values()) or [[0.0, 0.0]]
    for rot in (0, 90, 180, 270):
        b = packer.box(local["courtyard"], side, rot)
        py = sum(packer.transform(p[0], p[1], side, rot)[1] for p in pads) / len(pads)
        score = (py - b[1]) if edge == "bottom" else (b[3] - py)
        if best is None or score > best[0] + 1e-9:
            best = (score, rot)
    return best[1]


def edge_rotations(nl, geom):
    res = {}
    for ref, (x, y, rot, side, _) in plan.FIXED.items():
        if isinstance(y, str) and ref in nl.components:
            res[ref] = edge_rotation(geom[nl.components[ref].footprint], side, y.split(":")[1])
    return res
