# T1 battery pack specification (2S, contact interface)

- **Status:** Draft v0.1 (2026-10-25)
- **Applies:** [ADR 0014](../adr/0014-two-cell-battery.md) item 2 (2S pack criteria), [ADR 0020](../adr/0020-battery-connected-through-contacts.md) (contact interface), T1-079 (published pack specification), T1-080 (labels)
- **Board side:** [PCB design constraints](pcb-design-constraints.md) §6.1 (PCB-L-04 to PCB-L-10)

## 1. Pack specification additions

The made-to-order 2S pack (ADR 0014 item 2, T1-038 exception) connects through contacts (ADR 0020). In addition to the ADR 0014 item 2 criteria, its specification holds:

| Item | Specification |
|---|---|
| Terminal board | A rigid board at the PCM end of the pack, part of or soldered to the PCM board, its pad face flush with the pack's underside except for the recesses |
| Pads | Seven positions at 3.5 mm pitch in one row: P+, P+, (no pad), mid-cell tap, NTC, P−, P−. Each pad at least 4.0 × 2.5 mm (the contact's mating pad, drawing 70-9258-001-1X0-00XS sheet 2), lengthened along the contact axis by the pack's position tolerance in the pocket; gaps between pads ≥ 1.0 mm |
| Plating | Electrolytic hard gold, ≥ 0.76 µm, over nickel (thickness of nickel per the maker's practice, **UNVERIFIED** value to set); no ENIG or immersion gold in the contact area |
| Recess | Power pads 0.2 mm, signal pads 0.4 mm below the pack's underside, so power makes first and breaks last (ADR 0020 item 5); walls of the end cap around each group, so a flat metal object lying on the pack cannot touch two pads |
| Keying | Asymmetric terminal end matching the pocket (case input); polarity marked next to the pads (IEC 62133-2 clause 5.5) |
| Current | Each power pad and its copper to the PCM carry ≥ 5 A continuous |
| PCM | As ADR 0014 item 2 (over-charge, over-discharge, over-current trip 4.0–5.0 A, short-circuit, balancing), plus its short-circuit detection delay and threshold stated, and a pulse of 63 A for 2 µs (the estimated insertion pulse, ADR 0020 item 8) shown not to trip it, or the actual behaviour stated |
| Tests | UN 38.3 (T.5 external short at the pads) and IEC 62133-2 (7.3.2 external short with a single fault in the protection) on the pack as shipped, with exposed pads (T1-079) |
| Transport and spares | A terminal cover or separating packaging for spare packs |
| Label | Art. 13 and WEEE marks (T1-080), polarity at the pads, the specification identifier |
| Published | The full pack specification, so any maker can build a replacement (T1-079) |

## 2. Qualification of the T1 contact interface

| Row | Test | Pass | Level | T1 value |
|---|---|---|---|---|
| CB-01 | Contact resistance, initial (4-wire, dry circuit) | ≤ the device budget per contact | Q1 | ≤ 20 mΩ per contact at end of life (budget assumed in ADR 0020 item 3; replace with KYOCERA AVX specification 201-01-252) |
| CB-02 | Temperature rise at the worst continuous current per pole, and at the trip current for the protection's time | Within the pack's and the contact's limits; the device's derating met | Q0 (trip), Q1 | 3.2 A per pole continuous, 5 A per pole for the PCM's trip time; contact and pad temperature below the pack's charge limit at the pocket |
| CB-03 | Durability: rated cycles with the real pack motion (insert end first, press down) | ΔR within the maker's limit; no plating wear-through | Q2 | — |
| CB-04 | Vibration and mechanical shock with event detection; device drop tests with the pack fitted | No interruption longer than the system's hold-up; no reset | Q2 | Drop tests of the T1 (t1 verification matrix) with event detection on BAT; no reset on battery |
| CB-05 | Thermal cycling, damp heat, and a corrosive-gas exposure (mixed flowing gas or H₂S, where the market needs it) | ΔR within limits | Q2 | — |
| CB-06 | Fretting: micromotion at the pad over the device's vibration spectrum | Resistance stable | Q3 | — |
| CB-07 | Insertion with and without an adapter: inrush current and voltage at every part on the battery node | Within absolute maxima; no PCM trip; fuse I²t far below melting | Q0 | BAT, BATP and the pack side of the fuse ≤ 20 V × the BRD-049 margin; no PCM trip |
| CB-08 | Removal under the worst load, with and without an adapter | No damage; system behaviour as designed (cover-open power-down, power path takes over) | Q1 | — |
| CB-09 | Reverse, tilted and one-pitch-misaligned insertion attempts | No contact between the wrong poles; no damage | Q0 | — |
| CB-10 | ESD on the pads and the host contacts (IEC 61000-4-2) | No damage; no lasting fault | Q2 | — |
| CB-11 | Pack external short circuit at the pads (IEC 62133-2, UN 38.3 T.5) | Pass, in the pack makers' reports | Q2 (UN 38.3), Q3 | — |
| CB-12 | Gauge accuracy through the contacts after CB-03 to CB-06 | State-of-charge error within the device's target | Q3 | Gauge state of charge within the T1 target after CB-03 to CB-06 |

Before the board freezes: obtain KYOCERA AVX product specification 201-01-252 (force, resistance, current-rating basis); build a bench terminal board (the pack's pad layout on a small board, wired to a bench supply or a protected 2S pack) so prototype 1 is brought up through the same contacts (ADR 0014 item 4).

## 3. Sources

- KYOCERA AVX: TDS-BTB-0026 Rev 1 (9258-100), 2025-09-10; drawing 70-9258-001-1X0-00XS Rev F; catalog *Board to Board Connectors 090325* (pp. 8, 12, 13, 36).
- TI SLUSDV2C (BQ25798): §5 pin table (BAT, BATP, SDRV), Figure 8-2 notes.
- IEC 62133-2 (clauses 5.5 and 7.3.2); UN 38.3 (T.5); Regulation (EU) 2023/1542 Art. 11 and 13.
