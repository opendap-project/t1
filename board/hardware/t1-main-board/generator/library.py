"""Symbol libraries the T1 schematic draws from: kicad-lib (the pinned submodule), KiCad's stock
libraries and the project-local library. Gives each symbol's embeddable text and its pin geometry."""

from __future__ import annotations

import math
import os

from sexpr import balanced, kid, kids, parse, val

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)                      # hardware/t1-main-board
HW = os.path.dirname(PROJECT)                        # hardware
KICAD_LIB = os.path.join(HW, "lib", "opendap", "kicad")  # libs submodule, kicad/ folder
LOCAL_LIB = os.path.join(HW, "lib", "symbols")
KICAD_APP = os.environ.get("KICAD_APP", "/Applications/KiCad/KiCad.app")
STOCK = os.environ.get("KICAD10_SYMBOL_DIR", os.path.join(KICAD_APP, "Contents", "SharedSupport", "symbols"))

# Library nickname -> (file, kind). kind: "opendap" (kicad-lib), "stock" (KiCad), "local" (project).
# every symbol library of the pinned kicad-lib, so a part added there needs no edit here
LIBS = {n[:-len(".kicad_sym")]: (os.path.join(KICAD_LIB, "symbols", n), "opendap")
        for n in sorted(os.listdir(os.path.join(KICAD_LIB, "symbols"))) if n.endswith(".kicad_sym")}
LIBS.update({
    "T1_Main_Board": (os.path.join(LOCAL_LIB, "T1_Main_Board.kicad_sym"), "local"),
    "Device": (os.path.join(STOCK, "Device.kicad_sym"), "stock"),
    "power": (os.path.join(STOCK, "power.kicad_sym"), "stock"),
    "Connector": (os.path.join(STOCK, "Connector.kicad_sym"), "stock"),
    "Mechanical": (os.path.join(STOCK, "Mechanical.kicad_sym"), "stock"),
    "Transistor_FET": (os.path.join(STOCK, "Transistor_FET.kicad_sym"), "stock"),
    "Diode": (os.path.join(STOCK, "Diode.kicad_sym"), "stock"),
    "Switch": (os.path.join(STOCK, "Switch.kicad_sym"), "stock"),
})


class Pin:
    __slots__ = ("unit", "number", "name", "etype", "x", "y", "angle", "length", "hidden")

    def __init__(self, unit, number, name, etype, x, y, angle, length, hidden):
        self.unit, self.number, self.name, self.etype = unit, number, name, etype
        self.x, self.y, self.angle, self.length, self.hidden = x, y, angle, length, hidden

    def side(self):
        """Side of the body the pin sits on, in symbol coordinates (angle points into the body)."""
        return {0: "left", 180: "right", 90: "bottom", 270: "top"}[int(self.angle) % 360]


