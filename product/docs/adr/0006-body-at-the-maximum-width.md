# ADR 0006: Body at the T1-031 maximum, 62.5 × 95.0 × 25.0 mm

- **Status:** Accepted (2026-10-27). Supersedes [ADR 0003](0003-tentative-body-size.md).
- **Date:** 2026-10-27
- **Basis:** T1-031 (the body may grow to the maximum when needed) and the main board's area result below; T1-040 (no audio part is changed to save area before it is measured); the should features stay on every model.

## Context

ADR 0003 set a tentative body of 59.5 × 94.3 mm, credit-card proportions at the display's width; [board ADR 0016](https://github.com/opendap-project/board/blob/main/docs/adr/0016-front-side-height-under-the-display.md) took it to 25.0 mm thick. With every part of the main board placed on its real footprint ([placement v1](https://github.com/opendap-project/board/blob/main/docs/specs/placement-v1.md)), the board did not fit that body:

- By the floorplan's method (courtyard × 1.7 for placement and routing), the parts needed **111 %** of both sides of the 55.3 × 90.1 mm board. The core band was at 203 % of its area, the power band at 233 %, the audio zone's front at 254 %. The placement left a placement and routing factor of 1.49 against the 1.7 the floorplan assumed (range 1.5–1.9).
- Every way to recover area was quantified, alone and combined, against a target of at most 95 % with routing room. A body of the same size reached it only by removing every should block but the coprocessor (NFC reader and tag, IMU, haptics, TPM, ambient microphone, cover detect, board ID) from the design for every model. A population option (not fitted) frees no area, because the board is sized by the full variant.
- Growth inside T1-031: 62.5 mm of width (+3.0) and 95.0 mm of height (+0.7) give the board 622 mm² more; thinner case walls (1.6 → 1.2 mm, a case value that was an assumption) give 234 mm² more. With these, the speaker on a case shelf, pocket reliefs and every smaller part the area work found (the audio output stage's 0603 parts in 0402 included), the board's own placement tool placed all 1,012 parts at **91.3 %** by the same method, with no feature dropped. Smaller widths (60.5 and 61.5 mm) did not reach the target without dropping a feature.
- T1-032 (ideal footprint, should) and T1-033 (card proportion, should) are product identity: growth must be justified and reversed when it can be.

## Decision

1. **The body is 62.5 × 95.0 × 25.0 mm**: the T1-031 maximum in width and height, thickness unchanged (board ADR 0016's stack).
2. **The body grows evenly about the device centre** (T1-021 origin): +1.5 mm on each side, +0.35 mm at the top and at the bottom. The display, the battery pocket and the thickness stack do not move or change; the extra area is side strips and the two bands.
3. **The measurement gate of ADR 0003 is unchanged**: once the RK3566's draw is measured (a Radxa ZERO 3 or the prototype), T1-037 and T1-039 apply: the measured pessimistic runtime must clear the 6 h red line, and any recovered thickness goes back to the body first (board ADR 0016 item 5).
4. **No should feature is dropped for area.** If the routing stage or the shield-can frames need more area than this body gives, the first reserve is removing the NFC reader, then the TPM (board placement spec); either is a maintainers' decision.

## Consequences

- Proportion 95.0 / 62.5 = **1.52** against the card's 1.59 (T1-033). T1-032's ideal (54 mm wide) is further away; T1-031 is met with no width or height margin left.
- The rebuilt board (2026-10-27) carries the part swaps that pass today; the audio output stage's 0402 swap waits for an audio review and a THD+N measurement, and other swaps wait for DC-bias figures, a land or stock. It needs **98.8 %** by the floorplan's method (was 111 %), with every part placed and a placement and routing factor of 1.68 left (was 1.49). The 95 % target is reached only when the gated swaps pass or the reserve of item 4 is used ([placement v1](https://github.com/opendap-project/board/blob/main/docs/specs/placement-v1.md)).
- With 1.2 mm case walls and the board's 0.5 mm clearance per side, the main board outline is **59.1 × 91.6 mm** (was 55.3 × 90.1). The back bands grow to 17.75 mm (bottom) and 7.75 mm (top) from the inner wall (were 17.0 and 7.0).
- Every faceplate's outline follows the body; the faceplate interface's body row takes these values. The case takes the walls, the speaker shelf and the pocket reliefs as interface constraints ([case and board interface](../specs/case-board-interface.md)).
- Board ADR 0016 is superseded by [board ADR 0025](https://github.com/opendap-project/board/blob/main/docs/adr/0025-height-zones-in-the-wider-body.md), which restates its height zones for this body.
- Revisited when area is freed: a board that routes with room to spare, later part generations, or a thinner stack.
