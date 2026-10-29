#!/usr/bin/env python3
"""T1 main board floorplan v1: zones, area budget per zone and side, and a KiCad study board.

Run with KiCad's Python, from any directory:

    PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
    $PY hardware/studies/floorplan/floorplan.py

Writes, in this folder (FLOORPLAN_OUT=<dir> writes elsewhere):
- floorplan-v1.result.json: the area budget per zone and side (docs/specs/floorplan-v1.md §2);
- floorplan-v1.kicad_pcb / .kicad_pro / .kicad_dru: the outline, the zones and corridors as named
  rule areas, the height and battery areas, the mounting holes and the parts whose position is
  fixed by the product (edge connectors, battery contacts, faceplate connector, SoC, memory, radio
  feeds, microSD), placed from libs kicad/ footprints. Every other part is counted in the budget,
  not placed.

Frame: device frame of PCB-M-04 (origin at the board centre, x across, y along, +y towards the
top wall), drawn in KiCad with the board centre at (100, 100) mm and KiCad's y pointing down
(KiCad y = 100 - device y). "Front" is F.Cu (towards the display), "back" is B.Cu (towards the
battery). Geometry sources are cited where each value is set; UNVERIFIED values are marked.
"""

import json
import os
import re
import shutil
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
BOARD_REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DRU = os.path.join(BOARD_REPO, "hardware", "t1-main-board", "t1-main-board.kicad_dru")
OUT = os.environ.get("FLOORPLAN_OUT", HERE)
NAME = "floorplan-v1"
OX, OY = 100.0, 100.0

# ---- outline (PCB-M-02): cavity 56.3 x 91.1 mm less 0.5 mm per side, both UNVERIFIED
BW, BH = 55.3, 90.1
HX, HY = BW / 2, BH / 2
COPPER_LAYERS = int(os.environ.get("FLOORPLAN_LAYERS", "6"))   # stackup v3

# ---- height areas (ADR 0016; PCB-Z-01 to Z-03; pocket 51.3 mm wide, bands 17.0 / 7.0 mm from the inner walls)
DISPLAY = (54.46, 82.94)                 # E35GH module, centred (its y position UNVERIFIED)
BAND_BOTTOM = 17.0 - 0.5                 # bottom band from the board edge (17.0 mm from the inner wall)
BAND_TOP = 7.0 - 0.5                     # top band
POCKET_W = 51.3                          # pocket footprint on the board (PCB-Z-01)
FP_AREA = (54.0, 10.0)                   # faceplate connection area at the display's bottom edge (UNVERIFIED size)

# ---- zones (floorplan v1 §2): rectangles in the device frame, x0, y0, x1, y1
Y_SPLIT = -8.0                            # core above, bottom zones below
X_AUDIO, X_POWER = -6.2, 6.2             # bottom zones: audio | io | power
Y_RADIO, X_RADIO = 30.0, 3.0             # radio: top-left corner
FP = (-9.5, -HY + (BH - DISPLAY[1]) / 2, 9.5, -HY + (BH - DISPLAY[1]) / 2 + FP_AREA[1])  # FH35C area, front
HAT_STRIP = (X_POWER, -34.0, 20.0, -28.0)   # the HAT flat-cable connector strip (DF40C-50DS), part of the io zone
FRONT = {"F.Cu", "In1.Cu"}                  # layers of the front side's routing and its reference

