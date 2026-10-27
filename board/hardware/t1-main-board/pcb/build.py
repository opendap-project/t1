#!/usr/bin/env python3
"""Build the T1 main board's placement: t1-main-board.kicad_pcb from the schematic.

Run from anywhere with Python 3.11 or later (KiCad 10 installed):

    python3 hardware/t1-main-board/pcb/build.py            # board + placement-result.json
    python3 hardware/t1-main-board/pcb/build.py --drc      # and KiCad's DRC with the composed rules

Steps: export the netlist with kicad-cli; read every footprint's geometry with KiCad's Python
(fpgeom.py); take part heights from the 3D models (heights.py); place (placement.py, plan.py);
check what DRC does not (checks.py); write the board with KiCad's Python (kicad_write.py); report
the area budget and occupancy (occupancy.py) in placement-result.json. Nothing here is edited by
hand: change plan.py or the tools and run again. The same inputs give the same board.
Environment: KICAD_CLI and KICAD_PY override the KiCad 10 paths (macOS defaults below).
"""

from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys
import tempfile
import tomllib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import checks  # noqa: E402
import geometry as g  # noqa: E402
import heights as hmod  # noqa: E402
import netlist as nlmod  # noqa: E402
import occupancy  # noqa: E402
import placement  # noqa: E402
import plan  # noqa: E402
import zones  # noqa: E402

PROJECT = os.path.abspath(os.path.join(HERE, ".."))
BOARD_REPO = os.path.abspath(os.path.join(PROJECT, "..", ".."))
NAME = "t1-main-board"
SCH = os.path.join(PROJECT, NAME + ".kicad_sch")
PCB = os.path.join(PROJECT, NAME + ".kicad_pcb")
STACKUP = os.path.join(BOARD_REPO, "hardware", "stackup", "stackup-v3.toml")
RESULT = os.path.join(HERE, "placement-result.json")
KICAD_APP = "/Applications/KiCad/KiCad.app/Contents"
KICAD_CLI = os.environ.get("KICAD_CLI", KICAD_APP + "/MacOS/kicad-cli")
KICAD_PY = os.environ.get("KICAD_PY", KICAD_APP + "/Frameworks/Python.framework/Versions/Current/bin/python3")
ISSUE_DATE = os.environ.get("T1_ISSUE_DATE", "2026-10-27")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit("failed: " + " ".join(cmd[:3]))
    return r.stdout


# ------------------------------------------------------------------ stackup (stackup v3)

def stackup_spec():
    """KiCad stackup layers from hardware/stackup/stackup-v3.toml (stackup v3 §2)."""
    with open(STACKUP, "rb") as fh:
        st = tomllib.load(fh)
    cu_names = {"L1": "F.Cu", "L2": "In1.Cu", "L3": "In2.Cu", "L4": "In3.Cu", "L5": "In4.Cu", "L6": "B.Cu"}
    layers = [{"name": "F.SilkS", "type": "Top Silk Screen"}, {"name": "F.Paste", "type": "Top Solder Paste"}]
    nd = 0
    total = 0.0
    for L in st["layer"]:
        t = L["thickness_um"] / 1000.0
        total += t
        if L["type"] == "mask":
            top = L["name"].endswith("top")
            layers.append({"name": "F.Mask" if top else "B.Mask", "type": "Top Solder Mask" if top else "Bottom Solder Mask",
                           "thickness": t, "epsilon_r": L["er"]})
        elif L["type"] == "copper":
            layers.append({"name": cu_names[L["name"]], "type": "copper", "thickness": t})
        else:
            nd += 1
            core = L["name"].lower().startswith("core")
            layers.append({"name": "dielectric %d" % nd, "type": "core" if core else "prepreg", "thickness": t,
                           "material": L["material"].split(" (")[0][:40], "epsilon_r": L["er"]})
    layers += [{"name": "B.Paste", "type": "Bottom Solder Paste"}, {"name": "B.SilkS", "type": "Bottom Silk Screen"}]
    return {"layers": layers, "thickness": round(total, 4), "finish": "ENIG"}


