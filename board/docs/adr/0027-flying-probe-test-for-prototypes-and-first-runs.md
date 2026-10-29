# ADR 0027: Flying-probe test for prototypes and first runs

- **Status:** Accepted (2026-10-28). Supersedes the single-sided-fixture consequence of [ADR 0016](0016-front-side-height-under-the-display.md) ("flat test pads go on the front … for a single-sided fixture"), which [ADR 0025](0025-height-zones-in-the-wider-body.md) carried into the placement (placement v1 decision 9).
- **Date:** 2026-10-28
- **Basis:** BRD-047 (must: bring-up access); PCB-T-01, PCB-T-02, PCB-T-09 (test access); PCB-D-06 to PCB-D-09 (test-pad size, spacing and clearances); [placement v1](../specs/placement-v1.md) decision 9; the obsolete-item audit of 2026-10-28 (585 mm² of front courtyard were test pads held on the front by the fixture rule).

## Context

ADR 0016 put every flat test pad on the front so that one bed-of-nails fixture could reach them all. The front is the display side, limited to 1.0 mm parts (PCB-Z-03); the back carries the tall parts and the BGAs. Prototypes and first production runs are small builds, where a dedicated fixture is not made.

## Decision

1. Prototypes and first production runs are tested by **flying probe**, which reaches both sides of the board.
2. Flat test pads may stand on **either side**, where the zone of their net allows a part of their height on that side (PCB-S-17 keeps a test pad's track in its net's zone). The placement takes the nearest free spot to the pads a test pad serves, the front on a tie.
3. The test-pad size, spacing and clearance rows (PCB-D-06 to PCB-D-09) stay as they are on both sides.

## Consequences

- The placement no longer reserves front area for test pads. On the placement of 2026-10-28, 18 of the 156 board test pads take the back; the placer fills the front cells they leave with passives, so the front courtyard stays at about 2,800 mm² and the board need at 99.2 %: the front was not the binding side.
- A fixture for a later volume run is a new decision: it would need its pads on one side again or a two-sided fixture.
