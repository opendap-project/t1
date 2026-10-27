# Case requirements

Requirements for the physical case of the OpenDAP T1: core with the basic back cover, and the HAT case. Product requirements are in [`t1`](https://github.com/opendap-project/t1).

| ID | Requirement | Priority | Status |
|---|---|---|---|
| CASE-001 | The device footprint shall be approximately that of a credit card (ISO/IEC 7810 ID-1: 85.60 × 53.98 mm). | must | Moved |
| CASE-002 | The left edge shall carry the **Action**, **Volume +** and **Volume −** buttons. | must | Moved |
| CASE-003 | The right edge shall carry the **Main / Power** button. | must | Moved |
| CASE-004 | The bottom edge shall carry, from left to right: a 3.5 mm jack, a 4.4 mm jack, a USB-C port (centered) and the integrated mono speaker (right side). | must | Moved |
| CASE-005 | The Commercial and DIY editions shall use exactly the same design, differing only in manufacturing precision. | must | Moved |
| CASE-006 | The basic back cover shall be swappable for a HAT case, following the HAT Case Standard. | must | Confirmed |
| CASE-007 | The Commercial edition should reach at least IP65, or the ingress protection standard of its product category. | should | Moved |
| CASE-008 | The front shall accept interchangeable faceplates. The default faceplate is the touch faceplate. | must | Moved |
| CASE-009 | The case shall define the faceplate interface: flat-cable connector pinout, dimensions and anchoring with screws. | must | Moved |
| CASE-010 | Faceplates are not meant to be swapped regularly. | must | Moved |
| CASE-011 | Faceplate identification should rely on the faceplate interface pinout; an EEPROM only if the pinout cannot do it. | should | Moved |
| CASE-012 | Coordinate system for every mechanical part: origin at the device center, x across the width, y along the length, z through the thickness with +z towards the faceplate. General tolerances ISO 2768-m. | must | Moved |
| CASE-013 | Body footprint 92.5 × 55 mm with R 8.5 squircle corners (close to a credit card, CASE-001). | should | Withdrawn |
| CASE-014 | Body thickness about 19 mm. | should | Withdrawn |
| CASE-015 | Wall thickness 1.6 mm. | should | Withdrawn |
| CASE-016 | Buttons: Action on the left (Ø11, two-stage), Volume +/− as one capsule on the left, Main/Power on the right. | should | Withdrawn |
| CASE-017 | Bottom-edge positions: 3.5 mm jack at x −17.3, 4.4 mm jack at x −9.5, USB-C at x 0, speaker from x 8.1 to 16.9. | should | Withdrawn |
| CASE-018 | The faceplate shall be held by four M1.6 screws from the back. | should | Withdrawn |
| CASE-019 | The battery shall be a catalog Li-Po cell (654060 size, about 1,950 mAh / 7.2 Wh), with its protection on the board. | should | Withdrawn |
| CASE-020 | The first cases shall be made of a polymer (PC or ABS). | must | Confirmed |
| CASE-021 | The default finish shall be a graphite-colored polymer with a grip texture. | should | Confirmed |
| CASE-022 | Later material options: crystal clear, carbon and anodized aluminum. | should | Confirmed |
| CASE-023 | The Action button shall have a deeper travel and a clearer click; the other buttons need no special click or travel. | must | Moved |
| CASE-024 | The faceplate, the board and the device-side piece of the HAT case (when fitted) shall be screwed in place. | must | Confirmed |
| CASE-025 | The plain back cover (when no HAT case is fitted) shall snap on. | must | Confirmed |
| CASE-026 | Faceplate controls shall not send raw signals: the faceplate interface shall standardize binary commands that a DAP needs. | must | Moved |
| CASE-027 | The command set shall have a well-standardized core that is not minimal, plus reserved space for new commands. | must | Moved |
| CASE-028 | All mechanics, materials and finishes shall be producible as prototypes within the processes the prototype fab publishes (CNC machining, 3D printing, sheet metal, injection moulding, anodising and other finishes). | must | Confirmed |

## Open questions

- Device thickness.
- Final ingress protection target for the Commercial edition.

## Context

- CASE-021 is should since 2026-10-22: a colour and texture do not decide the promise.
- CASE-012 to CASE-019: recorded on 2026-10-21 as **Draft**.
- Withdrawn on 2026-10-21: CASE-013, CASE-014, CASE-015, CASE-016, CASE-017, CASE-018, CASE-019.
- Moved to `t1` on 2026-10-21 (the case repository covers only the physical case): CASE-001 → T1-013, CASE-002 → T1-014, CASE-003 → T1-015, CASE-004 → T1-016, CASE-007 → T1-017, CASE-009 → T1-018, CASE-010 → T1-019, CASE-011 → T1-020, CASE-012 → T1-021, CASE-023 → T1-022, CASE-026 → T1-023, CASE-027 → T1-024, CASE-005 → T1-004, CASE-008 → T1-003. CASE-005 and CASE-008 were already T1-004 and T1-003.
