# Main board feature blocks

- **Status:** Draft v0 (2026-10-24). Applies [RFC 0011](https://github.com/opendap-project/rfcs/blob/main/text/0011-feature-blocks-and-variants.md) (feature blocks and variants, amended 2026-10-24: promises are fixed, parts are not) and [RFC 0010](https://github.com/opendap-project/rfcs/blob/main/text/0010-quality-levels.md) (quality levels). Nothing here is drawn, built or measured. No decision, priority or requirement status changes here: every proposal below is input for the schematic and for the maintainers.
- **Updated 2026-10-24 (BOM v1.9, power tree v0.3):** records `blk.gpio-expander`, `blk.gauge`, `blk.hat-3v3`, `blk.hat-audio`, `blk.fp-connector`, `blk.fp-controls`, `blk.mclk`, `blk.radio` and `blk.rp2354` follow [ADR 0019](../adr/0019-master-clock-divided-from-twice-the-frequency.md), [pinout v1](pinout-v1.md) and three decisions taken on 2026-10-24 (radio in suspend for item tracking, faceplate supply in suspend, 802.15.4 balls); gaps G3, G8, G13 and G14 updated in §7.
- **Updated 2026-10-24 (BOM v1.10, power tree v0.4):** [ADR 0020](../adr/0020-battery-connected-through-contacts.md) (battery connected through contacts): the `blk.charger` record takes the six battery contacts (interface, absent state, alternates), and a new should block, `blk.cover-detect` (#50), is added to the catalog and to the three variant files (fitted in each).
- **Updated 2026-10-24 (BOM v1.11, power tree v0.5):** hats `standard/` interface v1.1 and its [ADR 0005](https://github.com/opendap-project/hats/blob/main/standard/docs/adr/0005-interface-v1-1-shared-extension-and-contact-reduction.md): `blk.hat-signals` (one DF40C-100, the two extension switches, `EXT_SB0`–`EXT_SB2`, SWD as a GPIO alternate), `blk.hat-5v` and `blk.hat-3v3` (single connector, fault ceilings 3.0 A and 1.5 A). The t1 faceplate interface v1 (t1 ADRs 0004, 0005): `blk.fp-connector`, `blk.fp-display`, `blk.fp-backlight`, `blk.fp-controls` (identity node in the devicetree, I2C3 pull-ups) and `blk.mic-main` (current-limited rail switches, TPS61160). No block is added or removed and no variant state changes, so the variant files are unchanged.
- **Updated 2026-10-25 (BOM v1.12, power tree v0.6):** [ADR 0021](../adr/0021-vdd-cpu-buck-ti-tps62869.md): the `blk.vdd-cpu` record takes the TI TPS62869 at I2C0 0x42 (decision item 8). [ADR 0022](../adr/0022-lpddr4x-micron-mt53e1g32d2fw-with-cxmt-second-source.md): `blk.lpddr4x` holds single-rank parts on the shared land, its 4 GB alternate becomes the CXMT CXDB5CBAM-MA-B, and gap G18 is closed for 4 GB. The [HAT flat cable](hat-flat-cable.md) spec (§17 B8): `blk.hat-signals`, `blk.hat-5v` and `blk.hat-3v3` name the DF40C-100DS receptacle on the board and the cable per that spec. No block is added or removed and no variant changes.
- **Updated 2026-10-25 (BOM v1.13, power tree v0.7, [RFC 0014](https://github.com/opendap-project/rfcs/blob/main/text/0014-hat-interface-v2-usb-only.md)):** HATs are USB only (hats `standard/` [interface v2](https://github.com/opendap-project/hats/blob/main/standard/docs/specs/interface-v2.md), [ADR 0006](https://github.com/opendap-project/hats/blob/main/standard/docs/adr/0006-hats-are-usb-only.md)). `blk.hat-5v` becomes the HAT `VBUS` source and sink with the HAT port's Type-C port controller (USB PD); `blk.hat-signals` carries USB 3, `D±` and `CC` with two ESD parts, no switches and no ID translator; `blk.hat-3v3` and `blk.hat-audio` are removed (records kept as removed; the variant files drop them); gap G14 closes by removal. The HAT connector parts (BOM lines 66, 67, 102) follow the open connector decision.
- **Updated 2026-10-28 (variant tool):** every record whose block has a devicetree node names it in its Software row (`` `<label>` node ``): the mainline RK3566 labels (`sdhci`, `sdmmc0`, `sdmmc1`, `uart0`, `i2c3`, `dsi0`, `pdm`, `usb_host1_xhci`) and the board devicetree's labels, which that devicetree takes when it is written; `odapkit variant apply` disables these nodes for an unfitted block. The absent-state pulls of `blk.rp2354` and `blk.hpa-rails` sit on the host side (`blk.soc-vccio-b`), so they stay when the block is not fitted; `blk.cover-detect` relies on the SoC ball's own reset pull-down.
- **Updated 2026-10-28 (BOM v1.20):** `blk.shields` has its sheet: two etched two-piece frames (SoC and LPDDR4X, radio module; the frame over the DACs and headphone stage of BOM v1.19 dropped in v1.20), not fitted in either variant, as the variant files had it. No block is added or removed.
- **Updated 2026-10-28 (BOM v1.18 item 8, power tree v0.10, [ADR 0026](../adr/0026-vdd-cpu-buck-ti-tps62870z4.md)):** the `blk.vdd-cpu` record (#13) takes the TPS62870Z4 with differential sense; the 1100 mV cap stays. No block is added or removed.
- **Updated 2026-10-27 (BOM v1.18 item 7, power tree v0.10, maintainer decision):** `blk.nfc-reader` (#42) withdrawn for board area, in every model; BRD-057 reworded: NFC as the tag only; `blk.nfc-tag` (#41) does not depend on the reader and stays. Both variant files drop the block; expander P05 becomes a spare (`blk.gpio-expander` record).
- **Updated 2026-10-25 (`blk.vdd-cpu`):** the software field records the BRD-049 safety limit `regulator-max-microvolt = <1100000>` and the bring-up condition that lifts it; one 22 µF more at the vdd_cpu balls.
- **Purpose:** the T1 main board's block catalog: one record per function of [BOM v1.7](bom-v1.md), with what it is bound by, its interface, power domain and switch, measurement point, absent state, swap classes, alternates and software. Then the variant file format and the three T1 variant files, what KiCad 10 offers for variants, the absent-state check, and the gaps the schematic must close.
- **Inputs:** [BOM v1.7](bom-v1.md), [power tree v0](power-tree-v0.md), [PCB design constraints](pcb-design-constraints.md) v0.5, [pinout v1](pinout-v1.md), [board requirements](../requirements/README.md), [ADR 0013](../adr/0013-production-variant.md) (production variant), [ADR 0016](../adr/0016-front-side-height-under-the-display.md) (front-side height), the system [hardware support spec](https://github.com/opendap-project/blackbird/blob/main/system/docs/specs/hardware-support.md) (layers H0–H5, device description), the t1 [faceplate interface](../../../product/docs/specs/faceplate-interface.md) and the hats `standard/` [HAT interface v1](https://github.com/opendap-project/hats/blob/main/standard/docs/specs/interface-v1.md).
- **Conventions:** "line N" is a BOM v1.7 line. **UNVERIFIED** marks what no primary source in this repository confirms yet; each one names what closes it. "Gap Gn" refers to the table in §7.

## 0. Summary

1. **50 blocks** cover every BOM v1.7 function, plus the cover detect of BOM v1.10 (`blk.cover-detect`, #50; 49 blocks until then) (§2, §3). 2026-10-25: 48 in use, `blk.hat-3v3` (#17) and `blk.hat-audio` (#20) removed (RFC 0014); 2026-10-27: 47 in use, `blk.nfc-reader` (#42) withdrawn (maintainer decision, board area); their numbers are not reused. Blocks nest where a swap needs a wider boundary than a fit: the audio converter boundary (`blk.audio`) holds the DACs, clocks, supplies and amplifiers, so another DAC family or output stage in another variant replaces what sits behind I2S/TDM/DSD, clocks, the control bus, supplies and the jack nets, never the rest of the board.
2. **Bound by, not fixed.** Following RFC 0011 rule 5, no block is structurally fixed. Each record names the requirements and promise any replacement must meet (for example T1-040 at 100 %, BRD-049 margins). Must requirements of a variant's declared promise keep their block fitted (or replaced by an alternate that meets them) in every product variant.
3. **Power and measurement are incomplete today.** Four should blocks have no usable switch or enable (IMU, TPM, NFC tag, and the haptic driver, whose enable has no GPIO), 20 blocks have no measurement point of their own, and only 4 current-sense channels exist (VSYS, "audio", "display", HAT 5.1 V), two of them with no defined position. §7 proposes a 0 Ω link plus shunt footprint with Kelvin pads per block supply, and load switches only where the off state matters.
4. **Five absent-state risks need hardware, not software:** the two CS43198 sit on the shared 1.8 V I2C2 while their digital supply is switched (back-powering through the control port, G2); the master clock can drive the DAC XTI pins with the DAC unpowered (G3); the RP2354A taps the live I2S nets while its own supply is switched (G4); the IMU is on `vcc_1v8`, which is off in suspend, yet it is the wake-on-motion source (G1); the PN7160 is fed "from the battery path", 6.0–8.8 V on the 2S tree, and takes a 3.3 V expander line on a 1.8 V pin (G7; withdrawn with the reader on 2026-10-27).
5. **Variant files** (`hardware/variants/*.toml`, §4) list every block with `fit`, `dnp` or `alternate`, parameters and open decisions. `full` fits everything; `production` follows ADR 0013 with instrumentation links as 0 Ω.
6. **KiCad 10.0.7 has design variants** (tested, §5): per-variant DNP, BOM and position-file exclusion, field overrides and sheet-level DNP, honoured by the BOM, schematic plots, position files, Gerbers and 3D exports. It does not cover devicetree, the device description, the verification plan or an absent-state check: ERC and DRC take no variant, and the S-expression netlist is identical across variants. The TOML files therefore stay the source: KiCad's variant overrides are written from them, and the absent-state check (§6) runs on the XML netlist, which carries every variant's overrides.

## 1. Block discipline on this board

- **One sheet per block.** Each block is one hierarchical sheet (`sheet` field) and one layout block of the same name. Every symbol carries a `Block` field with the block ID, so tools resolve blocks without parsing sheet names.
- **Absent-state parts live outside the block.** The pulls, straps and isolation that define a block's absent state sit on the host side of the boundary (the bus owner or the connector sheet), so a block marked DNP never removes its own safe state.
- **Interface names are connector-style** (hardware support spec, connector rule): buses, enables, interrupts, clocks and supplies by function, never by SoC ball. Ball assignments stay in the pin plan.
- **Boundaries are drawn for the largest plausible swap** (RFC 0011 rule 6). Each record lists the swap classes its interface holds and those that would need a block revision.
- **Levels.** No block has reached a level: nothing is drawn. Every block targets **Q1** for prototype 1 (RFC 0010; PCB design constraints). Q0 items (protection, fab and electrical rules, battery safety) are the floor for any powered board. The `Level` row says "— / Q1" (reached / target).

## 2. Catalog overview

Priority is the requirement's own (must / should) as recorded in its requirements file; "none recorded" means no requirement names the function, and the BOM status applies. Switch: the element that removes power from the block. Measure: the current-sense point; "G11/G12" marks a proposed one.

| # | ID | Function | Bound by (priority) | Switch / enable today | Measure today | full | production |
|---|---|---|---|---|---|---|---|
| 1 | `blk.soc` | RK3566, 24 MHz crystal | BRD-002, BRD-003, BRD-004 (must) | RK809 sequence | VSYS channel only | fit | fit |
| 2 | `blk.lpddr4x` | 4 GB LPDDR4X, VDDQ LDO | BRD-037 (must) | RK809 BUCK3 | none (G12) | fit | fit |
| 3 | `blk.emmc` | eMMC | BRD-037, BRD-043 (must) | none (always on) | none (G12) | fit 32 GB | open: 16 / 32 GB |
| 4 | `blk.microsd` | microSD socket, ESD | BRD-038, BRD-043, BRD-051 (must) | RK809 SWOUT2, LDO5 | none (G12) | fit | fit |
| 5 | `blk.board-id` | Board EEPROM | none recorded (BOM Proposed) | none | none | fit | fit |
| 6 | `blk.gpio-expander` | TCA6416A | infrastructure for BRD-008, BRD-019 | none (always on) | none | fit | fit |
| 7 | `blk.charger` | TPS2121, BQ25798, ship FET, fuse, six battery contacts and their ESD (v1.10), NTC | BRD-007, BRD-049, BRD-050 (must), ADR 0014, ADR 0020 | ship FET (BQ25798 SDRV) | VSYS channel | fit | fit |
| 8 | `blk.gauge` | BQ28Z610-R1, sense resistor | BRD-049 (must), ADR 0014 | none (always on) | its own sense resistor | fit | fit |
| 9 | `blk.usb-c` | USB-C, ESD, CC/SBU protection, FUSB302B, VBUS TVS | BRD-018, BRD-034, BRD-039, BRD-044 (must) | none (always on) | none | fit | fit |
| 10 | `blk.pwr-vsys-lv` | TPS62136 3.8 V pre-regulator | BRD-049 (must), ADR 0014 | none (EN = VSYS) | none (G11) | fit | fit |
| 11 | `blk.pwr-3v3-sys` | TPS62826 3.3 V | BRD-049 (must) | none (always on) | none (G12) | fit | fit |
| 12 | `blk.pmic` | RK809-5 and its inductors, RTC crystal | BRD-020 (must, Draft) | PWRON / OTP sequence | none | fit | fit |
| 13 | `blk.vdd-cpu` | TPS62870Z4 (v1.18, ADR 0026; TPS62869 v1.12–v1.17) | BRD-010, BRD-049 (must) | EN from vcc3v3_pmu (RC); on in suspend | H5 link (line 137), inside the differential sense loop | fit | fit |
| 14 | `blk.pwr-5v1` | TPS62903 5.1 V buck | BRD-026, BRD-034, BRD-050 (must) | EN = `HAT5V_EN` OR `USB_SRC_ON` | HAT channel (input) | fit | fit |
| 15 | `blk.hat-5v` | HAT port `VBUS` source (eFuse #A) and sink (TPS2121 IN2), FUSB302B01MPX port controller (USB PD), `VBUS` TVS, discharge FET | BRD-026 (must, Draft), BRD-049, HCS-027 to HCS-030 | eFuse EN (`HAT5V_EN`, TCPM) | eFuse IMON | fit | fit |
| 16 | `blk.usb-vbus-out` | eFuse #C | BRD-034 (must) | eFuse EN | eFuse IMON | fit | fit |
| 17 | `blk.hat-3v3` | Removed (2026-10-25, RFC 0014: interface v2 has no 3.3 V rail) | — | — | — | — | — |
| 18 | `blk.current-monitors` | 4 × INA236 and shunts | T1-026 (must) through BOM line 54 (Proposed; ADR 0013 keeps them) | INA236 power-down | — | fit | fit |
| 19 | `blk.hat-signals` | HAT USB port: USB3 HOST1 SuperSpeed pairs with AC caps, `D±`, `CC`; two TPD4E05U06; the HAT connector (follows the connector decision) | BRD-003, BRD-006, BRD-013, BRD-044 (must), HCS-012, HCS-027 | none (USB attach) | none | fit | fit |
| 20 | `blk.hat-audio` | Removed (2026-10-25, RFC 0014: HAT audio goes over USB Audio Class) | — | — | — | — | — |
| 21 | `blk.fp-connector` | FH35C, low-speed and DSI ESD (BOM v1.21), FP_3V3, FP_1V8 | BRD-048 (must) | `FP_IO_EN` (TPS22950 FP_3V3, TPS22945 FP_1V8; current-limited from BOM v1.11) | display channel (position open) | fit | fit |
| 22 | `blk.fp-display` | DSI lanes, FP_VCI, panel RST/TE (DSI ESD at the connector, `blk.fp-connector`, BOM v1.21) | BRD-048 (must) | RK809 LDO4, and a TPS22945 on `FP_IO_EN` (BOM v1.11) | display channel (G11) | fit | fit |
| 23 | `blk.fp-backlight` | TPS61160 (BOM v1.11; TPS61169 before), inductor, rectifier | BRD-048 (must) | CTRL (`BL_PWM`) | display channel (G11) | fit | fit |
| 24 | `blk.fp-controls` | Faceplate I2C, touch INT/RST, HID_INT, ALS_INT, FP_DET# | BRD-048, T1-023 (must), FPT-021 (must) | FP_3V3 | none | fit | fit |
| 25 | `blk.status-led` | LP5521 | FPT-003, FPT-016 (must), FPT-025 (should) | CHIP_EN (I2C) | none (G12) | fit | fit |
| 26 | `blk.mic-main` | MIC_1V8 switch (TPS22945, current-limited), privacy-LED gate, faceplate PDM | BRD-027 (must, Draft) | `MIC_EN` | none (G10) | fit | fit |
| 27 | `blk.audio` | Audio converter boundary (parent of 28–33) | T1-040, BRD-011, BRD-022, BRD-023, BRD-040, T1-049, T1-072 (must) | see children | audio channel (G11) | fit | fit |
| 28 | `blk.audio-supply` | DAC_VP, DAC_DIG_1V8, TPS62840 | as `blk.audio` | `DAC_VP_EN`, `DAC_DIG_EN`, `AUDIO_LN_EN` | audio channel (G11) | fit | fit |
| 29 | `blk.mclk` | 2 × NSC5083D (45.1584 / 49.152 MHz), TPS7A2031, 2 × SN74AUC1G74, MCLK_1V8 LDO (v1.9) | BRD-023 (must), ADR 0010, ADR 0019 | `AUDIO_LN_EN` AND DAC_DIG_1V8, DAC_DIG_1V8 (dividers), ST pins, `MCLK_DIV_RUN` | none (G12) | fit | fit |
| 30 | `blk.dac-l` | CS43198 (left) and its VA LDO | BRD-022 (must), ADR 0001 | `DAC_DIG_EN`, `AUDIO_LN_EN`, `DAC_VP_EN` | none (G12) | fit | fit |
| 31 | `blk.dac-r` | CS43198 (right) and its VA LDO | as `blk.dac-l` | as `blk.dac-l` | none (G12) | fit | fit |
| 32 | `blk.hpa-rails` | TPS65131 boost, LMR33630C, 2 × LT3045, 2 × LT3094 | BRD-022, BRD-049 (must), ADR 0012, ADR 0015 | `HPA_RAIL_EN`, `HPA_LDO_EN` | none (G11) | fit | fit |
| 33 | `blk.hpa-se` | 2 × OPA1622 for 3.5 mm, networks | BRD-011, BRD-022 (must) | `HPA_SE_EN` | none (G12) | fit | fit |
| 34 | `blk.hpa-bal` | 4 × OPA1622 for 4.4 mm, networks | BRD-011, BRD-022, BRD-024 (must) | `HPA_BAL_EN` | none (G12) | fit | fit |
| 35 | `blk.jack-se` | 3.5 mm jack, ESD, detect | BRD-011, BRD-052 (must) | — (passive) | — | fit | fit |
| 36 | `blk.jack-bal` | 4.4 mm jack, ESD, detect | BRD-011, BRD-024, BRD-052 (must) | — (passive) | — | fit | fit |
| 37 | `blk.speaker` | MAX98357A, speaker contacts | BRD-012 (must) | SD_MODE | none (G12) | fit | fit |
| 38 | `blk.mic-ambient` | Body PDM microphone | BRD-031 (should) | `MIC_EN` (shared) | none (G10) | fit | fit |
| 39 | `blk.radio` | Murata Type 2EL (IW612) | BRD-025, BRD-029 (must), BRD-030 (should) | TPS22916C on expander `WL_PWR_EN` (v1.9; RK809 SWOUT1 before), PDn | none (G12) | fit | fit |
| 40 | `blk.antennas` | 2 × U.FL, matching, 2 × antenna | BRD-025, BRD-029 (must) | — (passive) | — | fit | fit |
| 41 | `blk.nfc-tag` | NTAG I2C plus, loop antenna | BRD-057 (should) | none (G6) | none (G12) | fit | fit |
| 42 | `blk.nfc-reader` | Removed (2026-10-27, maintainer decision: board area; BRD-057 reworded: NFC as the tag only) | — | — | — | — | — |
| 43 | `blk.imu` | LSM6DSV16X | BRD-032 (should) | none (G1) | none (G12) | fit | fit |
| 44 | `blk.haptics` | DRV2605L, LRA | BRD-058 (should) | EN (GPIO not assigned, G20) | none (G12) | fit | fit |
| 45 | `blk.tpm` | SLB9673 TPM 2.0 | BRD-059 (should) | none (G5) | none (G12) | fit | fit |
| 46 | `blk.rp2354` | RP2354A, inductor, oscillator, SWD | BRD-014 (should), BRD-015, BRD-019, BRD-041 | `RP_PWR_EN` (2 × TPS22916C) | none (G12) | fit | fit |
| 47 | `blk.buttons` | Power, Action, Vol+, Vol−, ESD | BRD-016, BRD-017, BRD-035, BRD-036 (must), T1-022 (must) | — | — | fit | fit |
| 48 | `blk.maskrom` | MaskROM combo (TPS3808, gates, BAT54, FET) | BRD-035, BRD-043 (must) | — (vcca1v8_pmu) | — | fit | fit |
| 49 | `blk.debug` | UART pads, I2S/DSD pads, rail test points, RP SWD pads, measurement links | BRD-040, BRD-047 (must), T1-026 | — | — | fit | fit (links 0 Ω) |
| 50 | `blk.cover-detect` | Back-cover detect input: board-edge pad, pull-up, TPD1E10B06 (v1.10) | ADR 0020 item 7 (should; no requirement ID; T1-086 met without it) | — (passive input) | none (µA) | fit | fit |
| — | `blk.shields` | Shield-can frames (DNP footprints): two etched two-piece cans (BOM v1.20) | BOM line 90, PCB-T-06, PCB-EMC-03 | — | — | dnp | dnp |

`blk.shields` is listed for completeness: it is a mechanical footprint set, not a function, and is not counted among the 50. Item tracking (BRD-030, line 103) has no hardware block of its own: from BOM v1.9 it is `blk.radio` kept powered in suspend while the listener enables it (decision 2026-10-24); tracking with the T1 off stays open.

## 3. Block records

Field order follows RFC 0011 §1. "Holds" lists the swap classes the interface takes without touching the rest of the board; "Revision" lists those that need a new block revision. Devicetree compatibles are those named in the BOM; the H2 component record is a component entry of `opendap.device-description/v1` carrying the block ID (RFC 0011 §5, system row).

### 3.1 Compute and storage

#### 1. `blk.soc`: application processor

| Field | Content |
|---|---|
| Bound by | BRD-002, BRD-003, BRD-004, BRD-006, BRD-042 (must); the SoC is ADR 0003 |
| Interface | Every bus of the board by function; the block is the H0 layer. Supplies: vdd_cpu, vdd_logic, vdd_gpu, vdd_npu, vcc_ddr, vcc0v6_ddr, vcc_1v8, vcca_1v8, vdda_0v9, vdda0v9_pmu, vcca1v8_pmu, vcc3v3_pmu, vccio_sd, vcc3v3_sys |
| Power domain | RK809-5 sequence (power tree §6.1); vdd_cpu from `blk.vdd-cpu` |
| Measure | Today only the VSYS channel. Proposed: 0 Ω link + shunt footprints on vdd_cpu and vdd_logic outputs at the bulk capacitors (G12), Kelvin pads; the SoC draw is a bring-up item (T1-039) |
| Absent state | Not applicable: no variant of this board omits the SoC. A different SoC is a different H0/H1 board (RFC 0011 §3) |
| Holds / revision | Holds: speed grades of the RK3566. Revision: any other SoC (RK3576, i.MX 8M Plus are named as upgrades, line 1): new board, reusing every other block it can |
| Alternates | None same-land |
| Software | Mainline `rk3566.dtsi` (H0); board devicetree (H1) |
| Sub-blocks | `blk.soc-ddr`, `blk.soc-pmuio`, `blk.soc-vccio-a`, `blk.soc-vccio-b`, `blk.soc-phy`, `blk.soc-power`, `blk.soc-ground` (sheets of this record, each part's `Block` field) |
| Level | — / Q1 |

#### 2. `blk.lpddr4x`: memory

| Field | Content |
|---|---|
| Bound by | BRD-037 (must: 4 GB), T1-046, T1-047 (ADR 0013: 2 GB only as a qualified supply fallback) |
| Interface | LPDDR4X channel (`DDR_*` net classes, PCB-I-05); VDD1 (vcc_1v8), VDD2 (vcc_ddr 1.10 V), VDDQ (vcc0v6_ddr 0.60 V) |
| Power domain | RK809 BUCK3 (vcc_ddr, on in suspend) → TPS7A1006 (line 9) |
| Measure | Proposed: shunt footprint on vcc0v6_ddr and on vcc_ddr after the PMIC (G12) |
| Absent state | Not applicable (never omitted) |
| Holds / revision | Holds (v1.12, ADR 0022): single-rank 200-ball LPDDR4X on the MO-311 grid, 10 × 14.5 or 10 × 15 mm, listed T/A for RK3566 (the rank-1 outputs are not connected). Revision: a dual-rank part, LPDDR5 or another package |
| Alternates | `cxmt-4gb`: CXMT CXDB5CBAM-MA-B (line 8; land checked by libs `kicad/`, RK3566 T/A; fitted after a qualification build, ADR 0022). `2gb`: 2 GB fallback (ADR 0013; part not named) |
| Software | Memory node from the DDR blob; no component record beyond `memory` capacity in the board description |
| Level | — / Q1 |

#### 3. `blk.emmc`: internal storage

| Field | Content |
|---|---|
| Bound by | BRD-037 (must: 32 GB prototypes, 16 GB or 32 GB production per ADR 0013), BRD-043 |
| Interface | eMMC 8-bit HS200 (PCB-I-06), RSTn, VCC (vcc3v3_sys), VCCQ (vcc_1v8); the MaskROM pull on D0 belongs to `blk.maskrom` |
| Power domain | vcc3v3_sys, always on (power tree §6.1: up before the BootROM). No switch; suspend behaviour is an open question (power tree §6.5) |
| Measure | Proposed: 0 Ω link + shunt on VCC (G12) |
| Absent state | Not applicable for boot (never omitted). With an empty eMMC the BootROM falls through to SD or MaskROM (BRD-043) |
| Holds / revision | Holds: any JEDEC eMMC 5.1 in the same 153-ball package and capacity. Revision: UFS |
| Alternates | `emmc-32gb` Samsung KLMBG2JETD-B041 (line 10). `emmc-16gb` (ADR 0013 production option; MPN not in the BOM). Second makers Micron, Kioxia, Longsys (line 10; land **UNVERIFIED**). Parameter: `capacity_gb` |
| Software | `sdhci` node, `status = "okay"` |
| Level | — / Q1 |

#### 4. `blk.microsd`: removable storage

| Field | Content |
|---|---|
| Bound by | BRD-038, BRD-043, BRD-051 (must: UHS-I SDR104, 1.8 V signalling) |
| Interface | SDMMC0 CLK, CMD, D0–D3 (PCB-I-06), card detect, VDD (vcc3v3_sd), VCCIO3 (vccio_sd) |
| Power domain | RK809 SWOUT2 (card VDD), LDO5 (signalling 1.8 / 3.3 V) |
| Measure | Proposed: shunt footprint on vcc3v3_sd (G12) |
| Absent state | Card absent is a normal state: detect pulled to "absent"; CLK/CMD/D lines idle with the SoC's pulls. Socket unfitted is not a variant |
| Holds / revision | Holds: any push-push socket on the DM3AT land. Revision: a socket with another land |
| Alternates | Hirose DM3AT-SF-PEJM5 (line 11); Molex 104031-0811 (second source, land **UNVERIFIED**) |
| Software | `sdmmc0` node with `vqmmc-supply` = LDO5 |
| Level | — / Q1 |

#### 5. `blk.board-id`: board EEPROM

| Field | Content |
|---|---|
| Bound by | No requirement names it (line 17, Proposed). Proposed use beyond revision, serial and output trim: it also stores the variant name, so Blackbird OS can match the description to the fitted variant (rule 8) |
| Interface | I2C2 at 0x50; supply (rail not stated in the BOM) |
| Power domain | Not stated: proposed vcca1v8_pmu, so it reads like the rest of I2C2 (G16) |
| Measure | None needed (µA) |
| Absent state | 0x50 free on I2C2; nothing else |
| Holds / revision | Holds: any 24C02-class EEPROM at 0x50 in SOT23-5. Revision: SO-8 second source (M24C02, other land) |
| Alternates | AT24C02D-STUM-T (line 17) |
| Software | `board_id` node (the AT24C02D on I2C2); `atmel,24c02` at 0x50; board description `identity` reads it |
| Level | — / Q1 |

#### 6. `blk.gpio-expander`: slow enables and detects

| Field | Content |
|---|---|
| Bound by | BRD-008, BRD-019 (must): every enable it holds defaults off with the SoC unconfigured |
| Interface | I2C2 at 0x21, INT (`EXP_INT_N`, PMUIO0), VCCI (1.8 V), VCCP (vcc3v3_sys); 16 port lines. BOM v1.9 port map: P00 `FP_IO_EN`, P01 `HAT3V3_EN`, P02 `HAT5V_EN`, P03 `USB_SRC_ON`, P04 `HAPTIC_EN`, P05 `NFC_PWR_EN` (a spare since 2026-10-27, the NFC reader withdrawn), P06 `WL_PWR_EN`, P07 spare; P10–P11 jack detects, P12 `FP_DET_N`, P13–P14 faceplate GPIO, P15–P17 eFuse faults |
| Power domain | Always on: VCCI on vcca1v8_pmu (BOM v1.8 line 93, G15), VCCP on vcc3v3_sys. Outputs hold through suspend |
| Measure | None needed |
| Absent state | Not applicable (never omitted). Every output it drives has a board pull-down to its off state, since the TCA6416A ports power up as inputs |
| Holds / revision | Holds: PCAL6416A (same driver, line 93). Revision: an expander of another pin count |
| Alternates | `pcal6416a` |
| Software | `gpio_exp` node (the TCA6416A); `ti,tca6416` (`gpio-pca953x`) |
| Level | — / Q1 |

### 3.2 Power

#### 7. `blk.charger`: power input, charger and battery path

| Field | Content |
|---|---|
| Bound by | BRD-007, BRD-049, BRD-050 (must), ADR 0014 (decided parts: BQ25798, fuse rating, ship FET), ADR 0020 (battery contacts, BOM v1.10; replaces ADR 0014's connector family); T1-055, T1-079 (user-replaceable pack, published pack specification) |
| Interface | USB-C VBUS (from `blk.usb-c`), HAT_5V in (powerbank, from `blk.hat-5v` connector side), VSYS out, battery contacts (six KYOCERA AVX 70-9258-001-120-006 in a window of the pocket floor, face compression; order P+, P+, empty position, mid-cell tap, NTC, P−, P−; BOM line 47) to the pack's terminal board (recessed hard-gold pads, line 46), with a TPD1E10B06 on the mid-cell tap and NTC and a DNP P+ TVS position (line 142); BATP through 100 Ω with 47 nF to GND (line 115); I2C1 (0x6B), INT (wake), STAT; `USB_SRC_ON`, `HAT_SRC_ON` into the TPS2121 OV pins |
| Power domain | Source of VSYS. Ship FET (line 120) removes the pack |
| Measure | INA236 VSYS channel (10 mΩ, ≥ 1 W, line 54); BQ25798 ADC; test pads on VBUS_CHG, VSYS, VBAT (PCB-T-02), and from v1.10 on the pack side of the fuse and on BAT for the insertion measurement (CB-07, PCB-L-09) |
| Absent state | Not applicable (never omitted). Battery absent (pack out, contacts open): with no adapter the BQ25798 is unpowered and the ship FET off, so a pack inserted later meets a soft start (ADR 0020 item 6); with an adapter, the BQ25798 keeps SYS regulated, sees the missing NTC, stops charging and reports no battery. Bring-up: a bench terminal board with the pack's pad layout, wired to a bench supply or a protected 2S pack, presses on the same contacts (ADR 0020 item 9); TS window follows the pack NTC |
| Holds / revision | Holds: BQ25792 (same family, mainline-supported, line 39) on the same land; any pack built to the published pack specification (T1-079). Revision: 1S or 3S+ packs (ADR 0014), another charger family, another contact row (pitch, order or arrangement) |
| Alternates | `bq25792` (line 39); fuse 0451004.MRL only under ADR 0014's condition (line 104); battery contacts: none on the same land; `pogo-contacts`, Mill-Max 0965 or 0990 pogo pins, four per pole on their own land, as the fallback to qualify (line 47; rule 1: a DNP footprint set in this block's sheet, never a land outside it) |
| Software | `charger` node (the BQ25798); `ti,bq25798`, `ti,bq25792` (DKMS); board description `power` section |
| Sub-blocks | `blk.charger-input`, `blk.charger-core`, `blk.charger-battery` (sheets of this record, each part's `Block` field) |
| Level | — / Q1 (Q0 for the battery path: contacts, fuse, ship FET, margins; PCB-L-04 to L-09) |

#### 8. `blk.gauge`: fuel gauge

| Field | Content |
|---|---|
| Bound by | BRD-049 (must), ADR 0014 |
| Interface | I2C1 at 0x55, VC1 (mid-cell tap), VC2 (BAT+), SRP/SRN, TS1 (board NTC); no alert line: the BQ28Z610-R1 has no alert pin (SLUSE07B p. 3; pinout v1 C25, BOM v1.9 line 42) |
| Power domain | Pack, always on |
| Measure | Its own sense resistor (line 43; 3 mΩ from BOM v1.8, ADR 0017) |
| Absent state | Not applicable (never omitted) |
| Holds / revision | Holds: BQ28Z610 data-flash variants. Revision: BQ40Z50-R2 (other package, line 42) |
| Alternates | None same-land |
| Software | `fuel_gauge` node (the BQ28Z610); `ti,bq28z610` (DKMS); `org.opendap.hw.Battery` |
| Level | — / Q1 |

#### 9. `blk.usb-c`: main USB-C port

| Field | Content |
|---|---|
| Bound by | BRD-018, BRD-034, BRD-039, BRD-044, BRD-046 (must / should) |
| Interface | OTG0 D± (PCB-I-01), CC1/CC2, SBU (debug UART option), VBUS, I2C1 (FUSB302B 0x22), INT (wake) |
| Power domain | vcc3v3_pmu (FUSB302B, always on); VBUS from the port |
| Measure | VBUS current is visible through the BQ25798 ADC (sink) and eFuse #C IMON (source) |
| Absent state | Not applicable (never omitted) |
| Holds / revision | Holds: USB4105-GF-A land equivalents. Revision: the IP67 USB4730-GF-A (other land, line 61) |
| Alternates | Amphenol 12402012E212A (land **UNVERIFIED**); FUSB302B → RT1715 (other land) is a revision |
| Software | `usbc_tcpc` node (the FUSB302B); `fcs,fusb302` with `usb-c-connector` node; OTG0 `dr_mode = "otg"` |
| Level | — / Q1 |

#### 10. `blk.pwr-vsys-lv`: 3.8 V pre-regulator

| Field | Content |
|---|---|
| Bound by | BRD-049 (must), ADR 0014 |
| Interface | VSYS in, VSYS_LV out (3.8 V, 4 A rating), PG |
| Power domain | EN tied to VSYS: always on |
| Measure | None today. Proposed: a shunt footprint at its output, or an INA236 channel (G11): VSYS_LV feeds the PMIC, vdd_cpu, vcc3v3_sys and most of the audio and display supplies |
| Absent state | Not applicable |
| Holds / revision | Holds: TPS62136RGXT (same part). Revision: TPS62903 (other land, line 113) |
| Alternates | `tps62136rgxt` |
| Software | `vsys_lv` node (the fixed regulator); Fixed regulator node (`regulator-fixed`, always-on) |
| Level | — / Q1 |

#### 11. `blk.pwr-3v3-sys`: 3.3 V system rail

| Field | Content |
|---|---|
| Bound by | BRD-049 (must) |
| Interface | VSYS_LV in, vcc3v3_sys out (3 A), PG |
| Power domain | Always on (EN = VSYS_LV) |
| Measure | Proposed shunt footprint at the output (G12) |
| Absent state | Not applicable |
| Holds / revision | Holds: TPS62827DMQR (4 A, pin- and BOM-compatible, line 6) |
| Alternates | `tps62827` |
| Software | `vcc3v3_sys` node (the fixed regulator); `regulator-fixed`, always-on |
| Level | — / Q1 |

#### 12. `blk.pmic`: RK809-5

| Field | Content |
|---|---|
| Bound by | BRD-020 (must, Draft), BRD-009, BRD-010 |
| Interface | I2C0 (0x20), PMIC_INT, PMIC_SLEEP, TSADC_SHUT, PWRON, CLK32K out, VCC1–VCC4 (VSYS_LV), VCC5–VCC9 (vcc3v3_sys); outputs BUCK1–5, LDO1–9, SWOUT1–2 |
| Power domain | OTP sequence on PWRON (RK809-5 OTP table **UNVERIFIED**) |
| Measure | Rail test pads on every output (PCB-T-02). Proposed shunt footprints only where a block is attributed (G12) |
| Absent state | Not applicable |
| Holds / revision | Holds: RK809-5A (line 2). Revision: RK817-5 (codec PMIC, other pin map) |
| Alternates | `rk809-5a` |
| Software | `rk809` node (the PMIC); `rockchip,rk809` with `rk805-pwrkey`, regulators, RTC, `clk-rk808` |
| Level | — / Q1 |

#### 13. `blk.vdd-cpu`: CPU core buck

| Field | Content |
|---|---|
| Bound by | BRD-010, BRD-049 (must) |
| Interface | I2C0 at 0x42, VSYS_LV in, vdd_cpu out, EN from vcc3v3_pmu, PG to a test pad (monitor only), VOSNS and GOSNS differential sense from the 22 µF at the SoC ([ADR 0026](../adr/0026-vdd-cpu-buck-ti-tps62870z4.md), BOM v1.18 lines 3, 4, 147) |
| Power domain | EN from vcc3v3_pmu through 51 kΩ + 100 nF; on in suspend |
| Measure | The H5 link (line 137), inside the sense loop |
| Absent state | Not applicable |
| Holds / revision | Holds: none recorded on the same land (the TPS62871Z4, 9 A, shares the package). Revision: the 1800 MHz capacitor field of ADR 0026 item 7 |
| Alternates | none |
| Software | `vdd_cpu` node (the regulator of ADR 0026 item 6); `ti,tps62870` (`tps6287x`, mainline since Linux 6.5; not built by Debian: DKMS, OS-023). BRD-049 safety limit (2026-10-25, kept by ADR 0026): `regulator-max-microvolt = <1100000>` on `vdd_cpu`, so the OPP core drops the 1800 MHz / 1150 mV point and the top CPU clock is 1608 MHz; documented where the user sees the CPU frequencies, never silent. At this cap a 4.8 A release peaks at 1.149 V with the fitted 45.7 µF effective. Lifted to `<1150000>` at bring-up only if DC top + the measured load-step peak at the SoC stays ≤ 1.170 V (30 mV under the RK3566's 1.2 V absolute maximum, DS 1.1 p. 51) with the capacitors then fitted (ADR 0026 item 7). Forced PWM through the FPWMEN bit (`REGULATOR_MODE_FAST`). The converter's widest range reaches 3.35 V over I2C (SLVSGC5E p. 1), so the kernel and U-Boot constraints are the only ceiling (BOM §8 item 26) |
| Level | — / Q1 |

#### 14. `blk.pwr-5v1`: 5.1 V source for HAT_5V and USB-C VBUS out

| Field | Content |
|---|---|
| Bound by | BRD-026, BRD-034, BRD-049, BRD-050 (must) |
| Interface | VSYS in, 5V1_SRC out (1.6 A design), EN = `HAT5V_EN` OR `USB_SRC_ON` (hardware OR), PG |
| Power domain | Its own EN |
| Measure | INA236 HAT channel at its input (20 mΩ, line 54) |
| Absent state | EN pulled low; output discharge on (line 91) |
| Holds / revision | Holds: TPS62903 pin-compatible family members at ≤ 80 % load (TPS62902 fails: 80 %, line 91) |
| Alternates | None checked |
| Software | `vcc5v1` node (the 5.1 V regulator); `regulator-gpio` or fixed regulator with `enable-gpios` |
| Level | — / Q1 |

#### 15. `blk.hat-5v`: HAT port `VBUS` and USB PD

| Field | Content |
|---|---|
| Bound by | BRD-026 (must, Draft), BRD-049, HCS-012, HCS-027 to HCS-030 (USB PD power rules, hats `standard/` interface v2); PCB-P-11 [Q3] second limiter |
| Interface | 5V1_SRC in; HAT `VBUS` (board net `HAT_5V`) to the HAT connector (part follows the connector decision) and to TPS2121 IN2; `CC` to the port controller; `HAT5V_EN` (= `HAT_SRC_ON`, expander P02), `HAT_VBUS_DISCH` (expander P01), eFuse fault (P15), IMON (SARADC_VIN2), `HAT_PD_INT_N` (AG37), I2C1 0x23. Interface v2: 3.0 A continuous, 4.5 A fault ceiling; eFuse #A trips at 1.589 / 1.783 / 1.981 A (RILM 1.87 kΩ, BOM v1.13), the TPS2121 at 2.95 A at most (in); copper class `PWR_HAT5V` (PCB-P-20) |
| Power domain | Port controller VDD on vcc3v3_pmu (always on); eFuse #A EN |
| Measure | eFuse IMON to SARADC (line 44); the INA236 HAT channel at the 5.1 V buck input sees #A and #C together |
| Absent state | HAT detached: the port controller presents its sink pull-down on `CC` (also unpowered: dead-battery support), `HAT5V_EN` pulled low, `VBUS` discharged and held by the TVS0500; `HAT_SRC_ON` low releases TPS2121 OV2, so a source HAT can feed the T1 |
| Holds / revision | Holds: TPS259472A / TPS259474L (line 44); FUSB302B10MPX or FUSB302B11MPX (0x24, 0x25; FUSB302B/D Rev. 5 p. 18) on the same land if 0x23 is taken. Revision: PD voltages above 5 V from a HAT (OV2, TVS, `CC` protection); v1.14 accepts 5 V only (OV2 at 5.60–6.31 V) |
| Alternates | `tps259472a`, `tps259474l`; port controller address variants |
| Software | `hat_tcpc` node (the HAT port's FUSB302B01); Mainline `fusb302` + `tcpm`: a `usb-c-connector` node with power-role dual, data-role host, `vbus-supply` = a fixed regulator on `HAT5V_EN`; the source offer 5 V 1.5 A, the sink offer 5 V; Blackbird OS PD policy for the HAT port |
| Level | — / Q1 |

#### 16. `blk.usb-vbus-out`: USB-C source path

| Field | Content |
|---|---|
| Bound by | BRD-034 (must) |
| Interface | 5V1_SRC in, VBUS out, `USB_SRC_ON`, fault, IMON (SARADC_VIN3 from BOM v1.13; was a test pad). eFuse #C at RILM 1.87 kΩ: 1.589 / 1.783 / 1.981 A, so the 1.5 A offer sits below the minimum trip (BOM v1.13). 5V1_SRC comes through eFuse #D, the shared limiter of #A and #C (RILM 1.47 kΩ, 2.021 / 2.268 / 2.520 A; fault on expander P16 `EFUSE_5V_FLT_N`; BOM v1.14) |
| Power domain | eFuse #C EN |
| Measure | eFuse IMON (SARADC_VIN3) |
| Absent state | `USB_SRC_ON` pulled low; OV1 released |
| Holds / revision | As `blk.hat-5v` |
| Alternates | As `blk.hat-5v` |
| Software | `usbc_vbus` node (the source regulator); `vbus-supply` of the `usb-c-connector` (TCPM source role) |
| Level | — / Q1 |

#### 17. `blk.hat-3v3`: removed

Removed on 2026-10-25 (BOM v1.13, RFC 0014): hats `standard/` interface v2 has no 3.3 V rail. The TPS62903 3.3 V buck (line 38), its inductor (line 7) and eFuse #B go; expander P01 becomes `HAT_VBUS_DISCH`, P16 a spare, SARADC_VIN3 eFuse #C IMON.

#### 18. `blk.current-monitors`: instrumentation

| Field | Content |
|---|---|
| Bound by | T1-026 (must: the tooling to verify promises shall exist); BOM line 54 is Proposed and ADR 0013 keeps all four in every variant |
| Interface | I2C1 at 0x40–0x43; four shunts: VSYS 10 mΩ, audio 100 mΩ, display 100 mΩ, HAT 20 mΩ |
| Power domain | vcc3v3_sys; INA236 power-down mode over I2C |
| Measure | It is the measurement |
| Absent state | INA236 unfitted: the shunts stay in circuit (power tree §5), or become 0 Ω links in a variant that drops a channel; 0x40–0x43 free on I2C1 |
| Holds / revision | Holds: INA236 address options. Revision: INA238 (1.2 V I2C, hwmon, other land) |
| Alternates | Parameters per variant: `channels` (fitted INA236 channels; a dropped channel's shunt becomes a 0 Ω link) and `shunt_mohm` |
| Software | `ti,ina236` (IIO `ina2xx-adc`) ×4 |
| Level | — / Q1 |

Shunt positions of the audio and display channels are not defined in the BOM, and the audio block draws from both VSYS (LMR33630C) and VSYS_LV (everything else): one shunt cannot attribute it (G11).

### 3.3 HAT

#### 19. `blk.hat-signals`: HAT USB port

| Field | Content |
|---|---|
| Bound by | BRD-003, BRD-006, BRD-013, BRD-044 (must); HCS-012 (must); HCS-027 (HATs reach the device only through USB); hats `standard/` [interface v2](https://github.com/opendap-project/hats/blob/main/standard/docs/specs/interface-v2.md) and [ADR 0006](https://github.com/opendap-project/hats/blob/main/standard/docs/adr/0006-hats-are-usb-only.md) |
| Interface | USB3 HOST1: `SSTX±` (100 nF AC caps, line 70), `SSRX±`, `D±` (2.2 Ω series); `CC` to the port controller in `blk.hat-5v`; `VBUS` and `GND` from `blk.hat-5v`. ESD: one TPD4E05U06 on the SuperSpeed pairs (line 68), one on `D±` and `CC` (line 69), both on the device-side piece at the pogo field. Connector: DF40C-50DS on the board, the [HAT flat cable](hat-flat-cable.md) (line 102) to the device-side piece with 20 Mill-Max 0965 pogo pins (lines 66, 67; BOM v1.14, RFC 0015) |
| Power domain | Signals only; USB3 PHY in SoC `PD_PIPE` |
| Measure | Power is measured in `blk.hat-5v` |
| Absent state | HAT detached: the USB host sees no attach; `CC` held by the port controller's pull-down. A dangling flat cable without a HAT must not load the USB 3 pairs (AC caps on the board side) |
| Holds / revision | Holds: any HAT that meets interface v2 (H4). Revision: none planned |
| Alternates | ESD: TPD1E04U04DPYR per line (line 68) |
| Software | `usb_host1_xhci` node (mainline); USB host on HOST1; Blackbird OS reads the HAT's identity capability from its USB descriptors and binds class drivers (interface v2); no devicetree overlay per HAT |
| Level | — / Q1 |

#### 20. `blk.hat-audio`: removed

Removed on 2026-10-25 (BOM v1.13, RFC 0014): a HAT presents audio as a USB Audio Class device with its own clock, so the T1 has no HAT I2S port. The AXC translators (line 95) and the `I2S_MCLK` buffer (line 112) go; the DAC clock nets lose their HAT taps.

### 3.4 Faceplate interface

The faceplate interface is the t1 [faceplate interface v1](../../../product/docs/specs/faceplate-interface.md) (Draft, 2026-10-24; was v0; FH35C-51S, 46 used, 5 reserved). Its supply classes (t1 ADR 0005) put a fault ceiling on every rail, which the board enforces: FP_3V3 ≤ 0.4 A, FP_1V8, MIC_1V8, FP_VCI and the backlight ≤ 0.2 A, BL_LEDA ≤ 30 V in every state. The board blocks are the host side; the faceplate (H3) owns the panel, touch, ALS, HID controller and LEDs.

#### 21. `blk.fp-connector`: connector and faceplate logic supplies

| Field | Content |
|---|---|
| Bound by | BRD-048 (must) |
| Interface | FH35C-51S, contact positions in pinout v1 §8 (RFC 0001 group order); FP_3V3 ×2, FP_1V8, `FP_DET#`, 2 spare GPIO (expander), 5 reserved, grounds; low-speed ESD (line 75: 5 × TPD4E05U06 for 20 lines and a TPD1E10B06 for `FP_GPIO1` from BOM v1.21; 6 × TPD4E05U06 from v1.9); DSI ESD at the contacts (line 72: 3 × TPD4E05U06 for CLK± and D0–D3±, BOM v1.21) |
| Power domain | Current-limited switches (BOM v1.11 lines 145, 146; 2 × TPS22919 before): TPS22950 for FP_3V3 from vcc3v3_sys (0.22–0.38 A), TPS22945 for FP_1V8 from vcc_1v8 (100–200 mA), `FP_IO_EN` on expander P00. Suspend (decision 2026-10-24, T1-060): off by default, the T1 wakes from the body buttons; the expander holds `FP_IO_EN`, so FP_3V3 can stay on for a faceplate that must wake the T1; FP_1V8 follows vcc_1v8 |
| Measure | INA236 display channel (position open, G11). Proposed: shunt footprints on FP_3V3 and FP_1V8 at the switch outputs |
| Absent state | Faceplate detached: `FP_DET#` pulled up (reads "absent"); FP_3V3 and FP_1V8 off (TPS22950 QOD; the TPS22945 has none, so a 10 kΩ discharge resistor, BOM line 146); spares as SoC/expander inputs with pulls; reserved contacts unconnected |
| Holds / revision | Holds: FH35C-51S-0.3SHW(99). Revision: another connector family |
| Alternates | `fh35c-51s-99` |
| Software | Faceplate overlay (H3) selected from the HID identity (T1-020) |
| Level | — / Q1 |

#### 22. `blk.fp-display`: display lanes and panel supply

| Field | Content |
|---|---|
| Bound by | BRD-048 (must) |
| Interface | DSI0 CLK± and D0–D3± (or LVDS0 on the same balls; PCB-I-04), common-mode filter positions (PCB-EMC-01), FP_VCI (RK809 LDO4, 2.8 V DT-adjustable, 100 mA design, through a TPS22945 at 100–200 mA on `FP_IO_EN`, BOM v1.11: the datasheet gives LDO4 no trip value and the RK809-5 OTP start-up is unknown), panel RST and TE |
| Power domain | LDO4 over I2C, and its switch on `FP_IO_EN`; FP_1V8 for IOVCC |
| Measure | Display channel (G11) |
| Absent state | LDO4 off and its switch open (contact 44 dead whatever the RK809-5 OTP does); DSI PHY powered down (vdda_0v9 is shared with USB and PCIe PHYs, so it stays up); panel RST low; TE input pulled down |
| Holds / revision | Holds: any panel on DSI 1–4 lanes or LVDS within the faceplate interface. Revision: parallel RGB (not on the RK3566, pin plan §3.1), a second DSI |
| Alternates | Display part belongs to the faceplate |
| Software | `dsi0` node (mainline); Faceplate overlay: `focuslcds,e35gh-i-mw800cb` (`panel-ilitek-ili9488`) on the touch faceplate |
| Level | — / Q1 |

#### 23. `blk.fp-backlight`: backlight driver

| Field | Content |
|---|---|
| Bound by | BRD-048, BRD-049 (must) |
| Interface | VSYS_LV in, BL_LEDA (13–16.5 V on the touch faceplate, 60 mA; strings ≤ 22 V, BL_LEDA ≤ 27 V open string, faceplate interface v1 §2.3) and BL_LEDK to the faceplate, `BL_PWM` (CTRL) |
| Power domain | TPS61160 CTRL (BOM v1.11; TPS61169 before) |
| Measure | Display channel (G11). Proposed: the display INA236 shunt on the TPS61160 VIN, which carries most of the display power |
| Absent state | Faceplate detached: CTRL low; with an open string the open-LED protection (25–27 V at SW, SLVS791E §6.5) bounds the output below the FH35C's 30 V |
| Holds / revision | Holds: strings ≤ 18 V at 60 mA with ≥ 20 % margin from VSYS_LV, ≤ 22 V at lower currents (power tree §4.5). Revision: a driver on VSYS for longer strings, or a backlight on the faceplate |
| Alternates | None qualified with an open-LED threshold ≤ 30 V (the TPS61169 no longer qualifies) |
| Software | `backlight` node (the backlight); `pwm-backlight` |
| Level | — / Q1 |

#### 24. `blk.fp-controls`: faceplate control bus and interrupts

| Field | Content |
|---|---|
| Bound by | BRD-048, T1-023, T1-024 (must), FPT-021 (must) |
| Interface | Faceplate I2C (I2C3, 3.3 V, VCCIO5), SPI/DBI, touch INT and RST, `HID_INT`, `ALS_INT` (open drain, 4.7 kΩ pull-ups on FP_3V3; `HID_INT` on a PMUIO1 wake ball, `ALS_INT` on VCCIO5, not a wake source; pinout v1 C4), PDM is in `blk.mic-main` |
| Power domain | FP_3V3 (faceplate side) |
| Measure | Display channel |
| Absent state | Faceplate detached or FP_3V3 off: I2C3 pull-ups (2.2 kΩ, sized for 400 kHz with the faceplate's ≤ 100 pF, BOM v1.11) must sit on FP_3V3, not on an always-on rail, so no faceplate part is back-powered (G8); touch INT is the GT911 address strap: a board pull fixes the default address (G9); HID_INT and ALS_INT pulled up on FP_3V3, so they read low while it is off: masked by software then (pinout v1); SPI lines with SoC pulls |
| Holds / revision | Holds: any controller on I2C/SPI with these interrupts. Revision: a faceplate that needs USB |
| Alternates | — |
| Software | `i2c3` node (mainline: the faceplate control bus); Board devicetree (t1 faceplate interface v1 §4.1, t1 ADR 0004): the identity node on I2C3, `compatible = "hid-over-i2c"`, `reg = <0x2c>`, `hid-descr-addr = <0x0001>`, interrupt `FP_HID_INT_N` level-low (`IRQ_TYPE_LEVEL_LOW`), `vdd-supply` = FP_3V3, `post-power-on-delay-ms = <20>`, wakeup disabled by default (`power/wakeup` off, so `i2c-hid` releases FP_3V3 in suspend). The identity device itself is on the faceplate (faceplate-touch, BC7). Faceplate overlay, selected from the identity: `goodix,gt911`, `vishay,veml6030` |
| Level | — / Q1 |

#### 25. `blk.status-led`: RGB status LED driver

| Field | Content |
|---|---|
| Bound by | FPT-003, FPT-016 (must), FPT-025 (should: RGB) |
| Interface | I2C2 at 0x32, LED_R, LED_G, LED_B (current sources, ≤ 20 mA) to the faceplate, VDD (VSYS_LV), EN (vcca1v8_pmu) |
| Power domain | Always supplied; CHIP_EN bit, charge pump power-save |
| Measure | Proposed: shunt footprint on VDD (G12) |
| Absent state | Faceplate detached: current-source outputs open, no back-powering. LP5521 unfitted: 0x32 free; LED lines open |
| Holds / revision | Holds: LP5521 packaging and binning on the WQFN-24 land. Revision: LP5521TMX/NOPB (DSBGA, same die, other land), or a single-colour LED on a PWM (FPT-025 fallback) |
| Alternates | — same-land |
| Software | `status_led` node (the LP5521); `national,lp5521` (DKMS); `org.opendap.hw.Led`; description `indicators` |
| Level | — / Q1 |

#### 26. `blk.mic-main`: microphone supply, privacy LED gate and faceplate PDM

| Field | Content |
|---|---|
| Bound by | BRD-027 (must, Draft: the privacy LED cannot light without microphone power) |
| Interface | MIC_1V8 (TPS22945 from vcc_1v8, 100–200 mA, ≤ 0.2 A ceiling; BOM v1.11, TPS22919 before), `MIC_EN` (SoC GPIO in the power tree, expander in the pin plan: settle in pinout v1), PDM CLK0 and SDI0 to the faceplate, privacy-LED gate (DMG1012T, gate = MIC_1V8, LED anode from FP_3V3) |
| Power domain | MIC_1V8 switch; also feeds `blk.mic-ambient` |
| Measure | None (G10) |
| Absent state | MIC_1V8 off: PDM CLK0 must be parked low (pinctrl sleep state), otherwise it drives an unpowered microphone (G10); privacy LED off by construction |
| Holds / revision | Holds: any PDM microphone at 1.8 V. Revision: an I2S or analog microphone |
| Alternates | Infineon IM72D128 (line 34) |
| Software | `pdm` node (mainline); Rockchip PDM node with `dmic-codec`; the privacy LED is never described (hardware support spec §3) |
| Level | — / Q1 |

### 3.5 Audio

`blk.audio` is the boundary for a chipset swap; its children are the units that are fitted, enabled and measured. Another variant (RFC 0011 §3) may replace any child, or all of them, behind the parent's interface.

#### 27. `blk.audio`: audio converter boundary

| Field | Content |
|---|---|
| Bound by | T1-040 (must: the audiophile experience at 100 %), BRD-011, BRD-022, BRD-023, BRD-040, BRD-052, T1-049, T1-072 (must), BRD-049 (margins); ADR 0001, 0010, 0012, 0015 |
| Interface | Digital audio in: I2S1 TX BCLK, LRCK (clock outputs of the converter, which is clock master), SDO0 (PCM), SDO1, SDO2 (DSD left and right, reserved), DSD clock. Clocks out: none to the HAT since 2026-10-25 (`blk.hat-audio` removed, RFC 0014). Control: I2C2, `DAC_RESET`, `DAC_INT`. Enables: `DAC_VP_EN`, `DAC_DIG_EN`, `AUDIO_LN_EN`, `MCLK441_EN`, `MCLK48_EN`, `HPA_RAIL_EN`, `HPA_LDO_EN`, `HPA_SE_EN`, `HPA_BAL_EN`. Supplies: VSYS, VSYS_LV, vcc_1v8. Outputs: SE L, R and sense ground to `blk.jack-se`; balanced L+, L−, R+, R− to `blk.jack-bal`; REFA, REFB returns (PCB-A-03) |
| Power domain | Its children's switches; off in suspend (power tree §6.5) |
| Measure | INA236 audio channel (position open, G11) |
| Absent state | Not omitted in any product variant (T1-040). Unpowered: every enable pulled to off (PCB-A-13 [Q1]); I2S SDO lines parked low before power-down (power tree §5) and isolated from the unpowered DACs by hardware (G2) |
| Holds / revision | Holds: another DAC family or output stage behind I2S/TDM/DSD with the converter as clock master or consumer, 1.8 V or 3.3 V control (with translation inside the block), its own supplies from VSYS and VSYS_LV, and up to four analog legs per jack pair. Revision: a converter that needs a SoC MCLK output, SPDIF, or USB audio |
| Alternates | Child alternates below |
| Software | `sound` node (the card); `simple-audio-card` or audio-graph card (board devicetree); `org.opendap.hw.audio.Dac`, `.Output`; description `audio` and `outputs` sections |
| Level | — / Q1 |

#### 28. `blk.audio-supply`: DAC supplies

| Field | Content |
|---|---|
| Bound by | As `blk.audio`; CS43198 sequencing (VP first on, last off) |
| Interface | VSYS_LV, vcc_1v8 in; DAC_VP (TPS22916C), DAC_DIG_1V8 (TPS22916C), AUDIO_2V2 (TPS62840) out; `DAC_VP_EN`, `DAC_DIG_EN`, `AUDIO_LN_EN` |
| Power domain | Three switches, QOD and active discharge |
| Measure | Proposed: shunt footprints on DAC_DIG_1V8 and AUDIO_2V2 (G12) |
| Absent state | Every enable pulled low |
| Holds / revision | Holds: TPS22916 (line 50), TPS62A01 (line 27; land **UNVERIFIED**) |
| Alternates | `tps22916`, `tps62a01` |
| Software | Regulators with `enable-gpios`, consumed by the DAC nodes |
| Level | — / Q1 |

#### 29. `blk.mclk`: master clocks

| Field | Content |
|---|---|
| Bound by | BRD-023 (must), T1-040; ADR 0010 amended by ADR 0019; MCLK acceptance criteria (BOM §4.3) |
| Interface | VSYS_LV in, MCLK_3V1 (TPS7A2031, EN = `AUDIO_LN_EN` AND DAC_DIG_1V8), AUDIO_2V2 in for MCLK_1V8 (TPS7A2018, EN = DAC_DIG_1V8), `MCLK441_EN` and `MCLK48_EN` (ST pins, 3.3 V balls), `MCLK_DIV_RUN` (both CLR̅); one oscillator net (45.1584 / 49.152 MHz, 33 Ω per oscillator, 100 kΩ pull-down) into one SN74AUC1G74 per DAC, each Q through 27 Ω to its XTI at 22.5792 / 24.576 MHz ([ADR 0019](../adr/0019-master-clock-divided-from-twice-the-frequency.md), `sim/mclk-divider`); HAT copy (line 112, Open) |
| Power domain | `AUDIO_LN_EN` AND DAC_DIG_1V8 (oscillators), DAC_DIG_1V8 (dividers); one oscillator enabled at a time |
| Measure | Links 27 (TPS7A2031 input) and 36 (MCLK_1V8 LDO input), power tree §4.12 |
| Absent state | Both ST pins pulled down (outputs tri-stated); `MCLK_DIV_RUN` pulled down (dividers held). Neither the oscillators nor the dividers can run without DAC_DIG_1V8, so no clock reaches an unpowered XTI (G3); with MCLK_3V1 off and an ST line high, the 3.3 V logic drives an unpowered oscillator (pull-down, series footprint and ordering rule; ST rating **UNVERIFIED**, pinout O11) |
| Holds / revision | Holds: any 2520 3.3 V oscillator at 45.1584 / 49.152 MHz with tri-state that meets the acceptance criteria; the AUC1G74 in YZP or RSE packages with their own land. Revision: the ADR 0019 fallback (1.8 V KC2520K with a buffer per DAC), a PLL-based clock |
| Alternates | None qualified at 45.1584 / 49.152 MHz (line 20) |
| Software | `fixed-clock` nodes gated by GPIO (`gpio-gate-clock` with ST and `MCLK_DIV_RUN`), selected by the card driver per rate family; the CS43198 still sees 22.5792 or 24.576 MHz |
| Level | — / Q1 |

#### 30–31. `blk.dac-l`, `blk.dac-r`: one CS43198 per channel

| Field | Content |
|---|---|
| Bound by | BRD-022 (must), BRD-040 (test pads), T1-040; ADR 0001 |
| Interface | I2S1 BCLK and LRCK (left DAC is the clock master), SDO0, DSD clock and DSDA, XTI (MCLK), I2C2 (0x30 left, 0x31 right), `DAC_RESET` (shared), `DAC_INT` (wired-OR); VP (DAC_VP), VA (own TPS7A2018 from AUDIO_2V2), VD, VL, VCP (DAC_DIG_1V8); analog out to `blk.hpa-se` and `blk.hpa-bal` |
| Power domain | DAC_VP, DAC_DIG_1V8, VA LDO (`AUDIO_LN_EN`) |
| Measure | Proposed: shunt footprints on each VA LDO input (G12) |
| Absent state | RESET pulled low; INT pull-up on DAC_DIG_1V8, never on an always-on rail; I2C2 isolated from an unpowered DAC (G2); I2S data lines parked low and series-resistor footprints at the DAC pins (G2) |
| Holds / revision | Holds: CS43198 and CS43130-family parts on the same QFN-40 land (driver `cs43130`); the parent holds other families |
| Alternates | None in the BOM (line 18: no second source) |
| Software | `cirrus,cs43198` (DKMS: `SND_SOC_CS43130` off in Debian); DSD128 cap (blackbird-os ADR 0006) |
| Level | — / Q1 |

#### 32. `blk.hpa-rails`: amplifier rails

| Field | Content |
|---|---|
| Bound by | BRD-022, BRD-049 (must), T1-049; ADR 0012, ADR 0015 |
| Interface | VSYS_LV (TPS65131 boost), VSYS (LMR33630C inverting buck-boost), HPA_P6V0 and HPA_N6V0 out, `HPA_RAIL_EN`, `HPA_LDO_EN` (≥ 10 ms later, 3.3 V logic) |
| Power domain | TPS65131 ENP; LMR33630C EN through its level shifter; LDO EN/UV |
| Measure | Proposed: shunt footprints on AUDIO_P7V0 and AUDIO_N7V0 inputs (G11): the LMR33630C draws from VSYS, outside any INA236 channel today |
| Absent state | Both enables pulled low on the host side (`blk.soc-vccio-b`, PCB-A-13); LDO EN/UV low; OPA1622 EN low first |
| Holds / revision | Holds: LMR33620CRNXR (line 116), XAL4020-222MEC (line 117). Revision: another rail topology or voltage |
| Alternates | `lmr33620`, `xal4020-222` |
| Software | Regulators with `enable-gpios` and fixed delays, consumed by the output nodes |
| Sub-blocks | `blk.hpa-rails-pre`, `blk.hpa-rails-ldo` (sheets of this record, each part's `Block` field) |
| Level | — / Q1 |

#### 33–34. `blk.hpa-se`, `blk.hpa-bal`: headphone amplifier groups

| Field | Content |
|---|---|
| Bound by | BRD-011, BRD-022, BRD-024 (balanced), T1-040, T1-049, T1-072 (must); ADR 0012 |
| Interface | DAC differential outputs (both groups hang on the same DAC pins), HPA_P6V0, HPA_N6V0, `HPA_SE_EN` (2 packages) or `HPA_BAL_EN` (4 packages), outputs to the jack blocks |
| Power domain | OPA1622 EN per group (shutdown 5 µA per channel); the rails are shared |
| Measure | Proposed: a 0 Ω link per group on each rail branch, with Kelvin pads, for idle and loaded current per group (G12) |
| Absent state | EN pulled low; a disabled OPA1622 output is not high-impedance (SBOS727B §7.4.1), so a group is never left fitted but unpowered while the other plays from the same DAC pins without the rails up; mute shunt footprints DNP (line 100) |
| Holds / revision | Holds: OPA1622 replacements on the DRC0010J land. Revision: another topology (parent swap) |
| Alternates | Mute shunt (line 100) as `fit` option |
| Software | Part of the card's DAPM widgets; output selection follows jack detection (BRD-052) |
| Sub-blocks | `blk.hpa-bal-l`, `blk.hpa-bal-r` (sheets of this record, each part's `Block` field) |
| Level | — / Q1 |

#### 35–36. `blk.jack-se`, `blk.jack-bal`: headphone jacks

| Field | Content |
|---|---|
| Bound by | BRD-011, BRD-052 (must); BRD-024 (4.4 mm JEITA RC-8141C) |
| Interface | Output legs from the amplifier group, REF return, detect switch to the expander (3.3 V port, interrupt); TPD1E10B06 on every leg and detect line |
| Power domain | Passive |
| Measure | — |
| Absent state | Nothing plugged: detect reads "absent" through its pull-up |
| Holds / revision | Holds: same-land jacks. Revision: Pentaconn genuine part if its drawing differs (line 31) |
| Alternates | `sj2-35894d` (3.5 mm); `pentaconn` (4.4 mm, land **UNVERIFIED**) |
| Software | Jack detection through the expander GPIO; description `outputs` |
| Level | — / Q1 |

#### 37. `blk.speaker`: speaker amplifier

| Field | Content |
|---|---|
| Bound by | BRD-012 (must: independent of the DAC) |
| Interface | I2S3 (BCLK, LRCK, SDO at 3.3 V), `SPK_SD` (SD_MODE), VSYS_LV, speaker spring contacts |
| Power domain | SD_MODE shutdown; always supplied |
| Measure | Proposed: shunt footprint on its VDD (G12) |
| Absent state | SD_MODE pulled low (shutdown); with the part unfitted, I2S3 lines need SoC pull-downs |
| Holds / revision | Holds: MAX98360A (same driver, line 32) |
| Alternates | `max98360a` |
| Software | `speaker_amp` node (the MAX98357A); `maxim,max98357a` |
| Level | — / Q1 |

#### 38. `blk.mic-ambient`: ambient-noise microphone

| Field | Content |
|---|---|
| Bound by | BRD-031 (should); BRD-027 (the privacy LED covers it too, since it shares MIC_1V8) |
| Interface | PDM CLK1, SDI1, MIC_1V8 |
| Power domain | MIC_1V8 (shared with `blk.mic-main`). A separate switch is not proposed: it would let this microphone run without the privacy LED, against BRD-027 |
| Measure | Proposed: 0 Ω link + shunt footprint on its MIC_1V8 branch (G10) |
| Absent state | Unfitted: SDI1 pulled down; CLK1 parked low |
| Holds / revision | Holds: IM72D128 |
| Alternates | `im72d128` |
| Software | Second PDM channel; description `sensors` (ambient noise) |
| Level | — / Q1 |

### 3.6 Radio and sensors

#### 39. `blk.radio`: Wi-Fi and Bluetooth module

| Field | Content |
|---|---|
| Bound by | BRD-025, BRD-029 (must), BRD-030 (should: item tracking, T1-069 protections); T1-077 (certified variants carry granted parts only; 802.15.4 disabled while not wired) |
| Interface | SDIO 3.0 (SDMMC1), UART1 with RTS/CTS (Bluetooth), `WL_PD_N` (module PDn through the `WL_PD_HOLD_N` translator; names with the `_N` suffix from 2026-10-25), `WL_WAKE_OUT` and `BT_WAKE_OUT` (PMUIO2 wake balls), `BT_WAKE_IN`, vcc3v3_wl (AVDD33), vcc1v8_wl (AVDD18, BOM line 129), VIO and SD_VIO 1.8 V (vcc_1v8, VCCIO4), RF ports ANT0, ANT1. PCM and the 32.768 kHz input are dropped (pinout v1 C7, C18). The 802.15.4 SPI (module pins 4–8) is not connected; the four SPI2 M0 balls stay unassigned spares reserved for a variant (decision 2026-10-24, T1-077) |
| Power domain | vcc3v3_wl from a TPS22916C (BOM v1.9 line 50; RK809 SWOUT1 before), vcc1v8_wl following it; both from expander P06 `WL_PWR_EN`, which holds through suspend. Decision 2026-10-24: off in suspend by default; on in suspend only while the listener enables item tracking, and then vcc_1v8 (VIO, SD_VIO, VCCIO4) stays on too. Suspend draw **UNVERIFIED** until measured on M-RF; `WL_PDN` hold through standby open (BOM §7 item 40) |
| Measure | Links 11 (vcc3v3_wl) and 12 (vcc1v8_wl), power tree §4.12 |
| Absent state | Module unfitted or off: PDn pulled low; host-wake lines pulled to "no wake"; SDIO and UART lines with SoC pulls and parked low before VBAT is removed (module sequencing **UNVERIFIED**: datasheet not retrieved) |
| Holds / revision | Holds: u-blox MAYA-W271-00B (same chip, line 55; land **UNVERIFIED**) and any module behind SDIO, UART, PCM, the same supplies and two RF ports. Revision: PCIe or USB radios, a module that needs another supply. A PCIe + USB 2×2 module is a swap that needs a block revision; for it the PCIe sideband balls (`RSVD_PCIE_PERST_N`, `RSVD_PCIE_CLKREQ_N`, `RSVD_PCIE_WAKE_N`) and USB 2.0 HOST3 stay reserved and unconnected (pinout v1, 2026-10-25) |
| Alternates | `maya-w271` |
| Software | `sdmmc1` node (mainline: Wi-Fi on SDIO); `nxpwifi` on SDMMC1 (DKMS until 7.3), `btnxpuart` serdev node (DKMS); iwd and BlueZ |
| Sub-blocks | `blk.radio-module`, `blk.radio-power` (sheets of this record, each part's `Block` field) |
| Level | — / Q1 (Q2 items PCB-R-04, PCB-R-05) |

#### 40. `blk.antennas`: antenna feeds

| Field | Content |
|---|---|
| Bound by | BRD-025, BRD-029 (must); PCB-R-02, PCB-R-03 [Q1], PCB-R-04 [Q2] |
| Interface | ANT0, ANT1 50 Ω feeds, U.FL, π-network positions (DNP by default, line 58) |
| Power domain | Passive |
| Measure | Conducted RF at the U.FL |
| Absent state | Antenna unplugged is not a variant; π-network 0 Ω series fitted, shunts DNP |
| Holds / revision | Holds: antennas on the module's certification lists. Revision: on-board antennas |
| Alternates | Taoglas / Kyocera AVX FPC (**UNVERIFIED**) |
| Software | — |
| Level | — / Q1 |

#### 41. `blk.nfc-tag`: NFC dynamic tag

| Field | Content |
|---|---|
| Bound by | BRD-057 (should) |
| Interface | I2C2 at 0x55, field-detect (FD) to a GPIO interrupt (not assigned, G6), VCC (rail not stated, G6), loop antenna (line 126) |
| Power domain | None today (G6) |
| Measure | Proposed shunt footprint (G12) |
| Absent state | Unfitted: 0x55 free on I2C2; FD line pulled up (open-drain). Powered off with I2C2 live: whether the NTAG I2C plus pins tolerate the bus with VCC at 0 V is **UNVERIFIED** (G6) |
| Holds / revision | Holds: NTAG I2C plus 2k (same family). Revision: ST25DV (Type 5, other land) |
| Alternates | `nt3h2211` (**UNVERIFIED** MPN and land) |
| Software | No kernel driver (i2c-dev); `org.opendap.hw.Nfc` |
| Level | — / Q1 |

#### 42. `blk.nfc-reader`: removed

Removed on 2026-10-27 (maintainer decision, reason: board area; BOM v1.18 item 7, BRD-057 reworded: NFC as the tag only): the T1 has no NFC reader in any model. The PN7160 and its front end (EMC filter, matching, RX path, 27.12 MHz crystal), the antenna contacts, the `NFC_VBAT` switch and link #18 go; the SoC balls of `NFC_VEN`, `NFC_DWL_REQ` and `NFC_IRQ` become spares without a pad (pinout v1), expander P05 (`NFC_PWR_EN`) a spare. `blk.nfc-tag` (#41) does not depend on the reader and stays. The number is not reused.

#### 43. `blk.imu`: motion sensor

| Field | Content |
|---|---|
| Bound by | BRD-032 (should); BRD-009 wake source |
| Interface | I2C2 at 0x6A, INT1 (wake on motion, GPIO0), INT2 (unconnected or expander), VDD and VDDIO |
| Power domain | vcc_1v8, no switch. vcc_1v8 is off in suspend (power tree §3) while the IMU must stay on to wake on motion (§6.5) (G1) |
| Measure | Proposed shunt footprint (G12) |
| Absent state | Unfitted: INT1 pulled down so the wake line does not float; 0x6A free |
| Holds / revision | Holds: LSM6DSOXTR (same driver and footprint, line 59) |
| Alternates | `lsm6dsox` |
| Software | `imu` node (the LSM6DSV16X); `st,lsm6dsv16x` (`st_lsm6dsx`); description `sensors` |
| Level | — / Q1 |

#### 44. `blk.haptics`: haptic driver and actuator

| Field | Content |
|---|---|
| Bound by | BRD-058 (should); a bench check that the LRA adds nothing audible to either output (line 123) |
| Interface | I2C2 at 0x5A, EN (GPIO not assigned, G20), IN/TRIG, VDD (vcc3v3_sys), LRA terminals (actuator on the case) |
| Power domain | EN (standby) |
| Measure | Proposed shunt footprint on VDD (G12) |
| Absent state | EN pulled low; unfitted: 0x5A free, LRA contacts open |
| Holds / revision | Holds: other LRAs within the driver's range. Revision: DA7280 (not pin-compatible) |
| Alternates | `c10-100` actuator (Precision Microdrives) |
| Software | `haptics` node (the DRV2605L); `ti,drv2605l` (DKMS); `org.opendap.hw.Haptics` |
| Level | — / Q1 |

#### 45. `blk.tpm`: hardware key holder

| Field | Content |
|---|---|
| Bound by | BRD-059 (should); OS-032 keystore |
| Interface | I2C2 at 0x2E, reset and PIRQ (neither assigned in the pin plan, G5), supply (rail not stated, G5) |
| Power domain | None today (G5) |
| Measure | Proposed shunt footprint (G12); standby current **UNVERIFIED** (line 122) |
| Absent state | Unfitted: 0x2E free; reset pulled to its inactive level; PIRQ pulled up |
| Holds / revision | Holds: SLB9673 firmware versions. Revision: ST33KTPM2 (not pin-compatible: dual footprint or revision, line 122) |
| Alternates | `st33ktpm2` as an alternate footprint (DNP) if the land fits under PCB-Z-03 |
| Software | `tpm` node (the SLB9673); `infineon,slb9673`, `tcg,tpm-tis-i2c` (DKMS); `org.opendap.hw.KeyHolder` |
| Level | — / Q1 |

#### 46. `blk.rp2354`: coprocessor

| Field | Content |
|---|---|
| Bound by | BRD-014 (should), BRD-005, BRD-015, BRD-019 (must), BRD-041 (should, Draft). BRD-014 stays should only while no must function depends on it: the pin plan relays wake lines through it (requirements context) |
| Interface | UART0, IRQ/wake (0_C7), RUN, BOOTSEL (open-drain), SWD, USB (EHCI host 2), passive taps on I2S1 SCLK, LRCK, SDO0–SDO2 (BRD-041), optional I2C2 |
| Power domain | RP_3V3 and RP_IOVDD_1V8 (2 × TPS22916C, `RP_PWR_EN`; default an open question, power tree §8) |
| Measure | Proposed shunt footprints on RP_3V3 and RP_IOVDD_1V8 (G12) |
| Absent state | Unfitted or off: the I2S taps reach FT pins only (G4); UART0 TX from the SoC parked; IRQ pulled down on the host side (`blk.soc-vccio-b`, "no wake"); RUN open drain with 4.7 kΩ to RP_IOVDD_1V8; BOOTSEL (QSPI_SS, on RP_3V3) pulled low only through an N-FET whose gate is a 1.8 V ball with a pull-down on the host side (pinout v1 C6, BOM v1.9 line 35) |
| Holds / revision | Holds: RP2350A with external QSPI flash (other BOM, line 12). Revision: RP2354B (QFN-80) |
| Alternates | `rp2350a-qspi` |
| Software | `uart0` node (mainline: the coprocessor link); Flashed from Blackbird OS (BRD-015); serial node on UART0; description component |
| Sub-blocks | `blk.rp2354-core`, `blk.rp2354-power` (sheets of this record, each part's `Block` field) |
| Level | — / Q1 |

### 3.7 Controls and debug

#### 47. `blk.buttons`: side buttons

| Field | Content |
|---|---|
| Bound by | BRD-016, BRD-017, BRD-035, BRD-036 (must), BRD-056 (should), T1-022 (must, Action travel) |
| Interface | Power → RK809 PWRON; Vol+ → SARADC_VIN0; Vol− → SARADC_VIN1; Action → GPIO0 (wake); TPD1E10B06 per line |
| Power domain | Passive (pull-ups on vcca1v8_pmu and the SARADC reference) |
| Measure | — |
| Absent state | Released state through the pulls |
| Holds / revision | Holds: same-actuation switches on the land. Revision: the Action part (line 76 Open) |
| Alternates | Action: Open |
| Software | `adc_keys` node (the volume keys); `rk805-pwrkey`, `adc-keys`, `gpio-keys`; description `controls` with roles |
| Level | — / Q1 |

#### 48. `blk.maskrom`: MaskROM entry

| Field | Content |
|---|---|
| Bound by | BRD-035, BRD-043 (must) |
| Interface | PWRON_N (through BAT54), VOLDN_N, eMMC_D0 (through 1 kΩ), vcca1v8_pmu |
| Power domain | vcca1v8_pmu, always on |
| Measure | — |
| Absent state | Not omitted: the FET gate pull-down (100 kΩ) holds D0 free while vcca1v8_pmu is down |
| Holds / revision | Holds: Nexperia 74LVC1G57GW / 1G58GW (line 98) |
| Alternates | `nexperia-gates` |
| Software | None |
| Level | — / Q1 (simulated: boost and MaskROM study) |

#### 49. `blk.debug`: test and debug access

| Field | Content |
|---|---|
| Bound by | BRD-040, BRD-047 (must), T1-026 (must), PCB-T-01 to PCB-T-03 |
| Interface | UART2 pads (1.8 V), I2S/DSD pads (BRD-040), rail test points (PCB-T-02), RP2354A SWD pads, and the per-block measurement links proposed in §7 |
| Power domain | — |
| Measure | It is the measurement access |
| Absent state | Pads only; links are 0 Ω in production |
| Holds / revision | — |
| Alternates | Links: shunt value (full) or 0 Ω (production) |
| Software | — |
| Level | — / Q1 |

#### 50. `blk.cover-detect`: back-cover detect

| Field | Content |
|---|---|
| Bound by | ADR 0020 item 7 (should); no requirement names it; T1-086 is met without it. Added in BOM v1.10 (line 143) |
| Interface | One GPIO input (chosen in the pinout); a contact pad at the board edge for the case's actuator; TPD1E10B06 at the pad |
| Power domain | The pull-up on the GPIO's IO rail; no switch (µA while a closed cover grounds the input) |
| Measure | None (pull-up current only) |
| Absent state | If `dnp`: the GPIO's internal pull holds the "cover closed" level and the device description omits the input, so Blackbird OS never acts on it; no other block depends on it |
| Holds / revision | Holds: any switch or contact the case actuator uses, on the same pad. Revision: a detect that needs a supply (Hall or optical) |
| Alternates | None |
| Software | `cover_detect` node (the `gpio-keys` switch); `gpio-keys` (a switch event); Blackbird OS powers down in order (ADR 0017 item 3 sequence with no adapter) when the cover lifts |
| Level | — / Q2 (PCB-L-10) |

## 4. Variant files

### 4.1 Format: `opendap.board-variant/v1`

A variant is a TOML file in `hardware/variants/`, one per variant (RFC 0011 rule 7). It is the only place where a variant is defined; KiCad's variant data, the BOM, pick-and-place, devicetree overlays and the device description are generated from it (§6).

| Key | Type | Meaning |
|---|---|---|
| `schema` | string | `"opendap.board-variant/v1"` |
| `board` | string | Board identity (`"t1-main-board"`) |
| `name` | string | Variant name; also the KiCad variant name and the value written to the board EEPROM |
| `kind` | string | RFC 0011 §3 kind: `full`, `production`, or an application name |
| `status` | string | `proposed` or `accepted` (accepted only by the maintainers' decision) |
| `target_level` | string | RFC 0010 level this variant is built and verified to |
| `promise` | array | Requirement IDs the variant is declared against; every block bound by a must requirement in this list is `fit` or `alternate` (checked) |
| `catalog` | string | Path of this catalog; every catalog block appears exactly once under `[blocks]` |
| `[instrumentation]` | table | `links`: `"shunt"` (measurement links fitted with their shunt value) or `"zero-ohm"`; `test_points`: `"fit"` |
| `[blocks]` | table | One entry per block ID: `{ state = "fit" \| "dnp" \| "alternate", alternate = "<name>", params = { … }, open = "<pending decision>", note = "<reason>" }` |

Rules:

1. `state = "alternate"` names an alternate listed in the block's record; an alternate on another land is a DNP footprint pair in the block's sheet, never a new land outside it.
2. `params` keys are declared in the block's record (for example `capacity_gb` for `blk.emmc`, `shunt_mohm` for `blk.current-monitors`).
3. `open` marks a value the maintainers have not decided; the generator emits it as given and reports the open item. A variant with an `open` entry cannot be `accepted`.
4. A `dnp` block's absent state must pass the check (§6) before the variant is generated.
5. Comments carry the reason; the reason for a `dnp` in a product variant names the cost or availability evidence.

### 4.2 The T1 variants

The files list the 50 blocks plus `blk.shields` (51 entries; 50 until BOM v1.10 added `blk.cover-detect`), so the shield footprints' DNP state is data too.

- [`full.toml`](../../hardware/variants/full.toml): prototype 1 (RFC 0011 rule 1, BRD-053). Every block, every *should* part and every instrumentation link with its shunt value; shields DNP (fitted only if measurement requires, line 90).
- [`production.toml`](../../hardware/variants/production.toml): Commercial and DIY editions (T1-004, ADR 0013). Same blocks as `full`, measurement links as 0 Ω, the four INA236 kept (ADR 0013). Open: eMMC 16 or 32 GB (BRD-037). The PN7160 question closed on 2026-10-27: the reader is withdrawn from every model (#42).

## 5. KiCad 10 and variants

Tested on the developer machine with KiCad 10.0.7 (`kicad-cli version`), a two-resistor test schematic written for the purpose (not committed), and the KiCad 10.0 Schematic Editor manual, section "Design variants" (docs.kicad.org/10.0, read 2026-10-24), plus the 10.0 sources of the schematic reader and writer (`eeschema/sch_io/kicad_sexpr/`, read 2026-10-24).

| Capability | KiCad 10.0.7 | Evidence |
|---|---|---|
| Named variants on one design | Yes. Variant data is stored per symbol instance in the schematic (`(variant (name …) …)` inside each instance path); names and descriptions also in the project file (`schematic.variants`) | Manual; 10.0 writer source; test |
| DNP per variant | Yes | Test: `sch export bom --variant production` marks the symbol DNP; `--exclude-dnp` drops it |
| Exclude from BOM, position files, simulation, board per variant | Yes (`in_bom`, `in_pos_files`, `exclude_from_sim`, `on_board`) | Writer source; test (BOM exclusion honoured with file version ≥ 20260306: the reader inverts `in_bom` for older files) |
| Field overrides per variant (Value, MPN, Footprint, any field) | Yes; the Reference cannot be overridden | Manual; test: Value and MPN overrides appear in the variant BOM |
| Sheet-level DNP and exclusions | Yes: marking a hierarchical sheet DNP marks every symbol in it and its sub-sheets | Manual |
| Variant-aware outputs | `--variant` on `sch export bom, pdf, svg, dxf, ps, hpgl, netlist`; `pcb export pos, gerbers, pdf, svg, dxf, ps, ipc2581, odb, step, stpz, glb, brep, xao, ply, stl, u3d, vrml, 3dpdf` (not `drill`) | `kicad-cli … --help` |
| Netlist per variant | S-expression netlist: identical with and without `--variant` (overrides not applied). XML netlist (`--format kicadxml`): carries every variant's overrides in a `<variants>` element per component | Test (`diff`) |
| ERC and DRC per variant | No `--variant` on `sch erc` or `pcb drc` | `kicad-cli … --help` |
| Different copper or outline per variant | No: "All variants share the same copper, the same netlist, and the same board outline" | Manual |
| Footprint override on the PCB | Field overridable; effect on the board **UNVERIFIED** | The manual lists footprint substitution as a use, yet states that copper is shared; not tested on a PCB. This catalog uses alternate footprints as DNP pairs instead |

**Finding.** KiCad 10 covers the assembly half of RFC 0011 rule 7 (variants are data; "rule 6" in the RFC's open question, before the 2026-10-24 amendment): per-variant BOM, position files and fab and 3D outputs, generated by `kicad-cli` from variant data inside the schematic, with sheet-level DNP matching the one-sheet-per-block structure. It does not cover the rest of the rule: devicetree overlays, the device description and the verification plan are outside KiCad; there is no per-variant ERC, DRC or absent-state check; and the variant data lives inside the schematic, edited in the GUI, so a hand edit could diverge from the variant file. A generator is needed, but a thin one: it writes KiCad's own variant data from the TOML files, lets `kicad-cli` produce the fab outputs, and adds the checks and the software outputs.

## 6. Absent-state check

Every variant is checked on the schematic netlist (the XML netlist, which carries every variant's overrides), per scenario: **unfitted** (the variant's DNP set) and **unpowered** (for each switched block, its switch off with everything else on, plus the suspend state of power tree §6.5).

1. **Load.** Parse the XML netlist: components with their `Block`, fields and per-variant overrides; nets with their nodes and pin types; mark each component fitted or not for the variant.
2. **Rails.** Classify supply nets (power symbols and `NetRole = supply`). A rail is live if one fitted source drives it and, in the unpowered scenario, its switch is on. Propagate through switches and regulators.
3. **Per signal net**, with the fitted nodes only:
   - *floating input:* at least one input or bidirectional pin, and no driver (output, open-drain with a pull-up to a live rail, or a pull resistor to a live rail or ground) → error;
   - *back-powering:* a pin whose IO supply rail is dead, and a pull-up, driver or bus on the net whose rail is live, with no isolator between them (an isolator is a part whose enable is tied to the dead rail's domain) → error;
   - *bus held:* an open-drain bus (I2C, wired-OR interrupt) with a fitted device on a dead rail → error unless isolated;
   - *strap change:* a net with `NetRole = strap` whose resolved level (from fitted pulls) differs from the strap's declared level in the full variant → error;
   - *enable default:* an enable net whose resolved power-up level is not the off state (PCB-A-13 [Q1], BRD-019) → error.
4. **Promise.** Every block bound by a must requirement in the variant's `promise` is `fit` or `alternate` → error otherwise.
5. **Boundary.** A net that connects two blocks and is not in either block's interface list → warning (rule 4).
6. **Report** by level: findings 3–4 are Q0 for supply and battery nets and Q1 otherwise; 5 is Q1 as a warning (RFC 0010 rule 1: untagged is Q1).

Known limit: the check sees the schematic, not firmware ordering. Rules such as "park I2S low before removing DAC_DIG_1V8" stay review items until the driver sequence is tested on the bench.

## 7. Gaps the schematic must close

Proposed parts come from families already in the BOM where possible; Nothing here edits the BOM, the power tree or the PCB design constraints: each row is a proposal for those documents' owners.

| # | Block(s) | Gap | Proposal | Part (availability) | Status (BOM v1.8, power tree v0.2) |
|---|---|---|---|---|---|
| G1 | `blk.imu` | IMU on vcc_1v8, which is off in suspend (power tree §3), yet it is the wake-on-motion source in suspend (§6.5) | Supply the IMU (VDD, VDDIO) from vcca1v8_pmu (always on) through a 0 Ω link with a shunt footprint; I2C2 pull-ups on the same rail (G16) | 0 Ω 0402 (jellybean) | **Closed** (BOM v1.8 line 59; link line 137): IMU on vcca1v8_pmu |
| G2 | `blk.dac-l`, `blk.dac-r` | Both CS43198 sit on the shared 1.8 V I2C2 while DAC_DIG_1V8 is switched; their control pins tolerate only VL + 0.3 V (BOM §4.2), so a live bus back-powers an unpowered DAC; same for `DAC_INT` if pulled up to an always-on rail and for the I2S data lines | An I2C isolator between I2C2 and the two DACs, enabled from DAC_DIG_1V8, with 0 Ω bypass footprints (fit the bypass only if the CS43198 control pins prove fail-safe); `DAC_INT` pull-up on DAC_DIG_1V8; series-resistor footprints on SDO0–SDO2 and DSD clock at the DAC side; driver rule: park I2S low first | TI TCA9406DCUR (BOM line 94 second source); same-voltage operation on both sides **UNVERIFIED** until its datasheet is read; CS43198 fail-safe behaviour **UNVERIFIED** | **Closed in hardware** (line 133: SN74LVC2G66 controlled by DAC_DIG_1V8, bypass DNP; line 134 series footprints); CS43198 fail-safe **UNVERIFIED** decides bypass vs switch (BOM §7 item 34). TCA9406 rejected: VCCB ≥ 2.3 V |
| G3 | `blk.mclk` | MCLK_3V1 (`AUDIO_LN_EN`) and DAC_DIG_1V8 (`DAC_DIG_EN`) are separate enables: the attenuated clock can drive an unpowered XTI | Hardware interlock: `AUDIO_LN_EN` gated by DAC_DIG_1V8 power-good (AND), or a single enable for both; ST lines with pull-downs (kept) | SN74LVC1G58 (configurable gate, BOM line 98) at the right logic level | **Closed** (line 135: SN74LVC1G57 AND, TPS7A2031 EN = `AUDIO_LN_EN` AND DAC_DIG_1V8; the 1G58 has no plain AND). BOM v1.9 ([ADR 0019](../adr/0019-master-clock-divided-from-twice-the-frequency.md)): the attenuator is replaced by dividers on MCLK_1V8, whose EN is DAC_DIG_1V8, so the clock path to XTI is off whenever the DACs are |
| G4 | `blk.rp2354` | Passive I2S taps (BRD-041), UART0 and wake lines reach the RP2354A while RP_3V3 / RP_IOVDD_1V8 can be off: IO into an unpowered part whenever audio plays | Series-resistor footprints at the tap branch (stub ≤ 1 mm, PCB-A-12) sized to the RP2350's injection limit, or a rule that the RP rails are on whenever I2S1 runs; RP2350 GPIO behaviour unpowered **UNVERIFIED** | Resistors (jellybean); value **UNVERIFIED** | **Narrowed** (line 134): RP2350 FT pins accept 3.63 V at IOVDD = 0 V (absolute maximum), taps on FT GPIO0–25 only (pinout v1); 0 Ω tap footprints; injection into an unpowered pad **UNVERIFIED** |
| G5 | `blk.tpm` | No supply rail, reset or PIRQ line assigned | Supply from vcc_1v8 through a 0 Ω link + shunt footprint; reset on a spare expander line with a pull to inactive; PIRQ to a free 1.8 V GPIO (balls freed by interface v1, pin plan §4.3) or polled (`tpm_tis_i2c` polling **UNVERIFIED**) | 0 Ω (jellybean) | **Closed for supply and measure** (line 122: vcca1v8_pmu, 0.1 Ω link line 137); reset and PIRQ on native 1.8 V GPIO left to pinout v1; current **UNVERIFIED** |
| G6 | `blk.nfc-tag` | No VCC rail and no field-detect GPIO assigned; pin behaviour with VCC off on a live I2C2 **UNVERIFIED** | VCC from vcca1v8_pmu (so the bus never sees it unpowered) through a 0 Ω link + shunt; FD to the wake-capable 0_A0 freed by interface v1 (pin plan §4.3, owner choice) | 0 Ω (jellybean) | **Narrowed** (line 125: VCC on vcca1v8_pmu, 10 Ω link line 137); FD GPIO to pinout v1; tag supply range **UNVERIFIED** (NXP data sheet not retrieved) |
| G7 | `blk.nfc-reader` | VBAT "from the battery path" is 6.0–8.8 V on the 2S tree; DWL_REQ planned on a 3.3 V expander line into a 1.65–1.95 V pin | VBAT from VSYS_LV (3.8 V) behind a load switch, with a shunt footprint; DWL_REQ and VEN on native 1.8 V GPIO or through a level shifter; PN7160 VBAT range and peak current **UNVERIFIED** until its datasheet is read | TI TPS22919DCKR (line 50), 1.5 A rating against the PN7160 peak **UNVERIFIED** | **Closed** (lines 50, 127): NFC_VBAT from VSYS_LV via an eighth TPS22919 (290 mA max = 19 %); VBAT 2.8–5.5 V, 6 V absolute (PN7160 Rev. 3.4); VDD(PAD) 1.8 V on vcca1v8_pmu; VEN, DWL_REQ on native 1.8 V GPIO (pinout v1). 2026-10-27: moot, the block withdrawn |
| G8 | `blk.fp-controls` | I2C3 pull-up rail not defined; an always-on rail back-powers touch, ALS and HID parts when FP_3V3 is off; HID_INT and ALS_INT are pulled up to 1.8 V while their open-drain sources may be unpowered | I2C3 pull-ups on FP_3V3; interrupt pull-ups kept on PMUIO2 only if the faceplate parts' INT pins tolerate it unpowered (VEML6030, GT911 **UNVERIFIED**), else gate them | Resistors (jellybean) | **Narrowed** (BOM §4.2 VCCIO5 row): I2C3 pull-ups on FP_3V3; INT pull-up tolerance of VEML6030 and GT911 unpowered still **UNVERIFIED**. BOM v1.9 (pinout v1 C4): `HID_INT` and `ALS_INT` are 3.3 V lines with 4.7 kΩ pull-ups on FP_3V3, so nothing pulls them up while the faceplate is off (line 141) |
| G9 | `blk.fp-controls` | Touch INT is the GT911 address strap; with no faceplate or a different controller its level at reset is undefined | A board pull on touch INT to the default address level, value from the GT911 sheet (**UNVERIFIED**); a `strap` net role for the check | Resistor (jellybean) | **Open**: pull footprint on touch INT for the schematic; value from the GT911 sheet (**UNVERIFIED**); not a power item |
| G10 | `blk.mic-main`, `blk.mic-ambient` | One switch for both microphones (correct for BRD-027) but no per-microphone measurement; PDM clocks can drive unpowered microphones | 0 Ω link + shunt footprint per microphone branch; PDM pins in a pinctrl sleep state driving low while MIC_1V8 is off | 0 Ω (jellybean) | **Closed** (line 137, links 34–35, power tree §4.12); PDM CLK sleep state is a pinctrl rule |
| G11 | `blk.current-monitors`, `blk.audio`, `blk.fp-*`, `blk.pwr-vsys-lv` | Audio and display shunt positions undefined; audio draws from both VSYS (LMR33630C) and VSYS_LV, so one channel cannot attribute it; VSYS_LV itself is unmeasured | Audio INA236 shunt on a dedicated VSYS_LV audio branch (TPS65131, TPS62840, TPS7A2031, DAC_VP), plus a shunt footprint with Kelvin pads on the LMR33630C VIN (or a fifth INA236 if an address is free); display shunt on the TPS61169 VIN, links on FP_3V3, FP_1V8, FP_VCI; a shunt footprint at the VSYS_LV output | INA236AIDDFR (line 54); fifth-address option (INA236B) **UNVERIFIED**; shunts as line 43's family (Vishay WSL, 1206) or 0603 thin-film (part **UNVERIFIED**) | **Closed** (lines 54, 136, 137; power tree §4.12): audio INA236 on a dedicated VSYS_LV branch (20 mΩ), fifth INA236B at 0x48 on the LMR33630C VIN, display on the TPS61169 VIN, H5 link on VSYS_LV |
| G12 | 20 blocks without their own measurement | No measurement point on lpddr4x, emmc, microsd, pwr-3v3-sys, vdd-cpu (output), audio-supply, mclk, dac-l/r (VA), hpa-se, hpa-bal, speaker, radio, nfc-tag, nfc-reader, imu, haptics, tpm, rp2354, status-led (several of these share one link) | One measurement link per block supply: a 0603 (or 1206 above 1 A) footprint fitted with a shunt in `full` and 0 Ω in `production`, two Kelvin test pads, on the block side of its switch; low-current blocks (µA–mA) use a 1–10 Ω value for a bench meter, the rest 10–100 mΩ (values per block at schematic capture) | Shunt and 0 Ω parts jellybean; current-sense part numbers **UNVERIFIED** | **Closed** (line 137): 35 links, five classes, shunt in `full`, 0 Ω in `production` (H5 keeps 5 mΩ) |
| G13 | `blk.radio`, `blk.microsd` | SWOUT1 and SWOUT2 discharge **UNVERIFIED** (power tree §5); radio sequencing and the 1.8 V AVDD18 rail need the Murata datasheet (PCB constraints §9 item 3) | Close with the Murata datasheet; add a discharge resistor footprint on vcc3v3_wl and vcc3v3_sd | Resistors (jellybean) | **Narrowed** (lines 129–131): AVDD18 rail vcc1v8_wl added; discharge footprints DNP on vcc3v3_wl and vcc3v3_sd; module sequencing **UNVERIFIED** (datasheet). BOM v1.9: vcc3v3_wl comes from a TPS22919, whose quick output discharge empties it, so that footprint stays a spare; vcc3v3_sd unchanged |
| G14 | `blk.hat-signals` | `PCIE_PERST#` = SoC PERST# AND HAT power-good (power tree §6.4) has no part in the BOM; `I2S_MCLK` buffer is Open (line 112) | A single-gate AND at 3.3 V with Ioff; the MCLK buffer as BOM line 112 decides | SN74LVC1G58 family (line 98) or a 1G08 (not in the BOM) | **Narrowed** (line 135): PERST# AND gate on vcc3v3_sys; `I2S_MCLK` buffer still Open (line 112). BOM v1.9 (ADR 0019): the oscillator net has 1.3 pF left, so the HAT copy needs its own divider or a buffer behind one and a re-run of `sim/mclk-divider`; OE from `HAT_MCLK_EN` (GPIO1_A6) 2026-10-24 (BOM v1.11): the gate's output is `HAT_EXT_SB0`, PERST# or the sensor reset (hats `standard/` interface v1.1). 2026-10-25: closed by removal (RFC 0014): no PCIe to the HAT and no HAT MCLK |
| G15 | `blk.gpio-expander` | VCCI rail not named; if vcc_1v8, it is off in suspend while the expander holds enables, and the TCA6416A port state with VCCI off is **UNVERIFIED** | VCCI on vcca1v8_pmu; every expander-driven enable keeps its board pull-down | — | **Closed** (line 93): VCCI on vcca1v8_pmu |
| G16 | I2C2 bus | Pull-up rail of I2C2 not defined; the bus mixes always-on parts (LP5521 EN on vcca1v8_pmu, expander) with switched ones (DACs, RP2354A) | Pull-ups on vcca1v8_pmu; every switched device behind an isolator (G2) or moved to an always-on rail (G1, G5, G6); the RP2354A off I2C2 unless isolated | — | **Closed** (BOM §4.2 PMUIO2 row): pull-ups on vcca1v8_pmu, every I2C2 device always on or isolated |
| G17 | `blk.emmc` | The 16 GB production option has no MPN in the BOM | Pick a 16 GB part on the same 153-ball land before the production variant is accepted | **UNVERIFIED** | **Narrowed** (line 138): Samsung KLMAG1JETD-B041 named; land and height **UNVERIFIED** (NDA datasheet) |
| G18 | `blk.lpddr4x` | The 2 GB fallback and the SK hynix second source have no land or blob check | Check land and rkbin support before either is listed as an accepted alternate | **UNVERIFIED** | **4 GB closed** (BOM v1.12, ADR 0022): CXMT CXDB5CBAM-MA-B on the shared land, checked by libs `kicad/` and listed T/A by Rockchip; SK hynix removed. **Open:** the 2 GB fallback (BOM §7 item 38) |
| G19 | `blk.board-id` | Supply rail not stated | vcca1v8_pmu, with the variant name in the EEPROM map | — | **Closed** (line 17): VCC on vcca1v8_pmu |
| G20 | `blk.haptics` | DRV2605L EN has no GPIO | A spare expander line (five are spare, line 93) with a pull-down | — | **Closed** (lines 93, 123): `HAPTIC_EN` on an expander spare with pull-down (pinout v1) |
| G21 | `blk.audio` | No hardware guarantee that the I2S lines are parked before DAC_DIG_1V8 is removed (power tree §5 states it as a software step) | G2's series-resistor footprints plus a driver sequence test at bring-up | — | **Narrowed** (line 134): series footprints at the DAC end; the driver sequence test at bring-up remains |
| G22 | `blk.cover-detect` | No GPIO assigned (BOM v1.10, ADR 0020 item 7) | A spare GPIO that wakes from suspend, so the input is seen while suspended | — | **Closed** (2026-10-26, pinout v1 §7): `COVER_DET_N` on GPIO0_A6 (PMUIO1, wake-capable) |

## 8. Sources

- RFC 0011 (amended 2026-10-24) and RFC 0010, rfcs repository.
- BOM v1.7 lines 1–128, §4.2, §4.3, §7; power tree v0 §2, §3, §5, §6; PCB design constraints v0.5; pinout v1; board requirements; ADR 0013, ADR 0016.
- System hardware support spec (Draft, 2026-10-23); t1 faceplate interface v1 (v0 until 2026-10-24) and t1 ADRs 0004, 0005; hats `standard/` HAT interface v1.1 and ADR 0005.
- KiCad 10.0 Schematic Editor manual, "Design variants", docs.kicad.org/10.0/en/eeschema (read 2026-10-24); KiCad 10.0 sources `eeschema/sch_io/kicad_sexpr/sch_io_kicad_sexpr.cpp` and `sch_io_kicad_sexpr_parser.cpp`, `eeschema/schematic_settings.cpp` (gitlab.com/kicad/code/kicad, branch 10.0, read 2026-10-24); `kicad-cli` 10.0.7 help and test exports on the developer machine (2026-10-24).
