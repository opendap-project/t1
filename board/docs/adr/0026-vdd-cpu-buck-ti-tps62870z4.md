# ADR 0026: vdd_cpu buck: TI TPS62870Z4 for a ±1 % output over temperature

- **Status:** Accepted (2026-10-27). Supersedes [ADR 0023](0023-vdd-cpu-buck-ti-tps62869-restated.md).
- **Date:** 2026-10-28 (decision taken by the maintainers on 2026-10-27)
- **Basis:** BRD-010, BRD-049 (must); RK3566 DS 1.1 (p. 51, 1.2 V absolute maximum); mainline `rk3566.dtsi` operating points (read 2026-10-25); TI SLVSGC5E (TPS6287x, January 2023, revised October 2025, sha256 `7d9d4bd016674fa6dc55e655f8f3e81080b486fdf659d6e17e36b997d6e2ce48`); TI SLVSFS3B (TPS62869); Murata SimSurfing DC-bias data (read 2026-10-27 and 2026-10-28); sourcing check (T1-029), 2026-10-28.

## Context

ADR 0023 put vdd_cpu on the TI TPS62869. Its output holds ±1 % only at TJ 0–85 °C and ±2 % over TJ −40–125 °C (SLVSFS3B p. 7), and rises about 0.9 % in power-save mode (p. 25, Fig. 9-7, typical). At the RK3566's 1800 MHz operating point (1150 mV) the DC band alone reaches 1.173 V against the 1.2 V absolute maximum, so the device tree caps vdd_cpu at 1100 mV (top CPU clock 1608 MHz) as a documented BRD-049 safety limit (feature blocks #13).

Facts the decision relies on:

