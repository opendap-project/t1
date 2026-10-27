#!/usr/bin/env python3
"""Compaction study of the T1 main board: evaluation matrices for lower and smaller parts.

Run from anywhere with Python 3.11 or later:

    python3 hardware/studies/compaction/compaction.py                 # matrices from candidates.toml
    python3 hardware/studies/compaction/compaction.py --netlist T1.NET  # and the per-part rows

Families, each checked against the design's stresses with the rules of candidates.toml [rules]:

- inductors: same inductance; height within the zone; design peak and the converter's maximum
  current limit against Isat (30 % drop, BRD-049 as the power tree applies it); continuous current
  against Irms; the XxL4020 land; DCR loss at the continuous current against the current part;
- capacitors over 1.0 mm: a thinner part of the same value, rating and dielectric; its lifecycle
  and sourcing outcome (T1-029); DC bias (DRV-107) is carried as stated;
- test pads (with --netlist): signal-net pads at the signal minimum, power and ground pads at the
  power minimum (PCB-D-06);
- 0201 decoupling (with --netlist): 100 nF on rails at most half the 0201 part's rating in the
  zones the rule allows.

A candidate's verdict is the worst of its gates: pass, conditional or fail. The chosen part of a
position is the lowest one that does not fail (then the lowest DCR); the current part stays when no
candidate is lower. Availability and cost are not here: `odapkit parts matrix` reads them, privately,
and this file carries only the outcome per part (`sourcing`).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tomllib

HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = {"pass": 0, "conditional": 1, "fail": 2}


def worst(*verdicts):
    return max(verdicts, key=lambda v: ORDER[v])


# ------------------------------------------------------------------ inductors

def inductor_rows(pos, parts, rules):
    """One row per part of the position's inductance (within 1 %)."""
    cur = parts[pos["current"]]
    rows = []
    for p in parts.values():
        if abs(p["l_uh"] - pos["l_uh"]) > 0.01 * pos["l_uh"]:
            continue
        peak = pos["peak_a"] / p["isat30_a"]
        limit = pos["limit_a"] / p["isat30_a"]
        rms = pos["continuous_a"] / p["irms_a"]
        gates = {
            "height": "pass" if p["h_mm"] <= rules["h_back"] else "fail",
            "peak": "pass" if peak <= rules["inductor_peak_max"] else "fail",
            "limit": "pass" if limit <= rules["inductor_limit_max"] else "fail",
            "irms": "pass" if rms <= rules["inductor_peak_max"] else "fail",
            "land": "pass" if p["land4020"] or p["mpn"] == cur["mpn"] else "conditional",
            "sourcing": p["sourcing"],
        }
        dcr_loss = None
        if "dcr_mohm" in p and "dcr_mohm" in cur:
            dcr_loss = round(pos["continuous_a"] ** 2 * (p["dcr_mohm"] - cur["dcr_mohm"]), 1)   # mW
        gate_v = worst(*(v for k, v in gates.items() if k != "height"))
        rows.append({"mpn": p["mpn"], "h_mm": p["h_mm"], "peak_pct": round(100 * peak), "limit_pct": round(100 * limit),
                     "irms_pct": round(100 * rms), "dcr_loss_mw": dcr_loss, "gates": gates,
                     "electrical": gate_v, "verdict": worst(*gates.values()), "current": p["mpn"] == cur["mpn"]})
    rows.sort(key=lambda r: (ORDER[r["verdict"]], r["h_mm"], r["dcr_loss_mw"] or 0, r["mpn"]))
    return rows


def choose_inductor(rows):
    """The lowest part that does not fail, then the lowest DCR; else the current part."""
    ok = [r for r in rows if r["verdict"] != "fail"]
    if ok:
        return min(ok, key=lambda r: (r["h_mm"], r["dcr_loss_mw"] or 0, r["mpn"]))["mpn"]
    return next(r["mpn"] for r in rows if r["current"])


# ------------------------------------------------------------------ capacitors over 1.0 mm

