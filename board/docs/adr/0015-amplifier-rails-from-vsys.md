# ADR 0015: Amplifier rails sized for the full-scale peak

- **Status:** Accepted. Supersedes the rail items of [ADR 0012](0012-headphone-output-stage.md) (its "±6 V amplifier rails" decision and its "Inverter margin" and "Interim battery" conditions); the rest of ADR 0012 stands.
- **Date:** 2026-10-22

## Context

ADR 0012 asked for a simulation of the TPS65131 inverter before layout. The output-stage simulation ([`sim/output-stage/`](../../sim/output-stage/README.md), Results) found that a full-scale sine makes each amplifier rail draw a full-wave rectified current whose peak (433 mA) is well above the 275 mA average ADR 0012 used, and the converters follow the peak:

- the TPS65131 inverter needs 1.82 A against its 1.8 A minimum switch limit (101 %), even on the 3.8 V pre-regulated input of [ADR 0014](0014-two-cell-battery.md);
- a single LT3045 or LT3094 per rail cannot pass the amplifiers' peak (about 457 mA from the OPA1622 clip point) with margin: its current limit would have to exceed its 500 mA rating.

A software output cap would fix both by lowering the output, which the product rules do not allow for the audio path. The paralleled OPA1622 halves share current correctly (53/47 %, simulated with TI's model), so the amplifier side of ADR 0012 stands.

## Decision

1. **−7 V pre-rail:** a TI **LMR33630C** (2.1 MHz) in inverting buck-boost topology, fed from VSYS, as TI's application note SNVA856B describes. It replaces the TPS65131 inverter half, which is not used (connection per the simulation note, to be confirmed with TI before layout). The LMR33620C, same package and pins, is the second source.
2. **+7 V pre-rail:** stays on the TPS65131 boost half, from VSYS_LV.
3. **±6 V rails:** two LT3045 in parallel on the positive rail and two LT3094 in parallel on the negative rail, as both ADI datasheets describe, with current limits set to pass the full-scale peak with margin (RILIM 523 Ω per LT3045, 13.0 kΩ per LT3094: ±516–646 mA per rail). Pre-rails stay at ±7.0 V.
4. **Sequencing:** `HPA_RAIL_EN` enables both pre-rail converters (the LMR33630C enable through a level shifter, since its ground is the −7 V rail); the regulators are enabled at least 10 ms later, then the amplifiers.
5. **No output ceiling:** the full ADR 0012 output is available on a compliant ADR 0014 pack.

## Consequences

- BOM and power tree change as above (the simulation note §5 has the values).
- Margins (simulated): LMR33630C at 47 % of its minimum switch limit at the full-scale peak and 55 % at the regulators' current-limit case; 48 % of its voltage rating. The TPS65131 boost runs at 56–78 % in operation and reaches about 99 % (worst-case parameters) only when the positive regulators trip at their maximum limit, inside the 100 % rule for a limiting case; confirmed on the bench before the board freezes.
- To measure on the first boards: the LMR33630C idle pulse-skipping bursts at the amplifier output, its heat (0.4–0.9 W est. at 0.78 A), and the regulators' current sharing.
