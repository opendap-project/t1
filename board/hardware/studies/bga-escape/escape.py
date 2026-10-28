#!/usr/bin/env python3
"""RK3566 BGA escape and core-plane study on the T1 main board's stackup (stackup v3).

Run with KiCad's Python (pcbnew, numpy), from any directory, one stack per run:

    PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
    $PY hardware/studies/bga-escape/escape.py                    # v3 (default), z8, v1-10l

Inputs (read only):
- the RK3566 footprint from libs (kicad/; workspace repos.tsv, ODAP_KICAD_LIB_DIR, or the submodule
  hardware/lib/opendap once it carries the part);
- the ball nets from hardware/pinout/pinout-v1.csv;
- the composed T1 rules hardware/t1-main-board/t1-main-board.kicad_dru, copied next to the study
  board as bga-escape-<stack>.kicad_dru.

The SoC sits on the back of the board (ADR 0016), so the study places the footprint flipped on
B.Cu. Study layer index k counts from the SoC side: k = 0 is the back (B.Cu, the board's last
layer), k = n - 1 is L1 (F.Cu, the front). STACKS below gives each candidate's roles inside the
core zone; the zone maps of the whole board are in docs/specs/stackup-v3.md §3.

Writes bga-escape-<stack>.kicad_pcb / .kicad_pro / .kicad_dru and bga-escape-<stack>.result.json
in this folder (ESCAPE_OUT=<dir> writes elsewhere). The method, the assumptions and the results are
in README.md.

Method, in short: a grid router (0.025 mm grid, 8 directions, A* with a turn penalty) over obstacle
maps inflated by the clearances below; every geometric clearance is checked exactly again when a via
is placed. The power planes under the core are drawn as one zone per rail on its plane layer, grown
from the rail's vias; KiCad fills them, and KiCad's DRC with the composed rules is the judge.

Decoupling model (stacks with decap=True, ESCAPE_DECAP=0/1 overrides): every capacitor of
Rockchip's list near the SoC (HDG 1.1 pp. 35-41) gets its ground through a front-side stacked
microvia (L1-L2-L3, kind 'mvf') within 1.0 mm of one of its rail's through vias, where its power
pad lands; its body is an obstacle on L1 and a keep-out for the L1 fill; ground through vias
around the package join the front-side ground, as the board's stitching will (PCB-S-19).
"""

import csv
import heapq
import json
import math
import os
import shutil
import subprocess
import sys

import numpy as np
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))


BOARD_REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PINOUT = os.path.join(BOARD_REPO, "hardware", "pinout", "pinout-v1.csv")
DRU = os.path.join(BOARD_REPO, "hardware", "t1-main-board", "t1-main-board.kicad_dru")
FP_LIB = "rockchip.pretty"
FP_NAME = "Rockchip_FCCSP-565L_15.5x14.4mm_P0.4mm_P0.65mm_Ball0.25mm_Pad0.25mm_NSMD"

# ---- geometry and rules (mm). Sources: the RK3566 datasheet and the composed rules (README.md).
CX, CY = 11.0, 11.0          # package centre on the study board
BODY_X, BODY_Y = 15.5, 14.4  # RK3566 DS Rev 1.1 p. 21
BOARD = 22.0
ESCAPE_MARGIN = 0.3          # a route has escaped once it is this far outside the body
AREA_MARGIN = 1.0            # rule area BGA_ESCAPE: the body plus 1.0 mm (the courtyard)
W = 0.08                     # escape track: 0.08 mm (> PCBWay HDI 3 mil normal; CRAFT-43 series)
C = 0.0762                   # copper clearance: 3 mil, PCBWay HDI normal (0.065 mm is the floor)
W_PWR = 0.15                 # power and ground dog-bones and joins on L1 / L10
HOLE_CU_OUT = 6 * 0.0254     # PCBWay HDI hole to copper, outer layers [P2]
# Hole to inner copper: the fab set's 9 mil (PCBWay HDI, 8 layers, normal [P1]). Sensitivity:
# ESCAPE_HOLE_CU_IN_MIL sets another value in the router and adds, to the study's rule copy only,
# a rule at that value limited to BGA_ESCAPE (PCBWay advanced is 6 mil [P2]).
HOLE_CU_IN_MIL = float(os.environ.get("ESCAPE_HOLE_CU_IN_MIL", "9"))
HOLE_CU_IN = HOLE_CU_IN_MIL * 0.0254
OUT = os.environ.get("ESCAPE_OUT", HERE)

HOLE_HOLE = 11 * 0.0254      # PCBWay HDI via hole to hole (mechanical)
MV_D, MV_H = 0.25, 0.10      # first laser level: land / drill (stackup v1 §1, PCB-G-03)
MV2_D, MV2_H = 0.275, 0.125  # second laser level: land / drill (stackup v1 §1, UNVERIFIED)
TH_D, TH_H = 0.46, 0.20      # through via: pad / drill (PCB-G-04 0.45 mm, raised to keep PCBWay's 5 mil ring [P1])
PAD_D = 0.25                 # BGA land (kicad-lib footprint)
EPS = 0.004                  # grid safety margin
S = 0.025                    # router grid step

# Candidate stacks, by study index k from the SoC side (k = 0 is the SoC's outer layer, the
# back of the board; k = n - 1 is L1, the front). Inside the core zone only: other zones use the
# same physical layers for other roles (docs/specs/stackup-v3.md §3).
#   roles     per layer: SIG routing, GND ground, PWR power plane (rails of the "core" or "sys"
#             group, see RAILS)
#   signals   escape layers after the SoC's own, in order of preference; k = 2 is reached by the
#             stacked microvias (SoC side, second laser level), the others by through vias
#   core, sys the plane layer of each rail group
STACKS = {
    # stackup v1: 10 layers, HDI 2+6+2 (docs/specs/stackup-v1.md), for reference
    "v1-10l": dict(roles=["SIG", "GND", "SIG", "GND", "PWR", "PWR", "GND", "SIG", "GND", "SIG"],
                   signals=[2, 7, 9], core=5, sys=4),
    # stackup v2 (superseded): 8 layers, HDI 2+4+2, core-zone map P P G P G F G F (L1..L8;
    # docs/specs/stackup-v2.md), without the decoupling model as it was run for stackup v2:
    # L4 carries the SoC core rails (paired with the L5 ground across 90 µm), L2 the system rails
    # (over the L3 ground), L1 the front decoupling with joins
    "z8": dict(roles=["SIG", "GND", "SIG", "GND", "PWR", "GND", "PWR", "SIG"],
               signals=[2, 7], core=4, sys=6),
    # stackup v3: 6 layers, HDI 2+2+2, core-zone map P P G F G F (L1..L6; docs/specs/stackup-v3.md):
    # L2 (k = 4) carries the SoC core and the system rails, paired with the L3 ground across 90 µm;
    # the core rails also pour on L1 between the decoupling capacitors (front_feed); L4 the inner
    # routing layer; split rails are joined on L4, on the L2 plane through other rails' pours
    # (plane_joins, never on the core-rail layer when it is a layer of its own) and on L1
    "v3": dict(roles=["SIG", "GND", "SIG", "GND", "PWR", "PWR"],
               signals=[2], core=4, sys=4, front_joins=True, decap=True, front_feed=True,
               plane_joins=True, plane_join_set="sys"),
}
STACK = os.environ.get("ESCAPE_STACK", "v3")
ROLES = STACKS[STACK]["roles"]
NL = len(ROLES)
K_MV2 = 2                    # reached by the stacked microvias
K_FRONT = NL - 1             # L1
K_CORE, K_SYS = STACKS[STACK]["core"], STACKS[STACK]["sys"]
SIGNAL_ORDER = STACKS[STACK]["signals"]
FRONT_JOINS = STACKS[STACK].get("front_joins", True)
JOIN_LAYERS = [k for k in SIGNAL_ORDER if 0 < k < NL - 1] + ([K_FRONT] if FRONT_JOINS else []) + [0]
# ESCAPE_PLANE_JOINS=1: a split rail may also be joined by a track on a plane layer, through
# another rail's pour (the refill clears around it; a join that splits another rail is undone
# by the next round's check)
PLANE_JOINS = os.environ.get("ESCAPE_PLANE_JOINS", "1" if STACKS[STACK].get("plane_joins") else "0") == "1"
# ESCAPE_PLANE_JOIN_SET=sys keeps joins off the core-rail layer when it is a layer of its own
# (a join there cuts a core rail's feed corridor)
PLANE_JOIN_SET = os.environ.get("ESCAPE_PLANE_JOIN_SET", STACKS[STACK].get("plane_join_set", "all"))
if PLANE_JOINS:
    _pj = [K_SYS] if PLANE_JOIN_SET == "sys" else sorted({K_CORE, K_SYS})
    JOIN_LAYERS = JOIN_LAYERS[:-1] + _pj + JOIN_LAYERS[-1:]
PLANE_JOIN_W = float(os.environ.get("ESCAPE_PLANE_JOIN_W", str(W)))
CAP_W = float(os.environ.get("ESCAPE_CAP_W", "0.30"))   # capacitor body width on L1 (0201: 0.30, 01005: 0.20)
PLANE_LAYERS = sorted({K_CORE, K_SYS} | ({NL - 1} if STACKS[STACK].get("front_feed") else set()))
DECAP = os.environ.get("ESCAPE_DECAP", "1" if STACKS[STACK].get("decap") else "0") == "1"
# Capacitors under the SoC on the front, per rail (Rockchip HDG 1.1 pp. 35-41): the large ones and
# the 100 nF of each supply; PLL supplies 1 uF + 100 nF each; a 100 nF per GPIO supply.
DECAPS = {"vdd_cpu": 3, "vdd_logic": 5, "vdd_gpu": 3, "vdd_npu": 2, "vcc_ddr": 5, "vcc0v6_ddr": 5,
          "vdda_0v9": 2, "vcca_1v8": 2, "vdda0v9_pmu": 2, "vcca1v8_pmu": 2, "vccio6_1v8": 1,
          "vcc_1v8": 1, "vccio_sd": 1, "vcc3v3_sys": 1, "vcc3v3_pmu": 1}