def mlcc_rows(pos, cands, rules):
    rows = []
    for c in cands:
        if c["replaces"] != pos["mpn"]:
            continue
        life = c["lifecycle"]
        gates = {
            "height": "pass" if c["h_mm"] <= rules["h_front"] else "fail",
            "lifecycle": "fail" if life in ("obsolete", "not recommended for new designs") else
                         ("pass" if life == "active" else "conditional"),
            "sourcing": c["sourcing"],
            "dc_bias": "pass" if c["dc_bias"] == "checked" else "conditional",
        }
        rows.append({"mpn": c["mpn"], "h_mm": c["h_mm"], "gates": gates, "verdict": worst(*gates.values())})
    rows.sort(key=lambda r: (ORDER[r["verdict"]], r["mpn"]))
    return rows


# ------------------------------------------------------------------ netlist rows

_XY = re.compile(r"\((?:start|end|center|xy) ([-0-9.]+) ([-0-9.]+)\)")


def _elements(text, head):
    """Top-level `(head ...)` elements of a footprint file, by matching parentheses."""
    out, i = [], 0
    while True:
        i = text.find("(" + head, i)
        if i < 0:
            return out
        depth, j = 0, i
        while j < len(text):
            depth += {"(": 1, ")": -1}.get(text[j], 0)
            j += 1
            if depth == 0:
                break
        out.append(text[i:j])
        i = j


