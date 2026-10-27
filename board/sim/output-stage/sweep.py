#!/usr/bin/env python3
"""Sweeps behind the README results (TPS65131 part).

Runs tps65131-dc-load.cir at each (input voltage, load, parameter stack) point by
rewriting its .param lines, and writes results/<sweep>.csv. Standard library only.

    python3 sweep.py margin       # §2 table: VIN x load x stack
    python3 sweep.py ceiling      # §2.4: load for 80 % and 100 % of 1.8 A
    python3 sweep.py calibration  # §2.2: max output current against SLVS493E Fig. 6-2/6-4
"""
import csv
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = open(os.path.join(HERE, "tps65131-dc-load.cir")).read()
JOBS = int(os.environ.get("JOBS", "2"))

STACKS = {
    "worst": dict(rp=0.30, rn=0.62, dcr=0.19, l0="3.76u", isat30=2.1, fs="1.25meg",
                  dis="7.5u", dn=1.18, drs=0.07),
    "typ": dict(rp=0.20, rn=0.44, dcr=0.16, l0="4.7u", isat30=2.4, fs="1.38meg",
                dis="8.4u", dn=1.09, drs=0.05),
}


def netlist(vin, iload, stack, ilim=10, ipos=None, r1="475k", r3="576k"):
    s = BASE
    p = dict(STACKS[stack])
    s = re.sub(r"^\.param vin=.*$", f".param vin={vin}", s, flags=re.M)
    s = re.sub(r"^\.param iload=.*$", f".param iload={iload}", s, flags=re.M)
    s = re.sub(r"^\.param ilim=.*$", f".param ilim={ilim}", s, flags=re.M)
    s = re.sub(r"^\.param rp=.*$", ".param " + " ".join(f"{k}={v}" for k, v in p.items()),
               s, flags=re.M)
    if ipos is not None:
        s = s.replace("ILP vpos 0 {iload}", f"ILP vpos 0 {ipos}")
    vpos = 1.213 * (1 + float(r1.rstrip("k")) / 100)
    vneg = -1.213 * float(r3.rstrip("k")) / 100
    s = s.replace("X1 vin vpos vneg ilp iln tps65131 params:",
                  f"X1 vin vpos vneg ilp iln tps65131 params: r1={r1} r3={r3}")
    s = s.replace(".ic v(vpos)=6.975 v(vneg)=-6.987", f".ic v(vpos)={vpos:.3f} v(vneg)={vneg:.3f}")
    return s


def run(tag, **kw):
    fn = os.path.join(HERE, f"_{tag}.cir")
    open(fn, "w").write(netlist(**kw))
    out = subprocess.run(["ngspice", "-b", fn], capture_output=True, text=True, cwd=HERE).stdout
    os.remove(fn)
    r = {m.group(1): float(m.group(2))
         for m in re.finditer(r"^(\w+)\s+=\s+([-\d.e+]+)", out, re.M)}
    return r


def sweep(points, name):
    def one(i_pt):
        i, pt = i_pt
        r = run(f"{name}_{i}", **pt)
        row = dict(pt)
        row.update({k: r.get(k) for k in ("iln_peak", "ilp_peak", "vneg_avg", "vpos_avg",
                                          "iln_avg", "vneg_pp", "vpos_pp", "iin")})
        if row["iln_peak"] is not None:
            row["inv_pct_of_1A8"] = round(row["iln_peak"] / 1.8 * 100, 1)
            row["boost_pct_of_1A8"] = round(row["ilp_peak"] / 1.8 * 100, 1)
        print(row, flush=True)
        return row
    with ThreadPoolExecutor(JOBS) as ex:
        rows = list(ex.map(one, enumerate(points)))
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", f"{name}.csv"), "w", newline="") as f:
        keys = []
        for row in rows:
            keys += [k for k in row if k not in keys]
        w = csv.DictWriter(f, fieldnames=keys, restval="")
        w.writeheader()
        w.writerows(rows)


def main(which):
    if which == "margin":
        pts = [dict(vin=v, iload=i, stack=s) for s in ("worst", "typ")
               for v in (3.0, 3.3, 3.5, 3.6, 3.7, 3.8, 3.9, 4.2, 4.5, 5.0)
               for i in (0.275, 0.288, 0.433, 0.465)]
        pts += [dict(vin=v, iload=0.30, ipos=0.52, stack=s) for s in ("worst", "typ")
                for v in (3.7, 3.8)]
        sweep(pts, "margin")
    elif which == "ceiling":
        pts = [dict(vin=v, iload=i, stack=s) for s in ("worst", "typ") for v in (3.7, 3.8)
               for i in (0.26, 0.30, 0.32, 0.34, 0.36, 0.38, 0.40, 0.42)]
        sweep(pts, "ceiling")
    elif which == "calibration":
        # inverter: load swept on the negative rail, 50 mA on the positive one
        pts = []
        for r3, loads in (("330k", (0.4, 0.5, 0.6, 0.65, 0.7, 0.75, 0.8)),
                          ("824k", (0.2, 0.25, 0.3, 0.33, 0.36, 0.39, 0.42))):
            for v in (3.0, 3.7, 4.5):
                pts += [dict(vin=v, iload=i, ipos=0.05, stack="typ", r3=r3) for i in loads]
        # boost: load swept on the positive rail, 50 mA on the negative one
        for r1, loads in (("312k", (0.6, 0.7, 0.8, 0.9, 1.0, 1.1)),
                          ("724k", (0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6))):
            for v in (3.0, 3.7):
                pts += [dict(vin=v, iload=0.05, ipos=i, stack="typ", r1=r1) for i in loads]
        sweep(pts, "calibration")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
