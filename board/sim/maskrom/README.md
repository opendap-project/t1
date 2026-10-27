# MaskROM combo: ngspice simulation

The question: does the hardware MaskROM entry (Main + Volume − held at power-on, BRD-035,
[board ADR 0009](../../docs/adr/0009-bom-v1-decisions.md), BOM v1.5 lines 35, 77, 78, 97, 98)
hold eMMC_D0 low through the RK3566 BootROM's eMMC attempt across tolerances, and leave
normal boots, resume from suspend and HS200 signal integrity alone?

Results are below.

## Files

| File | What it is |
|---|---|
| `maskrom-model.inc` | Behavioural model: PWRON node (RK809 17 kΩ + 100 nF), Vol− node, RK809 power-on (PWRON_ON_TIME, 2 ms slots, RESETB), window supervisor (TPS3839 on vcc_1v8, or TPS3808 on vcca1v8_pmu), Schmitt gates SN74LVC1G57/58 at their worst thresholds, BAT54, DMG1012T switch, eMMC_D0 with its pull-up. |
| `maskrom-cold.cir` | Cold power-on with Main + Vol− (MaskROM request) and with Main only (normal boot), for the BOM design (A) and the proposed one (B), over supervisor-delay and PWRON_ON_TIME corners. |
| `maskrom-resume.cir` | Resume from suspend (vcc_1v8 off in suspend) woken with Main while Vol− is held. |
| `maskrom-levels.cir` | Gate-1 input levels: PWRON pressed through the BAT54 versus temperature and pull-up value; PWRON released versus the RK809 VCC_RTC level. |
| `maskrom-d0-si.cir` | eMMC_D0 at HS200 (200 MHz SDR) with the pull-down tap off: series resistor 100 Ω to 1 kΩ, FET output capacitance 10 and 25 pF. |

Every timing value in `maskrom-model.inc` is a parameter. Values not found in a primary
source (RK809-5 OTP slots, RESETB delay, BootROM timing, VCC_RTC level, Vol− pull-up and
filter, FET output capacitance at low VDS) are **UNVERIFIED**; each is
swept over corners.

## Run

Tools: ngspice 47 or later. No vendor model and no Python are needed: each file prints its
own table.

```sh
ngspice -b maskrom-cold.cir     | grep -E '^(design|0 |1 )'
ngspice -b maskrom-resume.cir   | grep -E '^SUP'
ngspice -b maskrom-levels.cir   | grep -E '^(pressed|released):'
ngspice -b maskrom-d0-si.cir    | grep -E '^(COSS|10p|25p)'
```

Each run takes under a minute.

## Results (2026-10-22, ngspice 47)

**MaskROM entry (BOM lines 35, 78, 97, 98): two holes in the circuit as designed; fix.**

1. **Normal boot is not affected.** With Main only (or Main + Volume +), eMMC_D0 is never forced (simulated, all corners).
2. **Hole 1: the window is too short to be guaranteed.** As designed, D0 is held low until **110–340 ms after RESETB** (TPS3839 td 120–350 ms from vcc_1v8). The BootROM's eMMC attempt has no published timing, and an eMMC may take up to 1 s to initialise after CMD1 (JEDEC limit, **UNVERIFIED** here) before the first D0-dependent step. The BOM's own condition ("the BootROM must sample eMMC_D0 before 120 ms") cannot be shown.
3. **Hole 2: the window reopens at every resume.** vcc_1v8 is off in suspend (power tree §3). The TPS3839 senses it, so each resume reopens the window: waking with Main while Volume − is held (the screenshot / power-menu combination, controls spec §1.3) forces **D0 low for 120–350 ms during resume** (simulated), which can corrupt eMMC traffic.
4. **The D0 tap costs HS200 margin.** With the FET off, 100 Ω plus the FET output capacitance (25 pF assumed at low VDS) removes about **0.18 V of both the high and the low margin** at mid-bit at 200 MHz (est. interconnect). 1 kΩ costs ≤ 0.04 V and still holds D0 at ≤ 0.32 V against a 4.7 kΩ pull-up (VIL 0.63 V).
5. **Levels hold, with thin margin at cold.** The pressed PWRON_N level through the BAT54 is 307 mV at −20 °C with the 20 kΩ pull-up, against the 350 mV VT− minimum (43 mV margin); 100 kΩ gives 261 mV (89 mV). The PWRON idle-voltage concern of BOM line 78 is closed: In2 stays above VT+ max for any VCC_RTC ≥ 0.6 V, below the RK809's own 1.26 V VIH.
6. **Fix:** window supervisor **TPS3839G18 on vcc_1v8 → TPS3808G01 on vcca1v8_pmu** (SENSE divider 280 kΩ / 100 kΩ, 1.54 V; **CT 390 nF** → td 1.21–3.43 s; RESET pull-up 100 kΩ); PWRON_N pull-up **20 kΩ → 100 kΩ**; D0 series resistor **100 Ω → 1 kΩ** at the D0 trace; optional 100 kΩ gate pull-down on the DMG1012T. Simulated: D0 held 1.20–3.42 s after RESETB, nothing at resume, normal boot untouched.

---
