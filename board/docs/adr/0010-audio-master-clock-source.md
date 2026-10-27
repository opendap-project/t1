# ADR 0010: Audio master clock source

- **Status:** Accepted (revised 2026-10-22 after the maintainers' review: no dependence on parts whose supply is not known)
- **Date:** 2026-10-22
- **Amended (2026-10-24) by [ADR 0019](0019-master-clock-divided-from-twice-the-frequency.md):** the oscillators run at 45.1584 / 49.152 MHz and one SN74AUC1G74 per DAC divides by two on a 1.8 V rail; the passive attenuator below is removed (it could not guarantee the 45–55 % duty or the oscillator's 15 pF load).
- **Note (2026-10-24):** since [ADR 0014](0014-two-cell-battery.md) (BOM v1.5) the TPS7A2031 is fed from VSYS_LV, a fixed 3.8 V from the TPS62136, so it has 0.7 V of headroom at every battery state. The "VSYS down to 3.4 V" case and the consequence on VSYS following the battery below applied to the 1S tree.

## Context

The CS43198 takes an external MCLK only at 22.5792 or 24.576 MHz, on its 1.8 V VL domain (BRD-023). The BOM v1 cross-validation found:

- NDK NSC5083A (1.8 V) has no authorized source. The project does not depend on parts it may not get.
- No other available, audio-grade 1.8 V oscillator exists at 22.5792 MHz: the TI CDC6C is about 60 dB worse close to the carrier; the Epson SG-210STF at 22.5792 MHz is obsolete; the Kyocera candidate has no authorized source; MEMS parts are rejected; available general-purpose XOs publish no phase-noise data.
- The 3.3 V NDK NSC5083D is available from authorized distributors and has the best phase noise of every candidate (−164 dBc/Hz at 1 kHz, against −158 dBc/Hz for the 1.8 V NSC5083A).

ADR 0009 excluded "a 3.3 V oscillator behind a level translator" because an active translator adds jitter. A passive attenuator adds no active stage.

## Decision

- **Oscillators:** NDK NSC5083D-22.5792M and NSC5083D-24.576M (NZ2520SDA, 3.3 V), one per rate family, the DAC as clock master (BRD-023).
- **Supply:** a dedicated low-noise LDO, MCLK_3V1 (TI TPS7A2031, 3.1 V), only for the two oscillators. 3.1 V is inside the NSC5083D supply range (2.97–3.63 V) and keeps the LDO's recommended 0.3 V headroom with VSYS down to 3.4 V on battery (BOM v1.1, D5). Phase noise at 3.1 V is **UNVERIFIED**; the catalogue figure is at 3.3 V.
- **Level adaptation:** a passive, series-terminated resistive attenuator from each oscillator output into the shared MCLK net at the CS43198 XTI/MCLK input (VL 1.8 V). No active translator in the clock path. The values are set in the schematic so the edge at XTI stays inside the VL input limits and does not slow down materially; this is checked by SPICE with the CS43198 input capacitance before layout freeze.
- **Tri-state:** each oscillator's ST pin is driven at 3.3 V logic (from the TCA6416A expander, or a single-bit translator if the expander port is not at 3.3 V; fixed in pinout v1). One oscillator runs at a time.
- **Second source:** a 3.3 V audio-grade XO in a compatible package, to be qualified (Crystek CCHD-957 class; availability **UNVERIFIED**).
- This revision supersedes the "no 3.3 V oscillator" line of ADR 0009.

## Consequences

- BOM v1 lines 20–21 are *Decided*, each with authorized sources. No part on the clock path is made to order.
- The power tree replaces MCLK_1V8 with MCLK_3V1 from VSYS. VSYS follows the battery, so a 3.3 V output would not keep the LDO's headroom at low charge (amended 2026-10-22 with BOM v1.1).
- The SoC GPIOs that drove the oscillator enables at 1.8 V (pin plan 4_B4, 4_C0) are freed or reassigned in pinout v1.
- Verification: SPICE for the attenuator edge, then the J-test and THD+N captures of the verification toolkit on the first boards.
