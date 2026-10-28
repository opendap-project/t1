"""Placement plan of the T1 main board: zones per block, fixed parts, targets and the placement
decisions taken at this stage (pure Python data).

Sources: floorplan v1 (docs/specs/floorplan-v1.md) for the zones, the fixed parts and the
corridors; ADR 0016 for the sides and heights; ADR 0018 for the antenna feeds; ADR 0020 for the
battery contacts; the BGA escape study for the SoC's position and its decoupling under the ball
field. Every change against floorplan v1 is a row of DELTAS with its reason; docs/specs/placement-v1.md
records them as decisions.
"""

from __future__ import annotations

import geometry as g

# ---- block -> zone (floorplan v1 §2). Sub-sheets follow their parent block.
ZONE_OF_BLOCK = {}
for _b in ("soc", "soc-ddr", "soc-pmuio", "soc-ground", "soc-phy", "soc-power", "soc-vccio-a", "soc-vccio-b",
           "lpddr4x", "emmc", "microsd", "pmic", "vdd-cpu", "pwr-3v3-sys", "rp2354", "rp2354-core",
           "rp2354-power", "tpm", "gpio-expander", "board-id", "imu", "haptics", "nfc-tag",
           "status-led", "maskrom", "buttons", "debug"):
    ZONE_OF_BLOCK["blk." + _b] = "CORE"
for _b in ("audio", "audio-supply", "mclk", "dac-l", "dac-r", "hpa-se", "hpa-bal", "hpa-bal-l", "hpa-bal-r",
           "hpa-rails", "hpa-rails-ldo", "jack-se", "jack-bal", "mic-ambient"):
    ZONE_OF_BLOCK["blk." + _b] = "AUDIO"
for _b in ("charger", "charger-input", "charger-core", "charger-battery", "gauge", "pwr-vsys-lv", "pwr-5v1",
           "hat-5v", "usb-vbus-out", "current-monitors", "hpa-rails-pre", "speaker", "fp-backlight",
           "cover-detect"):
    ZONE_OF_BLOCK["blk." + _b] = "POWER"
for _b in ("usb-c", "hat-signals", "fp-connector", "fp-display", "fp-controls", "mic-main"):
    ZONE_OF_BLOCK["blk." + _b] = "IO"
for _b in ("radio", "radio-module", "radio-power", "antennas"):
    ZONE_OF_BLOCK["blk." + _b] = "RADIO"

# The faceplate connection area carries the FH35C and its ESD only (ADR 0016 item 1, floorplan v1 §2)
FACEPLATE_REFS = {"J5301", "U5301", "U5302", "U5303", "U5304", "U5305", "U5306"}

