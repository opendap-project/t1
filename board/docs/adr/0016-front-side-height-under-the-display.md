# ADR 0016: Front-side height under the display

- **Status:** Superseded by [ADR 0025](0025-height-zones-in-the-wider-body.md) (2026-10-27; the body grows to 62.5 × 95.0 × 25.0 mm, t1 ADR 0006; the zone heights and the stack are restated unchanged). Previously: Accepted.
- **Date:** 2026-10-24

## Context

The T1 thickness stack, which sets the 59.5 × 94.3 × 24 mm body of [t1 ADR 0003](../../../product/docs/adr/0003-tentative-body-size.md) and the 10.9 × 50.5 × 63.8 mm pocket the [ADR 0014](0014-two-cell-battery.md) pack fills, leaves 0.3 mm between the display module and the board. The faceplate connector FH35C-51S is 0.9 mm high, and BRD-054 allows both sides populated ([PCB design constraints](../specs/pcb-design-constraints.md) PCB-Z-03, §9 item 1).

A front-side height budget (courtyard area from BOM v1.7, placement factor from the Radxa ZERO 3W) found:

- BOM v1.7 needs about 4,810 mm² of courtyard, about 7,800 mm² of board (7,000–8,600) with a placement and routing factor of 1.7 (1.5–1.9) derived from the Radxa ZERO 3W. The board offers about 4,880 mm² per side, and the display covers 91 % of the front.
- A board with nothing under the display (option b), a recess for the FH35C only (c) or the faceplate flex folded to the back (d) all leave about 5,350 mm² usable: short by 1,650–3,250 mm². About 2,100–3,700 mm² of parts must sit under the display, and all of them can be parts of 1.0 mm or less.
- Each millimetre taken from the battery layer costs about 8.3 % of pack energy. The pessimistic core session is already about 5.7–6.0 h (est.), below the 6 h red line of T1-039.

## Decision

1. **Front zone under the display (PCB-Z-03): 1.0 mm maximum part height**, the FH35C (0.9 ± 0.1 mm) included. **Display-to-board gap: 1.3 mm** (1.0 mm plus 0.3 mm for insulation, tolerance and module deflection under touch). No shield cans in this zone. A faceplate connection area of about 10 × 54 mm at the display's bottom edge carries only the FH35C and its ESD parts (size to be confirmed with the faceplate flex).
2. **The extra 1.0 mm comes from body thickness, not from the battery.** The tentative body becomes **59.5 × 94.3 × 25.0 mm** (T1-031 maximum). The battery layer (12.3 mm), the 10.9 × 50.5 × 63.8 mm pocket and the ADR 0014 pack criteria do not change.
3. **The RK3566, LPDDR4X and eMMC go on the back**, under the battery pocket (PCB-Z-01, 1.5 mm with can and thermal pad). Their 0201 decoupling goes on the front under the ball field. The pocket floor is to be a metal plate thermally tied to the frame (input to the case).
4. **Resulting height zones:**

   | ID | Zone | Max part height |
   |---|---|---|
   | PCB-Z-01 | Back, under the battery pocket | 1.5 mm (unchanged) |
   | PCB-Z-02 | Back, bottom and top bands | Battery layer + 1.9 mm = 14.2 mm at 25.0 mm (arithmetic: 25.0 − 12.7 + 1.5 + 0.4; value unchanged) |
   | PCB-Z-03 | Front, under the display | 1.0 mm; gap 1.3 mm; no shield cans; faceplate connection area for the FH35C and its ESD only |
   | PCB-Z-04 | Front, outside the display footprint | Gap + module = 6.8 mm where the faceplate frame leaves room (**UNVERIFIED** until the faceplate mechanics) |

5. **z recovered later goes back to the body first:** a 1.0 mm board (8-layer HDI, PCB-S-01) returns 0.2 mm, and a faceplate that uses the module's own touch lens returns up to 0.9 mm. After that, battery or body follows the measurement gate of t1 ADR 0003.

## Consequences

- The thickness stack (front to back) is: lens and OCA 0.9, display 5.5, gap 1.3, board 1.2, back components 1.5, pocket floor 0.4, battery layer 12.3, back cover 1.5, HAT case features 0.4 = 25.0 mm. t1 ADR 0003 gets a dated note pointing here.
- No z margin is left within T1-031. Any later z need, such as the 1.1 mm IP65 lens (+0.4 mm), comes from the battery unless a recovery of item 5 exists first.
- Battery autonomy is unchanged: typical core session about 12.8–13.4 h, pessimistic about 5.7–6.0 h (est.). The measurement gate of t1 ADR 0003 still decides the pessimistic case.
- Thermal: the SoC's heat goes to the planes and the pocket floor, not into the LCD (rated to +70 °C). Sustained high loads warm the pack. The pack temperature limits charge and load in hardware (BQ25798 TS window, gauge; BRD-049), and Blackbird OS reduces SoC load before that as a documented, visible limit (T1-045).
- Assembly: the front (light parts only) is reflowed first; the BGA side second. Flat test pads go on the front, outside the faceplate connection area, for a single-sided fixture.
- Placement items found by the study, not decided here: the back bands are at 104–123 % of their area with today's tall parts (4020 inductors, LRA, microSD), and the microSD socket (15.95 mm deep, 1.68 mm high) fits neither the 7 mm top band nor PCB-Z-01.
- **UNVERIFIED** inputs to close: RK3566, LPDDR4X and eMMC package heights (Rockchip guide, Samsung data); the 0.3 mm clearance (display sample); the faceplate connection area (faceplate flex, case); the routing factor (first placement).
- PCB-Z-01 to PCB-Z-04 of the PCB design constraints take these values, closing its §9 item 1.
