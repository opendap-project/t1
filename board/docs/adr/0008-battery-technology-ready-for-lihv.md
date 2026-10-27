# ADR 0008: Battery technology, ready for LiHV

- **Status:** Accepted
- **Date:** 2026-10-22
- **Note (2026-10-24):** the decision stands ([ADR 0014](0014-two-cell-battery.md) item 2 keeps 4.2 V or LiHV cells), but the parts named below are superseded by ADR 0014 and [BOM v1](../specs/bom-v1.md) v1.5: the charger is the TI BQ25798 (line 39), the gauge the TI BQ28Z610-R1 (line 42), and the pack a quoted 2S pack, a T1-038 exception (line 46). The Adafruit 328 is no longer a T1 pack.

## Context

The maintainers wants the best, most modern battery technology for the project. Today the most modern chemistry sold off the shelf is lithium-ion polymer with high-voltage cathodes (LiHV, 4.40–4.45 V charge), with about 10 % more energy in the same volume; silicon-anode cells are not sold off the shelf. No off-the-shelf LiHV pack of 2,000 mAh or more fits the bay, and parts must be off the shelf (T1-038).

## Decision

- The power design is **LiHV-ready**: the charger (BQ25895, charge voltage programmable up to 4.608 V) and the fuel gauge (MAX17055, configurable cell model) are configured per pack, the board's battery protection and thermal limits cover 4.45 V cells, and the charge voltage comes from the pack's identity in software, never hard-coded.
- The pack in use is the **most modern off-the-shelf, stocked and certified one that fits**. Today that is a standard 4.2 V lithium-ion polymer pack (Adafruit 328, [ADR 0007](0007-off-the-shelf-battery.md)); a stocked, certified LiHV pack replaces it as soon as one fits.