# ---- fixed parts: ref -> (x, y, rotation, side, reason). "edge:bottom"/"edge:top" as y puts the
# courtyard against that edge with the mouth outward (rotation chosen by build.py as in the floorplan
# study); x then is the courtyard centre.
SOC = (0.0, 10.0)
FIXED = {
    "U1301": (SOC[0], SOC[1], 0, "B", "RK3566 on the back at the floorplan's and escape study's position (ADR 0016 item 3)"),
    "U2101": (16.9, 11.0, 0, "B", "LPDDR4X right of the SoC (its DDR balls face right after the flip); 2.05 mm courtyard gap to the SoC (PCB-D-01)"),
    "U3801": (-17.75, 12.0, 0, "B", "eMMC left of the SoC (eMMC balls face left after the flip); floorplan v1"),
    "U1101": (-4.8, 25.0, 0, "B", "RK809-5 above the SoC on the back, next to the vdd_cpu buck, with room for its five 1.2 mm inductors (back only); 2 mm from the SoC and eMMC courtyards (PCB-D-01). Floorplan v1 had it below the SoC, where the grown audio and power zones leave 10 x 8 mm. Placement v1.3: 1.1 mm lower and 1.2 mm right (was -6.0, 25.7), at the SoC's and eMMC's 2 mm, so its top row of pins stands 1.3 mm from the radio zone and all 27 of its capacitors find room within their bound (capacitor proximity). Placement v1.6: 0.4 mm higher (was -4.8, 24.6), clear of the SoC shield frame's land and keep-out (decision 15)"),
    "U3501": (-16.0, 24.5, 0, "F", "RP2354A on the front (floorplan v1), above the eMMC: its exposed pad's thermal vias must not land under the eMMC's balls, and the audio zone grew up to y 6"),
    "U2501": (-20.0, -18.0, 0, "B", "CS43198 left channel on the back under the pocket (floorplan v1)"),
    "U2601": (-11.5, -18.0, 0, "B", "CS43198 right channel, mirror of the left about x = -15.75 (CRAFT-34)"),
    "Y2401": (-17.3, -11.0, 0, "B", "NZ2520 45.1584 MHz (floorplan v1), mirrored with Y2402 about the DACs' axis x = -15.75"),
    "Y2402": (-14.2, -11.0, 0, "B", "NZ2520 49.152 MHz (floorplan v1 had -13.0), mirrored with Y2401 about x = -15.75"),
    "J3401": (-22.3, "edge:bottom", None, "B", "3.5 mm jack, bottom edge, left (PCB-M-05)"),
    "J4001": (-11.55, "edge:bottom", None, "B", "4.4 mm jack, bottom edge (PCB-M-05)"),
    "J4601": (0.0, "edge:bottom", None, "B", "USB-C centred on the bottom edge (PCB-M-05)"),
    "J6201": (13.5, "edge:top", None, "B", "microSD at the top edge, right (floorplan v1), 0.5 mm right of the study so the core top band holds the two band inductors"),
    "J5201": (-14.0, 41.5, 0, "B", "U.FL ANT0 in the top band near the top wall (ADR 0018 item 4, PCB-R-02)"),
    "J5202": (-8.3, 41.5, 0, "B", "U.FL ANT1 in the top band near the top wall (ADR 0018 item 4, PCB-R-02)"),
    "J5301": (2.5, -32.9, 0, "F", "FH35C in the faceplate connection area, clear of the USB-C and jack through-holes (floorplan v1 §5)"),
    "J4701": (13.1, -31.0, 0, "B", "DF40C-50DS in the bottom band beside the USB-C, length along the edge (floorplan v1 §5)"),
    "U5001": (-17.0, 32.5, 0, "B", "Murata Type 2EL under the pocket, above the SDIO side (floorplan v1)"),
}
# Parts taller than 1.5 mm stand only in the bands (PCB-Z-02); the bands are small, so each band part
# has its place here, next to the converter or contact it serves:
# - power band above the USB-C (y -36 to -28.55): the battery fuse under the P+ contacts (the 5.1 V
#   converter's 1210 output capacitor stood here until placement v1.3: two 0805 replace it, BOM v1.18);
# - power band at the right edge (x 21 to 27.3, under the bottom-right hole): the VSYS_LV and pre-rail
#   inductors (XGL4020, 2.1 mm).
# The vdd_cpu, vcc3v3_sys, radio AVDD18, charger and 5.1 V inductors are 1.2-1.5 mm since the compaction
# study (placement v1 decision 12) and are placed by the search. In the wider body (ADR 0025) the
# VSYS_LV converter's 0805 C904 finds back room too, so no part uses PCB-Z-04 (placement v1 decision 4).
FIXED.update({
    "F701": (-2.4, -30.45, 0, "B", "battery fuse (NANO2, 2.69 mm) in the band under the P+ contacts (PCB-P-01)"),
    "L901": (24.2, -42.4, 0, "B", "VSYS_LV inductor (XAL4020, 2.1 mm) in the right band"),
    "L2802": (24.2, -37.7, 0, "B", "pre-rail inductor (XAL4020, 2.1 mm) in the right band"),
})

# Battery-contact ESD (PCB-L-08, ADR 0020 item 6): one TPD1E10B06 per signal contact, within 3 mm of
# it, just past the contact pads' top end (inside BATTERY_CONNECTOR, which allows battery nets and GND)
FIXED.update({
    "D702": (g.contact_x(3), g.CONTACT_Y + g.CONTACT_PAD[1] / 2 + 1.2, 0, "B", "mid-cell tap ESD at its contact (PCB-L-08)"),
    "D703": (g.contact_x(4), g.CONTACT_Y + g.CONTACT_PAD[1] / 2 + 1.2, 0, "B", "NTC ESD at its contact (PCB-L-08)"),
})

