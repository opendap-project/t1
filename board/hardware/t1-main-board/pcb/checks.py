"""Placement checks the DRC does not make (pure Python): courtyard overlaps among fixed parts,
height zones (PCB-Z-01 to Z-04, PCB-L-05), zone membership (PCB-S-16), hole rings (PCB-H-01, H-05)
and edge clearance (PCB-B-01) for every placed part. Each finding names its rule."""

from __future__ import annotations

import geometry as g
import zones as zmod


def _inside(r, rects, tol=1e-6):
    """True when r is covered by the union of rects (sampled on a 0.05 mm lattice of r's area)."""
    x0, y0, x1, y1 = r
    nx = max(2, int((x1 - x0) / 0.05) + 1)
    ny = max(2, int((y1 - y0) / 0.05) + 1)
    for i in range(nx):
        x = x0 + (x1 - x0) * i / (nx - 1)
        x = min(max(x, x0 + tol), x1 - tol)
        for j in range(ny):
            y = y0 + (y1 - y0) * j / (ny - 1)
            y = min(max(y, y0 + tol), y1 - tol)
            if not any(q[0] - tol <= x <= q[2] + tol and q[1] - tol <= y <= q[3] + tol for q in rects):
                return False
    return True


def height_limit(side, rect):
    """Lowest height limit over a rectangle on one side."""
    if side == "F":
        return g.H_FRONT_DISPLAY if zmod.intersect(rect, g.DISP) else g.H_FRONT_OUTSIDE
    if zmod.intersect(rect, g.POCKET):
        return g.H_BACK_POCKET
    return g.H_SHELF if zmod.intersect(rect, g.SPEAKER) else g.H_BACK_BAND


def run(placed, heights, zone_rects, exempt_zone=(), window_parts=()):
    """placed: ref -> dict(side, zone, rect). Returns a list of (rule, ref, detail)."""
    out = []
    by_side = {"F": [], "B": []}
    for ref, p in placed.items():
        by_side[p["side"]].append((ref, p["rect"]))
    for s, items in by_side.items():
        items.sort(key=lambda t: t[1][0])
        for i, (ra, a) in enumerate(items):
            for rb, b in items[i + 1:]:
                if b[0] >= a[2] - 1e-6:
                    break
                ov = zmod.intersect(a, b)
                if ov and (ov[2] - ov[0]) > 1e-4 and (ov[3] - ov[1]) > 1e-4:
                    out.append(("courtyard overlap", ra, "%s on %s" % (rb, s)))
    for ref, p in placed.items():      # through holes against the other side's courtyards
        other = "B" if p["side"] == "F" else "F"
        for hr in p.get("holes", ()):
            for rb, b in by_side[other]:
                ov = zmod.intersect(hr, b)
                if ov and (ov[2] - ov[0]) > 1e-4 and (ov[3] - ov[1]) > 1e-4:
                    out.append(("through hole under a part", ref, "%s on %s" % (rb, other)))
                    break
    for ref, p in placed.items():
        r, s, h = p["rect"], p["side"], heights[ref]
        lim = height_limit(s, r)
        if ref in window_parts and s == "B":
            lim = g.H_CONTACT_WINDOW
        if h is not None and h > lim + 1e-9:
            if s == "F":
                rule = "PCB-Z-03" if lim == g.H_FRONT_DISPLAY else "PCB-Z-04"
            elif ref in window_parts:
                rule = "PCB-L-05"
            elif zmod.intersect(r, g.POCKET):
                rule = "PCB-Z-01"
            else:
                rule = "PCB-Z-09" if zmod.intersect(r, g.SPEAKER) else "PCB-Z-02"
            out.append((rule, ref, "%.2f mm over a %.1f mm limit" % (h, lim)))
        if s == "F" and lim == g.H_FRONT_OUTSIDE and h > g.H_FRONT_DISPLAY:
            out.append(("PCB-Z-04 (UNVERIFIED value)", ref, "%.2f mm outside the display, on PCB-Z-04's 6.8 mm" % h))
        zs = p.get("zones") or (p["zone"],)
        if p["zone"] and ref not in exempt_zone and not _inside(r, [q for z in zs for q in zone_rects[z][s]]):
            out.append(("PCB-S-16 zone", ref, "courtyard leaves zone %s on %s" % ("/".join(zs), s)))
        ring_add = 3.0 if ref.startswith("C") else 1.4
        for hx, hy in g.HOLES:
            rr = g.HOLE_D / 2 + ring_add
            dx = max(r[0] - hx, 0, hx - r[2])
            dy = max(r[1] - hy, 0, hy - r[3])
            if (dx * dx + dy * dy) ** 0.5 < rr - 1e-6:
                out.append(("PCB-H-05" if ref.startswith("C") else "PCB-H-01", ref, "courtyard within %.1f mm of the hole edge" % ring_add))
        if not ref.startswith(("J", "SW")):
            e = g.B01_EDGE
            if r[0] < -g.HX + e - 1e-6 or r[2] > g.HX - e + 1e-6 or r[1] < -g.HY + e - 1e-6 or r[3] > g.HY - e + 1e-6:
                out.append(("PCB-B-01", ref, "courtyard within 0.3 mm of the edge"))
    return out