# ------------------------------------------------------------------ spec

def rule_areas():
    out = []
    for z, r, layers in zones.rule_areas():
        out.append({"name": "ZONE_" + z, "rect": list(r), "layers": layers})
    for k, r in sorted(zones.corridors().items()):
        out.append({"name": "ZONE_CORRIDOR", "rect": list(r), "layers": zones.CU})
    out.append({"name": "BATTERY_POCKET", "rect": list(g.battery_pocket_area()), "layers": ["B.Cu"]})
    out.append({"name": "BATTERY_CONNECTOR", "rect": list(g.contact_window()), "layers": ["B.Cu"]})
    out.append({"name": "BATTERY_CONTACT_EMPTY", "rect": list(g.contact_empty()), "layers": ["B.Cu"]})
    out.append({"name": "BATTERY_ESD", "rect": list(g.contact_esd_area()), "layers": ["B.Cu"]})
    # analog audio (floorplan v1 §4 item 5): x < -6.2, y < -14
    out.append({"name": "AUDIO_ANALOG", "rect": [-g.HX, -g.HY, g.X_AUDIO, -14.0], "layers": zones.CU})
    sx, sy = 15.5 / 2 + 1.0, 14.4 / 2 + 1.0       # RK3566 body + 1 mm (as the floorplan study)
    out.append({"name": "BGA_ESCAPE", "rect": [plan.SOC[0] - sx, plan.SOC[1] - sy, plan.SOC[0] + sx, plan.SOC[1] + sy],
                "layers": zones.CU})
    return out


def drawings_and_texts():
    d, t = [], []
    d.append({"rect": list(g.DISP), "layer": "User.1"})
    t.append({"x": 0, "y": g.DISP[3] - 1.5, "text": "PCB-Z-03 front under the display: parts <= 1.0 mm", "layer": "User.1", "size": 0.8})
    d.append({"rect": list(g.FP), "layer": "User.1"})
    t.append({"x": 0, "y": g.FP[3] - 1.0, "text": "faceplate connection area: FH35C and its ESD only", "layer": "User.1", "size": 0.6})
    d.append({"rect": list(g.POCKET), "layer": "User.2"})
    t.append({"x": 0, "y": g.POCKET[3] - 1.5, "text": "PCB-Z-01 back under the pocket: parts <= 1.5 mm", "layer": "User.2", "size": 0.8})
    t.append({"x": 0, "y": -g.HY + 1.2, "text": "PCB-Z-02 bottom band <= 14.2 mm", "layer": "User.2", "size": 0.6})
    t.append({"x": 0, "y": g.HY - 1.2, "text": "PCB-Z-02 top band <= 14.2 mm", "layer": "User.2", "size": 0.6})
    d.append({"rect": list(g.SPEAKER), "layer": "User.2"})
    t.append({"x": (g.SPEAKER[0] + g.SPEAKER[2]) / 2, "y": g.SPEAKER[3] - 1.2, "text": "speaker body (BOM line 33)", "layer": "User.2", "size": 0.6})
    for z, r, layers in zones.rule_areas():
        if "F.Cu" in layers and (r[2] - r[0]) > 8 and (r[3] - r[1]) > 8:
            t.append({"x": (r[0] + r[2]) / 2, "y": (r[1] + r[3]) / 2, "text": z, "layer": "User.3", "size": 1.5})
    ir = plan.IDENTITY["rect"]
    for i, line in enumerate(plan.IDENTITY["lines"]):
        t.append({"x": (ir[0] + ir[2]) / 2, "y": ir[3] - 1.2 - 1.4 * i, "text": line, "layer": "B.SilkS",
                  "size": plan.IDENTITY["size"], "stroke": 0.15})
    return d, t