# Speaker contact pads under the speaker body (BOM v1 line 33: spring contacts on gold pads); pad
# spacing UNVERIFIED until the speaker's contact drawing
FIXED.update({
    "TP5503": (10.5, -39.5, 0, "B", "speaker contact pad (+) under the speaker body"),
    "TP5504": (16.5, -39.5, 0, "B", "speaker contact pad (-) under the speaker body"),
})

# Side buttons at the edges (controls spec §1.4: Action, Vol+, Vol- on the left edge from the top;
# Main on the right). Long side along the edge, courtyard against the edge, above the eMMC's rework
# clearance. Positions UNVERIFIED (case); their 1.9-2.5 mm bodies stand 2 mm into PCB-Z-01 (open item).
FIXED.update({
    "SW6904": (-g.HX + 1.9, 35.0, 90, "B", "Action, left edge, top"),
    "SW6902": (-g.HX + 1.9, 29.5, 90, "B", "Vol+, left edge below Action"),
    "SW6903": (-g.HX + 1.9, 24.0, 90, "B", "Vol-, left edge below Vol+, 2 mm above the eMMC (PCB-D-01)"),
    "SW6901": (g.HX - 1.9, 29.5, 90, "B", "Main (power), right edge"),
})
# Pocket reliefs (case interface, ADR 0025; PCB-Z-06 to Z-08): parts that stand over PCB-Z-01's 1.5 mm
# where the pocket floor and the pack keep out of their volume. build.py reports each relief's
# courtyard and height (placement-result.json "pocket_reliefs") instead of a PCB-Z-01 finding.
POCKET_RELIEFS = {
    "J4001": "PCB-Z-06", "J6201": "PCB-Z-07",
    "SW6901": "PCB-Z-08", "SW6902": "PCB-Z-08", "SW6903": "PCB-Z-08", "SW6904": "PCB-Z-08",
}
# Battery contacts (ADR 0020 item 2, PCB-L-04): P+, P+, empty, mid-cell tap, NTC, P-, P-
CONTACT_ORDER = {"BAT_P": [0, 1], "BAT_MID": [3], "BAT_NTC": [4], "BAT_N": [5, 6]}

# ---- placement deltas against floorplan v1 (each recorded in docs/specs/placement-v1.md)
# (zone, rect, layers, reason): area added to a zone on those copper layers (floorplan v1's layer
# sets: None every layer, "front" F.Cu and In1.Cu, "back" B.Cu); the same rect leaves every other
# zone on those layers.
ZONE_DELTAS = [
    ("AUDIO", (-g.HX, g.Y_SPLIT, g.X_AUDIO, 2.4), None,
     "The audio zone grows from y -8 to y 2.4 (x < -6.2) on every layer, up to the eMMC's rework clearance: its "
     "parts need 1,596 mm2 of courtyard against 1,557 mm2 of floorplan zone on both sides; the core has room"),
    ("AUDIO", (-g.HX, 2.4, g.X_AUDIO, 14.0), "front",
     "On the front (L1, L2) the audio zone reaches y 14, over the eMMC, which keeps the back and inner layers there "
     "(an area may cover only some layers where two zones share a spot on opposite sides, floorplan v1 §2)"),
    ("POWER", (g.X_POWER, g.Y_SPLIT, g.HX, 0.0), None,
     "The power zone grows from y -8 to y 0 (x > 6.2): the charger's twelve 0805 capacitors (1.25 mm, back only) "
     "find no back area outside the battery-contact window otherwise"),
    ("CORE", (-5.5, g.POCKET[3], g.X_RADIO, g.HY), None,
     "Top band x -5.5 to 3 moves from the radio zone to the core: the vdd_cpu and vcc3v3_sys inductors (2.1 and "
     "2.0 mm) fit no core band otherwise"),
    ("POWER", (4.0, g.CW[1], g.X_POWER, 0.0), None,
     "The power zone's left edge moves from x 6.2 to x 4.0 between the battery-contact window and y 0: the "
     "charger, gauge and VSYS_LV converter passives need it, and the I/O zone keeps x -6.2 to 4.0 (34 % used)"),
    ("POWER", (g.FP[2], g.HAT_STRIP[1], g.HAT_STRIP[2], g.HAT_STRIP[3]), "front",
     "The front of the HAT strip right of the faceplate area moves from the I/O zone to the power zone: the "
     "DF40C-50DS sits on the back, its front is free"),
    ("POWER", (-2.0, g.CW[3], 4.0, g.Y_SPLIT), "back",
     "The back layer of the I/O column's right part above the battery-contact window (x -2 to 4, y -18.8 to -8) "
     "moves to the power zone: the charger's twelve 0805 capacitors (1.25 mm) and the VSYS_LV input capacitor "
     "are back-only and the power zone's back is full of parts over 1.0 mm; the I/O pairs pass there on L4 and L1"),
    ("POWER", (g.X_AUDIO, -36.0, g.X_POWER, g.POCKET[1]), "back",
     "Bottom band above the USB-C (x -6.2 to 6.2, y -36.0 to -28.55) moves from the I/O zone's back layer to the "
     "power zone: the fuse, the 5.1 V converter's 1210 and the band inductors exceed the power zone's band"),
]