# Power rails under the core: group and design current (A), from the rail table of power tree
# v0.6 (docs/specs/power-tree-v0.md): the regulator ratings, and for vdd_cpu its 3 A design
# estimate (the TPS6286910C is rated 6 A). The RK3566 design guide (HDG 1.1) gives no per-supply
# current, so these are UNVERIFIED as the SoC's own draw. Rails marked "est" are estimates of the
# SoC's share of a shared rail (UNVERIFIED). "core": the SoC core and LPDDR4X rails; "sys": the
# system rails (stackup v1 §3).
_RAILS = {
    "vdd_cpu": ("core", 3.0), "vdd_logic": ("core", 2.5), "vdd_gpu": ("core", 2.5),
    "vdd_npu": ("core", 1.5), "vcc_ddr": ("core", 1.5), "vcc0v6_ddr": ("core", 0.3),
    "vcca_1v8": ("sys", 0.4), "vdda_0v9": ("sys", 0.4),
    "vcc3v3_sys": ("sys", 0.3),     # est
    "vcc_1v8": ("sys", 0.3),        # est
    "vccio6_1v8": ("sys", 0.1), "vcca1v8_pmu": ("sys", 0.1), "vdda0v9_pmu": ("sys", 0.1),
    "vccio_sd": ("sys", 0.1), "vcc3v3_pmu": ("sys", 0.1),   # est
}
RAILS = {n: (K_CORE if g == "core" else K_SYS, a) for n, (g, a) in _RAILS.items()}
# Optional second plane area for a core rail (ESCAPE_SECOND_FEED=vdd_logic,...): the rail also
# grows on the system-rail layer. Off by default: on z8 a second vdd_logic area on L2 cut
# vdda_0v9 into pieces no join could reconnect (run of 2026-10-25); the feed corridors on the
# rail's own layer (feed_corridors) are used instead.
SECOND_LAYER = {n: K_SYS for n in os.environ.get("ESCAPE_SECOND_FEED", "").split(",") if n}
FRONT_FEED = STACKS[STACK].get("front_feed", False)
if FRONT_FEED:
    SECOND_LAYER.update({n: NL - 1 for n, (g, _) in _RAILS.items() if g == "core"})


def rail_layers(net):
    """Plane layers of a rail: its own, plus the second-feed layer if it has one."""
    if net not in RAILS:
        return ()
    return (RAILS[net][0],) + ((SECOND_LAYER[net],) if net in SECOND_LAYER else ())
VIA_AMPS = 0.5               # PCB-P-09: >= 1 via per 0.5 A (rule of thumb, UNVERIFIED)


def ipc2221_inner_width(amps, rise=10.0, copper_um=18.0):
    """IPC-2221 internal conductor width (mm) for a current at a temperature rise, as PCB-P."""
    area_mil2 = (amps / (0.024 * rise ** 0.44)) ** (1 / 0.725)
    return area_mil2 / (copper_um / 25.4) * 0.0254


def mm(v):
    return int(round(v * 1e6))


def V(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))



def workspace_root(start):
    """The nearest folder above start that holds the workspace's repos.tsv (None outside a workspace):
    the board may sit at any depth (its own repository or a merged root)."""
    d = os.path.abspath(start)
    while True:
        if os.path.isfile(os.path.join(d, "repos.tsv")):
            return d
        up = os.path.dirname(d)
        if up == d:
            return None
        d = up


def kicad_lib_dir():
    env = os.environ.get("ODAP_KICAD_LIB_DIR")
    cands = [env] if env else []
    ws = workspace_root(BOARD_REPO)
    tsv = os.path.join(ws, "repos.tsv") if ws else ""
    if tsv and os.path.exists(tsv):
        with open(tsv) as fh:
            for line in fh:
                f = line.rstrip("\n").split("\t")
                if len(f) == 2 and f[1] == "opendap-project/libs":
                    cands.append(os.path.join(ws, f[0], "kicad"))
    cands.append(os.path.join(BOARD_REPO, "hardware", "lib", "opendap", "kicad"))
    for c in cands:
        if c and os.path.exists(os.path.join(c, "footprints", FP_LIB, FP_NAME + ".kicad_mod")):
            return c
    sys.exit("RK3566 footprint not found in libs (kicad/) (set ODAP_KICAD_LIB_DIR)")


# ------------------------------------------------------------------ obstacle model

class Layer:
    """Exact geometry per copper layer plus a rasterised map of forbidden track centres."""

    def __init__(self, idx, x0, y0, nx, ny):
        self.idx = idx
        self.x0, self.y0, self.nx, self.ny = x0, y0, nx, ny
        self.block = np.zeros((ny, nx), dtype=np.int16)
        self.circles = []   # (x, y, r, net, hole_r, mech); hole_r -1 marks a pad
        self.segs = []      # (x1, y1, x2, y2, w, net)
        self.cb = {}        # circle buckets, 0.5 mm

    def near_circles(self, x, y, reach=1.2):
        k = int(math.ceil(reach / 0.5))
        bx, by = int(math.floor(x / 0.5)), int(math.floor(y / 0.5))
        for i in range(bx - k, bx + k + 1):
            for j in range(by - k, by + k + 1):
                for c in self.cb.get((i, j), ()):
                    yield c

    def cell(self, x, y):
        return int(round((x - self.x0) / S)), int(round((y - self.y0) / S))

    def xy(self, i, j):
        return self.x0 + i * S, self.y0 + j * S

    def _stamp_circle(self, x, y, R, sign):
        i0, i1 = int((x - R - self.x0) / S) - 1, int((x + R - self.x0) / S) + 2
        j0, j1 = int((y - R - self.y0) / S) - 1, int((y + R - self.y0) / S) + 2
        i0, j0 = max(i0, 0), max(j0, 0)
        i1, j1 = min(i1, self.nx), min(j1, self.ny)
        if i0 >= i1 or j0 >= j1:
            return
        xs = self.x0 + np.arange(i0, i1) * S
        ys = self.y0 + np.arange(j0, j1) * S
        d2 = (xs[None, :] - x) ** 2 + (ys[:, None] - y) ** 2
        self.block[j0:j1, i0:i1] += sign * (d2 < R * R).astype(np.int16)

    def _stamp_seg(self, x1, y1, x2, y2, R, sign):
        i0 = int((min(x1, x2) - R - self.x0) / S) - 1
        i1 = int((max(x1, x2) + R - self.x0) / S) + 2
        j0 = int((min(y1, y2) - R - self.y0) / S) - 1
        j1 = int((max(y1, y2) + R - self.y0) / S) + 2
        i0, j0 = max(i0, 0), max(j0, 0)
        i1, j1 = min(i1, self.nx), min(j1, self.ny)
        if i0 >= i1 or j0 >= j1:
            return
        xs = self.x0 + np.arange(i0, i1) * S
        ys = self.y0 + np.arange(j0, j1) * S
        X, Y = np.meshgrid(xs, ys)
        dx, dy = x2 - x1, y2 - y1
        L2 = dx * dx + dy * dy
        t = np.zeros_like(X) if L2 == 0 else np.clip(((X - x1) * dx + (Y - y1) * dy) / L2, 0, 1)
        d2 = (X - x1 - t * dx) ** 2 + (Y - y1 - t * dy) ** 2
        self.block[j0:j1, i0:i1] += sign * (d2 < R * R).astype(np.int16)

    def circle_R(self, r, hole_r, mech, inner):
        R = r + C
        if mech:
            R = max(R, hole_r + (HOLE_CU_IN if inner else HOLE_CU_OUT))
        return R + W / 2 + EPS

    def add_circle(self, x, y, r, net, hole_r=0.0, mech=False, inner=False):
        c = (x, y, r, net, hole_r, mech)
        self.circles.append(c)
        self.cb.setdefault((int(math.floor(x / 0.5)), int(math.floor(y / 0.5))), []).append(c)
        self._stamp_circle(x, y, self.circle_R(r, hole_r, mech, inner), 1)
        return c

    def del_circle(self, c, inner):
        self.circles.remove(c)
        self.cb[(int(math.floor(c[0] / 0.5)), int(math.floor(c[1] / 0.5)))].remove(c)
        self.remove_circle_stamp(c, inner, -1)

    def remove_circle_stamp(self, c, inner, sign):
        x, y, r, net, hole_r, mech = c
        self._stamp_circle(x, y, self.circle_R(r, hole_r, mech, inner), sign)

    def add_seg(self, x1, y1, x2, y2, w, net):
        q = (x1, y1, x2, y2, w, net)
        self.segs.append(q)
        self._stamp_seg(x1, y1, x2, y2, w / 2 + C + W / 2 + EPS, 1)
        return q

    def del_seg(self, q):
        self.segs.remove(q)
        self._stamp_seg(q[0], q[1], q[2], q[3], q[4] / 2 + C + W / 2 + EPS, -1)


def seg_seg_dist(a, b):
    (x1, y1, x2, y2), (x3, y3, x4, y4) = a, b
    def ccw(ax, ay, bx, by, cx, cy):
        return (cx - ax) * (by - ay) - (bx - ax) * (cy - ay)
    d1, d2 = ccw(x3, y3, x4, y4, x1, y1), ccw(x3, y3, x4, y4, x2, y2)
    d3, d4 = ccw(x1, y1, x2, y2, x3, y3), ccw(x1, y1, x2, y2, x4, y4)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        return 0.0
    return min(seg_point_dist(x1, y1, x2, y2, x3, y3), seg_point_dist(x1, y1, x2, y2, x4, y4),
               seg_point_dist(x3, y3, x4, y4, x1, y1), seg_point_dist(x3, y3, x4, y4, x2, y2))


def seg_point_dist(x1, y1, x2, y2, px, py):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - x1 - t * dx, py - y1 - t * dy)


# ------------------------------------------------------------------ router

DIRS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]


def astar(layer, start, is_goal, h, max_expand=400000, window=None, own=()):
    """A* from a cell to any goal cell, avoiding blocked cells. Turn penalty keeps paths straight.
    own: stamps (callables) removed during the search and restored afterwards."""
    for f in own:
        f(-1)
    try:
        blk = layer.block
        si, sj = start
        if window:
            wi0, wj0, wi1, wj1 = window
        else:
            wi0, wj0, wi1, wj1 = 0, 0, layer.nx, layer.ny
        if blk[sj, si] > 0:
            return None
        best = {}
        openq = [(h(si, sj), 0.0, si, sj, -1, None)]
        came = {}
        n = 0
        while openq:
            f, g, i, j, d, parent = heapq.heappop(openq)
            key = (i, j, d)
            if key in came:
                continue
            came[key] = parent
            n += 1
            if n > max_expand:
                return None
            if is_goal(i, j):
                path = []
                k = key
                while k is not None:
                    path.append((k[0], k[1]))
                    k = came[k]
                path.reverse()
                return path
            for nd, (di, dj) in enumerate(DIRS):
                ni, nj = i + di, j + dj
                if ni < wi0 or nj < wj0 or ni >= wi1 or nj >= wj1:
                    continue
                if blk[nj, ni] > 0:
                    continue
                if di and dj and (blk[j, ni] > 0 or blk[nj, i] > 0):
                    continue
                step = 1.4142 if di and dj else 1.0
                turn = 0.0 if d < 0 or d == nd else (0.6 if (nd - d) % 8 in (1, 7) else 3.0)
                ng = g + step + turn
                nk = (ni, nj, nd)
                if nk in came or best.get(nk, 1e18) <= ng:
                    continue
                best[nk] = ng
                heapq.heappush(openq, (ng + h(ni, nj), ng, ni, nj, nd, key))
        return None
    finally:
        for f in own:
            f(1)


def simplify(path):
    if len(path) < 3:
        return path
    out = [path[0]]
    for a, b, c in zip(path, path[1:], path[2:]):
        if (b[0] - a[0], b[1] - a[1]) != (c[0] - b[0], c[1] - b[1]):
            out.append(b)
    out.append(path[-1])
    return out


