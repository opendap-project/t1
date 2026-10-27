#!/usr/bin/env python3
"""Find text that collides on the plotted schematic (CRAFT-175: fields and text never overlap a
symbol, wire or other text).

Reads the SVG plot KiCad makes of every sheet (`kicad-cli sch export svg`): KiCad draws each piece of
stroke text as a `<g class="stroked-text">` group of paths, so the true extent of every text is in
the file, and every other path is a line of the drawing (wires, buses, symbol bodies, pins, frames).
Reports, per sheet, each pair of texts whose boxes overlap and each text a line crosses.
It also reports clearances: any text within NC_CLEAR of a no-connect cross, a label, reference or
value within SYMBOL_CLEAR of a component outline, pin or cross (strokes told apart by the OpenDAP
theme's colours), and a group outline within GROUP_MARGIN of the frame.

    python3 hardware/t1-main-board/generator/overlaps.py [SVG_DIR]

With no SVG_DIR it plots the project into a temporary folder first (kicad-cli on PATH, or KiCad in
/Applications). Exit status 1 when anything collides. Standard library only.
"""

from __future__ import annotations

import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_SCH = os.path.join(os.path.dirname(HERE), "t1-main-board.kicad_sch")
NUM = re.compile(r"-?\d+(?:\.\d+)?")
SHRINK_TEXT = 0.0     # mm: boxes shrunk by this before text-text tests (stroke width, rounding)
SHRINK_LINE = 0.25     # mm: a line must enter a text box by this much to count
FRAME = 14.0           # mm: the drawing sheet's frame and zone band (nothing may reach it)
TB = (130.0, 32.0)     # mm: the drawing sheet's title block, in the lower right corner of the frame


def kicad_cli():
    return shutil.which("kicad-cli") or "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"


REF = re.compile(r"^[A-Z]{1,2}[0-9]{3,4}$")      # a reference: prefix and a hundred-block number


# OpenDAP colour theme (kicad-lib colour-themes/opendap.json): what a stroke colour draws
INK_SYMBOL = "#191C1F"     # component outlines and pins (also local labels' text, sheet boxes)
INK_NO_CONNECT = "#737C85"  # no-connect crosses
NC_CLEAR = 0.1             # mm: no text touches a no-connect cross (pin numbers included)
SYMBOL_CLEAR = 0.5         # mm: labels, references and values keep this from outlines, pins and crosses
STYLE = re.compile(r'<g style="([^"]*)"')


def parse(path, kinds=None):
    """(texts, segments): texts as (string, x0, y0, x1, y1); segments as (x0, y0, x1, y1). With
    kinds (a dict), also files the segments by what draws them: kinds["nc"] the no-connect crosses,
    kinds["symbol"] the component outlines and pins."""
    svg = open(path, encoding="utf-8").read()
    texts, segs = [], []
    pos = 0
    group = re.compile(r'<g class="stroked-text"><desc>(.*?)</desc>(.*?)</g>', re.S)
    path_re = re.compile(r'<path d="([^"]*)"')

    def lines(chunk):
        if kinds is None:
            _paths(chunk, path_re, segs)
            return
        # the stroke colour in force for each run of paths
        cuts = [(m.start(), m.group(1)) for m in STYLE.finditer(chunk)]
        starts = [0] + [c[0] for c in cuts] + [len(chunk)]
        styles = [kinds.get("_style", "")] + [c[1] for c in cuts]
        for i, st in enumerate(styles):
            part = []
            _paths(chunk[starts[i]:starts[i + 1]], path_re, part)
            segs.extend(part)
            ink = re.search(r"stroke:(#[0-9A-F]{6})", st)
            ink = ink.group(1) if ink and "stroke:none" not in st else None
            if ink == INK_NO_CONNECT:
                kinds.setdefault("nc", []).extend(part)
            elif ink == INK_SYMBOL:
                kinds.setdefault("symbol", []).extend(part)
        kinds["_style"] = styles[-1]
    for m in group.finditer(svg):
        lines(svg[pos:m.start()])
        pts = [float(v) for v in NUM.findall(" ".join(path_re.findall(m.group(2))))]
        if pts:
            xs, ys = pts[0::2], pts[1::2]
            texts.append((_unescape(m.group(1)), min(xs), min(ys), max(xs), max(ys)))
        pos = m.end()
    lines(svg[pos:])
    w, h = (float(v) for v in re.search(r'viewBox="0\.0000 0\.0000 ([\d.]+) ([\d.]+)"', svg).groups())
    return texts, segs, (w, h)