# Corridors moved with the zone boundaries (floorplan v1 §4 item 3: a corridor straddles the boundary it serves)
CORRIDOR_DELTAS = {
    "core-audio": ((-11.0, -1.0, -5.0, 5.0), "straddles the audio zone's new top edge on the back and inner layers (y 2.4), next to the SoC's I2S side"),
    "core-power": ((8.0, -3.0, 14.0, 3.0), "straddles the power zone's new top edge (y 0)"),
}

# ---- blocks moved off their floorplan zone, block -> (zone, reason)
BLOCK_ZONE = {
    "blk.audio-supply": ("POWER", "its TPS62840 buck has a switch node, and switch nodes stay in the power zone "
                         "(floorplan v1 §4 item 6, PCB-A-06)"),
    "blk.mic-ambient": ("CORE", "placement v1.6: the ambient microphone is not on the playback path, and the audio "
                        "zone's back gives its room to the audio shield frame (decision 15)"),
}
FLOORPLAN_ZONE_OF_BLOCK = dict(ZONE_OF_BLOCK)
ZONE_OF_BLOCK.update({b: z for b, (z, _) in BLOCK_ZONE.items()})

# ---- parts moved off their block's zone, ref -> (zone, reason)
PART_ZONE = {}

# ---- block targets: where a block's first unplaced part goes (device frame); its other parts follow
# the pads they connect to.
TARGET = {
    "blk.soc-pmuio": (-5.0, 14.0), "blk.soc-vccio-a": (-4.0, 6.0), "blk.soc-vccio-b": (-8.0, -2.0),
    "blk.soc-power": SOC, "blk.soc-ddr": SOC, "blk.soc-phy": SOC,
    "blk.lpddr4x": (16.9, 11.0), "blk.emmc": (-17.75, 12.0), "blk.microsd": (13.5, 36.0),
    "blk.pmic": (-6.0, 25.7), "blk.vdd-cpu": (6.0, 22.5), "blk.pwr-3v3-sys": (1.5, 40.5),
    "blk.rp2354-core": (-16.0, 0.0), "blk.rp2354-power": (-20.0, -3.0), "blk.tpm": (20.0, -3.0),
    "blk.gpio-expander": (10.0, -2.0), "blk.board-id": (6.0, 26.0), "blk.imu": (0.0, 26.0),
    "blk.haptics": (-8.0, 26.0), "blk.nfc-tag": (13.0, 28.0),
    "blk.status-led": (2.0, -5.0), "blk.maskrom": (8.0, 2.0), "blk.buttons": (-26.0, 20.0),
    "blk.debug": (0.0, -4.0),
    "blk.audio-supply": (-9.0, -12.0), "blk.mclk": (-15.75, -11.0), "blk.dac-l": (-20.0, -18.0),
    "blk.dac-r": (-11.5, -18.0), "blk.hpa-se": (-22.0, -25.0), "blk.hpa-bal": (-12.0, -25.0),
    "blk.hpa-bal-l": (-14.0, -24.0), "blk.hpa-bal-r": (-10.0, -24.0), "blk.hpa-rails-ldo": (-8.5, -15.0),
    "blk.jack-se": (-22.3, -37.0), "blk.jack-bal": (-11.55, -34.0), "blk.mic-ambient": (-25.0, -10.0),
    "blk.charger-input": (12.0, -12.0), "blk.charger-core": (12.0, -22.0), "blk.charger-battery": (2.0, -30.0),
    "blk.gauge": (8.0, -18.0), "blk.pwr-vsys-lv": (22.0, -14.0), "blk.pwr-5v1": (20.0, -22.0),
    "blk.hat-5v": (20.0, -30.0), "blk.usb-vbus-out": (16.0, -26.0), "blk.current-monitors": (18.0, -10.0),
    "blk.hpa-rails-pre": (8.0, -14.0), "blk.speaker": (13.5, -39.5), "blk.fp-backlight": (12.0, -36.0),
    "blk.cover-detect": (26.5, -16.0),
    "blk.usb-c": (0.0, -30.0), "blk.hat-signals": (13.1, -31.0), "blk.fp-connector": (0.0, -26.0),
    "blk.fp-display": (-3.0, -24.0), "blk.fp-controls": (3.0, -24.0), "blk.mic-main": (-4.0, -20.0),
    "blk.radio-module": (-17.0, 32.5), "blk.radio-power": (-22.0, 26.0), "blk.antennas": (-12.0, 38.0),
}

