# ADR 0012: Headphone output stage

- **Status:** Accepted; its rail items are superseded by [ADR 0015](0015-amplifier-rails-from-vsys.md).
- **Date:** 2026-10-22
- **Note (2026-10-24):** the superseded items are those [ADR 0015](0015-amplifier-rails-from-vsys.md) names: the "±6 V amplifier rails" decision and the "Interim battery" and "Inverter margin" conditions. The interim pack itself was removed by [ADR 0014](0014-two-cell-battery.md) (items 3–4).

## Context

The BOM v1.2 output stage (four OPA1622 at ±5 V) delivers ≈ 125 mW single-ended and 150–190 mW balanced into 32 Ω, about 2 dB short single-ended and about 6 dB short balanced of the output that current portable players with the same two CS43198 DACs deliver into 32 Ω (195–245 mW single-ended, 660–700 mW balanced). The OPA1622 clips at about 100 mA per amplifier at ±5 V. The planned 2 Vrms per DAC output also needed the CS43198 `+1dB_EN` mode, specified at −105 dB THD+N instead of −115 dB.

## Decision

- **Six OPA1622** instead of four: on each balanced leg, both halves of one package run in parallel (current sharing through small ballast resistors inside the loop).
- **±6 V amplifier rails** from the TPS65131 through an **LT3045 / LT3094** pair, replacing the TPS7A4901 / TPS7A3001, which would run at 183 % of its rating. This amends the rail line of ADR 0009.
- **Level from the amplifier, not the DAC:** CS43198 at `+1dB_EN = 0` (its −115 dB THD+N mode), amplifier gain about 1.6.
- Expected output (desk estimate, to be measured): about 240 mW single-ended and about 640 mW balanced into 32 Ω (490–760 mW depending on current sharing).

## Conditions (BRD-049)

- **Interim battery:** a full-scale balanced 32 Ω sine draws about 1.4–1.6 A from VSYS, at the interim pack's 1.6 A budget. While the Adafruit 328 is fitted, Blackbird OS applies an output ceiling that keeps the battery current inside its budget; the full output needs an ADR 0011 pack.
- **Inverter margin:** the TPS65131 inverter runs at 72–79 % of its minimum switch current limit, at the edge of the 80 % rule. Confirmed by simulation before layout freeze, or the inverter is replaced by one with more margin.
- **Current sharing** between paralleled halves and the LT3045/LT3094 figures (datasheets not yet read in full) are **UNVERIFIED** until simulated and measured.

## Consequences

- BRD-022 is amended (four → six OPA1622). BOM v1.3 carries the parts, rails and passives.
- Autonomy: the core single-ended session drops about 11 % in the battery-life model (12.8 → 11.4 h on the Adafruit 328; 16.3 → 14.6 h on a 105060-class pack). The more conservative power-tree budget gives 7.1–10.1 h on the Adafruit 328 (v1.2: 7.6–11.1 h): its pessimistic end is below the T1-039 8 h warning, above the 6 h red line. The OPA1622 quiescent current is the largest audio term; powering the amplifier stage down when playback is paused, and measuring the SoC (the largest uncertainty), are the levers (power tree §4.9).
- Board area: about +80–110 mm².