def _gap(box, s, n=16):
    """Distance from a text box to a segment, sampled along the segment."""
    x0, y0, x1, y1 = s
    best = 1e9
    for k in range(n + 1):
        x, y = x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n
        dx, dy = max(box[0] - x, 0.0, x - box[2]), max(box[1] - y, 0.0, y - box[3])
        best = min(best, (dx * dx + dy * dy) ** 0.5)
    return best


def _near(box, s, d):
    return not (max(s[0], s[2]) < box[0] - d or min(s[0], s[2]) > box[2] + d
                or max(s[1], s[3]) < box[1] - d or min(s[1], s[3]) > box[3] + d)


def clearances(texts, kinds, skip=()):
    """Texts too close to a no-connect cross (NC_CLEAR, every text) or, for labels, references and
    values, to a component outline, pin or cross (SYMBOL_CLEAR). Pin names (inside the body) and
    sheet names (KiCad sets them on the sheet box) are skipped."""
    found = []
    for t in texts:
        box = t[1:]
        nc = [s for s in kinds.get("nc", []) if _near(box, s, NC_CLEAR)]
        if any(_gap(box, s) < NC_CLEAR for s in nc):
            found.append(f"text '{t[0]}' touches a no-connect flag at ({box[0]:.1f}, {box[1]:.1f})")
            continue
        if t[0] in skip or (len(t[0]) <= 4 and t[0].replace("_", "").isalnum() and not REF.match(t[0])):
            continue
        near = [s for s in kinds.get("symbol", []) + kinds.get("nc", []) if _near(box, s, SYMBOL_CLEAR)]
        d = min([_gap(box, s) for s in near] + [9.0])
        if d < SYMBOL_CLEAR:
            found.append(f"text '{t[0]}' {d:.2f} mm from a symbol at ({box[0]:.1f}, {box[1]:.1f})")
    return found


def _unescape(s):
    return s.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&amp;", "&")


