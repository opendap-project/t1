#!/usr/bin/env python3
"""Impedance, coupling, conductor loss and power-conductor sizing for the T1 flat cables.

HAT flat cable: hat-standard interface v2 (one USB port; RFC 0014, RFC 0015), updated 2026-10-25.

Used by the board's HAT flat-cable specification (docs/specs/hat-flat-cable.md) and by
faceplate-touch's faceplate flex specification. Every number those specs quote from
"the field solver" is printed by this script.

Method
------
* 2D electrostatic finite differences on a uniform square grid (potential on nodes,
  relative permittivity per cell, zero-flux outer boundaries unless a ground plane is
  placed there). Per-unit-length capacitance comes from the field energy.
* Odd and even mode impedances of a symmetric pair from the capacitance with the
  dielectrics and in vacuum: Z = 1 / (c * sqrt(C * C_vacuum)); Zdiff = 2 Zodd.
* Conductor loss by Wheeler's incremental-inductance rule: every conductor surface is
  receded by one grid step, R' = Rs * dL/dn / mu0, alpha = R' / (2 Zodd). Smooth copper;
  roughness is not modelled.
* Power conductors by the IPC-2221B design equation I = k * dT^0.44 * A^0.725
  (A in mil^2; k = 0.048 external, 0.024 internal), a conservative chart fit.

Validation (printed first): symmetric stripline against the Wheeler/Cohn closed form and
microstrip against Hammerstad; both agree within 1 %.

Stack-ups are the fab's published standard FPC stack-ups (Stack-up for FPC page, fetched
2026-10-24). The fab gives DK 3.3 for adhesiveless and 3.5 for adhesive-based polyimide;
the adhesive and bonding-sheet ("pure gum") DK is not published, so 3.5 is assumed and
the 3.3 and 3.6 cases are printed as sensitivity.

The specifications take their impedance figures from toolkit-hardware's `odapkit stackup`;
this script cross-checks them and adds loss, coupling, the EMI-film effect and power sizing.
"""
import math
import os
import sys

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

EPS0 = 8.854187817e-12
MU0 = 4e-7 * math.pi
C_LIGHT = 299792458.0
RHO_CU = 1.72e-8  # ohm*m at 20 C


# ---------------------------------------------------------------- solver


class Geo:
    """Cross-section on a uniform grid; lengths in micrometres, y = 0 at the bottom."""

    def __init__(self, width_um, height_um, d_um):
        self.d = d_um
        self.nx = int(round(width_um / d_um))
        self.ny = int(round(height_um / d_um))
        self.eps = np.ones((self.ny, self.nx))
        self.fixed = {}

    def _r(self, y):
        return int(round(y / self.d))

    def layer(self, y0, y1, er):
        self.eps[self._r(y0):self._r(y1), :] = er

    def plane(self, y, cid=0):
        r = self._r(y)
        for c in range(self.nx + 1):
            self.fixed[(r, c)] = cid

    def rect(self, x0, x1, y0, y1, cid):
        for r in range(self._r(y0), self._r(y1) + 1):
            for c in range(self._r(x0), self._r(x1) + 1):
                self.fixed[(r, c)] = cid


def energy(g, volts, eps):
    """Field energy per unit length divided by eps0, for the given conductor voltages."""
    ny, nx = g.ny + 1, g.nx + 1
    n = ny * nx
    zero_row = np.zeros(g.nx)
    zero_col = np.zeros(g.ny)
    ch = np.zeros((ny, nx - 1))
    for r in range(ny):
        a = eps[r - 1, :] if r - 1 >= 0 else zero_row
        b = eps[r, :] if r < g.ny else zero_row
        ch[r, :] = 0.5 * (a + b)
    cv = np.zeros((ny - 1, nx))
    for c in range(nx):
        a = eps[:, c - 1] if c - 1 >= 0 else zero_col
        b = eps[:, c] if c < g.nx else zero_col
        cv[:, c] = 0.5 * (a + b)
    rr, cc = np.meshgrid(np.arange(ny), np.arange(nx - 1), indexing="ij")
    k1 = (rr * nx + cc).ravel()
    rr2, cc2 = np.meshgrid(np.arange(ny - 1), np.arange(nx), indexing="ij")
    k3 = (rr2 * nx + cc2).ravel()
    a = np.concatenate([k1, k3])
    b = np.concatenate([k1 + 1, k3 + nx])
    w = np.concatenate([ch.ravel(), cv.ravel()])
    diag = np.zeros(n)
    np.add.at(diag, a, w)
    np.add.at(diag, b, w)
    mat = sp.coo_matrix(
        (np.concatenate([-w, -w, diag]),
         (np.concatenate([a, b, np.arange(n)]), np.concatenate([b, a, np.arange(n)]))),
        shape=(n, n)).tocsr()
    phi = np.zeros(n)
    fixed = np.zeros(n, bool)
    for (r, c), cid in g.fixed.items():
        k = r * nx + c
        fixed[k] = True
        phi[k] = volts.get(cid, 0.0)
    free = ~fixed
    phi[free] = spla.spsolve(mat[free][:, free].tocsc(), -mat[free][:, fixed] @ phi[fixed])
    return 0.5 * np.sum(w * (phi[a] - phi[b]) ** 2)


