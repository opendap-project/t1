# ADR 0021: vdd_cpu buck: TI TPS62869 instead of the Rockchip RK860-0

- **Status:** Accepted
- **Date:** 2026-10-25

## Context

BOM v1 line 3 supplies the RK3566 CPU cluster (vdd_cpu) from a Rockchip RK860-0, the part on the Radxa ZERO 3W, with a Murata DFE252012F-R47M (line 4). The RK860-0 has no public datasheet: its input range, current rating, the 0x40 address, the OTP boot voltage, its land pattern and whether it senses remotely are all **UNVERIFIED** in the BOM, the power tree (§4.10 lists its margin as "Open: datasheet from Rockchip") and the [parts-lib sheet](https://github.com/opendap-project/parts-lib/blob/main/Rockchip/RK860-0.md). No franchised distributor lists it. That fails T1-010 and T1-027 to T1-029, the authorised-channel rule of ADR 0013 and the supply rule of ADR 0010, the BRD-049 margins cannot be shown, and a DIY builder can neither check nor replace the part. Its mainline driver is `fan53555` (`rockchip,rk8600`).

## Research

### 1. What the RK3566 asks of vdd_cpu

- **Range and step.** RK3566 DS 1.1 gives VDD_CPU 0.81 V min, 0.9 V typ, no maximum (DVS) (p. 52, Table 3-2), and 1.2 V absolute maximum (p. 51, Table 3-1). The mainline CPU operating points (`arch/arm64/boot/dts/rockchip/rk3566.dtsi`, torvalds/linux master, read 2026-10-25) are 408–816 MHz at 850 mV, 1104 MHz at 900 mV, 1416 MHz at 1025 mV, 1608 MHz at 1100 mV and 1800 MHz at 1150 mV, each with a 1150 mV ceiling. Every value is a multiple of 5 mV and of 12.5 mV.
- **Topology.** "The power supply uses an external DCDC power supply independently and supports dynamic frequency and voltage regulation" (HDG 1.1, p. 36, §2.2.2.3). Both Rockchip power trees put VDD_CPU on an external DC/DC, not on the PMIC: RK809-5 (p. 49, Fig. 2-34, fed from VCC5V0_SYS) and RK817-5 (p. 44, Fig. 2-30, fed from VCC_SYS).
- **Current and transient.** Rockchip gives no figure: the HDG points to the *RK356X Power Consumption Test Report* (pp. 36, 41), which is not public. **UNVERIFIED.** What the reference boards size for: the RK860-0 (no rating published), the Silergy SYR827 at 6 A continuous (AN_SYR827/SYR828 Rev. 0.1, p. 1), the onsemi FAN53555 at 5 A (FAN53555CN/D Rev. 9, p. 2, Table 1), and the Tcsemi TCS4525 (no datasheet found). The T1 design maximum stays at 3 A (power tree v0 §3, est.).
- **Decoupling and ripple.** 2 × 4.7 µF 0402 and 22 µF 0603 at the SoC, 2 × 22 µF 0603 at the converter; large capacitors on the back under the SoC to keep ripple below 60 mV (HDG 1.1, p. 36, Fig. 2-19).
- **Remote feedback.** A separate feedback line from under the SoC to the converter's FB, with 100 Ω and 1 µF on the converter side so an open line still regulates (HDG 1.1, p. 38, §2.2.2.6). The ZERO 3W v1.12 (RK860-0, sheet 22) and the ROCK 3C v1.4 (TCS4525) fit 100 Ω and 100 nF; the ROCK 3C also has a 10 mΩ 1 % resistor in the vdd_cpu path, inside the sense loop.
- **Sequence.** VDDA0V9_PMU / VDDA_0V9 / VDD_LOGIC → VCCA1V8_PMU / VCC_1V8 / VCC3V3_PMU / VDD_GPU → VDD_CPU → VCC_DDR → VCC_3V3 → RESETn, RESETn released at least 10 ms after the last supply (HDG 1.1, p. 34). The ZERO 3W enables its RK860-0 from VCC3V3_PMU through 51 kΩ with 100 nF to ground, and drives VSEL from PMIC_SLEEP_H (sheet 22).
- **Placement and height.** The converter sits on the back, in the zone under the battery pocket: 1.5 mm with can (PCB-Z-01).

### 2. Candidates

"Debian" is `debian/config/arm64/config` on branch `debian/latest`: Blackbird OS runs the Debian `linux-image-arm64` kernel unmodified.

| Part | Driver (mainline / Debian arm64) | Primary document | VIN | IOUT | VOUT range, step | Boot voltage | Package, height | Authorized channel (2026-10-25) | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| Rockchip RK860-0 | `fan53555` (`rockchip,rk8600`) / `REGULATOR_FAN53555=m` | None public | **UNVERIFIED** | **UNVERIFIED** | 0.7125 V + 12.5 mV (driver) | OTP, **UNVERIFIED** | **UNVERIFIED** | No (one non-franchised source) | Rejected (the problem) |
| Silergy SYR827PKC / SYR828PKC | `fan53555` (`silergy,syr827`, `silergy,syr828`) / `=m` | AN_SYR827/SYR828 Rev. 0.1, marked "Confidential", LCSC mirror; no Silergy-hosted datasheet | 2.6–5.5 V (p. 3) | 6 A (p. 1) | 0.7125–1.5 V (p. 1), 12.5 mV (driver) | Not stated | CSP 1.56 × 1.96, 20 bumps (p. 1) | No | Rejected: no franchised channel, no released datasheet |
| Tcsemi TCS4525 / TCS4526 | `fan53555` (`tcs,tcs4525`, `tcs,tcs4526`) / `=m` | None found | — | — | 0.6 V + 6.25 mV (driver) | — | — | No | Rejected: no datasheet, no channel |
| onsemi FAN53555 (options) | `fan53555` (`fcs,fan53555`) / `=m` | FAN53555CN/D Rev. 9, April 2025 (Chinese edition; onsemi.com refused the English file) | — | 5 A (most options; 3–4 A for some) (p. 2) | 0.6–1.23 V / 10 mV, or 0.603–1.411 V / 12.826 mV, per option (p. 2) | 0.85–1.225 V per option; 0.90 V with VSEL1 off on UC01X / UC05X / BUC05X (p. 2) | WLCSP-20 2.015 × 1.615 × 0.586 mm, 0.4 mm pitch (p. 26) | Yes, multiple; some options obsolete | Second source (different land) |
| onsemi FAN53526 | `fan53555` (`fcs,fan53526`) / `=m` | FAN53526 Rev. 3.1 | — | 3.0 A (p. 2) | — | — | WLCSP-15 1.310 × 2.015 mm, 0.4 mm pitch (p. 2) | Yes; several options obsolete | Rejected: 3 A = no margin over the 3 A estimate |
| TI TPS62360 / TPS62361B / 62 / 63 | `tps62360` / **not set** | SLVSAU9C, Nov 2012 | 2.5–5.5 V | 3 A peak | 0.77–1.4 V or 0.5–1.77 V, 10 mV (p. 1) | — | DSBGA-16 2 × 2 mm | No authorized stock | Rejected: 3 A peak, not in Debian, no stock, 2011 generation |
| TI TPS6287x (TPS62870, 6 A) | `tps6287x` / **not set** | SLVSGC5E, Oct 2025 | 2.7–6 V | 6–15 A | 0.4–1.675 V / 5 mV and three other ranges (p. 1) | Pin-selected: TPS62870Z4 0.85 / 0.75 / 0.875 / 1.0 V (p. 5) | VQFN-FCRLF-16 2.55 × 3.55 mm, 1.05 mm max (p. 64) | Yes | Runner-up: true differential remote sense, but not in the Debian kernel, 1.75 mA operating IQ (p. 9), compensation network |
| **TI TPS62869** (TPS6286910C) | `tps6286x` (`ti,tps62869`) / **`REGULATOR_TPS6286X=m`** | SLVSFS3B, Jul 2021 | 2.4–5.5 V (p. 5) | 6 A (p. 5) | 0.4–1.675 V, 5 mV (p. 20) | 0.9 V factory-set, 0x42 (p. 15, Table 8-3) | VQFN-HR-9 1.5 × 2.5 mm, 1.0 mm max (p. 38) | Yes (C option; A option on order) | **Chosen** |
| MPS MP8869 / MP8867 | `mp886x` (`mps,mp8869`, `mps,mp8867`) / **not set** | Datasheet not retrieved (MPS page failed to load) | — | — | 0.6 V + 10 mV (driver) | — | — | None found | Rejected: not in Debian, no channel found |
| Richtek parts with a mainline I2C DVS driver (RT5739 / RT5733, `rt5739`) | `rt5739` / not set | Not retrieved | — | — | — | — | — | None found | Rejected: not in Debian, no channel found |

Mainline RK3566 boards (21 device-tree files read, torvalds/linux master, 2026-10-25; vdd_cpu defined in 18): TCS4525 on 12 (ROCK 3C, Quartz64-A, PineTab2, ODROID-M1S, PineNote, Radxa CM3, SOQuartz, NanoPi R3S, BTT CB2, ROC-PC, LubanCat-1, LCKFB TSPI), RK860-0 on the Radxa ZERO 3 family, SYR827 on the Orange Pi 3B and Tinker Board 3, `fcs,fan53555` on the Anbernic RGxx3 family, a PWM regulator on two boxes. None puts vdd_cpu on an RK8xx PMIC buck.

### 3. Options without a dedicated converter

- **An RK809-5 buck.** BUCK1 and BUCK2 are rated 2.5 A, BUCK3 and BUCK4 1.5 A, and BUCK5 starts at 1.5 V (RK809 DS Rev. 1.01, p. 17; p. 22–23 table). The T1 already uses BUCK1–BUCK4 for vdd_logic, vdd_gpu, vcc_ddr and vdd_npu as Rockchip's RK809-5 tree does (HDG p. 49), and BUCK5 for vcc_1v8. Freeing BUCK2 would put GPU and NPU on BUCK4 (1.5 A) as only the RK817-5 tree does, and 2.5 A sits under the 3 A estimate with no margin. Rockchip, the reference boards and mainline all use an external converter. The RK809 itself has the same supply problem as the RK860-0, outside this ADR. Rejected.
- **A fixed regulator.** vdd_cpu would have to sit at 1.15 V for 1.8 GHz, 50 mV under the 1.2 V absolute maximum, and the 408–816 MHz points would run at (1.15 / 0.85)² ≈ 1.83 times their dynamic power. The listener's battery pays for it in every screen-off hour. Rejected.

### 4. Why the TPS62869, and why the C option

- **Every gate passes.** Public, complete English datasheet with land pattern (SLVSFS3B); mainline driver since 2022 and built as a module in the Debian arm64 kernel the OS runs, so no out-of-tree module (OS-023 would allow one, at a maintenance cost); 3.8 V VSYS_LV inside 2.4–5.5 V; 6 A rating; 0.9 V boot without software; 1.0 mm maximum height; sold by the maker and by franchised distributors.
- **Against the FAN53555.** It shares the reference boards' driver and has more sources, but it is a 2010 design in a 0.4 mm-pitch WLCSP that can only be inspected by X-ray and that a DIY builder cannot replace by hand; the English datasheet could not be retrieved and several options are obsolete. It stays the second source on its own land.
- **Against the TPS6287x.** Its differential remote sense is the closest match to HDG p. 38, but the driver is not in the Debian kernel and it draws 1.75 mA (typ) whenever enabled, ≈ 6.7 mW from VSYS_LV, against 4 µA for the TPS62869 (SLVSFS3B p. 7). It is the fallback if the TPS62869's single-ended sense fails the transient check below.
- **C option (TPS6286910CRQYR) over the A option (TPS628691ARQYR).** The C option is factory-set to 0.9 V at 0x42 and has a power-good pin; the A option reads a resistor at start-up (86.6 kΩ: 0.90 V, 0x41) and has a VID pin. Today only the C option is available from distributors (2026-10-25). SLVSFS3B does not say which VOUT register the C option regulates from: the A option uses Register 1 with VID low (p. 16, §8.4.4; SLUUCH3 p. 2), and the mainline driver writes Register 1. The board takes both options on one land, so the A option is the fallback with no layout change.

## Decision

1. **vdd_cpu converter: TI TPS6286910CRQYR** (TPS62869, 6 A, VQFN-HR-9), on I2C0 (PMUIO2, 1.8 V; VIH 0.84 V, SLVSFS3B p. 7) at **0x42**, VIN from VSYS_LV 3.8 V, on the back next to the SoC. Same-land alternate: **TPS628691ARQYR** with an 86.6 kΩ 1 % resistor from pin 9 to AGND (0.90 V, 0x41). Second source on another land: onsemi FAN53555BUC18X (`fan53555`).
2. **Inductor: Coilcraft XGL4012-221MEC**, 0.22 µH ± 20 %, DCR 5.0 / 6.0 mΩ, Isat 6.1 / 9.9 / 14.4 A at 10 / 20 / 30 % drop, Irms 10.9 A (20 °C rise), 4.0 × 4.0 × 1.2 mm max (Coilcraft Document 1718, revised 2026-08-27, pp. 1, 3). 0.22 µH is the TPS628691x nominal (SLVSFS3B p. 5). The DFE252012F-R47M (0.47 µH) leaves line 4; its five RK809 pieces on line 5 stay.
3. **Capacitors.** Input 2 × 10 µF 10 V X7R 0603 + 100 nF at VIN–PGND (TI: 8 µF effective, p. 23; the X7R bias derating at 3.8 V must leave ≥ 8 µF, to check on the chosen capacitor). Output: Rockchip's set (HDG Fig. 2-19): 2 × 22 µF 6.3 V 0603 at the converter, 22 µF 0603 + 2 × 4.7 µF 0402 under the SoC, 75.4 µF nominal. TI proves 3 × 22 µF and 150 µF with 0.24 µH (p. 23, Table 9-3) and asks for ≥ 30 µF effective (p. 24); 75.4 µF lies between two proven cells and is to be confirmed with WEBENCH and the load step below.
4. **Sense.** VOS takes a dedicated sense trace from the 22 µF at the SoC (load side of the `blk.vdd-cpu` measurement link), kept away from SW (p. 31), with 100 Ω from VOS to the converter-side output and 100 nF from VOS to AGND, as the ZERO 3W and ROCK 3C fit for HDG p. 38. A 0 Ω footprint across the 100 Ω (not fitted) returns to TI's local sense if the remote sense fails the load-step check.
5. **Enable and sequence.** EN from vcc3v3_pmu through 51 kΩ with 100 nF to AGND (ZERO 3W). vdd_cpu then follows VCC3V3_PMU, as HDG p. 34 orders, within about 1.5 ms (RC to the 0.84 V threshold) + tDelay + tRamp (0.85–1.5 ms) of it. EN stays high while the system runs: EN low resets every register (p. 14).
6. **Pin 9.** C option: PG, 100 kΩ pull-up to vcca1v8_pmu and a test pad, **monitor only**. PG falls during a DVS step down of more than 9 % (VOS above 111 % of the new target until the ramp ends), so it never drives nPOR or any reset. A option: the 86.6 kΩ to AGND, pull-up not fitted.
7. **Device tree** (`ti,tps62864.yaml`):

   ```dts
   &i2c0 {
       regulator@42 {
           compatible = "ti,tps62869";
           reg = <0x42>;
           regulators {
               vdd_cpu: SW {
                   regulator-name = "vdd_cpu";
                   regulator-min-microvolt = <850000>;
                   regulator-max-microvolt = <1150000>;
                   regulator-always-on;
                   regulator-boot-on;
                   regulator-initial-mode = <TPS62864_MODE_NORMAL>;
               };
           };
       };
   };
   ```

   `cpu-supply = <&vdd_cpu>` on cpu0–cpu3 as in every RK3566 board. The driver has a fixed 1 mV/µs ramp (the register default, so a 300 mV step takes 300 µs) and no suspend operations: vdd_cpu stays on in suspend, unlike the references that switch it off through VSEL. The A option uses `reg = <0x41>`.
8. **Feature-block record `blk.vdd-cpu`** (feature blocks #13): Bound by BRD-010, BRD-049 (must). Interface: I2C0 0x42, VSYS_LV in, vdd_cpu out, EN from vcc3v3_pmu, PG to a test pad, VOS sense from the SoC. Power domain: EN from vcc3v3_pmu; on in suspend. Measure: the H5 link (line 137) inside the VOS sense loop. Holds: TPS628691ARQYR on the same land (pin 9 resistor). Alternates: `tps628691a`. Software: `ti,tps62869` (`tps6286x`, `CONFIG_REGULATOR_TPS6286X=m`). Level: unchanged.

## Consequences

### Margins (BRD-049)

| Item | Rating | Load | Use | Result |
|---|---|---|---|---|
| Converter output current | 6 A (SLVSFS3B p. 5) | 3 A (est.) | 50 % | OK; 4.8 A before the 80 % rule bites |
| Input voltage | 5.5 V recommended, 6 V absolute (pp. 5) | VSYS_LV 3.8 V | 69 % / 63 % | OK |
| Inductor peak vs high-side limit | 7 / 7.7 / 8.5 A (p. 7) | 3.76 A (3 A + ΔIL / 2, ΔIL = 1.52 A at 1.15 V, 3.8 V, 0.22 µH, 2.4 MHz) | 54 % of the minimum limit | OK |
| Inductor saturation vs worst-case limiter trip | 9.9 A at 20 % drop, 14.4 A at 30 % | 8.5 A | 86 % / 59 % | OK (≤ 100 %) |
| Inductor heating | Irms 10.9 A (20 °C rise) | 3 A | 28 % | OK |
| Output against the SoC limits | 0.81 V min, 1.2 V abs. max (DS 1.1 pp. 51–52) | 0.85–1.15 V ± 2 % (p. 7) | 0.833–1.173 V | OK; local-sense fallback with the 15 mV link drop: 0.818 V at 850 mV, still ≥ 0.81 V |
| Thermal | RθJA 60.3 °C/W (EVM, p. 5) | ≈ 0.3 W at 3 A (est.: 0.10 W conduction from p. 7 RDS(on), the rest not tabulated) | ≈ +18 °C (est.) | Check on the board |

### Exact changes for the BOM, power tree, pinout and feature-blocks owners

This ADR does not edit those files. To apply:

- **BOM v1 line 3:** part → "TI TPS6286910CRQYR (6 A, VQFN-HR-9 1.5 × 2.5 × 1.0 mm)", qty 1, status Decided (ADR 0021); driver → mainline + Debian (`tps6286x`, `ti,tps62869`, `REGULATOR_TPS6286X=m`); alternates → TPS628691ARQYR (same land, 86.6 kΩ pin 9 resistor, 0x41), onsemi FAN53555BUC18X (other land, `fan53555`); notes → I2C0 0x42, 0.9 V boot, VSYS_LV in, EN from vcc3v3_pmu through 51 kΩ + 100 nF, PG test pad only, stays on in suspend.
- **BOM v1 line 4:** Murata DFE252012F-R47M → Coilcraft XGL4012-221MEC, qty 1; no same-land second source found yet (the DFE201612E-R24M that TI lists saturates at 6.6 A, under the 8.5 A worst-case limit).
- **BOM, new passives (line 3 group):** 2 × 10 µF 10 V X7R 0603 + 100 nF (input); 2 × 22 µF 6.3 V 0603 (converter-side output); 100 Ω and 100 nF (VOS sense) and a 0 Ω DNP across the 100 Ω; 51 kΩ + 100 nF (EN); 100 kΩ pull-up (PG, C option) and an 86.6 kΩ 1 % DNP (pin 9 to AGND, A option); two test pads (PG, VOS).
- **BOM line 137:** the vdd_cpu H5 link sits inside the VOS sense loop; delete "RK860-0 remote sensing UNVERIFIED … fitted 0 Ω in every variant".
- **BOM I2C table (line 488 area) and Datasheets table:** I2C0 "RK809 0x20, RK860-0 0x40" → "RK809 0x20, TPS62869 0x42"; RK860-0 datasheet row → TPS62869, SLVSFS3B, <https://www.ti.com/lit/ds/symlink/tps62869.pdf>, sha256 `62f61d2bbc06f7d030be182838b00ff065a80c0b953b9319e11a4e66c4e6ab5c`.
- **Power tree v0:** §2 tree, "RK860-0 vdd_cpu 0.80-1.15 V (I2C DVS)" → "TPS62869 vdd_cpu 0.85–1.15 V (I2C DVS, 0x42), 6 A"; §3 rail table, vdd_cpu row: part TPS6286910C, 0.85–1.15 V, 6 A rating (3 A est. design), control "I2C DVS; EN from vcc3v3_pmu"; VSYS_LV row consumer list RK860-0 → TPS62869; §4.10 row "RK860-0 vdd_cpu | UNVERIFIED | … | Open" → the margin table above; §4.12 link 1 → "TPS62869 output, inside the VOS sense loop: drop regulated out"; §6.1 step 4 → "TPS62869 vdd_cpu starts at 0.9 V from EN (vcc3v3_pmu through 51 kΩ + 100 nF)"; §6.5 → vdd_cpu stays on in suspend (cost to measure); risks 10 and 12 → RK860 → TPS62869, rating now published (6 A); the RK3566 peak current stays **UNVERIFIED**.
- **Pinout v1:** row AJ37 (I2C0_SCL) note "RK809 0x20, RK860-0 0x40" → "RK809 0x20, TPS62869 0x42" (AK38 refers to it). No ball changes.
- **Feature blocks:** block #13 record as in decision item 8; the SoC block's power-domain line keeps "vdd_cpu from `blk.vdd-cpu`".
- **T1 product repository** (integration verification): RK860-0 mentions → TPS62869, by their owners.

### Done here

- parts-lib: [`Texas-Instruments/TPS6286910CRQYR.md`](https://github.com/opendap-project/parts-lib/blob/main/Texas-Instruments/TPS6286910CRQYR.md) (new), `Rockchip/RK860-0.md` (why it was replaced), `Rockchip/RK3566.md` (power line), `manifest.toml` (TPS6286910CRQYR datasheet and EVM guide, XGL4012-221MEC, SYR827PKC source; the RK860-0 entry notes that no datasheet exists).
- kicad-lib: symbol `Texas_Instruments:TPS6286910CRQYR` and footprint `Texas_RQY0009A_VQFN-HR-9_1.5x2.5mm_P0.5mm` from the generator data `generator/parts/Texas_Instruments/TPS6286910CRQYR.toml`, with its envelope STEP; `test_library.py` passes (11 tests).

### Open, to close on the first boards (UNVERIFIED until then)

- The C option regulates from VOUT Register 1 (write it, measure vdd_cpu). If not: fit the A option and change `reg` to 0x41.
- Load step at the SoC (0 → 3 A estimate) with the remote sense and the H5 link fitted: ripple ≤ 60 mV (HDG p. 36), no ringing; else fit the 0 Ω local-sense option (or move to the TPS6287x).
- vdd_cpu ready before the RK809-5 releases RESETn (scope vdd_cpu against RESETB); the RK809 OTP sequence is not public.
- RK3566 vdd_cpu peak current (the Rockchip report is not public): measure on the H5 link under all-core load.
- Suspend draw with vdd_cpu on: if it matters, a later revision gates EN from a rail that is off in suspend.
- Efficiency at 3.8 V and 0.15 A (screen-off playback): the datasheet curves are at 5 V.
