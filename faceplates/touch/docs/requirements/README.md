# Touch faceplate requirements

Requirements for the touch faceplate, the default faceplate of the OpenDAP T1.

| ID | Requirement | Priority | Status |
|---|---|---|---|
| FPT-001 | The touch faceplate shall be the default faceplate. | must | Confirmed |
| FPT-002 | The touch faceplate shall have a touch display. | must | Confirmed |
| FPT-003 | The touch faceplate shall include a status LED. | must | Confirmed |
| FPT-004 | The touch faceplate shall include a microphone. | must | Confirmed |
| FPT-005 | The touch faceplate shall meet the [faceplate interface](../../../../product/docs/specs/faceplate-interface.md) defined in the t1 repository. | must | Confirmed |
| FPT-006 | The touch faceplate shall keep its own mechanics in this repository. | must | Confirmed |
| FPT-007 | Display: 3.5" IPS, 480 × 800, MIPI DSI (ST7701S controller), with mainline Linux support. | should | Withdrawn |
| FPT-008 | Touch controller: Goodix GT911 (mainline driver). | should | Confirmed |
| FPT-009 | Stack: cover glass, touch and LCD laminated on an aluminum tray with a graphite spreader that also takes heat from the SoC. | should | Withdrawn |
| FPT-010 | Front sensors: ambient light sensor and microphone, next to the status LED. | should | Withdrawn |
| FPT-011 | Faceplate outline 53 × 90.5 × 3.6 mm. | should | Withdrawn |
| FPT-012 | The display panel shall already be supported by a mainline Linux panel driver (no kernel patch). | must | Withdrawn |
| FPT-013 | The display shall be a touch panel chosen for the best fit with the project requirements and commercial availability; a 3.5" IPS panel is the reference, not a fixed size or technology. | must | Confirmed |
| FPT-014 | The touch faceplate shall have a display and an ambient light sensor for dimming it (every faceplate has a display). | must | Confirmed |
| FPT-015 | The display driver shall be on the touch faceplate. | must | Confirmed |
| FPT-016 | The touch faceplate's status LED shall be controllable by developers, like the user LED on development boards. | must | Confirmed |
| FPT-017 | The main microphone shall be on the touch faceplate. | must | Confirmed |
| FPT-018 | The display panel should have a mainline Linux panel driver. If no suitable panel has one, OpenDAP may add the driver. | should | Confirmed |
| FPT-019 | For the display, availability outranks existing Debian support: choose the panel that is actually available, and provide its driver through DKMS or an upstreamed panel compatible if needed. | must | Confirmed |
| FPT-020 | The display shall keep an aspect ratio in about the same range as the body (height-to-width ≈1.5 to 1.6 in portrait), with **2:3 preferred**. | must | Confirmed |
| FPT-021 | The touch sensor shall be projected-capacitive multi-touch with good palm rejection. | must | Confirmed |
| FPT-022 | The display may need an additional cover glass (lens) so it fits and seals in the case; the stack shall account for it. Prefer the touch module's own cover lens or an off-the-shelf cover glass; a custom cover glass, or a custom touch sensor on the cover lens laminated to the panel, is allowed when it meets [t1 T1-038](../../../../product/docs/requirements/README.md). | must | Confirmed |
| FPT-023 | Front layout, seen from the front: above the display, the ambient light sensor centered and the status LED to the right, not all the way to the corner. | must | Confirmed |
| FPT-024 | Front layout, seen from the front: the main microphone centered below the display. | must | Confirmed |
| FPT-025 | The status LED should be RGB. If no compliant RGB part fits, a single colour is acceptable. | should | Confirmed |
| FPT-026 | The touch sensor should use the best available technology (for example in-cell or on-cell), with glove and wet operation where an available panel offers them (split from FPT-021). | should | Confirmed |
| FPT-027 | When choosing the display, high peak brightness and a low price come before resolution: a panel shall not be adopted for a higher resolution if it lowers the peak brightness below that of the current panel (800 cd/m², ADR 0001) or raises the cost materially (T1-090). | must | Confirmed |

## Context