- **TPS62870Z4WRXSR** (SLVSGC5E): 6 A; output accuracy ±1 % over TJ −40–125 °C with VIN ≥ VOUT + 1.4 V (pp. 2, 11; VSYS_LV 3.8 V gives 2.65 V at 1.15 V); differential remote sense (VOSNS, GOSNS); I2C, 0.4–1.675 V in 5 mV steps in its default range (p. 1); with VSEL tied to VIN the Z4 option starts at 0.875 V at address **0x42** (p. 5), the address vdd_cpu has today; FSEL tied to VIN sets 3 MHz (p. 22, Table 7-2); MODE/SYNC is ORed with the FPWMEN bit (p. 25); EN needs a series resistor of at least 15 kΩ (p. 6); input capacitance ≥ 5 µF effective per VIN pin, output ≥ 40 µF effective (p. 9, Recommended Operating Conditions); 1.75 mA typical operating quiescent current, 16.5 µA with EN low (p. 9); its registers stay readable and writable with EN low (p. 20); VQFN-FCRLF-16 (RXS0016A) 2.55 × 3.55 mm, 1.05 mm maximum (p. 64). Layout (pp. 53–54): input capacitors identical at both VIN–GND pairs, VOSNS and GOSNS routed as a differential pair to the lowest-impedance point of the distribution network and away from the switch node, compensation between COMP and GOSNS (never power ground), and **at least twice as much capacitance at the load as at the device**. Mainline driver `tps6287x` (`ti,tps62870`) since Linux 6.5; Debian arm64 (`debian/config/arm64/config`, `debian/latest`, read 2026-10-27) does not set `CONFIG_REGULATOR_TPS6287X`.
- **Coilcraft XEL4012-920NE**: 92 nH, Isat 24 A at 25 °C, 5.2 mΩ typical, 4 × 4 × 1.2 mm (SLVSGC5E Table 9-2, p. 45). The TPS6287x needs 55–330 nH at 3 MHz and VOUT ≤ 1.675 V (p. 9).
- **Transient design** (TI's procedure, SLVSGC5E pp. 45–48: Eq. 13 compensation resistor, Eq. 15 output capacitance in regulation, Eq. 17 with the loop saturated, Eq. 19 and 24 compensation capacitor; gm 1.5 mS, τ 12.5 µs ± 30 %, L ± 20 %, fsw ± 10 %).
- **Effective capacitance** (Murata SimSurfing typical DC-bias curves, the lowest of −20, 0, 25, 60 and 85 °C, less the −20 % tolerance): at 1.1 V the board's GRM188R60J226MEA0D (22 µF 6.3 V X5R 0603) keeps **10.25 µF** and the GRM155R60J475ME47D (4.7 µF 6.3 V X5R 0402) **2.37 µF**. The vdd_cpu set of ADR 0023, 2 × 22 µF at the converter and 2 × 22 µF + 2 × 4.7 µF at the SoC (`blk.vdd-cpu`, `blk.soc-power`), gives **45.7 µF effective** (97.4 µF nominal). At 3.8 V the GRM188R60J476ME15D (47 µF 6.3 V X5R 0603, 1.0 mm) keeps **8.65 µF**.
- **Load step:** the RK3566 cluster's step is not public (**UNVERIFIED**). The worst case designed for is 4.8 A, 80 % of the converter's 6 A (BRD-049), released in 1 µs and in 0.1 µs.

## Decision

1. **vdd_cpu converter: TI TPS62870Z4WRXSR** on I2C0 at **0x42** (unchanged), VIN from VSYS_LV, on the back next to the SoC in place of the TPS62869. VSEL and FSEL tied to VIN: 0.875 V start-up, 3 MHz. SYNC_OUT open. PG open drain with the 100 kΩ pull-up to vcca1v8_pmu and its test pad, monitor only, as before. EN from vcc3v3_pmu through 51 kΩ (≥ 15 kΩ) with 100 nF to ground, as before. MODE/SYNC to ground: power-save mode by pin; forced PWM through the FPWMEN bit (the driver's `REGULATOR_MODE_FAST`).
2. **Inductor: Coilcraft XEL4012-920NE** (orderable XEL4012-920NEC), 92 nH, on the board's 4020-family land (the XGL4012 it replaces stands on the same land; the land against Coilcraft's XEL4012 drawing is **UNVERIFIED**). Worst-case limiter trip 16.6 A (14 A maximum high-side limit plus VIN / L × 50 ns at L − 20 %, p. 26) is 69 % of the 24 A Isat.
3. **Input capacitors:** one GRM188R60J476ME15D (47 µF 6.3 V X5R 0603, 8.65 µF effective at 3.8 V, the 5 µF minimum with 73 % to spare) and one 100 nF 0201 at each VIN pin (5 and 9), each on its own side of the package (p. 6, butterfly layout p. 46).
4. **Output capacitance, sized at the 1.1 V safety cap for the 4.8 A worst case:** the same six capacitors, 45.7 µF effective at 1.1 V, meet the 40 µF minimum; one 22 µF moves from the converter to the SoC so that the load carries at least twice the device's capacitance (1 × 22 µF at the converter, 10.25 µF effective; 3 × 22 µF + 2 × 4.7 µF under the SoC, 35.5 µF effective). Compensation **RZ 82.5 Ω 1 %** (Eq. 15: needs 44.5 µF effective, 2.7 % under what is fitted), **CC 5.6 nF C0G** (Eq. 24, gm × RZ = 0.12 < 1, with the inner-loop bandwidth at the largest output capacitance, 116.9 µF: 97.4 µF nominal + 20 %, no DC bias; 5.16 nF calculated), **CC2 22 pF C0G** from COMP to GOSNS (p. 48). Peak at the cap for a 4.8 A release: DC top 1.111 V (1.1 V + 1 %) + deviation 32.9 mV in regulation (Eq. 13 inverted at RZ 82.5 Ω) or 36.1 mV with the loop saturated at a 0.1 µs edge (Eq. 17; 0 at 1 µs) + 1.6 mV half ripple = **1.149 V, 51 mV under 1.2 V**.
5. **Sense:** VOSNS from the 22 µF at the SoC through the existing net tie on the load side of the H5 link, GOSNS from that capacitor's ground pad as its own trace, routed as a differential pair away from SW (pp. 29, 53–54). The ADR 0023 local-sense network (100 Ω, 100 nF, DNP 0 Ω) is not used by this part and is removed.
6. **Device tree:**

   ```dts
   &i2c0 {
       vdd_cpu: regulator@42 {
           compatible = "ti,tps62870";
           reg = <0x42>;
           regulator-name = "vdd_cpu";
           regulator-min-microvolt = <850000>;
           regulator-max-microvolt = <1100000>;   /* BRD-049 safety limit, see item 7 */
           regulator-always-on;
           regulator-boot-on;
           regulator-initial-mode = <REGULATOR_MODE_NORMAL>;
       };
   };
   ```

   The driver picks the voltage range from these constraints (0.4–1.675 V, 5 mV) and so never selects the 0.8–3.35 V range a wrong I2C write could reach; there is no hardware clamp, recorded as a risk (BOM §8). The driver is built as a DKMS module from the mainline source until Debian enables `CONFIG_REGULATOR_TPS6287X=m` (OS-023).
7. **1800 MHz stays the target, with a 30 mV margin (peak ≤ 1.170 V at 1150 mV), lifted only by measurement.** At 1150 mV in forced PWM at 3 MHz, TI's procedure asks for 158 µF effective for a 3 A step (RZ ≈ 2.0 kΩ; 12 more 22 µF 0603 than fitted) and 224 µF for 4.8 A (RZ ≈ 3.1 kΩ; 18 more). The board fits none of them now. Verification row (t1 electronics integration verification, M-CORE): measure the cluster's release step (all cores loaded to idle) on the H5 link and the peak at the SoC capacitor at 1150 mV, forced PWM, cold and hot; raise `regulator-max-microvolt` to 1150000 only if DC top + measured peak ≤ 1.170 V with the capacitors and compensation then fitted. Until then the 1608 MHz cap holds.

## Consequences

- `blk.vdd-cpu` (feature blocks #13): part, inductor, input capacitors, compensation and sense as above; software `ti,tps62870` (`tps6287x`, DKMS). Alternates: the TPS62869 and the FAN53555 leave (other lands); no same-land second source is recorded (the TPS62871Z4WRXSR, 9 A, shares the package).
- **Quiescent current:** 1.75 mA typical while enabled (≈ 6.7 mW from VSYS_LV), against 4 µA for the TPS62869, in playback and in suspend while vdd_cpu stays on. To measure; the TPS62870 keeps its registers with EN low (p. 20), so a later revision can switch vdd_cpu off in suspend.
- **Area:** the RXS0016A, two input positions, RZ, CC and CC2 replace the TPS62869 and its sense network; the effect is in [placement v1](../specs/placement-v1.md).
- **Sourcing (T1-029), 2026-10-28:** TPS62870Z4WRXSR and GRM188R60J476ME15D pass; the XEL4012-920NEC is conditional (no authorized stock read at the distributors; the maker's own channel to be read before the board freezes).
- BOM v1 lines 3, 4, 147, the driver and datasheet tables, power tree v0, pinout v1 (the I2C0 note) and feature blocks #13 follow this ADR.
