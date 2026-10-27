"""Run the MCLK attenuator study (ADR 0010) and print its table.

Usage (from this folder):
    uv run run.py            # every case, a table per driver
    uv run run.py --json     # one JSON document instead of the table
    uv run run.py R1=1k RD=100   # override netlist parameters (exploration; not the proposed values)

--json prints {"schema": "opendap.sim-mclk-attenuator/v1", "limits": {...}, "cases": [...]}, one
case object per line ("case", "driver", "freq_hz", "cin_f", "layout" first, then the metrics),
so that odapkit sim checks can match a driver and a metric on one line.

The netlist is linear, so each case is simulated once at VCC = 1 V; the levels are scaled to the
MCLK_3V1 limits (TPS7A2031 3.1 V +/-1.5 %: 3.054-3.147 V) and compared with the CS43198 VL-domain
input limits at VL = 1.66 and 1.94 V. JOBS=n sets how many ngspice processes run at once
(default 2). Results go to results/ (ignored by git). Standard library only.
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

VCC = (3.054, 3.147)   # TPS7A2031 3.1 V +/-1.5 % (SBVS338H p. 6)
VL = (1.66, 1.94)      # CS43198 VL range (DS1156F2 Table 3-2, p. 12)
FREQS = (22.5792e6, 24.576e6)
CINS = ("1p", "4p", "10p")           # 10 pF = DS1156F2 Table 3-11 maximum; no minimum given
LAYOUTS = {                          # trace A (to the split), B (to DAC1), C (to DAC2), 7 ps/mm
    "short": dict(TDA="70p", TDB="70p", TDC="70p"),     # 10 / 10 / 10 mm
    "limit": dict(TDA="140p", TDB="140p", TDC="140p"),  # 20 / 20 / 20 mm: the longest that passes
}
DRIVERS = {"typ": 30, "bound": 181}  # ohm; see mclk-attenuator.cir
T0 = 2e-9                            # first source edge
WINDOW = (8, 12)                     # periods used (the network has settled)


def cases(over):
    tag = "".join(f"_{k}{v}" for k, v in sorted(over.items()))
    out = []
    for drv, rout in DRIVERS.items():
        for f in FREQS:
            for cin in CINS:
                for lay, tds in LAYOUTS.items():
                    name = f"{drv}_f{f / 1e6:.4f}_c{cin}_{lay}{tag}"
                    out.append((name, drv, f, cin, lay, dict(ROUT=rout, F=f, CIN=cin, **{**tds, **over})))
    return out


def render(name, params):
    text = (HERE / "mclk-attenuator.cir").read_text()
    m = re.search(r"^\.param (.*)$", text, re.M)
    d = dict(kv.split("=") for kv in m.group(1).split())
    d.update({k: str(v) for k, v in params.items()})
    text = text.replace(m.group(0), ".param " + " ".join(f"{k}={v}" for k, v in d.items()), 1)
    text = text.replace("wrdata mclk.dat", f"wrdata {RES / (name + '.dat')}")
    path = RES / f"{name}.cir"
    path.write_text(text)
    return path


def run_one(case):
    name, *_, params = case
    dat = RES / f"{name}.dat"
    if not dat.exists():
        cir = render(name, params)
        with open(RES / f"{name}.log", "w") as log:
            subprocess.run(["ngspice", "-b", str(cir)], cwd=HERE, stdout=log, stderr=subprocess.STDOUT, check=False)
    return name


def load(path):
    cols = [[] for _ in range(5)]
    with open(path) as fh:
        for line in fh:
            v = line.split()
            # wrdata: t v(xo) t v(p1) t v(p2) t i(vsrc)
            for i, k in enumerate((0, 1, 3, 5, 7)):
                cols[i].append(float(v[k]))
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


def phase(t, period, duty):
    """Where t falls in the source cycle: 'hi' plateau, 'lo' plateau or an edge region."""
    x = ((t - T0) / period) % 1.0
    if 0.25 * duty <= x < duty:
        return "hi"
    if duty + 0.25 * (1 - duty) <= x < 1.0:
        return "lo"
    return "edge"


def pin_metrics(t, v, period):
    ta, tb = T0 + WINDOW[0] * period, T0 + WINDOW[1] * period
    idx = [k for k in range(len(t)) if ta <= t[k] < tb]
    hi = [v[k] for k in idx if phase(t[k], period, 0.5) == "hi"]
    lo = [v[k] for k in idx if phase(t[k], period, 0.5) == "lo"]
    vmax, vmin = max(v[k] for k in idx), min(v[k] for k in idx)
    hi_min, lo_max = min(hi), max(lo)
    hi_end, lo_end = hi[-1], lo[-1]
    sw = hi_end - lo_end
    r10 = crossings(t, v, lo_end + 0.1 * sw, ta, tb, True)
    r90 = crossings(t, v, lo_end + 0.9 * sw, ta, tb, True)
    f90 = crossings(t, v, lo_end + 0.9 * sw, ta, tb, False)
    f10 = crossings(t, v, lo_end + 0.1 * sw, ta, tb, False)
    tr = r90[-1] - r10[-1] if r10 and r90 else float("nan")
    tf = f10[-1] - f90[-1] if f10 and f90 else float("nan")
    m = dict(hi_min=hi_min, lo_max=lo_max, vmax=vmax, vmin=vmin, tr=tr, tf=tf)
    duties, extra = [], 0
    n = WINDOW[1] - WINDOW[0]
    for vcc in VCC:
        for vl in VL:
            vil, vih = 0.3 * vl / vcc, 0.7 * vl / vcc
            for th in (vil, vih):
                ups, dns = crossings(t, v, th, ta, tb, True), crossings(t, v, th, ta, tb, False)
                extra = max(extra, len(ups) - n, len(dns) - n)
            # switching points anywhere in [VIL, VIH], rising point >= falling point (hysteresis)
            for rth, fth in ((vil, vil), (vih, vih), (vih, vil)):
                ups = crossings(t, v, rth, ta, tb, True)
                for u in ups:
                    dn = [x for x in crossings(t, v, fth, u, tb, False)]
                    if dn and dn[0] < u + period:
                        duties.append((dn[0] - u) / period * 100)
                if not ups:
                    duties.append(0.0)
    m.update(duty_min=min(duties), duty_max=max(duties), extra=extra)
    return m


def metrics(case):
    name, drv, f, cin, lay, _ = case
    t, xo, p1, p2, isrc = load(RES / f"{name}.dat")
    period = 1 / f
    pins = [pin_metrics(t, p, period) for p in (p1, p2)]
    x = pin_metrics(t, xo, period)
    ta = T0 + WINDOW[0] * period
    i_hi = max(-isrc[k] for k in range(len(t)) if t[k] >= ta and phase(t[k], period, 0.5) == "hi"
               and ((t[k] - T0) / period) % 1.0 > 0.45)
    lo_v, hi_v = min(VCC), max(VCC)
    row = dict(
        case=name, driver=drv, freq_hz=f, cin_f=cin, layout=lay,
        pin_high_min_v=min(p["hi_min"] for p in pins) * lo_v,
        pin_low_max_v=max(p["lo_max"] for p in pins) * hi_v,
        pin_peak_v=max(p["vmax"] for p in pins) * hi_v,
        pin_valley_v=min(p["vmin"] for p in pins) * hi_v,
        pin_rise_s=max(p["tr"] for p in pins),
        pin_fall_s=max(p["tf"] for p in pins),
        pin_duty_min_pct=min(p["duty_min"] for p in pins),
        pin_duty_max_pct=max(p["duty_max"] for p in pins),
        pin_extra_crossings=max(p["extra"] for p in pins),
        xo_rise_s=x["tr"], xo_fall_s=x["tf"],
        xo_high_frac=x["hi_min"],
        xo_dc_high_a=i_hi * hi_v,
    )
    return row


LIMITS = {
    "pin_high_min_v": (0.7 * max(VL), None, "VIH = 0.7 x VL at VL 1.94 V (DS1156F2 Table 3-11 p. 19, Table 3-2 p. 12)"),
    "pin_low_max_v": (None, 0.3 * min(VL), "VIL = 0.3 x VL at VL 1.66 V (Table 3-11 p. 19)"),
    "pin_peak_v": (None, min(VL) + 0.3, "VL + 0.3 V at VL 1.66 V (Table 3-2 p. 12)"),
    "pin_valley_v": (-0.3, None, "-0.3 V (Table 3-2 p. 12)"),
    "pin_rise_s": (None, 6e-9, "NZ2520SDA Tr 6 ns max (catalogue 1703A); ADR 0010"),
    "pin_fall_s": (None, 6e-9, "NZ2520SDA Tf 6 ns max (catalogue 1703A); ADR 0010"),
    "pin_duty_min_pct": (45, None, "DS1156F2 §4.5.1 p. 35"),
    "pin_duty_max_pct": (None, 55, "DS1156F2 §4.5.1 p. 35"),
    "pin_extra_crossings": (None, 0, "one VIL and one VIH crossing per edge"),
    "xo_rise_s": (None, 6e-9, "NZ2520SDA CL <= 15 pF at Tr <= 6 ns (bound driver)"),
}


def fmt(k, v):
    if v is None:
        return "-"
    if k.endswith("_s"):
        return f"{v * 1e9:.2f}"
    if k.endswith("_a"):
        return f"{v * 1e3:.2f}"
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
    rows = [metrics(c) for c in cs]
    if as_json:
        print('{"schema": "opendap.sim-mclk-attenuator/v1",')
        print(' "limits": ' + json.dumps({k: dict(min=a, max=b, source=s) for k, (a, b, s) in LIMITS.items()}) + ",")
        print(' "cases": [')
        print(",\n".join("  " + json.dumps(r) for r in rows))
        print("]}")
        return
    keys = ["pin_high_min_v", "pin_low_max_v", "pin_peak_v", "pin_valley_v", "pin_rise_s", "pin_fall_s",
            "pin_duty_min_pct", "pin_duty_max_pct", "pin_extra_crossings", "xo_rise_s", "xo_high_frac", "xo_dc_high_a"]
    heads = ["Vhi min", "Vlo max", "Vpeak", "Vvalley", "tr ns", "tf ns", "duty min", "duty max", "extra x",
             "XO tr ns", "XO hi/VCC", "XO I mA"]
    for drv in DRIVERS:
        print(f"### driver {drv} ({DRIVERS[drv]} ohm)")
        print(f"{'case':44s} " + " ".join(f"{h:>9s}" for h in heads))
        for r in rows:
            if r["driver"] == drv:
                print(f"{r['case']:44s} " + " ".join(f"{fmt(k, r[k]):>9s}" for k in keys))
        print()
    print("limits: " + "; ".join(f"{k} " + (f">= {fmt(k, a)}" if a is not None else f"<= {fmt(k, b)}")
                                  for k, (a, b, _) in LIMITS.items()))


if __name__ == "__main__":
    main()
