"""Board geometry of the T1 main board: outline, height areas, zones, corridors, holes (pure Python).

Device frame of PCB-M-04: origin at the board centre, x across, y along, +y towards the top wall,
millimetres. KiCad draws the board centre at (100, 100) mm with its y pointing down
(KiCad y = 100 - device y). "Front" is F.Cu (towards the display), "back" is B.Cu (towards the
battery). Every value cites its source; values the case has not fixed are marked UNVERIFIED.
The zones and corridors are floorplan v1's (docs/specs/floorplan-v1.md §2, §4), the same rectangles
as the floorplan study (hardware/studies/floorplan/floorplan.py).
"""

from __future__ import annotations

OX, OY = 100.0, 100.0

# Outline (PCB-M-02): cavity 56.3 x 91.1 mm (body 59.5 x 94.3 mm less 1.6 mm walls, UNVERIFIED)
# less 0.5 mm per side (UNVERIFIED); square corners until the case gives its radii (CRAFT-35).
BW, BH = 55.3, 90.1
HX, HY = BW / 2, BH / 2

# Height areas (ADR 0016; PCB-Z-01 to Z-04)
DISPLAY = (54.46, 82.94)                 # display module, centred (ADR 0016; position UNVERIFIED)
DISP = (-DISPLAY[0] / 2, -DISPLAY[1] / 2, DISPLAY[0] / 2, DISPLAY[1] / 2)
BAND_BOTTOM = 17.0 - 0.5                 # PCB-Z-02: bottom band 17.0 mm from the inner wall
BAND_TOP = 7.0 - 0.5                     # PCB-Z-02: top band 7.0 mm from the inner wall
POCKET_W = 51.3                          # PCB-Z-01: pocket footprint width on the board
POCKET = (-POCKET_W / 2, -HY + BAND_BOTTOM, POCKET_W / 2, HY - BAND_TOP)
FP_AREA_H = 10.0                         # faceplate connection area depth (ADR 0016 item 1, UNVERIFIED)

H_FRONT_DISPLAY = 1.0                    # PCB-Z-03
H_FRONT_OUTSIDE = 6.8                    # PCB-Z-04 (UNVERIFIED)
H_BACK_POCKET = 1.5                      # PCB-Z-01
H_BACK_BAND = 14.2                       # PCB-Z-02
H_CONTACT_WINDOW = 3.3                   # PCB-L-05: free height at the battery-contact window

# Zones (floorplan v1 §2): rectangles x0, y0, x1, y1 with the layers they cover
Y_SPLIT = -8.0
X_AUDIO, X_POWER = -6.2, 6.2
Y_RADIO, X_RADIO = 30.0, 3.0
FP = (-9.5, DISP[1], 9.5, DISP[1] + FP_AREA_H)          # faceplate connection area (zone FACEPLATE)
HAT_STRIP = (X_POWER, -34.0, 20.0, -28.0)
CW = (-5.0, -28.2, X_POWER, -18.8)                      # battery contact window and margin (floorplan)

