# Power tree v0

- **Version:** v0.8 (2026-10-25), with BOM v1.14: [Changes in v0.8](#changes-in-v08). v0.7 is the state of BOM v1.13, v0.6 is the state of BOM v1.12, v0.5 is the state of BOM v1.11, v0.4 of BOM v1.10, v0.3 of BOM v1.9, v0.2 the state of BOM v1.8, v0.1 of BOM v1.7.
- **Status:** Draft. Desk design only: nothing here has been built or measured. Simulated (updated 2026-10-24): the amplifier rails ([output-stage simulation](../../sim/output-stage/README.md)), the VSYS bucks and the MaskROM entry ([VSYS buck and MaskROM simulations](../../sim/README.md)); netlists in `sim/`. Every part is *Proposed* unless [BOM v1](bom-v1.md) says *Decided*. Updated 2026-10-22 by the BOM v1 cross-validation (battery, HAT/USB 5 V source, TPS2121 isolation, faceplate rails, IO voltages, vdd_cpu part), then by BOM v1.1 (RK809-5 feeds and ratings, TPS61089 boost, 3.1 V MCLK supply, RP2354A supplies, battery derating, TPS2121 OV1, HP-amp soft-start), then by BOM v1.2 (power margin check of every rail, converter, connector and cable, BRD-049, §4.10; vcc3v3_sys on a 3 A TPS62826; battery path sized for the full output budget, BRD-050 and proposed ADR 0011; battery fuse; 50-contact HAT power connector; RGB status LED driver; TPS61089 and TPS2121 current limits), then by BOM v1.3 ([ADR 0012](../adr/0012-headphone-output-stage.md): six OPA1622 with paralleled halves, ±6 V amplifier rails on LT3045/LT3094 from ±7 V TPS65131 pre-rails, gain 1.62 with the CS43198 at `+1dB_EN` = 0, §4.1, §4.2, §4.10.1; interim-pack output ceiling, §4.11; vcc3v3_sys inductor, §4.10), then by BOM v1.4 (HAT pogo power contacts fixed by the hat-standard HAT interface v1, §4.10; no power part changes), then updated by BOM v1.5 / [ADR 0014](../adr/0014-two-cell-battery.md) (two-cell battery: BQ25798 charger, VSYS 6.0–8.8 V, TPS62136 pre-regulator to a 3.8 V VSYS_LV rail feeding the former 1S tree, TPS62903 bucks for HAT_5V/USB-C and HAT_3V3, BQ28Z610-R1 gauge, 5 A fuse, Micro-Fit 3.0 connector; full output budget ≈ 2.4 A at VSYS 6.6 V, battery path sized for the ≈ 3.2 A worst case; interim ceiling removed; finding 14, §2, §3, §4.6, §4.7, §4.9–§4.11). Then updated by BOM v1.6 / [ADR 0015](../adr/0015-amplifier-rails-from-vsys.md) (−7 V pre-rail from an LMR33630C inverting buck-boost on VSYS, TPS65131 boost only, paired LT3045/LT3094; ship FET; MaskROM supervisor; TPS62136 inductor correction; §2, §3, §4.7, §4.10, §4.10.1, §5, §6).
- **Date:** 2026-10-22 (v0.2 to v0.5: 2026-10-24; v0.6 to v0.8: 2026-10-25)
- **Companion:** [BOM v1](bom-v1.md) (parts, datasheet links and hashes).
- **Inputs:** [BOM v0](bom-v0.md), ADR 0012, [board requirements](../requirements/README.md) (BRD-001 to BRD-050), board ADRs 0001–0015 (from v0.4 also [ADR 0020](../adr/0020-battery-connected-through-contacts.md); from v0.6 [ADR 0021](../adr/0021-vdd-cpu-buck-ti-tps62869.md) and [ADR 0022](../adr/0022-lpddr4x-micron-mt53e1g32d2fw-with-cxmt-second-source.md)), [output-stage simulation](../../sim/output-stage/README.md) and [VSYS buck and MaskROM simulations](../../sim/README.md) (v1.6), ADR 0014 (v1.5), touch-faceplate ADR 0001 (Focus E35GH), T1 and HAT Case Standard requirements, blackbird-os ADRs 0006–0008. Pin multiplexing v0 gave the balls until v0.2; from v0.3 [pinout v1](pinout-v1.md) does (§3.1). GPIO names below are net names.
- **Method:** datasheets were downloaded and read (revision and sha256 in the BOM's Datasheets table); the RK809 rail mapping follows the Radxa ROCK 3C v1.4 schematic (PMIC marked RK809-5) and the mainline device trees of RK3566 + RK809 boards (Orange Pi 3B, ROCK 3C, ODROID-M1S), with Anbernic RG353 (RK817) and the Radxa ZERO 3W schematic v1.12 for the rest. Calculations are shown inline.
- **Conventions:** **UNVERIFIED** = no primary source found in this session. "Est." = engineering estimate, to be replaced by measurement (T1-026).

## Changes in v0.8

With [BOM v1.14](bom-v1.md#changes-in-v114) and [RFC 0015](https://github.com/opendap-project/rfcs/blob/main/text/0015-hat-connector-pogo-field-and-usb-c-port-hat.md): the HAT connector is the pogo field (hat-standard ADR 0001 confirmed; Mill-Max 0965 primary). Nothing here is built or measured.

1. **Shared 5.1 V limiter, eFuse #D (§2, §4.6; closes §8 item 29).** A third TPS259470A sits between the TPS62903 5.1 V buck and the inputs of eFuses #A (HAT `VBUS`) and #C (USB-C source), **RILM 1.47 kΩ 1 %**:

   | Corner | RILM | Equation 7 (SLVSFC9C) | ±10 % | Trip |
   |---|---|---|---|---|
   | Minimum | 1.4847 kΩ (+1 %) | 2.246 A | −10 % | **2.021 A** |
   | Typical | 1.470 kΩ | 2.268 A | — | **2.268 A** |
   | Maximum | 1.4553 kΩ (−1 %) | 2.291 A | +10 % | **2.520 A** |

   | Fault case (BRD-049) | Limited by | Buck current | Of the 3 A rating | Of the 4.0 A minimum high-side limit |
   |---|---|---|---|---|
   | Normal, full budget | software (1.6 A design) | 1.6 A | 53 % | 40 % |
   | One port shorted or overloaded, the other idle | its eFuse, #A or #C (≤ 1.981 A, below #D's 2.021 A minimum) | ≤ 1.981 A | 66 % | 50 % |
   | One port overloaded, the other loaded | #D, or the overloaded port's eFuse | ≤ 2.520 A | 84 % | 63 % |
   | Both ports at their maximum trip (software fault) | #D | ≤ 2.520 A | **84 %** (was 3.96 A, 132 %) | 63 % |
   | #D failed short, one port at its maximum | #A or #C | ≤ 1.981 A | 66 % | 50 % |
   | #D failed short and both ports at their maximum (two independent faults) | the buck's high-side limit | ≤ 3.96 A | 132 % | 99 % |

   Every single-fault case stays at or below 84 % of the buck's rating. Inductor peak in the worst single fault: 2.520 + 0.535 = 3.06 A, 35 % of the XGL4020-102MEC's 8.8 A Isat. #D: switch 2.520 A = 46 % of 5.5 A; conduction 28.3 mΩ × 1.6² = 72 mW at the design load, 180 mW at its maximum trip. The added drop at 1.5 A is 42 mV (RON 28.3 mΩ), so a port sees 5.1 − 2 × 0.042 = 5.02 V nominal at 1.5 A, inside vSafe5V (4.75–5.5 V). EN from the buck's output (UVLO divider); fault on expander P16 (`EFUSE_5V_FLT_N`); IMON to a test pad. The fast trips of #D (2 × ILIM) and of #A and #C coordinate on the bench (V2-P04).
2. **5 V only from a HAT (§4.7; closes §8 item 30).** The HAT `VBUS` input path is rated for 5 V: TVS0500 5 V stand-off and 7.5 V minimum breakdown (SLVSED2C §7.4, §7.6), FUSB302B `CC` 6.0 V absolute maximum (FUSB302B/D Rev. 5 p. 14), TPD4E05U06 5.5 V stand-off (SLVSBO7O). The HAT port controller's sink capabilities list vSafe5V only. **TPS2121 OV2 divider R1 464 kΩ / R2 100 kΩ (1 %):** VTRIP = VREF × (1 + R1/R2) = 1.06 × 5.64 = 5.98 V typ, **5.60–6.31 V** over VREF 1.01–1.1 V and the resistor tolerance (the OV1 method): above the 5.5 V vSafe5V maximum, 84 % of the TVS's minimum breakdown at its maximum. The `HAT_SRC_ON` force on OV2 stays (hardware OR, as on OV1). A `CC`-to-`VBUS` short at vSafe5V reaches at most 5.5 V, 92 % of the `CC` absolute maximum.
3. **HAT connector (§4.10):** the pogo field on the device-side piece through one DF40C-50 per cable end (BOM lines 66, 67, 102; HAT flat cable spec v1). `VBUS` on 4 pogo contacts (0.75 A each at 3.0 A, 38 %; 75 % at the 4.5 A ceiling with one open) and 15 DF40 contacts (0.20 A, 67 %; 100 % at 4.5 A); at the T1's own trips 44 % out and 66 % in on the DF40. The `VBUS` TVS sits on the device-side piece at the field.

## Changes in v0.7

With [BOM v1.13](bom-v1.md#changes-in-v113): HATs are USB only and HAT power follows USB Power Delivery (hat-standard [interface v2](https://github.com/opendap-project/hat-standard/blob/main/docs/specs/interface-v2.md) and [ADR 0006](https://github.com/opendap-project/hat-standard/blob/main/docs/adr/0006-hats-are-usb-only.md); [RFC 0014](https://github.com/opendap-project/rfcs/blob/main/text/0014-hat-interface-v2-usb-only.md)). The HAT port carries one power net, `VBUS` (the board net keeps the name `HAT_5V`): 3.0 A continuous, 4.5 A fault ceiling (interface v2). The physical HAT connector is still open, so the contact and flat-cable rows of §4.10 stay as they were and follow that decision. Nothing here is built or measured.

1. **HAT_3V3 removed (§2, §3, §4.6, §5, §6.4, §6.5):** the TPS62903 3.3 V buck (BOM line 38), its inductor (line 7) and eFuse #B go. Nothing on the board used HAT_3V3 besides the HAT branch (PCA9306 VREF2 and the AXC B side, both removed). The full output budget loses its 3.67 W HAT_3V3 term (§4.7): 8.77 + 3.26 = **12.0 W → 1.82 A at VSYS 6.6 V**, ≈ 16.9 W → 2.56 A with full-scale headphones (was 15.7 W / 2.38 A and 20.6 W / 3.1 A). The battery chain keeps its 3.2 A design point (ADR 0014); every element gains margin.
2. **HAT `VBUS` source (§4.6):** eFuse #A from the 5.1 V buck, enabled by `HAT5V_EN` (expander P02), which the port controller's TCPM source path drives as the `vbus-supply` regulator of the HAT `usb-c-connector`. The offer is 5 V at 1.5 A, shared with the USB-C source as before (one 5.1 V converter, 1.6 A design).
3. **eFuse trip setting (§4.6, BRD-049).** At RILM 2.21 kΩ 1 % the minimum trip was 3,334 / 2,232 Ω = 1.494 A − 10 % = **1.344 A** (SLVSFC9C Equation 7, ±10 % above 1 A), below the 1.5 A both 5 V ports offer: a compliant sink drawing its full 1.5 A could trip the eFuse. **RILM → 1.87 kΩ 1 % on #A and #C:**

   | Corner | RILM | Equation 7 | ±10 % | Trip |
   |---|---|---|---|---|
   | Minimum | 1.8887 kΩ (+1 %) | 1.765 A | −10 % | **1.589 A** |
   | Typical | 1.870 kΩ | 1.783 A | — | **1.783 A** |
   | Maximum | 1.8513 kΩ (−1 %) | 1.801 A | +10 % | **1.981 A** |

   | Check | Rating or limit (source) | Value | Use | Result |
   |---|---|---|---|---|
   | 1.5 A offer against the minimum trip, #A and #C | 1.589 A | 1.5 A | 94 % | OK (was 112 % of 1.344 A) |
   | #A maximum trip against the HAT `VBUS` fault ceiling | 4.5 A (interface v2) | 1.981 A | 44 % | OK |
   | #A maximum trip against the HAT `VBUS` continuous rating | 3.0 A (interface v2) | 1.981 A | 66 % | OK |
   | #C maximum trip against the USB-C receptacle | 5.00 A for the VBUS pins together (GCT USB4105 drawing) | 1.981 A | 40 % | OK |
   | eFuse switch | 5.5 A (SLVSFC9C, title) | 1.981 A | 36 % | OK |
   | 5.1 V buck with both eFuses at their maximum trip (a software fault: the budget is 1.6 A) | 3 A rating; high-side limit 4.0 / 4.6 / 5.5 A (SLVSES3A §6.5) | 3.96 A | 132 % of the rating, 99 % of the minimum limit | Bounded by the eFuses below the buck's minimum limit; a sustained double fault runs the buck above its rating (was 3.36 A, 112 %), a thermal check for the board model (§8 item 29) |
   | 5.1 V buck inductor XGL4020-102MEC | Isat 8.8 A (30 % drop) | 3.96 A + ΔIL / 2 = 4.5 A | 51 % | OK |

   Datasheet cross-check: the 1.65 kΩ row gives 1.800 / 2.028 / 2.200 A (SLVSFC9C §6.5), consistent with Equation 7 and ±10 %. Conduction loss at the typical trip: 28.3 mΩ × 1.783² = 90 mW.
4. **HAT `VBUS` sink (§4.6, §4.7):** a source or dual-role HAT (a powerbank) feeds the T1 through TPS2121 IN2, as before; ILM 1.94 / 2.45 / 2.95 A (RILM 45.3 kΩ 0.1 %, v0.5): the maximum is 66 % of the 4.5 A fault ceiling and 98 % of the 3.0 A continuous rating. The HAT port's PD sink offer stays 5 V until the maintainers decide which PD voltages the T1 accepts from a HAT (§8 item 30): above 5 V the OV2 threshold, the `VBUS` TVS and the `CC` protection follow, as on the main USB-C.
5. **Dual-role power through the existing mux.** IN1 (main USB-C) keeps priority over IN2 (HAT). The T1 never sources and sinks the HAT port at once: `HAT_SRC_ON` (= `HAT5V_EN`) forces OV2 high while eFuse #A is on, in hardware, as in v0.5. A power-role swap goes through TCPM: it first drops one direction (eFuse #A off, or the sink contract released so the HAT turns its `VBUS` off), then enables the other; the interlock holds at every step. With a USB-C adapter present and a powerbank HAT attached, the T1 may charge the HAT (source role, IN2 off) or leave it idle; it never feeds the adapter's power back through IN2. eFuse #A blocks reverse current while it is off (SLVSFC9C: true reverse current blocking), so a source HAT's `VBUS` never reaches the 5.1 V buck.
6. **Dead battery.** With the T1 unpowered, the HAT port controller presents its sink pull-down on `CC` (FUSB302B/D Rev. 5 p. 1, "dead battery support"; VUFPDB ≤ 2.18 V, p. 15), so a source HAT can turn on `VBUS`, which reaches the charger through TPS2121 IN2 (enabled by default, §5).
7. **`VBUS` discharge on detach.** SLVSFC9C describes no output discharge for the TPS25947, so the HAT `VBUS` gets a discharge path: an N-FET (the line 35 DMG1012T-7) with a series resistor to GND, gate on expander P01 `HAT_VBUS_DISCH` (freed by `HAT3V3_EN`) with a pull-down, driven by Blackbird OS through TCPM after the source turns off. The resistor value, sized for the USB PD discharge time with the port's capacitance, is **UNVERIFIED** until the schematic.
8. **Measurement:** eFuse #A IMON stays on SARADC_VIN2; SARADC_VIN3 (was #B) takes eFuse #C IMON (closes pinout v1 C10). The INA236 HAT channel at the 5.1 V buck input still sees #A and #C together.
9. **Camera PHY rails (§5):** RK809 LDO1 (`vdda0v9_image`) and LDO9 (`vcca1v8_image`) have no consumer: the CSI-2 receiver is unused (pinout v1 O2 decides the unused-PHY handling). They stay off. The PCIe PHY has no HAT consumer either; the USB 3 PHY (combphy1, HOST1) feeds the HAT port.

## Changes in v0.6

With [BOM v1.12](bom-v1.md#changes-in-v112): [ADR 0021](../adr/0021-vdd-cpu-buck-ti-tps62869.md) (vdd_cpu buck TI TPS62869 instead of the RK860-0) and [ADR 0022](../adr/0022-lpddr4x-micron-mt53e1g32d2fw-with-cxmt-second-source.md) (LPDDR4X Micron MT53E1G32D2FW-046 IT:C, CXMT second source), both Accepted. The HAT flat-cable and faceplate-flex changes of BOM v1.12 move no rail. Nothing here is built or measured; no requirement priority or status changes.

1. **vdd_cpu (§2, §3):** TPS6286910C on VSYS_LV, 0.85–1.15 V in 5 mV steps by I2C DVS at **0x42** (I2C0), 0.9 V at boot without software, 6 A rating against the 3 A design estimate. EN from vcc3v3_pmu through 51 kΩ + 100 nF.
2. **Margins (§4.10, BRD-049):** converter 50 % of 6 A; VIN 69 % of the 5.5 V recommended maximum (63 % of 6 V); inductor peak 3.76 A = 54 % of the 7 A minimum high-side limit (ΔIL 1.52 A at 1.15 V out, 3.8 V in, 0.22 µH, 2.4 MHz); XGL4012-221MEC saturation 86 % (20 % drop) and 59 % (30 % drop) at the 8.5 A maximum limiter trip, heating 28 % of Irms; output 0.833–1.173 V (± 2 %) inside the RK3566's 0.81 V minimum and 1.2 V absolute maximum (27 mV of headroom at the 1150 mV ceiling). The "Open: datasheet from Rockchip" row is closed.
3. **Measurement link 1 (§4.12):** the H5 link on vdd_cpu sits inside the VOS sense loop, so its 15 mV drop is regulated out; it returns only with the 0 Ω local-sense fallback (0.818 V at the 850 mV point, still ≥ 0.81 V).
4. **Sequencing (§6.1):** vdd_cpu follows vcc3v3_pmu through the EN RC, as HDG 1.1 p. 34 orders; that it is up before RESETn is a first-boards check.
5. **Suspend (§6.5):** vdd_cpu stays on (EN low resets the converter's registers; the driver has no suspend operations); the cost is to measure.
6. **LPDDR4X windows (§4.8):** from the Micron data sheet, VDD1 1.70–1.95 V, VDD2 1.06–1.17 V, VDDQ 0.57–0.65 V. vcc_ddr (1.083–1.143 V) keeps 23 mV and 27 mV to the VDD2 limits, vcc0v6_ddr (0.591–0.609 V) 21 mV and 41 mV to the VDDQ limits, vcc1v8_ddr (1.79 V nominal at 100 mA) 90 mV and 160 mV to the VDD1 limits. No rail changes; the currents stay placeholders until the IDD tables are transcribed (§8 item 28).
7. **Risks 10 and 12 (§9):** the vdd_cpu converter rating is published; the RK3566 vdd_cpu peak current stays **UNVERIFIED**.

## Changes in v0.5

With [BOM v1.11](bom-v1.md#changes-in-v111): hat-standard [HAT interface v1.1](https://github.com/opendap-project/hat-standard/blob/main/docs/specs/interface-v1.md) and its [ADR 0005](https://github.com/opendap-project/hat-standard/blob/main/docs/adr/0005-interface-v1-1-shared-extension-and-contact-reduction.md), and the board changes of the t1 [faceplate interface v1](https://github.com/opendap-project/t1/blob/main/docs/specs/faceplate-interface.md) §10 (t1 ADRs 0004, 0005). Nothing here is built or measured; no requirement priority or status changes.

1. **HAT fault ceilings (§4.6):** the interface ceilings become `HAT_5V` 3.0 A, `HAT_3V3` 1.5 A, `GND` 4.5 A (were 3.6 / 1.8 / 5.4 A). The T1's limiters, tolerance and resistor included: eFuse #A (`HAT_5V` out) **1.68 A** (56 %), TPS2121 (`HAT_5V` in, class F) **2.95 A** (98 %) after RILM 44.2 → **45.3 kΩ 0.1 %** (at 44.2 kΩ 1 % it reached 3.02 A), eFuse #B (`HAT_3V3`) **1.16 A** (77 %), `GND` 2.95 + 1.16 = 4.11 A (91 %).
2. **Charger input (§4.7):** with the TPS2121 minimum at 1.94 A, the BQ25798 IINDPM becomes **1.9 A** at VBUS ≤ 5.5 V (≈ 1.86 A at most, est.), so the mux never current-limits in normal charging; 9 V PD stays at 1.67 A. 5 V charging input drops from 10 W to 9.5 W.
3. **HAT power connector (§4.6, §4.10):** the DF40C-50 power pair is removed; power runs on the single DF40C-100 (`HAT_5V` × 10, `HAT_3V3` × 5, `GND` × 15): 67 % continuous, 100 % at the interface ceilings, at most 98 % at the T1's own trips. Flat-cable power conductors are sized for the ceilings (BOM line 102).
4. **HAT extension switch (§2, §3, §5):** two TMUXHS4412 on vcc3v3_sys, 320 µA typical each while an L3 HAT is active (≈ 2.1 mW for both, 3.3 V × 0.64 mA), 0.1 µA in standby; standby (PD high) is the reset and suspend state through a pull-up, so nothing changes in the suspend budget.
5. **Faceplate rails (§2, §3, §5; t1 ADR 0005):** FP_3V3 from a **TPS22950** at 0.22–0.38 A (≤ 0.4 A ceiling); FP_1V8, MIC_1V8 and FP_VCI each from a **TPS22945** at 100–200 mA (≤ 0.2 A ceiling; limit at 1.8 V and 2.8 V **UNVERIFIED**). FP_VCI's switch sits between RK809 LDO4 and the connector, ON from `FP_IO_EN`, because the RK809 datasheet states no LDO4 trip value and the RK809-5's OTP start-up state of LDO4 is unknown. The TPS22945 has no output discharge and no reverse blocking (SLVS832D §9.1.3): 10 kΩ discharge resistors, and each switch opens before its source rail goes down (FP_VCI before LDO4; FP_1V8 and MIC_1V8 before vcc_1v8 in suspend).
6. **Backlight (§4.5):** **TPS61160** (open-LED threshold 25–27 V) instead of the TPS61169 (36–39 V), so BL_LEDA stays ≤ 27 V in every state against the FH35C's 30 V; RSET 3.32 Ω; inductor 22 µH.
7. **Naming:** "faceplate interface v0" is now "faceplate interface v1"; no rail or contact moves.

## Changes in v0.4

[ADR 0020](../adr/0020-battery-connected-through-contacts.md) (Accepted: battery connected through contacts), with [BOM v1.10](bom-v1.md#changes-in-v110). Nothing here is built or measured; no rail, regulator or requirement status changes.

1. **Battery connection (finding 20; §2, §4.7, §4.10):** the 4-pin Micro-Fit 3.0 and the pack lead are replaced by six KYOCERA AVX 70-9258-001-120-006 spring contacts in a window of the pocket floor, pressing on recessed hard-gold pads of the pack's terminal board. Order at 3.5 mm pitch: P+, P+, empty position, mid-cell tap, NTC, P−, P−.
2. **BRD-049 margins re-checked through the contacts (§4.7.1):** worst continuous 3.2 A puts 2.0 A on the hotter contact, **33 %** of its 6 A; the 5 A protective limit 3.1 A, **52 %**; the full budget (2.4 A) 1.5 A, 25 %. Heat at an end-of-life resistance of 20 mΩ per contact (**UNVERIFIED**): 0.08 W on the hotter contact and ≈ 0.26 W in the four power contacts at 3.2 A; 0.19 W and ≈ 0.63 W at 5 A, for the PCM's trip time only.
3. **Path resistance (§4.7):** ≈ 65 mΩ with the contacts at end of life (est., was ≈ 38–48 mΩ): ≈ 0.21 V and ≈ 0.66 W at 3.2 A. The cell pair must hold ≈ 6.8 V under load for VSYS = 6.6 V (was ≈ 6.7 V).
4. **Insertion (§4.7.1):** BATP gets 47 nF to GND behind its 100 Ω (SLUSDV2C Figure 8-2 note 2; BOM line 115); with no adapter the ship FET is off at insertion and is the soft start; with an adapter present the pulse into the BAT node (≈ 63 A peak for ≈ 2 µs, est.) is 0.07 % of the fuse's melting I²t.
5. **Cover detect (should, BOM line 143):** one GPIO input with a pull-up; no rail or regulator change. The pull-up value is set at schematic capture against the suspend budget (100 kΩ at 1.8 V draws 18 µA while a closed cover grounds the input, arithmetic).

## Changes in v0.3

[ADR 0019](../adr/0019-master-clock-divided-from-twice-the-frequency.md), the power-tree items of [pinout v1](pinout-v1.md) §9.2 (B1–B5, B16) and three decisions taken on 2026-10-24, with [BOM v1.9](bom-v1.md#changes-in-v19). Nothing here is built or measured.

1. **New rail MCLK_1V8** (ADR 0019, finding 18): a third TPS7A2018 from AUDIO_2V2, EN = DAC_DIG_1V8, ≈ 8.9 mA for two SN74AUC1G74 dividers; MCLK_3V1 now feeds the 45.1584 / 49.152 MHz oscillators only, without the attenuator (§2, §3, §4.4, §4.9, §4.10, §4.12, §5, §6.2, §6.3).
2. **vcc3v3_sys on a TPS62827** (finding 19): the re-sum gives ≈ 2.45 A (est.) = 82 % of the TPS62826's 3 A, past 80 %; the pin-compatible 4 A part runs at 61 % (§2, §3, §4.10).
3. **Radio in suspend for item tracking** (decision 2026-10-24; BRD-030, T1-069): vcc3v3_wl moves from RK809 SWOUT1 to a TPS22919 from vcc3v3_sys, ON = expander P06 `WL_PWR_EN`; vcc1v8_wl follows it. Default off in suspend, on only while the listener enables tracking; then vcc_1v8 also stays on in suspend. Suspend draw **UNVERIFIED** until measured on M-RF (§2, §3, §4.10, §5, §6.5).
4. **Faceplate supply in suspend** (decision 2026-10-24; T1-060; pinout B5): FP_3V3 and FP_1V8 off by default; `FP_IO_EN` on expander P00 can keep FP_3V3 on (§3, §5, §6.5).
5. **802.15.4** (decision 2026-10-24; T1-077): the four SPI2 M0 balls stay unassigned spares reserved for a variant; no power change.
6. **Pinout v1:** `vccio6_1v8` row (B1); IO-domain table §3.1 (B2); `HAT3V3_EN` on expander P01 (B3); USB PHY 3.3 V supplies (B16, **UNVERIFIED**); HAT ID translator and AXC B side on HAT_3V3 (B14); every "to reconcile with pinout v1" note of v0.2 holds (pinout v1 §9.1) except `HAT3V3_EN`.
7. **Measurement:** link 36 at the MCLK_1V8 LDO input (§4.12).

## Changes in v0.2

[ADR 0017](../adr/0017-fuel-gauge-wiring-sense-resistor-and-configuration.md) (Accepted), with [BOM v1.8](bom-v1.md#changes-in-v18). nothing here is built or measured. IO-domain voltages assumed here are marked "to reconcile with pinout v1".

1. **New rail vcc1v8_wl** (Type 2EL AVDD18, finding 16): a TPS62826 from VSYS_LV, EN on vcc3v3_wl, 390 mA typical, 1.05 A peak (§2, §3, §4.10).
2. **New rail vcc1v8_ddr** (LPDDR4X VDD1 and the TPS7A1006 BIAS) on vcca1v8_pmu, which stays on in suspend (finding 15, §4.8); vcc_1v8 no longer feeds anything the memory needs in self-refresh.
3. **VDD2 checked:** vcc_ddr 1.113 V nominal (BUCK3, 47 kΩ / 120 kΩ), ≈ 1.08–1.14 V worst case (§4.8).
4. **New rail NFC_VBAT** (PN7160 VBAT and VDD(UP)) from VSYS_LV through a TPS22919, 290 mA maximum (finding 17).
5. **Always-on 1.8 V group on vcca1v8_pmu** (G1, G5, G6, G15, G16, G19): IMU, TPM, NFC tag, PN7160 VDD(PAD), board EEPROM, expander VCCI, I2C2 pull-ups; budget ≈ 160 mA (est., §4.13).
6. **Interlocks** (G2, G3, G14): the CS43198 control bus closes only while DAC_DIG_1V8 is up; MCLK_3V1 EN = `AUDIO_LN_EN` AND DAC_DIG_1V8; `PCIE_PERST#` = SoC PERST# AND HAT power-good (§5, §6.4).
7. **Measurement** (G10–G12): 35 block measurement links and five INA236 positions (§4.12).
8. **Margins re-checked** (§4.10): VSYS_LV 53 % continuous, the TPS62136 switch at 81 % of its minimum limit only when three estimated peaks coincide; vcc3v3_sys peak ≈ 2.35 A = 78 % (est.).
9. **Fuel gauge ([ADR 0017](../adr/0017-fuel-gauge-wiring-sense-resistor-and-configuration.md)):** PACK on the switched side of the ship FET, sense resistor 3 mΩ, storage through gauge SHUTDOWN and the charger's shutdown mode: board drain ≈ 1 µA typical, 4.7 µA maximum (§2, §3, §4.7, §4.10, §6.1).

## 1. Findings that change earlier drafts

1. **The CS43198 does not accept a 45.1584 or 49.152 MHz master clock.** Its datasheet (DS1156F2, §4.6 and Table 3-13) allows an external MCLK only at the nominal internal frequencies **22.5792 MHz and 24.576 MHz** (or PLL references 9.6–26 MHz). BRD-023 (Draft) and BOM v0 lines 9–10 name 45.1584/49.152 MHz. Proposal: **22.5792 MHz and 24.576 MHz NDK NZ2520SDA**, which keeps the intent of BRD-023 (two families, DAC as clock master, no resampling). A divide-by-two flip-flop would also work but adds a part and jitter in the clock path, against BRD-042. **v0.3: superseded by finding 18** ([ADR 0019](../adr/0019-master-clock-divided-from-twice-the-frequency.md)): the divider is adopted because only it guarantees the DAC's 45–55 % duty.
2. **The CS43198 also needs a battery-class supply, VP = 3.0–5.25 V** (charge-pump supply for its output stage), plus four 1.8 V rails (VA, VCP, VD, VL). VP must come up first and go down last (DS1156F2 §5.2).
3. **The MCLK input is in the 1.8 V VL domain.** No available audio-grade 1.8 V oscillator exists at 22.5792 MHz (the 1.8 V NSC5083A has no authorized source), so the 3.3 V NSC5083D runs on its own MCLK_3V3 LDO and reaches XTI through a passive attenuator (ADR 0010). v0.3: the attenuator is removed; XTI is driven by 1.8 V dividers (finding 18).
4. **The LM27762 cannot make ±5 V from a 1S battery.** Its positive output is an LDO from VIN, so at VSYS = 3.5 V the positive rail is at most about 3.45 V (calculation in §4.2). The proposed generator is a **TPS65131** dual boost/inverter followed by **TPS7A4901 / TPS7A3001** LDOs (v1.3: **LT3045 / LT3094**, ADR 0012).
5. **The TPS7A94 is unsuitable for a battery device here:** 15 mA typical ground current at 5.1 V out (SBVS336C, Electrical Characteristics), that is about 80 mW wasted.
6. **The RK809-5 must be used with the reference rail mapping.** Its regulators come up at OTP default voltages before Linux runs. The mapping below copies the Radxa ROCK 3C v1.4 schematic (RK809-5) and the mainline device trees of the ROCK 3C, Orange Pi 3B and ODROID-M1S, which agree: every VCC pin of the reference boards is on a free-running vcc3v3_sys (the ROCK 3C leaves the EXT_EN option on its 3.3 V buck unfitted). The T1 keeps VCC5–VCC9 on vcc3v3_sys, now always-on, and feeds VCC1–VCC4 (BUCK1–4) from VSYS as in the datasheet application circuit (Fig. 1-1). Supply-pin mapping (RK809 datasheet §2.5): VCC1–VCC4 → BUCK1–4, VCC5 → LDO1–3, VCC6 → LDO4–6, VCC7 → LDO7–9, VCC9 → BUCK5 and SWOUT1, VCC8 → SWOUT2. The RK809-5 OTP defaults are not public (**UNVERIFIED**). v1.5: VCC1–VCC4 move from VSYS to VSYS_LV (3.8 V, finding 14).
7. **LPDDR4X needs a separate 0.6 V VDDQ rail.** The Radxa ZERO 3W schematic table gives VDDQ 1.10 V and VDDQL 0.60 V for LPDDR4X, with a 0 Ω option (R122) that ties VCC0V6_DDR to VCC_DDR only for plain LPDDR4.
8. **The battery path is limited to 1.6 A continuous with the interim pack** (v1.1 derating). The pack is the Adafruit 328 (ADR 0007): its sheet allows ≤ 2C discharge, but JST rates the PH contact 2 A with AWG #24 wire only, and the pack leads are 26 AWG. VSYS on battery is budgeted at 1.6 A (≈ 5.6 W at 3.5 V), and from v1.2 a 2.5 A board fuse bounds it (§4.7). The board itself is sized for the full output budget, 4.8 A from the battery (BRD-050, proposed ADR 0011); no available pack that carries it has been found yet. **v1.5: superseded by finding 14** (2S, ADR 0014): the Adafruit 328 is no longer a T1 pack.
9. **The BQ25895 cannot supply OTG while it charges.** The draft fed HAT_5V and the USB-C source from the OTG boost, so a class A/B HAT lost 5 V whenever USB-C power was plugged in. HAT_5V and USB-C VBUS out now come from a **TPS61089 boost from VSYS** (5.1 V) behind eFuses #A and #C (v1.1: the TPS61088 has no ti.com product page or datasheet any more). v1.5: the BQ25798 has the same OTG limitation; with a 2S VSYS the 5.1 V source becomes a **TPS62903 buck** (finding 14).
10. **The T1's own 5 V must not re-enter the charger.** When the T1 sources USB-C VBUS, that VBUS is also TPS2121 IN1; when it sources HAT_5V, that net is IN2. Both OV inputs are forced high by hardware OR of the source enables (`USB_SRC_ON`, `HAT_SRC_ON`), not by software order.
11. **IO voltages follow the pin plan:** I2C0/1/2 on PMUIO2 at 1.8 V (the CS43198 control port shares the bank and is 1.8 V-only); the faceplate bank VCCIO5 at 3.3 V.
12. **MCLK at 3.1 V** (ADR 0010, supply part amended in BOM v1.1): MCLK_3V1 from VSYS through a TPS7A2031. On battery VSYS follows VBAT below VSYSMIN, so a 3.3 V LDO had 0.2 V or less of headroom; 3.1 V stays inside the NSC5083D 2.97–3.63 V supply range with ≥ 0.3 V headroom down to 3.4 V. The oscillator current below is the NZ2520SDA figure. v1.5: the TPS7A2031 input is VSYS_LV, a fixed 3.8 V (finding 14): 0.7 V headroom at all battery states.
13. **Debian already enables the INA236 current monitor** through the IIO `ina2xx-adc` driver (`CONFIG_INA2XX_ADC=m`, compatible `ti,ina236`), while the hwmon INA2xx/INA238 drivers are off. The instrumentation uses INA236.
14. **v1.5, [ADR 0014](../adr/0014-two-cell-battery.md): the T1 runs on a two-cell series pack.** ADR 0014 sets the tree: a **TI BQ25798** buck-boost charger makes VSYS = 6.0–8.8 V; a **TPS62136** pre-regulator makes **VSYS_LV = 3.8 V** and feeds every part the 1S tree fed from VSYS, unchanged (all are rated ≤ 5.5 V, the TPS62840 6.5 V); two **TPS62903** bucks make HAT_5V / USB-C source (5.1 V) and HAT_3V3 from VSYS; a **BQ28Z610-R1** gauges the pack, which carries its own protection and balancing; a **5 A** fuse and a **Molex Micro-Fit 3.0** 4-pin connector (P+, P−, mid-cell tap, NTC) carry the battery path. The full output budget draws ≈ 2.4 A at VSYS 6.6 V instead of 4.8 A at 3.3 V, ≈ 3.2 A with full-scale headphones on top; the battery path is sized for 3.2 A (§4.7). The pack is quoted (a T1-038 exception); bring-up runs on a bench supply.

15. **v0.2: the LPDDR4X VDD1 and the VDDQ LDO bias were on a rail that is off in suspend.** The rail table put VDD1 (1.8 V) and the TPS7A1006 BIAS on vcc_1v8 (BUCK5), which the reference device trees turn off in suspend (`regulator-off-in-suspend` in `rk3566-rock-3c.dts`), while §6.5 keeps vcc_ddr and vcc0v6_ddr up for self-refresh. Every RK3566 reference keeps the DRAM 1.8 V always on: ZERO 3W v1.12 ties VCC1V8_DDR to VCCA1V8_PMU through 0 Ω (R123), Quartz64-A v2.0 through 0.1 Ω (R3807), ROCK 3C v1.4 feeds it from a dedicated LDO enabled by VCC3V3_PMU. The T1 follows the ZERO 3W (§4.8).
16. **v0.2: the Type 2EL needs a 1.8 V power rail.** AVDD18 draws 323–390 mA typical in Bluetooth and 802.15.4 transmit (Murata E2B-09-1413 Tables 20–21) and both module rails can exceed 1 A at start-up calibration (EA M.2 PA4, a carrier). It gets its own buck (vcc1v8_wl) so radio bursts stay off vcc_1v8, which feeds the DAC digital switch.
17. **v0.2: the PN7160 cannot sit on the battery path.** Its VBAT is 2.8–5.5 V in reader mode with a 6 V absolute maximum (PN7160/PN7161 data sheet Rev. 3.4, Table 1 p. 6, Table 28 p. 41); the 2S path is 6.0–8.8 V. It moves to VSYS_LV through a load switch.
18. **v0.3, [ADR 0019](../adr/0019-master-clock-divided-from-twice-the-frequency.md): the master clock is divided from twice the frequency.** The NZ2520SDA symmetry (40–60 %) can violate the CS43198's 45–55 % at XTI, and two XTI pins at 10 pF overload a weak oscillator; no passive attenuator fixes either. NSC5083D-45.158M / -49.152M on MCLK_3V1 feed one SN74AUC1G74 per DAC (divide by two), on a new 1.8 V rail **MCLK_1V8** (TPS7A2018 from AUDIO_2V2, EN = DAC_DIG_1V8), so no clock reaches an unpowered XTI. Simulated XTI duty 45.08–54.35 %, oscillator net 13.7 pF ≤ 15 pF (`sim/mclk-divider`).
19. **v0.3: vcc3v3_sys passes 80 % of the TPS62826.** The v0.2 sum missed the haptic driver (DRV2605L VDD, ≈ 0.1 A est.); with it the estimated peak is ≈ 2.45 A = 82 % of 3 A. The pin-compatible TPS62827 (4 A, SLVSEF9I) takes the rail at 61 %, with ≥ 20 µF effective output capacitance and a 6.4 A maximum current limit that the line 106 inductor carries (§4.10).
20. **v0.4, [ADR 0020](../adr/0020-battery-connected-through-contacts.md): the battery connects through contacts.** Six spring contacts (two per power pole) replace the Micro-Fit 3.0 and the pack lead, so a listener replaces the pack without a cable or a solder joint. The contacts run at 33 % of their rating on the hotter contact at 3.2 A (Micro-Fit: 64 %) but add ≈ 25 mΩ to the battery path at end of life (**UNVERIFIED**); the gauge's coulomb counter is unaffected and its cell voltages read ≤ 40 mV low per cell at 3.2 A, zero at rest (§4.7.1).

## 2. Power tree (text diagram)

Currents are design maxima (max) and estimated screen-off playback values (play). Arrows point from source to load.

```text
USB-C VBUS 5-12 V (PD sink, FUSB302B) --[TVS2200]--+
                                                   +--> TPS2121 IN1 (priority) --+
HAT VBUS (source or dual-role HAT) --[TVS0500]-----+--> TPS2121 IN2 (OV2 gate) --+--> VBUS_CHG (ILM 1.94-2.95 A, RILM 45.3 kohm 0.1 %, v0.5)
                                                                                  |
VBUS_CHG --> BQ25798 (2S buck-boost charger 1.5 MHz, NVDC; OTG NOT used; VAC1/VAC2 = VBUS, no input FETs)
   |   TPS2121 OV1 forced by USB_SRC_ON, OV2 forced by HAT_SRC_ON (hardware OR)    |
   |                                                                              |
   +--> BAT --[ship FET CSD17575Q3, SDRV (v1.6)]--[fuse 5 A]--> 6 battery contacts 70-9258 (P+ x2, P- x2, mid-cell tap, NTC; v0.4, ADR 0020) <--> made-to-order 2S1P pack (PCM + balancing; ADR 0014)
   |            P- --[sense 3 mohm, low side (v0.2, ADR 0017)]--> GND; BQ28Z610-R1 gauge (VC2, PBI = pack side after the fuse; PACK = BAT node after the ship FET; VC1 = mid-cell tap, TS1 = board NTC); pack NTC on BQ25798 TS
   +--> VSYS 6.0-8.8 V (= VBAT on battery; VSYSMIN on adapter)   full output budget 2.4 A at 6.6 V on battery (BATFET 6 A); on adapter ISW <= 2.25 A; play ~0.12-0.17 A (est.)
          |
          +--> TPS62136 VSYS_LV 3.8 V 4 A, ALWAYS ON (EN = VSYS)   ~1.6 A continuous, 2 A peak (est.)
          |     |
          |     +--> TPS62827 vcc3v3_sys 3.3 V 4 A, ALWAYS ON (EN = VSYS_LV; EXT_EN unused)   play ~0.15 A, peak ~2.45 A (est., v0.3; TPS62826 until v0.2)
          |     |         +--> RK809 VCC5-VCC9 (LDO1-9, BUCK5, SWOUT1, SWOUT2)
          |     |         +--> eMMC VCC, TPS22919 RP_3V3 (RP2354A), TCA6416A VCCP, DRV2605L VDD, INA236 x5, USB PHY 3.3 V (UNVERIFIED)
          |     |         +--> TPS22919 vcc3v3_wl (Type 2EL AVDD33), ON = expander P06 WL_PWR_EN (v0.3; was RK809 SWOUT1)  0.24 A typ TX, 1.05 A peak
          |     |         +--> TPS22950 FP_3V3, 0.22-0.38 A limit (CTP VDD, ALS, HID identity controller, faceplate logic, privacy LED) ~80 mA (v0.5; TPS22919 before)
          |     +--> RK809-5 PMIC (VCC1-VCC4 = BUCK1-4 from VSYS_LV; VCC5-VCC9 from vcc3v3_sys)
          |     |      BUCK1 vdd_logic   0.90 V  2.5 A max   play ~0.30 A (est.)          [VCC1, VSYS_LV]
          |     |      BUCK2 vdd_gpu     0.90 V  2.5 A max   off with GPU idle (DT)       [VCC2, VSYS_LV]
          |     |      BUCK3 vcc_ddr     1.113 V 1.5 A max   play ~0.10 A (est.)          [VCC3, VSYS_LV] (47k/120k, v0.2)
          |     |         +--> TPS7A1006 vcc0v6_ddr 0.60 V 0.3 A max (LPDDR4X VDDQ), play ~0.03 A; BIAS = vcc1v8_ddr (v0.2)
          |     |      BUCK4 vdd_npu     0.90 V  1.5 A max   OFF unless NPU used          [VCC4, VSYS_LV]
          |     |      BUCK5 vcc_1v8     1.80 V  2.5 A max   play ~0.10 A (est.)          [VCC9, vcc3v3_sys]
          |     |         +--> TPS22919 DAC_DIG_1V8  (2x VD+VL+VCP)       13 mA
          |     |         +--> TPS22945 FP_1V8, 100-200 mA limit (panel IOVCC, faceplate translator low side) ~5 mA (v0.5; TPS22919 before)
          |     |         +--> TPS22945 MIC_1V8, 100-200 mA limit (2x IM73D122 + privacy LED gate) ~2 mA (v0.5; TPS22919 before)
          |     |         +--> TPS22919 RP_IOVDD_1V8 (RP2354A IOVDD, 12 MHz XO)
          |     |         +--> eMMC VCCQ, Type 2EL VIO + SD_VIO, SoC VCCIO2 and VCCIO4 (v0.2: IMU and LPDDR4X VDD1 moved to vcca1v8_pmu)
          |     |         +--> 0 ohm link (ferrite-bead option) --> vccio6_1v8: SoC VCCIO6 (audio IO bank, v0.3, pinout v1 B1)
          |     |         +--> SN74LVC2G66 controls = DAC_DIG_1V8: I2C2 to the CS43198 pair only while powered (v0.2, G2)
          |     |      LDO1 vdda0v9_image 0.9 V 400 mA (CSI D-PHY: no consumer, off, v0.7)  [VCC5]
          |     |      LDO2 vdda_0v9      0.9 V 400 mA (USB/PCIe/DSI PHY)            [VCC5]
          |     |      LDO3 vdda0v9_pmu   0.9 V 100 mA (always on)                   [VCC5]
          |     |      LDO4 FP_VCI        2.8 V 100 mA design (panel VCI; adjustable per faceplate in DT) [VCC6] --> TPS22945, 100-200 mA limit, ON = FP_IO_EN (v0.5) --> contact 44
          |     |      LDO5 vccio_sd      1.8/3.3 V 400 mA (microSD signalling)      [VCC6]
          |     |      LDO6 vcc3v3_pmu    3.3 V 400 mA (always on: PMUIO1, FUSB302B; ~3.3 V less dropout from a 3.3 V feed, as on the reference) [VCC6]
          |     |      LDO7 vcca_1v8      1.8 V 400 mA (PLL, PHY analog)             [VCC7]
          |     |      LDO8 vcca1v8_pmu   1.8 V 400 mA (always on)                   [VCC7]   ~160 mA (est., v0.2, §4.13)
          |     |         +--> vcc1v8_ddr: LPDDR4X VDD1 + TPS7A1006 BIAS (link; DNP TPS7A2018 option) (v0.2)
          |     |         +--> IMU, TPM, NFC tag, PN7160 VDD(PAD), EEPROM, TCA6416A VCCI, I2C2 pull-ups, SN74LVC1G57 (MCLK gate), SN74LVC2G66 VCC (v0.2)
          |     |      LDO9 vcca1v8_image 1.8 V 400 mA (CSI D-PHY: no consumer, off, v0.7)  [VCC7]
          |     |      SWOUT1 unused (v0.3: AVDD33 moved to a TPS22919 on vcc3v3_sys)            [VCC9]
          |     |      SWOUT2 vcc3v3_sd  (microSD VDD)  3 A switch   [VCC8]  max 0.2 A
          |     |      RTC + 32.768 kHz crystal
          |     +--> TPS62869 vdd_cpu 0.85-1.15 V (I2C DVS, 0x42), 6 A   max 3 A (est.), play ~0.15 A (est.) (v0.6, ADR 0021; RK860-0 before)
          |     +--> TPS62826 vcc1v8_wl 1.8 V 3 A (EN = vcc3v3_wl, so WL_PWR_EN)  Type 2EL AVDD18: 0.39 A typ TX, 1.05 A peak (v0.2)
          |     +--> TPS22919 NFC_VBAT (PN7160 VBAT + VDD(UP))  0.29 A max, `NFC_PWR_EN` (v0.2)
          |     +--> TPS22919 DAC_VP (CS43198 VP x2)           0.1 mA play, VP first/last
          |     +--> TPS62840 AUDIO_2V2 2.2 V 750 mA max        play 16 mA
          |     |         +--> TPS7A2018 DAC1_VA 1.8 V    7.8 mA
          |     |         +--> TPS7A2018 DAC2_VA 1.8 V    7.8 mA
          |     |         +--> TPS7A2018 MCLK_1V8 1.8 V   8.9 mA, EN = DAC_DIG_1V8 --> 2x SN74AUC1G74 (one per DAC, divide by two) (v0.3, ADR 0019)
          |     +--> TPS7A2031 MCLK_3V1 3.1 V  15 mA (NSC5083D 45.1584 / 49.152 MHz, one active, other in standby; v0.3, ADR 0019); EN = AUDIO_LN_EN AND DAC_DIG_1V8 (v0.2)
          |     +--> TPS65131 boost only: AUDIO_P7V0 +7.0 V (v1.6, ADR 0015; inverter half unused)
          |     |         +--> 2x LT3045 in parallel, HPA_P6V0 +6.04 V, RILIM 523 ohm each, pair limit 516-631 mA
          |     |                  +--> 6x OPA1622 V+ (selected output only: 2 packages SE, 4 balanced)
          |     +--> MAX98357A speaker amp (VDD = VSYS_LV, SD_MODE shutdown)
          |     +--> TPS61160 backlight boost (v0.5; TPS61169 before), LEDA up to 16.5 V, <= 27 V open string, ILED 60 mA max (5S2P, 10 LEDs)
          |     +--> LP5521 RGB status LED driver (VDD = VSYS_LV, 1.5x charge pump ~4.5 V, 3 x <= 20 mA) --> faceplate RGB LED
          +--> LMR33630C inverting buck-boost (v1.6, ADR 0015): AUDIO_N7V0 -7.06 V (IC ground = -7 V; EN via level shifter)
          |         +--> 2x LT3094 in parallel, HPA_N6V0 -6.04 V, RILIM 13.0 kohm each, pair limit 519-646 mA
          |                  +--> 6x OPA1622 V-   (rail peak 433 mA, ~288 mA average at full-scale sine)
          +--> TPS62903 5.1 V 3 A, 1.6 A design (EN = HAT5V_EN OR USB_SRC_ON)
          |    +--> TPS259470 #D shared limiter (RILM 1.47 kohm: 2.021 / 2.268 / 2.520 A, v0.8)
          |         +--> TPS259470 #A (RILM 1.87 kohm: 1.589 / 1.783 / 1.981 A, v0.7) --> HAT_5V = HAT port VBUS out, TCPM source (full budget on battery with a compliant pack, §4.6)
          |         +--> TPS259470 #C (RILM 1.87 kohm, v0.7) --> USB-C VBUS source
```

## 3. Rail table

| Rail | Source | Voltage | Max current (design) | Screen-off playback (est.) | Gated by | Loads |
|---|---|---|---|---|---|---|
| VBUS_CHG | TPS2121 OUT | 5–12 V | 2.0 A (IINLIM, and ≤ 15 W; v1.2); v0.5: 1.9 A at VBUS ≤ 5.5 V; TPS2121 ILM 1.94–2.95 A hardware ceiling (RILM 45.3 kΩ 0.1 %, v0.5; was 2.0–3.0 A) | 0 (battery) | TPS2121 priority, OV pins | BQ25798 VBUS, VAC1, VAC2 (v1.5) |
| VSYS | BQ25798 SYS (v1.5, ADR 0014) | 6.0–8.8 V (= VBAT less the path drop on battery; VSYSMIN on adapter) | ≈ 2.4 A on battery at the full output budget (VSYS 6.6 V, §4.7; BATFET 6 A continuous); ISW ≤ 2.25 A on adapter (15 W input cap at VSYS 6.0 V) | 0.11–0.17 A (est., 0.20–0.30 A at 3.7 V before v1.5, scaled through the pre-regulator) | ship FET (BOM line 120); storage: charger shutdown mode (v0.2, ADR 0017) | VSYS_LV pre-regulator, HAT_5V/USB-C and HAT_3V3 bucks |
| VSYS_LV | TPS62136 (v1.5, ADR 0014; EN = VSYS) | 3.80 V (442 kΩ / 100 kΩ, VFB 0.7 V) | 4 A rating; ≈ 1.6 A continuous, 2 A peak (est.; ≈ 2.05 A with a 3 W system load and the full-scale balanced 32 Ω sine | 0.20–0.30 A (est.) | always on | Everything the 1S tree fed from VSYS: RK809-5 VCC1–VCC4, TPS62869 (v0.6; RK860-0 before), TPS62826, TPS65131, TPS61160 (v0.5; TPS61169 before), LP5521, MAX98357A, DAC_VP switch, TPS62840, TPS7A2031 v0.2: + vcc1v8_wl buck (0.22 A continuous, 0.59 A peak at its input, est.) and NFC_VBAT (0.29 A max): ≈ 2.1 A continuous, ≈ 2.9 A coincident peak (est., §4.10) |
| vdd_cpu | TPS6286910C (v0.6, ADR 0021; RK860-0 before) | 0.85–1.15 V (0.9 V at boot) | 6 A rating; 3 A (est.) design | 0.15 A (est.) | I2C DVS; EN from vcc3v3_pmu (51 kΩ + 100 nF); on in suspend | RK3566 CPU |
| vdd_logic | RK809 BUCK1 (VCC1 ← VSYS_LV) | 0.90 V | 2.5 A | 0.30 A (est.) | off in suspend | RK3566 logic |
| vdd_gpu | RK809 BUCK2 (VCC2 ← VSYS_LV) | 0.90 V | 2.5 A | ~0 (GPU idle) | DT regulator | GPU (and NPU if tied) |
| vcc_ddr | RK809 BUCK3 (VCC3 ← VSYS_LV) | 1.113 V (v0.2: FB3 divider 47 kΩ / 120 kΩ, ≈ 1.08–1.14 V worst case, §4.8) | 1.5 A | 0.10 A (est.) | on in suspend | LPDDR4X VDD2, SoC DDR_VDDQ, TPS7A1006 VIN |
| vdd_npu | RK809 BUCK4 (VCC4 ← VSYS_LV) | 0.90 V | 1.5 A | 0 | DT, off by default | NPU |
| vcc_1v8 | RK809 BUCK5 (VCC9 ← vcc3v3_sys) | 1.80 V | 2.5 A | 0.10 A (est.) | off in suspend; v0.3: stays on in suspend while radio item tracking is enabled (RK809 sleep configuration) | IO banks VCCIO2 and VCCIO4, vccio6_1v8 (VCCIO6), eMMC VCCQ, Type 2EL VIO and SD_VIO (VCCIO4 domain, pinout v1 confirms it), sub-switches (DAC_DIG_1V8, FP_1V8, MIC_1V8, RP_IOVDD_1V8). v0.2: LPDDR4X VDD1, the TPS7A1006 BIAS and the IMU moved to vcca1v8_pmu |
| vccio6_1v8 (v0.3) | vcc_1v8 through a 0603 0 Ω link (ferrite-bead option; BOM line 141) | 1.80 V | IO bank (mA class) | — | follows vcc_1v8 | SoC VCCIO6 balls 1L4 and 1L5, 100 nF each (HDG p. 32: ±5 % ripple): the audio IO bank (I2S1, PDM, audio enables) on its own branch, away from the switching currents of the eMMC and radio banks (pinout v1 B1). Bead value **UNVERIFIED**: fitted only if bring-up measures ripple above ±5 % |
| vcc0v6_ddr | TPS7A1006 (VIN vcc_ddr; BIAS vcc1v8_ddr from v0.2) | 0.60 V | 0.3 A | 0.03 A (est.) | follows vcc_ddr (EN on vcc_ddr) | LPDDR4X VDDQ, SoC DDR_VDDQL |
| vcc1v8_ddr (v0.2) | vcca1v8_pmu through a measurement link (BOM line 132; DNP TPS7A2018 option) | 1.80 V | 100 mA allowance (est., **UNVERIFIED**) | — | always on (also in suspend) | LPDDR4X VDD1, TPS7A1006 BIAS |
| vcc3v3_sys | TPS62827 (v0.3; TPS62826 v1.2–v0.2, TLV62569 before; EN = VSYS_LV, v1.5) | 3.30 V | 4 A (v0.3; 3 A before) | 0.15 A (est.) | always on (EXT_EN unused, as on the ROCK 3C) | RK809 VCC5–VCC9 (LDO1–9, BUCK5, SWOUT1, SWOUT2), eMMC VCC, RP2354A, FP_3V3, expander and translators. Peak ≈ 1.85 A (est.: BUCK5 input 0.4, LDOs 0.25, SWOUT1 0.6, SWOUT2 0.2, eMMC 0.25, rest 0.15 A) = 62 % of 3 A; in regulation down to ≈ 3.39 V input at that peak (100 % mode, BOM line 6), so always in regulation on the 3.8 V VSYS_LV (v1.5). TPS62827 (4 A) is the drop-in v0.2: the radio AVDD33 peak (1.05 A instead of 0.6 A) and the LDO8 loads raise the peak to ≈ 2.35 A = 78 % (est.); the radio's AVDD18 is no longer on this rail. **v0.3:** with the haptic driver (DRV2605L VDD ≈ 0.1 A, est.) the peak is ≈ 2.45 A (BUCK5 input 0.40, LDOs 0.30, AVDD33 switch 1.05, SWOUT2 0.20, eMMC 0.25, haptics 0.10, rest 0.15) = 82 % of 3 A, so the rail moves to the TPS62827: **61 %** of 4 A (§4.10). Also: the vcc3v3_wl switch, the INA236 ×5, the USB PHY 3.3 V supplies (B16) |
| vcc3v3_wl | TPS22919 from vcc3v3_sys (v0.3; RK809 SWOUT1 until v0.2) | 3.30 V less 95 mV at the 1.05 A peak (90 mΩ) | 1.5 A switch | 0 (radio off) | expander P06 `WL_PWR_EN` (holds through suspend; pull-down: off) | Type 2EL AVDD33 (pins 12–13): 240 mA typical transmit, 1.05 A peak (v0.2); also the EN of the vcc1v8_wl buck. Off in suspend by default; on in suspend only while item tracking is enabled (decision 2026-10-24). Supply range **UNVERIFIED** |
| vcc1v8_wl (v0.2) | TPS62826 (VSYS_LV; BOM line 129) | 1.80 V (200 kΩ / 100 kΩ) | 3 A rating; 0.39 A typical, 1.05 A design peak | 0 (radio off) | EN = vcc3v3_wl (so `WL_PWR_EN`, v0.3) | Type 2EL AVDD18 (pins 30–31) |
| vcc3v3_sd | RK809 SWOUT2 (VCC8 ← vcc3v3_sys) | 3.30 V | 3 A switch (DC table; the ROCK 3C labels both switches 2.1 A, so design to 1.5 A) | 0–0.1 A | RK809 I2C | microSD VDD |
| FP_VCI | RK809 LDO4 (VCC6 ← vcc3v3_sys) → TPS22945 (v0.5) | 2.80 V (DT-adjustable; panel absolute maximum 3.3 V) less ≤ 0.08 V across the switch at 100 mA (est.) | 100 mA design (400 mA in the DC table, 100 mA in Table 4-1); switch limit 100–200 mA (≤ 0.2 A ceiling, faceplate interface v1) | 0 (screen off) | RK809 I2C, and the switch on `FP_IO_EN` (v0.5) | panel VCI |
| vcc3v3_pmu | RK809 LDO6 (VCC6) | 3.3 V less dropout | 400 mA | — | always on | PMUIO1, FUSB302B |
| vdda0v9_pmu, vcca1v8_pmu | RK809 LDO3 (VCC5), LDO8 (VCC7) | 0.9 V, 1.8 V | 100 mA, 400 mA (LDO8: 400 mA at VIN 3.6 V, 200 mA at VIN 2 V, RK809 p. 18) | — | always on (also in suspend) | SoC PMU domain, MaskROM gates; v0.2: vcc1v8_ddr (LPDDR4X VDD1, TPS7A1006 BIAS), IMU, TPM, NFC tag, PN7160 VDD(PAD), EEPROM, expander VCCI, I2C2 pull-ups, the G2/G3 switch and gate: ≈ 160 mA (est., §4.13) |
| FP_3V3 | TPS22950 (vcc3v3_sys; v0.5, TPS22919 before) | 3.30 V | 200 mA faceplate budget; limit 0.22–0.38 A (≤ 0.4 A ceiling, faceplate interface v1) | 0 (screen off) | `FP_IO_EN` (expander P00) | CTP VDD, ALS, faceplate logic, privacy LED (the status LED runs from the LP5521, v1.2). v0.3 (decision 2026-10-24): off in suspend by default; the expander can hold it on for a faceplate that wakes the T1 |
| FP_1V8 | TPS22945 (vcc_1v8; v0.5, TPS22919 before) | 1.80 V less ≤ 0.11 V at 100 mA | 100 mA faceplate budget; limit 100–200 mA (≤ 0.2 A ceiling) | 0 (screen off) | `FP_IO_EN` | panel IOVCC, faceplate translators |
| DAC_VP | TPS22919 (VSYS_LV, v1.5) | 3.8 V | 1.5 A switch | 0.06 mA | `DAC_VP_EN` | 2× CS43198 VP |
| NFC_VBAT (v0.2) | TPS22919 (VSYS_LV; BOM line 50) | 3.8 V | 1.5 A switch; 0.29 A max load | 0 | `NFC_PWR_EN` (expander) | PN7160 VBAT, VBAT2, VDD(UP) |
| DAC_DIG_1V8 | TPS22919 (vcc_1v8) | 1.80 V | 1.5 A switch | 13.2 mA | `DAC_DIG_EN` | 2× CS43198 VD, VL, VCP v0.2: also the controls of the I2C2 isolation switch and one input of the MCLK gate |
| AUDIO_2V2 | TPS62840 | 2.20 V | 0.75 A | 25 mA (v0.3; 16 mA before) | `AUDIO_LN_EN` | three TPS7A2018 (two VA, MCLK_1V8 from v0.3) |
| DACx_VA | TPS7A2018 ×2 | 1.80 V | 0.3 A | 7.8 mA each | `AUDIO_LN_EN` | CS43198 VA |
| MCLK_3V1 | TPS7A2031 (from VSYS_LV, v1.5) | 3.10 V | 0.3 A | 15 mA | `AUDIO_LN_EN` | 2× NSC5083D (one in standby, ST pulled down) v0.2: EN = `AUDIO_LN_EN` AND DAC_DIG_1V8 (SN74LVC1G57). v0.3 (ADR 0019): 45.1584 / 49.152 MHz parts into the dividers; the attenuator is removed |
| MCLK_1V8 (v0.3) | TPS7A2018 (AUDIO_2V2; BOM line 29) | 1.80 V | 0.3 A | 8.9 mA (typ, est.) | EN = DAC_DIG_1V8 ([ADR 0019](../adr/0019-master-clock-divided-from-twice-the-frequency.md)) | 2× SN74AUC1G74 MCLK dividers (one per CS43198); the dividers run only while the DACs' VL is up |
| RP_3V3 | TPS22919 (vcc3v3_sys) | 3.30 V | 1.5 A switch | RP2354A dependent | `RP_PWR_EN` | RP2354A VREG_VIN + VREG_AVDD, QSPI_IOVDD, USB_OTP_VDD, ADC_AVDD |
| RP_IOVDD_1V8 | TPS22919 (vcc_1v8) | 1.80 V | 1.5 A switch | RP2354A dependent | `RP_PWR_EN` | RP2354A IOVDD, 12 MHz XO (≤ 2.5 mA at 1.8 V) |
| AUDIO_P7V0 | TPS65131 boost (from VSYS_LV; v1.6: boost half only, [ADR 0015](../adr/0015-amplifier-rails-from-vsys.md)) | +6.975 V | 433 mA peak, ≈ 288 mA average at the full-scale sine; boost 56–78 % of its minimum switch limit, ≈ 99 % at the positive LDOs' maximum trip (§4.10.1) | 12.7 mA (SE idle), 23 mA (balanced idle) | `HPA_RAIL_EN` (ENP) | 2 × LT3045 |
| AUDIO_N7V0 | LMR33630C inverting buck-boost (from VSYS; v1.6, [ADR 0015](../adr/0015-amplifier-rails-from-vsys.md)) | −7.06 V (100 kΩ / 16.5 kΩ) | 433 mA peak, ≈ 288 mA average; switch 47 % (sine) / 55 % (LDO limit case) of its minimum high-side limit (§4.10.1) | 12.9 mA (SE idle), 23 mA (balanced idle) | `HPA_RAIL_EN` through a level shifter to EN | 2 × LT3094 |
| HPA_P6V0 | 2 × LT3045 in parallel (v1.6; one LT3045 in v1.3–v1.5) | +6.04 V | 2 × 0.5 A; pair limit 516–631 mA (RILIM 523 Ω each) | 10.4 mA (SE idle) / 20.8 mA (balanced idle) at the amplifiers | `HPA_LDO_EN` (≥ 10 ms after `HPA_RAIL_EN`) | OPA1622 V+ |
| HPA_N6V0 | 2 × LT3094 in parallel (v1.6) | −6.04 V | 2 × 0.5 A; pair limit 519–646 mA (RILIM 13.0 kΩ each) | as HPA_P6V0 | `HPA_LDO_EN` | OPA1622 V− |
| BL_LEDA | TPS61160 (v0.5; TPS61169 before) | 13–16.5 V on the touch faceplate; ≤ 27 V open string; strings ≤ 22 V | 60 mA | 0 (screen off) | `BL_PWM` (CTRL, 1 µA off) | panel LED string |
| HAT_3V3 | Removed in v0.7 (HAT interface v2 has no 3.3 V rail; RFC 0014) | — | — | — | — | — |
| HAT_5V (out): HAT port `VBUS` | TPS62903 5.1 V (VSYS) → TPS259470 #A | 5.1 V | 1.5 A offered over USB PD; trip 1.589 / 1.783 / 1.981 A at RILM 1.87 kΩ (v0.7); on battery the full budget with a compliant pack (§4.6) | 0 | `HAT5V_EN` (expander P02) as the TCPM `vbus-supply` of the HAT port (v0.7); also forces TPS2121 OV2 | A sink HAT (interface v2) |
| LED_R/G/B | LP5521 current sources (VDD = VSYS_LV, v1.5) | ≤ 4.55 V (charge pump) | 25.5 mA per channel, 20 mA DT cap | 0 (LED off) | LP5521 CHIP_EN (I2C) | faceplate RGB status LED (v1.2) |
| USB-C VBUS (out) | TPS62903 5.1 V (v1.5) → TPS259470 #C | 5.1 V | 1.5 A offered; trip 1.589 / 1.783 / 1.981 A at RILM 1.87 kΩ (v0.7); on battery 1.5 A advertised with a compliant pack while HAT_5V is idle (§4.6) | 0 | TCPM source role → `USB_SRC_ON` (also forces OV1) | USB host mode |
| USB PHY 3.3 V (v0.3) | vcc3v3_sys (assumed) | 3.30 V | mA class (**UNVERIFIED**) | — | always on with vcc3v3_sys | SoC `USB_AVDD1_3V3`, `USB_AVDD2_3V3` supply balls (pinout v1 CSV, B16); the rail the Rockchip reference schematic uses is **UNVERIFIED** |

### 3.1 IO-domain rails (v0.3, pinout v1 B2)

From [pinout v1](pinout-v1.md) §1. A domain's supply and its software setting must match: a 1.8 V setting on a 3.3 V supply damages the pads over time, a 3.3 V setting on a 1.8 V supply makes them misbehave (HDG pp. 30–31; IO domain guide p. 2). Each supply ball takes at least one 100 nF capacitor and ±5 % ripple (HDG p. 32).

| Domain | Supply balls | Rail | Voltage | `pmu_io_domains` |
|---|---|---|---|---|
| PMUIO0 | PMUPLL_AVDD_1V8 (1N18) | vcca1v8_pmu | 1.8 V fixed | none (fixed) |
| PMUIO1 | PMUIO1 (1P16) | vcc3v3_pmu | 3.3 V fixed | none (fixed) |
| PMUIO2 | PMUIO2 (1N15) | vcca1v8_pmu | 1.8 V | `pmuio2-supply` = 1.8 V |
| VCCIO1 | 1D13 | vcc3v3_sys | 3.3 V | `vccio1-supply` = 3.3 V |
| VCCIO2 | 1C13 | vcc_1v8 | 1.8 V | none: `FLASH_VOL_SEL` high (HDG p. 19) |
| VCCIO3 | 1F17 | vccio_sd (RK809 LDO5) | 1.8 / 3.3 V | `vccio3-supply` = vccio_sd, switched by the SD driver |
| VCCIO4 | 1E16 | vcc_1v8 | 1.8 V | `vccio4-supply` = 1.8 V |
| VCCIO5 | 1N5, 1N6 | vcc3v3_sys | 3.3 V | `vccio5-supply` = 3.3 V |
| VCCIO6 | 1L4, 1L5 | vccio6_1v8 | 1.8 V | `vccio6-supply` = 1.8 V |
| VCCIO7 | 1N8 | vcc3v3_sys | 3.3 V | `vccio7-supply` = 3.3 V |

In suspend only PMUIO0–PMUIO2 keep their state and can wake the SoC (HDG pp. 17, 35, 53); vcc_1v8 (VCCIO2, VCCIO4, VCCIO6) is off unless radio item tracking keeps it on (§6.5).

## 4. Calculations

### 4.1 Headphone amplifier rails (OPA1622)

**v1.3: [ADR 0012](../adr/0012-headphone-output-stage.md)** (Accepted) replaces the v1.2 stage (four OPA1622 at ±5 V, gain 1, CS43198 at `+1dB_EN` = 1). Figures are from the ADR 0012 and are desk estimates until simulated and measured.

**Topology:**

- Six OPA1622. Every package runs both halves in parallel: one package per balanced leg (L+, L−, R+, R−) and one per single-ended channel.
- Each half is its own difference amplifier fed from the same CS43198 output pair: R1 = R3 = 1.00 kΩ, R2 = R4 = 1.62 kΩ, 100 pF across R2 and R4 (gain 1.62, pole at 982 kHz), feedback taken before a 1.0 Ω ballast resistor (BOM lines 37, 107, 108).
- CS43198 at `+1dB_EN` = 0: 1.73 Vrms full scale (4.66 Vpp minimum), −115 dB THD+N typ, −109 dB max (DS1156F2 Table 3-4).

**Limits (SBOS727B):** ≈ 100 mA peak per half at ±5 V (Table 2: 109 mA into 16 Ω, 97 mA into 32 Ω, both current-limited); swing headroom ≈ 1.9 V at ≈ 100 mA (derived from Table 2), 0.8–0.9 V at low current (§6.5). Swing against current at ±6 V is **UNVERIFIED** (Figure 38 is plotted at ±18 V).

**Expected output (est., ADR 0012):**

| Output | 16 Ω | 32 Ω | 300 Ω | Limited by |
|---|---|---|---|---|
| 3.5 mm SE | ≈ 320 mW | **≈ 240 mW** (3.92 V peak, 122 mA) | 26 mW | current at 16 Ω, DAC level × gain at 32 and 300 Ω |
| 4.4 mm balanced | ≈ 320 mW | **≈ 640 mW** (490–760 mW with imperfect sharing) | 102 mW | current (175–218 mA per leg) at 16 and 32 Ω, gain at 300 Ω |

**Supply current per rail** (sine, both channels; a rail supplies one half-cycle of each leg's current, average Ipk/π per leg):

- Quiescent: 2.6 mA per enabled half (3.3 mA max; 5 µA in shutdown). SE: 4 halves = **10.4 mA**; balanced: 8 halves = **20.8 mA** per rail. A disabled package cannot drop to one half, since its outputs are not high-impedance in shutdown (SBOS727B §7.4.1).
- SE 32 Ω full scale (122 mA peak per channel): 2 × 122 / π + 10.4 = **88 mA** per rail. SE 16 Ω (200 mA): **138 mA**.
- Balanced 32 Ω full scale (≈ 200 mA peak per leg, current limit): 2 channels × 2 legs × 200 / π + 20.8 = **275 mA** per rail. This is the design case for every part from VSYS to the amplifiers (§4.10.1).

**Thermal (est.):** per package, balanced 32 Ω full-scale sine (each leg into 16 Ω): ≈ 0.44 W at the 200 mA limit plus 0.06 W quiescent = **≈ 0.5 W**, +24 °C at θJA 47.6 °C/W (SBOS727B §6.4), the same per package as the v1.2 plan. Whole stage at the full-scale sine: ≈ 2.0 W in the four balanced packages, ≈ 0.6 W in the two LDOs, plus converter losses, ≈ 3.5 W into the body: a bench condition (music sits 10–20 dB lower). A balanced 32 Ω full-scale soak in the closed body is a prototype test.

### 4.2 Rail generator choice

| Option | Positive rail at VSYS = 3.5 V | Negative rail | Parts | Verdict |
|---|---|---|---|---|
| LM27762 alone (SNVSAF7C) | LDO from VIN: ≤ 3.5 − 0.045 = 3.45 V → swing 2.45 Vpk → 1.7 Vrms per leg | −VIN via charge pump, then LDO | 1 | **Rejected:** fails 4 Vrms balanced (needs 3.83 V) |
| Boost to 5.5 V + LM27762 | 5.0 V | −5.0 V | 2 + boost passives | Possible second option; LM27762 is the most widely available, 22 µVrms noise, 250 mA |
| TPS63710 inverter + boost | — | \|VOUT\| < 0.7 × VIN → max −2.45 V at 3.5 V in | 2 | **Rejected** for the negative rail |
| TPS65131 + TPS7A4901 + TPS7A3001 (v1.2) | +6.0 → +5.0 V | −6.0 → −5.0 V | 3 | **Removed in v1.3**: the LDOs would run at 183 % / 138 % of their 150 / 200 mA ratings at 275 mA |
| TPS65131 + LT3045 + LT3094 (v1.3, ADR 0012) | +7.0 → +6.04 V | −7.0 → −6.04 V | 3 | **Superseded in v1.6** ([ADR 0015](../adr/0015-amplifier-rails-from-vsys.md)): the inverter needs 101 % of its minimum switch limit at the full-scale peak ([output-stage simulation](../../sim/output-stage/README.md)). Was: one IC makes both pre-rails from 2.7–5.5 V, 1 µA shutdown, power-save per output (PSP/PSN); 500 mA LDOs |
| **TPS65131 boost + LMR33630C inverting buck-boost + 2 × LT3045 + 2 × LT3094** (v1.6, [ADR 0015](../adr/0015-amplifier-rails-from-vsys.md)) | +7.0 (boost, VSYS_LV) → +6.04 V | −7.06 (LMR33630C, VSYS) → −6.04 V | 6 | **Proposed**: sized for the 433 mA rail peak and the LDO current-limit case ([output-stage simulation](../../sim/output-stage/README.md)) |

TPS65131 (SLVS493E): input 2.7–5.5 V, 1.25 MHz, switch current limit 1.8 / 1.95 / 2.2 A, maximum output current given only as typical curves (Figures 6-2, 6-4). v1.3 pre-rails: VPOS = 1.213 V × (1 + 475 k / 100 k) = 6.97 V, VNEG = −1.213 V × 576 k / 100 k = −6.99 V (Eq. 1–2; BOM line 111). The need is 275 mA per rail; the margin check is in §4.10.1.

**Ripple and PSRR chain** (assume 20 mVpp switching ripple on each pre-rail, **UNVERIFIED** until the output capacitors are sized):

- Forced PWM (PSP = PSN = 0): ripple at 1.25 MHz, outside the audio band. LT3045 / LT3094 PSRR at 1 V headroom ≈ 65–75 dB / ≈ 65 dB near 1 MHz (curves G45 / G47, read from the plot) → ≤ 12 µVpp at the OPA1622 (v1.3; the TPS7A4901 gave ≥ 40 dB, ≤ 0.2 mVpp). Add a ferrite bead + 10 µF π-filter before each LDO for another 20 dB.
- Power-save (PFM bursts can land in the audio band): the v1.2 budget used the TPS7A4901's 72 dB at 120 Hz, 20 mV × 10^(−72/20) = 5 µV at the amplifier supply; the LT3045 is specified higher (117 dB at 120 Hz with CSET 4.7 µF, ≈ 110 dB at 1 kHz from curve G41; the figure with CSET 0.47 µF is not tabulated), so 5 µV stays an upper bound. The OPA1622 PSRR is 0.1 µV/V typ at DC (−140 dB); even at an assumed −100 dB in band, the residue is 0.05 nV, far below the DAC floor (0.63 µVrms, §4.3). **Conclusion: power-save mode can stay enabled during playback**, which matters for battery life. Verify by measurement.

**LDO headroom and dissipation:**

| LDO (v1.3) | In → out | Maximum dropout, full range (datasheet) | Headroom | Pd at idle (SE, 10.4 mA) | Pd at 275 mA |
|---|---|---|---|---|---|
| LT3045 (Rev. D) | +7.0 → +6.04 V | 350 mV at 300 mA | ≈ 0.96 V | ≈ 25 mW | ≈ 0.34 W (+12 °C at 34 °C/W) |
| LT3094 (Rev. B) | −7.0 → −6.04 V | 280 mV at 100 mA, 410 mV at 500 mA | ≈ 0.96 V | ≈ 27 mW | ≈ 0.33 W |

Ground currents: LT3045 2.2 mA typ at 10 µA load, 4.3 mA typ (7 mA max) at 100 mA in dropout; LT3094 2.35 mA typ, 3.8 mA typ (6.5 mA max) at 100 mA in dropout. Pd at idle counts the ground current at 7 V. The TPS65131 3 % output accuracy and the ±2 % SET current leave ≥ 0.7 V of headroom (est.), above the dropout. PSRR is specified at 2 V headroom; the 1 V curves above are the design basis.

**Ramp symmetry (v1.3, D30).** The OPA1622 wants V+ and V− to ramp symmetrically with EN held low (SBOS727B §7.4.2). The LT3045 and LT3094 share the soft-start law tSS ≈ 2.3 × RSET × CSET (LT3045 Rev. D p. 19, LT3094 Rev. B p. 22): with RSET 60.4 kΩ and CSET 0.47 µF on both, each rail ramps on the same RC curve in ≈ 65 ms. Fast start-up is disabled (PGFB tied to IN), because its SET currents differ (2 mA and 1.8 mA typ). Both EN/UV pins share the 3.3 V `HPA_LDO_EN` net, raised after the TPS65131 pre-rails settle (`HPA_RAIL_EN` first), so the LDO soft-start alone sets the ramp. The residual mismatch is the CSET tolerance: a bring-up measurement. The v1.1 TPS7A4901/TPS7A3001 sizing (CNR/SS 10 nF / 15 nF, D3) no longer applies.

**Rejected positive LDOs:** TPS7A94 (15 mA ground current, §1); TPS7A2050 (VIN absolute maximum 6.0 V, below the +7 V pre-rail of v1.3); TPS7A4901 (150 mA, removed in v1.3).

### 4.3 DAC analog rails: noise budget versus PSRR

- DAC noise floor: 130 dB A-weighted dynamic range re 2 Vrms → 2 × 10^(−130/20) = **0.63 µVrms**.
- CS43198 VA PSRR: 75 dB at 217 Hz (DS1156F2, Table 3-15; the only point given).
- TPS7A2018 output noise 7 µVrms (SBVS338H). Coupled to the output: 7 µV × 10^(−75/20) = **1.2 nV**, 54 dB below the floor. Even with PSRR falling to 40 dB at 20 kHz: 70 nV, still 19 dB below.
- **Conclusion:** an ultra-low-noise LDO (LT3042 class, 0.8 µVrms, about 2 mA Iq) buys nothing measurable on VA; the TPS7A2018 costs 6.5 µA quiescent. One LDO per DAC keeps dual mono independent.

**DAC power (Table 3-17, PCM playback, VA = VCP = VD = VL = 1.8 V, VP = 3.6 V):** VCP 3.808 mA, VA 7.835 mA, VD 2.786 mA, VP 0.028 mA, **26.1 mW per DAC**. Standby (HP detect on) 0.58 mW; off (VP only) 11 µW.

**Efficiency of the 1.8 V analog path** (two DACs' VA = 15.7 mA at 1.8 V = 28 mW; the MCLK now runs at 3.3 V from VSYS, see the clocks row):

| Feed | Chain efficiency | Battery power |
|---|---|---|
| LDO straight from VSYS (3.8 V) | 1.8 / 3.8 = 47 % | 117 mW |
| TPS62840 2.2 V (~90 %, **UNVERIFIED** at 31 mA) + LDO (1.8 / 2.2 = 82 %) | 74 % | 75 mW |

The pre-buck saves about **42 mW**, roughly 4–6 % of screen-off playback power. TPS62840 has 60 nA Iq and 25 nA shutdown (SLVSEC6D). v1.5: the TPS62840 input is VSYS_LV, a fixed 3.8 V, so the table's first row is now exact; the battery-side figures grow by the pre-regulator efficiency (≈ 0.88–0.92, est.).

### 4.4 Master clocks

- NZ2520SDA: 15 mA operating, 35 µA standby, **tri-state output in standby** (NDK catalog 1703A). Both oscillator outputs can therefore share one MCLK net to the two DACs, with exactly one enabled: no clock multiplexer in the path.
- Phase noise at 1.8 V: 22.5792 MHz −158 dBc/Hz at 1 kHz, −163 at 100 kHz; at 3.3 V −164 / −169 (NDK catalog). The 1.8 V version is about 6 dB worse close-in; it is still an audio-grade XO (the CS43198 PLL, which is bypassed here, only asks for < 50 ps reference jitter). Whether the 6 dB is audible or measurable is for an A/B measurement.
- Power (v1.1, MCLK_3V1): 15 mA maximum at 3.1 V = 47 mW at the oscillator, 15 mA × VSYS ≈ 56 mW from the battery at 3.7 V through the LDO (v1.5: 15 mA × 3.8 V VSYS_LV / 0.9 ≈ 63 mW, est.). The idle family costs 35 µA. The 15 mA is the catalogue maximum; the typical figure is not given.
- Phase noise is characterised at 3.3 V (−164 dBc/Hz at 1 kHz, 22.5792 MHz). The figure at 3.1 V and the 24.576 MHz figure are **UNVERIFIED** until the J-test captures (ADR 0010).
- **v0.3 ([ADR 0019](../adr/0019-master-clock-divided-from-twice-the-frequency.md)):** the oscillators run at 45.1584 and 49.152 MHz and one SN74AUC1G74 per DAC divides by two, so the duty at XTI comes from the divider, not the oscillator (simulated 45.08–54.35 %, `sim/mclk-divider`). NDK catalogues 49.152 MHz at −158 / −172 dBc/Hz (1 kHz / 100 kHz) and 43 fs; after an ideal division −164 / −178 dBc/Hz. With the divider estimates (**UNVERIFIED**: TI publishes no additive jitter for the AUC family) the budget is −157.9 / −159.0 dBc/Hz, 55.9 / 43.0 dB under the CS43198 mask; RMS jitter 73 fs against the 46.3 ps the mask allows.
- **v0.3 power:** the oscillator maximum stays 15 mA at MCLK_3V1. The dividers draw ≈ 8.9 mA at 1.8 V (typical Cpd 44 pF, SCES537D p. 5) from MCLK_1V8, ≈ 20 mW at AUDIO_2V2; the attenuator's ≈ 6.5 mW goes: ≈ +13 mW in playback (est.).

### 4.5 Backlight (Focus E35GH-I-MW800-CB)

From the Focus spec sheet (rev 1.0): 10 LEDs, edge-lit, IF 60 mA, VF 14.0 / 15.0 / 16.5 V (min/typ/max), so 5 in series × 2 parallel strings, single LEDA/LEDK pair. Panel VCI 2.5–3.3 V (2.8 V typ), IOVCC 1.65–3.3 V (1.8 V typ). CTP normal current 8 mA typ, 14.5 mA max.

TPS61169 (SNVSA40B; until v0.4): 2.7–5.5 V in, 1.2 MHz, 1.2 A minimum switch limit, 204 mV reference, 37.5 V OVP, 1 µA shutdown.

- Sense resistor: R = 0.204 V / 0.060 A = **3.40 Ω** (1 %, 12 mW).
- Full brightness: Pout = 16.5 V × 60 mA = 0.99 W (max VF). At VIN = 3.5 V and η = 85 %: Iin = 0.99 / (3.5 × 0.85) = 0.33 A. v1.5: VIN is the 3.8 V VSYS_LV, so 0.31 A and a lower peak; the 3.5 V figures below stay as the conservative case.
- Duty cycle: D = 1 − VIN·η / VOUT = 1 − 3.5 × 0.85 / 16.5 = 0.82.
- Ripple with L = 10 µH, f = 1.2 MHz: ΔIL = VIN·D / (L·f) = 3.5 × 0.82 / (10 µH × 1.2 MHz) = 0.24 A → peak 0.33 + 0.12 = **0.45 A < 1.2 A**. A 10 µH, ≥ 0.6 A saturation inductor (Murata LQH3NPN100MJRL class) and a 60 V, 1 A Schottky (Nexperia PMEG6010CEH, BOM v1.1; the 40 V PMEG4010CEH left 1 V over the 39 V OVP maximum) suffice.
- Indoor 200 nit: about 15 mA if luminance is linear in current (**UNVERIFIED**), VF about 13.5 V (est.) → 0.20 W out, about 0.25 W from the battery. Full 800 nit outdoors: about 1.1 W.
- Dimming: PWM on CTRL scales the internal reference (analog dimming of the LED current, flicker-free), driven by the ALS through Blackbird OS (`pwm-backlight`, Debian `=m`).
- Placement: on the main board, so the faceplate FPC carries LEDA/LEDK. 37.5 V OVP covers strings up to about 10 series LEDs, so other faceplates need no board change (BRD-048). *Superseded in v0.5 (below): the FH35C's 30 V rating caps BL_LEDA.*
- **v0.5 (t1 faceplate interface v1 §2.3, t1 ADR 0005): TPS61160** (SLVS791E): 2.7–18 V in, 600 kHz (500–700 kHz), switch limit 0.56 / 0.7 / 0.84 A at Dmax, 200 mV reference (196–204 mV), open-LED threshold **25 / 26 / 27 V** at SW. An open string holds BL_LEDA at ≤ 27 V (minus the rectifier drop), below the FH35C's 30 V rating in every state; the TPS61169's 36–39 V did not. Strings stay ≤ 22 V at their maximum current (25 V − 3 V).
  - Sense resistor: 0.200 V / 0.060 A = 3.33 Ω → **3.32 Ω** 1 % (60.2 mA, 12 mW).
  - Maximum output current (SLVS791E Equations 3, 4) at VIN 3.8 V, worst case ILIM 0.56 A, fS 500 kHz, η 0.85 (est.), rectifier 0.4 V: with 10 µH 51 mA at a 16.5 V string, below the 60 mA full scale, so the inductor becomes **22 µH** (TI's 10–22 µH range): 82 mA at 16.5 V (60 mA = 73 %), 75 mA at 18 V (80 %), 61 mA at 22 V (99 %). A faceplate whose string exceeds 18 V declares a lower full-scale current until a VSYS-fed driver is studied (§8).
  - Ripple at 16.5 V and 60 mA, 22 µH, 500 kHz: Iin = 16.7 × 0.06 / (3.8 × 0.85) = 0.31 A, ΔIL = 0.27 A, peak **0.44 A** = 79 % of the 0.56 A minimum limit and 82 % of the LQH3NPN220MMEL's 0.54 A rating (**UNVERIFIED**).

### 4.6 HAT power: eFuse current limits and inrush

**v0.8 (RFC 0015):** eFuse #D, a shared limiter between the 5.1 V buck and #A and #C, bounds both ports together to 2.520 A (84 % of the buck's rating): [Changes in v0.8](#changes-in-v08) item 1.

**v0.7 (hat-standard interface v2, RFC 0014):** the HAT port has one power net, `VBUS` (board net `HAT_5V`), under USB PD: 3.0 A continuous, 4.5 A fault ceiling. eFuse #A and #C move to **RILM 1.87 kΩ 1 %** (1.589 / 1.783 / 1.981 A), so the 1.5 A offer sits below the minimum trip; eFuse #B and `HAT_3V3` are removed. The figures and the dual-role, dead-battery and discharge behaviour are in [Changes in v0.7](#changes-in-v07) items 2–7. The v0.5 tables below keep their values for traceability; where they differ, v0.7 holds.

TPS259470 (SLVSFC9C): 2.7–23 V, RON 28.3 mΩ, ILIM set by RILM (1.65 kΩ → 2.03 A, 3.32 kΩ → 1.007 A, so ILIM ≈ 3,350 Ω·A / RILM; Equation 7 gives 3,334), reverse-current blocking, IMON.

**v0.5, hat-standard interface v1.1 §5 (ADR 0005):** the interface fault ceilings are `HAT_5V` 3.0 A (either direction), `HAT_3V3` 1.5 A, `GND` 4.5 A, and a device's limiter must stay inside them at its maximum trip, tolerance included. The T1's limiters, with the RILM tolerance:

| Limiter | Rail | Setting | Maximum trip | Of the ceiling | Basis |
|---|---|---|---|---|---|
| eFuse #A | `HAT_5V` out | 2.21 kΩ 1 % | 3,334 / 2,188 Ω = 1.524 A + 10 % = **1.68 A** | 56 % | SLVSFC9C Equation 7, §6.5 (±10 % above 1 A) |
| TPS2121 IN2 | `HAT_5V` in (class F) | **45.3 kΩ 0.1 %** (was 44.2 kΩ 1 %) | 65.2 / 45.25^0.861 = 2.448 A + 0.5 A = **2.95 A** | 98 % | SLVSEA3F Equation 2; ±0.5 A at every characterised value (§7.5), assumed at 45.3 kΩ (**UNVERIFIED**). At 44.2 kΩ 1 %: 3.02 A, 101 % |
| eFuse #B | `HAT_3V3` | 3.32 kΩ 1 % | 1.150 A × 3.320 / 3.287 = **1.16 A** | 77 % | SLVSFC9C §6.5 row at 3.32 kΩ; removed in v0.7 |
| — | `GND` return | — | 2.95 + 1.16 = **4.11 A** (`HAT_5V` in and out never together, OV2 interlock) | 91 % | arithmetic |

Transients above these values are bounded and short: the eFuse's scalable fast trip at 2 × ILIM ends any excess within its response, with ITIMER left open for the shortest blanking (SLVSFC9C §7.3.5); the TPS2121's fast trip at ≈ 2.4 × ILM acts within 1 µs (SLVSEA3F §9.3.3). Neither heats a contact whose rating is set by temperature rise.

The TPS2121 minimum moves to 2.45 − 0.5 = 1.94 A, below the 2.0 A IINDPM that charging used, so IINDPM becomes 1.9 A at VBUS ≤ 5.5 V (§4.7).

| eFuse | Path | ILIM target | RILM | Conduction loss at ILIM |
|---|---|---|---|---|
| #A | TPS62903 5.1 V (v1.5; was TPS61089) → HAT_5V | 1.5 A | 1.87 kΩ (1.783 A typical, v0.7; was 2.21 kΩ) | 28.3 mΩ × 1.783² = 90 mW |
| #B | Removed in v0.7 (was TPS62903 3.3 V → HAT_3V3, 3.32 kΩ) | — | — | — |
| #C | TPS62903 5.1 V (v1.5) → USB-C VBUS | 1.5 A | 1.87 kΩ (v0.7; was 2.21 kΩ) | 90 mW |

- **Source (v1.5, ADR 0014):** a **TPS62903 buck from VSYS** (6.0–8.8 V) feeds #A and #C at 5.1 V (VSET 95.3 kΩ), and a second TPS62903 feeds #B at 3.3 V. The BQ25798 OTG converter cannot run while charging, as the BQ25895's could not (finding 9). Design output 1.6 A at 5.1 V = 53 % of the 3 A rating; HAT_3V3 1.0 A = 33 %. Inductor peak at 1.6 A, VIN 8.8 V, 1 µH − 20 %, 2.5 MHz: ΔIL = 5.1 × (1 − 5.1 / 8.8) / (0.8 µH × 2.5 MHz) = 1.07 A, peak 2.14 A, 24 % of the XGL4020-102MEC's 8.8 A (30 % drop). If software lets both eFuses reach their 1.66 A ceilings (3.3 A), the buck's 4.0 / 4.6 / 5.5 A high-side limit bounds the fault (SLVSES3A §6.5); the 5.5 A maximum plus its 50 ns overshoot (≈ 5.7 A) stays below the inductor's 8.8 A. 100 % mode keeps 5.1 V at 1.6 A down to VSYS ≈ 5.29 V, below the 6.0 V minimum. On adapter power only HAT_5V can be sourced (the USB-C port is then the input). The buck also covers the case the draft missed: a class A/B HAT keeps 5 V while the T1 charges.
- **Before v1.5:** a TPS61089 boost from VSYS feeds #A and #C (the BQ25895 OTG boost cannot run while charging, finding 9). Sizing (SLVSD38C): on adapter power only HAT_5V can be sourced (1.5 A); on battery HAT_5V and USB-C source share ≈ 0.4 A with the interim pack and the full 1.5 A with an ADR 0011 pack (below). Design output 1.6 A at 5.1 V. At VIN = 3.0 V and η = 0.88 the input current is 5.1 × 1.6 / (3.0 × 0.88) = 3.1 A; with 1.5 µH at 1 MHz and D = 1 − 3.0 × 0.88 / 5.1 = 0.48, ΔIL = 3.0 × 0.48 / (1.5 µH × 1 MHz) = 0.96 A, so the peak is 3.6 A. With TI's L − 30 % (1.05 µH) the ripple is 1.18 A and the peak 3.7 A. v1.2: the limit can sit up to 0.8 A below the calculated value (SLVSD38C §9.2.2.3), so the v1.1 RILIM of 200 kΩ (5.15 A typ) gave 4.35 A minimum and the peak sat at 85 % of it. **RILIM = 182 kΩ** sets ILIM = 1,030,000 / 182,000 = 5.66 A typ, 4.86 A minimum: the peak is 76 %. The XAL4020-152 (Isat 7.1 A typ) is above the typical limit; the maximum limit at 182 kΩ is not specified (≈ 6.5 A if the spread is symmetric, **UNVERIFIED**). If software lets both eFuses reach their 1.5 A ceilings on battery, the boost current limit bounds the fault. On adapter power only HAT_5V can be sourced (the USB-C port is then the input), so #A at 1.5 A (≈ 8.5 W from VSYS at η ≈ 0.9) fits inside the 3.5 A VSYS rating with the system load. The boost also covers the case the draft missed: a class A/B HAT keeps 5 V while the T1 charges.
- **Full output budget (v1.2, BRD-050):** the same on battery as on adapter power: 1.5 A at 5.1 V shared by HAT_5V and the USB-C source (one 5.1 V converter, 1.6 A design), plus HAT_3V3 at 1.0 A. Serving both 5 V ports at 1.5 A together is not in the budget: at 1S it would have needed ≈ 7.3 A from the battery, above the BQ25895's 6 A. The battery current is derived in §4.7: v1.5 (2S) ≈ 2.4 A at VSYS 6.6 V.
- **Battery budget with the interim pack (v1.1; v1.5: no longer applies, ADR 0014 removes the interim pack; with a compliant 2S pack HAT_5V and the USB-C source get the full budget on battery):** on battery the derated JST PH path caps the pack at 1.6 A ≈ 5.6 W at 3.5 V. With the base system at 1–3 W (screen off to screen on with CPU load, **est.**), about 2.6 W remains: ≈ 2.6 × 0.9 / 5.1 = 0.46 A, taken as **0.4 A** at 5.1 V for HAT_5V **plus** USB-C source together. Blackbird OS enforces it with the VSYS INA236 and the eFuse IMON; USB-C advertises Default (0.5 A) on battery. HAT power classes A/B must be written against this number until an ADR 0011 pack is fitted (hat-standard). With such a pack, USB-C advertises 1.5 A on battery while HAT_5V is idle.
- **Hardware ceilings stay** at ILIM 1.5 / 1.0 / 1.5 A (maximum trip 1.66 / 1.15 / 1.66 A, SLVSFC9C §6.5; v0.5 with the 1 % RILM tolerance: 1.68 / 1.16 / 1.68 A, table above) so a fault is still bounded if software fails.
- **HAT power connector (v0.5, hat-standard interface v1.1): the DF40C-50 pair is removed**; power shares the single DF40C-100 pair: `HAT_5V` × 10, `HAT_3V3` × 5, `GND` × 15 at 0.3 A each (DF40 catalog 2020 p. 2). Continuous 2.0 / 1.0 / 3.0 A = 0.20 A per contact (67 %); at the interface ceilings 3.0 / 1.5 / 4.5 A = 0.30 A (100 %); at the T1's own trips `HAT_5V` 1.68 A out = 56 %, 2.95 A in = 98 %, `HAT_3V3` 1.16 A = 77 %, `GND` 4.11 A = 91 %. *Until v0.4:* **HAT power connector (v1.2):** a DF40 50-contact pair (HAT_5V ×12, HAT_3V3 ×6, GND ×22), allocated by the hat-standard HAT interface v0 and unchanged in v1. At 0.3 A per contact: HAT_5V 2.0 A continuous = 0.17 A per contact (56 %), HAT_3V3 1.15 A = 0.19 A (64 %), returns 2.0 + 1.15 A = 0.14 A (48 %); the worst fault ceiling, 3.0 A from a class F HAT through the TPS2121 ILM, is 0.25 A per contact (83 %, ≤ 100 %). The v1.1 30-contact pair put HAT_3V3 at 96 % (1.15 A on 4 contacts).
- **Inrush:** with CdVdt = 1.8 nF the rising slew is 0.87 V/ms at 2.7 V and 1.09 V/ms at 12 V; take 0.92 V/ms at 5 V. A HAT with 100 µF bulk draws I = C·dV/dt = 100 µF × 920 V/s = **92 mA** for 5.4 ms; 470 µF draws 0.43 A, still under ILIM. The HAT standard should cap HAT bulk capacitance at 470 µF per rail.
- **Powerbank HAT input (class F; v0.7: a source or dual-role HAT under USB PD, [Changes in v0.7](#changes-in-v07) items 4–6):** HAT_5V → TPS2121 IN2. When the T1 sources HAT_5V, `HAT_SRC_ON` (the same net that enables #A) drives TPS2121 OV2 high so IN2 cannot connect; when it sources USB-C VBUS, `USB_SRC_ON` drives OV1 high. The interlock is wired, not a software ordering rule.

### 4.7 Charger, battery and input path

- **Charger (v1.5, [ADR 0014](../adr/0014-two-cell-battery.md)): BQ25798** (SLUSDV2C): VBUS 3.6–24 V, IVBUS ≤ 3.3 A, ISW ≤ 5 A, charge ≤ 5 A, battery discharge 6 A RMS continuous and 10 A for ≤ 1 s, IBAT_OCP 9.3 A minimum, BATFET 11 mΩ (§6.3, §6.5). 1.5 MHz with a 1 µH inductor (XAL4020-102MEC, BOM line 40), SYS 5 × 10 µF + 0.1 µF. VREG 8.40 V for 4.2 V cells, up to 2 × 4.40 V for LiHV in 10 mV steps (ADR 0008); charge current per pack. Battery-only quiescent 17 µA typ (BATFET on, ADC off), 11 µA in ship mode, 0.5 µA in shutdown. OTG not used.
- **Pack (v1.5):** a made-to-order 2S1P pack accepted against ADR 0014 item 2: ≥ 4.0 A continuous, PCM trip 4.0–5.0 A with cell balancing, contact interface ≥ 4.6 A per pole (v0.4, ADR 0020 item 3; was lead and Micro-Fit plug), UN 38.3 (IEC 62133-2 for the Commercial edition), 4.2 V or LiHV cells. v0.4 ([ADR 0020](../adr/0020-battery-connected-through-contacts.md)): it connects through six spring contacts on the board (KYOCERA AVX 70-9258-001-120-006: P+ ×2, P− ×2, mid-cell tap, NTC) pressing on recessed hard-gold pads of the pack's terminal board, with no lead or plug (was a 4-pin Micro-Fit 3.0); the BQ28Z610-R1 reads both cells (VC2 at BAT+, VC1 at the tap) and the BQ25798 TS takes the pack NTC. No available pack meets the criteria; bring-up uses a bench supply or a protected 2S pack on the bench. The Adafruit 328 is no longer a T1 pack.
- **Full output budget on battery (v1.5, BRD-050, ADR 0014).** Loads at VSYS = 6.6 V (3.3 V per cell), below which Blackbird OS sheds HAT and USB-C source load through the gauge:

  | Load | Output | Efficiency | From VSYS |
  |---|---|---|---|
  | TPS62903, HAT_5V + USB-C source | 5.1 V × 1.6 A = 8.16 W | 0.93 (est.) | 8.77 W |
  | TPS62903, HAT_3V3 (removed in v0.7) | — | — | — |
  | System, screen on with CPU load, through the TPS62136 | 3.0 W (est.) | 0.92 (est.) | 3.26 W |
  | **Total** | | | **12.0 W → 1.82 A at 6.6 V** (v0.7; 15.7 W → 2.38 A with HAT_3V3 until v0.6) |

  Every element of the battery chain is sized for the worst continuous case of ≈ 3.2 A (next bullet; ADR 0014): pack ≥ 4.0 A continuous (80 %), PCM trip 4.0–5.0 A, contact interface ≥ 4.6 A per pole (70 %; v0.4, ADR 0020: was the pack lead and plug); on the board, two 6 A contacts per pole (v0.4: 33 % on the hotter contact, 25 % at 2.4 A, §4.7.1; was 5 A per Micro-Fit contact with the 43030-0001 crimp, 64 %), the 5 A fuse (64 %, 0451005.MRL), the BQ25798 battery discharge rating 6 A (53 %; IBAT_OCP 9.3 A minimum), the 10 mΩ VSYS shunt (0.10 W) and the 3 mΩ gauge sense resistor (31 mW, 12 % of 0.25 W; v0.2, ADR 0017; 51 mW with the 5 mΩ of v1.5–v1.7). Path resistance ≈ 65 mΩ (v0.4: BATFET 11 mΩ, fuse 12.5 mΩ cold, sense 3 mΩ, shunt 10 mΩ, ship FET 3.2 mΩ max, battery contacts ≈ 25 mΩ for both poles at end of life, **UNVERIFIED**; est.; ≈ 38–48 mΩ with the Micro-Fit until v0.3) → ≈ 0.16 V and ≈ 0.37 W at 2.4 A, ≈ 0.21 V and ≈ 0.66 W at 3.2 A, against ≈ 0.24 V and ≈ 1.15 W at 4.8 A for 1S. The cell pair must hold ≈ 6.8 V under load for VSYS = 6.6 V (≈ 6.7 V until v0.3).
- **Headphones on top of the full budget (v1.5, resolved: BOM §7 item 17; recomputed in v1.6).** The 3.0 W system term includes no full-scale headphone stage. v1.5 counted the full-scale balanced 32 Ω sine as ≈ 4.8 W at VSYS_LV, ≈ 5.2 W from VSYS, everything together ≈ 20.9 W → ≈ 3.2 A at 6.6 V. **v1.6 (ADR 0015):** the −7 V rail draws from VSYS through the LMR33630C, 2.12 W at the full-scale sine (simulated at VSYS 6.0 V, ≈ 288 mA average per rail); the +7 V rail stays on the TPS65131 boost from VSYS_LV, 7 V × 0.288 A / 0.8 ≈ 2.52 W, ≈ 2.74 W from VSYS. Headphones ≈ 4.86 W from VSYS; everything together ≈ 8.77 + 3.67 + 3.26 + 4.86 = **≈ 20.6 W → ≈ 3.1 A at 6.6 V** (≈ 2.8 A with the 1.0 W screen-off system load). **The 3.2 A design point and the 5 A fuse hold** (fuse 62 %, pack criterion 78 %, Micro-Fit contact 62 %, BQ25798 52 %); path drop ≈ 0.14 V. v0.4 (ADR 0020): battery contact 32 % on the hotter contact, path drop ≈ 0.20 V with the contacts at end of life (est.). The pre-regulator carries (3.0 + 2.52) W / 3.8 V ≈ 1.45 A (36 % of 4 A). A fault that holds both LDO pairs at their maximum trip (≈ 0.65 A per rail: LMR33630C ≈ 5.9 W in, boost ≈ 6.2 W from VSYS) is not a continuous case; with everything else at full budget it would reach ≈ 4.2 A (84 % of the fuse), where the pack PCM (4.0–5.0 A) may act, as intended. **Decision (ADR 0014):** the battery path covers this case: pack ≥ 4.0 A continuous, PCM trip 4.0–5.0 A, lead and plug ≥ 4.6 A per pole, 5 A fuse (64 %), Micro-Fit contact 64 %, BQ25798 53 % (v0.4, ADR 0020: contact interface ≥ 4.6 A per pole, battery contact 33 %). No output limit follows from the battery. v1.6: the −7 V inverter is replaced by the LMR33630C ([ADR 0015](../adr/0015-amplifier-rails-from-vsys.md)).
- **Storage and the off state (v0.2, [ADR 0017](../adr/0017-fuel-gauge-wiring-sense-resistor-and-configuration.md)).** The gauge's PACK pin sits on the BQ25798 BAT node, on the switched side of the ship FET (BOM line 120); VC2, PBI, VC1 and the 3 mΩ sense resistor stay on the pack side. For storage and at a critical-battery power-off, Blackbird OS (no adapter present) sends gauge MAC 0x0010 twice and then sets BQ25798 SDRV_CTRL = 01 (shutdown mode, wake on adapter): **board drain ≈ 1 µA typical, 4.7 µA maximum** (gauge SHUTDOWN 0.5 / 2 µA, charger ISD_BAT 0.5 / 0.7 µA, ship FET IDSS ≤ 1 µA, PACK leakage ≤ 1 µA), against a target of ≤ 5 µA and a hard limit of 15 µA (ADR 0017 §1). Ship mode (SDRV_CTRL = 10) costs up to 20 µA and is not used for storage. With the T1 off but not in storage (ship FET on, charger idle), the gauge sits in SLEEP at ≈ 100 µA typical (≈ 0.74 mW at 7.4 V), plus RPACK(PD) (30–50 kΩ) if it is connected permanently (**UNVERIFIED**, ADR 0017 item 6).
- **Input limits (v1.5).** BQ25798 IVBUS is rated 3.3 A and ISW 5 A (SLUSDV2C §6.3). IINLIM ≤ 2.0 A and VBUS × IINLIM ≤ 15 W keep IVBUS at 61 % (TPS2121 ILM 3.0 A maximum = 91 %; v0.5: IINDPM 1.9 A at VBUS ≤ 5.5 V, because the TPS2121 minimum is now 1.94 A, §4.6; IINDPM regulates at or below its setting, 1.80–1.96 A at 2.0 A, SLUSDV2C §6.5, so ≈ 1.86 A at most at 1.9 A, est.; ILM maximum 2.95 A = 89 %) and ISW ≤ 15 W × 0.9 / 6.0 V = 2.25 A (45 %). Charging a ≈ 1.5 Ah 2S pack at 0.5C is ≈ 0.75 A × 8.4 V ≈ 6.3 W, inside the 15 W cap with the system load.
- Input: PD sink at 9 V; v1.2 requests 1.65 A (15 W, see input limits above) against about 7.3 W needed for charging (1.5 A × 4.2 V charge + 1 W system; v1.5: ≈ 6.3 W + 1 W for a 2S pack at 0.75 A, est.). TPS2121 conduction loss at 2 A input: 56 mΩ typ → 0.22 W; 100 mΩ maximum over −40 to 125 °C (SLVSEA3F §7.5) → 0.40 W, a 29 °C rise at RθJA 72.2 °C/W (JEDEC board; check in the board thermal model).
- TPS2121 OV1 (BOM v1.1, one value): R1 = 1.02 MΩ, R2 = 100 kΩ (1 %), VTRIP = VREF × (1 + R1/R2) = 1.06 × 11.2 = 11.9 V typ; 11.1–12.6 V over VREF 1.01–1.1 V and resistor tolerance. That is above a 9 V PD contract (9.45 V at +5 %) and below the BQ25895 14 V operating maximum (v1.5: the BQ25798 operates to 24 V).
- USB-C VBUS surge: TVS2200 (22 V flat clamp, 28.4 V max at 40 A 8/20 µs). The TPS2121 (24 V absolute maximum, OV1 at 11.9 V) sits between the connector and the BQ25895 (22 V absolute maximum). A 40 A surge clamp of 28.4 V exceeds both ratings, so the TVS is sized for ESD and hot-plug ringing, not for an IEC 61000-4-5 surge (**risk**, §9). v1.5: the BQ25798 VBUS absolute maximum is 30 V (SLUSDV2C §6.1), above the 28.4 V clamp; the TPS2121 (24 V) remains the limiting part.

**Before v1.5 (1S, superseded by ADR 0014; kept for traceability):**

- BQ25895: 3.9–14 V input, 5 A charge, 1.5 MHz, 1 µH inductor and ≥ 20 µF on SYS recommended (SLUSC88C §9). PMID capacitance per the datasheet for charge-only use (OTG is not used).
- Battery-only quiescent: 32 µA typ with BATFET on and monitor off (12 µA with BATFET off, ship mode).
- Pack: Adafruit 328 (ADR 0007), spec sheet Q/WAPL785060-1011: charge ≤ 1C (2.5 A) at 0–40 °C and ≤ 4.25 V, discharge ≤ 2C. Charge current 1.2 A (Adafruit's advice), VREG 4.20 V; LiHV packs later at 4.35/4.40 V from the device tree (ADR 0008). The TS thresholds must stop charging above 40 °C (the BQ25895 default hot limit is higher, **UNVERIFIED** exact value).
- Battery current (v1.1): JST rates the PH contact 2 A AC/DC with AWG #24 wire (ePH catalog) and gives no figure for the 26 AWG leads of the Adafruit 328. Assuming the rating is set by heating of the crimp and wire, equal I²R per length scales the current by √(A26 / A24) = √(0.129 / 0.205) = 0.79, so the budget is **1.6 A continuous** (est.). The VSYS INA236 enforces it in software; a JST or Adafruit 26 AWG figure would restore 2 A. From v1.2 a 2.5 A NANO2 fuse in BAT+ (BOM line 104) bounds a sustained overload in hardware: 1.6 A is 64 % of it.
- **Full output budget on battery (v1.2, BRD-050, proposed ADR 0011).** Loads at VSYS = 3.3 V, below which Blackbird OS sheds HAT and USB-C source load through the gauge:

  | Load | Output | Efficiency | From VSYS |
  |---|---|---|---|
  | TPS61089, HAT_5V + USB-C source | 5.1 V × 1.6 A = 8.16 W | 0.88 (curve, **UNVERIFIED**) | 9.27 W |
  | TLV62569, HAT_3V3 | 3.3 V × 1.0 A = 3.3 W | 0.90 (**UNVERIFIED**) | 3.67 W |
  | System, screen on with CPU load | — | — | 3.0 W (est.) |
  | **Total** | | | **15.9 W → 4.8 A at 3.3 V** |

  Every element of the battery chain must carry 4.8 A with margin: cell ≥ 6.0 A continuous (80 %), pack PCM trip ≥ 6.0 A, lead and connector ≥ 6.9 A per pole (70 %), board fuse 7 A (69 %, NANO2 0451007, same footprint as the interim 2.5 A part), BQ25895 BATFET 6 A continuous (80 %, SLUSC88C §7.3; OCP 9 A), VSYS shunt ≥ 1 W, gauge sense 5 mΩ ≥ 0.5 W if the MAX17055 ±51.2 mV range holds (**UNVERIFIED**). Path drop at 4.8 A: BATFET 19 mΩ max + fuse + sense + shunt + connector ≈ 50 mΩ (est.) → ≈ 0.24 V, so the cell must hold ≈ 3.55 V under load for VSYS = 3.3 V. The Adafruit 328 fails at the cell (4.8 A = 96 % of its 5 A maximum) whatever the connection, and no available pack meeting these figures was found on 2026-10-22 (ADR 0011).
- **Input limits (v1.2).** BQ25895 IIN is rated 3.25 A and ISYS (SW) 5 A (SLUSC88C §7.3). IINLIM ≤ 2.0 A and VBUS × IINLIM ≤ 15 W (PD 9 V at 1.65 A; 5 V at 2.0 A) keep ISYS ≤ 15 W × 0.9 / 3.5 V = 3.9 A (77 %). The TPS2121 ILM is set with RILM = 44.2 kΩ to 2.0–3.0 A (2.5 A typ, SLVSEA3F §7.5): above IINLIM, ≤ 67 % of the 4.5 A rating, and it bounds a class F HAT on the DF40 power contacts (§4.6).

### 4.7.1 Battery contacts (v0.4, ADR 0020)

Six KYOCERA AVX **70-9258-001-120-006** spring contacts, two per power pole, one each for the mid-cell tap and the NTC ([ADR 0020](../adr/0020-battery-connected-through-contacts.md) item 2). Rating 6 A per contact (KYOCERA AVX TDS-BTB-0026 Rev 1; the rating's basis, temperature rise or contact resistance, is in product specification 201-01-252, not yet obtained: **UNVERIFIED**); working height 1.6–2.8 mm (drawing 70-9258-001-1X0-00XS Rev F sheet 2), used at 2.1 mm nominal, 1.8–2.4 mm with ± 0.3 mm assumed. The two contacts of a pole share the current with a factor k = 1.25 on the hotter one (assumption until CB-01, ADR 0020).

**BRD-049 check** (rule of §4.10: ≤ 70 % for connector contacts with all contacts loaded, the protecting limiter's worst-case trip ≤ 100 %):

| Case | Pole current | Hotter contact (× 1.25 / 2) | Use of 6 A | Rule | Verdict |
|---|---|---|---|---|---|
| Full output budget | 2.4 A | 1.5 A | 25 % | ≤ 70 % | OK |
| Worst continuous (headphones at full scale with the full budget) | 3.2 A | 2.0 A | **33 %** | ≤ 70 % | OK |
| PCM trip upper limit, fuse rating | 5.0 A | 3.1 A | **52 %** | trip ≤ 100 % | OK |
| ADR 0014 per-pole criterion | ≥ 4.6 A | pole rating 0.8 × 2 × 6 A = 9.6 A | 3.2 A = 33 % of 9.6 A | ≥ 4.6 A | OK |
| One contact of a pole not touching (fault, not a design case; arithmetic) | 3.2 A / 5.0 A | 3.2 A / 5.0 A | 53 % / 83 % | recorded only | Within the rating |

**Contact resistance and heat** (generic method §3.2), with an end-of-life resistance of ≤ 20 mΩ per contact (**UNVERIFIED** until 201-01-252 or CB-01) and a pole taken as 12.5 mΩ (two contacts with unequal sharing, ADR 0020 item 3):

| | 3.2 A (worst continuous) | 5.0 A (PCM trip time only) |
|---|---|---|
| Drop per pole | 40 mV | 63 mV |
| Drop, both poles | 80 mV (1.1 % of 7.4 V) | 125 mV |
| Loss per pole | 0.13 W | 0.31 W |
| Loss, four power contacts | ≈ 0.26 W | ≈ 0.63 W |
| Hotter contact | 0.08 W | 0.19 W |

- **Temperature rise: UNVERIFIED.** The contact's thermal resistance is not published; CB-02 measures contact and pad temperature at 3.2 A continuous and at 5 A for the PCM's trip time, against the pack's charge-temperature limit at the pocket. At ≤ 0.08 W each (3.2 A, est.) the contacts are not `Thermal = hot` parts under PCB-L-01, but they sit at the pack's terminal end, so their ≈ 0.26 W counts in the device's sustained budget (PCB-L-03), next to the fuse (0.13 W), ship FET (33 mW) and sense resistor (31 mW) on the same path.
- **Accuracy:** the coulomb counter sits on the board's 3 mΩ sense resistor, outside the contacts; cell voltages read ≤ 40 mV low per cell at 3.2 A and zero at rest; the contacts can only make charging stop short, never overcharge (ADR 0020).
- **Insertion:** with no adapter the BQ25798 is unpowered when the pack goes in, so the ship FET is off; it powers up from BATP and turns the ship FET on through SDRV's 100 nA charge pump, ≈ 0.3 V/ms on BAT and ≈ 30 mA inrush (est., SLUSDV2C §7.3.12). With an adapter present, the pack charges the BAT node (2 × 10 µF) through ≈ 0.1 Ω: ≈ 63 A peak, ≈ 2 µs, I²t ≈ 0.004 A²s (0.07 % of the fuse's 5.566 A²s melting I²t; est.); whether the pack PCM ignores that pulse is a pack-specification item (**UNVERIFIED**). BATP: 100 Ω in series and 47 nF to GND (SLUSDV2C Figure 8-2 note 2). Ringing up to 2 × 8.8 V = 17.6 V stays under BAT and BATP's 20 V absolute maximum only at 88 %, so PCB-P-15 and CB-07 check the node, and a P+ TVS footprint (standoff ≥ 9 V, clamp < 20 V) is kept DNP (BOM line 142).
- **Removal under load:** at ≤ 8.8 V no sustained arc forms (gold's minimum arc voltage 15 V, generic method §4.4); with an adapter present the BQ25798 keeps SYS regulated and reports the missing battery.

### 4.8 LPDDR4X VDDQ (0.6 V)

- TPS7A1006 (SBVS314B): 0.6 V fixed, 300 mA, VIN from vcc_ddr (1.1 V), BIAS from vcc_1v8 (1.7–5.5 V), 70 mV maximum dropout at 300 mA (VOUT > 1.0 V; larger at 0.6 V, still inside the 0.5 V headroom).
- Dissipation at an estimated 0.2 A peak: (1.1 − 0.6) × 0.2 = 0.10 W; efficiency 0.6 / 1.1 = 55 % on a small rail, against about 35 % from vcc_1v8.
- The current figure is **UNVERIFIED**: confirm it and the regulator type against the Rockchip RK3566 hardware design guide (not retrieved this session). v0.2: HDG 1.1 (read for the layout rules) confirms the two supplies for LPDDR4X, DDR_VDDQ 1.10 V and DDR_VDDQL 0.60 V (p. 23, Fig. 2-8; p. 40, Fig. 2-26), and gives no current.

**v0.2: LPDDR4X supplies at the memory and at the SoC.**

| Supply | Memory pin | SoC pin | Need | Source (v0.2) | In suspend | Check |
|---|---|---|---|---|---|---|
| 1.8 V | VDD1 | — | LPDDR4X VDD1 1.8 V; v0.6: window 1.70–1.95 V (Micron z42n Rev. C, ADR 0022) | **vcc1v8_ddr = vcca1v8_pmu** through a 0.1 Ω link (BOM line 132); was vcc_1v8 | on (LDO8 on in suspend) | Fixed: vcc_1v8 is off in suspend (finding 15) |
| 1.1 V | VDD2 | DDR_VDDQ (8 balls) | 1.10 V at the SoC with LPDDR4X (HDG p. 23); v0.6: VDD2 window 1.06–1.17 V (z42n Rev. C) | vcc_ddr, RK809 BUCK3 | on | 0.8 V × (1 + 47 k / 120 k) = 1.113 V; VFB3 0.784–0.816 V (RK809 p. 17) and 1 % resistors → ≈ 1.083–1.143 V; the RK3566 DC table gives 1.0–1.21 V for DDRPHY_VDDQ in LPDDR4 mode (parts-lib RK3566 sheet). v0.6: inside VDD2 1.06–1.17 V with 23 mV and 27 mV to spare |
| 0.6 V | VDDQ | DDR_VDDQL (5 balls) | 0.54–0.66 V at the SoC (RK3566 DS 1.1 p. 52) | vcc0v6_ddr, TPS7A1006 (VIN vcc_ddr, **BIAS vcc1v8_ddr**) | on | ±1.5 % over load, line and temperature (SBVS314B); BIAS ≥ VOUT + 1.05 V = 1.65 V met at 1.8 V; VIN − VOUT = 0.483 V at the vcc_ddr low corner, 17 mV under the 0.5 V of SBVS314B §9 (BOM §7 item 33); v0.6: 0.591–0.609 V inside the memory's VDDQ 0.57–0.65 V (z42n Rev. C) |

- **Order.** HDG 1.1 p. 34 brings VCCA1V8_PMU up before VCC_DDR, so VDD1 rises before VDD2 and VDDQ, the order LPDDR4-class parts ask for (JEDEC JESD209-4 not retrieved here: **UNVERIFIED**); the RK809-5 OTP order is still **UNVERIFIED** (finding 6).
- **Currents.** No public source gives VDD1, VDD2 or VDDQ currents for the K4UBE3D4AB; the 100 mA VDD1 allowance (§4.13) and the 0.2 A VDDQ estimate are placeholders until the Samsung datasheet or a measurement on the BOM line 137 links. v0.6 (ADR 0022): the Micron part's IDD tables are public (z42n pp. 50–57); their transcription into the VDD1 (§4.13) and VDDQ budgets is open (BOM §7 item 33), and the placeholders stay until then.
- **v0.6, VDD1 at the memory:** vcca1v8_pmu 1.8 V nominal less the 10 mV link drop at 100 mA: 1.79 V, 90 mV over the 1.70 V minimum and 160 mV under 1.95 V; the RK809 LDO8 output tolerance is not in the parts-lib RK809 sheet (**UNVERIFIED**).

### 4.9 Screen-off playback budget and runtime

| Block | Load at the rail | From the battery | Basis |
|---|---|---|---|
| SoC, LPDDR4X, eMMC, PMIC losses | — | 450–800 mW | **Est., UNVERIFIED** (no RK3566 measurement yet) |
| 2× CS43198 (VA, VCP, VD, VL, VP) | 52 mW | 65 mW | Table 3-17 + chain efficiency |
| Active MCLK oscillator | 47 mW | 56 mW | NDK catalog maximum at 3.1 V, LDO from VSYS |
| MCLK dividers (v0.3, ADR 0019) | 16 mW | ≈ +13 mW net | 8.9 mA at 1.8 V (typ Cpd, est.), ≈ 20 mW at AUDIO_2V2, less the attenuator's ≈ 6.5 mW |
| OPA1622, SE output (2 packages, 4 halves), quiescent, with the LT3045/LT3094 (v1.3) | 125 mW | 256 mW | 10.4 mA × 12 V at the amplifiers; (10.4 + 2.3) mA and (10.4 + 2.45) mA at ±7 V = 179 mW at the pre-rails; TPS65131 η ≈ 70 % (**UNVERIFIED**). v1.2 (±5 V, TPS7A pair): 180 mW |
| Headphone load, 1 mW per channel | 2 mW | 4 mW | — |
| IMU, gauge, TCPC, charger | — | 3 mW (v1.5: ≈ 5 mW; BQ25798 17 µA and BQ28Z610-R1 250 µA in normal mode at 7.4 V) | datasheets |
| Pre-regulator loss (v1.5, TPS62136) | — | +8–14 % of everything above (η 0.88–0.92 at 0.1–0.4 A, est. | est. |
| **Total** | — | **0.84–1.19 W** before v1.5 (v1.2: 0.76–1.11 W); **≈ 0.92–1.36 W** with the 2S tree (v1.5, est.) | — |

- Runtime, 90 % usable energy (v1.5): the pack is made to order (ADR 0014) and its energy is not known yet. At the same 9.4 Wh as the former interim pack, for comparison: **≈ 6.2–9.2 h** (est.). The 2S tree puts the core session 9–12 % below the 1S tree at the same pack energy, ≈ 10.1–10.4 h typical with ADR 0012 (est.), above the 8 h warning of T1-039; the quoted pack should hold the largest energy the pocket allows (ADR 0014 item 2).
- Before v1.5: Runtime, 90 % usable energy: Adafruit 328 (9.4 Wh, the only adopted pack, ADR 0007) → **7.1–10.1 h** (v1.2: 7.6–11.1 h): above the 6 h red line, around the 8 h warning, below the 12 h ideal (T1-039). The SoC estimate dominates (risk 1). Larger packs are not adopted (T1-038).
- The OPA1622 quiescent current (256 mW from the battery on the SE output) is the largest audio term. Only the selected output is enabled. The balanced output enables 8 halves: (20.8 + 2.3) mA and (20.8 + 2.45) mA at ±7 V = 324 mW at the pre-rails, **≈ 464 mW** from the battery (est.).
- Screen on at 200 nit adds about 0.25 W backlight + 0.05 W panel and touch + GPU/VOP (**UNVERIFIED**, est. 0.2 W).

### 4.10 Power margin check (BOM v1.2)

BRD-049 check of every rail, converter, connector and cable. Rule: continuous load ≤ 80 % of the rating for converters, regulators, switches and diodes (fuses ≤ 75 %), ≤ 70 % for connector contacts with all contacts loaded; the worst-case trip of the protecting limiter ≤ 100 % of the rating. Loads marked est. are estimates (T1-026). "Full" = the full output budget on battery (§4.7). v1.5 ([ADR 0014](../adr/0014-two-cell-battery.md), BOM v1.5): the 2S battery path, the VSYS_LV pre-regulator and the two TPS62903 bucks replace the 1S rows (BQ25895, Adafruit 328, JST PH, TPS61089, TLV62569); "Full" is now ≈ 2.4 A at VSYS 6.6 V.

| Item | Rating (source) | Design load | Use | Worst-case ceiling | Verdict |
|---|---|---|---|---|---|
| USB-C receptacle VBUS (USB4105) | 5 A (GCT drawing) | 2.0 A in / 1.5 A out | 40 % | 3.0 A (TPS2121 ILM max; v0.5: 2.95 A) | OK |
| TPS2121 power mux | 4.5 A (SLVSEA3F §7.3) | 2.0 A (IINLIM; v0.5: 1.9 A at 5 V) | 44 % | 2.95 A ILM = 66 % (v0.5) | OK (v1.2 sets RILM 44.2 kΩ; v0.5: 45.3 kΩ 0.1 %) |
| BQ25798 input (v1.5) | IVBUS 3.3 A (SLUSDV2C §6.3) | 2.0 A (IINLIM) | 61 % | ILM 2.95 A = 89 % (v0.5) | OK |
| BQ25798 SW output (VSYS on adapter, v1.5) | ISW 5 A (§6.3) | 2.25 A (15 W input cap at VSYS 6.0 V) | 45 % | — | OK |
| Charger inductor XAL4020-102 (v1.5: BQ25798, 1 µH at 1.5 MHz) | Isat 8.7 A (30 % drop), Irms 6.7 A (20 °C) | ≈ 3.5 A peak at the design point (est.) | 40 % of Isat | 6.3 A peak at the 5 A ISW rating (D = 0.5, L − 20 %) = 72 % | OK |
| BQ25798 battery discharge (v1.5) | 6 A RMS continuous, 10 A ≤ 1 s, IBAT_OCP 9.3 A min (SLUSDV2C §6.3, §6.5) | 3.2 A worst case (2.4 A full) | 53 % (40 %) | 9.3 A OCP | OK |
| Battery fuse 0451005.MRL (NANO2, v1.5) | 5 A | 3.2 A worst case (2.4 A full budget) | 64 % (48 %) | pack PCM trip 4.0–5.0 A | OK (≤ 75 %) |
| Battery contacts, 2 × KYOCERA AVX 70-9258-001-120-006 per power pole (v0.4, ADR 0020; was Micro-Fit 3.0 43650-0400 with crimp 43030-0001, 64 %) | 6 A per contact (TDS-BTB-0026 Rev 1; basis **UNVERIFIED**, spec 201-01-252) | 3.2 A worst case → 2.0 A on the hotter contact, k = 1.25 assumed (2.4 A full → 1.5 A) | 33 % (25 %) | 5 A fuse / PCM trip → 3.1 A = 52 % (≤ 100 % trip rule) | OK (≤ 70 %; §4.7.1) |
| Pack (made-to-order 2S1P, v1.5) | ≥ 4.0 A continuous (ADR 0014 item 2 criterion) | 3.2 A worst case | ≤ 80 % | PCM trip 4.0–5.0 A | OK by the criterion; no pack built yet |
| VSYS INA236 shunt 10 mΩ | ≥ 1 W required | 58 mW at 2.4 A (v1.5; 0.23 W at 4.8 A before) | 6 % | 0.36 W at 6 A | OK |
| Gauge sense WSL12063L000FEA 3 mΩ (v0.2, ADR 0017; was WSL12065L000FEA 5 mΩ) | 0.25 W at 70 °C (Vishay 30100) | 31 mW at 3.2 A | 12 % | 75 mW at 5 A = 30 % | OK |
| VSYS_LV pre-regulator TPS62136 (v1.5) | 4 A; high-side limit 4.8 / 5.6 / 6.5 A; VIN ≤ 17 V (SLVSDV2) | 1.6 A continuous, 2 A peak (est.); ≈ 1.45 A with full-scale headphones and a 3 W system (v1.6: −7 V no longer on VSYS_LV) | 36–50 % | VIN ≤ 9.9 V (VSYS OVP) = 58 % of 17 V | OK; loop: 49° phase margin at VSYS 6.0 V, 54° at 8.8 V (TI model, [VSYS buck and MaskROM simulations](../../sim/README.md)) v0.2: + vcc1v8_wl and NFC_VBAT: ≈ 2.1 A continuous = 53 % (est.). v0.3: the MCLK dividers add ≈ 10 mA; the haptic driver term that the vcc3v3_sys re-sum adds (≈ 0.1 A at VSYS_LV, if the 2 A system estimate did not hold it) gives ≈ 2.2 A = 55 % |
| Pre-regulator inductor XGL4020-152MEC (v1.5; peak corrected in v1.6) | Isat 7.5 A (30 % drop), 5.3 A (20 %); Irms 8.0 A (20 °C) (Doc 1529) | **3.03 A peak at 2.0 A**, VSYS 9.9 V, L −20 % (ΔIL = 250 ns × VIN / L = 2.06 A; TI model agrees; the 2.41 A of v1.5 used Eq. 10) | 40 % of 7.5 A; switch peak 63 % of the 4.8 A minimum limit | 6.5 A maximum limit < 7.5 A | OK v0.2: if the system peak (2.0 A), the radio calibration peak (0.59 A at the buck input) and the NFC reader (0.29 A) coincide, 2.88 A + 1.03 A ripple = **3.91 A = 81 %** of the 4.8 A minimum high-side limit, 52 % of Isat: a transient of three estimated peaks, inside the ≤ 100 % limiter rule; any two of them ≤ 3.62 A = 75 %. v0.3: with the haptic term on top, ≈ 4.0 A = 84 % of the minimum limit, 53 % of Isat: still inside the ≤ 100 % rule |
| vcc3v3_sys buck TPS62826 (until v0.2) | 3 A; ILIM ≥ 3.7 A | 1.85 A peak (est.) | 62 % | inductor peak 2.25 A = 61 % of ILIM min (v1.5: 2.06 A = 56 % at VIN 3.8 V) | OK (v1.2; TLV62569 was 80–90 %) v0.2: ≈ 2.35 A peak (est.) = 78 %, inductor 2.77 A = 75 % of ILIM min; TPS62827 (4 A, 59 %) if the schematic re-sum passes 80 % (BOM §7 item 36) |
| vcc3v3_sys buck TPS62827 (v0.3) | 4 A; high-side limit 4.8 / 5.6 / 6.4 A (SLVSEF9I p. 6) | ≈ 2.45 A peak (est., §3) | **61 %** | inductor peak 2.45 + 0.21 A (half of 0.42 A ripple at VIN 3.8 V) = 2.66 A = 55 % of the 4.8 A minimum limit | OK; TPS62826 would be 82 % (fails the 80 % rule) |
| vcc3v3_sys inductor Würth 744373240047 (v1.3, D27; was DFE252012F-R47M, 4.9 A < 5.0 A) | 6.8 A (TI Table 8-5); IR 8.7 A (ΔT 40 K), Isat 10.4 A at 10 % drop (Würth page) | 2.25 A peak (v0.3: 2.66 A) | 33 % of 6.8 A (v0.3: 39 %) | ILIM max 5.0 A = 74 % of 6.8 A; v0.3 with the TPS62827: 6.4 A = 94 % of 6.8 A, 62 % of the 10.4 A Isat | OK (≤ 100 % limiter rule) |
| TPS62869 vdd_cpu (v0.6, ADR 0021; was RK860-0, no public datasheet) | 6 A (SLVSFS3B p. 5); high-side limit 7 / 7.7 / 8.5 A (p. 7); VIN 5.5 V recommended, 6 V absolute | 3 A (est.) | 50 %; VIN 69 % / 63 % | inductor peak 3.76 A = 54 % of the 7 A minimum limit | OK |
| vdd_cpu inductor XGL4012-221MEC (v0.6) | Isat 9.9 / 14.4 A at 20 / 30 % drop, Irms 10.9 A (Coilcraft Document 1718) | 3 A | 28 % of Irms | 8.5 A maximum limiter trip = 86 % / 59 % of Isat | OK (≤ 100 % limiter rule) |
| RK809 BUCK1–5 | 2.5 / 2.5 / 1.5 / 1.5 / 2.5 A (RK809 DC table) | play 0.1–0.3 A; peaks **UNVERIFIED** | — | — | Open: measure on a reference board |
| RK809 LDO4 FP_VCI | 100 mA design (tables disagree, 100/400 mA) | panel VCI (spec gives no current) | — | v0.5: no LDO4 trip value in the datasheet; the TPS22945 behind it limits at 100–200 mA (≤ 0.2 A ceiling) | Open with the panel current |
| RK809 SWOUT1 / SWOUT2 | 1.5 A / 3 A (designed to 1.5 A) | 0.6 A / 0.2 A (est.) | 40 % / 13 % | — | OK v0.2: SWOUT1 carries only AVDD33: 0.24 A typical = 16 %, 1.05 A peak = 70 % of the 1.5 A design figure. v0.3: SWOUT1 unused (AVDD33 on a TPS22919, next row) |
| TPS22919 vcc3v3_wl (v0.3) | 1.5 A (SLVSEN5B) | 0.24 A typical, 1.05 A peak | 16 % / 70 % | 95 mV drop at the peak (90 mΩ) | OK |
| TPS7A1006 vcc0v6_ddr | 0.3 A | 0.2 A (est., **UNVERIFIED**) | 67 % | — | OK pending the RK3566 guide |
| TPS62826 vcc1v8_wl (v0.2) | 3 A; ILIM ≥ 3.7 A (SLVSEF9I) | 0.39 A typical, 1.05 A peak | 13 % / 35 % | inductor peak 1.51 A = 41 % of ILIM min | OK |
| vcc1v8_wl inductor Würth 744373240047 (v0.2) | 6.8 A (TI Table 8-5) | 1.51 A peak | 22 % | ILIM max 5.0 A = 74 % | OK |
| TPS22919 NFC_VBAT (v0.2) | 1.5 A | 0.29 A max (PN7160 Table 1) | 19 % | PN7160 transmitter limiter 330 mA max | OK |
| RK809 LDO8 vcca1v8_pmu (v0.2) | 400 mA (VIN 3.6 V) / 200 mA (VIN 2 V) (RK809 p. 18) | ≈ 157 mA (est., §4.13) | 39 % / 79 % | — | OK on either figure; measure (BOM §7 item 35) |
| Block measurement links (v0.2, §4.12) | WSL1206 0.25 W; 0603 thick film 0.1 W (Yageo RC/RL, **UNVERIFIED**, data sheet not read) | per §4.12 | ≤ 18 % | — | OK |
| TPS22919 load switches | 1.5 A | ≤ 0.08 A | ≤ 6 % | — | OK (v0.5: the faceplate rails leave them) |
| Faceplate rail switches (v0.5): TPS22950 FP_3V3; TPS22945 FP_1V8, MIC_1V8, FP_VCI | limits 0.22–0.38 A; 100–200 mA | 200 / 100 / 20 / 100 mA budgets | at or below each minimum limit | maxima 0.38 A = 96 % of 0.4 A; 0.2 A = 100 % of 0.2 A (faceplate interface v1 ceilings, per FH35C contact 0.2 A) | OK; TPS22945 limit at 1.8 V and 2.8 V **UNVERIFIED** |
| TPS62840 AUDIO_2V2 | 0.75 A | 25 mA (v0.3; 16 mA before) | 3 % | — | OK |
| TPS7A2018 ×3 (v0.3: + MCLK_1V8), TPS7A2031 | 0.3 A | 7.8 / 8.9 / 15 mA | ≤ 5 % | — | OK |
| SN74AUC1G74 ×2 (v0.3) | ±20 mA continuous output, IOH/IOL 8 mA at 1.65 V (SCES537D p. 3) | Q into ≤ 15 pF at 22.5792 / 24.576 MHz | — | VI 3.1 V oscillator ≤ 3.6 V rating (simulated peak 3.146 V) | OK (ADR 0019) |
| TPS65131 +7 V boost (v1.6: boost half only) | switch limit 1.8 A min | 433 mA rail peak (full-scale sine) | 56–78 % in operation (simulated, [output-stage simulation](../../sim/output-stage/README.md)) | ≈ 99 % at the positive LDO pair's maximum trip (0.65 A, worst-case parameters) | OK by the ≤ 100 % limiter rule; bench confirmation before freeze ([ADR 0015](../adr/0015-amplifier-rails-from-vsys.md)) |
| LMR33630C −7 V inverting buck-boost (v1.6) | high-side 3.85 A min, valley 2.9 A min; VIN−VOUT 36 V recommended (SNVSAN3F) | 1.80 A inductor peak at the full-scale sine; 2.13 A (valley 1.39 A) at the 0.78 A LDO-limit case (TI model, VSYS 6.0 V) | 47 % / 55 % of high-side; 48 % of valley; 17.1 V = 48 % of 36 V | Eq. 6 cross-check ≤ 63 % | OK |
| LMR33630C inductor XGL4020-222MEC (v1.6) | Isat 6.2 A (30 % drop), 4.4 A (20 %); Irms 6.7 A (20 °C) | 1.80 / 2.13 A peak | 29 % / 34 % of 6.2 A | 5.05 A maximum high-side limit < 6.2 A | OK |
| 2 × LT3045 HPA_P6V0 (v1.6) | 0.5 A per device | 165 mA per device continuous (330 mA model average / 2) | 33 % | 315 mA per device at the maximum trip = 63 %; pair limit 516–631 mA, +13 % over the 457 mA design peak | OK |
| 2 × LT3094 HPA_N6V0 (v1.6) | 0.5 A per device | 165 mA per device | 33 % | 323 mA = 65 %; pair limit 519–646 mA, +14 % | OK |
| TPS61160 backlight (v0.5; TPS61169 until v0.4: 0.45 A of ≥ 1.2 A) | switch ≥ 0.56 A | 0.44 A peak (16.5 V string, 60 mA, 22 µH) | 79 % | open string ≤ 27 V = 90 % of the FH35C's 30 V | OK; strings above 18 V derate (§4.5) |
| PMEG6010CEH rectifier | 1 A, 60 V | 0.06 A avg, 39 V OVP max | 6 % / 65 % | — | OK |
| LQH3NPN100MJRL | Isat **UNVERIFIED** (≥ 0.6 A needed) | 0.45 A peak | — | — | Open: spec sheet |
| TPS62903 5.1 V buck (v1.5; was the TPS61089 boost) | 3 A; high-side limit 4.0 / 4.6 / 5.5 A (SLVSES3A §6.5) | 1.6 A | 53 % | 3.96 A with both eFuses at their maximum trip (v0.7, RILM 1.87 kΩ; 3.3 A before): 132 % of the rating, 99 % of the minimum limit, a software-fault case (§8 item 29) | OK for the design load; fault case to check thermally |
| 5.1 V buck inductor XGL4020-102MEC (v1.5; was XAL4020-152) | Isat 8.8 A (30 % drop), 6.3 A (20 %); Irms 8.8 A (20 °C) (Doc 1529) | 2.14 A peak at 1.6 A, VIN 8.8 V | 24 % of 8.8 A | ≈ 5.7 A maximum dynamic limit < 8.8 A | OK |
| TPS259470 eFuses (#A, #C; #B removed in v0.7) | 5.5 A switch | 1.5 / 1.5 A | 27 % | 1.981 A maximum trip (v0.7) = 36 % | OK |
| TPS62903 HAT_3V3 buck | Removed in v0.7 | — | — | — | — |
| HAT_3V3 inductor XGL4020-102MEC | Removed in v0.7 | — | — | — | — |
| DF40C-100, HAT_5V (v0.5; DF40C-50 × 12 until v0.4) | 10 × 0.3 A | 2.0 A | 67 % | 2.95 A in = 98 %; interface ceiling 3.0 A = 100 % | OK (BRD-049: ≤ 70 % / ≤ 100 %) v0.7: follows the HAT connector decision (interface v2: `VBUS` 3.0 A continuous, 4.5 A fault; `HAT_3V3` removed) |
| DF40C-100, HAT_3V3 (v0.5; × 6 until v0.4) | 5 × 0.3 A | 1.0 A | 67 % | 1.16 A = 77 %; ceiling 1.5 A = 100 % | OK v0.7: follows the HAT connector decision (interface v2: `VBUS` 3.0 A continuous, 4.5 A fault; `HAT_3V3` removed) |
| DF40C-100, GND (v0.5; × 22 until v0.4) | 15 × 0.3 A | 3.0 A | 67 % | 4.11 A = 91 %; ceiling 4.5 A = 100 % | OK v0.7: follows the HAT connector decision (interface v2: `VBUS` 3.0 A continuous, 4.5 A fault; `HAT_3V3` removed) |
| HAT flat cable (FPC) power conductors | sized per IPC-2152 for ≤ 10 °C rise | 2.0 / 1.0 / 3.0 A | — | 3.0 / 1.15 / 4.15 A | Requirement for the FPC drawing (widths **UNVERIFIED**) v0.7: follows the HAT connector decision (interface v2: `VBUS` 3.0 A continuous, 4.5 A fault; `HAT_3V3` removed) |
| HAT pogo contacts (P70, device-side piece; v1.4: hat-standard interface v1 §5, HAT_5V ×3, HAT_3V3 ×2, GND ×4) | 2.0 A per contact | 2.0 / 1.0 / 3.0 A | 33 / 25 / 38 %; 50 % each with one contact open | interface v1.1 ceilings 3.0 / 1.5 / 4.5 A = 50 / 38 / 56 % (75 % with one contact open; v0.5, were 3.6 / 1.8 / 5.4 A); the T1's limiters are lower | OK (v1.4; v0.5: 68-contact field, same power counts) v0.7: follows the HAT connector decision (interface v2: `VBUS` 3.0 A continuous, 4.5 A fault; `HAT_3V3` removed) |
| Faceplate FH35C contacts | 0.2 A, 0.14 A all loaded | FP_VCI 0.1 A ×1; FP_3V3 ≈ 0.08 A ×2; BL 60 mA; LED ≤ 20 mA | ≤ 71 % of the derated figure | — | OK |
| LP5521 outputs / LED | 25.5 mA; LED IF 25 mA | 20 mA DT cap | 78 % / 80 % | — | OK (new, v1.2) |

### 4.10.1 Headphone stage margin (BOM v1.3, ADR 0012)

**v1.6 ([ADR 0015](../adr/0015-amplifier-rails-from-vsys.md), simulated in the [output-stage simulation](../../sim/output-stage/README.md)).** The full-scale sine makes each pre-rail draw a full-wave rectified current: **433 mA peak** (33 mA + 400 mA × \|sin\|), ≈ 288 mA average, not the 275 mA average used below; the converters follow the peak. The design peak at the LDO outputs is 457 mA (OPA1622 clip point, 2 channels in phase plus quiescent).

| Item | Rating (source) | Load | Use | Verdict |
|---|---|---|---|---|
| LMR33630C −7 V switch (high side) | 3.85 A min (SNVSAN3F) | 1.80 A peak at the sine; 2.13 A at the 0.78 A LDO-limit case (TI model, VSYS 6.0 V) | **47 % / 55 %** | OK |
| LMR33630C valley | 2.9 A min | 1.39 A (limit case) | 48 % | OK |
| LMR33630C VIN − VOUT | 36 V recommended, 38 V absolute | 9.9 + 7.24 = 17.1 V | 48 % / 45 % | OK |
| XGL4020-222MEC | 6.2 A (30 % drop) | 1.80 / 2.13 A | 29 % / 34 % | OK |
| TPS65131 boost switch (+7 V, VIN 3.8 V) | 1.8 A min | 433 mA rail peak; 0.65 A at the positive pair's maximum trip | **56–78 %**; **≈ 99 %** at the trip (worst-case parameters; ≈ 90 % typical) | OK by the ≤ 100 % limiter rule; bench item |
| 2 × LT3045 / 2 × LT3094 | 500 mA per device | 165 mA per device continuous; 315 / 323 mA at the maximum trip | 33 %; 63 % / 65 % | OK |
| LDO headroom at the peak, worst corner | ≤ 350 mV maximum dropout | 0.50 V (positive) / 0.65 V (negative) | +0.15 / +0.30 V | OK |
| −7 V ripple | — | 6 mVpp at 2.1 MHz; ≈ 2 µVpp after the LDOs (≈ 68–72 dB) | — | OK |

- The tables below (v1.3–v1.5) are kept for traceability; their inverter rows are superseded (the simulation gives 1.82 A = 101 % for the TPS65131 inverter even at 3.8 V).
- Bench items: LMR33630C PFM bursts at idle, its heat (0.4–0.9 W est. at 0.78 A), LDO current sharing (BOM §7 items 29–30).

Worst continuous case: full-scale sine into balanced 32 Ω, both channels, 275 mA per ±7 V rail (§4.1). VIN = VSYS, 3.0 V (battery near empty) to 3.5 V. The TPS65131 equations are SLVS493E Eq. 3 and 4 (peak inductor current, IL = V × I / (VIN × 0.64)); the curve readings are typical values at 25 °C, read from Figures 6-2 and 6-4 and interpolated between the plotted output voltages.

| Item | Rating (source) | Load at VIN 3.5 V | Load at VIN 3.0 V | Use (3.5 / 3.0 V) | Verdict |
|---|---|---|---|---|---|
| TPS65131 inverter switch | 1.8 A min, 1.95 typ, 2.2 max | 1.29 A peak (Eq. 4) | 1.43 A | **72 % / 79 %** | At the edge of the 80 % rule: conditional (simulation) |
| TPS65131 inverter output, typical curve | Figure 6-4: ≈ 480 mA at 3.5 V, ≈ 340 mA at 3.0 V (−7 V, interpolated) | 275 mA | 275 mA | 57 % / 81 % | Typical only; agrees with Eq. 4 at 3.0 V |
| TPS65131 boost switch | 1.8 A min | 0.86 A (Eq. 3) | 1.00 A | 48 % / 56 % | OK |
| TPS65131 boost output, typical curve | Figure 6-2: ≈ 640 mA at 3.0 V (+7 V, between the 5 V and 10 V curves) | 275 mA | 275 mA | — / 43 % | OK |
| Inverter inductor DFE252012F-4R7M | 2.1 A (ΔL/L −30 %), 1.5 A (ΔT 40 °C) | 1.29 A peak | 1.43 A peak, ≈ 1.15 A average (η 0.8, est.) | 61 % / 68 % peak; 76 % average | OK at the design load; the 2.2 A maximum switch limit exceeds the 2.1 A rating (BOM D31) |
| Boost inductor DFE252012F-4R7M | as above | 0.86 A peak | 1.00 A peak, ≈ 0.80 A average | 48 % peak; 53 % average | OK |
| Rectifiers PMEG2010AEH | 1 A, 20 V (listing) | 275 mA average | 275 mA; reverse VIN + 7 V ≤ 11.4 V | 28 %; 57 % | OK |
| LT3045 / LT3094 | 500 mA | 275 mA | 275 mA | 55 % | OK |
| VSYS draw of the headphone rails | interim battery path 1.6 A (§4.7) | 4.8 W = **1.38 A** (η 0.8, est.) | **1.61 A** | 86 % / 100 % by itself | **Fails on the interim pack without a ceiling**: §4.11 |

- **Result:** every part except the TPS65131 inverter is inside the BRD-049 rule with margin. The inverter stays at 79 % of its minimum switch limit at VIN 3.0 V by Eq. 4, and the typical curve gives ≈ 81 % there. ADR 0012's condition holds: confirm by WEBENCH or SPICE at VIN 3.0 V, ±7 V, 275 mA per rail before layout freeze, or replace the inverter by one with more margin.
- With the interim ceiling of §4.11 in screen-off playback the rails carry ≈ 217 mA, and the inverter peak drops to 1.13 A at VIN 3.0 V (63 %).
- **v1.5 (ADR 0014):** the TPS65131 runs from VSYS_LV, a regulated 3.8 V (TPS62136), so the 3.0–3.5 V columns above no longer occur. At VIN 3.8 V and 275 mA per rail: inverter switch 1.22 A peak (Eq. 4) = **68 %** of the 1.8 A minimum limit, boost switch 0.79 A (Eq. 3) = 44 %, inverter inductor 1.22 A peak = 58 % of its 2.1 A rating. The typical curves were not read at 3.8 V. The rails draw ≈ 4.8 W from VSYS_LV, ≈ 5.2 W from VSYS through the pre-regulator (0.92, est.), ≈ 0.79 A at VSYS 6.6 V; there is no interim battery path to compare against (§4.11). ADR 0012's simulation condition was run: the inverter fails at full-scale peaks, and v1.6 replaces it ([ADR 0015](../adr/0015-amplifier-rails-from-vsys.md), table above).

### 4.11 Interim battery: headphone output ceiling (BOM v1.3, ADR 0012)

**v1.5 ([ADR 0014](../adr/0014-two-cell-battery.md) item 3): this ceiling is removed.** It existed only because of the Adafruit 328's 1.6 A path, and the Adafruit 328 is no longer a T1 pack. With a compliant 2S pack the full output budget is available on battery and the battery imposes no output ceiling; the only limits left are safety limits, documented and visible (BRD-049, T1-045). Bring-up runs on a bench supply or a protected 2S pack on the bench, sized for the load, so no ceiling is needed there either. The combined case of full-scale headphones with the full HAT and USB-C load is covered by the battery path (§4.7, ADR 0014). The rest of this section is kept for traceability (1S).

The Adafruit 328 path is budgeted at **1.6 A continuous** (§4.7), for every load together. At full scale into balanced 32 Ω the headphone rails alone draw 2 × 7 V × 275 mA / 0.8 ≈ 4.8 W from VSYS: 1.38 A at 3.5 V, **1.61 A at 3.0 V** (η 0.8 for the TPS65131 at this load, est.). Single-ended, full scale draws ≈ 1.5 W into 32 Ω (0.51 A at 3.0 V) and ≈ 2.4 W into 16 Ω (0.80 A).

Headroom for the headphone rails is 1.6 A × VSYS less the rest of the system. Ceiling on a continuous full-scale sine into balanced 32 Ω, per channel, from the rail model of §4.1 (Ipk per leg = (I_rail − 20.8 mA) × π / 4, P = Ipk² × 16 Ω):

| VSYS | Rest of the system (est.) | Left for the headphone rails | Ceiling, balanced 32 Ω | Below the full ≈ 640 mW |
|---|---|---|---|---|
| 3.5 V | 1.0 W (screen-off playback, §4.9 without the amplifier terms, rounded up) | 4.6 W | ≈ 580 mW | −0.4 dB |
| 3.3 V | 1.0 W | 4.3 W | ≈ 490 mW | −1.1 dB |
| **3.0 V** | **1.0 W** | **3.8 W** | **≈ 380 mW** | **−2.3 dB** |
| 3.0 V | 3.0 W (screen on with CPU load, §4.7) | 1.8 W | ≈ 65 mW | −9.8 dB |

**Requirement for Blackbird OS (ADR 0012 condition):** while a battery path budgeted below the full output is fitted (the Adafruit 328: 1.6 A), Blackbird OS shall limit the headphone output level so that the continuous battery current, measured by the VSYS INA236, stays at or below that budget, together with the HAT and USB-C source load of §4.6. The design figure for screen-off playback is **≈ 380 mW per channel into balanced 32 Ω at VSYS 3.0 V** (≈ −2.3 dB under the full output); single-ended output stays below the ceiling except at 16 Ω with a high system load. The full output needs an ADR 0011 pack. The system figures are estimates (T1-026); the ceiling is enforced on the measured current, not on these numbers.

- **With an ADR 0011 pack (superseded in v1.5; the 2S figures are in §4.7):** the full output budget of §4.7 (15.9 W from VSYS) counts the system at 3.0 W and has no separate headphone term; the full-scale balanced 32 Ω sine adds ≈ 4.8 W. Blackbird OS must budget headphone and HAT/USB-C power together, or the budget grows: a decision for the maintainers (BOM §7 item 17).

### 4.12 Block measurement links and current monitors (v0.2, G10–G12)

Rule (feature blocks G12, RFC 0011 rule 3): one link per block supply, on the block side of its switch or at the input of the block's own regulator, with two Kelvin test pads; a shunt in `full`, 0 Ω in `production` (the H5 positions keep their 5 mΩ, BOM line 137). Classes: **H5** WSL12065L000FEA 5 mΩ 1206; **H20** WSL1206R0200FEA 20 mΩ 1206; **M** RL0603FR-070R1L 0.1 Ω 0603; **L1** RC0603FR-071RL 1.0 Ω; **L10** RC0603FR-0710RL 10 Ω. Where a regulator's feedback can be taken on the load side of its link (RK809 FB1, FB3; TPS62826 FB), it is, so the drop is regulated out. Currents marked est. come from §3; drop and power are I × R and I² × R.

| # | Block | Position | Class | Design current | Drop | Dissipation |
|---|---|---|---|---|---|---|
| 1 | `blk.vdd-cpu` | vdd_cpu, TPS62869 output before the SoC bulk capacitors, inside the VOS sense loop (v0.6, ADR 0021) | H5 | 3 A (est.) | 15 mV, regulated out (VOS senses at the SoC); 15 mV only with the 0 Ω local-sense fallback | 45 mW (18 %) |
| 2 | `blk.soc` | vdd_logic, BUCK1 output | H5 | 2.5 A rating (0.3 A play) | 12.5 mV, inside FB1 | 31 mW (13 %) |
| 3 | `blk.lpddr4x` | vcc_ddr, BUCK3 output | H5 | 1.5 A rating | 7.5 mV, inside the FB3 divider | 11 mW |
| 4 | `blk.pwr-3v3-sys` | vcc3v3_sys, TPS62827 output (v0.3) | H5 | 2.45 A peak (est.) | 12 mV | 30 mW (12 %) |
| 5 | `blk.pwr-vsys-lv` | VSYS_LV, TPS62136 output (G11) | H5 | 2.1 A continuous, 2.9 A peak (est.) | 14.5 mV (0.4 %) | 42 mW (17 %) |
| 6 | `blk.lpddr4x` | vcc0v6_ddr | H20 | 0.2 A (est.) | 4 mV (0.7 %) | 0.8 mW |
| 7–8 | `blk.hpa-se` | HPA_P6V0 and HPA_N6V0, SE branch, before the group's local capacitors | H20 | ≤ 0.46 A peak | ≤ 9 mV (0.15 %) | ≤ 4 mW |
| 9–10 | `blk.hpa-bal` | HPA_P6V0 and HPA_N6V0, balanced branch | H20 | 0.457 A peak, 0.275 A average | 9 mV peak | 1.5 mW average |
| 11 | `blk.radio` | vcc3v3_wl (AVDD33), at the TPS22919 output (v0.3) | H20 | 1.05 A peak, 0.24 A typical | 21 mV peak (0.6 %) | 22 mW peak |
| 12 | `blk.radio` | vcc1v8_wl (AVDD18), inside the TPS62826 feedback | H20 | 1.05 A peak, 0.39 A typical | regulated out | 22 mW peak |
| 13 | `blk.lpddr4x` | vcc1v8_ddr (VDD1, BIAS) | M | 0.1 A (est.) | 10 mV (0.6 %) | 1 mW |
| 14 | `blk.emmc` | VCC branch of vcc3v3_sys | M | 0.25 A (est.) | 25 mV (0.8 %) | 6 mW |
| 15 | `blk.emmc` | VCCQ branch of vcc_1v8 | M | 0.1 A (est.) | 10 mV (0.6 %) | 1 mW |
| 16 | `blk.microsd` | vcc3v3_sd | M | 0.2 A | 20 mV (0.6 %) | 4 mW |
| 17 | `blk.speaker` | MAX98357A VDD (VSYS_LV branch) | M | 0.3 A peak (est.) | 30 mV (0.8 %) | 9 mW |
| 18 | `blk.nfc-reader` | NFC_VBAT | M | 0.29 A max | 29 mV (0.8 %) | 8 mW |
| 19 | `blk.haptics` | DRV2605L VDD | M | 0.1 A (est.) | 10 mV | 1 mW |
| 20 | `blk.tpm` | VDD (vcca1v8_pmu branch) | M | 30 mA (est.) | 3 mV | — |
| 21 | `blk.rp2354` | RP_3V3 | M | 50 mA (est.) | 5 mV | — |
| 22 | `blk.status-led` | LP5521 VDD (VSYS_LV branch) | M | 0.1 A (est.) | 10 mV | 1 mW |
| 23 | `blk.fp-connector` | FP_3V3 | M | 80 mA | 8 mV | — |
| 24 | `blk.fp-display` | FP_VCI (LDO4 output) | M | 0.1 A design | 10 mV (0.4 %) | 1 mW |
| 25 | `blk.audio-supply` | DAC_DIG_1V8 | L1 | 13.2 mA | 13 mV (0.7 %) | — |
| 26 | `blk.audio-supply` | AUDIO_2V2 (TPS62840 output, both VA LDO inputs and the MCLK_1V8 LDO) | L1 | 25 mA (v0.3) | 25 mV (1.1 %) | — |
| 27 | `blk.mclk` | TPS7A2031 input (VSYS_LV branch) | L1 | 15 mA | 15 mV | — |
| 28–29 | `blk.dac-l`, `blk.dac-r` | each VA LDO input | L1 | 7.8 mA | 8 mV | — |
| 30 | `blk.rp2354` | RP_IOVDD_1V8 | L1 | ≤ 10 mA (est.) | ≤ 10 mV | — |
| 31 | `blk.fp-connector` | FP_1V8 | L1 | 5 mA | 5 mV | — |
| 32 | `blk.imu` | VDD + VDDIO (vcca1v8_pmu branch) | L10 | 0.65 mA | 6.5 mV | — |
| 33 | `blk.nfc-tag` | VCC (vcca1v8_pmu branch) | L10 | ≤ 1 mA (est., **UNVERIFIED**) | ≤ 10 mV | — |
| 34–35 | `blk.mic-main`, `blk.mic-ambient` | each MIC_1V8 branch (G10) | L10 | ≤ 1 mA (est.) | ≤ 10 mV | — |
| 36 (v0.3) | `blk.mclk` | MCLK_1V8 LDO input (AUDIO_2V2 branch, after link 26) | L1 | 8.9 mA | 9 mV (0.4 %) | — |

The DAC VP pair (0.06 mA) and the always-on logic (expander, EEPROM, gates) have no link: they are read through vcca1v8_pmu or not attributed. Blocks without a row share a parent's link.

**INA236 positions (G11)**, I2C1 at 1.8 V, BOM lines 54 and 136:

| Address | Channel | Position | Shunt | Full scale (81.92 mV) | Design load |
|---|---|---|---|---|---|
| 0x40 | VSYS | BQ25798 SYS output | 10 mΩ | 8.2 A | 2.4 A full budget |
| 0x41 | Audio, VSYS_LV side | dedicated VSYS_LV branch to the TPS65131, TPS62840, TPS7A2031 and DAC_VP switch | 20 mΩ (v0.2; was 100 mΩ) | 4.1 A | ≈ 0.71 A at the full-scale sine, ≈ 1.5 A at the positive LDO pair's maximum trip (est.) |
| 0x42 | Display | TPS61160 VIN (v0.5) | 100 mΩ | 0.82 A | 0.33 A |
| 0x43 | HAT | 5.1 V buck input | 20 mΩ | 4.1 A | ≈ 1.3 A |
| 0x48 (v0.2) | Audio, VSYS side | LMR33630C VIN | 20 mΩ | 4.1 A | 0.35 A sine, ≈ 1.0 A LDO-trip case |

Rail names of the measured branches in the schematic (`blk.current-monitors`): `VSYS_SRC` is the BQ25798 SYS node, the supply side of the 0x40 shunt, whose load side is `VSYS`; the load sides of the other shunts are `VSYS_LV_AUDIO` (0x41), `VSYS_LV_BL` (0x42), `VSYS_P5V1` (0x43) and `VSYS_AUDIO` (0x48). Each feeds only the consumers named in its row.

### 4.13 vcca1v8_pmu budget (v0.2)

RK809 LDO8 from VCC7 = vcc3v3_sys. The DC table gives 400 mA at VIN 3.6 V / VOUT 3.3 V and 200 mA at VIN 2 V / VOUT 1.8 V (RK809 Rev 1.01 p. 18); the T1's 3.3 V in, 1.8 V out is not tabulated, so both figures are checked.

| Load | Current | Basis |
|---|---|---|
| SoC PMU domain (PMUIO2 IO, PMUPLL, VCCA1V8_PMU analog) | 20 mA | est.; Rockchip's power report not retrieved (HDG p. 41) |
| LPDDR4X VDD1 (vcc1v8_ddr) | 100 mA | allowance, **UNVERIFIED** |
| TPS7A1006 BIAS | 0.06 mA | SBVS314B (60 µA max at 300 mA) |
| TPM SLB9673 | 30 mA | allowance, **UNVERIFIED** |
| Board EEPROM (write) | 3 mA | est. |
| I2C2 pull-ups, 2 × 2.2 kΩ, both lines low | 1.6 mA | 1.8 V / 2.2 kΩ × 2 |
| PN7160 VDD(PAD), NFC tag VCC | ≤ 2 mA | est., **UNVERIFIED** |
| IMU, gyroscope and accelerometer | 0.65 mA | DS13510 Table 4 |
| TCA6416A VCCI, TPS3808, three LVC gates, SN74LVC2G66, LP5521 EN | < 0.1 mA | µA-class supply currents (datasheets) |
| **Total** | **≈ 157 mA** | 39 % of 400 mA, 79 % of 200 mA |

VDD1 dominates and is the least known. If the BOM line 137 link (0.1 Ω, 10 mV at 100 mA) shows more, fit the DNP TPS7A2018 (BOM line 132) and remove the link.

## 5. Power-gating map

Default state is the state with no software running (pull resistors). "SoC GPIO" means a RK3566 GPIO; from v0.3 the balls and their domains are in [pinout v1](pinout-v1.md) §3 (1.8 V unless noted).

| Block | Rail(s) | Switch / enable | Control | Default | Discharge | Notes |
|---|---|---|---|---|---|---|
| DAC digital (both) | DAC_DIG_1V8 | TPS22919 | SoC GPIO `DAC_DIG_EN` | off (pull-down) | QOD in TPS22919 | Park I2S lines low before removal (back-powering) v0.2 (G2): the I2C2 branch to both DACs passes an SN74LVC2G66 whose controls are DAC_DIG_1V8 itself; `DAC_INT` pull-up on DAC_DIG_1V8 |
| DAC VP (both) | DAC_VP | TPS22919 | SoC GPIO `DAC_VP_EN` | off | QOD | VP first on, last off |
| DAC analog + clocks | AUDIO_2V2, DACx_VA, MCLK_3V1 | TPS62840 EN, TPS7A2018 EN, TPS7A2031 EN | SoC GPIO `AUDIO_LN_EN` | off | TPS7A20 smart pulldown, TPS62840 active discharge | — v0.2 (G3): the TPS7A2031 EN is `AUDIO_LN_EN` AND DAC_DIG_1V8 (SN74LVC1G57 on vcca1v8_pmu), so MCLK cannot drive an unpowered XTI. v0.3 (ADR 0019): MCLK_1V8 (dividers) EN = DAC_DIG_1V8 directly |
| MCLK family select | NZ2520SDA ×2 (45.1584 / 49.152 MHz, v0.3) | ST pin (tri-state) | `MCLK441_EN`, `MCLK48_EN` on native 3.3 V balls GPIO4_C2, GPIO4_C3 (VCCIO7, pinout v1), 0 Ω series footprints | both standby (pull-down on each ST pin; an open ST enables the output) | — | Never both enabled. ST rating at 3.3 V drive into a 3.1 V or unpowered oscillator **UNVERIFIED** (pinout O11) |
| MCLK dividers (v0.3) | MCLK_1V8, 2× SN74AUC1G74 | CLR̅ | `MCLK_DIV_RUN` (ball not in pinout v1; proposal GPIO4_C4, BOM §7 item 39) | held (100 kΩ pull-down) | — | ADR 0019 decision 6: CLR̅ low before the rails rise, released while the oscillator net is low, before ST rises |
| HP amp rails | AUDIO_P7V0/N7V0, HPA_P6V0/N6V0 | TPS65131 ENP (ENN, PSN tied to GND); LMR33630C EN through a level shifter (DMG1012T + DMP3099L, SNVA856B Figure 7-1); 2 × LT3045 and 2 × LT3094 EN/UV (v1.6) | `HPA_RAIL_EN` (both pre-rail converters), then `HPA_LDO_EN` (all four LDOs) **≥ 10 ms later**, 3.3 V logic (EN/UV thresholds 1.24 V and +1.26 V; GPIO4_C5, GPIO4_C6 on VCCIO7, pinout v1) | off | — | Symmetric ramp from equal SET networks, ≈ 65 ms (§4.2, OPA1622 §7.4.2) |
| HP amp outputs | per package | OPA1622 EN (×6: 2 SE, 4 balanced) | SoC GPIO `HPA_SE_EN`, `HPA_BAL_EN` | low (shutdown, 5 µA/ch) | — | EN low during rail ramps; v1.5: no battery ceiling with a compliant pack (§4.11) |
| Speaker amp | VSYS_LV (v1.5) | MAX98357A SD_MODE | SoC GPIO `SPK_SD_MODE` (GPIO3_A6, 3.3 V, through the 634 kΩ select resistor, v0.3) | shutdown | — | Device shutdown, no extra switch |
| Microphones + privacy LED | MIC_1V8 | TPS22945 (v0.5; current limit 100–200 mA) | SoC GPIO `MIC_EN` | off | QOD | LED gate driven by MIC_1V8 itself (BRD-027) |
| Faceplate logic | FP_VCI, FP_3V3, FP_1V8 | RK809 LDO4 → TPS22945; TPS22950 (FP_3V3); TPS22945 (FP_1V8) (v0.5; TPS22919 ×2 before) | RK809 I2C, expander `FP_IO_EN` (P00), which also switches FP_VCI at the connector (v0.5) | off | QOD | Panel and touch reset low first. v0.3 (decision 2026-10-24): off in suspend by default; the expander holds `FP_IO_EN`, so FP_3V3 can stay on for a faceplate wake (`FP_HID_INT_N`, PMUIO1); FP_1V8 follows vcc_1v8 |
| Backlight | BL_LEDA | TPS61160 CTRL (v0.5) | SoC PWM `BL_PWM` | off (1 µA) | — | ALS-driven |
| Status LED (RGB) | LED_R/G/B | LP5521 CHIP_EN bit, charge pump in power-save | I2C2 (`leds-lp5521`) | standby (1 µA, EN high, CHIP_EN = 0) | — | v1.2. EN tied to vcca1v8_pmu; works with the screen off and in suspend if the driver keeps it on |
| Wi-Fi/BT | vcc3v3_wl, vcc1v8_wl (v0.2) | TPS22919 (v0.3; RK809 SWOUT1 before); TPS62826 EN on vcc3v3_wl | expander P06 `WL_PWR_EN` (v0.3; holds through suspend) | off | TPS22919 QOD, TPS62826 output discharge (the 1 kΩ DNP footprint of G13 stays a spare) | Plus module PDn. VIO and SD_VIO on vcc_1v8 (VCCIO4, pinout v1 confirms it); sequencing between AVDD33, AVDD18 and VIO **UNVERIFIED** (datasheet), GPIO-EN option DNP. v0.3 (decision 2026-10-24): off in suspend by default; on in suspend only while item tracking is enabled, with vcc_1v8 kept on; `WL_PDN` hold through suspend open (BOM §7 item 40) |
| NFC reader (v0.2) | NFC_VBAT | TPS22919 | expander `NFC_PWR_EN` | off (pull-down) | QOD | VEN (native 1.8 V GPIO, pull-down) rises only after NFC_VBAT and falls before it (PN7160 §10.5.2.1); VDD(PAD) always on |
| IMU, TPM, NFC tag (v0.2) | vcca1v8_pmu | none (always on) | — | on | — | Low-power modes by software; measured by their links (§4.12) |
| Haptics (v0.2) | vcc3v3_sys | DRV2605L EN | expander `HAPTIC_EN` | off (pull-down) | — | G20 |
| microSD | vcc3v3_sd, vccio_sd | RK809 SWOUT2, LDO5 | RK809 I2C | per DT | **UNVERIFIED** | UHS-I voltage switch |
| RP2354A | RP_3V3, RP_IOVDD_1V8 | TPS22919 ×2 | SoC GPIO `RP_PWR_EN` | **open question** (§8) | QOD | SoC boots without it (BRD-019). VREG_VIN and VREG_AVDD share RP_3V3, so they ramp together (DS §6.1.8); IOVDD may come up in any order |
| NPU | vdd_npu | RK809 BUCK4 | DT | off | — | Enabled only by an AI overlay |
| GPU | vdd_gpu | RK809 BUCK2 | DT + devfreq | on with display | — | — |
| Camera PHY | LDO1, LDO9 | RK809 I2C | — | off | — | v0.7: the CSI-2 receiver has no consumer (RFC 0014); the LDOs stay off |
| USB3 PHY (HAT port) | SoC `PD_PIPE` | SoC power domain | USB host controller driver | off | — | v0.7: USB3 HOST1 to the HAT port; PCIe has no HAT consumer and the G14 gate is removed (RFC 0014). Earlier: `PCIE_PERST#` = SoC PERST# AND HAT_3V3 power-good |
| HAT 3.3 V | Removed in v0.7 (RFC 0014) | — | — | — | — | Expander P01 becomes `HAT_VBUS_DISCH` |
| HAT `VBUS` out | HAT_5V | TPS62903 5.1 V + TPS259470 #A | expander P02 `HAT5V_EN` (= `HAT_SRC_ON`), driven as the TCPM `vbus-supply` of the HAT port (v0.7) | off | eFuse | Same net forces TPS2121 OV2 |
| HAT `VBUS` in (source or dual-role HAT) | HAT_5V → VBUS_CHG | TPS2121 IN2 | OV2 (released when `HAT_SRC_ON` is low) | enabled | — | Dead-battery boot from a source HAT: the port controller's unpowered sink pull-down on `CC` (v0.7) |
| USB-C VBUS out | VBUS | TPS62903 5.1 V (v1.5) + TPS259470 #C | TCPM source role → `USB_SRC_ON` | off | eFuse | Forces TPS2121 OV1; on battery 1.5 A advertised with a compliant 2S pack while HAT_5V is idle (§4.6) |
| Instrumentation | vcc3v3_sys | INA236 power-down mode (I2C), five devices (v0.2) | Blackbird OS | power-down | — | Shunts and block links stay in circuit (§4.12) |

## 6. Sequencing

### 6.1 System power-up

1. A battery is present (or VBUS / powerbank HAT on TPS2121) → the BQ25798 regulates VSYS (v1.5): at VSYSMIN or above while an input source is present; on battery alone VSYS follows the 2S VBAT (6.0–8.8 V) less the BATFET drop. The TPS62136 (EN tied to VSYS) brings up VSYS_LV = 3.8 V, which feeds the PMIC, the vdd_cpu buck and vcc3v3_sys. Before v1.5: BQ25895 regulates VSYS: ≥ 3.5 V (VSYSMIN) only while an input source is present; on battery alone VSYS follows VBAT less the BATFET drop and can sit near 3.0 V.
2. Power button → RK809 PWRON. RK809-5 runs its OTP sequence. RK809-1 defaults (datasheet Table 4-1) step every 2 ms: BUCK5 (1) → BUCK1, BUCK2, LDO3 (2) → LDO1, LDO2 (3) → BUCK3 (4) → BUCK4, LDO4–6 (5). **The RK809-5 OTP table is UNVERIFIED** and must be read from Rockchip's RK3566 hardware design guide before the rail mapping is frozen.
3. vcc3v3_sys is already up: the TPS62826 (TLV62569 until v1.1) runs from VSYS_LV (v1.5; VSYS before) with EN tied high (BOM v1.1), as the 3.3 V rail of the ROCK 3C runs free, because it feeds RK809 VCC5–VCC9 (always-on LDO3, LDO6, LDO8 and BUCK5). EXT_EN is unused. eMMC VCC is therefore up before the BootROM reads it. Off-state cost: TPS62826 quiescent current (4 µA, SLVSEF9I) plus the RK809 input leakage; ship mode (BATFET off) removes it for storage. v0.2 (ADR 0017): storage uses the charger's shutdown mode after gauge SHUTDOWN, ≈ 1 µA typical, 4.7 µA maximum (§4.7); off but not in storage, the gauge adds ≈ 100 µA in SLEEP. v1.5: add the TPS62136 quiescent current (18 µA typ, 46 µA max, SLVSDV2) and the BQ25798 (17 µA typ).
4. v0.6 (ADR 0021): the TPS62869 brings vdd_cpu up at 0.9 V from EN (vcc3v3_pmu through 51 kΩ + 100 nF, ≈ 1.5 ms to the 0.84 V threshold, then tDelay and a 0.85–1.5 ms ramp), after VCC3V3_PMU as HDG 1.1 p. 34 orders; RESETB releases the SoC. That vdd_cpu is up before the RK809-5 releases RESETn is checked on the first boards (the RK809-5 OTP sequence is not public). Before v0.6: RK860-0 vdd_cpu powers up (EN tied per reference design), RESETB releases the SoC.
5. Everything behind a load switch or EN pin stays off until Linux (or U-Boot, for the display) turns it on.

### 6.2 Audio power-up (pop-free)

1. `DAC_VP_EN` (VP first, DS1156F2 §5.2).
2. `DAC_DIG_EN`, `AUDIO_LN_EN` (v0.3: both ST and `MCLK_DIV_RUN` low before these rails rise, ADR 0019 decision 6). Release `MCLK_DIV_RUN` while the oscillator net is held low, then raise one `MCLKxx_EN`. Wait for the XO start-up (≤ 4 ms) and LDO settling. A family change: DACs to their internal RCO (DS1156F2 §4.5), `MCLK_DIV_RUN` low, swap ST, repeat.
3. Release the CS43198 RESET (≥ 1 ms low pulse already done), program over I2C, keep outputs muted (Popguard).
4. `HPA_RAIL_EN`: the TPS65131 boost (ENP) and, through its level shifter, the LMR33630C (v1.6; TPS65131 current-limit ramp ≈ 1 ms, LMR33630C soft start 2.9–6 ms); **≥ 10 ms** later `HPA_LDO_EN` raises all four LDO EN/UV pins together, so the ±6 V rails ramp on equal RSET × CSET soft-starts, ≈ 65 ms (§4.2, OPA1622 §7.4.2). OPA1622 EN stays low.
5. After the rails are in regulation (a fixed delay: PG is unused because fast start-up is disabled), raise the OPA1622 EN for the selected output only.
6. Unmute with the DAC's soft ramp.

### 6.3 Audio power-down

Reverse order: soft-mute → OPA1622 EN low → rails off → CS43198 RESET low → ST low and `MCLK_DIV_RUN` low (v0.3) → VA/VCP/VL/VD off in any order (I2S lines parked low first) → VP off last.

### 6.4 HAT

**v0.7 (hat-standard interface v2, RFC 0014):**

1. The HAT port controller (FUSB302B01MPX, I2C1 0x23) watches `CC` with VDD on vcc3v3_pmu; an attach raises `HAT_PD_INT_N` (AG37, PMUIO1, wake-capable).
2. TCPM resolves the roles. A sink HAT (Rd): enable `HAT5V_EN` (5.1 V buck and eFuse #A; the same net forces TPS2121 OV2), offer 5 V within the budget of §4.6. A source or dual-role HAT offering power (Rp): keep `HAT5V_EN` low and sink through TPS2121 IN2 at 5 V (§8 item 30 for higher voltages); IN1 keeps priority.
3. USB enumeration on USB3 HOST1; Blackbird OS reads the identity capability from the USB descriptors (interface v2).
4. Detach or power-role swap: `HAT5V_EN` low, then `HAT_VBUS_DISCH` until `VBUS` is discharged; the OV2 interlock holds throughout.

Until v0.6 (interface v1.1, superseded):

1. Presence detect → `HAT3V3_EN` (TPS62903 3.3 V, v1.5, then eFuse #B) → read the HAT EEPROM (HCS-007).
2. Apply the overlay. Class A/B: assert `HAT5V_EN` (boost + eFuse #A; the same net forces TPS2121 OV2), within the battery budget of §4.6. Class F (powerbank): keep `HAT5V_EN` low and let TPS2121 select IN2 when USB-C is absent.
3. PCIe PERST# = SoC PERST# AND HAT power-good, released ≥ 100 ms after power-good (topology report §2.3). v0.2: the AND is an SN74LVC1G57 on vcc3v3_sys (BOM line 135), the delay an RC on the power-good input.
4. **v0.5 (hat-standard interface v1.1 §4.4):** for an L3 HAT, after the identity record: set `HAT_EXT_SEL` for the declared function (low PCIe, high CSI-2), enable `HAT_5V` if the class asks for it, pull `HAT_EXT_PD` low to connect the pairs (130 ns, SLASEW5A §5.7), then release `HAT_EXT_SB0` (the gate in step 3 still holds it until power-good + 100 ms). Removal and suspend in the reverse order: `HAT_EXT_SB0` asserted, `HAT_EXT_PD` high.

### 6.5 Suspend

- **v0.6 (ADR 0021): vdd_cpu stays on in suspend.** EN low resets the TPS62869's registers (SLVSFS3B p. 14) and the mainline `tps6286x` driver has no suspend operations, so the converter is not switched off as the reference boards switch theirs through VSEL. Cost: the converter's quiescent current plus the CPU cluster's leakage at the voltage left in place; not measured (**UNVERIFIED**). If it matters, a later revision gates EN from a rail that is off in suspend.
- Stay on: vdda0v9_pmu, vcca1v8_pmu (v0.2: with vcc1v8_ddr for the LPDDR4X VDD1 and the VDDQ LDO bias, the IMU, TPM, NFC tag, PN7160 VDD(PAD), expander VCCI and I2C2 pull-ups), vcc3v3_pmu, vcc_ddr + vcc0v6_ddr (self-refresh), RK809 RTC, BQ25798 and BQ28Z610-R1 (v1.5; BQ25895 and MAX17055 before), VSYS_LV (TPS62136), FUSB302B, IMU (wake on motion), vcc3v3_sys (eMMC stays powered: **open question**, could be dropped if the eMMC power-off notification is used).
- Everything in §5 goes to its default state. The OPA1622, DAC and oscillators are all off, so suspend audio cost is about 0.
- **v0.3, radio (decision 2026-10-24; BRD-030, T1-069):** vcc3v3_wl and vcc1v8_wl are off in suspend by default. While the listener enables Bluetooth item tracking, `WL_PWR_EN` (expander P06, which holds its outputs) keeps both on, and vcc_1v8 stays on too (RK809 sleep configuration), so the module VIO, SD_VIO and the VCCIO4 bank stay powered together and no module output drives an unpowered pad. Suspend draw with tracking on: **UNVERIFIED** until measured on M-RF (§4.12 links 11, 12). `WL_PDN` loses its state in standby (HDG p. 35): BOM §7 item 40.
- **v0.3, faceplate (decision 2026-10-24; T1-060):** FP_3V3 and FP_1V8 off by default; the T1 wakes from the body buttons on the always-on domain (power key on RK809 PWRON, Action on PMUIO2). The hardware can keep FP_3V3 on (`FP_IO_EN` on the expander) for a faceplate that wakes the T1 through `FP_HID_INT_N` (PMUIO1).
- **v0.3, HAT:** `HAT3V3_EN` on expander P01 keeps HAT_3V3 in its state through suspend. **v0.7:** HAT_3V3 is removed. The HAT port controller stays powered (vcc3v3_pmu) and its bus (I2C1, vcca1v8_pmu) stays up, so an attach or a `CC` event wakes the T1 through `HAT_PD_INT_N`; `HAT5V_EN` holds its state on the expander. A HAT's own wake request is USB remote wakeup on HOST1, whose behaviour from the T1's deep suspend is open (§8 item 31).

## 7. References

Datasheets with revision, date and sha256 are listed once, in the [BOM v1 Datasheets table](bom-v1.md#datasheets). The ones used for calculations here:

- TI OPA1622, SBOS727B (May 2016): <https://www.ti.com/lit/ds/symlink/opa1622.pdf>
- Cirrus Logic CS43198, DS1156F2 (Dec 2022): <https://www.cirrus.com/docs/ds/cs43198-datasheet.pdf>
- Rockchip RK809 datasheet Rev 1.01 (2018-08-28): <https://rockchip.fr/RK809%20datasheet%20V1.01.pdf>
- TI TPS65131, SLVS493E (Apr 2022): <https://www.ti.com/lit/ds/symlink/tps65131.pdf>
- TI LM27762, SNVSAF7C (Oct 2025): <https://www.ti.com/lit/ds/symlink/lm27762.pdf>
- TI TPS7A49, SBVS121E (May 2015): <https://www.ti.com/lit/ds/symlink/tps7a49.pdf> (part removed in v1.3)
- TI TPS7A30, SBVS125D (Jun 2015): <https://www.ti.com/lit/ds/symlink/tps7a30.pdf> (part removed in v1.3)
- ADI LT3045, Rev. D (Nov 2022), and LT3094, Rev. B (Jan 2020), read through a distributor mirror (BOM Datasheets table) (v1.3)
- TI TPS62826, SLVSEF9I (Mar 2024), Table 8-5 (v1.3 inductor): <https://www.ti.com/lit/ds/symlink/tps62826.pdf>
- TI TPS7A20, SBVS338H (Jul 2024): <https://www.ti.com/lit/ds/symlink/tps7a20.pdf>
- TI TPS7A94, SBVS336C (Jun 2023): <https://www.ti.com/lit/ds/symlink/tps7a94.pdf>
- TI TPS62840, SLVSEC6D (Mar 2020): <https://www.ti.com/lit/ds/symlink/tps62840.pdf>
- TI TPS61169, SNVSA40B (Jun 2024): <https://www.ti.com/lit/ds/symlink/tps61169.pdf>
- v0.5 additions: TI TPS61160, SLVS791E (Jul 2016); TPS22950, SLVSFJ2B (Feb 2023); TPS22945, SLVS832D (Jul 2014); TMUXHS4412, SLASEW5A (Oct 2024); TPS25947, SLVSFC9C (May 2026) and TPS2121, SLVSEA3F (Aug 2020) re-read for the trip tolerances; Hirose DF40 catalog (May 1, 2020) pp. 2, 4, 10; RK809 datasheet Rev 1.01 (LDO4); NXP UM10204 (I2C rise time). Hashes in the BOM Datasheets table.
- TI TPS25947, SLVSFC9C (May 2026): <https://www.ti.com/lit/ds/symlink/tps25947.pdf>
- TI TPS2121, SLVSEA3F (Aug 2020): <https://www.ti.com/lit/ds/symlink/tps2121.pdf>
- TI BQ25895, SLUSC88C (Oct 2022): <https://www.ti.com/lit/ds/symlink/bq25895.pdf> (part removed in v1.5)
- BOM v1.5 additions ([ADR 0014](../adr/0014-two-cell-battery.md), ADR 0014): TI BQ25798, SLUSDV2C (Jun 2026): <https://www.ti.com/lit/ds/symlink/bq25798.pdf>; TI BQ28Z610-R1, SLUSE07B (Jan 2022): <https://www.ti.com/lit/ds/symlink/bq28z610-r1.pdf>; TI TPS62136, SLVSDV2 (Mar 2017): <https://www.ti.com/lit/ds/symlink/tps62136.pdf>; TI TPS62903, SLVSES3A (Mar 2021): <https://www.ti.com/lit/ds/symlink/tps62903.pdf>; Coilcraft XGL4020 (Document 1529, rev. 2026-02-19) and XEL4020 (Document 1302); Littelfuse 451/453 (Revised 06/15/17); Vishay WSL (Document 30100, Rev. 23-Nov-2023). Hashes in the BOM Datasheets table.
- TI TPS7A10, SBVS314B (Oct 2018): <https://www.ti.com/lit/ds/symlink/tps7a10.pdf>
- TI TVS2200, SLVSED5C (Aug 2023): <https://www.ti.com/lit/ds/symlink/tvs2200.pdf>
- NDK NZ2520SDA catalog 1703A: <https://www.ndk.com/images/products/catalog/c_NZ2520SDA_e.pdf>
- Focus LCDs E35GH-I-MW800-CB spec rev 1.0: <https://focuslcds.com/wp-content/uploads/2025/09/E35GH-I-MW800-CB_Spec.pdf>
- Raspberry Pi, Hardware design with RP2350 (build 2026-08-20): <https://datasheets.raspberrypi.com/rp2350/hardware-design-with-rp2350.pdf>
- Reference designs: Radxa ZERO 3W schematic v1.12 <https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_v1.12_schematic.pdf>; mainline DTs [`rk3566-orangepi-3b.dtsi`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-orangepi-3b.dtsi) (RK809 + SYR827) and [`rk3566-anbernic-rgxx3.dtsi`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-anbernic-rgxx3.dtsi) (RK817 + FAN53555-class vdd_cpu, handheld battery power), read 2026-10-22.
- BOM v1.1 additions: TI TPS61089, SLVSD38C (Aug 2021): <https://www.ti.com/lit/ds/symlink/tps61089.pdf> (part removed in v1.5); Radxa ROCK 3C schematic v1.4 (2024-03-05, RK809-5): <https://dl.radxa.com/rock3/docs/hw/3c/v1400/radxa_rock_3c_v1400_schematic.pdf>; mainline [`rk3566-rock-3c.dts`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-rock-3c.dts) and [`rk3566-odroid-m1s.dts`](https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/rockchip/rk3566-odroid-m1s.dts), read 2026-10-22; JST PH catalog (ePH): <https://www.jst-mfg.com/product/pdf/eng/ePH.pdf>.
- v0.2 additions: Murata E2B-09-1413 Rev. 9.0 and Embedded Artists 2EL/2DL M.2 datasheet PA4 (through the parts-lib LBES5PL2EL-923 sheet); NXP PN7160/PN7161 data sheet Rev. 3.4 (4 August 2022; read from a distributor mirror, sha256 in the BOM Datasheets table); TI SN74LVC2G66, SCES325N (Aug 2018); TI SN74LVC1G58, SCES415N (Dec 2013); TI TPS22919, SLVSEN5B (May 2019); Rockchip RK3566 Hardware Design Guide V1.1.0 (2022-02-06) pp. 23, 34–35, 38–40; reference schematics Radxa ZERO 3W v1.12 (sheet 14), Radxa ROCK 3C v1.4 (sheets 16, PMIC), Pine64 Quartz64-A v2.0 (LPDDR4 sheet); mainline `rk3566-rock-3c.dts` (read 2026-10-24); [ADR 0017](../adr/0017-fuel-gauge-wiring-sense-resistor-and-configuration.md).
- v0.3 additions: TI SN74AUC1G74, SCES537D (Jun 2007); NDK NZ2520SDA catalogue (49.152 MHz rows); TI TPS62827 in SLVSEF9I (Mar 2024) pp. 4–6, 13–14; Rockchip RK3566 Hardware Design Guide V1.1.0 pp. 17, 30–32, 35, 53, 59; [pinout v1](pinout-v1.md); [ADR 0019](../adr/0019-master-clock-divided-from-twice-the-frequency.md) and `sim/mclk-divider`.
- v0.4 additions ([ADR 0020](../adr/0020-battery-connected-through-contacts.md)): KYOCERA AVX TDS-BTB-0026 Rev 1 (9258-100, 2025-09-10) and drawing 70-9258-001-1X0-00XS Rev F; TI SLUSDV2C §6.5, §7.3.12, Figure 8-2 notes; TI SLUUCB5E §1; TI SLPS489A p. 2. KYOCERA AVX product specification 201-01-252 not obtained.
- v0.6 additions ([ADR 0021](../adr/0021-vdd-cpu-buck-ti-tps62869.md), [ADR 0022](../adr/0022-lpddr4x-micron-mt53e1g32d2fw-with-cxmt-second-source.md)): TI TPS62868/TPS62869, SLVSFS3B (Jul 2021): <https://www.ti.com/lit/ds/symlink/tps62869.pdf>; Coilcraft XGL4012 (Document 1718, revised 2026-08-27); Micron z42n LPDDR4X/LPDDR4 data sheet Rev. C (Feb 2023); CXMT CXDB5CBAM-MA-B datasheet Version 1.0 (2024-04-17); RK3566 DS 1.1 pp. 51–52; HDG 1.1 pp. 34, 36, 38. Hashes in the BOM Datasheets table.
- Not retrieved this session: Rockchip RK3566 hardware design guide and reference schematic, Pine64 Quartz64/SOQuartz schematics, Cirrus CDB43198 eval board, TI BQ25895 EVM guide, onsemi FUSB302B app note, ADI MAX17055 EV kit, Murata Type 2EL hardware guide. Their content is not used above.

## 8. Open questions

1. **BRD-023 frequencies:** closed (22.5792/24.576 MHz, BRD-023 corrected).
2. **Output targets:** closed in v1.3 by ADR 0012 (full-scale output into low-impedance headphones; paralleled halves on every package, §4.1).
3. **MCLK:** 3.3 V NSC5083D with a passive attenuator into the 1.8 V XTI input (ADR 0010); SPICE check pending. **v0.3: closed by [ADR 0019](../adr/0019-master-clock-divided-from-twice-the-frequency.md)** (divide-by-two from twice the frequency); open on the first boards: the divider's additive phase noise, the NSC5083D phase noise at 45.1584 MHz and 3.1 V, opposite-phase divider start.
4. **RK809-5 OTP sequence:** confirm with Rockchip (or the RK3566 hardware design guide) the OTP defaults. VCC5–VCC9 on vcc3v3_sys follows the ROCK 3C v1.4 (RK809-5) and three mainline device trees; feeding VCC1–VCC4 from VSYS follows the datasheet application circuit only.
5. **Is the NPU supply separate on the RK3566 (BUCK4) or shared with the GPU** as on RK817 handhelds? This decides whether BUCK4 is free.
6. **RP2354A power default:** on at boot (always-available orchestrator) or off until Blackbird OS enables it (lowest standby)?
7. **Backlight driver location:** main board (proposed, keeps faceplates passive) or on each faceplate?
8. **HAT power classes and the battery (v1.2):** the board carries the full output budget (§4.6–4.7); the interim pack still leaves about 0.4 A at 5.1 V on battery. ADR 0011 (Proposed) sets the pack criteria; no available pack meets them yet. Accept ADR 0011 and its budget definition, and choose a fallback if no pack is found. **v1.5: closed by [ADR 0014](../adr/0014-two-cell-battery.md)** (2S pack, full budget ≈ 2.4 A at VSYS 6.6 V); open: two independent pack makers.
9. **eMMC power in suspend:** keep vcc3v3_sys on, or power the eMMC down in suspend?
10. **HP-amp +5 V LDO (v1.2):** closed in v1.3 by ADR 0012 (LT3045/LT3094 at ±6 V, 55 %).
11. **TPS65131 inverter (v1.3, ADR 0012 condition):** simulate at VIN 3.0 V, ±7 V, 275 mA per rail before layout freeze, or replace the inverter (§4.10.1). **Updated 2026-10-24: superseded by [ADR 0015](../adr/0015-amplifier-rails-from-vsys.md)**: simulated ([output-stage simulation](../../sim/output-stage/README.md)); the inverter half is not used and −7 V comes from the LMR33630C (item 15).
12. **Headphone and HAT power on an ADR 0011 pack (v1.3):** budget them together, or grow the full output budget (§4.11)? **v1.5: resolved by ADR 0014**: the battery path covers the combined ≈ 3.2 A at VSYS 6.6 V (pack ≥ 4.0 A, 5 A fuse; §4.7).
13. **BQ25798 driver and gauge configuration (v1.5, ADR 0014):** the BQ25798 on the mainline `bq257xx` driver, Debian's `BATTERY_BQ27XXX_I2C` on arm64, and the BQ28Z610-R1 gauge-only configuration (BOM §7 items 21–22). Updated 2026-10-24: the register map matches the BQ25792 and the binding is already in linux-next, so no ID needs sending; `BATTERY_BQ27XXX_I2C` is not set on Debian arm64 (DKMS) (ADR 0014 item 5). Open: the gauge-only configuration.
14. **VSYS_LV voltage (v1.5):** 3.8 V keeps every former 1S part inside the range it was chosen for; a higher value (up to about 5.0 V) would help the TPS65131 and the speaker amplifier, with more MCLK LDO and DAC_VP losses. Left at 3.8 V.
15. **−7 V inverter (v1.5):** closed in v1.6 by [ADR 0015](../adr/0015-amplifier-rails-from-vsys.md) (LMR33630C from VSYS). Open: the TPS65131 single-output connection with TI, and the bench items of BOM §7 items 29–31.

16. **Radio rail sequencing (v0.2):** AVDD33 and AVDD18 rise together from one switch; the module datasheet decides whether an order is needed (GPIO-EN option on BOM line 131).
17. **vcca1v8_pmu load (v0.2, §4.13):** ≈ 157 mA (est.) with a 100 mA VDD1 allowance; measure, and fit the dedicated VDD1 LDO if needed.
18. **vcc_ddr setpoint and the VDDQ LDO headroom (v0.2, §4.8):** keep 1.113 V (ROCK 3C values) or move toward 1.125 V once the memory's VDD2 window is known.
19. **IO-domain assumptions (v0.2), to reconcile with pinout v1 (v0.3: closed: every one holds, pinout v1 §9.1; `HAT3V3_EN` moved to expander P01):** radio VIO/SD_VIO on vcc_1v8 (VCCIO4); PN7160 VEN/DWL_REQ, TPM reset/PIRQ and the tag's FD on native 1.8 V GPIO; RP2354A taps on FT GPIO; SoC PERST# at 3.3 V (VCCIO1).
20. **Radio in suspend (v0.3):** the suspend draw with tracking on (M-RF), the `WL_PDN` hold through standby and the module's rail order (BOM §7 item 40).
21. **`MCLK_DIV_RUN` ball (v0.3):** not in pinout v1 (BOM §7 item 39).
22. **USB PHY 3.3 V supplies (v0.3, B16):** vcc3v3_sys assumed; the reference schematic's choice is **UNVERIFIED**.
23. **Battery contacts (v0.4, ADR 0020):** the contact resistance at end of life, the rating basis and the force (KYOCERA AVX product specification 201-01-252), the sharing factor of a pole (CB-01), the contact temperature at 3.2 A and 5 A (CB-02), the insertion transient on BAT and BATP (CB-07) and whether the P+ TVS is fitted (§4.7.1, BOM §7 item 42).
24. **HAT limiters (v0.5):** the TPS2121 limit spread at 45.3 kΩ (TI characterises other values only) and the 0.1 % resistor's availability; measure the trip on the first boards against 3.0 A.
25. **Faceplate rail switches (v0.5):** the TPS22945 limit at 1.8 V (FP_1V8, MIC_1V8) and 2.8 V (FP_VCI), which TI specifies at 3.3 V only; the TPS22950 spread at 3.57 kΩ (interpolated); the RK809-5 OTP state of LDO4.
26. **Backlight above an 18 V string (v0.5):** from VSYS_LV the TPS61160 cannot guarantee 60 mA above ≈ 18 V with margin (§4.5); a faceplate with a longer string declares less current, or the driver input moves to VSYS (2.7–18 V input rating allows 6.0–8.8 V), to study with that faceplate.
27. **vdd_cpu on the first boards (v0.6, ADR 0021):** the C option's VOUT register, the load step at the SoC with the remote sense, vdd_cpu before RESETn, the cluster's peak current on the H5 link, the suspend draw with vdd_cpu on, the efficiency at 3.8 V and 0.15 A (BOM §7 item 43).
28. **LPDDR4X currents (v0.6, ADR 0022):** transcribe the Micron IDD tables (z42n pp. 50–57) into the VDD1 allowance of §4.13 and the VDDQ estimate of §4.8 (BOM §7 item 33).
29. **Closed (v0.8, RFC 0015): eFuse #D bounds the buck at 2.520 A, 84 % (Changes in v0.8 item 1).** Was: **5.1 V buck in a double eFuse fault (v0.7):** with RILM 1.87 kΩ both eFuses at their 1.981 A maximum trip reach 3.96 A, 132 % of the TPS62903's 3 A rating and 99 % of its 4.0 A minimum high-side limit. Software keeps the sum at the 1.6 A design; the case is a thermal check for the board model.
30. **Closed (v0.8, RFC 0015): 5 V only; OV2 at 5.60–6.31 V (Changes in v0.8 item 2).** Was: **PD voltages accepted from a HAT (v0.7, RFC 0014):** the HAT port sinks 5 V until the maintainers decide. Above 5 V: the TPS2121 OV2 threshold, a `VBUS` TVS rated for the voltage (TVS0500: 5 V stand-off, 7.5 V minimum breakdown, SLVSED2C §7.4, §7.6), and `CC` protection against a short to `VBUS` (the FUSB302B `CC` pins are rated 6.0 V absolute maximum, FUSB302B/D Rev. 5 p. 14).
31. **USB3 HOST1 remote wakeup from deep suspend (v0.7, RFC 0014):** the HAT's wake path; whether the RK3566 keeps HOST1 able to wake the system in its deep standby is **UNVERIFIED**.

## 9. Risks

1. **SoC power is unmeasured.** The 450–800 mW SoC estimate dominates the runtime figure; a ±30 % error moves runtime by hours. *Mitigation:* measure on a Radxa ZERO 3W or Quartz64 with mainline 7.2 and the INA236 plan.
2. **RK809-5 OTP defaults unknown.** A wrong mapping can put a wrong voltage on a rail at boot. *Mitigation:* the VCC feeds and rail names copy the ROCK 3C v1.4 (RK809-5); confirm the OTP table with Rockchip.
3. **TPS65131 output current at low battery** is read from a curve, not a table, and v1.3 puts the inverter at 79 % of its minimum switch limit at VIN 3.0 V. *Mitigation:* SPICE/WEBENCH at VIN = 3.0 V, ±7 V, 275 mA per rail (ADR 0012); the interim ceiling of §4.11 lowers the load on the Adafruit 328; a converter with more margin is the fallback. v1.5: from the regulated 3.8 V VSYS_LV the inverter sits at 68 % (§4.10.1). v1.6: the inverter is no longer used ([ADR 0015](../adr/0015-amplifier-rails-from-vsys.md)); the remaining risk is the boost at ≈ 99 % in the positive LDOs' maximum-trip case.
4. **OPA1622 parallel halves** (v1.3: every package) are not described by TI. *Mitigation:* simulate current sharing and stability with the 1.0 Ω ballast and 400 pF loads (TINA-TI model availability **UNVERIFIED**), then measure maximum power, THD+N and output impedance on the first board.
5. **VBUS surge coordination:** TVS2200 clamp at 40 A (28.4 V) is above the TPS2121 (24 V) and BQ25895 (22 V) absolute maxima (v1.5: the BQ25798 VBUS absolute maximum is 30 V, so the TPS2121 is the limit). *Mitigation:* decide whether IEC 61000-4-5 applies to the USB-C port; if it does, add series OVP or choose a lower-clamp TVS with a 14 V standoff and accept the 20 V fault case.
6. **Self-feeding loops** through TPS2121 IN1/IN2 when the T1 sources 5 V. *Mitigation:* hardware OR of `USB_SRC_ON`/`HAT_SRC_ON` into OV1/OV2 (finding 11); verify the OV pin drive levels against SLVSEA3F.
7. **MCLK attenuator** (ADR 0010): the edge at XTI must stay within the VL input limits. *Mitigation:* SPICE with the CS43198 input capacitance before layout freeze; J-test captures on the first boards. v0.3: the attenuator is replaced by the dividers of [ADR 0019](../adr/0019-master-clock-divided-from-twice-the-frequency.md); the risk is now their unpublished additive phase noise and supply sensitivity. *Mitigation:* MCLK phase noise at XTI, inter-channel delay, J-test and THD+N on the first boards; fallback in ADR 0019 decision 7.
8. **Battery current limit** (1.6 A, JST PH derated for 26 AWG, interim pack). *Mitigation:* software power budget on the VSYS INA236 and, from v1.2, a 2.5 A fuse; screen-on + CPU peak + HAT load must be measured; a pack meeting ADR 0011 for the full budget. v1.5: superseded by ADR 0014 (≈ 3.2 A worst case through a Micro-Fit 3.0 and a 5 A fuse). New risk: the pack is made to order and needs two independent makers building to the ADR 0014 specification; bring-up runs on a bench supply.
9. **0.6 V LPDDR4X rail sizing** is an estimate. *Mitigation:* Rockchip guide, Radxa/Firefly LPDDR4X schematics.
10. **Thermal:** RK3566 + RK809 + TPS62869 (v0.6; RK860 before; ≈ +18 °C at 3 A, est., ADR 0021) + charger in a 25 mm sealed body; not modelled. *Mitigation:* thermal simulation once the board outline exists.
11. **vcc3v3_sys peak** (1.85 A est.): closed in v1.2 by the 3 A TPS62826 (62 %). *Mitigation:* re-sum from the schematic; the 4 A TPS62827 is pin- and BOM-compatible. v0.3: the re-sum (≈ 2.45 A, est.) passed 80 %; the TPS62827 is fitted (61 %).
12. **Ratings not yet published** for the RK860-0 and the RK809 BUCK1–4 peak loads of the RK3566 (§4.10). *Mitigation:* measure on a reference board; RK860 datasheet from Rockchip. v0.6 (ADR 0021): the vdd_cpu converter is now the TPS62869 with a published 6 A rating (50 % at the 3 A estimate); the RK3566 vdd_cpu peak current stays **UNVERIFIED** (Rockchip's power report is not public), and the RK809 BUCK1–4 peaks are unchanged.
13. **Interim-pack output ceiling** depends on Blackbird OS (§4.11). *Mitigation:* the 2.5 A battery fuse still bounds a software failure (§4.7); the ceiling acts on the measured VSYS current. v1.5: removed with the interim pack (ADR 0014 item 3).
14. **2S software path (v1.5; updated 2026-10-24):** the BQ25798 binding is in linux-next but not yet in master, and Debian builds neither `MFD_BQ257XX`/`CHARGER_BQ257XX` nor `BATTERY_BQ27XXX_I2C` for arm64 (ADR 0014 item 5). *Mitigation:* DKMS (ADR 0014 item 5, OS-023) until upstream and Debian carry them.
15. **TPS62903 5.1 V thermal (v1.5):** ≈ 0.6 W at 8.16 W out (est.) in a 1.5 × 2 mm package, ≈ +44 °C at the EVM's 73.5 °C/W. *Mitigation:* copper and placement in the board thermal model; the full budget is a worst case, not a playback load.
16. **VSYS_LV coincident peaks (v0.2):** the TPS62136 reaches 81 % of its minimum switch limit if the system peak, the radio's calibration peak and the NFC reader coincide (§4.10). *Mitigation:* all three are estimates; measure on the VSYS_LV link (§4.12); the radio calibrates at module power-up, which software can keep apart from NFC polling.
17. **LPDDR4X self-refresh (v0.2):** fixed by design (finding 15); confirm suspend and resume with memory intact at bring-up.
18. **Battery contact pressure after drops (v0.4, ADR 0020):** the recorded failure of contact battery interfaces is loss of contact pressure after a drop (generic method §1.2), which resets the T1 on battery. *Mitigation:* the back cover's foam preloads the pack above the six contact forces; drop tests with event detection on BAT (CB-04); the BAT node's 2 × 10 µF and the system capacitance ride through a short opening only as far as CB-04 shows (**UNVERIFIED**).
