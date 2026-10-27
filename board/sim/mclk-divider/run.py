"""Run the MCLK divider study (ADR 0019) and print its tables.

Usage (from this folder):
    uv run run.py            # every case, one table per side
    uv run run.py --json     # one JSON document instead of the tables
    uv run run.py RS=22 RX=47    # override netlist parameters (exploration; not the proposed values)

Two linear netlists, each simulated at VCC = 1 V and scaled:
  - xo-to-divider.cir: the 2x oscillator (NSC5083D on MCLK_3V1, 3.054-3.147 V) into the
    SN74AUC1G74 clock input; checked against the AUC input limits at MCLK_1V8 = 1.76-1.84 V
    and the oscillator's 15 pF rating.
  - divider-to-xti.cir: the flip-flop output (MCLK_1V8) into two CS43198 XTI/MCLK pins; checked
    against the CS43198 VL-domain limits at VL = 1.66-1.94 V and the 45-55 % duty cycle.

--json prints {"schema": "opendap.sim-mclk-divider/v1", "limits": {...}, "cases": [...]}, one
case object per line ("case", "side", "driver" first, then the metrics), so that odapkit sim
checks can match a side, a driver and a metric on one line. JOBS=n sets how many ngspice
processes run at once (default 2). Results go to results/ (ignored by git). Standard library only.
"""

import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES = HERE / "results"

VOSC = (3.054, 3.147)     # MCLK_3V1: TPS7A2031 3.1 V +/-1.5 % (SBVS338H p. 6)
VDIV = (1.76, 1.84)       # MCLK_1V8: TPS7A2018 DBV 1.8 V +/-40 mV (SBVS338H p. 6)
VL = (1.66, 1.94)         # CS43198 VL range (DS1156F2 Table 3-2, p. 12)
FOUT = (22.5792e6, 24.576e6)
T0 = 2e-9

# Input side: oscillator drivers (ohm), symmetry, flip-flop input capacitance, trace D.
XO_DRIVERS = {"strong": 10, "typ": 30, "bound": 181}
XO_DUTY = (0.4, 0.6)                  # NZ2520SDA symmetry 40-60 % (catalogue 1703A)
CFFS = ("2.5p", "4p")                 # SCES537D p. 4: 2.5 pF typ; 4 pF assumed bound (UNVERIFIED)
D_LAYOUTS = {"short": "35p", "limit": "70p"}    # 5 mm and 10 mm at 7 ps/mm

# Output side: flip-flop drivers (ohm), DLT = tPHL - tPLH, XTI capacitance, traces B and C.
FF_DRIVERS = {"strong": 15, "bound": 56}
DLTS = ("-0.7n", "0", "0.7n")         # SCES537D p. 4: CLK -> Q 1.0-1.7 ns at CL 15 pF
CINS = ("1p", "4p", "10p")            # DS1156F2 Table 3-11: 10 pF max, no min
B_LAYOUTS = {"short": "35p", "limit": "105p"}   # 5 / 15 mm from each divider to its DAC

IN_WINDOW = (10, 16)                  # oscillator periods used
OUT_WINDOW = (8, 12)                  # output periods used


def to_s(x):
    m = re.fullmatch(r"([-+0-9.eE]+)([pnu]?)", str(x))
    return float(m.group(1)) * {"": 1, "p": 1e-12, "n": 1e-9, "u": 1e-6}[m.group(2)]


def cases(over):
    tag = "".join(f"_{k}{v}" for k, v in sorted(over.items()))
    out = []
    for drv, rout in XO_DRIVERS.items():
        for f in FOUT:
            for duty in XO_DUTY:
                for cff in CFFS:
                    for lay, tdd in D_LAYOUTS.items():
                        name = f"in_{drv}_f{f / 1e6:.4f}_d{duty}_c{cff}_{lay}{tag}"
                        p = dict(ROUT=rout, F=2 * f, DUTY=duty, CFF=cff, TDD=tdd)
                        p.update({k: v for k, v in over.items() if k in ("RX", "COFF", "CPAD", "TDD")})
                        out.append(dict(name=name, side="in", driver=drv, f=f, cir="xo-to-divider.cir",
                                        dat="xo.dat", params=p, tag=dict(duty=duty, cff=cff, layout=lay)))
    for drv, rout in FF_DRIVERS.items():
        for f in FOUT:
            for dlt in DLTS:
                for cin in CINS:
                    for lay, tdb in B_LAYOUTS.items():
                        name = f"out_{drv}_f{f / 1e6:.4f}_dlt{dlt}_c{cin}_{lay}{tag}"
                        p = dict(ROUT=rout, F=f, DLT=dlt, CIN=cin, TDB=tdb)
                        p.update({k: v for k, v in over.items() if k in ("RS", "CPAD", "TRS", "TDB")})
                        out.append(dict(name=name, side="out", driver=drv, f=f, cir="divider-to-xti.cir",
                                        dat="xti.dat", params=p, tag=dict(dlt=dlt, cin=cin, layout=lay)))
    return out


