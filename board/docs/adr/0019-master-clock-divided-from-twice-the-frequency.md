# ADR 0019: Master clock divided from twice the frequency

- **Status:** Accepted
- **Date:** 2026-10-24
- **Amends:** [ADR 0010](0010-audio-master-clock-source.md) (oscillator frequencies and level adaptation; the oscillator family, its supply and the DAC as clock master stand)

## Context

ADR 0010 feeds both CS43198 XTI/MCLK inputs from an NDK NSC5083D (NZ2520SDA, 3.3 V class) at
22.5792 or 24.576 MHz on MCLK_3V1, through a passive attenuator. The attenuator simulation
([`sim/mclk-attenuator/`](../../sim/mclk-attenuator/README.md)) and the duty and load review
found two faults no passive values remove:

- The NZ2520SDA symmetry is specified at 40–60 % (catalogue 1703A); the CS43198 requires 45–55 %
  at XTI (DS1156F2 §4.5.1 p. 35). A compliant oscillator can violate the DAC requirement.
- Two XTI pins at their 10 pF maximum (DS1156F2 Table 3-11 p. 19) load the oscillator beyond its
  15 pF rating with the weakest drive the catalogue allows.

Three remedies were compared:

- **(a) An oscillator with a 45–55 % specification.** The best available quartz part, Kyocera
  KC2520K at 1.8 V, is 21 dB noisier than the NSC5083D at 1 kHz (−143 against −164 dBc/Hz), meets
  45–55 % only at its own pin with no margin at XTI, and cannot drive two XTI pins within its
  15 pF rating.
- **(b) A buffer per DAC.** It fixes level and load but not the duty: the best-specified part,
  TI LMK1C1102, guarantees 45–55 % only for a 50 % input (SNAS791D p. 6).
- **(c) An oscillator at twice the frequency divided by two.** A toggling D flip-flop gives an
  output period of exactly two oscillator periods, whatever the oscillator symmetry; the duty
  error is (tPHL − tPLH) / T. The TI SN74AUC1G74 at 1.8 V specifies CLK → Q at 1.0–1.7 ns into
  15 pF (SCES537D p. 4), so the datasheets alone bound the duty at 50 ± 1.7 % (24.576 MHz) and
  50 ± 1.6 % (22.5792 MHz). The NZ2520SDA catalogue tabulates 49.152 MHz itself (−158 dBc/Hz at
  1 kHz, −172 dBc/Hz at 100 kHz, 43 fs), which gives −164 and −178 dBc/Hz after an ideal division.

## Decision

1. **Oscillators:** NDK **NSC5083D-45.158M** (45.1584 MHz, 44.1 kHz family) and
   **NSC5083D-49.152M** (49.152 MHz, 48 kHz family), NZ2520SDA, on MCLK_3V1 (TPS7A2031, 3.1 V,
   unchanged). One runs at a time; both outputs share one net, with a 33 Ω series resistor at each
   oscillator and a 100 kΩ pull-down at the dividers. ST pins as in ADR 0010.
2. **Dividers: one TI SN74AUC1G74DCUR per DAC**, Q̅ to D (divide by two), PRE high, Q through a
   27 Ω series resistor to that DAC's XTI/MCLK. Both clock inputs sit on the oscillator net; both
   CLR inputs on one control line (`MCLK_DIV_RUN`, expander or GPIO, 100 kΩ pull-down, fixed in
   pinout v1). One divider for both DACs is not enough: its weakest output cannot hold the duty
   into two 10 pF pins.
3. **Divider supply: a new rail MCLK_1V8**, TPS7A2018PDBVR from AUDIO_2V2, its EN tied to
   DAC_DIG_1V8. The dividers run only while the DACs' VL is up, so no clock reaches an unpowered
   XTI (feature-block gap G3 for the clock path).
4. **The passive attenuator of ADR 0010 is removed.** The XTI levels come from the 1.8 V divider
   supply.
5. **Layout limits:** oscillators and dividers in one cluster; oscillator-to-divider trace ≤ 10 mm;
   each divider-to-XTI branch ≤ 15 mm (20 mm fails the duty by 0.02 % in the worst corner).
6. **Start sequence (driver):** both ST low and CLR low before the rails come up; release CLR while
   the oscillator net is held low, then raise the ST of the wanted family. Before a family change,
   the DACs move to their internal RCO (DS1156F2 §4.5, p. 36), CLR goes low, ST is swapped, and
   the sequence repeats.
7. **Fallback:** if bench measurements reject the divider, option (a) with the Kyocera KC2520K at
   1.8 V (no level shifting) plus a buffer per DAC is the stocked alternative, at the cost of the
   duty guarantee and about 20 dB of close-in phase noise.

## Consequences