def footprint_specs(nl, placed, geom):
    out = []
    for ref in sorted(placed):
        p = placed[ref]
        c = nl.components[ref]
        fields = dict(c.fields)
        if ref in plan.THERMAL_HOT:
            fields["Thermal"] = "hot"
        if ref in plan.REWORK_BGA:
            fields["Rework"] = "BGA"
        if c.block == "blk.charger-battery" and c.ref.startswith("D") and any(
                nlmod.short(n).endswith(("BAT_MID", "BAT_NTC")) for n in c.nets):
            fields["ESD"] = "battery"
        ph = plan.PLACEHOLDER.get(c.footprint)
        if ph:
            fields["Placeholder"] = ph[1]
        sheet = c.sheet_names.rstrip("/").rsplit("/", 1)[-1] if c.sheet_names else ""
        out.append({"ref": ref, "fpid": c.footprint, "x": p.x, "y": p.y, "rot": p.rot, "side": p.side,
                    "value": c.value, "fields": fields, "path": c.path, "sheetname": sheet,
                    "sheetfile": c.sheet_file, "dnp": c.dnp, "pins": c.pins,
                    "exclude_bom": c.ref.startswith("TP"),
                    "placeholder": {"courtyard": list(ph[0])} if ph else None})
    for ref, x, y, side, kind in plan.FIDUCIALS:
        out.append({"ref": ref, "fpid": plan.FIDUCIAL_FP, "x": x, "y": y, "rot": 0, "side": side, "value": "Fiducial",
                    "fields": {}, "board_only": True, "exclude_bom": True, "fiducial": kind, "pins": {}})
    return out


# ------------------------------------------------------------------ main

