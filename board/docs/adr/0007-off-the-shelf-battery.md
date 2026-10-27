# ADR 0007: Off-the-shelf battery

- **Status:** Superseded by [ADR 0011](0011-battery-path-rated-for-the-full-output-budget.md). The Adafruit 328 remains the interim prototype pack.
- **Date:** 2026-10-22
- **Note (2026-10-24):** ADR 0011 was in turn superseded by [ADR 0014](0014-two-cell-battery.md), under which the Adafruit 328 is no longer a T1 pack (item 4); bring-up uses a bench supply or a protected 2S pack.

## Context

ADR 0005 relied on a 105060 pack made to order. The maintainers rules out custom or made-to-order components (T1-038). The battery must still be standard and commercial, at least 2,000 mAh, as large as fits (T1-035), certified and user-replaceable.

## Decision

- Use **off-the-shelf, stocked catalog packs only**. The primary is the **Adafruit 328** (2,500 mAh, 9.4 Wh, protection circuit and JST connector), estimated at about 88 % of the category's average audiophile runtime, within the "slightly below average" allowed by T1-037. The **Adafruit 2011** (2,000 mAh) is the second source.
- The battery bay is sized for the Adafruit 328; an NTC sits on the board, because the stocked packs have none.
- Larger stocked packs are re-checked before the design freezes; any pack adopted must have its safety reports (UN 38.3 at least, IEC 62133-2 for the Commercial edition) and real stock.
