# Case and main board interface

- **Status:** Draft v0.1 (2026-10-27). What the case must provide for the main board in the body of [ADR 0006](../adr/0006-body-at-the-maximum-width.md). The values come from the board's placement ([board placement v1](https://github.com/opendap-project/board/blob/main/docs/specs/placement-v1.md), its tool's report `pcb/placement-result.json`) and the [PCB design constraints](https://github.com/opendap-project/board/blob/main/docs/specs/pcb-design-constraints.md) (rows PCB-M and PCB-Z); the board side is mirrored there. Nothing here is built or measured yet.
- **Requirements:** T1-014 to T1-016, T1-021, T1-031, T1-040; BRD-038, BRD-049.
- **Decisions:** [ADR 0006](../adr/0006-body-at-the-maximum-width.md) (body), [board ADR 0025](https://github.com/opendap-project/board/blob/main/docs/adr/0025-height-zones-in-the-wider-body.md) (height zones, walls, speaker shelf, reliefs), [board ADR 0016](https://github.com/opendap-project/board/blob/main/docs/adr/0016-front-side-height-under-the-display.md) (thickness stack, superseded by 0025 for the outline only), [board ADR 0020](https://github.com/opendap-project/board/blob/main/docs/adr/0020-battery-connected-through-contacts.md) (battery contacts).

Coordinates are in the T1 system (T1-021: origin at the device centre, x across the width, y along the length towards the top wall, +z towards the faceplate), in millimetres; general tolerances ISO 2768-m. The case's own design (shapes, materials, fixing) is case scope; this spec lists only what the board needs from it.

## 1. What the case must do

| ID | The case must | Value | Status | Board row |
|---|---|---|---|---|
| CB-01 | Enclose the body at the T1-031 maximum | 62.5 × 95.0 × 25.0 mm | Defined | PCB-M-01 |
| CB-02 | Keep its walls at 1.2 mm on all four sides | Cavity 60.1 × 92.6 mm | Defined (stiffness, drop and the antenna windows of board ADR 0018 are checked on the case) | PCB-M-02 |
| CB-03 | Hold the board with 0.5 mm clearance per side | Board outline 59.1 × 91.6 mm, centred; ISO 2768-m ±0.3 mm on the case plus ±0.1 mm on the outline | Clearance **UNVERIFIED** | PCB-M-02, M-03 |
| CB-04 | Keep the battery pocket where it is | Pocket footprint on the board x −25.65 to 25.65, y −28.55 to 38.55; back bands 17.75 mm (bottom) and 7.75 mm (top) from the inner wall | Defined | PCB-Z-01, Z-02 |
| CB-05 | Carry the speaker on a shelf above the board's bottom band, right of the USB-C | Shelf footprint x 6.0 to 21.0, y −45.0 to −34.0 (the speaker's 15 × 11 mm outline, BOM v1 line 33); board parts under it up to 1.5 mm until the case sets the shelf clearance; the speaker keeps its acoustic volume and reaches the board's spring-contact pads TP5503 (10.5, −39.5) and TP5504 (16.5, −39.5), or a flex the case routes | Clearance, pad spacing and the contact path **UNVERIFIED** | PCB-Z-09, PCB-M-05 |
| CB-06 | Relieve the pocket floor and the pack at the 4.4 mm jack J4001 | Volume x −16.64 to −6.45, y −28.55 to −23.75 (4.79 mm into the pocket footprint), 6.5 mm above the board's back; the jack's mouth at the bottom wall | Defined (no catalog 4.4 mm jack fits 1.5 mm) | PCB-Z-06 |
| CB-07 | Relieve the pocket floor at the microSD socket J6201 (DM3AT push-push) | Volume x 5.62 to 21.38, y 27.53 to 38.55 (11.02 mm into the pocket footprint), 1.68 mm above the board's back (0.18 mm over PCB-Z-01); the card enters along +y through the top wall and travels with the push-push mechanism | Defined | PCB-Z-07 |
| CB-08 | Keep a side strip along the pocket's long edges at the side buttons | Left x −29.59 to −25.70 over y 21.60 to 39.44 (Action, Vol+, Vol−; board placement v1.6, the PTS815 land drawn), right x 25.70 to 29.59 over y 26.50 to 32.50 (Main); 1.9 mm (KMR2) and 2.7 mm (PTS815, 2.5 ± 0.2 mm) high; the courtyards end 0.05 mm (KMR2) and 0.15 mm (PTS815) outside the pocket footprint, so the strip carries the case tolerance; actuators face the side walls | Positions **UNVERIFIED** (controls spec §1.4) | PCB-Z-08 |
| CB-09 | Provide four mounting bosses at the board's holes | 2.2 mm holes at (±26.05, 42.3) and (±26.8, −27.0); screw M2 or M1.6 class not chosen | **UNVERIFIED** until the case | PCB-M-08, PCB-H |
| CB-10 | Respect the board's height zones | Back under the pocket 1.5 mm (PCB-Z-01); back bands 14.2 mm (Z-02); front under the display 1.0 mm with a 1.3 mm gap (Z-03); front outside the display 6.8 mm where the faceplate frame leaves room (Z-04, **UNVERIFIED**) | Defined (Z-04 open) | PCB-Z-01 to Z-04 |

## 2. Checks

- **CHK (3D):** the case STEP against the board's STEP export: every board part inside its height zone or inside a relief of §1. The case publishes no export yet (`case/export/` is empty).
- **REV:** shelf clearance and speaker contacts (CB-05), the side strips' tolerance (CB-08), the boss positions (CB-09).

## 3. Open items

1. Shelf clearance, speaker contact path and the speaker's acoustic volume (CB-05).
2. Corner radii of the board outline (CRAFT-35) and the boss positions (CB-09).
3. The antenna windows on a 1.2 mm wall (board ADR 0018, PCB-R-07).
