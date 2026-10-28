"""Capacitor proximity (PCB-P-07, PCB-P-10): every converter's input and output capacitors and every
IC's decoupling stand within a bound of the pins they serve (pure Python, Python 3.9 or later).

Which capacitor serves which pins comes from the netlist (pin functions and electrical types of the
symbols) and from the generator's `Decoupling` field:

- converter: a U part with a pin on a switch-node net (placement.is_switch_node). Its ground is the
  net of its GND-named pins (an inverting converter's ground is its negative rail). Input
  capacitors: two-pin capacitors between one of its supply-input nets (pins typed power_in that are
  not ground) and its ground. Output capacitors: two-pin capacitors between the far net of an
  inductor on its switch node and its ground; they serve the inductor's output pad and the
  converter's pins on that net.
- decoupling: any other two-pin capacitor to ground whose other net reaches a supply pin (power_in)
  or a regulator output pin (power_out) of an IC (U) of its own block; a capacitor the generator
  marks with a `Decoupling` field (the rail) and whose block has no such pin serves the rail's
  supply pins on the board (the SoC's banks). 10 µF and more is "bulk". Where one block has
  several ICs on the rail, its capacitors are placed with them in turn (owner), and each is checked
  against the nearest pin it serves.

Distance: from the capacitor's pad on the served net to the nearest served pad, centre to centre in
the board plane (either side: a via joins them). A capacitor passes when the distance is within its
role's bound (BOUNDS). The bound is a placement-stage bound, decided for the T1 on 2026-10-27; see
BOUNDS for its basis.
"""

from __future__ import annotations

import math

import netlist as nlmod

# role -> (bound in mm, basis). The data sheets of the T1's converters and ICs ask for the input
# capacitor "as close as possible" to its pins and show it adjacent in their layout examples
# (SLVSDV2 §12.1-12.2, SLVSES3A §10.1-10.2, SNVSAN3F §10.1-10.2, SBVS338H §7.4) without a number; PCB-P-07 asks for
# each data sheet's loop and PCB-P-10 for the smallest capacitor closest to its pin. The bounds turn
# that into a check: a hot-loop input capacitor at most one 0805 length plus a pad pitch from its
# pin (3 mm centre to centre), an output capacitor within the inductor-to-capacitor loop of the
# layout examples (5 mm), a decoupling capacitor next to its pin (4 mm), a bulk part of 10 µF or
# more in a decoupling bank one part further (6 mm).
BOUNDS = {
    "input": (3.0, "converter input, hot loop (PCB-P-07; data sheets: as close as possible)"),
    "output": (5.0, "converter output loop (PCB-P-07)"),
    "decoupling": (4.0, "IC decoupling (PCB-P-10)"),
    "bulk": (6.0, "bulk (>= 10 µF) in a decoupling bank (PCB-P-10)"),
}
GROUND_WORDS = ("GND", "VSS", "PGND", "AGND", "DGND", "EP")
_UNIT = {"pF": 1e-6, "nF": 1e-3, "µF": 1.0, "uF": 1.0}


def _func(c, pin):
    f = c.pin_info.get(pin, ("", ""))[0]
    return f.rsplit("_", 1)[0] if f.endswith("_" + pin) else f


def _is_ground_pin(c, pin):
    f = _func(c, pin).upper()
    return any(f == w or f.startswith(w) or f.endswith(w) for w in GROUND_WORDS)


def microfarads(value):
    num, _, unit = (value or "").partition(" ")
    try:
        return float(num) * _UNIT[unit]
    except (KeyError, ValueError):
        return None


def two_pin_caps(nl):
    return [c for c in nl.components.values()
            if c.ref.startswith("C") and len(c.pins) == 2 and len(set(c.pins.values())) == 2 and not c.dnp]


def converters(nl, is_switch_node):
    """ref -> {"ground": net, "inputs": set(nets), "outputs": {net: [(ref, pin), ...]}}"""
    out = {}
    for c in nl.components.values():
        if not c.ref.startswith("U") or not any(is_switch_node(n) for n in c.pins.values()):
            continue
        gnds = [n for p, n in c.pins.items() if _is_ground_pin(c, p)]
        if not gnds:
            continue
        ground = max(set(gnds), key=gnds.count)
        inputs = {n for p, n in c.pins.items() if c.pin_info.get(p, ("", ""))[1] == "power_in"
                  and not _is_ground_pin(c, p) and n != ground and not is_switch_node(n)}
        outputs = {}
        for sw in {n for n in c.pins.values() if is_switch_node(n)}:
            for lref, _ in nl.nets.get(sw, []):
                if not lref.startswith("L"):
                    continue
                for lp, ln in nl.components[lref].pins.items():
                    if ln != sw and not is_switch_node(ln):
                        served = [(lref, lp)] + [(c.ref, p) for p, n in c.pins.items() if n == ln]
                        outputs.setdefault(ln, []).extend(served)
        out[c.ref] = {"ground": ground, "inputs": inputs, "outputs": outputs}
    return out