RECT = re.compile(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"')


def _paths(chunk, path_re, segs):
    # rectangles: group outlines (dashed), sheet symbols, table borders; the four edges
    for m in RECT.finditer(chunk):
        x, y, w, h = (float(v) for v in m.groups())
        if w > 0 and h > 0:
            segs += [(x, y, x + w, y), (x + w, y, x + w, y + h), (x, y + h, x + w, y + h), (x, y, x, y + h)]
    for d in path_re.findall(chunk):
        for sub in re.split(r"(?=M)", d):
            if "A" in sub:            # an arc (inductor turns): its chord, from the start to the end point
                nums = [float(v) for v in NUM.findall(sub)]
                if len(nums) >= 9:
                    segs.append((nums[0], nums[1], nums[-2], nums[-1]))
                continue
            pts = [float(v) for v in NUM.findall(sub)]
            for i in range(0, len(pts) - 3, 2):
                segs.append((pts[i], pts[i + 1], pts[i + 2], pts[i + 3]))


def _seg_hits_box(s, b):
    """True if segment s enters box b (axis-aligned segments only; others by sampling)."""
    x0, y0, x1, y1 = s
    bx0, by0, bx1, by1 = b
    if max(x0, x1) < bx0 or min(x0, x1) > bx1 or max(y0, y1) < by0 or min(y0, y1) > by1:
        return False
    if x0 == x1 or y0 == y1:
        return True
    for k in range(21):
        t = k / 20
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        if bx0 <= x <= bx1 and by0 <= y <= by1:
            return True
    return False


def _inside(x, y, box, eps=0.3):
    return box[0] + eps < x < box[2] - eps and box[1] + eps < y < box[3] - eps


def _outside(x, y, box, eps=0.3):
    return x < box[0] - eps or x > box[2] + eps or y < box[1] - eps or y > box[3] + eps


def frame_hits(texts, segs, w, h):
    """Drawing that reaches the frame's zone band or the title block (the drawing sheet's own
    lines and texts lie wholly in them): a text partly across the frame or the title block's
    edge, a line with one end inside the frame and one in the band, a line into the title block."""
    inner = (FRAME, FRAME, w - FRAME, h - FRAME)
    tb = (w - FRAME - TB[0], h - FRAME - TB[1], w - FRAME, h - FRAME)
    found = []
    for t in texts:
        box = t[1:]
        wholly_in = inner[0] <= box[0] and box[2] <= inner[2] and inner[1] <= box[1] and box[3] <= inner[3]
        wholly_out = box[2] <= inner[0] or box[0] >= inner[2] or box[3] <= inner[1] or box[1] >= inner[3] \
            or box[0] < inner[0] and box[2] < inner[0] + 4
        if not wholly_in and not wholly_out:
            found.append(f"text '{t[0]}' crosses the frame at ({box[0]:.1f}, {box[1]:.1f})")
        meets_tb = box[0] < tb[2] and box[2] > tb[0] and box[1] < tb[3] and box[3] > tb[1]
        in_tb = tb[0] <= box[0] and box[2] <= tb[2] and tb[1] <= box[1] and box[3] <= tb[3]
        if meets_tb and not in_tb:
            found.append(f"text '{t[0]}' crosses the title block at ({box[0]:.1f}, {box[1]:.1f})")
    for x0, y0, x1, y1 in segs:
        a_in, b_in = _inside(x0, y0, inner), _inside(x1, y1, inner)
        if a_in != b_in and (_outside(x0, y0, inner) or _outside(x1, y1, inner)):
            found.append(f"line crosses the frame at ({x0:.1f}, {y0:.1f})-({x1:.1f}, {y1:.1f})")
        a_tb, b_tb = _inside(x0, y0, tb), _inside(x1, y1, tb)
        if a_tb != b_tb and (_outside(x0, y0, tb) or _outside(x1, y1, tb)):
            found.append(f"line enters the title block at ({x0:.1f}, {y0:.1f})-({x1:.1f}, {y1:.1f})")
    return found


def check(path, skip=()):
    kinds = {}
    texts, segs, (w, h) = parse(path, kinds)
    edge = frame_hits(texts, segs, w, h)
    inside = [t for t in texts if FRAME < t[1] and t[3] < w - FRAME and FRAME < t[2] and t[4] < h - FRAME]
    # the title block (lower right) is the drawing sheet's own
    inside = [t for t in inside if not (t[1] > w - 14 - 131 and t[2] > h - 14 - 33)]
    # KiCad plots some texts twice (bold, highlighted): keep one of each
    seen, uniq = set(), []
    for t in inside:
        k = (t[0], round(t[1], 1), round(t[2], 1), round(t[3], 1), round(t[4], 1))
        if k not in seen:
            seen.add(k)
            uniq.append(t)
    inside = uniq
    found = []
    shr = SHRINK_TEXT
    for i, a in enumerate(inside):
        for b in inside[i + 1:]:
            if a[1] + shr < b[3] - shr and b[1] + shr < a[3] - shr and a[2] + shr < b[4] - shr and b[2] + shr < a[4] - shr:
                found.append(f"text '{a[0]}' overlaps text '{b[0]}' at ({a[1]:.1f}, {a[2]:.1f})")
    # lines: a text's own glyph strokes are not in segs; skip glyph-sized texts (pin numbers sit on pins)
    for t in inside:
        if len(t[0]) <= 4 and t[0].replace("_", "").isalnum() and not REF.match(t[0]):
            continue          # pin numbers sit on their own pin line by design (references are checked)
        # a line must cross the middle of the text, not graze its ascenders or descenders
        dx = SHRINK_LINE if t[3] - t[1] > t[4] - t[2] else (t[3] - t[1]) * 0.3
        dy = (t[4] - t[2]) * 0.3 if t[3] - t[1] > t[4] - t[2] else SHRINK_LINE
        box = (t[1] + dx, t[2] + dy, t[3] - dx, t[4] - dy)
        if box[0] >= box[2] or box[1] >= box[3]:
            continue
        for s in segs:
            if _seg_hits_box(s, box):
                found.append(f"line crosses text '{t[0]}' at ({t[1]:.1f}, {t[2]:.1f})")
                break
    return edge + found + clearances(inside, kinds, skip)


PAPER = {"A3": (420.0, 297.0), "A4": (297.0, 210.0)}
HEAD = 3.81            # mm: a group or table title above its top edge (2.54 mm text, 1.27 mm up)
GROUP_MARGIN = 3.81    # mm: a group outline keeps this from the frame (draw.Flow's right margin)


def _num(node, name):
    k = next((c for c in node[1:] if isinstance(c, list) and c and c[0] == name), None)
    return (float(k[1]), float(k[2])) if k else None


def _meet(a, b, eps=0.1):
    return a[0] + eps < b[2] and b[0] + eps < a[2] and a[1] + eps < b[3] and b[1] + eps < a[3]


def zones(path):
    """The sheet's zones from the .kicad_sch itself (CRAFT-170, -174): titled groups, tables and the
    notes box must not meet each other, the title block or the frame, and no symbol or label may sit
    in a table, the notes or the title block, or outside the frame."""
    sys.path.insert(0, HERE)
    from sexpr import parse as sparse
    root = sparse(open(path, encoding="utf-8").read())
    paper = next(c[1] for c in root[1:] if isinstance(c, list) and c[0] == "paper")
    w, h = PAPER[paper]
    inner = (FRAME, FRAME, w - FRAME, h - FRAME)
    tb = (w - FRAME - TB[0], h - FRAME - TB[1], w - FRAME, h - FRAME)
    boxes, anchors = [], []
    for c in root[1:]:
        if not isinstance(c, list) or not c:
            continue
        if c[0] == "rectangle" and "dash" in str(c):
            (x0, y0), (x1, y1) = _num(c, "start"), _num(c, "end")
            boxes.append(("group", (min(x0, x1), min(y0, y1) - HEAD, max(x0, x1), max(y0, y1))))
        elif c[0] == "table":
            cells = [k for k in c[1:] if isinstance(k, list) and k and k[0] == "cells"]
            pts = []
            for cell in (cells[0][1:] if cells else []):
                (x, y), (cw, ch) = _num(cell, "at"), _num(cell, "size")
                pts.append((x, y, x + cw, y + ch))
            if pts:
                boxes.append(("table", (min(p[0] for p in pts), min(p[1] for p in pts) - HEAD,
                                        max(p[2] for p in pts), max(p[3] for p in pts))))
        elif c[0] == "text_box":
            (x, y), (bw, bh) = _num(c, "at"), _num(c, "size")
            boxes.append(("notes", (x, y, x + bw, y + bh)))
        elif c[0] in ("symbol", "label", "hierarchical_label", "global_label", "sheet"):
            at = _num(c, "at")
            if at:
                name = c[1] if c[0] != "symbol" else next((k[2] for k in c[1:] if isinstance(k, list) and k[:2] == ["property", "Reference"]), "?")
                anchors.append((c[0], name, at))
    found = []
    for i, (ka, a) in enumerate(boxes):
        if not (inner[0] <= a[0] and a[2] <= inner[2] and inner[1] <= a[1] and a[3] <= inner[3]):
            found.append(f"{ka} at ({a[0]:.1f}, {a[1]:.1f}) reaches the frame")
        elif ka == "group" and min(a[0] - inner[0], inner[2] - a[2], a[1] - inner[1], inner[3] - a[3]) < GROUP_MARGIN - 0.01:
            found.append(f"group at ({a[0]:.1f}, {a[1]:.1f}) within {GROUP_MARGIN} mm of the frame")
        if _meet(a, tb):
            found.append(f"{ka} at ({a[0]:.1f}, {a[1]:.1f}) meets the title block")
        for kb, b in boxes[i + 1:]:
            if _meet(a, b):
                found.append(f"{ka} at ({a[0]:.1f}, {a[1]:.1f}) meets {kb} at ({b[0]:.1f}, {b[1]:.1f})")
    for kind, name, (x, y) in anchors:
        if not (inner[0] < x < inner[2] and inner[1] < y < inner[3]):
            found.append(f"{kind} {name} at ({x:.1f}, {y:.1f}) outside the frame")
        elif _meet((x, y, x, y), tb, eps=-0.01):
            found.append(f"{kind} {name} at ({x:.1f}, {y:.1f}) in the title block")
        for kb, b in boxes:
            if kb != "group" and b[0] < x < b[2] and b[1] < y < b[3]:
                found.append(f"{kind} {name} at ({x:.1f}, {y:.1f}) in the {kb}")
    return found


def main(argv):
    if len(argv) > 1:
        d = argv[1]
    else:
        d = tempfile.mkdtemp(prefix="t1-svg-")
        subprocess.run([kicad_cli(), "sch", "export", "svg", "--theme", "OpenDAP", "-o", d, ROOT_SCH],
                       check=True, capture_output=True)
    total = 0
    # sheet names: KiCad sets them on the sheet box, they are not the generator's to move
    names = set()
    for f in glob.glob(os.path.join(os.path.dirname(ROOT_SCH), "*.kicad_sch")):
        names.update(re.findall(r'\(property "Sheetname" "([^"]*)"', open(f, encoding="utf-8").read()))
    for f in sorted(glob.glob(os.path.join(d, "*.svg"))):
        found = check(f, names)
        if found:
            print(f"{os.path.basename(f)}: {len(found)}")
            for x in found:
                print("   ", x)
        total += len(found)
    for f in sorted(glob.glob(os.path.join(os.path.dirname(ROOT_SCH), "*.kicad_sch"))):
        found = zones(f)
        if found:
            print(f"{os.path.basename(f)}: {len(found)}")
            for x in found:
                print("   ", x)
        total += len(found)
    print(f"{total} collision(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
