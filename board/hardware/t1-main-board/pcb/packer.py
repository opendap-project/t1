"""Occupancy grids and a nearest-free-spot search for courtyard rectangles (pure Python).

A side of the board is a grid of 0.05 mm cells (the CRAFT-30 placement grid) in the device frame;
each row is a Python int used as a bit set, so a rectangle test is one mask operation per row.
A part fits where its courtyard's cells are all inside the allowed mask of its region and none is
occupied. Courtyards are rounded outward to whole cells, so two placed courtyards at most touch
(KiCad 10.0.7 does not report touching courtyards: tested 2026-10-27 with two 0402s at zero gap).
"""

from __future__ import annotations

import math

RES = 0.05
GAP = 0.0


class Grid:
    def __init__(self, x0: float, y0: float, x1: float, y1: float, fill: bool = False):
        self.x0, self.y0 = x0, y0
        self.ncols = int(round((x1 - x0) / RES))
        self.nrows = int(round((y1 - y0) / RES))
        full = (1 << self.ncols) - 1
        self.rows = [full if fill else 0 for _ in range(self.nrows)]

    def copy(self) -> "Grid":
        g = Grid.__new__(Grid)
        g.x0, g.y0, g.ncols, g.nrows = self.x0, self.y0, self.ncols, self.nrows
        g.rows = list(self.rows)
        return g

    def cells(self, rect, grow: float = GAP):
        """Cell span (c0, c1, r0, r1), half-open, of a rectangle grown by `grow`, rounded outward.
        None when the rectangle leaves the grid."""
        x0, y0, x1, y1 = rect
        c0 = math.floor((x0 - grow - self.x0) / RES + 1e-9)
        c1 = math.ceil((x1 + grow - self.x0) / RES - 1e-9)
        r0 = math.floor((y0 - grow - self.y0) / RES + 1e-9)
        r1 = math.ceil((y1 + grow - self.y0) / RES - 1e-9)
        if c0 < 0 or r0 < 0 or c1 > self.ncols or r1 > self.nrows:
            return None
        return c0, c1, r0, r1

    def inner_cells(self, rect):
        """Cells wholly inside a rectangle (rounded inward)."""
        x0, y0, x1, y1 = rect
        c0 = max(0, math.ceil((x0 - self.x0) / RES - 1e-9))
        c1 = min(self.ncols, math.floor((x1 - self.x0) / RES + 1e-9))
        r0 = max(0, math.ceil((y0 - self.y0) / RES - 1e-9))
        r1 = min(self.nrows, math.floor((y1 - self.y0) / RES + 1e-9))
        return c0, c1, r0, r1

    @staticmethod
    def _mask(c0, c1):
        return ((1 << (c1 - c0)) - 1) << c0

    def set_rect(self, rect, value: bool = True, inner: bool = False, grow: float = GAP):
        span = self.inner_cells(rect) if inner else self.cells(rect, grow)
        if span is None:
            x0, y0, x1, y1 = rect
            span = self.inner_cells((x0 - grow, y0 - grow, x1 + grow, y1 + grow))
        c0, c1, r0, r1 = span
        if c1 <= c0 or r1 <= r0:
            return
        m = self._mask(c0, c1)
        for r in range(r0, r1):
            self.rows[r] = (self.rows[r] | m) if value else (self.rows[r] & ~m)

    def clear_disc(self, cx: float, cy: float, r: float):
        """Clear every cell that comes closer than r to (cx, cy)."""
        r0 = max(0, int(math.floor((cy - r - self.y0) / RES)))
        r1 = min(self.nrows, int(math.ceil((cy + r - self.y0) / RES)))
        for row in range(r0, r1):
            ya, yb = self.y0 + row * RES, self.y0 + (row + 1) * RES
            dy = 0.0 if ya <= cy <= yb else min(abs(ya - cy), abs(yb - cy))
            if dy >= r:
                continue
            hw = math.sqrt(r * r - dy * dy)
            c0 = max(0, int(math.floor((cx - hw - self.x0) / RES)))
            c1 = min(self.ncols, int(math.ceil((cx + hw - self.x0) / RES)))
            if c1 > c0:
                self.rows[row] &= ~self._mask(c0, c1)

    def any_set(self, span) -> bool:
        c0, c1, r0, r1 = span
        m = self._mask(c0, c1)
        rows = self.rows
        for r in range(r0, r1):
            if rows[r] & m:
                return True
        return False

    def all_set(self, span) -> bool:
        c0, c1, r0, r1 = span
        m = self._mask(c0, c1)
        rows = self.rows
        for r in range(r0, r1):
            if rows[r] & m != m:
                return False
        return True

    def count(self) -> int:
        return sum(bin(r).count("1") for r in self.rows)

    def area(self) -> float:
        return self.count() * RES * RES