# ------------------------------------------------------------------ study

class Study:

    def __init__(self):
        self.n = NL
        self.roles = ROLES
        self.board = pcbnew.BOARD()
        self.board.SetCopperLayerCount(NL)
        # study index k -> KiCad layer of L(10 - k): B.Cu, In8.Cu, ..., In1.Cu, F.Cu
        self.cu = [pcbnew.B_Cu] + [getattr(pcbnew, "In%d_Cu" % i) for i in range(NL - 2, 0, -1)] + [pcbnew.F_Cu]
        for k, (lid, role) in enumerate(zip(self.cu, self.roles)):
            self.board.SetLayerName(lid, "L%d_%s" % (NL - k, role))
        hx, hy = BODY_X / 2 + ESCAPE_MARGIN + 0.3, BODY_Y / 2 + ESCAPE_MARGIN + 0.3
        self.x0, self.y0 = -round(hx / S) * S, -round(hy / S) * S
        nx, ny = int(round(2 * -self.x0 / S)) + 1, int(round(2 * -self.y0 / S)) + 1
        self.L = [Layer(k, self.x0, self.y0, nx, ny) for k in range(NL)]
        self.nets = {}
        self.rec = None
        self.result = {"stack": STACK, "soc_side": "L%d (B.Cu)" % NL, "roles": {
            "L%d" % (NL - k): r for k, r in enumerate(ROLES)},
            "hole_to_inner_copper_mil": HOLE_CU_IN_MIL, "escaped": {}, "failed": [],
            "vias": {}, "via_in_pad": [], "shared_power_vias": 0}

    @property
    def pvias(self):
        """net -> [(x, y)]: the through vias of the power rails now on the board (read from
        the obstacle map, so a via removed by a rip-up is gone from it too)."""
        out = {}
        for c in self.L[0].circles:
            if c[5] and c[3] in RAILS:
                out.setdefault(c[3], []).append((c[0], c[1]))
        return out

    @staticmethod
    def lname(k):
        return "L%d" % (NL - k)

    # ---- board items (package frame: origin at the package centre)
    def net(self, name):
        if name not in self.nets:
            ni = pcbnew.NETINFO_ITEM(self.board, name)
            self.board.Add(ni)
            self.nets[name] = ni
        return self.nets[name]

    def track(self, pts, li, w, net):
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(self.board)
            t.SetStart(V(CX + x1, CY + y1))
            t.SetEnd(V(CX + x2, CY + y2))
            t.SetWidth(mm(w))
            t.SetLayer(self.cu[li])
            t.SetNet(self.net(net))
            self.board.Add(t)
            q = self.L[li].add_seg(x1, y1, x2, y2, w, net)
            if self.rec is not None:
                self.rec.append(("s", t, li, q))

    def via(self, x, y, kind, net):
        """kind: 'th' through via; 'mv2' stacked microvias from the SoC side over two laser levels
        (signals to study layer 2); 'mvg' one microvia into the ground plane under the SoC."""
        def add(vtype, a, b, d, h):
            v = pcbnew.PCB_VIA(self.board)
            v.SetViaType(vtype)
            v.SetPosition(V(CX + x, CY + y))
            v.SetLayerPair(self.cu[a], self.cu[b])
            v.SetWidth(mm(d))
            v.SetDrill(mm(h))
            v.SetNet(self.net(net))
            if vtype == pcbnew.VIATYPE_THROUGH and net not in RAILS:
                ps = v.Padstack()
                ps.SetUnconnectedLayerMode(pcbnew.UNCONNECTED_LAYER_MODE_REMOVE_EXCEPT_START_AND_END)
                v.SetPadstack(ps)
            self.board.Add(v)
            if self.rec is not None:
                self.rec.append(("b", v))

        def circ(k, *a):
            c = self.L[k].add_circle(x, y, *a)
            if self.rec is not None:
                self.rec.append(("c", k, c, 0 < k < self.n - 1))
        if self.rec is not None:
            self.rec.append(("v", kind))
        if kind == "th":
            add(pcbnew.VIATYPE_THROUGH, 0, self.n - 1, TH_D, TH_H)
            # signal and ground through vias: non-functional pads removed on inner layers (pads
            # stay on both outer layers and where a track joins), so another net's copper keeps
            # the hole clearance from the barrel, not the copper clearance from a 0.46 mm pad.
            # Power vias keep every pad: KiCad 10.0.7 does not count a plane fill as a connection
            # to a via whose pad on that layer is removed (observed in this study)
            for k in range(self.n):
                inner = 0 < k < self.n - 1
                bare = inner and net not in RAILS     # power vias keep every pad (plane joints)
                circ(k, TH_H / 2 if bare else TH_D / 2, net, TH_H / 2, True, inner)
        elif kind == "mv2":
            add(pcbnew.VIATYPE_MICROVIA, 0, 1, MV_D, MV_H)
            add(pcbnew.VIATYPE_MICROVIA, 1, 2, MV2_D, MV2_H)
            circ(0, MV_D / 2, net, MV_H / 2)
            circ(1, MV2_D / 2, net, MV2_H / 2)
            circ(2, MV2_D / 2, net, MV2_H / 2)
        elif kind == "mvg":
            add(pcbnew.VIATYPE_MICROVIA, 0, 1, MV_D, MV_H)
            circ(0, MV_D / 2, net, MV_H / 2)
            circ(1, MV_D / 2, net, MV_H / 2)
        elif kind == "mvf":
            # front-side stacked microvias L1-L2-L3: a decoupling capacitor's ground
            f = self.n - 1
            add(pcbnew.VIATYPE_MICROVIA, f, f - 1, MV_D, MV_H)
            add(pcbnew.VIATYPE_MICROVIA, f - 1, f - 2, MV2_D, MV2_H)
            circ(f, MV_D / 2, net, MV_H / 2)
            circ(f - 1, MV2_D / 2, net, MV2_H / 2)
            circ(f - 2, MV2_D / 2, net, MV2_H / 2)
        self.result["vias"][kind] = self.result["vias"].get(kind, 0) + 1

    def undo(self, rec):
        for e in reversed(rec):
            if e[0] == "s":
                self.board.Remove(e[1])
                self.L[e[2]].del_seg(e[3])
            elif e[0] == "b":
                self.board.Remove(e[1])
            elif e[0] == "c":
                self.L[e[1]].del_circle(e[2], e[3])
            elif e[0] == "v":
                self.result["vias"][e[1]] -= 1

    # ---- exact clearance check of a via site
    def via_fits(self, x, y, kind, net):
        f = self.n - 1
        layers = {"th": range(self.n), "mv2": (0, 1, 2), "mvg": (0, 1), "mvf": (f, f - 1, f - 2)}[kind]
        for k in layers:
            if kind == "th":
                r, hole, mech = (TH_H / 2 if 0 < k < self.n - 1 and net not in RAILS else TH_D / 2), TH_H / 2, True
            elif kind == "mvf" and k < f:
                r, hole, mech = MV2_D / 2, MV2_H / 2, False
            elif kind == "mv2" and k >= 1:
                r, hole, mech = MV2_D / 2, MV2_H / 2, False
            else:
                r, hole, mech = MV_D / 2, MV_H / 2, False
            inner = 0 < k < self.n - 1
            hcu = HOLE_CU_IN if inner else HOLE_CU_OUT
            for (cx, cy, cr, cnet, chole, cmech) in self.L[k].near_circles(x, y):
                if abs(cx - x) > 1.2 or abs(cy - y) > 1.2:
                    continue
                d = math.hypot(cx - x, cy - y)
                if cnet == net:
                    if d < 1e-6 and k > 0:
                        return False  # no stacking on own items except the L1 pad (via in pad)
                    if mech and cmech and d < hole + chole + HOLE_HOLE:
                        return False  # hole to hole applies whatever the net
                    continue
                # KiCad applies the hole-to-copper rule when either item is a pad or a
                # mechanical via (PCBWay HDI rule condition, observed with KiCad 10.0.7)
                cpad = chole < 0
                need = r + cr + C
                if (mech or cmech or cpad) and hole > 0:
                    need = max(need, hole + hcu + cr)
                if (mech or cmech) and chole > 0:
                    need = max(need, chole + hcu + r)
                if mech and cmech:
                    need = max(need, hole + chole + HOLE_HOLE)
                if d < need:
                    return False
            for (x1, y1, x2, y2, w, snet) in self.L[k].segs:
                if snet == net:
                    continue
                d = seg_point_dist(x1, y1, x2, y2, x, y)
                need = r + w / 2 + C
                if mech:
                    need = max(need, hole + hcu + w / 2)
                if d < need:
                    return False
        return True

    def dogbone_fits(self, x1, y1, x2, y2, w, net):
        for (cx, cy, cr, cnet, chole, cmech) in self.L[0].near_circles((x1 + x2) / 2, (y1 + y2) / 2,
                                                                       math.hypot(x2 - x1, y2 - y1) / 2 + 0.8):
            if cnet == net:
                continue
            if seg_point_dist(x1, y1, x2, y2, cx, cy) < cr + C + w / 2:
                return False
            if cmech and seg_point_dist(x1, y1, x2, y2, cx, cy) < chole + HOLE_CU_OUT + w / 2:
                return False
        for (a, b, c, d, sw, snet) in self.L[0].segs:
            if snet == net:
                continue
            if seg_seg_dist((a, b, c, d), (x1, y1, x2, y2)) < sw / 2 + C + w / 2:
                return False
        return True

    # ---- goals
    def outside(self, x, y):
        return abs(x) >= BODY_X / 2 + ESCAPE_MARGIN or abs(y) >= BODY_Y / 2 + ESCAPE_MARGIN

    def h_out(self, i, j):
        x, y = self.L[0].xy(i, j)
        return max(0.0, min(BODY_X / 2 + ESCAPE_MARGIN - abs(x), BODY_Y / 2 + ESCAPE_MARGIN - abs(y))) / S

    def route_out(self, li, x, y, net, own_circle=None, window_box=None, max_expand=300000):
        lay = self.L[li]
        inner = 0 < li < self.n - 1
        own = []
        if own_circle is not None:
            c = own_circle
            own.append(lambda s, c=c: lay.remove_circle_stamp(c, inner, s))
        start = lay.cell(x, y)
        win = None
        if window_box:
            a, b = lay.cell(window_box[0], window_box[1])
            c2, d2 = lay.cell(window_box[2], window_box[3])
            win = (max(0, min(a, c2)), max(0, min(b, d2)), min(lay.nx, max(a, c2) + 1), min(lay.ny, max(b, d2) + 1))
        path = astar(lay, start, lambda i, j: self.outside(*lay.xy(i, j)), self.h_out, max_expand, win, own)
        if not path:
            return None
        return [lay.xy(i, j) for i, j in simplify(path)]

    # ------------------------------------------------------------------ run
    def run(self, lib_dir):
        # board outline and the BGA_ESCAPE rule area
        r = pcbnew.PCB_SHAPE(self.board)
        r.SetShape(pcbnew.SHAPE_T_RECT)
        r.SetStart(V(0, 0))
        r.SetEnd(V(BOARD, BOARD))
        r.SetLayer(pcbnew.Edge_Cuts)
        r.SetWidth(mm(0.05))
        self.board.Add(r)
        z = pcbnew.ZONE(self.board)
        z.SetIsRuleArea(True)
        z.SetZoneName("BGA_ESCAPE")
        z.SetLayerSet(pcbnew.LSET.AllCuMask())
        for f in ("SetDoNotAllowTracks", "SetDoNotAllowVias", "SetDoNotAllowPads",
                  "SetDoNotAllowZoneFills", "SetDoNotAllowFootprints"):
            getattr(z, f)(False)
        o = z.Outline()
        o.NewOutline()
        ax, ay = BODY_X / 2 + AREA_MARGIN, BODY_Y / 2 + AREA_MARGIN
        for x, y in ((-ax, -ay), (ax, -ay), (ax, ay), (-ax, ay)):
            o.Append(mm(CX + x), mm(CY + y))
        self.board.Add(z)

        # footprint and nets
        fp = pcbnew.FootprintLoad(os.path.join(lib_dir, "footprints", FP_LIB), FP_NAME)
        fp.SetReference("U1")
        fp.SetPosition(V(CX, CY))
        fp.SetFPIDAsString("rockchip:" + FP_NAME)
        self.board.Add(fp)
        self.fp = fp
        fp.Flip(V(CX, CY), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)   # the SoC is on the back
        with open(PINOUT, newline="") as fh:
            rows = {r["ball"]: r for r in csv.DictReader(fh)}
        balls = {}
        seen = {}
        for pad in sorted(fp.Pads(), key=lambda p: p.GetNumber()):
            b = pad.GetNumber()
            row = rows[b]
            p = pad.GetPosition()
            x, y = pcbnew.ToMM(p.x) - CX, pcbnew.ToMM(p.y) - CY
            net = row["net"]
            kind = "nc" if net in ("NC", "") else ("gnd" if row["function"] == "ground" else
                                                     ("pwr" if row["function"] == "power" else "sig"))
            if kind == "sig":
                # a signal net on two balls (joined outside the package on the real board) gets
                # one net per ball here, so each escape is checked on its own
                if net in seen:
                    net = "%s_%s" % (net, b)
                seen[net] = b
            if kind != "nc":
                pad.SetNet(self.net(net))
            balls[b] = dict(x=x, y=y, net=net, kind=kind, ring=not b.startswith("1"))
            self.L[0].add_circle(x, y, PAD_D / 2, net if kind != "nc" else "~" + b, -1.0)
        self.balls = balls

        sig = [b for b, v in balls.items() if v["kind"] == "sig"]
        self.result["used_signal_balls"] = len(sig)
        self.result["power_balls"] = sum(v["kind"] == "pwr" for v in balls.values())
        self.result["ground_balls"] = sum(v["kind"] == "gnd" for v in balls.values())

        def edge_dist(v):
            return min(BODY_X / 2 - abs(v["x"]), BODY_Y / 2 - abs(v["y"]))

        # 1. ring signals on L10 (the SoC side): outward, outer row first, then inner balls through the gaps
        escaped = {}
        for b in sorted([b for b in sig if balls[b]["ring"]], key=lambda b: edge_dist(balls[b])):
            v = balls[b]
            x, y = v["x"], v["y"]
            box = self.out_window(x, y, 1.0)
            own = (x, y, PAD_D / 2, v["net"], -1.0, False)
            path = self.route_out(0, x, y, v["net"], own, box, 60000)
            if path:
                self.track(path, 0, W, v["net"])
                escaped[b] = 1
        self.result["escaped"][self.lname(0)] = len(escaped)

        # 2. vias: ring ground balls first (microvia L10-L9 into the L9 plane)
        gnd = [b for b, v in balls.items() if v["kind"] == "gnd"]
        for b in sorted([b for b in gnd if balls[b]["ring"]], key=lambda b: edge_dist(balls[b])):
            if not self.place_via(b, "gnd"):
                self.result["failed"].append(b)
        # 3. vias for every signal that did not escape on L10 (ring: in the channel; core: at
        # the interstitials, outer core rows also in the channel), outer balls first: stacked
        # microvias L10-L9-L8 first; a through via (L3, L1) only when L8 has no way out
        need_via = [b for b in sig if b not in escaped]
        need_via.sort(key=lambda b: (not balls[b]["ring"], edge_dist(balls[b])))
        pwr = [b for b, v in balls.items() if v["kind"] == "pwr"]
        core_pg = [b for b in pwr + gnd if not balls[b]["ring"]]
        sites = {}
        pwr_sites = {}
        self.ballrec = {}
        later = []
        for b in need_via + sorted(core_pg, key=lambda b: edge_dist(balls[b])):
            role = balls[b]["kind"]
            if role != "sig":
                later.append(b)   # core power and ground: after the signals are routed
                continue
            self.rec = []
            s = self.place_via(b, role)
            self.ballrec[b], self.rec = self.rec, None
            if s and role == "sig":
                sites[b] = s
            elif s and role == "pwr":
                pwr_sites[b] = s
            elif not s:
                later.append(b) if role != "sig" else self.result["failed"].append(b)
        # 4. inner and front layers: route every signal via out, layer by layer (L8, then L3,
        # then L1), vias nearest the package edge first
        order = list(SIGNAL_ORDER)
        todo = sorted(sites, key=lambda b: self.site_edge(sites[b]))
        for li in order:
            done = []
            for b in todo:
                x, y, kind = sites[b]
                if kind == "mv2" and li != K_MV2:
                    continue  # the stacked microvias stop on L8
                net = balls[b]["net"]
                own = next(c for c in self.L[li].circles if c[3] == net and
                           abs(c[0] - x) < 1e-6 and abs(c[1] - y) < 1e-6)
                path = self.route_out(li, x, y, net, own, self.out_window(x, y, 3.0), 250000)
                if not path:
                    path = self.route_out(li, x, y, net, own, None, 500000)
                if path:
                    self.rec = self.ballrec[b]
                    self.track(path, li, W, net)
                    self.rec = None
                    done.append(b)
            self.result["escaped"][self.lname(li)] = len(done)
            todo = [b for b in todo if b not in done]
            print("  %s: %d routed, %d left" % (self.lname(li), len(done), len(todo)), flush=True)
        # rip-up and retry: a signal boxed in on every layer moves its via (routed dog-bone on
        # L10 to any site within 1.3 mm) to the first site from which it escapes, stacked
        # microvias first, then a through via
        moved = {}
        for b in list(todo):
            li = self.retry(b, order)
            if li is None:
                li = self.retry_with_neighbour(b, order, sites)
            if li is not None:
                moved[b] = self.lname(li)
                self.result["escaped"][self.lname(li)] = self.result["escaped"].get(self.lname(li), 0) + 1
                todo.remove(b)
        self.result["moved_vias"] = moved
        self.result["unrouted"] = sorted(todo)
        self.result["failed"] += sorted(todo)

        # 5. core power (through vias, shared between adjacent balls of one rail once the rail
        # has its PCB-P-09 count) and ground (microvias to L9), placed around the routed
        # signals; a ball whose four interstitial sites are taken gets a routed dog-bone
        for b in later:
            role = balls[b]["kind"]
            s = self.place_via(b, role)
            if not s:
                s = self.repair_supply(b, order, sites)
            if s and role == "pwr":
                pwr_sites[b] = s
            elif not s:
                self.result["failed"].append(b)

        self.pwr_sites = pwr_sites
        return self.result

    def broad_sites(self, x, y, rad, step=0.05):
        pts = []
        k = int(rad / step)
        for i in range(-k, k + 1):
            for j in range(-k, k + 1):
                d = math.hypot(i * step, j * step)
                if 0.3 <= d <= rad:
                    pts.append((d, round((x + i * step) / S) * S, round((y + j * step) / S) * S))
        pts.sort()
        return [(px, py) for _, px, py in pts]

    def dogbone_to(self, x, y, px, py, w, net, limit=6000):
        """Straight dog-bone if it fits, else a routed one on L1; adds the track. True on success."""
        if self.dogbone_fits(x, y, px, py, w, net):
            self.track([(x, y), (px, py)], 0, w, net)
            return True
        lay = self.L[0]
        goal = lay.cell(px, py)
        own = (x, y, PAD_D / 2, net, -1.0, False)
        stamp = [lambda sg, c=own: lay.remove_circle_stamp(c, False, sg)]
        path = astar(lay, lay.cell(x, y), lambda i, j: (i, j) == goal,
                     lambda i, j: max(abs(i - goal[0]), abs(j - goal[1])), limit, None, stamp)
        if not path:
            return False
        pts = [lay.xy(i, j) for i, j in simplify(path)]
        pts[0], pts[-1] = (x, y), (px, py)
        self.track(pts, 0, w, net)
        return True

    def route_ball(self, b, px, py, kind, order):
        net = self.balls[b]["net"]
        for li in order:
            if kind == "mv2" and li != K_MV2:
                continue
            own = next(c for c in self.L[li].circles if c[3] == net and
                       abs(c[0] - px) < 1e-6 and abs(c[1] - py) < 1e-6)
            path = self.route_out(li, px, py, net, own, None, 300000)
            if path:
                self.track(path, li, W, net)
                return li
        return None

    def retry_with_neighbour(self, b, order, sites):
        """Rip up one neighbouring signal (via, dog-bone and escape), place and route the boxed
        ball first, then put the neighbour back through its own retry. Kept only if both escape."""
        v = self.balls[b]
        near = sorted((math.hypot(sites[n][0] - v["x"], sites[n][1] - v["y"]), n) for n in sites
                      if n != b and n in self.ballrec and math.hypot(sites[n][0] - v["x"], sites[n][1] - v["y"]) < 1.4)
        for _, n in near:
            saved_n = self.ballrec[n]
            saved_b = self.ballrec.get(b, [])
            n_layer = next((e[2] for e in saved_n if e[0] == "s" and e[2] > 0), None)
            self.undo(saved_n)
            self.ballrec[n] = []
            li = self.retry(b, order)
            if li is not None:
                ln = self.retry(n, order)
                if ln is not None:
                    self.result["escaped"][self.lname(ln)] = self.result["escaped"].get(self.lname(ln), 0) + 1
                    if n_layer is not None:
                        self.result["escaped"][self.lname(n_layer)] -= 1
                    return li
                # restore both as they were
                self.undo(self.ballrec[b])
                self.replay(saved_b)
                self.ballrec[b] = saved_b
            self.replay(saved_n)
            self.ballrec[n] = saved_n
        return None

    def repair_supply(self, b, order, sites):
        """A power or ground ball with no legal via site: move one neighbouring signal's via
        (and its escape) elsewhere, take the freed site, keep it only if the signal escapes."""
        v = self.balls[b]
        near = []
        for n in sites:
            if n not in self.ballrec:
                continue
            d = math.hypot(sites[n][0] - v["x"], sites[n][1] - v["y"])
            for e in self.ballrec[n]:
                if e[0] == "s":
                    q = e[3]
                    d = min(d, seg_point_dist(q[0], q[1], q[2], q[3], v["x"], v["y"]))
            if d < 0.6:
                near.append((d, n))
        near.sort()
        for _, n in near:
            saved_n = self.ballrec[n]
            n_layer = next((e[2] for e in saved_n if e[0] == "s" and e[2] > 0), None)
            self.undo(saved_n)
            self.ballrec[n] = []
            self.rec = []
            s = self.place_via(b, v["kind"])
            rec_b, self.rec = self.rec, None
            if s:
                ln = self.retry(n, order)
                if ln is not None:
                    if n_layer is not None:
                        self.result["escaped"][self.lname(n_layer)] -= 1
                    self.result["escaped"][self.lname(ln)] = self.result["escaped"].get(self.lname(ln), 0) + 1
                    self.result.setdefault("moved_for_supply", {})[n] = b
                    return s
            self.undo(rec_b)
            self.replay(saved_n)
            self.ballrec[n] = saved_n
        return None

    def replay(self, rec):
        """Re-add the items of an undone record (tracks and vias)."""
        new = []
        for e in rec:
            if e[0] == "s":
                t = e[1]
                self.board.Add(t)
                q = self.L[e[2]].add_seg(*e[3])
                new.append(("s", t, e[2], q))
            elif e[0] == "b":
                self.board.Add(e[1])
                new.append(e)
            elif e[0] == "c":
                c = e[2]
                self.L[e[1]].add_circle(c[0], c[1], c[2], c[3], c[4], c[5], e[3])
                new.append(e)
            elif e[0] == "v":
                self.result["vias"][e[1]] += 1
                new.append(e)
        rec[:] = new

    def retry(self, b, order):
        v = self.balls[b]
        x, y, net = v["x"], v["y"], v["net"]
        old = self.ballrec.get(b, [])
        self.undo(old)
        for kind in ("mv2", "th"):
            for px, py in self.broad_sites(x, y, 1.3):
                if not self.via_fits(px, py, kind, net):
                    continue
                self.rec = []
                ok = self.dogbone_to(x, y, px, py, W, net)
                if ok:
                    self.via(px, py, kind, net)
                    li = self.route_ball(b, px, py, kind, order)
                    if li is not None:
                        self.ballrec[b], self.rec = self.rec, None
                        return li
                self.undo(self.rec)
                self.rec = None
        # nothing better: put the original items back
        self.replay(old)
        self.ballrec[b] = old
        return None

    def site_edge(self, s):
        return min(BODY_X / 2 - abs(s[0]), BODY_Y / 2 - abs(s[1]))

    def out_window(self, x, y, lateral):
        """Box from the point to the nearest body side, extended past the escape line."""
        ex, ey = BODY_X / 2 + ESCAPE_MARGIN + 0.2, BODY_Y / 2 + ESCAPE_MARGIN + 0.2
        dx, dy = ex - abs(x), ey - abs(y)
        if dx < dy:
            sx = 1 if x > 0 else -1
            return (min(x - sx * 0.3, sx * ex), y - lateral, max(x - sx * 0.3, sx * ex), y + lateral)
        sy = 1 if y > 0 else -1
        return (x - lateral, min(y - sy * 0.3, sy * ey), x + lateral, max(y - sy * 0.3, sy * ey))

    def candidates(self, b, kind):
        """Via sites around a ball, best first: dog-bone positions on 0.025 mm steps."""
        v = self.balls[b]
        x, y = v["x"], v["y"]
        out = []
        if v["ring"]:
            # into the channel between the ring and the core, then sideways along it
            ix, iy = -np.sign(x) if abs(abs(x) - 7.0) < 1e-6 else 0, -np.sign(y) if abs(abs(y) - 6.4) < 1e-6 else 0
            if abs(abs(x) - 7.4) < 1e-6:
                ix = -np.sign(x)
            if abs(abs(y) - 6.8) < 1e-6:
                iy = -np.sign(y)
            if ix and iy:  # corner balls: outward diagonal first
                cand = [(x - ix * d, y - iy * d) for d in (0.3, 0.35, 0.4)]
                cand += [(x + ix * d, y + iy * d) for d in (0.3, 0.35, 0.4)]
            else:
                cand = []
                depth = (0.825 if ix else 0.875) / 2
                base = abs(abs(x) - 7.4) < 1e-6 or abs(abs(y) - 6.8) < 1e-6  # outer row: farther
                for dd in np.arange(-0.10, 0.11, 0.025):
                    for lat in np.arange(0, 1.61, 0.025):
                        for sgn in ((1,) if lat == 0 else (1, -1)):
                            d = depth + dd + (0.4 if base else 0.0)
                            if ix:
                                cand.append((x + ix * d, y + sgn * lat))
                            else:
                                cand.append((x + sgn * lat, y + iy * d))
                cand.sort(key=lambda p: math.hypot(p[0] - x, p[1] - y))
            if kind == "gnd":
                # ground: also outward: into the gap of the outer row, or outside the body
                ox = np.sign(x) if abs(abs(x) - 7.4) < 1e-6 or abs(abs(x) - 7.0) < 1e-6 else 0
                oy = np.sign(y) if abs(abs(y) - 6.8) < 1e-6 or abs(abs(y) - 6.4) < 1e-6 else 0
                out = []
                for d in (0.4, 0.6, 0.7, 0.8, 1.0, 1.1, 1.2):
                    if ox:
                        out.append((x + ox * d, y))
                    if oy:
                        out.append((x, y + oy * d))
                cand = out + cand
            return [(round(px / S) * S, round(py / S) * S) for px, py in cand]
        # core: the four interstitial sites, then (outer core rows) the channel
        h = 0.325
        cand = [(x + sx * h, y + sy * h) for sx in (1, -1) for sy in (1, -1)]
        # quadrant fan-out: the diagonal pointing away from the package centre first, which
        # gives every ball of a full quadrant its own site
        qx, qy = (1 if x > 1e-6 else -1), (1 if y > 1e-6 else -1)
        cand.sort(key=lambda p: ((np.sign(p[0] - x) != qx) + (np.sign(p[1] - y) != qy),
                                 min(BODY_X / 2 - abs(p[0]), BODY_Y / 2 - abs(p[1]))))
        if kind == "sig":
            extra = []
            for d in np.arange(0.35, 0.56, 0.025):
                for lat in np.arange(-0.5, 0.51, 0.025):
                    for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        px, py = x + sx * d + sy * 0 + (lat if sy else 0), y + sy * d + (lat if sx else 0)
                        if abs(px) > 6.175 + 0.2 or abs(py) > 5.525 + 0.2:
                            extra.append((px, py))
            extra.sort(key=lambda p: math.hypot(p[0] - x, p[1] - y))
            cand = extra + cand if min(BODY_X / 2 - abs(x), BODY_Y / 2 - abs(y)) < 1.7 else cand + extra
        return [(round(px / S) * S, round(py / S) * S) for px, py in cand]

    def place_via(self, b, role):
        v = self.balls[b]
        x, y, net = v["x"], v["y"], v["net"]
        w = W if role == "sig" else W_PWR
        if role == "pwr" and len(self.pvias.get(net, ())) >= self.vias_needed(net):
            # shared via: a through via of the same rail already at one of this ball's
            # interstitial sites (the grid diagonals); one dog-bone, no new hole in the planes
            for px, py in self.candidates(b, role)[:4]:
                if any(abs(px - qx) < 1e-6 and abs(py - qy) < 1e-6 for qx, qy in self.pvias.get(net, ())) \
                        and self.dogbone_fits(x, y, px, py, w, net):
                    self.track([(x, y), (px, py)], 0, w, net)
                    self.result["shared_power_vias"] += 1
                    return (px, py, "shared")
        for px, py in self.candidates(b, role):
            if role == "gnd":
                kind = "mvg"
            elif role == "pwr":
                kind = "th"
            else:
                kind = "mv2"
            if not self.via_fits(px, py, kind, net):
                continue
            straight = self.dogbone_fits(x, y, px, py, w, net)
            if straight:
                self.track([(x, y), (px, py)], 0, w, net)
                self.via(px, py, kind, net)
                return (px, py, kind)
            if role == "sig":
                # a routed dog-bone on L10 to the site
                lay = self.L[0]
                goal = lay.cell(px, py)
                own = (x, y, PAD_D / 2, net, -1.0, False)
                stamp = [lambda s, c=own: lay.remove_circle_stamp(c, False, s)]
                path = astar(lay, lay.cell(x, y), lambda i, j: (i, j) == goal,
                             lambda i, j: max(abs(i - goal[0]), abs(j - goal[1])), 4000, None, stamp)
                if path and len(path) < 120:
                    pts = [lay.xy(i, j) for i, j in simplify(path)]
                    pts[0], pts[-1] = (x, y), (px, py)
                    self.track(pts, 0, w, net)
                    self.via(px, py, kind, net)
                    return (px, py, kind)
        if role == "gnd":
            # ground: join a neighbouring ground ball or ground via on L10 (Rockchip's "#" pattern
            # of ground traces on top, HSPCB p. 26), nearest first
            near = sorted((math.hypot(c[0] - x, c[1] - y), c) for c in self.L[0].circles
                          if c[3] == net and 1e-6 < math.hypot(c[0] - x, c[1] - y) < 0.95)
            for wd in (W_PWR, W):
                for _, c in near:
                    if self.dogbone_fits(x, y, c[0], c[1], wd, net):
                        self.track([(x, y), (c[0], c[1])], 0, wd, net)
                        self.result.setdefault("ground_joined_on_L10", []).append(b)
                        return (c[0], c[1], "shared")
        if role in ("gnd", "pwr"):
            kind = "mvg" if role == "gnd" else "th"
            for px, py in self.broad_sites(x, y, 1.4):
                if not self.via_fits(px, py, kind, net):
                    continue
                if self.dogbone_to(x, y, px, py, W, net, 8000):
                    self.via(px, py, kind, net)
                    self.result.setdefault("routed_dogbones", []).append(b)
                    return (px, py, kind)
        # last resort: microvia in the pad (counted; the study reports it)
        kind = "mvg" if role == "gnd" else ("th" if role == "pwr" else "mv2")
        if self.via_fits(x, y, kind, net):
            self.via(x, y, kind, net)
            self.result["via_in_pad"].append(b)
            return (x, y, kind)
        return None

    # ------------------------------------------------------------------ planes under the core
    HP = 0.325                     # half the core pitch: cells centred on balls and interstitials
    GX0, GY0 = -6.175, -5.525      # first core ball centre (package frame)

    def vias_needed(self, net):
        return max(1, int(math.ceil(RAILS.get(net, (None, 0.0))[1] / VIA_AMPS - 1e-9)))

    def cell_of(self, x, y):
        return int(round((x - self.GX0) / self.HP)), int(round((y - self.GY0) / self.HP))

    def cell_xy(self, a, b):
        return self.GX0 + a * self.HP, self.GY0 + b * self.HP

    def rail_regions(self, k):
        """Partition the core area of plane layer k among its rails: a multi-source
        breadth-first growth from each rail's through vias on a 0.325 mm grid (balls and
        interstitials), out to the BGA_ESCAPE area. Returns {net: set(cells)}."""
        rails = sorted((n for n in RAILS if k in rail_layers(n) and self.pvias.get(n)),
                       key=lambda n: -RAILS[n][1])
        amax = int((BODY_X / 2 + AREA_MARGIN - 0.35 - self.GX0) / self.HP)
        bmax = int((BODY_Y / 2 + AREA_MARGIN - 0.35 - self.GY0) / self.HP)
        amin = -int((BODY_X / 2 + AREA_MARGIN - 0.35 + self.GX0) / self.HP)
        bmin = -int((BODY_Y / 2 + AREA_MARGIN - 0.35 + self.GY0) / self.HP)
        owner = {}
        q = []
        for net in rails:
            for (x, y) in self.pvias[net]:
                a0, b0 = self.cell_of(x, y)
                for da in (-1, 0, 1):
                    for db in (-1, 0, 1):
                        c = (a0 + da, b0 + db)
                        if c not in owner:
                            owner[c] = net
                            q.append(c)
        head = 0
        while head < len(q):
            a, b = q[head]
            head += 1
            for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                c = (a + da, b + db)
                if c in owner or not (amin <= c[0] <= amax and bmin <= c[1] <= bmax):
                    continue
                owner[c] = owner[(a, b)]
                q.append(c)
        self.connect_regions(owner, k)
        self.feed_corridors(owner, k)
        regions = {}
        for c, net in owner.items():
            regions.setdefault(net, set()).add(c)
        return regions

    @staticmethod
    def cell_components(cells):
        cells, comps = set(cells), []
        while cells:
            stack = [cells.pop()]
            comp = set(stack)
            while stack:
                a, b = stack.pop()
                for c in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                    if c in cells:
                        cells.remove(c)
                        comp.add(c)
                        stack.append(c)
            comps.append(comp)
        return comps

    def connect_regions(self, owner, k):
        """Plane plan: a rail whose region came out in pieces gets a corridor of cells through
        its neighbours' regions, one cell (0.325 mm) wide, avoiding cells that hold another net's
        via; a corridor is kept only if every rail it crosses stays in one piece. KiCad's fill
        then decides whether copper passes between the vias along it."""
        foreign = {}
        for net, vias in self.pvias.items():
            if k not in rail_layers(net):
                continue
            for (x, y) in vias:
                foreign[self.cell_of(x, y)] = net
        others = [(c[0], c[1]) for kk in (k,) for c in self.L[kk].circles if c[5] and c[3] not in self.pvias]
        for (x, y) in others:
            foreign[self.cell_of(x, y)] = "~"
        for net in sorted({n for n in owner.values()}, key=lambda n: -RAILS[n][1]):
            for _ in range(8):
                mine = [c for c, n in owner.items() if n == net]
                comps = self.cell_components(mine)
                if len(comps) < 2:
                    break
                comps.sort(key=len, reverse=True)
                src, rest = comps[0], set().union(*comps[1:])
                dist, prev = {c: 0 for c in src}, {}
                heap = [(0, c) for c in src]
                heapq.heapify(heap)
                end = None
                while heap:
                    d, c = heapq.heappop(heap)
                    if d > dist.get(c, 1e9):
                        continue
                    if c in rest:
                        end = c
                        break
                    a, b = c
                    for n2 in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                        if n2 not in owner or (foreign.get(n2, net) != net):
                            continue
                        nd = d + (0 if owner[n2] == net else 1)
                        if nd < dist.get(n2, 1e9):
                            dist[n2], prev[n2] = nd, c
                            heapq.heappush(heap, (nd, n2))
                if end is None:
                    break
                path, c = [], end
                while c in prev:
                    path.append(c)
                    c = prev[c]
                donors = {owner[c] for c in path if owner[c] != net}
                # a donor may already be in pieces on a crowded layer: the corridor is refused
                # only if it adds pieces to a donor
                before = {d: len(self.cell_components([c for c, n in owner.items() if n == d])) for d in donors}
                saved = {c: owner[c] for c in path}
                for c in path:
                    owner[c] = net
                if any(len(self.cell_components([c for c, n in owner.items() if n == d])) > max(1, before[d]) for d in donors):
                    owner.update(saved)
                    break

    def outside_cell(self, c):
        x, y = self.cell_xy(*c)
        return abs(x) > BODY_X / 2 or abs(y) > BODY_Y / 2

    def feed_corridors(self, owner, k):
        """Plane necks against rail currents: a rail whose area crosses the package outline over
        fewer cells than its IPC-2221 width (inner, 18 µm, 10 °C rise, at its design current)
        gets corridors of cells from its area to the outline through its neighbours' areas, one
        cell (0.325 mm) of outline per corridor, avoiding cells that hold another net's via. A
        corridor is kept only if every rail it crosses stays in one piece and keeps its own
        outline width. KiCad's fill then decides how much copper the corridor holds; the result
        reports the filled width (feed_width_mm)."""
        foreign = {}
        for net, vias in self.pvias.items():
            if k in rail_layers(net):
                for (x, y) in vias:
                    foreign[self.cell_of(x, y)] = net
        for (x, y) in [(c[0], c[1]) for c in self.L[k].circles if c[5] and c[3] not in self.pvias]:
            foreign[self.cell_of(x, y)] = "~"
        edge = {c for c in owner if self.outside_cell(c) and any(
            (c[0] + da, c[1] + db) in owner and not self.outside_cell((c[0] + da, c[1] + db))
            for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)))}

        def need(n):
            return int(math.ceil(ipc2221_inner_width(RAILS[n][1]) / self.HP - 1e-9))

        def have(n):
            return sum(1 for c in edge if owner[c] == n)
        carved = {}
        for net in sorted({n for n in owner.values()}, key=lambda n: -RAILS[n][1]):
            for _ in range(64):
                if have(net) >= need(net):
                    break
                src = [c for c, n in owner.items() if n == net]
                dist, prev = {c: 0 for c in src}, {}
                heap = [(0, c) for c in src]
                heapq.heapify(heap)
                end = None
                while heap:
                    d, c = heapq.heappop(heap)
                    if d > dist.get(c, 1e9):
                        continue
                    if c in edge and owner[c] != net:
                        end = c
                        break
                    a, b = c
                    for n2 in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                        if n2 not in owner or foreign.get(n2, net) != net or carved.get(n2, net) != net:
                            continue
                        donor = owner[n2]
                        if donor != net and have(donor) - (1 if n2 in edge else 0) < need(donor):
                            continue
                        nd = d + (0 if donor == net else 1)
                        if nd < dist.get(n2, 1e9):
                            dist[n2], prev[n2] = nd, c
                            heapq.heappush(heap, (nd, n2))
                if end is None:
                    break
                path, c = [], end
                while c in prev:
                    path.append(c)
                    c = prev[c]
                donors = {owner[c] for c in path if owner[c] != net}
                before = {d: len(self.cell_components([c for c, n in owner.items() if n == d])) for d in donors}
                saved = {c: owner[c] for c in path}
                for c in path:
                    owner[c] = net
                bad = any(len(self.cell_components([c for c, n in owner.items() if n == d])) > max(1, before[d])
                          or have(d) < need(d) for d in donors)
                if bad:
                    owner.update(saved)
                    break
                for c in path:
                    carved[c] = net
        self.result.setdefault("feed_cells", {})[self.lname(k)] = {
            n: [have(n), need(n)] for n in sorted({n for n in owner.values()})}

    def add_zone(self, k, net, cells=None, priority=0):
        z = pcbnew.ZONE(self.board)
        z.SetLayer(self.cu[k])
        z.SetNet(self.net(net))
        z.SetLocalClearance(mm(C))
        # PCB-W-01 in BGA_ESCAPE; ESCAPE_RAIL_MIN_W sets a wider minimum for the rail planes
        # (a 0.065 mm sliver of a rail's own fill meeting a join track leaves a neck)
        z.SetMinThickness(mm(0.065 if net == "GND" else float(os.environ.get("ESCAPE_RAIL_MIN_W", "0.065"))))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        z.SetAssignedPriority(priority)
        o = z.Outline()
        if cells is None:
            o.NewOutline()
            for x, y in ((0.5, 0.5), (BOARD - 0.5, 0.5), (BOARD - 0.5, BOARD - 0.5), (0.5, BOARD - 0.5)):
                o.Append(mm(x), mm(y))
        else:
            h = self.HP / 2 + 0.001
            for (a, b) in sorted(cells):
                x, y = self.cell_xy(a, b)
                o.NewOutline()
                for dx, dy in ((-h, -h), (h, -h), (h, h), (-h, h)):
                    o.Append(mm(CX + x + dx), mm(CY + y + dy))
            o.Simplify()
        self.board.Add(z)
        return z

    def build_planes(self):
        self.zones = {}
        for k, role in enumerate(self.roles):
            if role == "GND":
                self.zones[(k, "GND")] = self.add_zone(k, "GND")
        self.regions = {}
        for k in PLANE_LAYERS:
            reg = self.rail_regions(k)
            for p, (net, cells) in enumerate(sorted(reg.items(), key=lambda t: -RAILS[t[0]][1])):
                self.regions[net] = cells
                self.zones[(k, net)] = self.add_zone(k, net, cells, priority=len(reg) - p)

    def fill(self):
        pcbnew.ZONE_FILLER(self.board).Fill(self.board.Zones())

    def islands(self, k, net):
        """Filled outlines of the zone (k, net) as SHAPE_LINE_CHAINs."""
        z = self.zones[(k, net)]
        ps = z.GetFilledPolysList(self.cu[k])
        return [ps.Outline(i) for i in range(ps.OutlineCount())]

    @staticmethod
    def inside(chain, x, y):
        return chain.PointInside(V(CX + x, CY + y))

    def snapshot(self):
        """KiCad connectivity of a saved and reloaded copy: in memory, KiCad 10.0.7 reported
        plane connections that the saved board (and its DRC) did not have."""
        tmp = os.path.join(OUT, ".connectivity-" + STACK + ".kicad_pcb")
        pcbnew.SaveBoard(tmp, self.board)
        copy = pcbnew.LoadBoard(tmp)
        os.remove(tmp)
        copy.BuildConnectivity()
        return copy, copy.GetConnectivity()

    def rail_components(self, net, snap=None):
        """Groups of the rail's through vias that KiCad's connectivity joins (planes, tracks)."""
        copy, conn = snap or self.snapshot()
        vias = list(self.pvias.get(net, ()))
        index = {(round(x, 4), round(y, 4)): i for i, (x, y) in enumerate(vias)}

        def key(item):
            p = item.GetPosition()
            return (round(pcbnew.ToMM(p.x) - CX, 4), round(pcbnew.ToMM(p.y) - CY, 4))
        seen, comps = set(), []
        for t in copy.GetTracks():
            if t.Type() != pcbnew.PCB_VIA_T or t.GetNetname() != net or key(t) not in index:
                continue
            i = index[key(t)]
            if i in seen:
                continue
            group = sorted({index[key(o)] for o in conn.GetConnectedItems(t)
                            if o.Type() == pcbnew.PCB_VIA_T and key(o) in index} | {i})
            seen.update(group)
            comps.append(group)
        return vias, comps

    def ground_clusters(self):
        """Number of separate ground clusters that hold SoC ground balls (KiCad connectivity,
        on a saved and reloaded copy as rail_components)."""
        tmp = os.path.join(OUT, ".connectivity-" + STACK + ".kicad_pcb")
        pcbnew.SaveBoard(tmp, self.board)
        copy = pcbnew.LoadBoard(tmp)
        os.remove(tmp)
        copy.BuildConnectivity()
        conn = copy.GetConnectivity()
        fp = next(f for f in copy.GetFootprints() if f.GetReference() == "U1")
        pads = [p for p in fp.Pads() if p.GetNetname() == "GND"]
        seen, n = set(), 0
        for p in pads:
            if p.GetNumber() in seen:
                continue
            n += 1
            seen.add(p.GetNumber())
            seen.update(o.GetNumber() for o in conn.GetConnectedItems(p) if o.Type() == pcbnew.PCB_PAD_T)
        return n

    def ground_islands(self):
        """L9 fill outlines holding ground microvias but no ground through via and not the
        main plane: each is a set of ground balls cut off from the board's ground."""
        gl9 = self.islands(1, "GND")
        if not gl9:
            return []
        areas = [abs(ch.Area()) for ch in gl9]
        main = areas.index(max(areas))
        mv = [(c[0], c[1]) for c in self.L[1].circles if c[3] == "GND" and not c[5]]
        th = [(c[0], c[1]) for c in self.L[1].circles if c[3] == "GND" and c[5]]
        out = []
        for i, ch in enumerate(gl9):
            if i == main or any(self.inside(ch, x, y) for x, y in th):
                continue
            pts = [(x, y) for x, y in mv if self.inside(ch, x, y)]
            if pts:
                out.append((ch, pts))
        return out

    def repair_ground(self, ch, pts):
        """A ground through via inside a cut-off L9 island joins it to L7, L4 and L2."""
        x0, x1 = min(p[0] for p in pts) - 0.7, max(p[0] for p in pts) + 0.7
        y0, y1 = min(p[1] for p in pts) - 0.7, max(p[1] for p in pts) + 0.7
        a0, b0 = self.cell_of(x0, y0)
        a1, b1 = self.cell_of(x1, y1)
        cands = []
        for a in range(a0, a1 + 1):
            for b in range(b0, b1 + 1):
                x, y = self.cell_xy(a, b)
                if self.inside(ch, x, y):
                    cands.append((min(math.hypot(x - p[0], y - p[1]) for p in pts), x, y))
        for _, x, y in sorted(cands):
            if self.via_fits(x, y, "th", "GND"):
                self.via(x, y, "th", "GND")
                return True
        return False

    def join_on_l1(self, net, vias, comps):
        """Join a rail's separate plane pieces with a track on an inner routing layer, else on
        L1 (the front, where the decoupling sits)."""
        base = comps[0]
        for comp in comps[1:]:
            best = sorted((math.hypot(vias[i][0] - vias[j][0], vias[i][1] - vias[j][1]), i, j)
                          for i in comp for j in base)
            for li, (_, i, j) in [(li, t) for li in JOIN_LAYERS for t in best[:4]]:
                lay = self.L[li]
                (xa, ya), (xb, yb) = vias[i], vias[j]
                goal = lay.cell(xb, yb)
                own = [c for c in lay.circles if c[3] == net]
                if li in (K_CORE, K_SYS):
                    # on a plane layer the join may touch only the two vias it joins: grazing
                    # another via of its rail leaves a copper neck (PCB-W-01)
                    own = [c for c in own if min(math.hypot(c[0] - xa, c[1] - ya), math.hypot(c[0] - xb, c[1] - yb)) < 1e-3]
                inner = 0 < li < self.n - 1
                stamps = [lambda sg, c=c, lay=lay, inner=inner: lay.remove_circle_stamp(c, inner, sg) for c in own]

                start = lay.cell(xa, ya)
                path = astar(lay, start, lambda p, q, g=goal: (p, q) == g,
                             lambda p, q, g=goal: max(abs(p - g[0]), abs(q - g[1])), 600000, None, stamps)
                if path:
                    pts = [lay.xy(p, q) for p, q in simplify(path)]
                    pts[0], pts[-1] = (xa, ya), (xb, yb)
                    on_plane = li in (K_CORE, K_SYS)
                    self.track(pts, li, PLANE_JOIN_W if on_plane else W, net)
                    self.joins.setdefault(net, []).append((i, j))
                    self.result.setdefault("rail_joins", {}).setdefault(net, []).append(self.lname(li))
                    base = base + comp
                    break
            else:
                self.result.setdefault("rail_joins_failed", []).append(net)

    def feed_width(self, net):
        """Copper width of the rail's planes where they cross the package outline (mm), summed
        over its plane layers."""
        hx, hy, st = BODY_X / 2, BODY_Y / 2, 0.01
        pts = [(-hx + i * st, s * hy) for i in range(int(2 * hx / st) + 1) for s in (-1, 1)]
        pts += [(s * hx, -hy + i * st) for i in range(int(2 * hy / st) + 1) for s in (-1, 1)]
        total = 0.0
        for k in rail_layers(net):
            chains = self.islands(k, net)
            total += sum(st for x, y in pts if any(self.inside(ch, x, y) for ch in chains))
        return total

    def cap_keepout(self, x1, y1, x2, y2, w=None, ext=0.15):
        """A capacitor body on L1 as a rule area that keeps zone fills out."""
        z = pcbnew.ZONE(self.board)
        z.SetIsRuleArea(True)
        z.SetZoneName("DECAP_BODY")
        z.SetLayer(pcbnew.F_Cu)
        for f in ("SetDoNotAllowTracks", "SetDoNotAllowVias", "SetDoNotAllowPads", "SetDoNotAllowFootprints"):
            getattr(z, f)(False)
        z.SetDoNotAllowZoneFills(True)
        w = CAP_W + 0.05 if w is None else w
        L = math.hypot(x2 - x1, y2 - y1) or 1e-3
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        nx, ny = -uy * w / 2, ux * w / 2
        # from the edge of the power via's pad (the capacitor's power pad sits on it and joins
        # the pour there) to past the ground microvia
        ax, ay = x1 + ux * (TH_D / 2 + 0.02), y1 + uy * (TH_D / 2 + 0.02)
        bx, by = x2 + ux * ext, y2 + uy * ext
        o = z.Outline()
        o.NewOutline()
        for px, py in ((ax + nx, ay + ny), (bx + nx, by + ny), (bx - nx, by - ny), (ax - nx, ay - ny)):
            o.Append(mm(CX + px), mm(CY + py))
        self.board.Add(z)

    def isolated_decaps(self):
        """Front-side ground stacks of the decoupling model not connected to the SoC's ground."""
        copy, conn = self.snapshot()
        fp = next(f for f in copy.GetFootprints() if f.GetReference() == "U1")
        gpads = {p.GetNumber() for p in fp.Pads() if p.GetNetname() == "GND"}
        iso = []
        for t in copy.GetTracks():
            if t.Type() != pcbnew.PCB_VIA_T or t.GetNetname() != "GND" or t.GetViaType() != pcbnew.VIATYPE_MICROVIA:
                continue
            if not t.IsOnLayer(pcbnew.F_Cu):
                continue
            if not any(o.Type() == pcbnew.PCB_PAD_T and o.GetNumber() in gpads for o in conn.GetConnectedItems(t)):
                p = t.GetPosition()
                iso.append((round(pcbnew.ToMM(p.x) - CX, 4), round(pcbnew.ToMM(p.y) - CY, 4)))
        return iso

    def stitch_isolated_decaps(self):
        """A capacitor whose ground stack lands on a ground island moves: its stack is removed
        and placed again farther from the vias that cut the island (up to three rounds)."""
        moved, left = 0, []
        for _ in range(3):
            iso = self.isolated_decaps()
            if not iso:
                break
            for (x0, y0) in iso:
                for v in list(self.board.GetTracks()):
                    if v.Type() == pcbnew.PCB_VIA_T and v.GetNetname() == "GND" and \
                            abs(pcbnew.ToMM(v.GetPosition().x) - CX - x0) < 1e-3 and \
                            abs(pcbnew.ToMM(v.GetPosition().y) - CY - y0) < 1e-3:
                        self.board.Remove(v)
                done = False
                for rad in (0.6, 0.8, 1.0, 1.3, 1.6, 2.0, 2.5):
                    for a in range(24):
                        t = 2 * math.pi * a / 24
                        x, y = x0 + rad * math.cos(t), y0 + rad * math.sin(t)
                        if abs(x) > BODY_X / 2 or abs(y) > BODY_Y / 2:
                            continue
                        if self.via_fits(x, y, "mvf", "GND"):
                            self.via(x, y, "mvf", "GND")
                            moved += 1
                            done = True
                            break
                    if done:
                        break
            self.fill()
        left = self.isolated_decaps()
        self.result["decap_relocated"] = {"moved": moved, "still_isolated": len(left)}
        print("  decoupling ground stacks moved %d, still isolated %d" % (moved, len(left)), flush=True)

    def place_decoupling(self):
        """Decoupling model: one front-side ground microvia stack per capacitor, within 1.0 mm
        of one of its rail's through vias (the capacitor's power pad sits on that via)."""
        placed, missing = {}, {}
        for net, count in sorted(DECAPS.items()):
            vias = self.pvias.get(net, [])
            got = 0
            for i in range(count):
                done = False
                for rad in (0.45, 0.55, 0.65, 0.8, 1.0):
                    for (vx, vy) in vias[i % max(1, len(vias)):] + vias[:i % max(1, len(vias))]:
                        for a in range(16):
                            t = 2 * math.pi * (a + 0.5 * (i % 2)) / 16
                            x, y = vx + rad * math.cos(t), vy + rad * math.sin(t)
                            if abs(x) > BODY_X / 2 or abs(y) > BODY_Y / 2:
                                continue
                            gk = "mvf"
                            if self.via_fits(x, y, gk, "GND"):
                                self.via(x, y, gk, "GND")
                                # the capacitor body between its two pads on L1: an obstacle
                                # for joins on the front (router map only, not a board item)
                                self.L[self.n - 1].add_seg(vx, vy, x, y, CAP_W, "CAP_" + net)
                                if FRONT_FEED:
                                    self.cap_keepout(vx, vy, x, y)
                                done = True
                                break
                        if done:
                            break
                    if done:
                        break
                got += 1 if done else 0
            placed[net] = got
            if got < count:
                missing[net] = count - got
        self.result["decap_ground_stacks"] = {"placed": placed, "missing": missing}
        # the board stitches every ground layer outside the package (PCB-S-19): ground through
        # vias around the body join the front-side ground the capacitors' stacks land on
        st = 0
        hx, hy = BODY_X / 2 + 0.7, BODY_Y / 2 + 0.7
        for (x, y) in [(sx * hx, sy * f * hy) for sx in (-1, 1) for sy in (-1, 1) for f in (1.0, 0.5, 0.0)] + \
                      [(sx * f * hx, sy * hy) for sx in (-1, 1) for sy in (-1, 1) for f in (0.5, 0.0)]:
            for d in (0.0, 0.2, 0.4, -0.2, -0.4):
                xx, yy = (x + d, y) if abs(y) >= hy - 1e-6 else (x, y + d)
                if self.via_fits(xx, yy, "th", "GND"):
                    self.via(xx, yy, "th", "GND")
                    st += 1
                    break
        self.result["ground_stitching_vias_outside"] = st
        print("  decoupling: %d ground stacks placed, missing %s" % (sum(placed.values()), missing), flush=True)

    def planes(self):
        """Draw and fill the planes, repair cut-off ground islands with through vias, join split
        rails on L1, then record the per-rail figures."""
        self.joins = {}
        self.result["front_joins"] = FRONT_JOINS
        self.result["plane_joins"] = PLANE_JOINS
        self.result["cap_body_w_mm"] = CAP_W
        self.result["decoupling_model"] = DECAP
        if DECAP:
            self.place_decoupling()
        self.build_planes()
        self.fill()
        repairs = 0
        for _ in range(6):
            isl = self.ground_islands()
            if not isl:
                break
            placed = sum(1 for ch, pts in isl if self.repair_ground(ch, pts))
            repairs += placed
            print("  ground islands %d, through vias added %d" % (len(isl), placed), flush=True)
            # a new through via cuts the power planes too: redraw them around it
            for key in [k for k in self.zones if k[1] != "GND"]:
                self.board.Remove(self.zones.pop(key))
            for k in PLANE_LAYERS:
                reg = self.rail_regions(k)
                for p, (net, cells) in enumerate(sorted(reg.items(), key=lambda t: -RAILS[t[0]][1])):
                    self.regions[net] = cells
                    self.zones[(k, net)] = self.add_zone(k, net, cells, priority=len(reg) - p)
            self.fill()
            if not placed:
                break
        self.result["ground_through_vias_added"] = repairs
        self.result["ground_islands_left"] = len(self.ground_islands())
        self.result["ground_clusters_kicad"] = self.ground_clusters()
        # Join split rails. A join on a plane layer cuts the pours of the other rails there once
        # the planes are refilled, so join, refill and look again until no rail is split.
        self.result["join_rounds"] = 0
        for rnd in range(4):
            split = 0
            snap = self.snapshot()
            for net in sorted(RAILS):
                if not self.pvias.get(net):
                    continue
                vias, comps = self.rail_components(net, snap)
                if len(comps) > 1:
                    print("  round %d: %s in %d pieces" % (rnd + 1, net, len(comps)), flush=True)
                for _ in range(4):
                    if len(comps) < 2:
                        break
                    split += 1
                    self.join_on_l1(net, vias, sorted(comps, key=len, reverse=True))
                    vias, comps = self.rail_components(net)
            self.fill()
            self.result["join_rounds"] += 1
            if not split:
                break
        if DECAP:
            self.stitch_isolated_decaps()
        rails = {}
        snap = self.snapshot()
        for net in sorted(RAILS):
            if not self.pvias.get(net):
                continue
            vias, comps = self.rail_components(net, snap)
            amps = RAILS[net][1]
            rails[net] = {
                "layer": "+".join(self.lname(k) for k in rail_layers(net)), "design_current_A": amps,
                "balls": sum(1 for v in self.balls.values() if v["net"] == net),
                "through_vias": len(vias), "vias_needed_PCB_P_09": self.vias_needed(net),
                "plane_pieces_before_joins": None, "plane_pieces": len(comps),
                "feed_width_mm": round(self.feed_width(net), 2),
                "ipc2221_inner_width_mm": round(ipc2221_inner_width(amps), 2),
            }
        for net, js in self.result.get("rail_joins", {}).items():
            rails[net]["plane_pieces_before_joins"] = rails[net]["plane_pieces"] + len(js)
        for r in rails.values():
            if r["plane_pieces_before_joins"] is None:
                r["plane_pieces_before_joins"] = r["plane_pieces"]
        self.result["rails"] = rails

    def drc(self, name):
        """KiCad's DRC on the saved study board with its rule copy: the JSON report."""
        cli = os.environ.get("KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
        out = os.path.join(OUT, "." + name + ".drc.json")
        subprocess.run([cli, "pcb", "drc", "--format", "json", "--severity-all", "-o", out,
                        os.path.join(OUT, name + ".kicad_pcb")], check=True, capture_output=True)
        with open(out) as fh:
            rep = json.load(fh)
        os.remove(out)
        return rep

    def relieve_necks(self, name):
        """Where two joins of one rail meet on a plane layer, the rail's own fill can leave a
        sliver against the corner of the joins: a copper neck (PCB-W-01). The layout draws such
        joins as one track; the study keeps the rail's own fill 0.15 mm off the shared corner
        (a rule area that keeps fills out) and refills. Up to three rounds."""
        tracks = {t.m_Uuid.AsString(): t for t in self.board.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T}
        relieved = []
        for _ in range(3):
            rep = self.drc(name)
            necks = [v for v in rep["violations"] if v["severity"] == "error" and v["type"] == "connection_width"]
            added = 0
            for v in necks:
                items = [tracks.get(it.get("uuid")) for it in v["items"]]
                if len(items) != 2 or None in items or items[0].GetNetname() != items[1].GetNetname() \
                        or items[0].GetNetname() not in RAILS or items[0].GetLayer() != items[1].GetLayer():
                    continue
                ends = lambda t: [(pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)) for p in (t.GetStart(), t.GetEnd())]
                (x, y), _ = min(((p, q) for p in ends(items[0]) for q in ends(items[1])),
                                key=lambda pq: math.hypot(pq[0][0] - pq[1][0], pq[0][1] - pq[1][1]))
                z = pcbnew.ZONE(self.board)
                z.SetIsRuleArea(True)
                z.SetZoneName("NECK_RELIEF")
                z.SetLayer(items[0].GetLayer())
                for f in ("SetDoNotAllowTracks", "SetDoNotAllowVias", "SetDoNotAllowPads", "SetDoNotAllowFootprints"):
                    getattr(z, f)(False)
                z.SetDoNotAllowZoneFills(True)
                o = z.Outline()
                o.NewOutline()
                for i in range(12):
                    a = 2 * math.pi * i / 12
                    o.Append(mm(x + 0.15 * math.cos(a)), mm(y + 0.15 * math.sin(a)))
                self.board.Add(z)
                relieved.append({"net": items[0].GetNetname(), "layer": self.board.GetLayerName(items[0].GetLayer()),
                                 "at_mm": [round(x - CX, 3), round(y - CY, 3)]})
                added += 1
            if not added:
                break
            self.fill()
            self.save()
        self.result["neck_reliefs"] = relieved
        rep = self.drc(name)
        errors = [v for v in rep["violations"] if v["severity"] == "error"]
        self.result["drc"] = {"errors": len(errors), "unconnected": len(rep.get("unconnected_items", [])),
                              "error_types": sorted({v["type"] for v in errors})}
        self.save()
        print("  neck reliefs %d; DRC errors %d, unconnected %d" % (
            len(relieved), self.result["drc"]["errors"], self.result["drc"]["unconnected"]), flush=True)

    def save(self):
        name = "bga-escape-" + STACK
        ds = self.board.GetDesignSettings()
        ds.m_SolderMaskExpansion = 0
        ds.m_SolderMaskMinWidth = mm(3 * 0.0254)   # PCBWay advanced green web [P2]
        pcbnew.SaveBoard(os.path.join(OUT, name + ".kicad_pcb"), self.board)
        with open(DRU) as fh:
            text = fh.read()
        if HOLE_CU_IN_MIL != 9:
            text += ('\n(rule "Study: hole to inner copper under the RK3566"\n\t(layer inner)\n'
                     "\t(condition \"(A.Type == 'Pad' || (A.Type == 'Via' && A.Via_Type != 'Micro')) && "
                     "A.intersectsArea('BGA_ESCAPE')\")\n"
                     "\t(constraint hole_clearance (min %gmil))\n)\n" % HOLE_CU_IN_MIL)
        with open(os.path.join(OUT, name + ".kicad_dru"), "w") as fh:
            fh.write(text)
        zero = {k: 0.0 for k in (
            "min_clearance", "min_connection", "min_copper_edge_clearance", "min_groove_width",
            "min_hole_clearance", "min_hole_to_hole", "min_microvia_diameter", "min_microvia_drill",
            "min_silk_clearance", "min_text_height", "min_text_thickness", "min_through_hole_diameter",
            "min_track_width", "min_via_annular_width", "min_via_diameter")}
        project = {
            "board": {"design_settings": {"rules": zero}},
            "meta": {"filename": name + ".kicad_pro", "version": 3},
            "net_settings": {"classes": [{
                "name": "Default", "priority": 2147483647, "clearance": C, "track_width": W,
                "via_diameter": TH_D, "via_drill": TH_H, "microvia_diameter": MV_D, "microvia_drill": MV_H,
                "diff_pair_gap": 0.1, "diff_pair_width": 0.1, "diff_pair_via_gap": 0.1}],
                "meta": {"version": 4}},
        }
        with open(os.path.join(OUT, name + ".kicad_pro"), "w") as fh:
            json.dump(project, fh, indent=2, sort_keys=True)
            fh.write("\n")
        with open(os.path.join(OUT, name + ".result.json"), "w") as fh:
            json.dump(self.result, fh, indent=1, sort_keys=True)
            fh.write("\n")
        return name


def main():
    pcbnew.KIID.SeedGenerator(1)
    lib = kicad_lib_dir()
    print("%s, inner hole to copper %g mil" % (STACK, HOLE_CU_IN_MIL), flush=True)
    st = Study()
    res = st.run(lib)
    st.planes()
    name = st.save()
    st.relieve_necks(name)
    print("  %s: escaped %s; failed %d; via-in-pad %d; ground islands left %d; rails split %s" % (
        name, res["escaped"], len(res["failed"]), len(res["via_in_pad"]), res["ground_islands_left"],
        {n: r["plane_pieces"] for n, r in res["rails"].items() if r["plane_pieces"] > 1}), flush=True)


if __name__ == "__main__":
    main()
