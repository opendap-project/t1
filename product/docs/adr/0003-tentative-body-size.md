# ADR 0003: Tentative body size

- **Status:** Superseded by [ADR 0006](0006-body-at-the-maximum-width.md) (2026-10-27; the body grows to the T1-031 maximum, 62.5 × 95.0 × 25.0 mm; the measurement gate is carried over). Previously: Accepted.
- **Date:** 2026-10-22
- **Basis:** the product rules

## Context

The body should be as close to a credit card as possible, keep its proportions and be as thin as possible (T1-032, T1-033), but may grow up to the maximum (T1-031) when needed. The display fixes the width at about 59.5 mm (faceplate-touch ADR 0001). Battery capacity is maximized within the body (T1-035) and autonomy should stay around the category average (T1-037).

## Decision

- The tentative body is **59.5 × 94.3 × 24 mm** (credit-card proportions at the display's width), to be tightened around the off-the-shelf battery (board ADR 0007, about 88 % of the category's average audiophile runtime). Only catalog cells are used (T1-038).
- The design does not wait for a development kit (T1-042). Until real measurements exist, the body stays at the conservative **24 mm** and is not shrunk, so a larger off-the-shelf pack can still fit if the estimate turns out pessimistic; power-saving levers (gating the unused output's amplifiers, large audio buffers, clock and block gating) are designed in from the start.
- When measurements exist (a Radxa ZERO 3 is planned, or the prototype itself), apply T1-037 and T1-039: the measured pessimistic runtime must clear the 6 h red line, and the thickness shrinks toward 20 mm only while runtime stays around the category average.

## Notes

- Note (2026-10-24): the battery basis above is superseded. Board ADR 0007 (off-the-shelf Adafruit 328) was superseded by board ADR 0011, and [board ADR 0014](../../../board/docs/adr/0014-two-cell-battery.md) (Accepted) moves the T1 to a 2S pack of catalog cells, admitted as a T1-038 exception like the cover glass. "Only catalog cells" still holds; the pack itself is the exception. The body size and the measurement gate of this decision are unchanged; the 2S pack is sized to the battery pocket of this body.
- Note (2026-10-24): [board ADR 0016](../../../board/docs/adr/0016-front-side-height-under-the-display.md) (Accepted) grows the display-to-board gap from 0.3 to 1.3 mm so the main board can carry parts of up to 1.0 mm under the display. The extra 1.0 mm comes from body thickness, not from the battery: the tentative body becomes 59.5 × 94.3 × 25.0 mm (T1-031 maximum), and the battery pocket is unchanged. The measurement gate of this decision is unchanged.