def pair(g):
    """Odd/even impedances of conductors 1 and 2 (ground is 0)."""
    air = np.ones_like(g.eps)
    co = energy(g, {1: 1.0, 2: -1.0}, g.eps) * EPS0
    co0 = energy(g, {1: 1.0, 2: -1.0}, air) * EPS0
    ce = energy(g, {1: 1.0, 2: 1.0}, g.eps) * EPS0
    ce0 = energy(g, {1: 1.0, 2: 1.0}, air) * EPS0
    zo = 1.0 / (C_LIGHT * math.sqrt(co * co0))
    ze = 1.0 / (C_LIGHT * math.sqrt(ce * ce0))
    return {"zdiff": 2 * zo, "zodd": zo, "zeven": ze, "zcomm": ze / 2,
            "eeff": co / co0, "lodd": MU0 * EPS0 / co0}


def single(g):
    c = 2 * energy(g, {1: 1.0}, g.eps) * EPS0
    c0 = 2 * energy(g, {1: 1.0}, np.ones_like(g.eps)) * EPS0
    return {"z0": 1.0 / (C_LIGHT * math.sqrt(c * c0)), "eeff": c / c0}


def rs(f):
    return math.sqrt(math.pi * f * MU0 * RHO_CU)


# ---------------------------------------------------------------- stack-ups

# HAT flat cable: the fab standard 4-layer FPC, 0.268 mm (coverlay 12.5 PI + 15 adhesive;
# L1 18 um base, 24 um finished; adhesive 13 / PI 25 / bonding sheet 13; L2 12 um;
# adhesive 13 / PI 25 / adhesive 13; L3 12 um; bonding sheet 13 / PI 25 / adhesive 13;
# L4 18/24 um; coverlay). Pairs on L2; L1 ground above; L3 voided under the pair band;
# L4 ground below.
T_L2 = 12
BELOW_L2 = 114  # adh 13 + PI 25 + adh 13 + void L3 12 + gum 13 + PI 25 + adh 13
ABOVE_L2 = 51   # gum 13 (around and over L2) + PI 25 + adh 13


def hat_geo(w, s, er_pi=3.3, er_adh=3.5, d=1.0, side=400, recede=0.0, single_line=False):
    yb = BELOW_L2 + recede
    t = T_L2 - 2 * recede
    h = BELOW_L2 + T_L2 + ABOVE_L2 + 2 * recede
    width = (w if single_line else 2 * w + s) + 2 * side
    g = Geo(width, h, d)
    # below L2 (from L4 upwards)
    g.layer(0, 13, er_adh)
    g.layer(13, 38, er_pi)
    g.layer(38, 76, er_adh)   # adhesive 13 + void L3 (12, filled) + adhesive 13
    g.layer(76, 101, er_pi)
    g.layer(101, 114, er_adh)
    # L2 embedded in the bonding sheet, then PI and adhesive up to L1
    g.layer(114, 114 + T_L2 + 13, er_adh)
    g.layer(114 + T_L2 + 13, 114 + T_L2 + 38, er_pi)
    g.layer(114 + T_L2 + 38, h, er_adh)
    g.plane(0)
    g.plane(h)
    x0 = side
    g.rect(x0, x0 + w, yb + recede, yb + recede + t, 1)
    if not single_line:
        g.rect(x0 + w + s, x0 + 2 * w + s, yb + recede, yb + recede + t, 2)
    return g


def hat_microstrip_geo(w, s, film, d=1.5, side=400):
    """Comparison only: pairs on L1 over L2 of the fab's 0.204 mm 4-layer stack
    (PI 25 + bonding sheet 13 = 38 um), coverlay 15 adhesive + 12.5 PI, with or without an
    EMI shielding film taken as a ground plane on the coverlay surface."""
    t, h = 18, 38
    top = h + t + 27.5
    height = top + (0 if film else 300)
    g = Geo(2 * w + s + 2 * side, height, d)
    g.layer(0, 25, 3.3)
    g.layer(25, h, 3.5)
    g.layer(h, h + t + 15, 3.5)
    g.layer(h + t + 15, top, 3.3)
    g.plane(0)
    if film:
        g.plane(height)
    g.rect(side, side + w, h, h + t, 1)
    g.rect(side + w + s, side + 2 * w + s, h, h + t, 2)
    return g