CW = (-5.0, -28.2, X_POWER, -18.8)          # battery contact window and its margin (ADR 0020)
ZONES = {
    # name: [(rect, layers or None for every copper layer)]
    "CORE": [((-HX, Y_SPLIT, HX, Y_RADIO), None), ((X_RADIO, Y_RADIO, HX, HY), None)],
    "RADIO": [((-HX, Y_RADIO, X_RADIO, HY), None)],
    "AUDIO": [((-HX, -HY, FP[0], Y_SPLIT), None),
              ((FP[0], FP[3], X_AUDIO, Y_SPLIT), None), ((FP[0], -HY, X_AUDIO, FP[1]), None),
              ((FP[0], FP[1], X_AUDIO, FP[3]), "inner_back")],
    # the battery contact window (back) sits in the io column: the power zone owns the back
    # layer there, the io zone every other layer (its routes pass over the window inside the board)
    "IO": [((X_AUDIO, -HY, X_POWER, CW[1]), None), ((X_AUDIO, CW[3], X_POWER, Y_SPLIT), None),
           ((X_AUDIO, CW[1], CW[0], CW[3]), None), ((CW[0], CW[1], X_POWER, CW[3]), "not_back"),
           (HAT_STRIP, None)],
    "POWER": [((FP[2], -HY, HX, HAT_STRIP[1]), None), ((FP[2], HAT_STRIP[3], HX, Y_SPLIT), None),
              ((HAT_STRIP[2], HAT_STRIP[1], HX, HAT_STRIP[3]), None),
              ((X_POWER, HAT_STRIP[3], FP[2], Y_SPLIT), None), ((X_POWER, -HY, FP[2], FP[1]), None),
              ((X_POWER, FP[1], FP[2], HAT_STRIP[1]), "inner_back"),
              ((CW[0], CW[1], X_POWER, CW[3]), "back")],
    "FACEPLATE": [(FP, "front")],
}
# Declared corridors: where a net of one zone may cross another zone (floorplan v1 §3.3).
CORRIDORS = {
    "core-audio": (-11.0, -11.0, -5.0, -5.0),     # I2S, DAC control, MCLK enables
    "core-io": (-4.0, -11.0, 4.0, -5.0),          # USB 2 (USB-C), HAT USB 3 and USB 2, DSI
    "core-power": (8.0, -11.0, 14.0, -5.0),       # PMIC and converter control, sense, enables
    "core-radio": (-22.0, 27.0, -12.0, 33.0),     # SDIO, UART, PCM, radio control
    "io-faceplate": (-9.5, -31.5, 9.5, -27.5),    # DSI and faceplate control into the FH35C area
}