def courtyard_area(path):
    """Area (mm2) of the bounding box of a footprint file's front courtyard."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    xs, ys = [], []
    for kind in ("fp_rect", "fp_circle", "fp_line", "fp_poly"):
        for el in _elements(text, kind + " ") + _elements(text, kind + "\n") + _elements(text, kind + "\t"):
            if '"F.CrtYd"' not in el:
                continue
            pts = [(float(a), float(b)) for a, b in _XY.findall(el)]
            if kind == "fp_circle" and len(pts) == 2:
                (cx, cy), (ex, ey) = pts
                r = ((ex - cx) ** 2 + (ey - cy) ** 2) ** 0.5
                pts = [(cx - r, cy - r), (cx + r, cy + r)]
            xs += [p[0] for p in pts]
            ys += [p[1] for p in pts]
    return (max(xs) - min(xs)) * (max(ys) - min(ys)) if xs else 0.0


def footprint_file(fpid, dirs):
    lib, name = fpid.split(":", 1)
    for d in dirs:
        p = os.path.join(d, lib + ".pretty", name + ".kicad_mod")
        if os.path.exists(p):
            return p
    return None


def netlist_rows(net_path, data, fp_dirs, zone_of_block, rails):
    """Test pads and 100 nF capacitors of the netlist, with their size gate and area."""
    sys.path.insert(0, os.path.join(HERE, "..", "..", "t1-main-board", "pcb"))
    import netlist as nlmod  # noqa: E402
    nl = nlmod.load(net_path)
    rules = data["rules"]
    area = {}

    def a(fpid):
        if fpid not in area:
            f = footprint_file(fpid, fp_dirs)
            area[fpid] = round(courtyard_area(f), 3) if f else None
        return area[fpid]

    tps, caps = [], []
    rule = data["c0201"][0]
    for ref, c in sorted(nl.components.items()):
        nets = sorted(nlmod.short(n) for n in c.nets)
        if ref.startswith("TP") and c.footprint.startswith(("TestPoint:TestPoint_Pad_D", "T1_Main_Board:TestPoint_Pad_D")):
            d = float(re.search(r"_D([0-9.]+)mm", c.footprint).group(1))
            power = any(n == "GND" or n in rails for n in nets)
            need = rules["tp_power_min"] if power else rules["tp_signal_min"]
            tps.append({"ref": ref, "net": nets[0] if nets else "", "power": power, "pad_mm": d,
                        "verdict": "pass" if d >= need else "fail", "area_mm2": a(c.footprint)})
        if c.fields.get("MPN") in (rule["from_mpn"], rule["to_mpn"]) and c.value == "100 nF":
            other = [n for n in nets if n != "GND"]
            zone = zone_of_block.get(c.block, "CORE")
            v = rails.get(other[0]) if len(other) == 1 and "GND" in nets else None
            ok = v is not None and zone in rule["zones"] and rules["mlcc_rating_min"] * v <= rule["rated_v"]
            caps.append({"ref": ref, "rail": other[0] if other else "", "zone": zone, "rail_v": v,
                         "eligible": ok, "mpn": c.fields.get("MPN"), "area_mm2": a(c.footprint)})
    return tps, caps


# ------------------------------------------------------------------ report

def evaluate(data):
    ind_parts = {p["mpn"]: p for p in data["inductor"]["part"]}
    out = {"inductors": [], "mlcc": []}
    for pos in data["inductor"]["position"]:
        rows = inductor_rows(pos, ind_parts, data["rules"])
        out["inductors"].append({"refs": pos["refs"], "converter": pos["converter"], "current": pos["current"],
                                 "chosen": choose_inductor(rows), "rows": rows})
    for pos in data["mlcc"]["position"]:
        rows = mlcc_rows(pos, data["mlcc"]["part"], data["rules"])
        ok = [r for r in rows if r["verdict"] == "pass"]
        out["mlcc"].append({"current": pos["mpn"], "value": pos["value"], "count": pos["count"],
                            "chosen": ok[0]["mpn"] if ok else pos["mpn"], "rows": rows})
    return out


def markdown(res):
    lines = ["| Position | Part | h (mm) | Peak / Isat30 | Limit / Isat30 | Irms use | DCR loss vs current (mW) | Sourcing | Verdict (under the pocket) |",
             "|---|---|---|---|---|---|---|---|---|"]
    for p in res["inductors"]:
        for r in p["rows"]:
            mark = " (current)" if r["current"] else ""
            pick = " **chosen**" if r["mpn"] == p["chosen"] else ""
            lines.append(f"| {', '.join(p['refs'])} {p['converter']} | {r['mpn']}{mark}{pick} | {r['h_mm']} | "
                         f"{r['peak_pct']} % | {r['limit_pct']} % | {r['irms_pct']} % | "
                         f"{'' if r['dcr_loss_mw'] is None else r['dcr_loss_mw']} | {r['gates']['sourcing']} | {r['verdict']} |")
    lines += ["", "| Capacitor (count) | Candidate | h (mm) | Lifecycle | Sourcing | DC bias | Verdict |", "|---|---|---|---|---|---|---|"]
    for p in res["mlcc"]:
        for r in p["rows"]:
            g = r["gates"]
            lines.append(f"| {p['current']} {p['value']} ({p['count']}) | {r['mpn']} | {r['h_mm']} | {g['lifecycle']} | "
                         f"{g['sourcing']} | {g['dc_bias']} | {r['verdict']} |")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--candidates", default=os.path.join(HERE, "candidates.toml"))
    ap.add_argument("--netlist", help="KiCad netlist (kicad-cli sch export netlist --format kicadsexpr)")
    ap.add_argument("--out", default=os.path.join(HERE, "compaction.result.json"))
    args = ap.parse_args(argv)
    with open(args.candidates, "rb") as fh:
        data = tomllib.load(fh)
    res = evaluate(data)
    if args.netlist:
        sys.path.insert(0, os.path.join(HERE, "..", "..", "t1-main-board", "pcb"))
        sys.path.insert(0, os.path.join(HERE, "..", "..", "t1-main-board", "generator"))
        import plan  # noqa: E402
        from parts import RAILS_0201  # noqa: E402
        from sch import RAILS  # noqa: E402
        rails = {r: None for r in RAILS}
        rails.update(RAILS_0201)
        fp_dirs = [os.environ.get("KICAD10_FOOTPRINT_DIR", "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"),
                   os.path.join(HERE, "..", "..", "lib", "footprints")]
        tps, caps = netlist_rows(args.netlist, data, fp_dirs, plan.ZONE_OF_BLOCK, rails)
        res["test_pads"] = {"count": len(tps), "fail": [t["ref"] for t in tps if t["verdict"] == "fail"],
                            "by_pad_mm": {str(d): sum(1 for t in tps if t["pad_mm"] == d) for d in sorted({t["pad_mm"] for t in tps})},
                            "area_mm2": round(sum(t["area_mm2"] or 0 for t in tps), 1)}
        res["c0201"] = {"eligible": sum(c["eligible"] for c in caps), "in_0201": sum(c["mpn"] == data["c0201"][0]["to_mpn"] for c in caps),
                        "eligible_not_0201": [c["ref"] for c in caps if c["eligible"] and c["mpn"] != data["c0201"][0]["to_mpn"]],
                        "area_mm2": round(sum(c["area_mm2"] or 0 for c in caps), 1)}
    with open(args.out, "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True, ensure_ascii=False)
        fh.write("\n")
    print(markdown(res))
    for k in ("test_pads", "c0201"):
        if k in res:
            print(k, json.dumps({a: b for a, b in res[k].items()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