def mask_from(x0, y0, x1, y1, include, exclude=()):
    """Allowed mask: the union of `include` rectangles (cells wholly inside) less `exclude`
    rectangles (cells touching them)."""
    g = Grid(x0, y0, x1, y1)
    for r in include:
        g.set_rect(r, True, inner=True)
    for r in exclude:
        g.set_rect(r, False, grow=0.0)
    return g


def offsets(r_max: float = 60.0):
    """Candidate offsets from a target, nearest first: 0.1 mm steps within 4 mm, 0.25 mm within
    12 mm, 0.5 mm beyond (all multiples of the 0.05 mm grid)."""
    pts = set()
    for step, lo, hi in ((0.1, 0.0, 4.0), (0.25, 4.0, 12.0), (0.5, 12.0, r_max)):
        n = int(hi / step) + 1
        for i in range(-n, n + 1):
            for j in range(-n, n + 1):
                d = math.hypot(i * step, j * step)
                if lo <= d <= hi:
                    pts.add((round(i * step, 2), round(j * step, 2)))
    return sorted(pts, key=lambda p: (round(math.hypot(*p), 4), p[1], p[0]))


def snap(v: float) -> float:
    return round(round(v / RES) * RES, 2)


# ---- footprint frame to device frame

def transform(lx: float, ly: float, side: str, rot: int):
    """A point of a footprint (KiCad local frame, y down, front, rotation 0) placed at the origin on
    `side` with orientation `rot` (degrees, KiCad's counter-clockwise on screen), as a device-frame
    offset (y up). Back side: as `build.py` places it (FOOTPRINT.Flip left-right, then
    SetOrientationDegrees(rot)), which reads as the local y mirrored, then rotated (checked against
    pcbnew by tests/test_kicad.py)."""
    if side == "B":
        ly = -ly
    a = math.radians(rot)
    c, s = round(math.cos(a)), round(math.sin(a))
    x = lx * c + ly * s
    y = -lx * s + ly * c
    return x, -y


def box(local, side: str, rot: int):
    """Device-frame bounding box offsets of a local box (x0, y0, x1, y1)."""
    xs, ys = [], []
    for lx in (local[0], local[2]):
        for ly in (local[1], local[3]):
            x, y = transform(lx, ly, side, rot)
            xs.append(x)
            ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def at(b, x, y):
    return (b[0] + x, b[1] + y, b[2] + x, b[3] + y)


# ---- feasibility maps: every grid position where a w x h block of cells is free

def _runs(row: int, w: int) -> int:
    """Bits i of `row` such that bits i .. i+w-1 are all set."""
    if w <= 1:
        return row
    res = None
    cur, span, shift = row, 1, 0
    powers = []
    while span <= w:
        powers.append((span, cur))
        cur = cur & (cur >> span)
        span *= 2
    rem = w
    for span, a in reversed(powers):
        if span <= rem:
            part = a >> shift
            res = part if res is None else (res & part)
            shift += span
            rem -= span
    return res


def feasible(free_rows, w: int, h: int):
    """Rows of bits marking top-left cells (column i, row r) of free w x h blocks."""
    rows = [_runs(r, w) for r in free_rows]
    n = len(rows)
    if h <= 1:
        return rows
    # vertical runs by doubling
    res = None
    cur, span, shift = rows, 1, 0
    powers = []
    while span <= h:
        powers.append((span, cur))
        cur = [cur[i] & cur[i + span] if i + span < n else 0 for i in range(n)]
        span *= 2
    rem = h
    for span, a in reversed(powers):
        if span <= rem:
            part = [a[i + shift] if i + shift < n else 0 for i in range(n)]
            res = part if res is None else [x & y for x, y in zip(res, part)]
            shift += span
            rem -= span
    return res


def nearest_bit(rows, c: int, r: int, max_cells: int):
    """The set bit nearest to (c, r) in cells, Euclidean, within max_cells; (col, row) or None."""
    best = None
    bestd = max_cells * max_cells + 1
    n = len(rows)
    for dr in range(0, max_cells + 1):
        if dr * dr >= bestd:
            break
        for rr in ((r - dr, r + dr) if dr else (r,)):
            if rr < 0 or rr >= n:
                continue
            row = rows[rr]
            if not row:
                continue
            cands = []
            if c >= 0:
                hi = row >> c
                if hi:
                    cands.append(c + ((hi & -hi).bit_length() - 1))
                lo = row & ((1 << c) - 1) if c > 0 else 0
                if lo:
                    cands.append(lo.bit_length() - 1)
            else:
                cands.append((row & -row).bit_length() - 1)
            for cc in cands:
                d = (cc - c) ** 2 + dr * dr
                if d < bestd:
                    bestd, best = d, (cc, rr)
    return best