# layer sets: None = every copper layer; "front" = F.Cu + In1.Cu; "back" = B.Cu;
# "not_back" = all but B.Cu; "inner_back" = all but F.Cu and In1.Cu
ZONES = {
    "CORE": [((-HX, Y_SPLIT, HX, Y_RADIO), None), ((X_RADIO, Y_RADIO, HX, HY), None)],
    "RADIO": [((-HX, Y_RADIO, X_RADIO, HY), None)],
    "AUDIO": [((-HX, -HY, FP[0], Y_SPLIT), None),
              ((FP[0], FP[3], X_AUDIO, Y_SPLIT), None), ((FP[0], -HY, X_AUDIO, FP[1]), None),
              ((FP[0], FP[1], X_AUDIO, FP[3]), "inner_back")],
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
CORRIDORS = {
    "core-audio": (-11.0, -11.0, -5.0, -5.0),
    "core-io": (-4.0, -11.0, 4.0, -5.0),
    "core-power": (8.0, -11.0, 14.0, -5.0),
    "core-radio": (-22.0, 27.0, -12.0, 33.0),
    "io-faceplate": (-9.5, -31.5, 9.5, -27.5),
}

# Mounting holes (PCB-M-08, PCB-H): positions UNVERIFIED until the case; 2.2 mm (M2 class)
HOLES = [(-24.15, 41.55), (24.15, 41.55), (-24.9, -27.0), (24.9, -27.0)]
HOLE_D = 2.2
H01_RING = 1.4        # PCB-H-01: courtyards 1.4 mm from the hole edge (UNVERIFIED screw)
H05_MLCC = 3.0        # PCB-H-05: MLCC courtyard 3 mm from the hole edge (UNVERIFIED)
B01_EDGE = 0.3        # PCB-B-01: courtyard 0.3 mm from the board edge (J*, SW* exempt)
D01_BGA = 2.0         # PCB-D-01: BGA rework clearance, courtyard to courtyard (UNVERIFIED)

# Battery contacts (ADR 0020 item 2; PCB-L-04): seven positions at 3.5 mm pitch, the third empty
CONTACT_PITCH = 3.5
CONTACT_X0, CONTACT_Y = -2.0, -23.5
CONTACT_PAD = (2.7, 7.0)            # pad across x, along y after the 90° rotation (PCB-L-04)


def contact_x(k: int) -> float:
    return CONTACT_X0 + k * CONTACT_PITCH


def contact_window():
    """Rule area BATTERY_CONNECTOR: the contact pads' extent plus 1 mm (PCB-L-05)."""
    return (contact_x(0) - CONTACT_PAD[0] / 2 - 1.0, CONTACT_Y - CONTACT_PAD[1] / 2 - 1.0,
            contact_x(6) + CONTACT_PAD[0] / 2 + 1.0, CONTACT_Y + CONTACT_PAD[1] / 2 + 1.0)


def contact_esd_area():
    """Rule area BATTERY_ESD: the mid-cell and NTC pads grown by 3 mm (PCB-L-08, UNVERIFIED)."""
    return (contact_x(3) - CONTACT_PAD[0] / 2 - 3.0, CONTACT_Y - CONTACT_PAD[1] / 2 - 3.0,
            contact_x(4) + CONTACT_PAD[0] / 2 + 3.0, CONTACT_Y + CONTACT_PAD[1] / 2 + 3.0)


def contact_empty():
    """Rule area BATTERY_CONTACT_EMPTY: the empty position (PCB-L-04)."""
    return (contact_x(2) - CONTACT_PAD[0] / 2, CONTACT_Y - CONTACT_PAD[1] / 2,
            contact_x(2) + CONTACT_PAD[0] / 2, CONTACT_Y + CONTACT_PAD[1] / 2)


def battery_pocket_area():
    """Rule area BATTERY_POCKET: the pocket footprint grown by 3 mm (PCB-L-01, UNVERIFIED margin)."""
    return (POCKET[0] - 3, POCKET[1] - 3, POCKET[2] + 3, POCKET[3] + 3)


# Speaker (BOM v1 line 33, Same Sky CMS-151125-078S-67): spring contacts on gold pads; its body sits
# over the board in the bottom band, right of the USB-C (PCB-M-05). Shadow 15 x 11 mm at the floorplan's
# position (floorplan study; 15 x 11 is the part's outline from BOM v1, its position UNVERIFIED).
SPEAKER = (13.5 - 7.5, -39.5 - 5.5, 13.5 + 7.5, -39.5 + 5.5)

LAYER_SETS = {
    None: ("F", "B"), "front": ("F",), "back": ("B",), "not_back": ("F",), "inner_back": ("B",),
}


def zone_rects(zone: str, side: str):
    """Rectangles of a zone on one side's outer layer ("F" or "B")."""
    return [r for r, layers in ZONES[zone] if side in LAYER_SETS[layers]]


def height_areas(side: str):
    """(rect, max height) pairs covering one side; later entries override earlier ones."""
    board = (-HX, -HY, HX, HY)
    if side == "F":
        return [(board, H_FRONT_OUTSIDE), (DISP, H_FRONT_DISPLAY)]
    return [(board, H_BACK_BAND), (POCKET, H_BACK_POCKET)]


def rect_area(r):
    return max(0.0, r[2] - r[0]) * max(0.0, r[3] - r[1])


def overlap(a, b):
    return rect_area((max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])))


def to_kicad(x: float, y: float):
    return OX + x, OY - y