- Body outline re-checked on 2026-10-27 against [t1 ADR 0006](../../../../product/docs/adr/0006-body-at-the-maximum-width.md) (Accepted): the body is now **62.5 × 95.0 × 25.0 mm**, which replaces the "about 59.5 × 91.5 mm" in the consequences of [ADR 0001](../adr/0001-focus-lcds-e35gh-display.md) and the 59.5 × 94.3 mm of t1 ADR 0003; the faceplate outline follows it ([faceplate interface](../../../../product/docs/specs/faceplate-interface.md) §8). The panel choice of ADR 0001 stands and nothing in it depends on the larger body. Fit against the new body: with 1.2 mm case walls the cavity is 60.1 × 92.6 mm ([board ADR 0025](../../../../board/docs/adr/0025-height-zones-in-the-wider-body.md) item 1), so the 54.46 × 82.94 mm display module leaves 2.82 mm per side across and 4.83 mm above and below it if centred (it was 0.92 mm across in a 59.5 mm body with 1.6 mm walls; the display's position on the board is **UNVERIFIED**, board placement); FPT-023 and FPT-024 gain that room for the ambient light sensor, the status LED and the microphone. FPT-020 holds: the module's 82.94 / 54.46 = 1.52 and the 2:3 panel match the body's 95.0 / 62.5 = 1.52. The display-to-board gap (1.3 mm), the stack above it (lens and OCA 0.9 mm, display 5.5 mm) and the FH35C tail are unchanged (interface §8). The 3.5" ST7703 touch module noted above (61.90 × 96.04 mm lens) still exceeds the body in height (96.04 > 95.0 mm).
- FPT-022 amended on 2026-10-25 to follow the amended [t1 T1-038](../../../../product/docs/requirements/README.md) (made-to-order parts a small independent project can obtain). Under it, the display was re-checked the same day: a 3.5" 640 × 960 panel on the Sitronix ST7703 (bare panel 54.56 × 82.84 × 2.25 mm) with a projected-capacitive GT911 sensor on our own cover lens, fully laminated with OCA, passes the viability test and every established requirement (ratio, envelope, DSI lanes 0–3, interface rails), and would shorten the front stack from about 6.4 mm to about 3.5 mm (**UNVERIFIED** until a drawing). It does not yet meet T1-090's cost condition, so [ADR 0001](../adr/0001-focus-lcds-e35gh-display.md) stands until that is shown. Custom-cut or semi-custom AMOLED panels remain out: re-cutting a panel is a panel-fab step, and none of the candidates' display driver ICs has a public command set for a mainline driver.
- Display re-checked on 2026-10-25 under [t1 T1-090](../../../../product/docs/requirements/README.md) (best display technology that meets the established requirements without a material cost change). Result: [ADR 0001](../adr/0001-focus-lcds-e35gh-display.md) stands. No small AMOLED panel with MIPI DSI meets FPT-020 and the module width (the 3.92" 1080 × 1240 panel is 1.15 in ratio and 67.25 mm wide). The nearest improvement, a 3.5" 640 × 960 IPS panel on the Sitronix ST7703 (mainline `panel-sitronix-st7703`), is offered as a touch module only with a 61.90 × 96.04 mm lens, which exceeds the body; without touch it fails FPT-002 and T1-038. It would use DSI lanes 0–1 or 0–3 of the existing interface and no new rail.
- FPT-008 confirmed on 2026-10-24: [ADR 0001](../adr/0001-focus-lcds-e35gh-display.md) (Accepted) fixes the GT911 with the display.
- Revised on 2026-10-22: FPT-010 withdrawn as a duplicate of FPT-014, FPT-017, FPT-023 and FPT-024; FPT-021 split into FPT-021 (must) and FPT-026 (should); FPT-018 is should, matching its wording (a mainline driver is preferred, not mandatory).
- FPT-007 to FPT-011: recorded on 2026-10-21 as **Draft**. FPT-007, FPT-009 and FPT-011 were withdrawn on 2026-10-21 and FPT-010 on 2026-10-22.
- Mainline-supported panels already used on RK3566 handhelds (for example the Anbernic RG353P panel, `panel-newvision-nv3051d`) show which panels qualify.
- FPT-012 was replaced by the requirement above (2026-10-21): a mainline driver is preferred, not mandatory. Debian's kernel may also need the driver enabled; asking Debian is the standard path.
- The concept art (`docs/concept-art/touch-faceplate-three-quarter.png`) shows the status LED above the display on the right and the microphone below it at the center. Use it as a visual reference only.
- FPT-025: board BOM v1.2 proposes an RGB LED (Everlight 19-337/R6GHBHC-A01/2T) on the faceplate, driven from the main board by a TI LP5521 I2C driver whose charge pump gives green and blue their forward voltage with margin at low battery; the faceplate connector carries one line per colour (Proposed, not yet confirmed).
- FPT-023 and FPT-024 are the preferred layout. If the microphone or the status LED do not fit around the display panel, they may move to other positions (maintainers, 2026-10-22).
- FPT-027 (maintainers, 2026-10-25): offered a 3.5" 640 × 960 IPS with a laminated touch lens (about 400–500 cd/m²), the maintainers preferred high brightness and a low price; ADR 0001 stands.
