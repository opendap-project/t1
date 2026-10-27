# ADR 0011: Battery path rated for the full output budget

- **Status:** Superseded by [ADR 0014](0014-two-cell-battery.md) (2026-10-22). Previously: Accepted (2026-10-22), superseding [ADR 0007](0007-off-the-shelf-battery.md).
- **Date:** 2026-10-22

## Context

BRD-050 asks the battery path to carry the full HAT and USB-C output budget on battery, with a more robust battery connection if the off-the-shelf lead or connector cannot. BRD-049 puts power safety first: every rail, converter, connector and cable runs with margin below its rating and is protected.

With the Adafruit 328 of ADR 0007, BOM v1.1 derated the battery path to 1.6 A continuous (26 AWG lead into a JST PH contact that JST rates at 2 A with AWG #24 only), which leaves about 0.4 A at 5.1 V for HAT_5V and the USB-C source together. Changing the board connector alone does not help, because the lead and its crimp belong to the pack. The cell itself is rated 2C (5 A) maximum discharge (Q/WAPL785060-1011 p. 7).

The full output budget, as BOM v1.2 defines it, is the same on battery as on external power: 1.5 A at 5.1 V shared by HAT_5V and the USB-C source (the 5 V boost's 1.6 A design output), plus HAT_3V3 at 1.0 A, with the system at its estimated 3 W. That is about 15.9 W, **4.8 A from the battery at VSYS = 3.3 V** (power tree §4.7). The BQ25895 allows 6 A continuous battery discharge through its BATFET (SLUSC88C §7.3), so 4.8 A is 80 % of its rating. Serving HAT_5V and the USB-C source at 1.5 A each at the same time would need about 7.3 A, above the charger's rating: that is not part of this budget.

Against 4.8 A the Adafruit 328 cannot comply at any connection: 4.8 A is 96 % of the cell's 5 A maximum. No off-the-shelf lithium-polymer pack found on 2026-10-22 fits the 11.8 × 53.5 × 63.25 mm pocket, has a protection circuit and publishes a discharge rating of 6 A or more (the search was partial).

## Decision

1. **Battery acceptance criteria.** A pack is adopted only if it is off the shelf, available through authorized channels and meets all of:
   - continuous discharge rating ≥ 6.0 A (4.8 A at 80 %);
   - protection circuit with an over-current trip ≥ 6.0 A and short-circuit protection;
   - leads and pack connector rated ≥ 6.9 A per pole (4.8 A at 70 %), latching;
   - ≥ 2,000 mAh, inside the 11.8 × 53.5 × 63.25 mm pocket, UN 38.3 report (IEC 62133-2 for the Commercial edition);
   - 4.2 V or LiHV chemistry ([ADR 0008](0008-battery-technology-ready-for-lihv.md) unchanged).
2. **The board is built for the full budget whatever pack is fitted:** BATFET path, VSYS copper, sense resistors and a board fuse in series with BAT+ sized for 4.8 A continuous (BOM v1.2 lines 43, 47, 104; power tree §4.7). The battery connector footprint and the fuse value follow the pack.
3. **Interim pack.** Until a compliant pack is qualified, the Adafruit 328 stays the bring-up and DIY pack with the v1.1 limits: 1.6 A battery budget enforced in software, a 2.5 A board fuse in the same footprint to protect its lead and connector, and about 0.4 A at 5.1 V for HAT_5V and USB-C source on battery. **BRD-050 is not met with it.**
4. The search for a compliant off-the-shelf pack (same size class) continues before the board freezes.

## Consequences

- BRD-050 is met only when a pack that meets item 1 is found; until then the output budget on battery stays at the v1.1 figure.
- If no off-the-shelf pack meets item 1, the maintainers choose between a lower on-battery output budget, a made-to-order pack (against T1-038), or a different charger and cell format.

## Status of the branches (2026-10-22)

- **No off-the-shelf pack meets this ADR**, in 1S or in 2S: no 1S pouch pack in the size class publishes a ≥ 6 A continuous rating, and cylindrical cells do not fit the pocket's thickness.
- **Branch A is in effect:** the Adafruit 328 with the 1.6 A battery budget (about 0.4 A at 5.1 V for HAT and USB-C output on battery) and the Blackbird OS output ceiling of ADR 0012, shown to the user as a safety limit (T1-045). The board side stays sized for the full 4.8 A budget, so a compliant pack can be fitted without a board change.
- **Branches B and C need an exception to T1-038** (no made-to-order parts), which is the maintainers' call. If granted, a made-to-order **2S** pack of two ordinary cells (about 1.5 Ah each) is the better form of that exception: it needs no 6 A high-rate cell, and every other 2S part (BQ25798 charger, BQ28Z610 gauge with protection and balancing, pre-regulator to the existing 1S tree) is an off-the-shelf part.