def main():
    want_drc = "--drc" in sys.argv
    with tempfile.TemporaryDirectory() as tmp:
        net = os.path.join(tmp, NAME + ".net")
        run([KICAD_CLI, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", net, SCH])
        geom_path = os.path.join(tmp, "geom.json")
        run([KICAD_PY, os.path.join(HERE, "fpgeom.py"), net, geom_path, plan.FIDUCIAL_FP])
        with open(geom_path) as fh:
            geom = json.load(fh)
        nl = nlmod.load(net)
        for fpid, (cy, _) in plan.PLACEHOLDER.items():
            geom[fpid] = {"courtyard": list(cy), "pads": None, "holes": [], "pad_pos": {}, "pad_count": 0, "models": []}
        missing = sorted({c.footprint for c in nl.components.values() if geom.get(c.footprint) is None})
        if missing:
            raise SystemExit("footprints not found: " + ", ".join(missing))
        hts = {r: hmod.height(c.footprint, geom[c.footprint], c.fields.get("MPN", ""))[0]
               for r, c in nl.components.items()}
        placer = placement.Placer(nl, geom, hts)
        placed, failed = placer.run(placement.edge_rotations(nl, geom))

        spec = {"seed": 7, "copper_layers": 6, "stackup": stackup_spec(), "outline": [-g.HX, -g.HY, g.HX, g.HY],
                "title_block": {"title": "OpenDAP T1 main board", "revision": "A", "date": ISSUE_DATE,
                                "company": "The OpenDAP Project",
                                "comment1": "Placement stage: parts placed, not routed",
                                "comment2": "CERN-OHL-S-2.0"},
                "holes": [{"ref": "H%d" % i, "x": x, "y": y, "d": g.HOLE_D} for i, (x, y) in enumerate(g.HOLES, 1)],
                "rule_areas": rule_areas(), "footprints": footprint_specs(nl, placed, geom)}
        spec["drawings"], spec["texts"] = drawings_and_texts()
        spec_path = os.path.join(tmp, "spec.json")
        with open(spec_path, "w") as fh:
            json.dump(spec, fh)
        print(run([KICAD_PY, os.path.join(HERE, "kicad_write.py"), spec_path, PCB]).strip().splitlines()[-1])

    # checks and reports
    window = {r for r, c in nl.components.items() if c.footprint.startswith("KYOCERA_AVX:")}
    fixed = set(plan.FIXED) | window
    pl = {r: {"side": p.side, "zone": p.zone, "rect": p.rect, "zones": p.zones,
              "holes": placer.holes_at(r, p.x, p.y, p.side, p.rot)} for r, p in placed.items()}
    findings = checks.run(pl, hts, placer.zone_rects, exempt_zone=fixed, window_parts=window)
    budget = occupancy.floorplan_budget(nl, geom, hts, plan.FLOORPLAN_ZONE_OF_BLOCK, plan.FACEPLATE_REFS)
    occ = occupancy.placed_occupancy({r: (p.zone, p.side, p.rect) for r, p in placed.items()}, placer.zone_rects)
    sides = {"F": 0, "B": 0}
    for p in placed.values():
        sides[p.side] += 1
    result = {
        "parts": len(nl.components), "placed": len(placed), "failed": failed,
        "per_side": sides, "board_only": [f[0] for f in plan.FIDUCIALS] + ["H1", "H2", "H3", "H4"],
        "placeholders": sorted(r for r, c in nl.components.items() if c.footprint in plan.PLACEHOLDER),
        "checks": [list(f) for f in findings],
        "floorplan_budget_real_courtyards": budget,
        "placed_occupancy": occ,
        "zone_deltas": [{"zone": z, "rect": list(r), "layers": spec_ or "all", "reason": why}
                        for z, r, spec_, why in plan.ZONE_DELTAS],
        "block_moves": {b: {"zone": z, "reason": why} for b, (z, why) in plan.BLOCK_ZONE.items()},
        "converter_to_inductor_mm": converter_distances(nl, placed),
        "positions": {r: [p.x, p.y, p.rot, p.side, p.zone] for r, p in sorted(placed.items())},
    }
    if want_drc:
        result["drc"] = drc()
    with open(RESULT, "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("placed %d of %d parts (front %d, back %d), %d failed; %d check findings" % (
        len(placed), len(nl.components), sides["F"], sides["B"], len(failed), len(findings)))
    for f in findings:
        print("  check: %s %s: %s" % tuple(f))
    if want_drc:
        d = result["drc"]
        print("DRC: %d errors, %d warnings, %d unconnected" % (d["errors"], d["warnings"], d["unconnected"]))
    return 1 if failed else 0


def converter_distances(nl, placed):
    """Distance from each converter to its inductor, through the switch-node net (mm)."""
    res = {}
    for r, c in sorted(nl.components.items()):
        if not r.startswith("L") or r not in placed:
            continue
        for n in c.nets:
            if placement.is_switch_node(n):
                for o, _ in nl.nets.get(n, []):
                    if o != r and o.startswith("U") and o in placed:
                        a, b = placed[o], placed[r]
                        res[r] = {"converter": o, "mm": round(((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5, 2),
                                  "sides": a.side + b.side}
    return res


def drc():
    """KiCad's DRC with the composed rules; summary by type and rule."""
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "drc.json")
        subprocess.run([KICAD_CLI, "pcb", "drc", "--format", "json", "--severity-all", "-o", out, PCB],
                       capture_output=True, text=True)
        with open(out) as fh:
            d = json.load(fh)
    by = {}
    errors = warnings = 0
    for v in d.get("violations", []):
        sev = v.get("severity")
        errors += sev == "error"
        warnings += sev == "warning"
        desc = v.get("description", "")
        rule = desc.split("(rule '")[-1].split("'")[0] if "(rule '" in desc else ""
        key = "%s | %s | %s" % (sev, v.get("type"), rule)
        by[key] = by.get(key, 0) + 1
    return {"errors": errors, "warnings": warnings, "unconnected": len(d.get("unconnected_items", [])),
            "by_type": dict(sorted(by.items())),
            "schematic_parity": len(d.get("schematic_parity", []))}


if __name__ == "__main__":
    sys.exit(main())