def ic_pins(nl, net, block=None, types=("power_in",)):
    """(ref, pin) of the non-ground pins of ICs (U) on a net with one of the pin types, in a block
    when given."""
    res = []
    for ref, pin in nl.nets.get(net, []):
        c = nl.components.get(ref)
        if c is None or not ref.startswith("U") or (block and c.block != block):
            continue
        if c.pin_info.get(pin, ("", ""))[1] in types and not _is_ground_pin(c, pin):
            res.append((ref, pin))
    return res


def assignments(nl, is_switch_node):
    """Every checked capacitor: ref -> dict(role, net, pins (every pad it serves), owner (the IC it
    is placed with), owner_pins)."""
    conv = converters(nl, is_switch_node)
    res = {}
    caps = sorted(two_pin_caps(nl), key=lambda c: c.ref)
    for c in caps:
        nets = set(c.pins.values())
        for u, cv in sorted(conv.items()):
            if cv["ground"] not in nets or nl.components[u].block != c.block:
                continue
            other = (nets - {cv["ground"]}).pop()
            if other in cv["inputs"]:
                pins = [(u, p) for p, n in sorted(nl.components[u].pins.items()) if n == other]
                res[c.ref] = {"role": "input", "net": other, "pins": pins, "owner": u, "owner_pins": pins}
            elif other in cv["outputs"]:
                pins = cv["outputs"][other]
                res[c.ref] = {"role": "output", "net": other, "pins": pins, "owner": u,
                              "owner_pins": [q for q in pins if q[0].startswith("L")] or pins}
            if c.ref in res:
                break
    shared = {}
    for c in caps:
        if c.ref in res:
            continue
        shorts = {nlmod.short(n): n for n in c.pins.values()}
        if "GND" not in shorts:
            continue
        rail = [n for s, n in shorts.items() if s != "GND"][0]
        marked = c.fields.get("Decoupling")
        # the supply pins of the rail in the capacitor's block, and a regulator's output pin there;
        # a capacitor the generator marks as decoupling and whose block has no pin on the rail
        # serves the rail's supply pins on the board (the SoC's banks on blk.soc-power)
        pins = ic_pins(nl, rail, c.block, ("power_in", "power_out"))
        if not pins and marked:
            pins = ic_pins(nl, rail)
        if not pins:
            continue
        uf = microfarads(c.value)
        role = "bulk" if (uf is not None and uf >= 10.0) else "decoupling"
        res[c.ref] = {"role": role, "net": rail, "pins": pins}
        shared.setdefault((rail, c.block), []).append(c.ref)
    # several ICs on one rail in one block: the capacitors go to them in turn, by reference
    for (rail, _), refs in shared.items():
        ics = sorted({r for r, _ in res[refs[0]]["pins"]})
        for k, ref in enumerate(sorted(refs)):
            owner = ics[k % len(ics)]
            res[ref]["owner"] = owner
            res[ref]["owner_pins"] = [q for q in res[ref]["pins"] if q[0] == owner]
    return res


def check(nl, pad_xy, placed, is_switch_node, bounds=None):
    """Rows for every assigned capacitor: dict(ref, role, net, owner, mm, bound, ok, nearest).
    pad_xy(ref, pin) -> (x, y) of a placed pad; placed: the set of placed references."""
    bounds = bounds or BOUNDS
    rows = []
    for ref, a in sorted(assignments(nl, is_switch_node).items()):
        role, net, pins, owner = a["role"], a["net"], a["pins"], a["owner"]
        if ref not in placed:
            continue
        cpins = [p for p, n in nl.components[ref].pins.items() if n == net]
        best = None
        for cp in cpins:
            cx, cy = pad_xy(ref, cp)
            for r, p in pins:
                if r not in placed:
                    continue
                x, y = pad_xy(r, p)
                d = math.hypot(x - cx, y - cy)
                if best is None or d < best[0]:
                    best = (d, r, p)
        if best is None:
            continue
        b = bounds[role][0]
        rows.append({"ref": ref, "role": role, "net": nlmod.short(net), "owner": owner, "mm": round(best[0], 2),
                     "bound": b, "ok": best[0] <= b + 1e-9, "nearest": "%s.%s" % best[1:]})
    return rows