# Parts placed at their own target (contact pads for parts mounted in the case, edge pads)
PART_TARGET = {
    "TP5801": ((g.HX - 1.25, -14.0), "B", "cover-detect pad at the board edge (ADR 0020 item 7, PCB-L-10)"),
    "TP5802": ((g.HX - 1.25, -17.5), "B", "cover-detect ground pad at the board edge (ADR 0020 item 7)"),
    # placement v1.6: the audio parts taller than the audio shield lid allows (1.45 mm SOT-23-5, 1.3 mm
    # inside) take their room first, outside the frame next to their DACs and clocks (decision 15)
    "U2502": ((-26.65, -20.8), "B", "DAC L supply regulator, 1.45 mm, left of the audio shield frame"),
    "U2602": ((-26.65, -16.6), "B", "DAC R supply regulator, 1.45 mm, left of the audio shield frame"),
    "U2402": ((-18.8, -24.75), "B", "master-clock oscillator, 1.45 mm, below the audio shield frame"),
    "U2403": ((-18.8, -28.25), "B", "master-clock oscillator, 1.45 mm, below the audio shield frame"),
    "U2902": ((-20.35, -4.45), "F", "amplifier-rail LDO at its v1.5 position, over its output capacitors on the back (placement v1.6)"),
    # placement v1.6: the six OPA1622 of the headphone stage take their room before the passives, at
    # their v1.5 positions; the two on the back that crossed the audio frame move inside it
    "U3001": ((-14.6, 0.4), "B", "OPA1622, SE stage, v1.5 position, above the audio shield frame"),
    "U3002": ((-15.55, -3.1), "F", "OPA1622, SE stage, v1.5 position"),
    "U3201": ((-9.7, -5.6), "B", "OPA1622, balanced L, inside the audio shield frame (was -8.2, -4.6)"),
    "U3202": ((-13.7, -5.6), "B", "OPA1622, balanced L, inside the audio shield frame (was -12.2, -4.75)"),
    "U3301": ((-10.6, -8.1), "F", "OPA1622, balanced R, v1.5 position"),
    "U3302": ((-10.75, -11.4), "B", "OPA1622, balanced R, v1.5 position, inside the audio shield frame"),
    "TP6803": ((-20.0, 22.0), "B", "LRA contact (actuator in the case, feature block 44)"),
    "TP6804": ((-17.5, 22.0), "B", "LRA contact (actuator in the case, feature block 44)"),
    "TP6403": ((2.0, 23.5), "B", "NFC tag loop antenna contact (BOM line 126)"),
    "TP6404": ((4.5, 23.5), "B", "NFC tag loop antenna contact (BOM line 126)"),
    # the two LT3094 first, so their back-only 0805 output capacitors (BOM v1.18 items 3 and 5) find
    # room within their bound (capacitor proximity, placement v1.3)
    "U2903": ((-22.4, 0.35), "B", "LT3094 A with its capacitors (PCB-P-10, placement v1.3)"),
    "U2904": ((-26.5, -6.6), "B", "LT3094 B with its capacitors (PCB-P-10, placement v1.3)"),
    # the RK809's vdd_gpu output capacitor by L1102's output pad, before the RP2354's parts fill the
    # front there (capacitor proximity, placement v1.3)
    "C1104": ((-13.15, 27.55), "F", "vdd_gpu output capacitor over L1102's output pad (PCB-P-07, placement v1.3)"),
    "C904": ((27.6, -42.55), "B", "VSYS_LV output capacitor by L901's output pad in the right band (PCB-P-07, placement v1.3)"),
    "C2819": ((27.75, -38.45), "B", "pre-rail output 1206 by L2802's output pad in the right band (PCB-P-07, placement v1.3)"),
    "C2818": ((27.95, -33.6), "B", "pre-rail output 1206 by L2802's output pad in the right band (PCB-P-07, placement v1.3)"),
    "C2817": ((24.3, -34.15), "B", "pre-rail output 1206 by L2802's output pad in the right band (PCB-P-07, placement v1.3)"),
}
# Edge parts exempt from PCB-B-01 (J*, SW*) that may reach the edge
EDGE_OK = ("J", "SW")

