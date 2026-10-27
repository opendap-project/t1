"""Run the VSYS buck studies and print the result tables of README.md.

Usage (from this folder):
    uv run run.py step903      # TPS62903 5.1 V load steps (generic model)
    uv run run.py loop903      # TPS62903 loop gain (generic model)
    uv run run.py step136      # TPS62136 3.8 V load steps (TI model, needs models/)
    uv run run.py loop136      # TPS62136 loop gain (TI model, needs models/)
    uv run run.py check        # generic model with TPS62136 values (calibration)
    uv run run.py all
    uv run run.py --json step903 loop136   # one JSON document instead of the tables

--json prints {"schema": "opendap.sim-vsys-bucks/v1", "cases": [...]}, one case object per
line ("group" and "case" first, then the metrics in SI units: V, A, s, Hz, deg), so that
odapkit sim checks can match a case and a metric on one line. JOBS=n sets how many ngspice processes run at once (default 2). Results go to
results/ (ignored by git); a case whose .dat file exists is not run again.
"""

import concurrent.futures as cf
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RES = HERE / "results"

# ---------------------------------------------------------------- cases

STEP_T = (0.6e-3, 0.9e-3, 1.2e-3)  # step up, step down, end


def step903():
    cases = []
    for co in ("10u", "20u"):
        for vin in (6.0, 6.6, 8.8):
            cases.append((f"s903_v{vin}_c{co}", dict(VIN=vin, CO=co)))
    cases.append(("s903_v6.0_c10u_worst", dict(VIN=6.0, CO="10u", L="0.8u", RHS=0.111, ILIMH=4.0)))
    cases.append(("s903_v8.8_c10u_lmin", dict(VIN=8.8, CO="10u", L="0.8u")))
    cases.append(("s903_v7.4_c10u_fpwm", dict(VIN=7.4, CO="10u", PFM=0)))
    return [("tps62903-5v1-step.cir", n, p, (0.1, 1.6)) for n, p in cases]


def step136():
    cases = [
        ("s136_v6.0_pfm", dict(VIN=6.0, MODE=0)),
        ("s136_v8.8_pfm", dict(VIN=8.8, MODE=0)),
        ("s136_v7.4_fpwm", dict(VIN=7.4, MODE=2)),
        ("s136_v8.8_fpwm", dict(VIN=8.8, MODE=2)),
        ("s136_v4.6_pfm", dict(VIN=4.6, MODE=0)),  # low headroom, calibration only
    ]
    return [("tps62136-3v8-step.cir", n, p, (0.1, 2.0)) for n, p in cases]


def check_step():
    cases = [
        ("chk_v6.0_pfm", dict(VIN=6.0, PFM=1)),
        ("chk_v8.8_pfm", dict(VIN=8.8, PFM=1)),
        ("chk_v7.4_fpwm", dict(VIN=7.4, PFM=0)),
        ("chk_v8.8_fpwm", dict(VIN=8.8, PFM=0)),
        ("chk_v4.6_pfm", dict(VIN=4.6, PFM=1)),
    ]
    return [("generic-check-step.cir", n, p, (0.1, 2.0)) for n, p in cases]


def loop_cases(template, tag, vins, cos, freqs, tstart):
    out = []
    for vin in vins:
        for co in cos:
            for f in freqs:
                n = max(6, min(20, int(f / 10e3 * 5) + 5))
                p = dict(VIN=vin, CO=co, FINJ=f, TSTART=tstart, TSTOP=tstart + n / f)
                out.append((template, f"{tag}_v{vin}_c{co}_f{int(f / 1e3)}k", p, None))
    return out


GEN_F = [20e3, 30e3, 50e3, 70e3, 100e3, 150e3, 200e3, 300e3, 400e3]
TI_F = [10e3, 20e3, 30e3, 50e3, 70e3, 100e3, 150e3, 200e3, 250e3, 300e3]

GROUPS = {
    "step903": step903,
    "loop903": lambda: loop_cases("tps62903-5v1-loop.cir", "l903", (6.0, 8.8), ("10u", "20u"), GEN_F, 0.4e-3),
    "step136": step136,
    "loop136": lambda: loop_cases("tps62136-3v8-loop.cir", "l136", (6.0, 8.8), ("30u",), TI_F, 0.6e-3),
    "check": lambda: check_step()
    + loop_cases("generic-check-loop.cir", "lchk", (6.0, 8.8), ("30u",), TI_F, 0.4e-3),
}

