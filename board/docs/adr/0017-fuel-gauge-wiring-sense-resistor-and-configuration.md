# ADR 0017: Fuel gauge wiring, sense resistor and production configuration

- **Status:** Accepted
- **Date:** 2026-10-24

## Context

[ADR 0014](0014-two-cell-battery.md) made the TI BQ28Z610-R1 the gauge of the 2S pack, used as a gauge only: the pack's PCM protects and balances, so the gauge's CHG and DSG drives are unused. BOM v1 §7 item 22 left three items open after TI's technical reference (SLUUC81) was read:

- (a) PACK tied to BAT+ with no FETs: the gauge never shuts down above 3.0 V;
- (b) the 5 mΩ sense resistor is outside the datasheet's 1–3 mΩ;
- (c) three data-flash defaults differ between SLUUC81 §13 and its Table 14-1.

Sources: TI SLUSE07B (BQ28Z610-R1 datasheet, January 2022), TI SLUUC81 (technical reference, January 2020), TI SLUSDV2C (BQ25798), TI SLPS489A (CSD17575Q3), Vishay document 30100 (WSL, 23-Nov-2023). All are in the [parts-lib manifest](https://github.com/opendap-project/libs/blob/main/parts/manifest.toml) and were read from the local cache with matching sha256.

## Research

### 1. Shutdown, storage drain and wiring

**When the gauge shuts down.** SLUUC81 gives two paths, and both need the PACK pin low:

- voltage-based shutdown (§5.4.1, p. 27): the lowest cell below Shutdown Voltage (2300 mV) for Shutdown Time (10 s) **and** PACK below Charger Present Threshold (3000 mV) and Current() ≤ 0;
- commanded shutdown (MAC 0x0010, §12.2.10, p. 68; sent twice when sealed): once armed (OperationStatus()[SDM] = 1), the gauge trips when Current() = 0 **and** PACK < Charger Present Threshold. "Once SHUTDOWN mode is enabled, it is not possible to clear it without entering SHUTDOWN mode." It wakes, with a full reset, when PACK rises above VSHUTDOWN+ (2.05–2.45 V, SLUSE07B §7.3, p. 4).

With PACK on BAT+ (BOM v1.7 line 42), PACK equals the stack voltage (≥ 5 V for a 2S pack above its PCM cut-off), so neither condition is ever met: the gauge stays in SLEEP or NORMAL until the pack PCM opens.

**What that costs** (SLUSE07B §7.5–7.6, p. 5; typical at 25 °C and 7.2 V, no maximum given for SLEEP):

| Gauge mode | Current | Note |
|---|---|---|
| NORMAL | 250 µA typ | |
| SLEEP | 100 µA typ | |
| SHUTDOWN | 0.5 µA typ, 2 µA max | |
| PACK pull-down RPACK(PD) | 30 / 40 / 50 kΩ | 185 µA at 7.4 V, 280 µA at 8.4 V and 30 kΩ, if it is connected permanently: SLUSE07B does not say whether it is (**UNVERIFIED**) |

**Does the ship FET isolate the gauge?** No. The BQ25798 ship FET (CSD17575Q3, BOM line 120) sits between the pack and the charger's BAT pin; BATP senses the pack side through 100 Ω (SLUSDV2C §7.3.12, pp. 49–50). The gauge cannot move to the switched side: VC1 is wired to the mid-cell tap, and VC2 must stay above VC1 − 0.3 V (SLUSE07B §7.1, p. 4), which a collapsed VC2 with a live VC1 would violate. VC2, PBI, VC1 and the sense resistor therefore stay on the pack side, and the gauge drains the pack whatever the ship FET does.

**Storage target, derived.** Pack capacity basis: 1,000 mAh, the lowest 2S capacity that meets T1-012 (the made-to-order pack will be larger, which only helps). A stored T1 shall keep at least half of a 30 % charge (a common shipping charge level, **UNVERIFIED** as a requirement) after 12 months from the board's drain alone, leaving the other half for the cells' own self-discharge and the PCM, which the board does not control:

- hard limit: 0.5 × 0.30 × 1,000 mAh / 8,760 h = 17 µA → **≤ 15 µA**;
- target: **≤ 5 µA** (3.6 mAh a month, 0.36 % of 1,000 mAh);
- ideal: ≤ 2 µA.

The same figures cover a T1 that powers off at critical battery: at 5 % (50 mAh), 100 µA empties the pack into its PCM cut-off in about 21 days; 5 µA takes about 14 months.

**Drain of each wiring in storage** (no adapter; µA, typ / max):

| Wiring | Gauge | Charger (BATP) | Ship FET IDSS | PACK pin | Total | Verdict |
|---|---|---|---|---|---|---|
| A. PACK on BAT+ (BOM v1.7), charger ship mode | 100 / — (SLEEP) | 11 / 16 | — | 0–280 (pull-down) | **≥ 111 / ≥ 116** | Fails the hard limit 7×: 30 % of 1,000 mAh lasts ≈ 3.7 months |
| B. PACK on the switched side, gauge SHUTDOWN, charger **shutdown mode** | 0.5 / 2 | 0.5 / 0.7 | — / 1 (24 V, 25 °C) | — / 1 (leakage, PACK at 0 V) | **≈ 1 / 4.7** | Meets the 5 µA target |
| C. As B, charger **ship mode** | 0.5 / 2 | 11 / 16 | — / 1 | — / 1 | ≈ 12 / 20 | Within the hard limit typically, above it at maximum |

Charger figures: SLUSDV2C §6.5 (IQ_BAT_OFF 11 / 16 µA in ship mode, ISD_BAT 0.5 / 0.7 µA in shutdown mode, VBAT 8 V). Ship FET: SLPS489A p. 2. PACK leakage: SLUSE07B §7.6, p. 5. With PACK at 0 V the pull-down draws nothing, whether or not it is permanent.

**Reference circuits.** No TI document shows the BQ28Z610-R1 without FETs. TI's own circuits put PACK on the system side of the switch that disconnects the cells (SLUSE07B p. 1 simplified schematic, "Pack side / System side"; Figure 9-1, p. 23), and TI's BQ25798EVM puts the ship FET between the battery and BAT (SLUUCB5E, Q5). With the protection FETs in the pack, the ship FET is the board's only switch between cells and system, so it takes the place of TI's DSG FET for the PACK sense. TI's E2E forum was not reachable on 2026-10-24 (HTTP 403).

**Alternatives** (only a failure of this wiring would justify a change):

| Part | Cells, function | Linux (torvalds master, 2026-10-24) | Fit |
|---|---|---|---|
| BQ28Z610-R1 (kept) | 1–2S gauge, per-cell voltages, FET drive unused | `bq27xxx_battery`, `ti,bq28z610` | Meets the storage target with wiring B |
| TI BQ27Z746, BQ27Z561 | 1S | — | Excluded: 1S |
| TI BQ40Z50-R2 | 1–4S gauge and protection, FET drive | `sbs-battery` | Same PACK behaviour, nothing gained gauge-only; datasheet not read |
| TI BQ34Z100-R2 | Multi-cell gauge only, stack voltage through a divider | `bq27xxx_battery`, `ti,bq34z100` | Loses per-cell voltage, so pack imbalance cannot be seen; datasheet not read |
| ADI MAX17205 | 2S/3S gauge with balancing | `max1720x_battery` (since July 2024) | 25 µA active, 12 µA hibernate (ADI product summary); shutdown current not read (**UNVERIFIED**) |
| ADI MAX17320 | 2–4S gauge with protector, FET drive | No driver in `drivers/power/supply` | Excluded: no mainline driver |

### 2. Sense resistor

Figures for the BQ28Z610-R1 coulomb counter (SLUSE07B §7.11, p. 7): ±100 mV input, 16-bit (≈ 3.05 µV per LSB), offset ±2.6 LSB maximum after calibration, gain drift ≤ 9.8 LSB/°C (15-bit + sign). Datasheet range: 1–3 mΩ in the body (§8.4.2.3 p. 22, §11.1 p. 27, Figure 9-1 p. 23), TCR ≤ 50 ppm/°C guidance (§11.1). WSL1206 component TCR (Vishay 30100, p. 2): ±150 ppm/°C at 3–4.9 mΩ, ±275 ppm/°C at 1–2.9 mΩ, ±110 ppm/°C at 5–6.9 mΩ.

| | 5 mΩ (BOM v1.7) | **3 mΩ** | 2 mΩ |
|---|---|---|---|
| Inside TI's 1–3 mΩ | No | Yes | Yes |
| Full scale (±100 mV) | ±20 A | ±33 A | ±50 A |
| 3.2 A worst continuous: signal, power (of 0.25 W) | 16 mV, 51 mW (20 %) | 9.6 mV, 31 mW (12 %) | 6.4 mV, 20 mW (8 %) |
| 5 A fuse rating: power | 125 mW (50 %) | 75 mW (30 %) | 50 mW (20 %) |
| 10 A for ≤ 1 s (BQ25798 discharge pulse) | 0.5 W pulse | 0.3 W pulse | 0.2 W pulse |
| Max offset as current | 1.6 mA | 2.6 mA | 4.0 mA |
| Offset against the lightest playback load (≈ 0.11 A from VSYS, power tree §3, est.) | 1.4 % | 2.4 % | 3.6 % |
| Component TCR (WSL1206) | ±110 ppm/°C | ±150 ppm/°C | ±275 ppm/°C |
| Sleep entry (Sleep Current 10 mA) | 50 µV, 16 LSB | 30 µV, 10 LSB | 20 µV, 7 LSB |
| AOLD default (setting 4, −19.42 mV, RSNS = 0) | 3.9 A | 6.5 A | 9.7 A |

3 mΩ is the largest value TI supports: the best resolution and offset inside the specified range, a lower TCR than 2 mΩ, and dissipation that 2 mΩ would not improve in any way that matters (31 mW at 3.2 A). It also moves the AOLD detector to 6.5 A, above the 5 A fuse, so load peaks can no longer set AOLD and block SLEEP (SLUUC81 §5.3.1, p. 26). None of the 1206 WSL values meets the 50 ppm/°C guidance; over a 25 K board temperature swing ±150 ppm/°C is ±0.38 % of gain, below the counter's own uncalibrated gain error (±492 LSB of 32,768, 1.5 %), and the gain is calibrated per board.

**Part:** Vishay WSL12063L000FEA (3 mΩ ±1 %, 1206, 0.25 W), same family, package and pad table (30100 p. 2, 0.002–0.0059 Ω row) as the current part, so the footprint does not change. Multiple authorized sources (2026-10-24).

### 3. Conflicting TRM defaults

| Field (address) | SLUUC81 §13 | SLUUC81 Table 14-1 | What differs |
|---|---|---|---|
| Settings:Protection:Enabled Protections C (0x46B1) | 0x3C (p. 93) | 0x14 (p. 114) | Bits 3 and 5, both reserved; PTO (bit 2) and CTO (bit 4) set in both |
| Settings:AFE:AFE Protection Control (0x469D) | 0x00 (p. 94) | 0x70 (p. 114) | RSTRIM (bits 7–4); the p. 94 text itself says to leave RSTRIM at 0x7, which matches 0x70 |
| Settings:Configuration:IT Gauging Configuration (0x464D) | 0xD4DE (p. 92) | 0x14CE (p. 114) | Bits 4, 14 and 15, all reserved; the functional bits (1, 2, 3, 6, 7, 10, 12) are the same |

Only RSTRIM is a functional difference, and it is a trim TI says not to change.

## Decision

1. **The BQ28Z610-R1 stays.** Wired as item 2, it meets the storage target; no alternative is better for a gauge-only 2S design with a mainline driver.
2. **Wiring.**
   - VC2 and PBI on the pack side of the ship FET, after the 5 A fuse; VC1 to the mid-cell tap; both through the SLUSE07B Figure 9-1 RC filters. PBI 2.2 µF.
   - Sense resistor low side in the P− return, as before; gauge VSS on the cell side.
   - **PACK on the switched side of the ship FET** (the BQ25798 BAT node), not on BAT+. When the ship FET opens, PACK falls below 3.0 V and the gauge can shut down; when it closes, PACK rises and the gauge wakes. The PACK input network follows Figure 9-1.
   - Only the gauge (VC1, VC2, PBI, SRP/SRN), the charger's BATP sense and the ship FET connect on the pack side of the ship FET.
   - CHG and DSG stay open.
3. **Storage and critical-battery power-off.** Blackbird OS, with no adapter present: sends MAC 0x0010 twice to the gauge, then writes the BQ25798 SDRV_CTRL = 01 (**shutdown mode**, wake by plugging an adapter). Board drain: ≈ 1 µA typical, 4.7 µA maximum. Ship mode (SDRV_CTRL = 10, wake on QON) costs up to 20 µA and is not used for storage. The factory ships the T1 in shutdown mode, and a power-off at critical battery uses the same sequence. If the charger write fails, the armed gauge shuts down at the next ship-FET opening (a QON system reset) and wakes when it closes: a gauge reset, no harm.
4. **Sense resistor: 3 mΩ, Vishay WSL12063L000FEA.** CC Gain and Capacity Gain calibrated per board at 1–2 A (SLUUC81 §11.4.3, pp. 54–56).
5. **Production configuration** (golden image, in addition to the parts-lib table): the three conflicting fields are set explicitly. The production tool reads each one, checks that it equals one of TI's two documented defaults (otherwise it stops), writes the value below, reads it back and logs it:
   - Enabled Protections C: the read value with PTO and CTO cleared (0x14 → 0x00, 0x3C → 0x28); reserved bits as read.
   - AFE Protection Control: RSNS = 0, SCDDx2 = 0; RSTRIM as read (expected 0x7, giving 0x70).
   - IT Gauging Configuration: functional bits 0x14CE (TI defaults kept); reserved bits 4, 14, 15 as read.

   Also set explicitly: DA Configuration 0x19 (2S, SLEEP, IN_SYSTEM_SLEEP: I2C1 stays pulled up while the T1 runs, which otherwise keeps the gauge awake, SLUUC81 §5.3.1–5.3.2, p. 26); Power Configuration 0x00 (AUTO_SHIP_EN off: the shutdown in item 3 is commanded); Charger Present Threshold 3000 mV; Shutdown Voltage 2300 mV and Shutdown Time 10 s; Ship FET Off Time 10 s and Delay 20 s; Sleep Current 10 mA; Bus Timeout 5 s; AOLD Threshold 0xF4 (6.5 A at 3 mΩ) (SLUUC81 Table 14-1, p. 118; Table A-1, p. 123).
6. **Checked on the first M-PWR module:** storage drain at the pack ≤ 5 µA; the gauge enters SHUTDOWN after the sequence of item 3 and wakes on adapter plug-in; whether RPACK(PD) is permanently connected; the three read-back values, recorded in the parts-lib sheet.

## Consequences

Changes to BOM v1 and power tree v0:

- **BOM line 42:** PACK to the BQ25798 BAT node (switched side of the line 120 ship FET), not to BAT+ after the fuse; VC2 and PBI stay on the pack side. Replace the "gauge never enters SHUTDOWN above 3.0 V" note with item 3 of this decision. Golden-image notes: item 5.
- **BOM line 43:** WSL12065L000FEA (5 mΩ) → **Vishay WSL12063L000FEA (3 mΩ ±1 %, 1206, 0.25 W)**; alternate WSL12063L000FEA18. Same footprint. 3.2 A → 9.6 mV, 31 mW (12 %); 5 A → 75 mW (30 %); ±33 A full scale; component TCR ±150 ppm/°C (**above** TI's 50 ppm/°C guidance, accepted: §2).
- **BOM line 120:** the ship FET also switches the gauge's PACK sense; storage uses the charger shutdown mode, not ship mode.
- **BOM §7 item 22:** (a), (b) and (c) closed by this ADR; (d) CC Gain calibration and the golden image per pack stay open, with the bring-up checks of item 6. BOM §8 item 20 unchanged.
- **BOM figures elsewhere** that quote 5 mΩ: the passives table ("gauge 5 mΩ") and the path resistance.
- **Power tree §4.7:** the 5 mΩ sense term becomes 3 mΩ (51 → 31 mW at 3.2 A; path resistance about 2 mΩ lower). Add a storage line: board drain in storage ≈ 1 µA typical, 4.7 µA maximum (gauge SHUTDOWN + BQ25798 shutdown mode + ship FET + PACK leakage), target ≤ 5 µA, hard limit 15 µA. The VSYS row's "BATFET ship mode" becomes "ship FET, charger shutdown mode for storage".
- **Power tree, off state:** with the T1 off but not in storage (charger idle, ship FET on), the gauge draws about 100 µA in SLEEP (≈ 0.74 mW at 7.4 V), plus RPACK(PD) if it is permanent.
- **Blackbird OS:** the storage and critical-battery power-off sequence of item 3 (gauge MAC 0x0010 twice, then BQ25798 SDRV_CTRL = 01), checked by Blackbird OS before writing (no adapter present). The mainline `bq27xxx` driver does not send it; it is a power-off hook, not a driver change.
- **Parts-lib:** the BQ28Z610-R1 sheet takes the wiring, the shutdown sequence and the explicit configuration; a WSL12063L000FEA sheet and its manifest entry are added.