def render(c):
    text = (HERE / c["cir"]).read_text()
    m = re.search(r"^\.param (.*)$", text, re.M)
    d = dict(kv.split("=") for kv in m.group(1).split())
    d.update({k: str(v) for k, v in c["params"].items()})
    text = text.replace(m.group(0), ".param " + " ".join(f"{k}={v}" for k, v in d.items()), 1)
    text = text.replace(f"wrdata {c['dat']}", f"wrdata {RES / (c['name'] + '.dat')}")
    path = RES / f"{c['name']}.cir"
    path.write_text(text)
    return path


def run_one(c):
    dat = RES / f"{c['name']}.dat"
    if not dat.exists():
        cir = render(c)
        with open(RES / f"{c['name']}.log", "w") as log:
            subprocess.run(["ngspice", "-b", str(cir)], cwd=HERE, stdout=log, stderr=subprocess.STDOUT, check=False)
    return c["name"]


def load(path, ncols):
    cols = [[] for _ in range(ncols + 1)]
    with open(path) as fh:
        for line in fh:
            v = line.split()
            cols[0].append(float(v[0]))
            for i in range(ncols):
                cols[i + 1].append(float(v[2 * i + 1]))
    return cols


def crossings(t, v, th, ta, tb, up):
    out = []
    for k in range(1, len(t)):
        if t[k] < ta or t[k] > tb:
            continue
        a, b = v[k - 1], v[k]
        if (up and a < th <= b) or (not up and a > th >= b):
            out.append(t[k - 1] + (th - a) / (b - a) * (t[k] - t[k - 1]))
    return out


def plateaus(t, v, period, duty, ta, tb):
    """Samples in the settled part of the high and of the low half of each source cycle."""
    hi, lo = [], []
    for k in range(len(t)):
        if not ta <= t[k] < tb:
            continue
        x = ((t[k] - T0) / period) % 1.0
        if 0.25 * duty <= x < duty:
            hi.append(v[k])
        elif duty + 0.25 * (1 - duty) <= x < 1.0:
            lo.append(v[k])
    return hi, lo


def edges(t, v, ta, tb):
    """Last 10-90 % rise and fall times (normalised levels 0..1)."""
    r10, r90 = crossings(t, v, 0.1, ta, tb, True), crossings(t, v, 0.9, ta, tb, True)
    f90, f10 = crossings(t, v, 0.9, ta, tb, False), crossings(t, v, 0.1, ta, tb, False)
    tr = r90[-1] - r10[-1] if r10 and r90 else float("nan")
    tf = f10[-1] - f90[-1] if f10 and f90 else float("nan")
    return tr, tf


def extra_crossings(t, v, ths, ta, tb, n):
    extra = 0
    for th in ths:
        extra = max(extra, len(crossings(t, v, th, ta, tb, True)) - n, len(crossings(t, v, th, ta, tb, False)) - n)
    return extra


def metrics_in(c):
    t, xo, ck, isrc = load(RES / f"{c['name']}.dat", 3)
    period = 1 / (2 * c["f"])
    duty = c["tag"]["duty"]
    ta, tb = T0 + IN_WINDOW[0] * period, T0 + IN_WINDOW[1] * period
    n = IN_WINDOW[1] - IN_WINDOW[0]
    idx = [k for k in range(len(t)) if ta <= t[k] < tb]
    xtr, xtf = edges(t, xo, ta, tb)
    ctr, ctf = edges(t, ck, ta, tb)
    lo_v, hi_v = min(VOSC), max(VOSC)
    # AUC thresholds in units of the oscillator swing, at every supply combination
    ths = []
    for vo in VOSC:
        for vd in VDIV:
            ths += [0.35 * vd / vo, 0.65 * vd / vo]
    vih_n = 0.65 * max(VDIV) / lo_v            # worst VIH, normalised to the lowest swing
    vil_n = 0.35 * min(VDIV) / hi_v            # worst VIL, normalised to the highest swing
    # per source cycle: its highest and lowest point, time above VIH and below VIL
    peaks, valleys, t_hi, t_lo = [], [], [], []
    for k in range(IN_WINDOW[0], IN_WINDOW[1]):
        a, b = T0 + k * period, T0 + (k + 1) * period
        seg = [j for j in idx if a <= t[j] < b]
        peaks.append(max(ck[j] for j in seg))
        valleys.append(min(ck[j] for j in seg))
        th = tl = 0.0
        for j in seg[1:]:
            dt = t[j] - t[j - 1]
            th += dt if ck[j] >= vih_n else 0.0
            tl += dt if ck[j] <= vil_n else 0.0
        t_hi.append(th)
        t_lo.append(tl)
    return dict(
        case=c["name"], side="in", driver=c["driver"], freq_hz=c["f"], xo_duty=duty, cff_f=c["tag"]["cff"],
        layout=c["tag"]["layout"],
        clk_high_min_v=min(peaks) * lo_v,
        clk_low_max_v=max(valleys) * hi_v,
        clk_peak_v=max(ck[k] for k in idx) * hi_v,
        clk_valley_v=min(ck[k] for k in idx) * hi_v,
        clk_pulse_min_s=min(t_hi + t_lo),
        clk_rate_ns_per_v=max(ctr, ctf) * 1e9 / (0.8 * lo_v),
        clk_extra_crossings=extra_crossings(t, ck, ths, ta, tb, n),
        xo_rise_s=xtr, xo_fall_s=xtf,
        xo_load_pf=(2 * (to_s(c["params"]["CFF"]) + 0.5e-12) + 0.3e-12 + to_s(c["params"]["TDD"]) / 50
                    + 1e-12 + 2e-12) * 1e12,
    )