# ---------------------------------------------------------------- running


def render(template, name, params):
    text = (HERE / template).read_text()
    m = re.search(r"^\.param (.*)$", text, re.M)
    defaults = dict(kv.split("=") for kv in m.group(1).split())
    defaults.update({k: str(v) for k, v in params.items()})
    text = text.replace(m.group(0), ".param " + " ".join(f"{k}={v}" for k, v in defaults.items()), 1)
    text = re.sub(r"^\.include (\S+)", lambda mm: f".include {HERE / mm.group(1)}", text, flags=re.M)
    text = re.sub(r"wrdata \S+\.dat", f"wrdata {RES / (name + '.dat')}", text)
    path = RES / f"{name}.cir"
    path.write_text(text)
    return path


def run_one(case):
    template, name, params, _ = case
    dat = RES / f"{name}.dat"
    if dat.exists():
        return name
    cir = render(template, name, params)
    with open(RES / f"{name}.log", "w") as log:
        subprocess.run(["ngspice", "-b", str(cir)], cwd=HERE, stdout=log, stderr=subprocess.STDOUT, check=False)
    return name


# ---------------------------------------------------------------- analysis


def load(path):
    with open(path) as fh:
        head = [h.lower() for h in fh.readline().split()]
    data = np.loadtxt(path, skiprows=1)
    return {h: data[:, i] for i, h in enumerate(head)}


def step_metrics(path, band=0.005):
    t_up, t_dn, t_end = STEP_T
    d = load(path)
    t, v = d["time"], d["v(vout)"]
    il = d[[k for k in d if k.startswith("i(")][0]]
    win = lambda a, b: (t >= a) & (t < b)
    k = max(1, int(round(1e-6 / (t[1] - t[0]))))
    vf = np.convolve(v, np.ones(k) / k, mode="same")  # 1 us average: removes the ripple

    def settle(t0, t1, target):
        m = win(t0, t1 - 3e-6)
        out = np.abs(vf[m] - target) > band * target
        return 0.0 if not out.any() else t[m][np.where(out)[0][-1]] - t0

    lo, hi = win(t_up - 50e-6, t_up), win(t_dn - 50e-6, t_dn)
    v_lo, v_hi = v[lo].mean(), v[hi].mean()
    return dict(
        v_lo=v_lo, v_hi=v_hi,
        v_min=v[win(t_up, t_dn)].min(), v_max=v[win(t_dn, t_end)].max(),
        rip_lo=np.ptp(v[lo]), rip_hi=np.ptp(v[hi]),
        ts_up=settle(t_up, t_dn, v_hi), ts_dn=settle(t_dn, t_end, v_lo),
        il_pk=il[win(t_up, t_dn)].max(), il_ss=il[hi].max(),
    )


def loop_point(path, f, t0, t1, skip=2):
    d = load(path)
    t, vo, vs = d["time"], d["v(vout)"], d["v(vs)"]
    n = int(round((t1 - t0) * f))
    m = (t >= t0 + skip / f) & (t < t0 + n / f)
    ph = np.exp(-2j * np.pi * f * t[m])
    c = lambda x: np.trapezoid((x[m] - x[m].mean()) * ph, t[m])
    T = -c(vo) / c(vs)  # loop gain: injection + side at the sense node
    return 20 * math.log10(abs(T)), math.degrees(math.atan2(T.imag, T.real))


def step_rows(group, cases):
    rows = []
    for _, name, _, _ in cases:
        p = RES / f"{name}.dat"
        if not p.exists():
            rows.append(dict(group=group, case=name, missing=True))
            continue
        r = step_metrics(p)
        rows.append(dict(
            group=group, case=name,
            v_lo_v=r["v_lo"], v_hi_v=r["v_hi"], v_min_v=r["v_min"], v_max_v=r["v_max"],
            undershoot_v=r["v_hi"] - r["v_min"], overshoot_v=r["v_max"] - r["v_hi"],
            ripple_lo_v=r["rip_lo"], ripple_hi_v=r["rip_hi"],
            settle_up_s=r["ts_up"], settle_down_s=r["ts_dn"],
            il_pk_a=r["il_pk"], il_ss_a=r["il_ss"],
        ))
    return rows