# ---- fixed parts (libs kicad/ footprints), device-frame centre, rotation (deg), side
KLIB = None
PARTS = [
    # ref, library, footprint, x, y, rot, side, fields
    ("U1", "rockchip", "Rockchip_FCCSP-565L_15.5x14.4mm_P0.4mm_P0.65mm_Ball0.25mm_Pad0.25mm_NSMD",
     0.0, 10.0, 0, "B", {"Rework": "BGA", "Thermal": "hot", "Block": "blk.soc"}),
    ("U2", "micron", "LPDDR4_FBGA-200_10.0x15.0mm_Layout12x22_P0.8x0.65mm_Pad0.3mm_NSMD",
     16.75, 11.0, 0, "B", {"Rework": "BGA", "Block": "blk.lpddr4x"}),
    ("U3", "samsung", "Samsung_FBGA-153_11.5x13.0mm_Layout14x14_P0.5mm_Ball0.3mm_Pad0.25mm_NSMD",
     -17.75, 12.0, 0, "B", {"Rework": "BGA", "Block": "blk.emmc"}),
    ("U4", "rockchip", "QFN-68-1EP_7x7mm_P0.35mm_EP5.49x5.49mm_ThermalVias",
     -6.0, -4.5, 0, "B", {"Thermal": "hot", "Block": "blk.pmic"}),
    ("U5", "raspberry-pi", "QFN-60-1EP_7x7mm_P0.4mm_EP3.4x3.4mm_ThermalVias",
     -16.0, 0.0, 0, "F", {"Block": "blk.rp2354"}),
    ("U6", "cirrus-logic", "QFN-40-1EP_5x5mm_P0.4mm_EP3.5x3.5mm_ThermalVias",
     -20.0, -18.0, 0, "B", {"Block": "blk.dac-l"}),
    ("U7", "cirrus-logic", "QFN-40-1EP_5x5mm_P0.4mm_EP3.5x3.5mm_ThermalVias",
     -11.5, -18.0, 0, "B", {"Block": "blk.dac-r"}),
    ("Y1", "ndk", "Oscillator_SMD_NDK_NZ2520SDA-4Pin_2.5x2.0mm", -17.0, -11.0, 0, "B", {"Block": "blk.mclk"}),
    ("Y2", "ndk", "Oscillator_SMD_NDK_NZ2520SDA-4Pin_2.5x2.0mm", -13.0, -11.0, 0, "B", {"Block": "blk.mclk"}),
    # edge parts: "rot" None = the rotation that puts the pad-free nose (the mouth) at the edge;
    # y is then the edge the courtyard is set against (PCB-M-05 order: 3.5, 4.4, USB-C centred)
    ("J1", "same-sky", "Same_Sky_SJ2-35954D-SMT-TR_Jack_3.5mm_TRRS_Horizontal",
     -22.3, "bottom", None, "B", {"Block": "blk.jack-se"}),
    ("J2", "g-switch", "G_Switch_GT-3321667P-01_Jack_4.4mm_5Pole_Horizontal",
     -11.55, "bottom", None, "B", {"Block": "blk.jack-bal"}),
    ("J3", "gct", "GCT_USB4105-GF-A_USB-C_Receptacle_USB2.0_Horizontal",
     0.0, "bottom", None, "B", {"Block": "blk.usb-c"}),
    ("J4", "hirose", "Hirose_DM3AT-SF-PEJM5_microSD_PushPush_Top",
     13.0, "top", None, "B", {"Block": "blk.microsd"}),
    ("J5", "hirose", "Hirose_U.FL-R-SMT-1_Vertical", -18.5, 41.5, 0, "B", {"Block": "blk.antennas"}),
    ("J6", "hirose", "Hirose_U.FL-R-SMT-1_Vertical", -9.0, 41.5, 0, "B", {"Block": "blk.antennas"}),
    # FH35C: in the faceplate connection area, clear of the USB-C and jack through-hole pins
    ("J8", "hirose", "Hirose_FH35C-51S-0.3SHW_1x51-1MP_P0.3mm_Horizontal",
     2.5, -32.9, 0, "F", {"Block": "blk.fp-connector"}),
    ("U8", "texas-instruments", "Texas_RPJ0009A_VQFN-HR-9_1.5x2mm_P0.5mm", 16.0, -18.0, 0, "B",
     {"Thermal": "hot", "Block": "blk.pwr-5v1"}),
]
# Battery contacts (ADR 0020): six KYOCERA AVX 70-9258-001-120-006 on a row at 3.5 mm pitch at the
# pocket's bottom end, order P+, P+, empty, mid-cell tap, NTC, P-, P-; placed on the power side.
CONTACT_PITCH = 3.5
CONTACT_X0, CONTACT_Y = -2.0, -23.5
CONTACT_FP = ("kyocera-avx", "KYOCERA_AVX_9258-100_70-9258-001-120-006_SpringFinger_Pad7.0x2.7mm")
# Mounting holes (PCB-M-08, PCB-H): positions UNVERIFIED until the case; 2.2 mm (M2 class).
HOLES = [(-24.15, 41.55), (24.15, 41.55), (-24.9, -27.0), (24.9, -27.0)]

# ---- drawn, not placed: bodies the budget counts that have no libs kicad/ footprint yet
DRAWN = [
    ("Radio module 2EL (8.2 x 9.3 courtyard, UNVERIFIED size)", -17.0, 32.5, 8.2, 9.3, "B"),
    ("Speaker shadow 15 x 11 (CMS-151125, BOM v1)", 13.5, -39.5, 15.0, 11.0, "B"),
    ("4020 inductor", 24.6, -42.0, 4.4, 4.4, "B"),
    ("4020 inductor", 24.6, -37.4, 4.4, 4.4, "B"),
    ("4020 inductor", 24.6, -32.8, 4.4, 4.4, "B"),
    # Hirose DF40C-50DS-0.4V(51), 12.6 x 3.38 mm, 1.45 mm high (BOM line 66, catalog p. 4); no
    # libs kicad/ footprint yet
    ("HAT flat-cable receptacle DF40C-50DS (12.6 x 3.38 mm)", 13.1, -31.0, 12.6, 3.38, "B"),
]


