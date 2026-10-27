"""Phase-noise and jitter budget of the divided master clock against the CS43198 mask (ADR 0019).

Usage (from this folder):
    uv run budget.py           # table
    uv run budget.py --json    # one JSON object per line, for odapkit sim checks

Sources (every input is a datasheet value or a stated estimate):
  - Mask: CS43198 DS1156F2 Figure 4-11 p. 35, read from the plot: -95 dBc/Hz at 100 Hz falling
    linearly in log f to -116 dBc/Hz at 100 kHz, flat -116 dBc/Hz to 10 MHz.
  - Oscillator: NDK NZ2520SDA catalogue 1703A, F = 49.152 MHz, 3.3 V, 25 degC, typical:
    -158 dBc/Hz at 1 kHz, -172 dBc/Hz at 100 kHz; 43 fs RMS, 12 kHz-20 MHz. The 45.1584 MHz part
    is not tabulated; the 49.152 MHz figures are used for both (UNVERIFIED). At 3.1 V: UNVERIFIED.
  - Divide by two: an ideal divider lowers phase noise by 20 log10(2) = 6.02 dB; time jitter is
    unchanged.
  - Divider supply term (estimate): delay modulation by the MCLK_1V8 LDO noise. TPS7A20 noise
    10 uVrms, 10 Hz-100 kHz at 1 mA (SBVS338H p. 7), taken as a flat 31.6 nV/sqrt(Hz). Delay
    sensitivity bound 3.2 ns/V: SN74AUC1G74 CLK->Q maximum 2.5 ns at 1.4 V and 1.7 ns at 1.65 V
    (SCES537D p. 4), (2.5 - 1.7) / 0.25. TI publishes no supply sensitivity: UNVERIFIED.
  - Divider floor (estimate): TI publishes no additive jitter for the AUC family. The LMK1C1102,
    a CMOS clock buffer at 1.8 V, guarantees 50 fs RMS maximum, 12 kHz-20 MHz (SNAS791D p. 7);
    that figure is used as a flat floor for the flip-flop (UNVERIFIED).
"""

import json
import math
import sys

F_OUT = 24.576e6
MASK = [(100, -95.0), (100e3, -116.0), (10e6, -116.0)]
XO_2X = {1e3: -158.0, 100e3: -172.0}        # NZ2520SDA at 49.152 MHz, 3.3 V, typ
XO_JITTER_S = 43e-15                         # 12 kHz-20 MHz, 49.152 MHz
DIV_DB = 20 * math.log10(2)
LDO_VRMS, LDO_BW = 10e-6, 100e3 - 10
K_DELAY = 3.2e-9                             # s/V
FLOOR_JITTER_S = 50e-15                      # LMK1C1102 maximum, as an analogue
FLOOR_BW = 20e6 - 12e3


def mask(f):
    for (f0, l0), (f1, l1) in zip(MASK, MASK[1:]):
        if f0 <= f <= f1:
            return l0 + (l1 - l0) * (math.log10(f) - math.log10(f0)) / (math.log10(f1) - math.log10(f0))
    raise ValueError(f)


def dbsum(*levels):
    return 10 * math.log10(sum(10 ** (x / 10) for x in levels))


def supply_term():
    en = LDO_VRMS / math.sqrt(LDO_BW)                 # V/sqrt(Hz)
    phi = 2 * math.pi * F_OUT * K_DELAY * en          # rad/sqrt(Hz)
    return 10 * math.log10(phi ** 2 / 2)              # dBc/Hz, single sideband


def floor_term():
    phi2 = (2 * math.pi * F_OUT * FLOOR_JITTER_S) ** 2
    return 10 * math.log10(phi2 / (2 * FLOOR_BW))


def mask_jitter(f_lo=100.0, f_hi=10e6, n=4000):
    """RMS jitter the mask allows (both sidebands), integrated on a log grid."""
    s, prev = 0.0, None
    for i in range(n + 1):
        f = f_lo * (f_hi / f_lo) ** (i / n)
        v = 10 ** (mask(f) / 10)
        if prev:
            s += (f - prev[0]) * (v + prev[1]) / 2
        prev = (f, v)
    return math.sqrt(2 * s) / (2 * math.pi * F_OUT)


def main():
    sup, flo = supply_term(), floor_term()
    rows = []
    for f, xo in XO_2X.items():
        div = xo - DIV_DB
        total = dbsum(div, sup, flo)
        rows.append(dict(item="phase_noise", offset_hz=f, mask_dbc_hz=round(mask(f), 2),
                         xo_2x_dbc_hz=xo, xo_divided_dbc_hz=round(div, 2), divider_supply_dbc_hz=round(sup, 2),
                         divider_floor_dbc_hz=round(flo, 2), total_dbc_hz=round(total, 2),
                         margin_db=round(mask(f) - total, 2)))
    sup_j = K_DELAY * LDO_VRMS
    total_j = math.sqrt(XO_JITTER_S ** 2 + sup_j ** 2 + FLOOR_JITTER_S ** 2)
    mj = mask_jitter()
    rows.append(dict(item="jitter", xo_s=XO_JITTER_S, divider_supply_s=sup_j, divider_floor_s=FLOOR_JITTER_S,
                     total_s=total_j, mask_s=mj, margin_db=round(20 * math.log10(mj / total_j), 2)))
    if "--json" in sys.argv[1:]:
        for r in rows:
            print(json.dumps(r))
        return
    print(f"{'offset':>8s} {'mask':>8s} {'XO 2x':>8s} {'XO /2':>8s} {'supply':>8s} {'floor':>8s} {'total':>8s} {'margin':>8s}")
    for r in rows[:-1]:
        print(f"{r['offset_hz']:8.0f} {r['mask_dbc_hz']:8.1f} {r['xo_2x_dbc_hz']:8.1f} {r['xo_divided_dbc_hz']:8.1f} "
              f"{r['divider_supply_dbc_hz']:8.1f} {r['divider_floor_dbc_hz']:8.1f} {r['total_dbc_hz']:8.1f} {r['margin_db']:8.1f}")
    j = rows[-1]
    print(f"jitter: XO {j['xo_s'] * 1e15:.0f} fs, divider supply {j['divider_supply_s'] * 1e15:.0f} fs, "
          f"divider floor {j['divider_floor_s'] * 1e15:.0f} fs, total {j['total_s'] * 1e15:.0f} fs RMS; "
          f"mask allows {j['mask_s'] * 1e12:.1f} ps RMS (100 Hz-10 MHz); margin {j['margin_db']:.1f} dB")


if __name__ == "__main__":
    main()