- **Verified by simulation** ([`sim/mclk-divider/`](../../sim/mclk-divider/README.md), 2026-10-24,
  ngspice 47, `odapkit sim run`: 20 checks pass): XTI duty 45.08–54.35 %, XTI 1.737–1.889 V high /
  ≤ 0.023 V low, valley −0.049 V, no re-crossing; oscillator net 13.7 pF ≤ 15 pF; divider input
  within the AUC limits (peak 3.146 V ≤ 3.6 V, pulses ≥ 1.98 ns) for oscillator symmetry 40–60 %,
  the weakest catalogue drive, XTI 1–10 pF and the full tPHL − tPLH spread.
- **Phase-noise budget** (`budget.py`, 24.576 MHz): oscillator ÷ 2 −164.0 / −178.0 dBc/Hz at
  1 kHz / 100 kHz; with the divider estimates (supply term −159.1 dBc/Hz, floor −178.3 dBc/Hz,
  both **UNVERIFIED**: TI publishes no additive jitter for the AUC family) −157.9 / −159.0 dBc/Hz:
  55.9 / 43.0 dB under the CS43198 mask. RMS jitter 73 fs (43 fs oscillator, 32 + 50 fs divider
  estimates) against 46.3 ps the mask allows: 56.0 dB.
- **Power:** two dividers ≈ 8.9 mA at 1.8 V (typical, Cpd 44 pF, SCES537D p. 5), ≈ 20 mW at
  AUDIO_2V2; the attenuator's ≈ 6.5 mW goes. Net ≈ +13 mW in playback (est.). Oscillator current
  at 45.1584 / 49.152 MHz is covered by the same 15 mA maximum.
- **Device tree and mainline:** none. The CS43198 still sees a fixed 22.5792 or 24.576 MHz clock
  (`fixed-clock`, or `gpio-gate-clock` with ST and `MCLK_DIV_RUN`).
- **Open (UNVERIFIED until the first boards):** the AUC1G74 additive phase noise and supply
  sensitivity; the NSC5083D phase noise at 45.1584 MHz and at 3.1 V; the exact 45.1584 MHz value
  on an NDK document (distributor listings show "45.158 MHz"); whether oscillator start-up runts can start the
  two dividers in opposite phase (a constant 20.3 / 22.1 ns left-right offset) and its effect on the
  slave CS43198; the typical XTI capacitance. Measure MCLK phase noise at XTI, the inter-channel
  delay, J-test and THD+N on the first boards.
- **BOM v1 line changes** (applied in BOM v1):
  - **Line 20:** NDK NSC5083D-22.5792M → **NDK NSC5083D-45.158M** (45.1584 MHz, NZ2520SDA, 3.3 V,
    feeds the dividers), Decided (ADR 0019).
  - **Line 21:** NDK NSC5083D-24.576M → **NDK NSC5083D-49.152M** (49.152 MHz), Decided (ADR 0019).
  - **Line 29:** TPS7A2018PDBVR qty 2 → **3**: the third makes MCLK_1V8 (1.8 V, ≈ 9 mA) from
    AUDIO_2V2, EN = DAC_DIG_1V8.
  - **New line (Audio, MCLK dividers):** **TI SN74AUC1G74DCUR**, qty 2, Decided (ADR 0019), driver
    none. Second
    source: none with a comparable datasheet bound; same die in YZPR and RSER packages.
  - **New passives (Audio, MCLK):** 33 Ω ×2 (oscillator outputs), 27 Ω ×2 (divider outputs),
    100 kΩ ×2 (oscillator net pull-down, `MCLK_DIV_RUN` pull-down), 100 nF ×2 (divider VCC),
    MCLK_1V8 LDO input and output capacitors as the other line 29 LDOs.
  - **Removed:** the attenuator passives proposed in §7 item 1 (R1 820 Ω and C1 27 pF at each
    oscillator, RD 47 Ω, 2.0 kΩ and 2.2 pF at each XTI).
  - **§4.3 enable table, MCLK rows:** frequencies 45.1584 / 49.152 MHz; add `MCLK_DIV_RUN` (CLR,
    low = dividers held, pull-down).
  - **§7 item 1:** closed by this ADR (duty and oscillator load); item 19 and **line 112** (HAT
    `I2S_MCLK`): the oscillator net has 1.3 pF left, so the HAT copy needs its own divider or
    buffer and a re-run of `sim/mclk-divider`.
  - **Acceptance criteria for a second-source oscillator** (§4.3 note): symmetry no longer matters;
    the criteria become 45.1584 / 49.152 MHz, CMOS, tri-state, ≤ 15 pF rating met by 13.7 pF,
    phase noise at least as good as the NSC5083D at 49.152 MHz.
- **Power tree:** new rail MCLK_1V8 (TPS7A2018 from AUDIO_2V2, EN = DAC_DIG_1V8, 2× SN74AUC1G74);
  MCLK_3V1 loads become the 2× oscillators without the attenuator.
- The attenuator study stays as the record of why the passive path was abandoned.
