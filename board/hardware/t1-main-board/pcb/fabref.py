"""Fabrication-layer reference texts: each one inside its own part's courtyard (CRAFT-11, placement v1).

A library footprint puts its `${REFERENCE}` fab text where the library drew it, often at a fixed
1 mm size beside the land (KiCad's test pads put it below the pad), so on a dense board it runs over
the next part's text. The board places it instead: centred on the courtyard, along the courtyard's
longer side, at the largest height up to MAX_H whose text fits the courtyard less MARGIN. Courtyards
do not overlap (DRC), so texts that stay inside their courtyards do not overlap either; `overlaps`
finds any pair that does, and the build stops on one.

Pure geometry, no pcbnew (kicad_write.py applies it and measures the drawn text): boxes are
(x0, y0, x1, y1) in millimetres. Keep it compatible with Python 3.9 (KiCad's Python).
"""

MAX_H = 1.0          # the library's fab reference size, kept where the part is large enough
MIN_H = 0.2          # smallest height written; a text that does not fit at it is reported
MARGIN = 0.05        # clear of the courtyard line on each side
CHAR_W = 0.8         # KiCad stroke font: advance per character, as a fraction of the height (estimate)
THICK = 0.15         # stroke as a fraction of the height: the libraries' 1.0 mm text at 0.15 mm


def text_box(x, y, angle, h, n):
    """Box of an n-character text of height h centred at (x, y), at 0 or 90 degrees."""
    w = n * CHAR_W * h
    hw, hh = (w / 2, h / 2) if angle % 180 == 0 else (h / 2, w / 2)
    return (x - hw, y - hh, x + hw, y + hh)


def fit(courtyard, n):
    """(x, y, angle, h) for an n-character reference inside the courtyard box."""
    x0, y0, x1, y1 = courtyard
    w, hgt = (x1 - x0) - 2 * MARGIN, (y1 - y0) - 2 * MARGIN
    n = max(n, 1)

    def height(along, across):
        return max(min(MAX_H, across, along / (n * CHAR_W)), 0.0)

    flat, upright = height(w, hgt), height(hgt, w)
    angle = 0 if flat >= upright else 90
    h = max(flat if angle == 0 else upright, MIN_H)
    return ((x0 + x1) / 2, (y0 + y1) / 2, angle, round(h, 3))


def inside(inner, outer, eps=1e-6):
    return (inner[0] >= outer[0] - eps and inner[1] >= outer[1] - eps
            and inner[2] <= outer[2] + eps and inner[3] <= outer[3] + eps)


def overlaps(items):
    """Pairs (a, b) of named boxes [(name, side, box)] on one side whose boxes intersect."""
    out = []
    items = sorted(items, key=lambda t: t[2][0])
    for i, (na, sa, a) in enumerate(items):
        for nb, sb, b in items[i + 1:]:
            if b[0] >= a[2]:
                break
            if sa == sb and a[1] < b[3] and b[1] < a[3]:
                out.append((na, nb))
    return out