# Faceplate flex: the fab standard 2-layer FPC, 0.156 mm (coverlay 12.5 PI + 15 adhesive;
# L1 18 um base, 24 um finished; adhesive 20 / PI 25 / adhesive 20; L2 18/24 um;
# coverlay). DSI on L1 over the L2 ground plane.
def fp_geo(w, s, film=False, er_pi=3.3, er_adh=3.5, d=1.5, side=400):
    t, h = 24, 65
    top = h + t + 27.5
    height = top + (0 if film else 350)
    g = Geo(2 * w + s + 2 * side, height, d)
    g.layer(0, 20, er_adh)
    g.layer(20, 45, er_pi)
    g.layer(45, 65, er_adh)
    g.layer(65, 65 + t + 15, er_adh)
    g.layer(65 + t + 15, top, er_pi)
    g.plane(0)
    if film:
        g.plane(height)
    g.rect(side, side + w, h, h + t, 1)
    g.rect(side + w + s, side + 2 * w + s, h, h + t, 2)
    return g


# ---------------------------------------------------------------- studies


def wheeler_loss_db_per_100mm(w, s, f, d=1.0):
    nominal = pair(hat_geo(w, s, d=d))
    l1 = nominal["lodd"]
    l2 = pair(hat_geo(w - 2 * d, s + 2 * d, d=d, recede=d))["lodd"]
    r_per_m = rs(f) * (l2 - l1) / (d * 1e-6) / MU0
    return 8.686 * r_per_m / (2 * nominal["zodd"]) * 0.1, r_per_m


def ipc2221_width_mm(i, t_um, dt=10.0, internal=True):
    k = 0.024 if internal else 0.048
    area_mil2 = (i / (k * dt ** 0.44)) ** (1 / 0.725)
    return area_mil2 / (t_um / 25.4) * 0.0254


def res_mohm(w_mm, t_um, l_mm):
    return 1e3 * RHO_CU * l_mm * 1e-3 / (w_mm * 1e-3 * t_um * 1e-6)