def metrics_out(c):
    t, q, p1, isrc = load(RES / f"{c['name']}.dat", 3)
    period = 1 / c["f"]
    ta, tb = T0 + OUT_WINDOW[0] * period, T0 + OUT_WINDOW[1] * period
    n = OUT_WINDOW[1] - OUT_WINDOW[0]
    rows = []
    duty_src = 0.5 + to_s(c["params"]["DLT"]) / period
    for v in (p1,):
        hi, lo = plateaus(t, v, period, duty_src, ta, tb)
        idx = [k for k in range(len(t)) if ta <= t[k] < tb]
        tr, tf = edges(t, v, ta, tb)
        duties, extra = [], 0
        for vd in VDIV:
            for vl in VL:
                vil, vih = 0.3 * vl / vd, 0.7 * vl / vd
                extra = max(extra, extra_crossings(t, v, (vil, vih), ta, tb, n))
                # switching points anywhere in [VIL, VIH], rising point >= falling point (hysteresis)
                for rth, fth in ((vil, vil), (vih, vih), (vih, vil)):
                    ups = crossings(t, v, rth, ta, tb, True)
                    for u in ups:
                        dn = crossings(t, v, fth, u, tb, False)
                        if dn and dn[0] < u + period:
                            duties.append((dn[0] - u) / period * 100)
                    if not ups:
                        duties.append(0.0)
        rows.append(dict(hi=min(hi), lo=max(lo), vmax=max(v[k] for k in idx), vmin=min(v[k] for k in idx),
                         tr=tr, tf=tf, dmin=min(duties), dmax=max(duties), extra=extra))
    cin = to_s(c["params"]["CIN"])
    cpad = to_s(c["params"].get("CPAD", "0.5p"))
    load_pf = (to_s(c["params"]["TDB"]) / 50 + cin + cpad) * 1e12   # line C = TD / Z0
    return dict(
        case=c["name"], side="out", driver=c["driver"], freq_hz=c["f"], dlt_s=to_s(c["tag"]["dlt"]),
        cin_f=c["tag"]["cin"], layout=c["tag"]["layout"],
        pin_high_min_v=min(r["hi"] for r in rows) * min(VDIV),
        pin_low_max_v=max(r["lo"] for r in rows) * max(VDIV),
        pin_peak_v=max(r["vmax"] for r in rows) * max(VDIV),
        pin_valley_v=min(r["vmin"] for r in rows) * max(VDIV),
        pin_rise_s=max(r["tr"] for r in rows),
        pin_fall_s=max(r["tf"] for r in rows),
        pin_duty_min_pct=min(r["dmin"] for r in rows),
        pin_duty_max_pct=max(r["dmax"] for r in rows),
        pin_extra_crossings=max(r["extra"] for r in rows),
        ff_load_pf=load_pf,
    )