# ------------------------------------------------------------------ area budget
# Courtyard per zone and height class (mm²). Sources: libs kicad/ footprints (courtyard bounding
# boxes, read by this script where a footprint exists), class estimates from BOM v1.7 parts (est.),
# and the BOM v1.11 to v1.14 changes. F <= 1.0 mm (front under the display or anywhere),
# B <= 1.5 mm (back under the pocket or the bands), T > 1.5 mm (bands only), E edge parts.
# Passives and test pads (1,201 mm², est.) are shared out by an estimated share per zone.
PASSIVES = 1201.0
PASSIVE_SHARE = {"CORE": 0.40, "POWER": 0.20, "AUDIO": 0.20, "IO": 0.13, "RADIO": 0.05, "FACEPLATE": 0.02}
BUDGET = {
    "CORE": [("RK3566", "fp:U1", "B"), ("LPDDR4X", "fp:U2", "B"), ("eMMC", "fp:U3", "B"),
             ("RK809-5", "fp:U4", "F"), ("RP2354A", "fp:U5", "F"), ("microSD DM3AT", "fp:J4", "T"),
             ("TPS62869 vdd_cpu, TPS62827, TPS7A1006, crystals (est.)", 45.0, "F"),
             ("DFE252012F x 7 (est.)", 53.0, "B"),
             ("TPM, expander, EEPROM, LP5521, IMU, NFC reader and tag, haptic driver (est.)", 190.0, "F"),
             ("TSSOP translators (est.)", 95.0, "B"), ("MaskROM combo, buttons ESD (est.)", 30.0, "F"),
             ("LRA haptic actuator (est.)", 110.0, "T")],
    "AUDIO": [("CS43198 x 2", "fp:U6+U7", "F"), ("OPA1622 x 6 (est.)", 74.0, "F"),
              ("LT3045/LT3094 x 4 (est.)", 49.0, "F"), ("TPS62840, MCLK LDOs, dividers (est.)", 20.0, "F"),
              ("NZ2520 oscillators x 2", "fp:Y1+Y2", "F"), ("3.5 mm jack", "fp:J1", "E"),
              ("4.4 mm jack", "fp:J2", "E"), ("jack ESD, mute shunts (est.)", 36.0, "F"),
              ("ambient microphone (est.)", 10.0, "B")],
    "POWER": [("BQ25798, TPS2121, ship FET, sense, BQ28Z610 (est.)", 55.0, "F"),
              ("TPS62136, TPS62903, TPS65131, LMR33630C (libs kicad/, est.; v1.13: one TPS62903)", 65.0, "F"),
              ("4020 inductors x 5 (est.)", 101.0, "T"), ("WE-LHMI (est.)", 23.0, "T"),
              ("NANO2 fuse (est.)", 21.0, "T"), ("eFuses x 3 (#A, #C, #D), TVS2200, TVS0500 (est.)", 45.0, "F"),
              ("INA236 x 4, TPS22919 x 7 (est.)", 74.0, "B"),
              ("battery contacts x 6 (pocket-floor window, PCB-L-05 height exception)", "fp:contacts", "B"), ("speaker shadow", 165.0, "E"),
              ("MAX98357A, TPS61160 and inductor (est.)", 30.0, "F")],
    "IO": [("USB-C USB4105", "fp:J3", "E"), ("DF40C-50DS HAT flat-cable receptacle (catalog 12.6 x 3.38; 1.45 +- 0.15 mm high, band only)", 42.6, "T"),
           ("faceplate load switches TPS22950, TPS22945 (est.)", 15.0, "F"),
           ("FUSB302B x 2 (USB-C, HAT port), USB-C ESD, HAT ESD x 2, AC caps (est.; v1.13: no TMUXHS4412)", 40.0, "F")],
    "RADIO": [("Murata 2EL", 76.0, "B"), ("U.FL x 2", "fp:J5+J6", "B"),
              ("matching, DC block, ESD, feed and ground pads (est.)", 45.0, "F")],
    "FACEPLATE": [("FH35C-51S and approach", "fp:J8", "F"), ("DSI and low-speed ESD (est.)", 10.0, "F")],
}
FACTOR, FACTOR_EDGE = 1.7, 1.2   # placement and routing factor (est., 1.5-1.9), edge parts 1.2


def mm(v):
    return int(round(v * 1e6))


def P(x, y):
    """Device frame to KiCad."""
    return pcbnew.VECTOR2I(mm(OX + x), mm(OY - y))



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
    ws = workspace_root(BOARD_REPO)
    env = os.environ.get("ODAP_KICAD_LIB_DIR")
    cands = [env] if env else []
    tsv = os.path.join(ws, "repos.tsv") if ws else ""
    if tsv and os.path.exists(tsv):
        for line in open(tsv):
            f = line.rstrip("\n").split("\t")
            if len(f) == 2 and f[1] == "opendap-project/libs":
                cands.append(os.path.join(ws, f[0], "kicad"))
    cands.append(os.path.join(BOARD_REPO, "hardware", "lib", "opendap", "kicad"))
    for c in cands:
        if c and os.path.exists(os.path.join(c, "footprints", "rockchip.pretty")):
            return c
    sys.exit("libs kicad/ not found (set ODAP_KICAD_LIB_DIR)")


