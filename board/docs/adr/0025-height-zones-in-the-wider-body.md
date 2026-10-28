# ADR 0025: Height zones and board outline in the 62.5 × 95.0 mm body

- **Status:** Accepted (2026-10-27). Supersedes [ADR 0016](0016-front-side-height-under-the-display.md).
- **Date:** 2026-10-27
- **Basis:** [t1 ADR 0006](https://github.com/opendap-project/t1/blob/main/docs/adr/0006-body-at-the-maximum-width.md) (body at the T1-031 maximum); the board-area result below; T1-040 (audio parts change only after measurement); BRD-038 (microSD); T1-016 (speaker at the bottom edge, right).

## Context

ADR 0016 set the front-side height under the display and the four height zones in the 59.5 × 94.3 × 25.0 mm body. Its stack and zone heights still hold; the body around them changes.

Area result (2026-10-27), by the floorplan's method (courtyard × 1.7, 1.2 for jacks and USB-C; [placement v1](../specs/placement-v1.md) §3.1):

- In the 55.3 × 90.1 mm outline the parts needed 111 % of both sides: core band 203 %, power band 233 % (the speaker's 165 mm² shadow included), audio front 254 %; the placement left a placement and routing factor of 1.49.
- Per option alone: the body at 62.5 × 95.0 mm frees 6.5 points; 1.2 mm walls 2.5; the speaker on a case shelf 1.9; the 4.4 mm jack, microSD and side-button reliefs move tall parts out of the band count (bands 138 % → 79 %) and change no board total; the audio output stage's 0603 parts in 0402 free 3.9 points by the factor (2.3 with each pin's routing kept).
- With all of these and every part swap found, the board's own placement tool places all 1,012 parts at 91.3 %; no smaller set without dropping a should feature reaches 95 %.
- No catalog 4.4 mm jack fits PCB-Z-01 (its plug bore alone exceeds 1.5 mm), and the DM3AT microSD socket is 1.68 mm high (0.18 mm over PCB-Z-01).

## Decision

1. **Board outline 59.1 × 91.6 mm**: the body of t1 ADR 0006 less 1.2 mm walls (cavity 60.1 × 92.6 mm) less 0.5 mm per side, centred on the device. The pocket, the display and every part fixed in the device frame keep their positions; mounting holes keep their distance to the edges (PCB-M-08).
2. **Height zones and stack of ADR 0016, unchanged in value:**

   | ID | Zone | Max part height |
   |---|---|---|
   | PCB-Z-01 | Back, under the battery pocket (RK3566, LPDDR4X, eMMC here) | 1.5 mm, can and thermal pad included |
   | PCB-Z-02 | Back, bottom band (17.75 mm from the inner wall) and top band (7.75 mm) | 14.2 mm (25.0 − 12.7 + 1.5 + 0.4) |
   | PCB-Z-03 | Front, under the display | 1.0 mm; display-to-board gap 1.3 mm; no shield cans; a faceplate connection area at the display's bottom edge for the FH35C and its ESD only |
   | PCB-Z-04 | Front, outside the display footprint | 6.8 mm where the faceplate frame leaves room (**UNVERIFIED**) |

   The thickness stack stays: lens and OCA 0.9, display 5.5, gap 1.3, board 1.2, back components 1.5, pocket floor 0.4, battery layer 12.3, back cover 1.5, HAT case features 0.4 = 25.0 mm. The RK3566, LPDDR4X and eMMC stay on the back with their decoupling on the front under the ball field; z recovered later goes back to the body first (a 1.0 mm board returns 0.2 mm, a faceplate on the module's own touch lens up to 0.9 mm).
3. **Speaker on a case shelf (PCB-Z-09).** The speaker (BOM line 33) sits on a case shelf above the bottom band, right of the USB-C, at its floorplan position (x 6.0 to 21.0, y −45.0 to −34.0). It takes no board area; board parts under the shelf are held to 1.5 mm until the case sets the shelf clearance; the spring-contact pads stay on the board.
4. **Pocket reliefs, case interface:** the pocket floor and the pack keep out of the 4.4 mm jack's volume (PCB-Z-06) and the microSD socket's (PCB-Z-07, the DM3AT push-push socket is kept), and a side strip along the pocket's long edges at the side buttons (PCB-Z-08). The volumes are in the PCB design constraints and the t1 case and board interface (CB-06 to CB-08).
5. **Part swaps that pass are applied** ([BOM v1.16](../specs/bom-v1.md#changes-in-v116)): 121 resistors of 0402 in 0201 of the same series outside the audio chain and the VBUS paths, five 100 nF signal capacitors in 0201.
6. **The audio output stage's 0603 parts stay 0603** until an audio review and a THD+N measurement at full output show no difference with the same values in 0402 of the same series (t1 verification row V2-A08; T1-040).
7. **Reserve, not applied:** if the routing stage or the shield-can frames need more area, the next lever is removing the NFC reader (BRD-057), then the TPM (BRD-059), from the design for every model; either is a maintainers' decision.

## Consequences

- The rebuilt board ([placement v1](../specs/placement-v1.md) §3): all 1,012 parts placed, 846 front and 166 back; the floorplan's method gives **98.8 %** of both sides (was 111 %), the placed courtyards cover 59.4 % (was 67.3 %), a placement and routing factor of 1.68 is left (was 1.49). Bands by the method: core 124 % (was 203 %), power 223 % (233 %), audio 99 % (123 %); audio front 216 % (254 %). The 95 % target waits for the gated swaps (item 6 and BOM v1.16's open lines) or the reserve (item 7).
- With the wider body the side buttons and the VSYS_LV converter's 0805 leave the zones they exceeded: the buttons' courtyards end 0.05 mm outside the pocket footprint (the strip of item 4 carries the case tolerance), and the 0805 finds back room, so PCB-Z-04 carries no part.
- The case receives the walls, the shelf, the reliefs and the bosses as interface constraints; the case repository's own design is not changed by this ADR.
- PCB-M-01, M-02, M-08 and PCB-Z-02, Z-06 to Z-09 of the PCB design constraints take these values.