# Decoupling under a BGA, on the front under its ball field (ADR 0016 item 3, PCB-P-10):
# capacitors of these blocks whose nets are only a rail and GND
UNDER_BGA = {"blk.soc-power": "U1301", "blk.lpddr4x": "U2101", "blk.emmc": "U3801"}

# Footprint fields the product rules read (hardware/rules/README.md, conventions); set here until
# the symbols carry them
THERMAL_HOT = {"U1301", "U1101", "U1201", "U1001", "U601", "U901", "U4401", "U2801", "U2802", "U4501", "U4502",
               "U4801", "U501", "U5103", "U2303", "U5401"}
REWORK_BGA = {"U1301", "U2101", "U3801"}

# Board-only parts (not in the schematic): fiducials (PCB-M-09: three global per populated side, not
# symmetric, and two local at the RK3566; PCB-D-02 to D-04: 1 mm dot, 1 mm clear area). Each keeps
# a 3.2 mm square free of other parts (dot, clear area, 0.1 mm).
FIDUCIAL_FP = "Fiducial:Fiducial_1mm_Mask2mm"
FIDUCIALS = [
    ("FID1", -23.0, 36.0, "F", "global"), ("FID2", 23.0, 35.0, "F", "global"), ("FID3", -23.0, -22.0, "F", "global"),
    ("FID4", -7.8, 31.4, "B", "global"), ("FID5", 23.0, -1.5, "B", "global"), ("FID6", 22.5, 24.0, "B", "global"),
    ("FID7", -13.0, 0.8, "B", "local"), ("FID8", 8.0, 22.8, "B", "local"),
]
# Placement v1.6: FID4, FID7 and FID8 moved clear of the shield frames' lands and keep-outs
# (decision 15); the two local fiducials stay at opposite corners of the RK3566, outside its frame.
FIDUCIAL_KEEP = 3.2

# Board identity (CRAFT-20, Q1): title and revision on the back silk, in an area kept free of parts
IDENTITY = {"rect": (-9.0, 33.5, 5.0, 37.3),   # v1.6: right of the radio frame (was x -11.5)
            "side": "B", "size": 0.8,
            "lines": ["${TITLE}", "rev ${REVISION} ${ISSUE_DATE}"]}

# Nets that do not pull a part towards them (ground and wide rails reach every part through planes)
WEAK_NETS = {"GND", "VSYS", "VSYS_LV", "vcc3v3_sys", "vcc_1v8", "vcca1v8_pmu", "vcc3v3_pmu", "VBAT"}

# Footprints with no land in the libraries yet: placed as courtyard-only placeholders (no pads), with
# the body named by the part (UNVERIFIED) and the field Placeholder.
PLACEHOLDER = {
    "T1_Main_Board:L_Wuerth_WE-LHMI_4020": ((-2.3, -2.3, 2.3, 2.3), "Wuerth 744373240047, 4020 size code: 4.0 x 4.0 mm body + 0.3 mm; land not drawn"),
    "T1_Main_Board:L_Murata_LQH3NP_3x3mm": ((-1.8, -1.8, 1.8, 1.8), "Murata LQH3NPN220MMEL 3.0 x 3.0 mm body + 0.3 mm; land not drawn"),
    "T1_Main_Board:SW_CK_PTS815": ((-2.4, -1.9, 2.4, 1.9), "C&K PTS815 body UNVERIFIED (drawing not retrieved); courtyard estimated as the KMR2 class"),
}