def courtyard_mm2(fp):
    bb = fp.GetCourtyard(pcbnew.F_CrtYd if not fp.IsFlipped() else pcbnew.B_CrtYd).BBox()
    return pcbnew.ToMM(bb.GetWidth()) * pcbnew.ToMM(bb.GetHeight())


def rect_area(r):
    return max(0.0, r[2] - r[0]) * max(0.0, r[3] - r[1])


def overlap(a, b):
    return rect_area((max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])))


def zone_area(name, side):
    """Board area of a zone on one side (mm²), less the mounting-hole rings (1.4 mm + hole)."""
    tot = 0.0
    for rect, layers in ZONES[name]:
        if layers == "front" and side == "B":
            continue
        if layers in ("inner_back", "back") and side == "F":
            continue
        if layers == "not_back" and side == "B":
            continue
        tot += rect_area(rect)
    for hx, hy in HOLES:
        ring = (hx - 2.5, hy - 2.5, hx + 2.5, hy + 2.5)
        for rect, layers in ZONES[name]:
            if (layers in ("front", "not_back") and side == "B") or (layers in ("inner_back", "back") and side == "F"):
                continue
            tot -= overlap(rect, ring)
    return tot


def pocket_rect():
    return (-POCKET_W / 2, -HY + BAND_BOTTOM, POCKET_W / 2, HY - BAND_TOP)


def back_split(name):
    """A zone's back area split into under-the-pocket (<= 1.5 mm) and band (tall parts) area."""
    pocket = band = 0.0
    for rect, layers in ZONES[name]:
        if layers in ("front", "not_back"):
            continue
        a = rect_area(rect)
        p = overlap(rect, pocket_rect())
        pocket += p
        band += a - p
    return pocket, band


# ------------------------------------------------------------------ board