def main(out):
    p = lambda *a: print(*a, file=out)  # noqa: E731

    p("# Validation")
    g = Geo(1000, 100, 1.0)
    g.plane(0)
    g.plane(100)
    g.rect(475, 525, 50, 50, 1)
    p(f"stripline b=100 w=50 t=0 er=1: solver {single(g)['z0']:.1f} ohm, "
      f"closed form {30 * math.pi * 100 / (50 + 0.441 * 100):.1f} ohm")
    g = Geo(2500, 1200, 4.0)
    g.plane(0)
    g.rect(1150, 1350, 100, 100, 1)
    u = 2.0
    p(f"microstrip h=100 w=200 t=0 er=1: solver {single(g)['z0']:.1f} ohm, "
      f"Hammerstad {120 * math.pi / (u + 1.393 + 0.667 * math.log(u + 1.444)):.1f} ohm")

    p("\n# HAT flat cable (the fab 4-layer 0.268 mm; pairs on L2, L1 and L4 ground, L3 void)")
    p("# One USB port (hat-standard interface v2): SSTX, SSRX and D+/D- at 90 ohm differential")
    w, s = 70, 100
    r = pair(hat_geo(w, s))
    p(f"USB 90 ohm: w={w} s={s} um -> Zdiff {r['zdiff']:.1f}, Zcomm {r['zcomm']:.1f}, "
      f"eeff {r['eeff']:.2f}, delay {math.sqrt(r['eeff']) / C_LIGHT * 1e9:.2f} ps/mm")
    for slabel, kw in [("all DK 3.3", {"er_adh": 3.3}), ("all DK 3.6", {"er_pi": 3.6, "er_adh": 3.6})]:
        p(f"   {slabel}: {pair(hat_geo(w, s, **kw))['zdiff']:.1f}")
    for dw in (-10, 10):
        p(f"   w{dw:+d} um (gap kept centred): {pair(hat_geo(w + dw, s - dw))['zdiff']:.1f}")
    for f in (1.25e9, 2.5e9):
        db, rpm = wheeler_loss_db_per_100mm(w, s, f)
        p(f"   conductor loss at {f / 1e9:.2f} GHz: R' {rpm:.0f} ohm/m per line, {db:.2f} dB per 100 mm")
    for gap in (300, 350, 400):
        r = pair(hat_geo(70, gap))
        k = (r["zeven"] - r["zodd"]) / (r["zeven"] + r["zodd"])
        p(f"coupling between two 70 um lines {gap} um apart: K {k:.1e}, backward ~ {20 * math.log10(k / 2):.0f} dB")
    ad = 8.686 * math.pi * 2.5e9 * math.sqrt(3.42) / C_LIGHT * 0.1  # dB per 100 mm per unit tan_delta
    p(f"dielectric loss at 2.5 GHz, eeff 3.42: {ad:.1f} x tan_delta dB per 100 mm "
      f"(tan_delta 0.005: {ad * 0.005:.2f} dB; 0.02: {ad * 0.02:.2f} dB)")
    for w, s in ((60, 150), (70, 150)):
        a = pair(hat_microstrip_geo(w, s, film=False))["zdiff"]
        b = pair(hat_microstrip_geo(w, s, film=True))["zdiff"]
        p(f"comparison, microstrip L1/L2 on the 0.204 mm stack w={w} s={s}: {a:.1f} ohm, "
          f"with EMI film on the coverlay {b:.1f} ohm ({(b / a - 1) * 100:.0f} %)")

    p("\n# HAT flat cable power conductors (IPC-2221B, dT = 10 C)")
    p("# VBUS: interface v2, 3.0 A continuous, 4.5 A fault ceiling, either direction")
    p(f"VBUS 4.5 A on L3 (12 um, internal): {ipc2221_width_mm(4.5, 12):.2f} mm")
    p(f"GND 4.5 A on an outer layer (18 um base, external): {ipc2221_width_mm(4.5, 18, internal=False):.2f} mm")
    p(f"rise at the continuous rating (3.0 of 4.5 A): {10 * (3.0 / 4.5) ** (1 / 0.44):.1f} C")
    vbus_w, gnd_w = 18.5, 2 * 21.0  # L3 pour; L1 + L4 planes over a 21 mm body (layout estimate)
    for l in (40, 100):
        rv, rg = res_mohm(vbus_w, 12, l), res_mohm(gnd_w, 18, l)
        cv = cg = 90 / 15 * 2  # 15 DF40 contacts per rail, two mated pairs, 90 mOhm maximum each
        for case, i in (("continuous", 3.0), ("fault ceiling", 4.5)):
            v = i * (rv + cv + rg + cg)
            p(f"L={l} mm {case} {i} A: VBUS loop {v:.0f} mV ({v / 50:.1f} % of 5 V) "
              f"[conductors {rv:.1f}/{rg:.1f} mOhm, DF40 max {cv:.0f}/{cg:.0f} mOhm for both ends]")

    p("\n# Faceplate flex (the fab 2-layer 0.156 mm; DSI on L1 over L2 ground)")
    for w, s in ((80, 150), (85, 150), (90, 150)):
        p(f"DSI w={w} s={s} um: Zdiff {pair(fp_geo(w, s))['zdiff']:.1f}")
    w, s = 85, 150
    for slabel, kw in (("all DK 3.3", {"er_adh": 3.3}), ("all DK 3.6", {"er_pi": 3.6, "er_adh": 3.6}),
                       ("EMI film on the coverlay", {"film": True})):
        p(f"   {slabel}: {pair(fp_geo(w, s, **kw))['zdiff']:.1f}")
    for dw in (-10, 10):
        p(f"   w{dw:+d} um: {pair(fp_geo(w + dw, s - dw))['zdiff']:.1f}")
    for gap in (300, 450):
        r = pair(fp_geo(85, gap))
        k = (r["zeven"] - r["zodd"]) / (r["zeven"] + r["zodd"])
        p(f"coupling between two 85 um lines {gap} um apart: K {k:.1e}, backward ~ {20 * math.log10(k / 2):.0f} dB")
    p(f"FP_3V3 0.4 A, 24 um external: {ipc2221_width_mm(0.4, 24, internal=False):.3f} mm minimum")
    for name, wmm, i in (("FP_3V3", 0.5, 0.2), ("FP_1V8", 0.3, 0.1), ("FP_VCI", 0.3, 0.1),
                         ("MIC_1V8", 0.2, 0.02), ("BL_LEDA/K", 0.3, 0.06)):
        p(f"{name} {wmm} mm at its budget {i} A over 80 mm: {i * res_mohm(wmm, 24, 80):.1f} mV")


if __name__ == "__main__":
    os.makedirs(os.path.join(os.path.dirname(__file__) or ".", "results"), exist_ok=True)

    class Tee:
        def __init__(self, *files):
            self.files = files

        def write(self, x):
            for f in self.files:
                f.write(x)

        def flush(self):
            for f in self.files:
                f.flush()

    path = os.path.join(os.path.dirname(__file__) or ".", "results", "flex-impedance.txt")
    with open(path, "w") as fh:
        main(Tee(sys.stdout, fh))
