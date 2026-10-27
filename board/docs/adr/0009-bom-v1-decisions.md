# ADR 0009: BOM v1 decisions

- **Status:** Accepted
- **Date:** 2026-10-22
- **Note (2026-10-24):** the HAT power pair is a 50-contact DF40 since [BOM v1](../specs/bom-v1.md) v1.2 (line 66), not the 30-pin pair named below; the 100-pin signal pair is unchanged.

## Context

The complete BOM v1 draft (since superseded by [`../specs/bom-v1.md`](../specs/bom-v1.md)) and power tree ([`../specs/power-tree-v0.md`](../specs/power-tree-v0.md)) found errors in v0 and left choices open. The audiophile experience is never sacrificed (T1-040).

## Decision

- **Audio master clocks:** 22.5792 MHz and 24.576 MHz at 1.8 V, as the CS43198 requires (BRD-023 corrected). The parts must be low-jitter and in stock; no active level translator in the clock path, because it would degrade jitter. Revised by [ADR 0010](0010-audio-master-clock-source.md): a stocked 3.3 V oscillator through a passive attenuator.
- **Headphone amplifier rails** (amended by [ADR 0012](0012-headphone-output-stage.md): ±6 V through LT3045/LT3094, six OPA1622): ±5 V from a TPS65131 followed by low-noise TPS7A4901 / TPS7A3001 regulators, the minimum for 4 Vrms balanced output with 1 V of headroom.
- **MaskROM entry:** holding **Power + Volume −** at power-on forces MaskROM (BRD-035); the power button alone never does, so normal boots are not affected.
- **PMIC configuration:** follow the RK809-5 configuration of an RK3566 reference design that uses the same PMIC (the Orange Pi 3B; Quartz64 and Radxa ZERO 3 use the RK817).
- **HAT flat-cable connector:** chosen during the BOM cross-validation: Hirose DF40, a 100-pin and a 30-pin pair on an impedance-controlled FPC ([BOM v1](../specs/bom-v1.md)), pending a 5 Gb/s test coupon.