def loop_rows(group, cases):
    pts = {}
    for _, name, p, _ in cases:
        key = name.rsplit("_f", 1)[0]
        path = RES / f"{name}.dat"
        if path.exists():
            pts.setdefault(key, []).append((p["FINJ"], *loop_point(path, p["FINJ"], p["TSTART"], p["TSTOP"])))
    rows = []
    for key, pp in pts.items():
        pp.sort()
        row = dict(group=group, case=key, crossover_hz=None, phase_margin_deg=None,
                   points=[dict(f_hz=f, gain_db=g, phase_deg=ph) for f, g, ph in pp])
        for (f1, g1, p1), (f2, g2, p2) in zip(pp, pp[1:]):
            if g1 > 0 >= g2:
                fc = f1 * (f2 / f1) ** (g1 / (g1 - g2))
                pc = p1 + (p2 - p1) * math.log(fc / f1) / math.log(f2 / f1)
                row["crossover_hz"], row["phase_margin_deg"] = fc, 180 + pc
                break
        rows.append(row)
    return rows


def print_steps(cases):
    print(f"{'case':24s} {'Vlo':>6s} {'Vhi':>6s} {'Vmin':>6s} {'Vmax':>6s} {'under mV':>8s} {'over mV':>8s} {'rip lo':>7s} {'rip hi':>7s}"
          f" {'ts up us':>8s} {'ts dn us':>8s} {'IL pk':>6s} {'IL ss':>6s}")
    for _, name, _, (ilo, ihi) in cases:
        p = RES / f"{name}.dat"
        if not p.exists():
            print(f"{name:24s} missing")
            continue
        r = step_metrics(p)
        print(f"{name:24s} {r['v_lo']:6.3f} {r['v_hi']:6.3f} {r['v_min']:6.3f} {r['v_max']:6.3f}"
              f" {(r['v_hi'] - r['v_min']) * 1e3:8.1f} {(r['v_max'] - r['v_hi']) * 1e3:8.1f} {r['rip_lo'] * 1e3:7.1f} {r['rip_hi'] * 1e3:7.1f}"
              f" {r['ts_up'] * 1e6:8.1f} {r['ts_dn'] * 1e6:8.1f} {r['il_pk']:6.2f} {r['il_ss']:6.2f}")


def print_loops(cases):
    rows = {}
    for _, name, p, _ in cases:
        key = name.rsplit("_f", 1)[0]
        path = RES / f"{name}.dat"
        if path.exists():
            rows.setdefault(key, []).append((p["FINJ"], *loop_point(path, p["FINJ"], p["TSTART"], p["TSTOP"])))
    for key, pts in rows.items():
        pts.sort()
        print(f"== {key}")
        for f, g, ph in pts:
            print(f"   {f / 1e3:6.0f} kHz  {g:7.2f} dB  {ph:8.1f} deg")
        for (f1, g1, p1), (f2, g2, p2) in zip(pts, pts[1:]):
            if g1 > 0 >= g2:
                fc = f1 * (f2 / f1) ** (g1 / (g1 - g2))
                pc = p1 + (p2 - p1) * math.log(fc / f1) / math.log(f2 / f1)
                print(f"   crossover {fc / 1e3:.0f} kHz, phase margin {180 + pc:.0f} deg")


def main():
    RES.mkdir(exist_ok=True)
    args = sys.argv[1:]
    as_json = "--json" in args
    args = [a for a in args if a != "--json"]
    groups = list(GROUPS) if args == ["all"] else args
    if not groups or any(g not in GROUPS for g in groups):
        print(__doc__)
        sys.exit(1)
    jobs = int(os.environ.get("JOBS", "2"))
    rows = []
    for g in groups:
        cases = GROUPS[g]()
        with cf.ThreadPoolExecutor(max_workers=jobs) as ex:
            list(ex.map(run_one, cases))
        steps = [c for c in cases if c[3] is not None]
        loops = [c for c in cases if c[3] is None]
        if as_json:
            rows += step_rows(g, steps) + loop_rows(g, loops)
            continue
        print(f"### {g}")
        if steps:
            print_steps(steps)
        if loops:
            print_loops(loops)
    if as_json:
        print('{"schema": "opendap.sim-vsys-bucks/v1", "cases": [')
        print(",\n".join("  " + json.dumps(r, default=float) for r in rows))
        print("]}")


if __name__ == "__main__":
    main()