class Symbol:
    def __init__(self, nick, name, text, node):
        self.nick, self.name, self.lib_id = nick, name, f"{nick}:{name}"
        self.text = text.replace(f'(symbol "{name}"', f'(symbol "{self.lib_id}"', 1)
        self.node = node
        self.props = {p[1]: p[2] for p in kids(node, "property")}
        self.power = kid(node, "power") is not None
        self.pins = []
        self.unit_names = {}
        self.bodies = {}
        for sub in kids(node, "symbol"):
            parts = sub[1].rsplit("_", 2)
            unit = int(parts[-2])
            un = val(sub, "unit_name")
            if un:
                self.unit_names[unit] = un
            for r in kids(sub, "rectangle"):
                s, e = kid(r, "start"), kid(r, "end")
                self.bodies.setdefault(unit, []).append((float(s[1]), float(s[2]), float(e[1]), float(e[2])))
            for p in kids(sub, "pin"):
                at = kid(p, "at")
                hidden = kid(p, "hide") is not None or "hide" in p
                self.pins.append(Pin(unit, kid(p, "number")[1], kid(p, "name")[1], p[1], float(at[1]),
                                     float(at[2]), float(at[3]) if len(at) > 3 else 0.0,
                                     float(val(p, "length", "2.54")), hidden))
        self.units = sorted({p.unit for p in self.pins if p.unit} or {1})

    def unit_pins(self, unit):
        return [p for p in self.pins if p.unit in (0, unit)]

    def pin(self, number, unit=None):
        for p in self.pins:
            if p.number == number and (unit is None or p.unit in (0, unit)):
                return p
        raise KeyError(f"{self.lib_id}: no pin {number}")

    def pins_named(self, name, unit=None):
        return [p for p in self.pins if p.name == name and (unit is None or p.unit in (0, unit))]

    def body(self, unit):
        """Bounding box (x0, y0, x1, y1) of the unit's body in symbol coordinates (y up)."""
        rects = self.bodies.get(unit) or self.bodies.get(0) or []
        if not rects:
            pts = [(p.x, p.y) for p in self.unit_pins(unit)] or [(0, 0)]
            xs, ys = [x for x, _ in pts], [y for _, y in pts]
            return min(xs), min(ys), max(xs), max(ys)
        xs = [v for r in rects for v in (r[0], r[2])]
        ys = [v for r in rects for v in (r[1], r[3])]
        return min(xs), min(ys), max(xs), max(ys)


_cache = {}
_texts = {}


def load(nick, name):
    key = (nick, name)
    if key in _cache:
        return _cache[key]
    path, _kind = LIBS[nick]
    if path not in _texts:
        with open(path, encoding="utf-8") as fh:
            _texts[path] = fh.read()
    t = _texts[path]
    # top-level symbols are indented by one tab in KiCad's writer
    i = -1
    for pre in ("\n\t(symbol ", "\n  (symbol ", "\n(symbol "):
        i = t.find(f'{pre}"{name}"')
        if i >= 0:
            i += len(pre) - len("(symbol ")
            break
    if i < 0:
        raise SystemExit(f"generator: {nick}:{name} not found in {path}")
    j = balanced(t, i)
    text = t[i:j]
    node = parse(text)
    ext = kid(node, "extends")
    if ext is not None:
        text, node = _flatten(nick, name, node, ext[1])
    sym = Symbol(nick, name, text, node)
    _cache[key] = sym
    return sym


def _flatten(nick, name, node, base_name):
    """A stock symbol that extends another (KiCad's derived symbols): the base's body and pins
    under this symbol's name, with this symbol's properties."""
    import re
    base = load(nick, base_name)
    text = base.text
    text = text.replace(f'(symbol "{base.lib_id}"', f'(symbol "{name}"', 1)
    text = re.sub(r'\(symbol "' + re.escape(base_name) + r'_(\d+)_(\d+)"', lambda m: f'(symbol "{name}_{m[1]}_{m[2]}"', text)
    for p in kids(node, "property"):
        k, v = p[1], p[2]
        esc = v.replace("\\", "\\\\").replace('"', '\\"')
        pat = re.compile(r'(\(property "' + re.escape(k) + r'" )"(?:[^"\\]|\\.)*"')
        if pat.search(text):
            text = pat.sub(lambda m: m.group(1) + '"' + esc + '"', text, count=1)
    return text, parse(text)


def reset_local():
    path = LIBS["T1_Main_Board"][0]
    _texts.pop(path, None)
    for k in [k for k in _cache if k[0] == "T1_Main_Board"]:
        del _cache[k]


def outward(pin, angle):
    """Unit vector (dx, dy) in schematic coordinates pointing away from the body at the pin end,
    for a symbol placed at rotation `angle` (degrees, counter-clockwise), not mirrored."""
    a = math.radians(pin.angle + 180)
    dx, dy = round(math.cos(a)), -round(math.sin(a))
    return rotate(dx, dy, angle)


def rotate(x, y, angle):
    """Rotate a schematic-coordinate vector by `angle` degrees counter-clockwise on screen."""
    for _ in range((int(angle) // 90) % 4):
        x, y = y, -x
    return x, y