class Floorplan:
    def __init__(self):
        self.board = pcbnew.BOARD()
        self.board.SetCopperLayerCount(COPPER_LAYERS)
        self.lib = kicad_lib_dir()
        self.fps = {}

    def cu_layers(self, which):
        if which is None:
            return pcbnew.LSET.AllCuMask(COPPER_LAYERS)
        ls = pcbnew.LSET()
        if which == "front":
            for name in FRONT:
                ls.AddLayer(self.board.GetLayerID(name))
        elif which == "back":
            ls.AddLayer(pcbnew.B_Cu)
        elif which == "not_back":
            for lid in pcbnew.LSET.AllCuMask(COPPER_LAYERS).CuStack():
                if lid != pcbnew.B_Cu:
                    ls.AddLayer(lid)
        elif which == "inner_back":
            for lid in pcbnew.LSET.AllCuMask(COPPER_LAYERS).CuStack():
                if self.board.GetLayerName(lid) not in FRONT:
                    ls.AddLayer(lid)
        else:
            for name in which:
                ls.AddLayer(self.board.GetLayerID(name))
        return ls

    def rule_area(self, name, rect, layers=None, keep_fill=True):
        z = pcbnew.ZONE(self.board)
        z.SetIsRuleArea(True)
        z.SetZoneName(name)
        z.SetLayerSet(self.cu_layers(layers))
        for f in ("SetDoNotAllowTracks", "SetDoNotAllowVias", "SetDoNotAllowPads",
                  "SetDoNotAllowFootprints"):
            getattr(z, f)(False)
        z.SetDoNotAllowZoneFills(not keep_fill)
        o = z.Outline()
        o.NewOutline()
        x0, y0, x1, y1 = rect
        for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            o.Append(P(x, y))
        self.board.Add(z)

    def drawing(self, rect, layer, width=0.1):
        s = pcbnew.PCB_SHAPE(self.board)
        s.SetShape(pcbnew.SHAPE_T_RECT)
        s.SetStart(P(rect[0], rect[3]))
        s.SetEnd(P(rect[2], rect[1]))
        s.SetLayer(layer)
        s.SetWidth(mm(width))
        self.board.Add(s)

    def text(self, x, y, msg, layer, size=0.8):
        t = pcbnew.PCB_TEXT(self.board)
        t.SetText(msg)
        t.SetPosition(P(x, y))
        t.SetLayer(layer)
        t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
        t.SetTextThickness(mm(size / 8))
        self.board.Add(t)

    def footprint(self, ref, lib, name, x, y, rot, side, fields, netname=None):
        fp = pcbnew.FootprintLoad(os.path.join(self.lib, "footprints", lib + ".pretty"), name)
        fp.SetReference(ref)
        fp.SetFPIDAsString(lib + ":" + name)
        self.board.Add(fp)
        edge = y if isinstance(y, str) else None
        y0 = 0.0 if edge else y
        fp.SetPosition(P(x, y0))
        if side == "B":
            fp.Flip(P(x, y0), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        if edge:
            # the rotation whose pads sit farthest from the edge: the nose faces the edge
            best = None
            for r in (0, 90, 180, 270):
                fp.SetOrientationDegrees(r)
                cy = fp.GetCourtyard(pcbnew.B_CrtYd if side == "B" else pcbnew.F_CrtYd).BBox()
                pads = [pcbnew.ToMM(pd.GetPosition().y) for pd in fp.Pads()]
                if edge == "bottom":    # KiCad y grows downward: the bottom edge is the largest y
                    score = pcbnew.ToMM(cy.GetBottom()) - sum(pads) / len(pads)
                else:
                    score = sum(pads) / len(pads) - pcbnew.ToMM(cy.GetTop())
                if best is None or score > best[0]:
                    best = (score, r)
            fp.SetOrientationDegrees(best[1])
            cy = fp.GetCourtyard(pcbnew.B_CrtYd if side == "B" else pcbnew.F_CrtYd).BBox()
            target = OY + HY if edge == "bottom" else OY - HY
            shift = target - pcbnew.ToMM(cy.GetBottom() if edge == "bottom" else cy.GetTop())
            cx = (pcbnew.ToMM(cy.GetLeft()) + pcbnew.ToMM(cy.GetRight())) / 2
            fp.Move(pcbnew.VECTOR2I(mm(OX + x - cx), mm(shift)))
        elif rot:
            fp.SetOrientationDegrees(rot)
        for k, v in fields.items():
            fp.SetField(k, v)
            fp.GetField(k).SetVisible(False)
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
        # one net per part: the study has no wiring; pads of one part are not each other's
        # foreign copper, pads of two parts are
        net = self.board.FindNet(netname or ("P_" + ref))
        if net is None:
            net = pcbnew.NETINFO_ITEM(self.board, netname or ("P_" + ref))
            self.board.Add(net)
        for pd in fp.Pads():
            if pd.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH:
                pd.SetNet(net)
        self.fps[ref] = fp
        return fp

    def hole(self, ref, x, y, d=2.2):
        fp = pcbnew.FOOTPRINT(self.board)
        fp.SetReference(ref)
        fp.SetValue("MountingHole_2.2mm")
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
        fp.SetPosition(P(x, y))
        fp.SetAttributes(pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_EXCLUDE_FROM_BOM)
        pad = pcbnew.PAD(fp)
        pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
        pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
        pad.SetSize(pcbnew.VECTOR2I(mm(d), mm(d)))
        pad.SetDrillSize(pcbnew.VECTOR2I(mm(d), mm(d)))
        pad.SetLayerSet(pad.UnplatedHoleMask())
        pad.SetPosition(P(x, y))
        fp.Add(pad)
        self.board.Add(fp)

    def build(self):
        b = self.board
        self.drawing((-HX, -HY, HX, HY), pcbnew.Edge_Cuts, 0.05)
        # zones and corridors
        for name, rects in ZONES.items():
            for rect, layers in rects:
                self.rule_area("ZONE_" + name, rect, layers)
        for key, rect in CORRIDORS.items():
            self.rule_area("ZONE_CORRIDOR", rect)
        # product areas the rules already use
        self.rule_area("BATTERY_POCKET", (pocket_rect()[0] - 3, pocket_rect()[1] - 3,
                                          pocket_rect()[2] + 3, pocket_rect()[3] + 3), ["B.Cu"])
        cx = [CONTACT_X0 + k * CONTACT_PITCH for k in range(7)]
        win = (cx[0] - 1.35 - 1.0, CONTACT_Y - 3.5 - 1.0, cx[-1] + 1.35 + 1.0, CONTACT_Y + 3.5 + 1.0)
        self.rule_area("BATTERY_CONNECTOR", win, ["B.Cu"])
        self.rule_area("BATTERY_CONTACT_EMPTY", (cx[2] - 1.35, CONTACT_Y - 3.5, cx[2] + 1.35, CONTACT_Y + 3.5),
                       ["B.Cu"])
        self.rule_area("BATTERY_ESD", (cx[3] - 1.35 - 3, CONTACT_Y - 3.5 - 3, cx[4] + 1.35 + 3, CONTACT_Y + 3.5 + 3),
                       ["B.Cu"])
        self.rule_area("AUDIO_ANALOG", (-HX, -HY, X_AUDIO, -14.0))
        sx, sy = 15.5 / 2 + 1.0, 14.4 / 2 + 1.0
        self.rule_area("BGA_ESCAPE", (-sx, 10.0 - sy, sx, 10.0 + sy))
        # height areas, drawn on User.1 (front) and User.2 (back) with their limits
        dy = (BH - DISPLAY[1]) / 2
        disp = (-DISPLAY[0] / 2, -HY + dy, DISPLAY[0] / 2, HY - dy)
        self.drawing(disp, pcbnew.User_1)
        self.text(0, HY - dy - 1.5, "PCB-Z-03 front under the display: parts <= 1.0 mm", pcbnew.User_1)
        self.drawing(FP, pcbnew.User_1)
        self.text(0, FP[3] - 1.0, "faceplate connection area: FH35C and its ESD only", pcbnew.User_1, 0.6)
        self.drawing(pocket_rect(), pcbnew.User_2)
        self.text(0, pocket_rect()[3] - 1.5, "PCB-Z-01 back under the pocket: parts <= 1.5 mm", pcbnew.User_2)
        self.text(0, -HY + 1.2, "PCB-Z-02 bottom band <= 14.2 mm", pcbnew.User_2, 0.6)
        self.text(0, HY - 1.2, "PCB-Z-02 top band <= 14.2 mm", pcbnew.User_2, 0.6)
        for label, x, y, w, h, side in DRAWN:
            self.drawing((x - w / 2, y - h / 2, x + w / 2, y + h / 2), pcbnew.User_2)
        for name, rects in ZONES.items():
            r = rects[0][0]
            self.text((r[0] + r[2]) / 2, (r[1] + r[3]) / 2, name, pcbnew.User_3, 1.5)
        # parts
        for ref, lib, name, x, y, rot, side, fields in PARTS:
            self.footprint(ref, lib, name, x, y, rot, side, fields)
        order = ["PWR_BAT_P", "PWR_BAT_P", None, "BAT_SENSE_MID", "BAT_SENSE_NTC", "PWR_BAT_N", "PWR_BAT_N"]
        n = 0
        for k, net in enumerate(order):
            if net is None:
                continue
            n += 1
            self.footprint("J%d" % (20 + n), CONTACT_FP[0], CONTACT_FP[1],
                           CONTACT_X0 + k * CONTACT_PITCH, CONTACT_Y, 90, "B", {"Block": "blk.charger"}, net)
        for i, (x, y) in enumerate(HOLES, 1):
            self.hole("H%d" % i, x, y)

    def budget(self):
        res = {"factor": FACTOR, "factor_edge": FACTOR_EDGE, "zones": {}}
        contacts = sum(courtyard_mm2(fp) for r, fp in self.fps.items() if r.startswith("J2") and len(r) == 3)
        for zname, items in BUDGET.items():
            rows, need = [], {"F": 0.0, "B": 0.0, "T": 0.0, "E": 0.0}
            for label, src, cls in items:
                if isinstance(src, str):
                    refs = src[3:].split("+")
                    a = contacts if refs == ["contacts"] else sum(courtyard_mm2(self.fps[r]) for r in refs)
                    source = "libs kicad/ courtyard"
                else:
                    a, source = src, "estimate"
                rows.append({"item": label, "courtyard_mm2": round(a, 1), "class": cls, "source": source})
                need[cls] += a
            pas = PASSIVES * PASSIVE_SHARE[zname]
            rows.append({"item": "passives and test pads (share, est.)", "courtyard_mm2": round(pas, 1),
                         "class": "F", "source": "estimate, share est."})
            need["F"] += pas
            board_need = {k: v * (FACTOR_EDGE if k == "E" else FACTOR) for k, v in need.items()}
            front = zone_area(zname, "F")
            back = zone_area(zname, "B")
            pocket, band = back_split(zname)
            # placement: tall and edge parts in the band, B parts on the back, F parts on the
            # back's leftover first (the SoC side's under-pocket area), then on the front
            band_need = board_need["T"] + board_need["E"]
            back_need = board_need["B"]
            back_left = max(0.0, back - band_need - back_need)
            f_back = min(board_need["F"], back_left)
            f_front = board_need["F"] - f_back
            res["zones"][zname] = {
                "items": rows, "courtyard_mm2": {k: round(v, 1) for k, v in need.items()},
                "board_need_mm2": round(sum(board_need.values()), 1),
                "front_area_mm2": round(front, 1), "back_area_mm2": round(back, 1),
                "back_pocket_mm2": round(pocket, 1), "back_band_mm2": round(band, 1),
                "band_need_mm2": round(band_need, 1), "band_use_pct": round(100 * band_need / band, 1) if band else None,
                "back_need_mm2": round(band_need + back_need + f_back, 1),
                "front_need_mm2": round(f_front, 1),
                "back_use_pct": round(100 * (band_need + back_need + f_back) / back, 1) if back else None,
                "front_use_pct": round(100 * f_front / front, 1) if front else None,
            }
        tot_need = sum(z["board_need_mm2"] for z in res["zones"].values())
        res["total_need_mm2"] = round(tot_need, 1)
        res["board_both_sides_mm2"] = round(2 * BW * BH, 1)
        res["total_use_pct"] = round(100 * tot_need / (2 * BW * BH), 1)
        return res

    def save(self, budget):
        pcbnew.SaveBoard(os.path.join(OUT, NAME + ".kicad_pcb"), self.board)
        shutil.copyfile(DRU, os.path.join(OUT, NAME + ".kicad_dru"))
        with open(os.path.join(OUT, NAME + ".kicad_pro"), "w") as fh:
            json.dump({"meta": {"filename": NAME + ".kicad_pro", "version": 3},
                       "board": {"design_settings": {
                           "rules": {"min_clearance": 0.0},
                           # no wiring in a floorplan: every part is one net, never routed
                           "rule_severities": {"unconnected_items": "ignore"}}},
                       "net_settings": {"meta": {"version": 4}, "classes": [
                           {"name": "Default", "priority": 2147483647, "clearance": 0.1, "track_width": 0.1},
                           {"name": "PWR_BAT", "priority": 0, "clearance": 0.1, "track_width": 0.1},
                           {"name": "BAT_SENSE", "priority": 1, "clearance": 0.1, "track_width": 0.1}],
                           "netclass_patterns": [{"netclass": "PWR_BAT", "pattern": "PWR_BAT_*"},
                                                 {"netclass": "BAT_SENSE", "pattern": "BAT_SENSE_*"}]}},
                      fh, indent=2)
            fh.write("\n")
        with open(os.path.join(OUT, NAME + ".result.json"), "w") as fh:
            json.dump(budget, fh, indent=1, sort_keys=True)
            fh.write("\n")


def main():
    pcbnew.KIID.SeedGenerator(2)
    f = Floorplan()
    f.build()
    budget = f.budget()
    f.save(budget)
    for z, r in budget["zones"].items():
        print("%-10s need %7.1f mm2 | back %6.1f (band %5.1f %% of %5.1f) %5.1f %% | front %6.1f %5s %%" % (
            z, r["board_need_mm2"], r["back_area_mm2"], r["band_use_pct"] or 0, r["back_band_mm2"],
            r["back_use_pct"] or 0, r["front_area_mm2"], r["front_use_pct"]))
    print("total need %.0f mm2 of %.0f (%.0f %%)" % (budget["total_need_mm2"], budget["board_both_sides_mm2"],
                                                  budget["total_use_pct"]))


if __name__ == "__main__":
    main()