LIMITS = {
    "clk_high_min_v": (0.65 * max(VDIV), None, "AUC VIH = 0.65 x VCC at 1.84 V (SCES537D p. 3)"),
    "clk_low_max_v": (None, 0.35 * min(VDIV), "AUC VIL = 0.35 x VCC at 1.76 V (SCES537D p. 3)"),
    "clk_peak_v": (None, 3.6, "AUC VI max 3.6 V (SCES537D p. 3, abs. max p. 3)"),
    "clk_valley_v": (-0.5, None, "AUC VI min -0.5 V (SCES537D abs. max p. 3)"),
    "clk_pulse_min_s": (1e-9, None, "AUC tw CLK high or low >= 1 ns at 1.8 V (SCES537D p. 4)"),
    "xo_load_pf": (None, 15, "NZ2520SDA load CL max 15 pF (catalogue 1703A): pins, trace, pads, tri-stated part"),
    "clk_rate_ns_per_v": (None, 20, "AUC input transition rate <= 20 ns/V (SCES537D p. 3)"),
    "clk_extra_crossings": (None, 0, "one VIL and one VIH crossing per edge (a re-crossing is an extra toggle)"),
    "xo_rise_s": (None, 6e-9, "NZ2520SDA CL <= 15 pF at Tr <= 6 ns (catalogue 1703A), bound driver"),
    "pin_high_min_v": (0.7 * max(VL), None, "VIH = 0.7 x VL at VL 1.94 V (DS1156F2 Table 3-11 p. 19, Table 3-2 p. 12)"),
    "pin_low_max_v": (None, 0.3 * min(VL), "VIL = 0.3 x VL at VL 1.66 V (Table 3-11 p. 19)"),
    "pin_peak_v": (None, min(VL) + 0.3, "VL + 0.3 V at VL 1.66 V (Table 3-2 p. 12)"),
    "pin_valley_v": (-0.3, None, "-0.3 V (Table 3-2 p. 12)"),
    "pin_duty_min_pct": (45, None, "DS1156F2 §4.5.1 p. 35"),
    "pin_duty_max_pct": (None, 55, "DS1156F2 §4.5.1 p. 35"),
    "pin_extra_crossings": (None, 0, "one VIL and one VIH crossing per edge"),
    "ff_load_pf": (None, 15, "SCES537D p. 4: CLK -> Q 1.0-1.7 ns specified at CL = 15 pF"),
}


def fmt(k, v):
    if v is None:
        return "-"
    if k.endswith("_s"):
        return f"{v * 1e9:.2f}"
    return f"{v:.3f}" if isinstance(v, float) else str(v)


def main():
    args = sys.argv[1:]
    as_json = "--json" in args
    rest = [a for a in args if a != "--json"]
    if any("=" not in a for a in rest):
        print(__doc__)
        sys.exit(1)
    over = dict(a.split("=", 1) for a in rest)
    RES.mkdir(exist_ok=True)
    cs = cases(over)
    with cf.ThreadPoolExecutor(max_workers=int(os.environ.get("JOBS", "2"))) as ex:
        list(ex.map(run_one, cs))
    rows = [metrics_in(c) if c["side"] == "in" else metrics_out(c) for c in cs]
    if as_json:
        print('{"schema": "opendap.sim-mclk-divider/v1",')
        print(' "limits": ' + json.dumps({k: dict(min=a, max=b, source=s) for k, (a, b, s) in LIMITS.items()}) + ",")
        print(' "cases": [')
        print(",\n".join("  " + json.dumps(r) for r in rows))
        print("]}")
        return
    sides = {
        "in": (["clk_high_min_v", "clk_low_max_v", "clk_peak_v", "clk_valley_v", "clk_rate_ns_per_v",
                "clk_extra_crossings", "clk_pulse_min_s", "xo_rise_s", "xo_fall_s", "xo_load_pf"],
               ["Vhi min", "Vlo max", "Vpeak", "Vvalley", "ns/V", "extra x", "tw ns", "XO tr ns", "XO tf ns",
                "XO pF"]),
        "out": (["pin_high_min_v", "pin_low_max_v", "pin_peak_v", "pin_valley_v", "pin_rise_s", "pin_fall_s",
                 "pin_duty_min_pct", "pin_duty_max_pct", "pin_extra_crossings", "ff_load_pf"],
                ["Vhi min", "Vlo max", "Vpeak", "Vvalley", "tr ns", "tf ns", "duty min", "duty max", "extra x",
                 "load pF"]),
    }
    for side, (keys, heads) in sides.items():
        print(f"### {'oscillator -> divider clock input' if side == 'in' else 'divider -> XTI'}")
        print(f"{'case':52s} " + " ".join(f"{h:>9s}" for h in heads))
        for r in rows:
            if r["side"] == side:
                print(f"{r['case']:52s} " + " ".join(f"{fmt(k, r[k]):>9s}" for k in keys))
        worst = {}
        for k in keys:
            vals = [r[k] for r in rows if r["side"] == side and (k != "xo_rise_s" or r["driver"] == "bound")]
            worst[k] = (min(vals), max(vals))
        print("worst (min, max): " + "; ".join(f"{k} {fmt(k, a)}..{fmt(k, b)}" for k, (a, b) in worst.items()))
        print()
    print("limits: " + "; ".join(f"{k} " + (f">= {fmt(k, a)}" if a is not None else f"<= {fmt(k, b)}")
                                  for k, (a, b, _) in LIMITS.items()))


if __name__ == "__main__":
    main()
