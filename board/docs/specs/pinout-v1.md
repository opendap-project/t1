# Pinout v1 of the T1 main board

- **Status:** Draft v1 (2026-10-24). It supersedes the ball allocation of pin multiplexing v0 (§2 and §4.3 there). Nothing here is drawn or measured: the schematic is checked against it, and every **UNVERIFIED** item names what closes it. No decision, priority or requirement status changes here; the BOM and power-tree changes it needs are listed in §9 for their owner, and the faceplate contact positions in §8 are a proposal for the t1 spec.
- **Updated 2026-10-24 (hats `standard/` interface v1.1, t1 faceplate interface v1):** the HAT section follows hats `standard/` [interface v1.1](https://github.com/opendap-project/hats/blob/main/standard/docs/specs/interface-v1.md) and [ADR 0005](https://github.com/opendap-project/hats/blob/main/standard/docs/adr/0005-interface-v1-1-shared-extension-and-contact-reduction.md): the freed SWD balls A22 and B22 drive the extension switch (`HAT_EXT_SEL`, `HAT_EXT_PD`), SWD becomes the bit-banged L2 alternate on `HAT_GPIO2`/`HAT_GPIO3`, the PCIe sideband balls carry `EXT_SB0`–`EXT_SB2`, and the PCIe and CSI-2 balls go to the two TMUXHS4412 ports ([BOM v1.11](bom-v1.md#changes-in-v111) line 144). Faceplate sources follow BOM v1.11 (current-limited rail switches, TPS61160, I2C3 pull-ups 2.2 kΩ); "faceplate interface v0" is now v1. No faceplate contact moves. Changes listed in §10.
- **Updated 2026-10-25 (BOM v1.12, [ADR 0021](../adr/0021-vdd-cpu-buck-ti-tps62869.md), [ADR 0022](../adr/0022-lpddr4x-micron-mt53e1g32d2fw-with-cxmt-second-source.md)):** the I2C0 note names the TPS62869 at 0x42; the `vdd_cpu` rows take its 0.85–1.15 V range and VOS remote sense; the six rank-1 DDR outputs are not connected (single-rank DRAM, closes O14). No ball moves; §10 lists the rows.
- **Updated 2026-10-25 ([RFC 0014](https://github.com/opendap-project/rfcs/blob/main/text/0014-hat-interface-v2-usb-only.md), hats `standard/` [interface v2](https://github.com/opendap-project/hats/blob/main/standard/docs/specs/interface-v2.md), BOM v1.13):** HATs are USB only. 41 HAT balls change: 23 GPIO balls become spares, the 16 CSI-2 and PCIe PHY balls have no consumer (`NC`, O2), AG37 takes the HAT port controller's interrupt (`HAT_PD_INT_N`) and SARADC_VIN3 takes eFuse #C IMON (closes C10). Conflict C1 (I2C5 M1 on the HDMI DDC balls) closes with the HAT I2C. USB3 HOST1 to the HAT port is unchanged. Expander P01 becomes `HAT_VBUS_DISCH`, P16 a spare. §3 HAT lists the balls; §5 and §10 note the closed items.
- **Updated 2026-10-25 (CRAFT-84 net names):** the three active-low DDR nets end in `_N`, upper case: `DDR_CS0n_A` → `DDR_CS0_A_N` (B3), `DDR_CS0n_B` → `DDR_CS0_B_N` (1B5), `DDR_RESETn` → `DDR_RESET_N` (1C7), in the CSV and in the schematic. No ball moves.
- **Updated 2026-10-26 (`blk.rp2354` capture):** the RP2354A side of the coprocessor lines is allocated (§3, Coprocessor): UART0 on GPIO0/GPIO1, `RP_IRQ` on GPIO2, a spare pad on GPIO3, the five I2S/DSD taps on GPIO4–GPIO8. No SoC ball moves; the notes of the eight rows name the RP2354A GPIO.
- **Updated 2026-10-28 (BOM v1.18 item 8, [ADR 0026](../adr/0026-vdd-cpu-buck-ti-tps62870z4.md)):** the I2C0 note names the TPS62870Z4 at 0x42 (AJ37); no ball moves.
- **Updated 2026-10-27 (maintainer decision, board area; BOM v1.18 item 7):** the NFC reader is withdrawn from the board in every model ([feature blocks](feature-blocks.md) #42). Its three balls become spare 1.8 V GPIO left unconnected (no-connect flag, no pad): 1N20 `NFC_IRQ` → `SPARE_0D5`, A37 `NFC_VEN` → `SPARE_2C0`, B38 `NFC_DWL_REQ` → `SPARE_2C6` (block `blk.debug`); expander P05 (`NFC_PWR_EN`) becomes a spare, no-connect, set as an output low by the driver; 0x28 on I2C2 is free. O10 closes by withdrawal. The NFC tag (`NFC_FD_N`, 1M19) is unchanged.
- **Machine-readable copy:** [`../../hardware/pinout/pinout-v1.csv`](../../hardware/pinout/pinout-v1.csv), all 565 balls (ball, pad, function, domain, voltage, net, block, reset_state, notes). The tables in §3 were generated from the same data as the CSV; the CSV is the reference for the schematic check, and a change edits both.
- **Inputs:** pin multiplexing v0; board [ADR 0006](../adr/0006-pin-plan-decisions.md); [BOM v1.8](bom-v1.md) and [power tree v0.2](power-tree-v0.md) (both committed in `00c5183`, reconciled in §9.1); [feature blocks](feature-blocks.md) (block IDs, gaps G1–G21); [PCB design constraints](pcb-design-constraints.md); Rockchip HDG 1.1 and HSPCB 1.0; t1 [faceplate interface](../../../product/docs/specs/faceplate-interface.md) and [RFC 0001](https://github.com/opendap-project/rfcs/blob/main/text/0001-faceplate-interface-v0-pinout.md); hats `standard/` [HAT interface v1](https://github.com/opendap-project/hats/blob/main/standard/docs/specs/interface-v1.md); [RFC 0010](https://github.com/opendap-project/rfcs/blob/main/text/0010-quality-levels.md) and [RFC 0011](https://github.com/opendap-project/rfcs/blob/main/text/0011-feature-blocks-and-variants.md).

## Sources

Every document is listed in the libs `parts/manifest.toml` (URL, revision, sha256) and read from the local cache; none is committed.

| Short | Document | Revision |
|---|---|---|
| DS | Rockchip *RK3566 Datasheet*: package pp. 21–22, pin list Table 2-1 pp. 23–30, power balls pp. 30–31, function IO and power domain §2.7 pp. 32–35, electrical pp. 51–53 | Rev 1.1, 2021-03-05 |
| HDG | Rockchip *RK3566 Hardware Design Guide* | V1.1.0, 2022-02-06 |
| IOD | Rockchip *RK3566 RK3568 IO Domain Configuration Developer Guide* (RK-SM-YF-905) | V1.0.2, 2021-06-02 |
| HSPCB | Rockchip *RK3568 High Speed PCB Design Guide* (RK-YH-YJ-6012) | V1.0.0, 2021-04-12 |
| RK809 | Rockchip *RK809 Datasheet* | Rev 1.01, 2018 |
| RP2350 | Raspberry Pi *RP2350 Datasheet* | build 2026-01-10 (libs parts manifest, RP2354A entry) |
| — | TI SCES898C (SN74AXC4T774), SCES875C (SN74AXC8T245), SCPS194F (TCA6416A), SCPS113O (PCA9306), SLUSE07B (BQ28Z610-R1); onsemi FUSB302B/D Rev. 5; Analog Devices MAX98357A; Goodix GT911 v09 | as cached |
| — | Murata *Type 2EL/2DL/2LL/2KL Unified Design Guide* E2B-54-1953 (Table 3) and *Type 2EL/2DL Hardware Application Note* E2B-09-1413 | Rev. 2.0, 2025-08-21; Rev. 9.0, 2026-05-21 |

The *RK3566_PinOut* document (with "usage of unused pins") and the *RK3566 IO Power Domain Checklist* that HDG p. 4 names were not found; what depends on them is open item O2.

## 0. Summary

1. **142 GPIO balls** (DS Table 2-1, counted: the v0 count of 142 holds; GPIO4_B7 is ball AC2), **130 assigned**, 8 spare, 4 reserved. Every assignment was checked against DS 1.1, not the RK3568 datasheet v0 used: ball, pad name, mux functions, power domain (DS §2.7 and the HDG function-domain tables), reset pull (pad suffix, HDG p. 31) and whether the ball sits in the 0.4 mm ring.
2. **IO-domain map (§1):** PMUIO0 1.8 V fixed, PMUIO1 3.3 V fixed, PMUIO2 1.8 V, VCCIO1 3.3 V (HAT), VCCIO2 1.8 V (eMMC, `FLASH_VOL_SEL` high), VCCIO3 1.8/3.3 V (microSD UHS-I), VCCIO4 1.8 V (radio), VCCIO5 3.3 V (faceplate, speaker, HAT GPIO), VCCIO6 1.8 V (audio), VCCIO7 3.3 V (HAT I2C, 3.3 V audio controls). Unchanged from v0, now confirmed on the RK3566.
3. **28 conflicts in v0** (§5). The ones that change hardware: the radio host-wake lines were on GPIO2, which cannot wake the SoC from Rockchip's standby (HDG pp. 17, 35, 53), and the coprocessor relayed wakes (BRD-014 context): every wake line now sits on a PMU ball and nothing relays through the RP2354A. Speaker, headphone-amplifier and SWD lines sat on FSPI balls the BootROM drives at boot, one with a pull-up that would enable the speaker amplifier at reset. The RP2354A BOOTSEL line would have put 3.3 V on a 1.8 V ball. The PCA9306 enable cannot be a push-pull GPIO. The faceplate interrupts were at 1.8 V against the faceplate interface's 3.3 V. Three eFuse current monitors do not fit the two free SARADC inputs. The fuel gauge has no alert pin.
4. **Feature-block gaps:** TPM reset and PIRQ, PN7160 IRQ, VEN and DWL_REQ, the NFC tag field-detect, the expander interrupt, `HAPTIC_EN` and `NFC_PWR_EN` all have balls or expander lines (§7), at the voltage of the device they drive (BOM v1.8 rails).
5. **Ring escape (§6):** of the 174 signal balls the T1 uses outside the LPDDR4X interface, 44 are inner-ring balls behind an outer ball and need a microvia. The DAC data and clock path never needs a ring microvia: SCLK_TX and LRCK_RX are core balls, LRCK_TX is on the outer ring row, SDO0, SDO2 and SCLK_RX are inner-ring balls behind a gap. The speaker bit clock and data, the faceplate PDM clock, one HAT capture line and the DAC interrupt are inner-ring balls behind an outer ball and need a microvia.
6. **Faceplate (§8):** a 51-contact order on the FH35C-51S in RFC 0001's group order: DSI pairs fenced by grounds at contacts 1–16, low-speed groups 17–38 with a ground before the PDM pair, supplies 40–46 with the backlight anode at 46 next to its return and a reserved contact, five reserved contacts 47–51.
7. **For the BOM and power-tree owner (§9):** 16 items, among them the per-domain rail table, a filtered VCCIO6 supply, `HAT3V3_EN` moving to the expander so HAT power survives suspend, an N-FET for BOOTSEL, the PCA9306 enable network, a VBUS divider for `USB_OTG0_VBUSDET`, the expander port map, and the RK809 codec pins to ground.

## 1. IO-domain voltage assignment

This table constrains every block. A domain's supply voltage and its software setting must match: a 1.8 V setting on a 3.3 V supply damages the pads over time, a 3.3 V setting on a 1.8 V supply makes them misbehave (HDG pp. 30–31; IOD p. 2). The SDK sets every configurable domain to 3.3 V until the device tree says otherwise (IOD p. 9), so a 1.8 V domain is safe before Linux configures it. PMUIO0 and PMUIO1 are fixed; VCCIO2 follows the `FLASH_VOL_SEL` strap, not software (HDG p. 31). Each supply ball takes at least one 100 nF capacitor and ±5 % ripple (HDG p. 32).

| Domain | GPIO | Supply balls | Voltage | Rail (T1 net) | Software setting (`pmu_io_domains`) | Serves | Why this voltage |
|---|---|---|---|---|---|---|---|
| PMUIO0 | GPIO0_D3–D6 (and XIN/XOUT24M) | PMUPLL_AVDD_1V8 (1N18) | 1.8 V fixed | vcca1v8_pmu | none (fixed) | TPM reset, NFC tag field detect, expander interrupt; GPIO0_D5 spare (2026-10-27, was the PN7160 IRQ) | Fixed by the SoC (HDG p. 32, Table 2-8); on in suspend and wake-capable (HDG pp. 17, 35). v0 left these four balls unused |
| PMUIO1 | GPIO0_A0–A7, nPOR | PMUIO1 (1P16) | 3.3 V fixed | vcc3v3_pmu | none (fixed) | PMIC control, reset, straps, SD detect, HAT port controller interrupt (2026-10-25; was HAT presence and interrupt), faceplate HID interrupt | Fixed by the SoC (DS p. 52: 2.97–3.63 V) |
| PMUIO2 | GPIO0_B0–D1 | PMUIO2 (1N15) | 1.8 V | vcca1v8_pmu | `pmuio2-supply` = 1.8 V | I2C0, I2C1, I2C2 (every board control part), RP2354A UART, debug UART, wake interrupts | CS43198 control port tolerates VL + 0.3 V only (BOM §4.2); every I2C device meets a 1.8 V pull-up (FUSB302B VIH 1.32 V, FUSB302B/D Rev. 5 p. 16); precedent Quartz64-B and Radxa ZERO 3 (v0 §1.3) |
| VCCIO1 | GPIO1_A0–B3 | VCCIO1 (1D13) | 3.3 V | vcc3v3_sys | `vccio1-supply` = 3.3 V | RP2354A power enable, spares (2026-10-25: the HAT extension controls, sidebands, `HAT_RST#` and HAT ID enable are freed, RFC 0014) | 3.3 V bank; no HAT line since RFC 0014 |
| VCCIO2 | GPIO1_B4–D4 | VCCIO2 (1C13) | 1.8 V | vcc_1v8 | none: `FLASH_VOL_SEL` high (HDG p. 19) | eMMC HS200, TPM PIRQ (HAT audio translator enable freed, RFC 0014) | eMMC 5.1 HS200 at 1.8 V VCCQ |
| VCCIO3 | GPIO1_D5–GPIO2_A2 | VCCIO3 (1F17) | 1.8 / 3.3 V | vccio_sd (RK809 LDO5) | `vccio3-supply` = vccio_sd, switched by the SD driver | microSD | UHS-I SDR104 needs the 3.3 → 1.8 V switch (BRD-051; HDG p. 52) |
| VCCIO4 | GPIO2_A3–C6 | VCCIO4 (1E16) | 1.8 V | vcc_1v8 | `vccio4-supply` = 1.8 V | Type 2EL SDIO 3.0 and Bluetooth UART, radio PDn and BT wake; GPIO2_C0 and GPIO2_C6 spare (2026-10-27, were the PN7160 VEN and DWL_REQ) | SDIO 3.0 needs 1.8 V (HDG p. 53); the module VIO and SD_VIO are on vcc_1v8 (BOM v1.8 item 1) |
| VCCIO5 | GPIO3_A1–C5 | VCCIO5 (1N5, 1N6) | 3.3 V | vcc3v3_sys | `vccio5-supply` = 3.3 V | Faceplate low-speed groups, speaker I2S, backlight PWM | Faceplate interface: 3.3 V for the low-speed groups |
| VCCIO6 | GPIO3_C6–GPIO4_C1 | VCCIO6 (1L4, 1L5) | 1.8 V | vccio6_1v8 (vcc_1v8 through a filter footprint, proposal B1) | `vccio6-supply` = 1.8 V | I2S1 to the DACs, DSD lines, PDM microphones, audio enables, DAC reset and interrupt, RP2354A SWD, RUN, BOOTSEL | CS43198 digital I/O at VL = 1.8 V; the DAC clock and data nets are never translated (ADR 0010) |
| VCCIO7 | GPIO4_C2–D1 | VCCIO7 (1N8) | 3.3 V | vcc3v3_sys | `vccio7-supply` = 3.3 V | master-clock select, headphone-rail enables, spares | NSC5083D ST needs VIH ≥ 2.17 V (BOM §4.3); the LT3045/LT3094 and TPS65131 enables are 3.3 V logic (power tree §5) |

Domain boundaries: DS §2.7 (pp. 32–35) and the HDG function-domain tables: UART (p. 61, Table 2-15), I2C (p. 63, Table 2-16), PWM (pp. 64–65, Table 2-17), SPI (p. 65, Table 2-18), I2S and PDM (pp. 69–72), SPDIF (p. 73, Table 2-24). GPIO4_D1 is VCCIO7 (SPI3_CS1_M1, HDG Table 2-18), which closes v0 risk 12.

**Wake.** In Rockchip's standby solution only PMUIO0, PMUIO1 and PMUIO2 balls can wake the SoC; GPIO1–GPIO4 lose their state and their interrupts unless VDD_LOGIC and the domain stay powered (HDG pp. 17, 35, 53). Every wake source of the T1 is therefore on a GPIO0 ball, and every output whose state must survive suspend is on a PMU ball or on the expander (VCCI on vcca1v8_pmu, BOM v1.8 line 93).

**Reset state.** The pad suffix gives the state after reset: `_u` pull-up, `_d` pull-down, `_z` high impedance; every ball is an input after reset except the boot-related ones (HDG p. 31). Internal pulls are 16–43 kΩ (DS p. 53, Table 3-3). Rules applied in §3: enables sit on `_d` balls; active-low lines that must idle high sit on `_u` balls or carry an external pull-up of 4.7 kΩ or less (2.2 kΩ where the receiver needs 0.7 × VCC), which wins against the 16 kΩ minimum internal pull-down until the pin controller disables it. PCB-P-18 still requires the external default resistor on every enable: an internal pull only exists while its bank is powered.

## 2. Method

1. Ball names and pad names from DS Table 2-1 (pp. 23–30), extracted to text and cross-checked against §2.7 (pp. 32–35) for every GPIO ball. Nine balls whose §2.7 row is overprinted by the domain label were checked in Table 2-1 by hand (1U1, 1E18, 1F19, 1P18, AJ37, AP12, AR10, B22, B27). Ball C1 (LPDDR4_A1_A) is wrapped in the text extraction and was read from the raw page.
2. Mux options: one option group per controller ("only one of them can be used at the same time … the same group of function pins can only be used in combination with the same suffix", HDG p. 31). This confirms v0's one-route-per-controller assumption.
3. Ring position from the ball name: rows A and AR and columns 1 and 38 are the outer ring, rows B and AP and columns 2 and 37 the inner ring (DS pp. 21–30; layout rules §3). An inner-ring ball is "behind" when the outer ball in front of it exists, and then needs a microvia; otherwise it escapes on L1 through the gap.
4. The schematic check compares each SoC symbol pin with the CSV row of the same ball: net, and for supply balls the rail.

## 3. Ball assignment by function block

Columns: ball; pad (the GPIO name with its reset suffix; the full mux list is in the CSV); chosen function; domain, voltage and rail; reset state and why; net; block (feature-block ID); ring escape class; notes. Dedicated balls (PHY, SARADC, clock, reset) follow the GPIO rows of their block. The 73 LPDDR4X balls, the 80 supply balls and the 188 ground balls are in the CSV only: LPDDR4X balls connect to the same-named DRAM balls in the Rockchip template order, which may not be swapped (HDG p. 22).

### SoC, reset, PMIC, buttons and debug

| Ball | Pad | Function | Domain | Reset state and why | Net | Block | Escape | Notes |
|---|---|---|---|---|---|---|---|---|
| 1R20 | GPIO0_A1_z | TSADC_SHUT_M0 | PMUIO1, 3.3 V fixed, vcc3v3_pmu | high-Z: no fight with the reset pull-up | `SOC_RESET_N` | `blk.soc` | core | Watchdog/thermal reset out to the nPOR and RK809 RESETB net (HDG p. 18, Fig. 2-2) |
| 1P19 | GPIO0_A2_d | PMIC_SLEEP | PMUIO1, 3.3 V fixed, vcc3v3_pmu | pull-down: PMIC not in sleep while the SoC resets | `PMIC_SLEEP` | `blk.pmic` | core | RK809 SLEEP; RK809 pin rating 6.5 V (RK809 DS p. 16) |
| 1R19 | GPIO0_A3_u | GPIO in | PMUIO1, 3.3 V fixed, vcc3v3_pmu | pull-up: matches the open-drain idle level | `PMIC_INT_N` | `blk.pmic` | core | RK809 INT, open drain (RK809 DS p. 14); wake (RTC, power key) |
| AF38 | GPIO0_A7_u | FLASH_VOL_SEL | PMUIO1, 3.3 V fixed, vcc3v3_pmu | pull-up; external pull-up to vcc3v3_pmu holds it high during reset | `FLASH_VOL_SEL` | `blk.soc` | ring, outer | Boot strap: high = VCCIO2 at 1.8 V (HDG p. 19, p. 20 Table 2-3). Nothing else on this net |
| 1T20 | GPIO0_B0_u | CLK32K_IN | PMUIO2, 1.8 V, vcca1v8_pmu | pull-up | `CLK32K_PMIC` | `blk.pmic` | core | RK809 CLK32K is open drain (RK809 DS p. 15): pull-up to vcca1v8_pmu; level 0.65 × VDD to VDD + 0.3 (HDG p. 17, Table 2-2) |
| AJ37 | GPIO0_B1_u | I2C0_SCL | PMUIO2, 1.8 V, vcca1v8_pmu | pull-up | `I2C0_SCL` | `blk.pmic` | ring, inner (microvia) | RK809 0x20, TPS62870Z4 0x42 (ADR 0026; TPS62869 0x42 BOM v1.12–v1.17, ADR 0021; RK860-0 0x40 until BOM v1.11). Pull-ups to vcca1v8_pmu |
| AK38 | GPIO0_B2_u | I2C0_SDA | PMUIO2, 1.8 V, vcca1v8_pmu | pull-up | `I2C0_SDA` | `blk.pmic` | ring, outer | As I2C0_SCL |
| AJ38 | GPIO0_A6_d | GPIO in | PMUIO1, 3.3 V fixed, vcc3v3_pmu | pull-down until pinctrl: reads the cover closed, as with the block unfitted | `COVER_DET_N` | `blk.cover-detect` | ring, outer | Back-cover detect (BOM line 143, ADR 0020 item 7; G22, 2026-10-26): low with the cover closed, 100 kΩ pull-up to vcc3v3_pmu; wake (RFC 0014: was `HAT_INT_N`, then `SPARE_0A6`) |
| AM37 | GPIO0_C2_d | GPIO in | PMUIO2, 1.8 V, vcca1v8_pmu | pull-down until pinctrl; external pull-up to vcca1v8_pmu wins | `ACTION_BTN_N` | `blk.buttons` | ring, inner (microvia) | Action button (BRD-036); wake |
| 1V19 | GPIO0_D0_u | UART2_RX_M0 | PMUIO2, 1.8 V, vcca1v8_pmu | pull-up: idle UART level | `DBG_UART_RX` | `blk.debug` | core | BootROM/TPL/U-Boot console (HDG p. 61); 1.8 V pads (BRD-047) |
| 1U18 | GPIO0_D1_u | UART2_TX_M0 | PMUIO2, 1.8 V, vcca1v8_pmu | pull-up | `DBG_UART_TX` | `blk.debug` | core | As DBG_UART_RX |
| 1D17 | SARADC_VIN0 | SARADC_VIN0 | SARADC, 0–1.8 V | - | `SARADC_VOLUP` | `blk.buttons` | core | Vol+ and recovery key: 10 kΩ to vcca_1v8, 1 nF at the pin (HDG p. 60, Table 2-14); low at boot = loader Rockusb (HDG p. 59, BRD-017) |
| AG38 | nPOR_u | nPOR | PMUIO1, 3.3 V | internal pull-up | `SOC_RESET_N` | `blk.soc` | ring, outer | RK809 RESETB, 100 nF at the pin, pull-up to the PMUIO1 rail, ground guard (HDG pp. 17-18); internal pull-up |
| 1C17 | SARADC_VIN1 | SARADC_VIN1 | SARADC, 0–1.8 V | - | `VOLDN_N` | `blk.buttons` | core | Vol- (BOM line 77), also the MaskROM gate input (blk.maskrom); 1 nF at the pin |
| AD37 | XIN24M | XIN24M | PMUIO0, 1.8 V | - | `XIN24M` | `blk.soc` | ring, inner (microvia) | 24 MHz crystal, 2 × 18 pF matched to CL, 1 MΩ across (HDG pp. 16-17) |
| AD38 | XOUT24M | XOUT24M | PMUIO0, 1.8 V | - | `XOUT24M` | `blk.soc` | ring, outer | 22 Ω series, keep (HDG p. 16) |

### Storage

| Ball | Pad | Function | Domain | Reset state and why | Net | Block | Escape | Notes |
|---|---|---|---|---|---|---|---|---|
| AF37 | GPIO0_A4_u | SDMMC0_DET | PMUIO1, 3.3 V fixed, vcc3v3_pmu | pull-up = no card: SDMMC0 balls carry JTAG/UART2 M1 at reset (HDG p. 20, Table 2-3) | `SD_DET_N` | `blk.microsd` | ring, inner (microvia) | Boot strap. Socket switch pulls low with a card; 100 Ω series (HDG p. 52); hot-plug wake |
| A32 | GPIO1_B4_u | EMMC_D0 | VCCIO2, 1.8 V, vcc_1v8 | pull-up | `EMMC_D0` | `blk.emmc` | ring, outer | Also the MaskROM pull through 1 kΩ (blk.maskrom, BOM line 35); test point (HDG p. 27); 10 kΩ pull-up (HDG p. 26) |
| B27 | GPIO1_B5_u | EMMC_D1 | VCCIO2, 1.8 V, vcc_1v8 | pull-up | `EMMC_D1` | `blk.emmc` | ring, inner (microvia) |  |
| B32 | GPIO1_B6_u | EMMC_D2 | VCCIO2, 1.8 V, vcc_1v8 | pull-up | `EMMC_D2` | `blk.emmc` | ring, inner (microvia) |  |
| B29 | GPIO1_B7_u | EMMC_D3 | VCCIO2, 1.8 V, vcc_1v8 | pull-up | `EMMC_D3` | `blk.emmc` | ring, inner (microvia) |  |
| B33 | GPIO1_C0_u | EMMC_D4 | VCCIO2, 1.8 V, vcc_1v8 | pull-up | `EMMC_D4` | `blk.emmc` | ring, inner (microvia) |  |
| A30 | GPIO1_C1_u | EMMC_D5 | VCCIO2, 1.8 V, vcc_1v8 | pull-up | `EMMC_D5` | `blk.emmc` | ring, outer |  |
| B30 | GPIO1_C2_u | EMMC_D6 | VCCIO2, 1.8 V, vcc_1v8 | pull-up | `EMMC_D6` | `blk.emmc` | ring, inner (microvia) |  |
| A33 | GPIO1_C3_u | EMMC_D7 | VCCIO2, 1.8 V, vcc_1v8 | pull-up | `EMMC_D7` | `blk.emmc` | ring, outer |  |
| A27 | GPIO1_C4_u | EMMC_CMD | VCCIO2, 1.8 V, vcc_1v8 | pull-up | `EMMC_CMD` | `blk.emmc` | ring, outer | 10 kΩ pull-up (HDG p. 26) |
| A29 | GPIO1_C5_d | EMMC_CLKOUT | VCCIO2, 1.8 V, vcc_1v8 | pull-down | `EMMC_CLK` | `blk.emmc` | ring, outer | 22 Ω series at the SoC (HDG p. 26); MaskROM test point (HDG p. 27) |
| 1A16 | GPIO1_C6_d | EMMC_DATA_STROBE | VCCIO2, 1.8 V, vcc_1v8 | pull-down | `EMMC_DS` | `blk.emmc` | core | Reserve a pull-down (HDG p. 26) |
| 1B16 | GPIO1_C7_d | EMMC_RSTn | VCCIO2, 1.8 V, vcc_1v8 | pull-down | `EMMC_RST_N` | `blk.emmc` | core | Also FSPI_D2: the BootROM FSPI probe may toggle it |
| 1E20 | GPIO1_D5_u | SDMMC0_D0 | VCCIO3, 1.8/3.3 V, vccio_sd | pull-up | `SD_D0` | `blk.microsd` | core | 22 Ω series (HDG p. 52). UART2_TX_M1 while SD_DET_N is high |
| 1F19 | GPIO1_D6_u | SDMMC0_D1 | VCCIO3, 1.8/3.3 V, vccio_sd | pull-up | `SD_D1` | `blk.microsd` | core | 22 Ω series. UART2_RX_M1 while SD_DET_N is high |
| 1D20 | GPIO1_D7_u | SDMMC0_D2 | VCCIO3, 1.8/3.3 V, vccio_sd | pull-up | `SD_D2` | `blk.microsd` | core | 22 Ω series. ARM_JTAG_TCK while SD_DET_N is high |
| 1F18 | GPIO2_A0_u | SDMMC0_D3 | VCCIO3, 1.8/3.3 V, vccio_sd | pull-up | `SD_D3` | `blk.microsd` | core | 22 Ω series. ARM_JTAG_TMS while SD_DET_N is high |
| 1E19 | GPIO2_A1_u | SDMMC0_CMD | VCCIO3, 1.8/3.3 V, vccio_sd | pull-up | `SD_CMD` | `blk.microsd` | core | 22 Ω series |
| G38 | GPIO2_A2_d | SDMMC0_CLK | VCCIO3, 1.8/3.3 V, vccio_sd | pull-down | `SD_CLK` | `blk.microsd` | ring, outer | 22 Ω series near the SoC (HDG p. 52) |

### Power path and expander

| Ball | Pad | Function | Domain | Reset state and why | Net | Block | Escape | Notes |
|---|---|---|---|---|---|---|---|---|
| AK37 | GPIO0_B3_u | I2C1_SCL | PMUIO2, 1.8 V, vcca1v8_pmu | pull-up | `I2C1_SCL` | `blk.charger` | ring, inner (microvia) | FUSB302B 0x22 (main USB-C), FUSB302B01MPX 0x23 (HAT port, 2026-10-25; FUSB302B/D Rev. 5 p. 18 Table 15), BQ28Z610-R1 0x55, BQ25798 0x6B, INA236 0x40-0x43. FUSB302B VIH 1.32 V (FUSB302B/D Rev. 5 p. 16) |
| AM38 | GPIO0_B4_u | I2C1_SDA | PMUIO2, 1.8 V, vcca1v8_pmu | pull-up | `I2C1_SDA` | `blk.charger` | ring, outer | As I2C1_SCL |
| 1U20 | GPIO0_B5_u | I2C2_SCL_M0 | PMUIO2, 1.8 V, vcca1v8_pmu | pull-up | `I2C2_SCL` | `blk.gpio-expander` | core | Board control bus: TCA6416A 0x21, TPM 0x2E, CS43198 0x30/0x31 (behind the G2 isolator), LP5521 0x32, AT24C02D 0x50, NTAG 0x55, DRV2605L 0x5A, LSM6DSV16X 0x6A. Pull-ups to vcca1v8_pmu (G16) |
| 1R16 | GPIO0_B6_u | I2C2_SDA_M0 | PMUIO2, 1.8 V, vcca1v8_pmu | pull-up | `I2C2_SDA` | `blk.gpio-expander` | core | As I2C2_SCL |
| AN38 | GPIO0_C3_d | GPIO in | PMUIO2, 1.8 V, vcca1v8_pmu | pull-down until pinctrl; external pull-up wins | `CHG_INT_N` | `blk.charger` | ring, outer | BQ25798 INT, open drain; wake |
| AN37 | GPIO0_C4_d | GPIO in | PMUIO2, 1.8 V, vcca1v8_pmu | pull-down until pinctrl; external pull-up wins | `USBC_INT_N` | `blk.usb-c` | ring, inner (microvia) | FUSB302B INT_N, open drain; wake |
| 1P20 | GPIO0_D6_d | GPIO in | PMUIO0, 1.8 V fixed, vcca1v8_pmu | pull-down until pinctrl; 4.7 kΩ pull-up to vcca1v8_pmu wins | `EXP_INT_N` | `blk.gpio-expander` | core | TCA6416A INT, open drain (SCPS194F p. 17); wake (jack, faceplate detect, eFuse faults). Replaces the wired-OR with RP_IRQ (C3) |
| 1A19 | SARADC_VIN3 | SARADC_VIN3 | SARADC, 0–1.8 V | - | `EFUSE_VBUS_IMON` | `blk.usb-vbus-out` | core | eFuse #C IMON (USB-C VBUS source, BOM line 44); 1 nF; range set by RIMON ≤ 1.8 V. 2026-10-25 (RFC 0014): was eFuse #B IMON, removed; closes C10 |
| 1B18 | SARADC_VIN2 | SARADC_VIN2 | SARADC, 0–1.8 V | - | `EFUSE_HAT5V_IMON` | `blk.hat-5v` | core | eFuse #A IMON (BOM line 44); 1 nF; range set by RIMON ≤ 1.8 V |
| T37 | USB_OTG0_ID | USB_OTG0_ID | USB PHY, - | - | `NC` | `blk.usb-c` | ring, inner (microvia) | Micro-B only (HDG p. 59); role comes from the FUSB302B. Internal 1.8 V pull-up |
| R38 | USB_OTG0_DM | USB_OTG0_DM | USB PHY, - | - | `USBC_DM` | `blk.usb-c` | ring, outer | As USBC_DP |
| R37 | USB_OTG0_DP | USB_OTG0_DP | USB PHY, - | - | `USBC_DP` | `blk.usb-c` | ring, inner (microvia) | Main USB-C, 2.2 Ω series (HDG p. 59); MaskROM download port (HDG p. 18) |
| T38 | USB_OTG0_VBUSDET | USB_OTG0_VBUSDET | USB PHY, - | - | `USBC_VBUSDET` | `blk.usb-c` | ring, outer | VBUS through a resistor divider (HDG p. 59, Table 2-13); divider not in the BOM (B8) |

### Audio

| Ball | Pad | Function | Domain | Reset state and why | Net | Block | Escape | Notes |
|---|---|---|---|---|---|---|---|---|
| AP10 | GPIO3_A3_d | I2S3_SCLK_M0 | VCCIO5, 3.3 V, vcc3v3_sys | pull-down | `SPK_BCLK` | `blk.speaker` | ring, inner (microvia) | 22 Ω series at the SoC (HDG p. 71) |
| AR9 | GPIO3_A4_d | I2S3_LRCK_M0 | VCCIO5, 3.3 V, vcc3v3_sys | pull-down | `SPK_LRCK` | `blk.speaker` | ring, outer | 22 Ω series at the SoC |
| AP9 | GPIO3_A5_d | I2S3_SDO_M0 | VCCIO5, 3.3 V, vcc3v3_sys | pull-down | `SPK_SDIN` | `blk.speaker` | ring, inner (microvia) | Direct |
| 1U4 | GPIO3_A6_d | GPIO out | VCCIO5, 3.3 V, vcc3v3_sys | pull-down: amplifier in shutdown | `SPK_SD_MODE` | `blk.speaker` | core | MAX98357A SD_MODE through its select resistor (MAX98357A DS Figure 5, Table 6); 100 kΩ internal pull-down in the amplifier. I2S3_SDI_M0 not needed. Was 1_D1 (1.8 V, pull-up) in v0 (C5, C14) |
| 1U1 | GPIO3_C7_d | I2S1_SCLK_TX_M1 | VCCIO6, 1.8 V, vccio6_1v8 | pull-down | `I2S_BCLK` | `blk.audio` | core | Input: bit clock from the CS43198 L (clock master). 22 Ω at the source, the DAC (HDG p. 70). Test pad (BRD-040), RP2354A tap (BRD-041), HAT I2S_BCLK buffer tap RP2354A GPIO4 (PIO input, tap; §3 Coprocessor allocation) |
| AP1 | GPIO3_D0_d | I2S1_LRCK_TX_M1 | VCCIO6, 1.8 V, vccio6_1v8 | pull-down | `I2S_LRCK` | `blk.audio` | ring, outer | Input: frame clock from the CS43198 L. Test pad, taps as I2S_BCLK RP2354A GPIO5 (PIO input, tap; §3 Coprocessor allocation) |
| AN2 | GPIO3_D1_d | I2S1_SDO0_M1 | VCCIO6, 1.8 V, vccio6_1v8 | pull-down: parked low into unpowered DACs | `I2S_SDO0` | `blk.audio` | ring, inner (gap) | PCM to both CS43198 (dual mono). Test pad, RP2354A tap RP2354A GPIO6 (PIO input, tap; §3 Coprocessor allocation) |
| AL2 | GPIO3_D6_d | PDM_CLK0_M1 | VCCIO6, 1.8 V, vccio6_1v8 | pull-down: parked low while MIC_1V8 is off (G10) | `PDM_CLK0` | `blk.mic-main` | ring, inner (microvia) | Faceplate contact 34; 22 Ω series (HDG p. 72) |
| AL1 | GPIO3_D7_d | PDM_SDI0_M1 | VCCIO6, 1.8 V, vccio6_1v8 | pull-down | `PDM_DATA0` | `blk.mic-main` | ring, outer | Faceplate contact 35 |
| AK2 | GPIO4_A0_d | PDM_CLK1_M1 | VCCIO6, 1.8 V, vccio6_1v8 | pull-down: parked low while MIC_1V8 is off | `PDM_CLK1` | `blk.mic-ambient` | ring, inner (gap) | Ambient microphone; 22 Ω series |
| 1P2 | GPIO4_A1_d | PDM_SDI1_M1 | VCCIO6, 1.8 V, vccio6_1v8 | pull-down: defined level with the microphone unfitted | `PDM_DATA1` | `blk.mic-ambient` | core |  |
| 1R1 | GPIO4_A2_d | GPIO out | VCCIO6, 1.8 V, vccio6_1v8 | pull-down: both DACs in reset | `DAC_RST_N` | `blk.audio` | core | Shared CS43198 RESET |
| AJ2 | GPIO4_A3_d | GPIO in | VCCIO6, 1.8 V, vccio6_1v8 | pull-down until pinctrl; pull-up on DAC_DIG_1V8 (G2) | `DAC_INT_N` | `blk.audio` | ring, inner (microvia) | Wired-OR CS43198 INT; I2C2 reaches the DACs through the SN74LVC2G66 controlled by DAC_DIG_1V8 (BOM v1.8 line 133), no SoC enable needed |
| AH2 | GPIO4_A6_d | I2S1_SCLK_RX_M1 | VCCIO6, 1.8 V, vccio6_1v8 | pull-down | `I2S_BCLK_RX` | `blk.audio` | ring, inner (gap) | DNP 0 Ω to I2S_BCLK: fallback if RX cannot take the TX clocks internally (pin plan v0 4.3) |
| 1N1 | GPIO4_A7_d | I2S1_LRCK_RX_M1 | VCCIO6, 1.8 V, vccio6_1v8 | pull-down | `I2S_LRCK_RX` | `blk.audio` | core | DNP 0 Ω to I2S_LRCK, as above |
| 1L2 | GPIO4_B0_d | I2S1_SDO1_M1 | VCCIO6, 1.8 V, vccio6_1v8 | pull-down: parked low | `DSD_L` | `blk.audio` | core | Reserved for native DSD to DAC L DSDA (blackbird-os ADR 0006). Test pad, RP2354A tap RP2354A GPIO7 (PIO input, tap; §3 Coprocessor allocation) |
| AG2 | GPIO4_B1_d | I2S1_SDO2_M1 | VCCIO6, 1.8 V, vccio6_1v8 | pull-down: parked low | `DSD_R` | `blk.audio` | ring, inner (gap) | Reserved for native DSD to DAC R DSDA RP2354A GPIO8 (PIO input, tap; §3 Coprocessor allocation) |
| AF2 | GPIO4_B2_d | GPIO out | VCCIO6, 1.8 V, vccio6_1v8 | pull-down: off | `DAC_DIG_EN` | `blk.audio-supply` | ring, inner (microvia) | TPS22916C ON (DAC_DIG_1V8) |
| AE2 | GPIO4_B3_d | GPIO out | VCCIO6, 1.8 V, vccio6_1v8 | pull-down: off | `DAC_VP_EN` | `blk.audio-supply` | ring, inner (gap) | TPS22916C ON (DAC_VP) |
| AF1 | GPIO4_B4_d | GPIO out | VCCIO6, 1.8 V, vccio6_1v8 | pull-down: off | `AUDIO_LN_EN` | `blk.audio-supply` | ring, outer | TPS62840 and TPS7A2018 x2 EN directly; TPS7A2031 EN through the SN74LVC1G57 AND with DAC_DIG_1V8 (BOM v1.8 line 135, G3). Gate VCC on vcca1v8_pmu, VIH 0.65 × VCC: a 1.8 V ball drives it |
| 1L1 | GPIO4_B6_d | GPIO out | VCCIO6, 1.8 V, vccio6_1v8 | pull-down: off | `HPA_SE_EN` | `blk.hpa-se` | core | OPA1622 EN, 3.5 mm group (was on the expander in v0) |
| AC2 | GPIO4_B7_d | GPIO out | VCCIO6, 1.8 V, vccio6_1v8 | pull-down: off | `HPA_BAL_EN` | `blk.hpa-bal` | ring, inner (gap) | OPA1622 EN, 4.4 mm group (was 1_D0, an FSPI ball, in v0: C5) |
| AB2 | GPIO4_C0_d | GPIO out | VCCIO6, 1.8 V, vccio6_1v8 | pull-down: off, privacy LED off | `MIC_EN` | `blk.mic-main` | ring, inner (microvia) | TPS22945 ON (MIC_1V8; TPS22919 until 2026-10-24, BOM v1.11 line 146); settles the SoC-or-expander question of the block record |
| 1U7 | GPIO4_C2_d | GPIO out | VCCIO7, 3.3 V, vcc3v3_sys | pull-down: oscillator tri-stated | `MCLK441_EN` | `blk.mclk` | core | NSC5083D ST, VIH ≥ 0.7 × 3.1 V = 2.17 V needs a 3.3 V ball (BOM 4.3). Series resistor footprint; ST pin rating against 3.3 V with MCLK_3V1 at 3.1 V or off is UNVERIFIED (G3) |
| AP12 | GPIO4_C3_d | GPIO out | VCCIO7, 3.3 V, vcc3v3_sys | pull-down: oscillator tri-stated | `MCLK48_EN` | `blk.mclk` | ring, inner (microvia) | As MCLK441_EN; never both high |
| 1U6 | GPIO4_C5_d | GPIO out | VCCIO7, 3.3 V, vcc3v3_sys | pull-down: off | `HPA_RAIL_EN` | `blk.hpa-rails` | core | TPS65131 ENP and the LMR33630C EN level shifter (3.3 V logic, power tree 5) |
| 1T6 | GPIO4_C6_d | GPIO out | VCCIO7, 3.3 V, vcc3v3_sys | pull-down: off | `HPA_LDO_EN` | `blk.hpa-rails` | core | LT3045 x2, LT3094 x2 EN/UV, ≥ 10 ms after HPA_RAIL_EN |

### Radio, NFC, sensors, key holder

| Ball | Pad | Function | Domain | Reset state and why | Net | Block | Escape | Notes |
|---|---|---|---|---|---|---|---|---|
| 1R17 | GPIO0_B7_d | GPIO in | PMUIO2, 1.8 V, vcca1v8_pmu | pull-down: no wake while the module is off | `WL_WAKE_OUT` | `blk.radio` | core | Type 2EL WL_WAKE_OUT (pin 73). Moved from 2_C0 (VCCIO4) to a PMU ball (C2, HDG p. 53). Wakes from deep standby only if the radio stays powered in suspend, which BOM v1.8 does not do (O9) |
| 1U19 | GPIO0_C5_d | GPIO in | PMUIO2, 1.8 V, vcca1v8_pmu | pull-down: no wake with the IMU unfitted | `IMU_INT1` | `blk.imu` | core | LSM6DSV16X INT1, wake on motion (BRD-032); IMU on vcca1v8_pmu (G1) |
| 1T18 | GPIO0_C6_d | GPIO in | PMUIO2, 1.8 V, vcca1v8_pmu | pull-down: no wake while the module is off | `BT_WAKE_OUT` | `blk.radio` | core | Type 2EL BT15.4_WAKE_OUT (pin 76). Moved from 2_C1 (VCCIO4) to a PMU ball (C2, HDG p. 53); same suspend condition as WL_WAKE_OUT (O9) |
| 1N19 | GPIO0_D3_d | GPIO out | PMUIO0, 1.8 V fixed, vcca1v8_pmu | pull-down until pinctrl; 2.2 kΩ pull-up to vcca1v8_pmu wins (≥ 1.58 V against the 16 kΩ minimum internal pull, DS p. 53): TPM out of reset | `TPM_RST_N` | `blk.tpm` | core | SLB9673 reset (G5). TPM on vcca1v8_pmu (BOM v1.8 line 122), so its reset sits in a domain that stays on in suspend and holds inactive |
| 1M19 | GPIO0_D4_d | GPIO in | PMUIO0, 1.8 V fixed, vcca1v8_pmu | pull-down until pinctrl; 4.7 kΩ pull-up to vcca1v8_pmu wins | `NFC_FD_N` | `blk.nfc-tag` | core | NTAG I2C plus field detect, open drain; wake on tap (G6) |
| 1N20 | GPIO0_D5_d | GPIO (spare) | PMUIO0, 1.8 V fixed, vcca1v8_pmu | pull-down | `SPARE_0D5` | `blk.debug` | core | Spare 1.8 V always-on GPIO, left unconnected (no-connect flag). Maintainer decision 2026-10-27, the NFC reader removed: was `NFC_IRQ` |
| 1A18 | GPIO1_D2_u | GPIO in | VCCIO2, 1.8 V, vcc_1v8 | pull-up: idle level of an active-low IRQ | `TPM_PIRQ_N` | `blk.tpm` | core | SLB9673 PIRQ, open drain (G5). Board pull-up on vcc_1v8 (the VCCIO2 rail), never on vcca1v8_pmu: in suspend the line sits at 0 V with no current. FSPI_D1 is an input during an x1 probe |
| 1C19 | GPIO2_A3_u | SDMMC1_D0 | VCCIO4, 1.8 V, vcc_1v8 | pull-up | `WL_SD_D0` | `blk.radio` | core | SDIO 3.0 (HDG p. 54) |
| 1E18 | GPIO2_A4_u | SDMMC1_D1 | VCCIO4, 1.8 V, vcc_1v8 | pull-up | `WL_SD_D1` | `blk.radio` | core |  |
| 1D18 | GPIO2_A5_u | SDMMC1_D2 | VCCIO4, 1.8 V, vcc_1v8 | pull-up | `WL_SD_D2` | `blk.radio` | core |  |
| 1A20 | GPIO2_A6_u | SDMMC1_D3 | VCCIO4, 1.8 V, vcc_1v8 | pull-up | `WL_SD_D3` | `blk.radio` | core |  |
| B35 | GPIO2_A7_u | SDMMC1_CMD | VCCIO4, 1.8 V, vcc_1v8 | pull-up | `WL_SD_CMD` | `blk.radio` | ring, inner (microvia) |  |
| B37 | GPIO2_B0_d | SDMMC1_CLK | VCCIO4, 1.8 V, vcc_1v8 | pull-down | `WL_SD_CLK` | `blk.radio` | ring, inner (microvia) | 22 Ω series near the SoC, ground guard (HDG p. 54) |
| 1C20 | GPIO2_B3_u | UART1_RX_M0 | VCCIO4, 1.8 V, vcc_1v8 | pull-up | `BT_UART_TXD` | `blk.radio` | core | From module UART_TX (pin 49) |
| F38 | GPIO2_B4_u | UART1_TX_M0 | VCCIO4, 1.8 V, vcc_1v8 | pull-up | `BT_UART_RXD` | `blk.radio` | ring, outer | To module UART_RX (pin 51) |
| F37 | GPIO2_B5_u | UART1_RTSn_M0 | VCCIO4, 1.8 V, vcc_1v8 | pull-up | `BT_UART_CTS` | `blk.radio` | ring, inner (microvia) | To module UART_CTS (pin 50) |
| G37 | GPIO2_B6_u | UART1_CTSn_M0 | VCCIO4, 1.8 V, vcc_1v8 | pull-up | `BT_UART_RTS` | `blk.radio` | ring, inner (microvia) | From module UART_RTS (pin 52) |
| D38 | GPIO2_B7_d | GPIO out | VCCIO4, 1.8 V, vcc_1v8 | pull-down: module held in power-down until Linux | `SPARE_2B7` (was `WL_PDN`) | `blk.radio` | ring, outer | Type 2EL PDn (pin 10). Same rail as the module VIO (vcc_1v8, BOM v1.8 item 1), so it never drives an unpowered module |
| A37 | GPIO2_C0_d | GPIO (spare) | VCCIO4, 1.8 V, vcc_1v8 | pull-down | `SPARE_2C0` | `blk.debug` | ring, outer | Spare 1.8 V GPIO, left unconnected (no-connect flag). Maintainer decision 2026-10-27, the NFC reader removed: was `NFC_VEN` |
| D37 | GPIO2_C5_d | GPIO out | VCCIO4, 1.8 V, vcc_1v8 | pull-down | `BT_WAKE_IN` | `blk.radio` | ring, inner (microvia) | Module BT15.4_WAKE_IN (pin 75), host to module. Was 2_C4 in v0 |
| B38 | GPIO2_C6_d | GPIO (spare) | VCCIO4, 1.8 V, vcc_1v8 | pull-down | `SPARE_2C6` | `blk.debug` | ring, outer | Spare 1.8 V GPIO, left unconnected (no-connect flag). Maintainer decision 2026-10-27, the NFC reader removed: was `NFC_DWL_REQ`; CLK32K_OUT1 not needed (the radio module has no 32.768 kHz input, C21) |

### Coprocessor

| Ball | Pad | Function | Domain | Reset state and why | Net | Block | Escape | Notes |
|---|---|---|---|---|---|---|---|---|
| 1T19 | GPIO0_C0_d | UART0_RX | PMUIO2, 1.8 V, vcca1v8_pmu | pull-down: no current into an unpowered RP2354A | `RP_UART_TX` | `blk.rp2354` | core | From an RP2354A FT GPIO (GPIO0-25): FT pads accept 3.63 V with IOVDD = 0 V (BOM line 134), so the always-on 1.8 V line stays inside the rating (G4) RP2354A GPIO0 (UART0 TX; §3 Coprocessor allocation) |
| 1R18 | GPIO0_C1_d | UART0_TX | PMUIO2, 1.8 V, vcca1v8_pmu | pull-down | `RP_UART_RX` | `blk.rp2354` | core | To an RP2354A FT GPIO (GPIO0-25); park low while RP_IOVDD_1V8 is off (G4) RP2354A GPIO1 (UART0 RX; §3 Coprocessor allocation) |
| 1V20 | GPIO0_C7_d | GPIO in | PMUIO2, 1.8 V, vcca1v8_pmu | pull-down; keep a board pull-down, never a pull-up (G4) | `RP_IRQ` | `blk.rp2354` | core | RP2354A interrupt and wake, active high, push-pull from an RP2354A FT GPIO RP2354A GPIO2 (SIO output; §3 Coprocessor allocation) |
| A23 | GPIO1_A2_d | GPIO out | VCCIO1, 3.3 V, vcc3v3_sys | pull-down: RP2354A off at reset (BRD-019) | `RP_PWR_EN` | `blk.rp2354` | ring, outer | Both TPS22916C ON pins (ON rated independently of VIN, BOM line 50). Default on or off is power tree open question 6; a board pull-up reverses it. RP rails are off in suspend anyway (RP_IOVDD_1V8 from vcc_1v8) |
| 1T2 | GPIO3_C6_d | GPIO open drain | VCCIO6, 1.8 V, vccio6_1v8 | pull-down: FET off, RP2354A boots normally | `RP_BOOTSEL_DRV` | `blk.rp2354` | core | Gate of an N-FET that pulls RP2354A QSPI_SS low; QSPI_SS is on RP_3V3 (C6). I2S1_MCLK_M1 not needed (the DAC is clock master) |
| 1N2 | GPIO4_A4_d | GPIO out | VCCIO6, 1.8 V, vccio6_1v8 | pull-down: parked low while the RP2354A is off | `RP_SWCLK` | `blk.rp2354` | core | Moved off the FSPI balls (C5). Also SWD pads (BOM line 89) |
| AJ1 | GPIO4_A5_d | GPIO in/out | VCCIO6, 1.8 V, vccio6_1v8 | pull-down: parked low while the RP2354A is off | `RP_SWDIO` | `blk.rp2354` | ring, outer | Moved off the FSPI balls (C5) |
| AB1 | GPIO4_C1_d | GPIO open drain | VCCIO6, 1.8 V, vccio6_1v8 | pull-down until pinctrl; 4.7 kΩ pull-up to RP_IOVDD_1V8 wins (≥ 1.39 V) | `RP_RUN` | `blk.rp2354` | ring, outer | RP2354A RUN, IOVDD domain (RP2350 DS p. 17). SoC pulls low to reset |
| V1 | USB_HOST2_DM | USB_HOST2_DM | USB PHY (usb2phy1 otg), - | - | `RP_USB_DM` | `blk.rp2354` | ring, outer | 2.2 Ω series |
| V2 | USB_HOST2_DP | USB_HOST2_DP | USB PHY (usb2phy1 otg), - | - | `RP_USB_DP` | `blk.rp2354` | ring, inner (microvia) | EHCI/OHCI host 0 to the RP2354A (topology report 3); 2.2 Ω series |

#### RP2354A GPIO allocation (2026-10-26)

Accepted (2026-10-26) for `blk.rp2354`. Basis: BOM v1 lines 12, 89 and 134, the feature-block record 46 and G4, power tree §4.12 and the RP2350 data sheet (Release 8). Every line the SoC side reaches lands on an FT pad (GPIO0–25), which accepts 3.63 V with IOVDD at 0 V (G4), and GPIO0–15 come out of reset pulled down (RP2350 datasheet).

| RP2354A pin | GPIO | Net | Function | Why |
|---|---|---|---|---|
| 2 | GPIO0 | `RP_UART_TX` | UART0 TX (F2) | To the SoC's UART0_RX (1T19); UART0's lowest pair (DS Table 3, §1.2.3) |
| 3 | GPIO1 | `RP_UART_RX` | UART0 RX (F2) | From the SoC's UART0_TX (1R18) |
| 4 | GPIO2 | `RP_IRQ` | SIO output, push-pull, active high | To 1V20 (wake); the reset pull-down and the board pull-down keep it low while the RP2354A is off or in reset |
| 5 | GPIO3 | `RP_SPARE` | test pad | The spare coprocessor GPIO on a pad (PCB-T-09) |
| 7, 8 | GPIO4, GPIO5 | `RP_TAP_BCLK`, `RP_TAP_LRCK` | PIO inputs | `I2S_BCLK`, `I2S_LRCK` through the tap branch's 0 Ω positions (BOM line 134) |
| 9, 10, 12 | GPIO6–GPIO8 | `RP_TAP_SDO0`, `RP_TAP_DSD_L`, `RP_TAP_DSD_R` | PIO inputs | `I2S_SDO0`, `DSD_L` (SDO1), `DSD_R` (SDO2), as above |
| 13–19, 27–29, 31–37, 40–43 | GPIO9–GPIO29 | — | not connected | Free for firmware; no other function asks for a line |

The five taps sit on consecutive GPIOs, clocks first: a PIO state machine reads them in one `IN` from `PINCTRL_IN_BASE` = 4, since the IN bus is the GPIO inputs rotated by IN_BASE (DS §11.5.6), so BRD-041 capture needs no remapping. The I2C2 option of record 46 is not wired: G16 keeps the RP2354A off I2C2 unless isolated. SWD, RUN, BOOTSEL and USB stay on the RP2354A's dedicated pins (table above).

### Faceplate

| Ball | Pad | Function | Domain | Reset state and why | Net | Block | Escape | Notes |
|---|---|---|---|---|---|---|---|---|
| 1P18 | GPIO0_A0_d | GPIO in | PMUIO1, 3.3 V fixed, vcc3v3_pmu | pull-down until pinctrl; 4.7 kΩ pull-up on FP_3V3 wins (≥ 2.55 V) | `FP_HID_INT_N` | `blk.fp-controls` | core | Faceplate HID controller interrupt, open drain on the faceplate; wake (PMUIO1). Was 0_B7 at 1.8 V in v0 (C4). Masked while FP_3V3 is off |
| 1U5 | GPIO3_A1_d | SPI1_CS0_M1 | VCCIO5, 3.3 V, vcc3v3_sys | pull-down: add a pull-up on FP_3V3 so CS is inactive when the faceplate powers up | `FP_SPI_CS_N` | `blk.fp-controls` | core | Faceplate contact 22 |
| AR10 | GPIO3_A2_d | GPIO out | VCCIO5, 3.3 V, vcc3v3_sys | pull-down | `FP_DBI_DC` | `blk.fp-display` | ring, outer | Faceplate contact 23. I2S3_MCLK_M0 not needed by the MAX98357A |
| 1V3 | GPIO3_A7_d | GPIO out | VCCIO5, 3.3 V, vcc3v3_sys | pull-down: panel in reset | `FP_LCD_RST_N` | `blk.fp-display` | core | Faceplate contact 26 |
| AR7 | GPIO3_B0_d | GPIO in | VCCIO5, 3.3 V, vcc3v3_sys | pull-down | `FP_LCD_TE` | `blk.fp-display` | ring, outer | Faceplate contact 27 |
| AP7 | GPIO3_B1_d | PWM8_M0 | VCCIO5, 3.3 V, vcc3v3_sys | pull-down: backlight off | `BL_PWM` | `blk.fp-backlight` | ring, inner (microvia) | TPS61160 CTRL (enable and PWM dimming; TPS61169 until 2026-10-24, BOM v1.11 line 51); board-side, not on the faceplate connector |
| AR6 | GPIO3_B2_d | GPIO in | VCCIO5, 3.3 V, vcc3v3_sys | pull-down until pinctrl; 4.7 kΩ pull-up on FP_3V3 wins | `FP_ALS_INT_N` | `blk.fp-controls` | ring, outer | Faceplate contact 29, open drain on the faceplate. Was 0_C6 at 1.8 V in v0 (C4). Not a deep-standby wake source |
| AP6 | GPIO3_B3_d | GPIO in/out | VCCIO5, 3.3 V, vcc3v3_sys | pull-down: GT911 address strap level at reset (G9) | `FP_TP_INT` | `blk.fp-controls` | ring, inner (microvia) | Faceplate contact 24; also the GT911 address strap, keep a board pull-down footprint |
| 1U3 | GPIO3_B4_d | GPIO out | VCCIO5, 3.3 V, vcc3v3_sys | pull-down: touch in reset | `FP_TP_RST_N` | `blk.fp-controls` | core | Faceplate contact 25 |
| 1T4 | GPIO3_B5_d | I2C3_SCL_M1 | VCCIO5, 3.3 V, vcc3v3_sys | pull-down until pinctrl; pull-up on FP_3V3 | `FP_I2C_SCL` | `blk.fp-controls` | core | Faceplate contact 17; pull-ups on FP_3V3 (G8), 2.2 kΩ for 400 kHz with ≤ 100 pF from the faceplate (2026-10-24, BOM v1.11) |
| 1V2 | GPIO3_B6_d | I2C3_SDA_M1 | VCCIO5, 3.3 V, vcc3v3_sys | pull-down until pinctrl; pull-up on FP_3V3 | `FP_I2C_SDA` | `blk.fp-controls` | core | Faceplate contact 18; 2.2 kΩ pull-up on FP_3V3 |
| AP4 | GPIO3_C1_d | SPI1_MOSI_M1 | VCCIO5, 3.3 V, vcc3v3_sys | pull-down | `FP_SPI_MOSI` | `blk.fp-controls` | ring, inner (microvia) | Faceplate contact 20 |
| AP3 | GPIO3_C2_d | SPI1_MISO_M1 | VCCIO5, 3.3 V, vcc3v3_sys | pull-down | `FP_SPI_MISO` | `blk.fp-controls` | ring, inner (gap) | Faceplate contact 21 |
| AR2 | GPIO3_C3_d | SPI1_CLK_M1 | VCCIO5, 3.3 V, vcc3v3_sys | pull-down | `FP_SPI_SCLK` | `blk.fp-controls` | ring, outer | Faceplate contact 19 |
| 1V15 | MIPI_DSI_TX0_CLKN/LVDS_TX0_CLKN | MIPI_DSI_TX0_CLKN | DSI0/LVDS0 D-PHY, - | - | `FP_DSI_CLK_N` | `blk.fp-display` | core | Faceplate contact 15 |
| 1V16 | MIPI_DSI_TX0_CLKP/LVDS_TX0_CLKP | MIPI_DSI_TX0_CLKP | DSI0/LVDS0 D-PHY, - | - | `FP_DSI_CLK_P` | `blk.fp-display` | core | Faceplate contact 14; core ball |
| AR30 | MIPI_DSI_TX0_D0N/LVDS_TX0_D0N | MIPI_DSI_TX0_D0N | DSI0/LVDS0 D-PHY, - | - | `FP_DSI_D0_N` | `blk.fp-display` | ring, outer | Faceplate contact 12 |
| AP30 | MIPI_DSI_TX0_D0P/LVDS_TX0_D0P | MIPI_DSI_TX0_D0P | DSI0/LVDS0 D-PHY, - | - | `FP_DSI_D0_P` | `blk.fp-display` | ring, inner (microvia) | Faceplate contact 11 |
| AP29 | MIPI_DSI_TX0_D1N/LVDS_TX0_D1N | MIPI_DSI_TX0_D1N | DSI0/LVDS0 D-PHY, - | - | `FP_DSI_D1_N` | `blk.fp-display` | ring, inner (microvia) | Faceplate contact 9 |
| AR29 | MIPI_DSI_TX0_D1P/LVDS_TX0_D1P | MIPI_DSI_TX0_D1P | DSI0/LVDS0 D-PHY, - | - | `FP_DSI_D1_P` | `blk.fp-display` | ring, outer | Faceplate contact 8 |
| AR27 | MIPI_DSI_TX0_D2N/LVDS_TX0_D2N | MIPI_DSI_TX0_D2N | DSI0/LVDS0 D-PHY, - | - | `FP_DSI_D2_N` | `blk.fp-display` | ring, outer | Faceplate contact 6 |
| AP27 | MIPI_DSI_TX0_D2P/LVDS_TX0_D2P | MIPI_DSI_TX0_D2P | DSI0/LVDS0 D-PHY, - | - | `FP_DSI_D2_P` | `blk.fp-display` | ring, inner (microvia) | Faceplate contact 5 |
| AP26 | MIPI_DSI_TX0_D3N/LVDS_TX0_D3N | MIPI_DSI_TX0_D3N | DSI0/LVDS0 D-PHY, - | - | `FP_DSI_D3_N` | `blk.fp-display` | ring, inner (microvia) | Faceplate contact 3 |
| AR26 | MIPI_DSI_TX0_D3P/LVDS_TX0_D3P | MIPI_DSI_TX0_D3P | DSI0/LVDS0 D-PHY, - | - | `FP_DSI_D3_P` | `blk.fp-display` | ring, outer | Faceplate contact 2 |

### HAT

**2026-10-25 ([RFC 0014](https://github.com/opendap-project/rfcs/blob/main/text/0014-hat-interface-v2-usb-only.md), hats `standard/` interface v2):** HATs are USB only. The HAT port keeps USB3 HOST1 (SuperSpeed pairs and D±) and gains a Type-C port controller whose interrupt takes AG37; the other HAT balls are freed (table below, and the spare table).

| Ball | Pad | Function | Domain | Reset state and why | Net | Block | Escape | Notes |
|---|---|---|---|---|---|---|---|---|
| AG37 | GPIO0_A5_d | GPIO in | PMUIO1, 3.3 V fixed, vcc3v3_pmu | pull-down until pinctrl; 4.7 kΩ pull-up to vcc3v3_pmu wins | `HAT_PD_INT_N` | `blk.hat-5v` | ring, inner (microvia) | INT_N of the HAT port's Type-C port controller (FUSB302B01MPX, I2C1 0x23), open drain; wake. RFC 0014: was `HAT_DET_N` (presence is USB attach) |
| 1J20 | USB3_HOST1_DM | USB3_HOST1_DM | USB PHY (usb2phy0 host), - | - | `HAT_USB3_DM` | `blk.hat-signals` | core | 2.2 Ω series |
| 1J19 | USB3_HOST1_DP | USB3_HOST1_DP | USB PHY (usb2phy0 host), - | - | `HAT_USB3_DP` | `blk.hat-signals` | core | USB 2 half of the HAT port, 2.2 Ω series |
| V37 | USB3_HOST1_SSRXN/SATA1_RXN | USB3_HOST1_SSRXN | USB3 PHY (combphy1), - | - | `HAT_USB3_SSRX_N` | `blk.hat-signals` | ring, inner (microvia) | Direct |
| V38 | USB3_HOST1_SSRXP/SATA1_RXP | USB3_HOST1_SSRXP | USB3 PHY (combphy1), - | - | `HAT_USB3_SSRX_P` | `blk.hat-signals` | ring, outer | Direct (HDG p. 59) |
| W38 | USB3_HOST1_SSTXN/SATA1_TXN | USB3_HOST1_SSTXN | USB3 PHY (combphy1), - | - | `HAT_USB3_SSTX_N` | `blk.hat-signals` | ring, outer | 100 nF series |
| W37 | USB3_HOST1_SSTXP/SATA1_TXP | USB3_HOST1_SSTXP | USB3 PHY (combphy1), - | - | `HAT_USB3_SSTX_P` | `blk.hat-signals` | ring, inner (microvia) | 100 nF series (BOM line 70) |

#### Balls freed by RFC 0014 (2026-10-25)

| Ball | Pad | Was | Now |
|---|---|---|---|
| AJ38 | GPIO0_A6_d | `HAT_INT_N` | `SPARE_0A6`, spare (spare table) |
| A22 | GPIO1_A0_u | `HAT_EXT_SEL` | `SPARE_1A0`, spare (spare table) |
| B22 | GPIO1_A1_u | `HAT_EXT_PD` | `SPARE_1A1`, spare (spare table) |
| B24 | GPIO1_A5_d | `HAT_ID_EN` | `SPARE_1A5`, spare (spare table) |
| 1A14 | GPIO1_A6_d | `HAT_MCLK_EN` | `SPARE_1A6`, spare (spare table) |
| 1B13 | GPIO1_B0_d | `HAT_EXT_SB1` | `RSVD_PCIE_CLKREQ_N`, reserved (spare table; 2026-10-25) |
| A26 | GPIO1_B1_d | `HAT_EXT_SB2` | `RSVD_PCIE_WAKE_N`, reserved (spare table; 2026-10-25) |
| B26 | GPIO1_B2_d | `SOC_EXT_SB0` | `RSVD_PCIE_PERST_N`, reserved (spare table; 2026-10-25) |
| 1B14 | GPIO1_B3_d | `HAT_RST_N` | `SPARE_1B3`, spare (spare table) |
| 1C15 | GPIO1_D4_u | `HAT_AUD_OE_N` | `SPARE_1D4`, spare (spare table) |
| A35 | GPIO2_B1_d | `HAT_ID_SDA_1V8` | `SPARE_2B1`, spare (spare table) |
| B34 | GPIO2_B2_u | `HAT_ID_SCL_1V8` | `SPARE_2B2`, spare (spare table) |
| AP5 | GPIO3_B7_d | `HAT_GPIO0` | `SPARE_3B7`, spare (spare table) |
| AR4 | GPIO3_C0_d | `HAT_GPIO1` | `SPARE_3C0`, spare (spare table) |
| 1P3 | GPIO3_C4_d | `HAT_GPIO2` | `SPARE_3C4`, spare (spare table) |
| 1P4 | GPIO3_C5_d | `HAT_GPIO3` | `SPARE_3C5`, spare (spare table) |
| AM2 | GPIO3_D2_d | `HAT_I2S_DIN0_1V8` | `SPARE_3D2`, spare (spare table) |
| AM1 | GPIO3_D3_d | `HAT_I2S_DIN1_1V8` | `SPARE_3D3`, spare (spare table) |
| 1R2 | GPIO3_D4_d | `HAT_I2S_DIN2_1V8` | `SPARE_3D4`, spare (spare table) |
| 1T1 | GPIO3_D5_d | `HAT_I2S_DIN3_1V8` | `SPARE_3D5`, spare (spare table) |
| AD1 | GPIO4_B5_d | `HAT_I2S_DOUT_1V8` | `SPARE_4B5`, spare (spare table) |
| AR12 | GPIO4_C7_u | `HAT_I2C_SCL` | `SPARE_4C7`, spare (spare table) |
| AP11 | GPIO4_D0_u | `HAT_I2C_SDA` | `SPARE_4D0`, spare (spare table) |
| 1U9 | MIPI_CSI_RX_CLK0N | `HAT_CSI_CLK_N` | `NC`: no consumer; unused-PHY handling per O2 |
| 1V9 | MIPI_CSI_RX_CLK0P | `HAT_CSI_CLK_P` | `NC`: no consumer; unused-PHY handling per O2 |
| AR18 | MIPI_CSI_RX_D0N | `HAT_CSI_D0_N` | `NC`: no consumer; unused-PHY handling per O2 |
| AP18 | MIPI_CSI_RX_D0P | `HAT_CSI_D0_P` | `NC`: no consumer; unused-PHY handling per O2 |
| AP17 | MIPI_CSI_RX_D1N | `HAT_CSI_D1_N` | `NC`: no consumer; unused-PHY handling per O2 |
| AR17 | MIPI_CSI_RX_D1P | `HAT_CSI_D1_P` | `NC`: no consumer; unused-PHY handling per O2 |
| AR15 | MIPI_CSI_RX_D2N | `HAT_CSI_D2_N` | `NC`: no consumer; unused-PHY handling per O2 |
| AP15 | MIPI_CSI_RX_D2P | `HAT_CSI_D2_P` | `NC`: no consumer; unused-PHY handling per O2 |
| AP14 | MIPI_CSI_RX_D3N | `HAT_CSI_D3_N` | `NC`: no consumer; unused-PHY handling per O2 |
| AR14 | MIPI_CSI_RX_D3P | `HAT_CSI_D3_P` | `NC`: no consumer; unused-PHY handling per O2 |
| 1K20 | PCIE20_REFCLKN | `HAT_PCIE_REFCLK_N` | `NC`: no consumer; unused-PHY handling per O2 |
| 1K19 | PCIE20_REFCLKP | `HAT_PCIE_REFCLK_P` | `NC`: no consumer; unused-PHY handling per O2 |
| AB38 | PCIE20_RXN/SATA2_RXN | `HAT_PCIE_RX_N` | `NC`: no consumer; unused-PHY handling per O2 |
| AB37 | PCIE20_RXP/SATA2_RXP | `HAT_PCIE_RX_P` | `NC`: no consumer; unused-PHY handling per O2 |
| AA38 | PCIE20_TXN/SATA2_TXN | `HAT_PCIE_TX_N` | `NC`: no consumer; unused-PHY handling per O2 |
| AA37 | PCIE20_TXP/SATA2_TXP | `HAT_PCIE_TX_P` | `NC`: no consumer; unused-PHY handling per O2 |
| 1A19 | SARADC_VIN3 | `EFUSE_HAT3V3_IMON` (eFuse #B) | `EFUSE_VBUS_IMON`: eFuse #C IMON (closes C10) |

The 16 PCIe 2.0 and CSI RX PHY balls above stay unconnected in v1. Reserved on 2026-10-25 for a possible radio module variant on PCIe with USB 2×2 (a swap that needs a `blk.radio` revision, feature blocks record 39): the PCIe sideband balls B26, 1B13 and A26 (`RSVD_PCIE_PERST_N`, `RSVD_PCIE_CLKREQ_N`, `RSVD_PCIE_WAKE_N`, unconnected with no-connect flags) and USB 2.0 HOST3 (Y1, Y2, unconnected).

### Spare and reserved GPIO

| Ball | Pad | Domain | Reset | Net | Why it is spare |
|---|---|---|---|---|---|
| B23 | GPIO1_A3_d | VCCIO1, 3.3 V, vcc3v3_sys | _d | `SPARE_1A3` | Spare 3.3 V GPIO, test pad |
| 1A13 | GPIO1_A4_d | VCCIO1, 3.3 V, vcc3v3_sys | _d | `SPARE_1A4` | Spare 3.3 V GPIO, test pad |
| B25 | GPIO1_A7_d | VCCIO1, 3.3 V, vcc3v3_sys | _d | `SPARE_1A7` | Spare 3.3 V GPIO, test pad |
| 1A15 | GPIO1_D0_d | VCCIO2, 1.8 V, vcc_1v8 | _d | `SPARE_1D0` | FSPI_CLK: driven by the BootROM FSPI probe (HDG p. 18 boot order), so no load; test pad only (C5) |
| 1A17 | GPIO1_D1_u | VCCIO2, 1.8 V, vcc_1v8 | _u | `SPARE_1D1` | FSPI_D0: driven by the BootROM FSPI probe, so no load; test pad only (C5) |
| 1B17 | GPIO1_D3_u | VCCIO2, 1.8 V, vcc_1v8 | _u | `SPARE_1D3` | FSPI_CS0n: driven by the BootROM, so no load; test pad only (C5) |
| B36 | GPIO2_C1_d | VCCIO4, 1.8 V, vcc_1v8 | _d | `RSVD_15P4_SPI_CLK` | Kept free: SPI2_CLK_M0, the only 1.8 V SPI that can reach the module 802.15.4 SPI (pins 4-8). Not connected in v1 (O6 closed 2026-10-24: unassigned spare reserved for a variant) |
| C37 | GPIO2_C2_d | VCCIO4, 1.8 V, vcc_1v8 | _d | `RSVD_15P4_SPI_MISO` | Kept free: SPI2_MISO_M0 (O6 closed 2026-10-24: unassigned spare reserved for a variant) |
| 1D19 | GPIO2_C3_d | VCCIO4, 1.8 V, vcc_1v8 | _d | `RSVD_15P4_SPI_MOSI` | Kept free: SPI2_MOSI_M0 (O6 closed 2026-10-24: unassigned spare reserved for a variant) |
| 1B20 | GPIO2_C4_d | VCCIO4, 1.8 V, vcc_1v8 | _d | `RSVD_15P4_SPI_CS` | Kept free: SPI2_CS0_M0 (O6 closed 2026-10-24: unassigned spare reserved for a variant) |
| 1V6 | GPIO4_C4_d | VCCIO7, 3.3 V, vcc3v3_sys | _d, plus 100 kΩ pull-down | `MCLK_DIV_RUN` | Clear of both MCLK dividers (ADR 0019; `blk.audio.clock`). Held low at reset, so the dividers stay cleared until the driver releases them after MCLK_1V8 is up; the SN74AUC1G74 inputs tolerate 3.6 V at any VCC (SCES537D p. 3). Driven high only while MCLK_1V8 is on (Ioff is specified at 2.7 V only). Assigned 2026-10-24, BOM v1.9 item 39 |
| 1V5 | GPIO4_D1_u | VCCIO7, 3.3 V, vcc3v3_sys | _u | `SPARE_4D1` | Spare 3.3 V GPIO, test pad; pull-up at reset, so not for an enable |
| A22 | GPIO1_A0_u | VCCIO1, 3.3 V, vcc3v3_sys | _u | `SPARE_1A0` | Spare 3.3 V GPIO, test pad (RFC 0014: was `HAT_EXT_SEL`) |
| B22 | GPIO1_A1_u | VCCIO1, 3.3 V, vcc3v3_sys | _u | `SPARE_1A1` | Spare 3.3 V GPIO, test pad (RFC 0014: was `HAT_EXT_PD`) |
| B24 | GPIO1_A5_d | VCCIO1, 3.3 V, vcc3v3_sys | _d | `SPARE_1A5` | Spare 3.3 V GPIO, test pad (RFC 0014: was `HAT_ID_EN`) |
| 1A14 | GPIO1_A6_d | VCCIO1, 3.3 V, vcc3v3_sys | _d | `SPARE_1A6` | Spare 3.3 V GPIO, test pad (RFC 0014: was `HAT_MCLK_EN`) |
| 1B13 | GPIO1_B0_d | VCCIO1, 3.3 V, vcc3v3_sys | _d | `RSVD_PCIE_CLKREQ_N` | Reserved for a PCIe + USB 2×2 radio module variant (PCIE20_CLKREQn_M2, 2026-10-25); not connected in v1, no-connect flag (RFC 0014: was `HAT_EXT_SB1`) |
| A26 | GPIO1_B1_d | VCCIO1, 3.3 V, vcc3v3_sys | _d | `RSVD_PCIE_WAKE_N` | Reserved for a PCIe + USB 2×2 radio module variant (PCIE20_WAKEn_M2, 2026-10-25); not connected in v1, no-connect flag (RFC 0014: was `HAT_EXT_SB2`) |
| B26 | GPIO1_B2_d | VCCIO1, 3.3 V, vcc3v3_sys | _d | `RSVD_PCIE_PERST_N` | Reserved for a PCIe + USB 2×2 radio module variant (PCIE20_PERSTn_M2, 2026-10-25); not connected in v1, no-connect flag (RFC 0014: was `SOC_EXT_SB0`) |
| 1B14 | GPIO1_B3_d | VCCIO1, 3.3 V, vcc3v3_sys | _d | `SPARE_1B3` | Spare 3.3 V GPIO, test pad (RFC 0014: was `HAT_RST_N`) |
| 1C15 | GPIO1_D4_u | VCCIO2, 1.8 V, vcc_1v8 | _u | `SPARE_1D4` | Spare 1.8 V GPIO on an FSPI ball the BootROM probes (C5), left unconnected (RFC 0014: was `HAT_AUD_OE_N`) |
| A35 | GPIO2_B1_d | VCCIO4, 1.8 V, vcc_1v8 | _d | `SPARE_2B1` | Spare 1.8 V GPIO, test pad (RFC 0014: was `HAT_ID_SDA_1V8`) |
| B34 | GPIO2_B2_u | VCCIO4, 1.8 V, vcc_1v8 | _u | `SPARE_2B2` | Spare 1.8 V GPIO, test pad (RFC 0014: was `HAT_ID_SCL_1V8`) |
| AP5 | GPIO3_B7_d | VCCIO5, 3.3 V, vcc3v3_sys | _d | `SPARE_3B7` | Spare 3.3 V GPIO, test pad (RFC 0014: was `HAT_GPIO0`) |
| AR4 | GPIO3_C0_d | VCCIO5, 3.3 V, vcc3v3_sys | _d | `SPARE_3C0` | Spare 3.3 V GPIO, test pad (RFC 0014: was `HAT_GPIO1`) |
| 1P3 | GPIO3_C4_d | VCCIO5, 3.3 V, vcc3v3_sys | _d | `SPARE_3C4` | Spare 3.3 V GPIO, test pad (RFC 0014: was `HAT_GPIO2`) |
| 1P4 | GPIO3_C5_d | VCCIO5, 3.3 V, vcc3v3_sys | _d | `SPARE_3C5` | Spare 3.3 V GPIO, test pad (RFC 0014: was `HAT_GPIO3`) |
| AM2 | GPIO3_D2_d | VCCIO6, 1.8 V, vccio6_1v8 | _d | `SPARE_3D2` | Spare 1.8 V GPIO on the audio bank, left unconnected (no stub beside the I2S1 lines) (RFC 0014: was `HAT_I2S_DIN0_1V8`) |
| AM1 | GPIO3_D3_d | VCCIO6, 1.8 V, vccio6_1v8 | _d | `SPARE_3D3` | Spare 1.8 V GPIO on the audio bank, left unconnected (no stub beside the I2S1 lines) (RFC 0014: was `HAT_I2S_DIN1_1V8`) |
| 1R2 | GPIO3_D4_d | VCCIO6, 1.8 V, vccio6_1v8 | _d | `SPARE_3D4` | Spare 1.8 V GPIO on the audio bank, left unconnected (no stub beside the I2S1 lines) (RFC 0014: was `HAT_I2S_DIN2_1V8`) |
| 1T1 | GPIO3_D5_d | VCCIO6, 1.8 V, vccio6_1v8 | _d | `SPARE_3D5` | Spare 1.8 V GPIO on the audio bank, left unconnected (no stub beside the I2S1 lines) (RFC 0014: was `HAT_I2S_DIN3_1V8`) |
| AD1 | GPIO4_B5_d | VCCIO6, 1.8 V, vccio6_1v8 | _d | `SPARE_4B5` | Spare 1.8 V GPIO on the audio bank, left unconnected (no stub beside the I2S1 lines) (RFC 0014: was `HAT_I2S_DOUT_1V8`) |
| AR12 | GPIO4_C7_u | VCCIO7, 3.3 V, vcc3v3_sys | _u | `SPARE_4C7` | Spare 3.3 V GPIO, test pad (RFC 0014: was `HAT_I2C_SCL`) |
| AP11 | GPIO4_D0_u | VCCIO7, 3.3 V, vcc3v3_sys | _u | `SPARE_4D0` | Spare 3.3 V GPIO, test pad (RFC 0014: was `HAT_I2C_SDA`) |

### Expander lines (TCA6416A, I2C2 0x21)

VCCI on vcca1v8_pmu, VCCP on vcc3v3_sys (BOM v1.8 line 93); every port is an input after power-up (SCPS194F p. 1), so each output carries a board pull-down to its off state (PCB-P-18). Its interrupt is `EXP_INT_N` on GPIO0_D6. Lines here are slow (I2C latency) and hold their state through suspend.

| Port | Net | Direction | Default (board pull) | Block | Why on the expander |
|---|---|---|---|---|---|
| P00 | `FP_IO_EN` | out | low (off) | `blk.fp-connector` | Power tree §5; state kept in suspend if faceplate wake is wanted (B5). From 2026-10-24 (BOM v1.11): ON of the FP_3V3 TPS22950 and of the FP_1V8 and FP_VCI TPS22945 |
| P01 | `HAT_VBUS_DISCH` | out | low (off) | `blk.hat-5v` | 2026-10-25 (RFC 0014): gate of the HAT `VBUS` discharge FET, driven after the source turns off (power tree v0.7 item 7). Was `HAT3V3_EN` (HAT_3V3 removed) |
| P02 | `HAT5V_EN` (= `HAT_SRC_ON`) | out | low (off) | `blk.hat-5v` | Power tree §5; also forces TPS2121 OV2. 2026-10-25: the HAT `VBUS` source enable, driven as the TCPM `vbus-supply` of the HAT port |
| P03 | `USB_SRC_ON` | out | low (off) | `blk.usb-vbus-out` | Power tree §5; also forces TPS2121 OV1 |
| P04 | `HAPTIC_EN` | out | low (off) | `blk.haptics` | G20, BOM v1.8 line 93 |
| P05 | — (spare; was `NFC_PWR_EN`) | out | low (driver) | — | No-connect. Maintainer decision 2026-10-27, the NFC reader removed (was G7, BOM v1.8 line 50) |
| P06 | `WL_PWR_EN` | `blk.radio` | low (radio off) | Radio 3.3 V load switch and, through it, AVDD18; holds through suspend when Bluetooth tracking is on (BOM v1.9 decision a) | — |
| P07 | `WL_PD_HOLD_N` (was `WL_PDN_HOLD`; renamed 2026-10-25 for the `_N` rule, CRAFT-84) | `blk.radio` | low (power-down) | Radio PDn through an SN74AXC1T45 (A = expander 3.3 V, B = `vcc1v8_wl`, DIR high), so PDn holds through suspend; with the radio rail off the B port is unpowered and Ioff protects it (SCES882E). Replaces GPIO2_B7 for PDn (BOM v1.9 item 40) | — |
| P10 | `HP_DET_SE` | in | jack switch pull-up | `blk.jack-se` | BRD-052; interrupt latency in milliseconds is enough |
| P11 | `HP_DET_BAL` | in | jack switch pull-up | `blk.jack-bal` | BRD-052 |
| P12 | `FP_DET_N` | in | pull-up (absent) | `blk.fp-connector` | Faceplate contact 36 |
| P13 | `FP_GPIO0` | in/out | pull-down | `blk.fp-connector` | Faceplate contact 37 (RFC 0001: slow lines) |
| P14 | `FP_GPIO1` | in/out | pull-down | `blk.fp-connector` | Faceplate contact 38 |
| P15 | `EFUSE_HAT5V_FLT_N` | in | pull-up | `blk.hat-5v` | eFuse #A fault |
| P16 | `EFUSE_5V_FLT_N` | in | pull-up | `blk.usb-vbus-out` | eFuse #D fault (shared 5.1 V limiter, BOM v1.14 line 44, [RFC 0015](https://github.com/opendap-project/rfcs/blob/main/text/0015-hat-connector-pogo-field-and-usb-c-port-hat.md)). Spare from 2026-10-25 (RFC 0014: was `EFUSE_HAT3V3_FLT_N`, eFuse #B removed) |
| P17 | `EFUSE_VBUS_FLT_N` | in | pull-up | `blk.usb-vbus-out` | eFuse #C fault |

The fuel-gauge alert of v0 §2.3 has no source: the BQ28Z610-R1 has no alert pin (SLUSE07B p. 3, Figure 6-1), so the gauge is read over I2C1 and charger events arrive on `CHG_INT_N` (C25).

## 4. Boot strapping, MaskROM and recovery

| Item | Ball | Level at reset | How it is set | Source |
|---|---|---|---|---|
| `FLASH_VOL_SEL` | AF38 (GPIO0_A7_u) | High: VCCIO2 is 1.8 V | Internal pull-up plus an external pull-up to vcc3v3_pmu; nothing else on the net. A low here with a 1.8 V VCCIO2 makes the flash interface misbehave (HDG p. 19, p. 31) | HDG p. 19, p. 20 Table 2-3 |
| `SDMMC0_DET` | AF37 (GPIO0_A4_u) | Low with a card (SDMMC function), high without (JTAG and UART on the SDMMC0 balls) | Socket switch to ground, 100 Ω series (HDG p. 52) | HDG p. 19, p. 20 Table 2-3 |
| Boot order | — | FSPI NOR, FSPI NAND, NAND, eMMC, SD; MaskROM over USB OTG0 when nothing boots | The T1 has no FSPI or NAND part, so the BootROM probes the FSPI balls first at every boot (§5 C5) | HDG p. 18 |
| MaskROM (BRD-016, BRD-035) | eMMC_D0 A32 (GPIO1_B4) | — | Power + Vol− held at power-on: `blk.maskrom` pulls `EMMC_D0` low through 1 kΩ inside the boot window, so the eMMC does not answer and, with no bootable card, the BootROM falls to MaskROM on `USBC_DP`/`USBC_DM` (BOM lines 35, 78, 97, 98; t1 controls spec §1.2). `EMMC_D0` (A32) and `EMMC_CLK` (A29) are outer-ring balls with test points (HDG p. 27) | HDG pp. 18, 27 |
| Vol− for the MaskROM gate | 1C17 (SARADC_VIN1) | — | Kept on SARADC_VIN1 as in BOM line 77. A GPIO would not do: every free PMU ball is `_d`, and the internal pull-down against the 100 kΩ pull-up would read "pressed" at every power-on and trigger MaskROM with the power button alone | BOM lines 77, 98; DS p. 53 |
| Recovery key (BRD-017) | 1D17 (SARADC_VIN0) | High (10 kΩ to vcca_1v8) | Vol+ held low at boot enters the loader's Rockusb mode (HDG p. 59); 1 nF at the pin (HDG p. 60, Table 2-14) | HDG pp. 59–60 |
| SD recovery (BRD-043) | SDMMC0 balls | — | A card in the slot pulls `SD_DET_N` low, so SDMMC is selected and the BootROM boots it when the eMMC is empty or masked | HDG pp. 18–20 |
| Reset | AG38 (nPOR_u) | — | RK809 RESETB; 100 nF at the pin, pull-up to the PMUIO1 rail; `TSADC_SHUT_M0` (GPIO0_A1, 1R20) joins the same net (HDG p. 18, Fig. 2-2). Minimum pulse 4 µs (HDG p. 17) | HDG pp. 17–18 |
| Debug console (BRD-047) | 1V19, 1U18 (UART2 M0) | Idle high | 1.8 V pads, 1.5 Mbaud default (HDG pp. 61–62). With no card, `UART2_TX_M1`/`RX_M1` and ARM JTAG also appear on the microSD contacts at VCCIO3 level (HDG p. 20) | HDG pp. 20, 61 |

## 5. Conflicts in v0 and their resolution

"v0" is pin multiplexing v0; "v1" is §3.

| # | Conflict | Evidence | Resolution in v1 |
|---|---|---|---|
| C1 | I2C5 M1 (HAT I2C) uses the HDMI DDC balls, and HDG p. 64 says HDMITX_SCL/SDA is dedicated to the HDMI controller | HDG p. 64; DS p. 35 lists I2C5_SCL_M1/SDA_M1 as separate mux functions on AR12/AP11; HDG Table 2-16 lists I2C5 M1 on VCCIO7 | Kept: the T1 has no HDMI and the HDG sentence concerns the DDC function, not the I2C5 mux. I2C5 M0 is taken by the touch lines. Open item O1 with a fallback. 2026-10-25: closed, the HAT I2C is removed (RFC 0014); AR12 and AP11 are spares |
| C2 | Radio host-wake lines on GPIO2_C0/C1 (VCCIO4) cannot wake from standby | HDG pp. 17, 35, 53 ("WIFI/BT control signal should be connected to the GPIO of the PMUIO power domain") | `WL_WAKE_OUT` → GPIO0_B7, `BT_WAKE_OUT` → GPIO0_C6 |
| C3 | Expander interrupt on an FSPI ball or wired-OR with the RP2354A IRQ; BRD-014 context forbids must functions relayed by the coprocessor | Requirements context (BRD-014) | `EXP_INT_N` on its own PMUIO0 ball (GPIO0_D6); `RP_IRQ` stays the RP2354A's own line |
| C4 | Faceplate `HID_INT` and `ALS_INT` at 1.8 V (PMUIO2) while the faceplate interface says 3.3 V for the low-speed groups | t1 faceplate interface v0 (v1 since 2026-10-24) | `FP_HID_INT_N` → GPIO0_A0 (PMUIO1, 3.3 V, wake); `FP_ALS_INT_N` → GPIO3_B2 (VCCIO5, 3.3 V, not a standby wake source; spec edit in §8.3) |
| C5 | FSPI balls (GPIO1_D0–D4) carried the 4.4 mm amplifier enable, the speaker SD_MODE and the RP2354A SWD; the BootROM probes FSPI first at every boot | HDG p. 18 boot order | Only the TPM PIRQ (an input) and the HAT translators' OE (pull-up, a toggle only enables isolated translators with Ioff) remain; FSPI_CLK, FSPI_D0 and FSPI_CS0n are test pads only |
| C6 | RP2354A BOOTSEL wired to a 1.8 V ball; BOOTSEL is the QSPI chip select, powered by QSPI_IOVDD = RP_3V3 (the internal flash needs 2.7–3.6 V) | RP2350 pp. 18, 340, 1329; BOM line 12 | `RP_BOOTSEL_DRV` (GPIO3_C6) drives the gate of an N-FET that pulls QSPI_SS low; no 3.3 V reaches the SoC (B8) |
| C7 | Bluetooth PCM reserved through DNP links on I2S2 M0 balls that v0 also gave to RP2354A RUN/BOOTSEL and BT_WAKE | v0 §2.2 | Dropped: Bluetooth audio runs over HCI (ADR 0006). I2S2 M1 balls went to audio enables |
| C8 | PCA9306 enable as a push-pull GPIO: EN and VREF2 form the bias node at VREF1 + Vth (≈ 2.4 V with 1.8 V on side 1), and a GPIO high must not exceed it | SCPS113O §8.1.2–8.1.3 (pp. 10, 12) | `HAT_ID_EN` on GPIO1_A5 (3.3 V ball) used open drain: the SoC only pulls EN low or releases it; 200 kΩ from EN/VREF2 to HAT_3V3 (B8). 2026-10-25: no longer applies, the PCA9306 is removed (RFC 0014) |
| C9 | Master-clock ST lines on 1.8 V balls cannot reach VIH ≥ 2.17 V | BOM §4.3 | `MCLK441_EN`, `MCLK48_EN` on GPIO4_C2/C3 (VCCIO7, 3.3 V); ST rating at 3.3 V into a 3.1 V oscillator **UNVERIFIED** (O11) |
| C10 | Four SARADC inputs for Vol+, Vol− and three eFuse IMON outputs | HDG p. 59 (four inputs); BOM lines 44, 77 | VIN2 = eFuse #A (HAT 5 V), VIN3 = eFuse #B (HAT 3.3 V); eFuse #C (USB-C VBUS out) IMON to a test pad. The INA236 HAT channel at the 5.1 V buck input sees #A + #C together (B6). 2026-10-25: closed, eFuse #B is removed and SARADC_VIN3 takes eFuse #C IMON (RFC 0014) |
| C11 | TPM, PN7160 and haptic lines unassigned; PN7160 DWL_REQ planned on a 3.3 V expander line into a 1.65–1.95 V pin | Feature blocks G5, G7, G20 | Native 1.8 V balls in the device's domain (§7); `HAPTIC_EN`, `NFC_PWR_EN` on expander lines |
| C12 | Speaker SD_MODE on GPIO1_D1, a `_u` ball: the amplifier (always supplied from VSYS_LV) would be enabled at reset | DS Table 2-1; MAX98357A SD_MODE high = on | `SPK_SD_MODE` on GPIO3_A6 (`_d`, VCCIO5 3.3 V) with the select resistor of MAX98357A Figure 5 |
| C13 | HAT GPIO alternates (UART3 M1, UART7 M1) and their TX/RX order were **UNVERIFIED** | v0 §4.3 | Confirmed on DS: GPIO3_B7 UART3_TX_M1, GPIO3_C0 UART3_RX_M1, GPIO3_C4 UART7_TX_M1, GPIO3_C5 UART7_RX_M1, matching interface v1 §4.3. 2026-10-25: the HAT GPIO balls are spares (RFC 0014); the alternates stay available |
| C14 | GPIO4_D1 domain and VCCIO7 extent **UNVERIFIED** | v0 risk 12 | VCCIO7 = GPIO4_C2–D1 (DS §2.7 p. 35; HDG Tables 2-17, 2-18) |
| C15 | Domain map taken from the RK3568 datasheet | v0 risk 1 | Every domain re-read on DS 1.1 and HDG (§1). PMUIO0 holds four free 1.8 V GPIO (GPIO0_D3–D6), now used for always-on lines |
| C16 | FUSB302B on a 1.8 V I2C1 **UNVERIFIED** | v0 §5.1 | VIH 1.32 V (FUSB302B/D Rev. 5 p. 16): fits |
| C17 | `CLK32K_IN` level not stated | v0 §2.3 | RK809 CLK32K is open drain (RK809 p. 15): pull-up to vcca1v8_pmu, level 0.65 × VDD to VDD + 0.3 (HDG p. 17, Table 2-2) |
| C18 | `CLK32K_OUT1` reserved as the radio sleep clock | v0 §2.2 | Not needed: the Type 2EL has no 32.768 kHz input (E2B-54-1953 Table 3). GPIO2_C6 now carries `NFC_DWL_REQ` |
| C19 | Radio PDn on a VCCIO4 ball while v1 drafts put it on a PMU ball | BOM v1.8 item 1 (module VIO on vcc_1v8, radio switched off in suspend) | `WL_PDN` on GPIO2_B7, same rail as the module VIO, so it never drives an unpowered module |
| C20 | RP2354A RUN with an open-drain driver on a `_d` ball: the internal pull-down and a weak pull-up leave RUN between thresholds at reset | DS p. 53; RP2350 p. 17 (RUN in the IOVDD domain) | `RP_RUN` (GPIO4_C1) with 4.7 kΩ to RP_IOVDD_1V8 (≥ 1.39 V at reset); SoC pulls low to reset |
| C21 | Open-drain interrupts on `_d` balls with "a pull-up": undefined strength | DS p. 53 (16–43 kΩ) | External pull-ups ≤ 4.7 kΩ on every open-drain line that lands on a `_d` ball (B9) |
| C22 | `HPA_SE_EN` on the expander, `HPA_BAL_EN` on an FSPI ball | v0 §2.1 | Both on VCCIO6 `_d` balls (GPIO4_B6, GPIO4_B7), same timing for both outputs |
| C23 | Backlight enable line (v0 GPIO3_A6) on the faceplate connector; the faceplate interface has none (the TPS61169 on the board takes `BL_PWM` on CTRL) | RFC 0001 | Removed from the faceplate; GPIO3_A6 reused for `SPK_SD_MODE` |
| C24 | Status LED PWM (GPIO3_B2) | BOM v1.2 (LP5521) | Ball reused for `FP_ALS_INT_N` |
| C25 | Fuel-gauge alert line to the expander | SLUSE07B p. 3: no alert pin on the BQ28Z610-R1 | Removed (B7) |
| C26 | Wake-capable lines needed exceed the free GPIO0 balls when the RP2354A relays nothing | v0 §3.11–3.12 | Faceplate HID interrupt to the free 3.3 V PMUIO1 ball, ALS off the wake set, and the four PMUIO0 balls (C15) |
| C27 | `HAT_INT#`, `HAT_DET#`, `PCIE_CLKREQ#`, `PCIE_WAKE#` on `_d` balls with "a pull-up on the device" | DS p. 53 | 4.7 kΩ pull-ups (B9); `HAT_RST#` and `PCIE_PERST#` on `_d` balls hold the HAT in reset during SoC boot, which is intended 2026-10-24: the PCIe sidebands are now `HAT_EXT_SB0`–`SB2` (interface v1.1), same pulls. 2026-10-25: only AG37 remains, as `HAT_PD_INT_N` with its 4.7 kΩ pull-up; the other lines are removed (RFC 0014) |
| C28 | HAT SWD balls (GPIO1_A0/A1) are `_u`: at reset they pull an unpowered HAT's SWD pins to 3.3 V through 16–43 kΩ | DS Table 2-1 | Pin controller sets them to pull-down while the HAT is unpowered; pull-up ownership stays interface v1 open point 4 2026-10-24: closed by interface v1.1, the balls now drive the extension switch: A22 with an external pull-down, B22 with an external pull-up (standby), no HAT line on either. 2026-10-25: A22 and B22 are spares (RFC 0014) |

## 6. The 0.4 mm ring

Of the 174 signal balls the T1 uses outside the LPDDR4X interface, 69 are core balls (0.65 mm), 50 sit on the outer ring and escape on L1, 11 are inner-ring balls behind a gap (L1 between two outer balls, 0.55 mm copper gap at 0.8 mm spacing), and 44 are inner-ring balls behind an outer ball, which need a laser microvia in the ring-to-core channel (layout rules §3: dog-bone microvias fit, through vias do not). The CSV `notes` column gives the class per ball.

Audio balls in the ring (DS Table 2-1):

| Ball | Net | Class | Consequence |
|---|---|---|---|
| AP1 | `I2S_LRCK` | outer | L1 escape, straight to the DAC side |
| AN2 | `I2S_SDO0` | inner, gap | L1 escape |
| AG2 | `DSD_R` | inner, gap | L1 escape |
| AH2 | `I2S_BCLK_RX` | inner, gap | L1 escape (DNP fallback link) |
| AD1 | `SPARE_4B5` (2026-10-25; was a HAT I2S line) | outer | L1 |
| AM1 | `SPARE_3D3` (2026-10-25; was a HAT I2S line) | outer | L1 |
| AM2 | `SPARE_3D2` (2026-10-25; was a HAT I2S line) | inner, behind AM1 | microvia |
| AL1 | `PDM_DATA0` | outer | L1 |
| AL2 | `PDM_CLK0` | inner, behind AL1 | microvia; a clock next to its data ball, guard per PCB-I-08 |
| AK2 | `PDM_CLK1` | inner, gap | L1 |
| AJ2 | `DAC_INT_N` | inner, behind AJ1 | microvia (static line) |
| AR9 | `SPK_LRCK` | outer | L1 |
| AP9 | `SPK_SDIN` | inner, behind AR9 | microvia |
| AP10 | `SPK_BCLK` | inner, behind AR10 | microvia |
| AR10 | `FP_DBI_DC` | outer | (I2S3_MCLK ball, used as a GPIO) |

`I2S_BCLK` (1U1), `I2S_LRCK_RX` (1N1), `DSD_L` (1L2) and the I2S1 SDI2/SDI3 balls (1R2, 1T1) are core balls. So the DAC path (BCLK, LRCK, SDO0, both DSD lines) needs no ring microvia; only the speaker, the faceplate PDM clock and the DAC interrupt do (the HAT capture line is gone since 2026-10-25, RFC 0014). The audio enables in the ring (AB2, AC2, AE2, AF1, AF2) are static lines.

Every DSI0, CSI and HDMI pair in the ring has one ball on row AP (inner) and its partner on row AR (outer) in the same column (for example `FP_DSI_D0_P` AP30, `FP_DSI_D0_N` AR30), so the inner ball of each pair is behind its own partner and takes a microvia. `FP_DSI_CLK_P`/`_N` are core balls (1V16, 1V15): their length to the ring lanes counts against the 0.91 mm data-to-clock limit (layout rules PCB-I-04).

## 7. Pins for the feature-block gaps

| Gap | What the pinout gives | Consistent with |
|---|---|---|
| G1 IMU | `IMU_INT1` on GPIO0_C5 (PMUIO2, vcca1v8_pmu): same always-on rail as the IMU | BOM v1.8 line 59 |
| G2 DAC back-powering | No SoC enable needed: the SN74LVC2G66 is controlled by DAC_DIG_1V8. `DAC_INT_N` (GPIO4_A3) pull-up on DAC_DIG_1V8; I2S1 balls are `_d` and parked low by the pin controller before DAC_DIG_1V8 drops | BOM v1.8 lines 133, 134 |
| G3 MCLK into an unpowered DAC | `AUDIO_LN_EN` (GPIO4_B4, 1.8 V) into the SN74LVC1G57 AND on vcca1v8_pmu (VIH 0.65 × VCC); `MCLK441_EN`/`MCLK48_EN` on GPIO4_C2/C3 at 3.3 V | BOM v1.8 line 135 |
| G4 RP2354A taps | Taps on RP2354A FT GPIO0–25; UART0 (GPIO0_C0/C1) and `RP_IRQ` (GPIO0_C7, board pull-down) also to FT GPIO; SWD (GPIO4_A4/A5) and RUN (GPIO4_C1) parked low or released while RP_IOVDD_1V8 is off; BOOTSEL through the N-FET (C6) | BOM v1.8 line 134 |
| G5 TPM | `TPM_RST_N` on GPIO0_D3 (PMUIO0, vcca1v8_pmu, 2.2 kΩ pull-up: inactive and held through suspend); `TPM_PIRQ_N` on GPIO1_D2 (VCCIO2) with its pull-up on vcc_1v8, so in suspend the line rests at 0 V with no current into either side | BOM v1.8 line 122 |
| G6 NFC tag | `NFC_FD_N` on GPIO0_D4 (PMUIO0, 1.8 V, wake); pull-up to vcca1v8_pmu, the tag's supply. v1 does not use GPIO0_A0 as G6 proposed: a 3.3 V pull-up on a 1.8 V-supplied tag pin would exceed its supply | BOM v1.8 line 125 |
| G7 PN7160 | Withdrawn 2026-10-27 with the NFC reader (BOM v1.18 item 7): GPIO0_D5, GPIO2_C0 and GPIO2_C6 are spares, expander P05 a spare driven low. Was: `NFC_IRQ` on GPIO0_D5, `NFC_VEN` on GPIO2_C0, `NFC_DWL_REQ` on GPIO2_C6, `NFC_PWR_EN` on expander P05 | BOM v1.8 lines 50, 93, 127; BOM v1.18 item 7 |
| G8 Faceplate pull-ups | I2C3 pull-ups on FP_3V3 (2.2 kΩ from 2026-10-24, BOM v1.11); `FP_HID_INT_N` and `FP_ALS_INT_N` now 3.3 V lines with 4.7 kΩ pull-ups on FP_3V3; both masked while FP_3V3 is off | BOM v1.8 item 12 |
| G9 GT911 strap | `FP_TP_INT` on GPIO3_B3 (`_d`) plus a board pull-down footprint; the address the low level selects is read from GT911 v09 pp. 9–10 timing figures, **UNVERIFIED** in text (O7) | — |
| G10 PDM clocks | Both PDM clock balls `_d`, pinctrl sleep state drives low while MIC_1V8 is off | — |
| G14 PCIe reset | `SOC_PCIE_PERST_N` (2026-10-24: `SOC_EXT_SB0`, out of the gate as `HAT_EXT_SB0`) on GPIO1_B2 (VCCIO1, 3.3 V, `_d`: asserted at reset) into the SN74LVC1G57 on vcc3v3_sys; `HAT_MCLK_EN` on GPIO1_A6 for the line-112 buffer (Open) | BOM v1.8 line 135. 2026-10-25: gap closed by removal, PCIe has no HAT consumer and the gate and `HAT_MCLK_EN` go (RFC 0014) |
| G15, G16 | `EXP_INT_N` on PMUIO0; I2C2 on PMUIO2 with pull-ups on vcca1v8_pmu, the same rail as the bank | BOM v1.8 line 93, §4.2 |
| G20 Haptics | `HAPTIC_EN` on expander P04 | BOM v1.8 line 93 |
| G21 I2S parking | Same as G2: `_d` balls and a pinctrl sleep state | BOM v1.8 line 134 |
| G22 Cover detect | `COVER_DET_N` on GPIO0_A6 (AJ38, PMUIO1, 3.3 V, wake-capable), the only spare GPIO0 ball; low with the cover closed. Accepted (2026-10-26). Basis: feature blocks G22 (a spare GPIO that wakes from suspend), BOM v1 line 143; the ball's reset pull-down reads the cover-closed level, the absent state the block record gives | BOM v1 line 143 |

G11–G13 and G17–G19 need no SoC ball.

## 8. Faceplate contact positions on the FH35C-51S (proposal)

### 8.1 Rules

- RFC 0001's group order, in the order of the t1 table: display, I2C, SPI/DBI, touch, panel, interrupts, status LED, microphone, detect and spare GPIO, power, reserved; the eight grounds sit where RFC 0001 places them: between DSI pairs, at group edges, and as returns.
- Each DSI pair has a ground on both sides. Lane 0 and the clock sit together, so a single-lane faceplate (the touch faceplate's panel is one lane, BOM line 81) uses contacts 10–16 only.
- The PDM clock (about 3 MHz) has a ground on the side facing the LED group.
- The backlight anode (13–16.5 V, power tree §3) is at contact 46, with its own return (45) on one side and a reserved contact (47) on the other. Contact 47 never becomes a logic line in a later revision; it may become a ground.
- Contact numbering follows the Hirose drawing; the land pattern decides how the 0.3 mm contacts escape on the board.

### 8.2 Positions

| Contact | Line | Group | Board net | Board source |
|---|---|---|---|---|
| 1 | GND | Ground | GND | — |
| 2 | DSI_D3+ | Display | `FP_DSI_D3_P` | AR26 |
| 3 | DSI_D3− | Display | `FP_DSI_D3_N` | AP26 |
| 4 | GND | Ground | GND | — |
| 5 | DSI_D2+ | Display | `FP_DSI_D2_P` | AP27 |
| 6 | DSI_D2− | Display | `FP_DSI_D2_N` | AR27 |
| 7 | GND | Ground | GND | — |
| 8 | DSI_D1+ | Display | `FP_DSI_D1_P` | AR29 |
| 9 | DSI_D1− | Display | `FP_DSI_D1_N` | AP29 |
| 10 | GND | Ground | GND | — |
| 11 | DSI_D0+ | Display | `FP_DSI_D0_P` | AP30 |
| 12 | DSI_D0− | Display | `FP_DSI_D0_N` | AR30 |
| 13 | GND | Ground | GND | — |
| 14 | DSI_CLK+ | Display | `FP_DSI_CLK_P` | 1V16 |
| 15 | DSI_CLK− | Display | `FP_DSI_CLK_N` | 1V15 |
| 16 | GND | Ground | GND | — |
| 17 | I2C_SCL | I2C | `FP_I2C_SCL` | 1T4 (GPIO3_B5, I2C3_SCL_M1) |
| 18 | I2C_SDA | I2C | `FP_I2C_SDA` | 1V2 (GPIO3_B6, I2C3_SDA_M1) |
| 19 | SPI_SCLK | SPI/DBI | `FP_SPI_SCLK` | AR2 (GPIO3_C3, SPI1_CLK_M1) |
| 20 | SPI_MOSI | SPI/DBI | `FP_SPI_MOSI` | AP4 (GPIO3_C1) |
| 21 | SPI_MISO | SPI/DBI | `FP_SPI_MISO` | AP3 (GPIO3_C2) |
| 22 | SPI_CS# | SPI/DBI | `FP_SPI_CS_N` | 1U5 (GPIO3_A1, SPI1_CS0_M1) |
| 23 | DBI_D/C | SPI/DBI | `FP_DBI_DC` | AR10 (GPIO3_A2) |
| 24 | TP_INT | Touch | `FP_TP_INT` | AP6 (GPIO3_B3) |
| 25 | TP_RST# | Touch | `FP_TP_RST_N` | 1U3 (GPIO3_B4) |
| 26 | LCD_RST# | Panel | `FP_LCD_RST_N` | 1V3 (GPIO3_A7) |
| 27 | LCD_TE | Panel | `FP_LCD_TE` | AR7 (GPIO3_B0) |
| 28 | HID_INT# | Interrupts | `FP_HID_INT_N` | 1P18 (GPIO0_A0, PMUIO1, wake) |
| 29 | ALS_INT# | Interrupts | `FP_ALS_INT_N` | AR6 (GPIO3_B2) |
| 30 | LED_R | Status LED | `LED_R` | LP5521 R output |
| 31 | LED_G | Status LED | `LED_G` | LP5521 G output |
| 32 | LED_B | Status LED | `LED_B` | LP5521 B output |
| 33 | GND | Ground | GND | — |
| 34 | PDM_CLK | Microphone | `PDM_CLK0` | AL2 (GPIO3_D6, PDM_CLK0_M1, 1.8 V) |
| 35 | PDM_DATA | Microphone | `PDM_DATA0` | AL1 (GPIO3_D7, PDM_SDI0_M1, 1.8 V) |
| 36 | FP_DET# | Detect | `FP_DET_N` | Expander P12 |
| 37 | GPIO0 | Spare GPIO | `FP_GPIO0` | Expander P13 |
| 38 | GPIO1 | Spare GPIO | `FP_GPIO1` | Expander P14 |
| 39 | GND | Ground | GND | — |
| 40 | MIC_1V8 | Power | `MIC_1V8` | TPS22945 (`MIC_EN`; TPS22919 until 2026-10-24) |
| 41 | FP_1V8 | Power | `FP_1V8` | TPS22945 (`FP_IO_EN`; TPS22919 until 2026-10-24) |
| 42 | FP_3V3 | Power | `FP_3V3` | TPS22950 (`FP_IO_EN`; TPS22919 until 2026-10-24) |
| 43 | FP_3V3 | Power | `FP_3V3` | as 42 |
| 44 | FP_VCI | Power | `FP_VCI` | RK809 LDO4 through a TPS22945 (`FP_IO_EN`; from 2026-10-24) |
| 45 | BL_LEDK | Power | `BL_LEDK` | TPS61160 FB side (TPS61169 until 2026-10-24) |
| 46 | BL_LEDA | Power | `BL_LEDA` | TPS61160 output, ≤ 27 V open string (TPS61169 until 2026-10-24) |
| 47 | Reserved | Reserved | NC | Never a logic line (next to BL_LEDA) |
| 48–51 | Reserved | Reserved | NC | — |

Counts: 10 DSI + 21 low-speed signals + 7 power + 8 ground + 5 reserved = 51 (RFC 0001: 46 used, 5 reserved). Current per contact stays as BOM line 71 computed (FP_3V3 on two contacts, FP_VCI 0.1 A on one); the contact voltage rating for BL_LEDA is RFC 0001's open question (O8).

### 8.3 Edit the t1 faceplate interface spec needs

Not made here (the spec belongs to t1). In `docs/specs/faceplate-interface.md`, section "Flat-cable connector, interface v0" (2026-10-24: the t1 spec is now faceplate interface v1, which carries these positions in its §1.1, v1.0 of 2026-10-24):

1. Replace the sentence "Contact positions are fixed in pinout v1." with "Contact positions are in the table below (board pinout v1 §8)."
2. Add the table of §8.2 with the columns Contact, Line and Group only (no board nets or SoC balls; the board side stays in the board repository).
3. In the Interrupts row, replace "Open-drain on the faceplate side; wake sources" with "Open-drain on the faceplate side, pulled up on the board to FP_3V3; HID_INT is a wake source, ALS_INT is not".
4. Under the table, add: "Contact 47, next to BL_LEDA, stays reserved or becomes a ground; it never carries a logic line."
5. In "Control commands → Not defined yet", remove "interrupt line": the HID controller's interrupt is HID_INT (contact 28).

## 9. Changes the BOM and the power tree need

For the owner of `bom-v1.md` and `power-tree-v0.md`; nothing here edits them.

### 9.1 Reconciliation with BOM v1.8 and power tree v0.2

| v1.8 / v0.2 assumption | Holds? | Where in this pinout |
|---|---|---|
| Radio VIO and SD_VIO on vcc_1v8 (VCCIO4) | Holds | VCCIO4 = vcc_1v8 (§1); `WL_PDN` moved to VCCIO4 (C19). The host-wake lines stay on PMU balls (C2); they can only wake from standby if a later rail map keeps the radio powered, which BOM line 103's item-tracking baseline (BLE advertising in suspend) needs and v1.8 item 1 does not provide (O9) |
| Native 1.8 V GPIO for PN7160 VEN and DWL_REQ | Withdrawn 2026-10-27 (NFC reader removed) | GPIO2_C0, GPIO2_C6 (VCCIO4) are spares |
| Native 1.8 V GPIO for TPM reset and PIRQ | Holds | GPIO0_D3 (PMUIO0, always on, matching the TPM on vcca1v8_pmu) and GPIO1_D2 (VCCIO2, pull-up on vcc_1v8) |
| NFC tag field detect on native 1.8 V GPIO | Holds | GPIO0_D4 (PMUIO0, vcca1v8_pmu, wake) |
| RP2354A taps only on FT GPIO0–25 | Holds; extended | RP-side rule; v1 also puts the UART and `RP_IRQ` on FT GPIO (G4) |
| `HAPTIC_EN`, `NFC_PWR_EN` on expander spares | Holds | P04, P05 |
| SoC PERST# at 3.3 V (VCCIO1) | Holds | GPIO1_B2 |
| LPDDR4X VDD1 and the 0.6 V LDO bias on vcca1v8_pmu | Holds | No SoC ball changes; the DDR supply balls stay on vcc_ddr and vcc0v6_ddr (CSV) |
| vcc1v8_wl switched with the radio 3.3 V | Holds | No SoC ball; AVDD18 is not an IO domain |
| DAC I2C isolation by SN74LVC2G66 on DAC_DIG_1V8 | Holds | No SoC enable needed (G2) |
| MCLK gated by SN74LVC1G57 AND | Holds | Gate on vcca1v8_pmu accepts the 1.8 V `AUDIO_LN_EN` (VIH 0.65 × VCC) |
| Power tree §5: `MCLK441_EN`/`MCLK48_EN` "TCA6416A or translator, pinout v1"; BOM D2: `HPA_RAIL_EN` "expander or translator" | Resolved | Native 3.3 V balls on VCCIO7, no translator, no expander line |
| Power tree §5: `HAT3V3_EN` as a SoC GPIO | Does not hold | Expander P01 (B3) |

### 9.2 Change list

| # | Document | Change | Reason |
|---|---|---|---|
| B1 | Power tree §3 | Add a `vccio6_1v8` row: vcc_1v8 through a ferrite-bead footprint (0 Ω option) with 100 nF per VCCIO6 ball (1L4, 1L5). **Closed** in power tree v0.3 §3 and BOM v1.9 line 141 (0 Ω link, bead option) | The audio IO bank (I2S1, PDM) shares nothing with the radio and eMMC banks' switching currents; ripple limit ±5 % (HDG p. 32). Value of the filter **UNVERIFIED** |
| B2 | Power tree §3 | Add the IO-domain table of §1 (domain → rail → voltage → `pmu_io_domains` value); the vcc_1v8 row says "IO banks" without naming them. **Closed** in power tree v0.3 §3.1 | Domain mismatch damages pads (IOD p. 2) |
| B3 | Power tree §5 | `HAT3V3_EN` from "SoC GPIO" to expander P01. **Closed** in power tree v0.3 §5 and BOM v1.9 lines 38, 93 | GPIO1–4 lose state in standby (HDG p. 35); a HAT that wakes the T1 must stay powered |
| B4 | Power tree §6.5, BOM line 103 | Decide whether the radio stays powered in suspend. With VIO on vcc_1v8 (off in suspend) it cannot, so wake-on-WLAN and the BLE item-tracking baseline fail. **Closed** by the decision of 2026-10-24 (BOM v1.9 item 2): the radio can stay powered in suspend for item tracking; its rails switch from expander P06 `WL_PWR_EN`, off in suspend by default, with vcc_1v8 kept on while tracking. Follow-up for this pinout: `WL_PWR_EN` on P06 and the `WL_PDN` hold (BOM §7 item 40) | v1.8 item 1 versus line 103 |
| B5 | Power tree §6.5 | Decide whether FP_3V3 stays on in suspend: faceplate-button wake needs the HID controller powered and `FP_HID_INT_N` pulled up. **Closed** by the decision of 2026-10-24 (BOM v1.9 item 3): FP_3V3 off in suspend by default, wake from the body buttons; `FP_IO_EN` on P00 can keep it on | BRD-009; T1-023 |
| B6 | BOM line 44 | "IMON to SoC SARADC" holds for eFuse #A (VIN2) and #B (VIN3); #C goes to a test pad. **Closed** in BOM v1.9 line 44 | C10 |
| B7 | BOM line 42 note, feature-blocks `blk.gauge` | Remove the gauge alert line to the expander. **Closed** in BOM v1.9 line 42 and the `blk.gauge` record | C25 |
| B8 | BOM | Add: one more DMG1012T-7 (line 35, qty +1) as the BOOTSEL driver; 200 kΩ from PCA9306 EN/VREF2 to HAT_3V3 (SCPS113O Figure 8-1); pull-up from `HAT_AUD_OE_N` to vcc_1v8 (SCES898C, SCES875C); series-resistor footprints on the two ST lines; the MAX98357A SD_MODE select resistor (its Table 6); a VBUS divider into `USB_OTG0_VBUSDET` (HDG p. 59, Table 2-13; values per the reference schematic, **UNVERIFIED**). **Closed** in BOM v1.9 lines 35, 141 (VBUS divider values stay **UNVERIFIED**, BOM §7 item 41) | C6, C8, C9, C12; HDG |
| B9 | BOM §5 (passives) | Pulls: external pull-downs on every enable in §3 and P00–P05 (PCB-P-18); pull-ups ≤ 4.7 kΩ on `HAT_DET_N`, `HAT_INT_N`, `FP_HID_INT_N`, `FP_ALS_INT_N`, `ACTION_BTN_N`, `CHG_INT_N`, `USBC_INT_N`, `NFC_FD_N`, `EXP_INT_N`, `DAC_INT_N`, `TPM_PIRQ_N`, `PCIE_CLKREQ_N`, `PCIE_WAKE_N`, `CLK32K_PMIC`; 2.2 kΩ on `TPM_RST_N`; 4.7 kΩ on `RP_RUN`; pull-up on `FLASH_VOL_SEL` to vcc3v3_pmu; pull-downs on `RP_IRQ`, `FP_TP_INT`, `FP_LCD_TE`, `NFC_DWL_REQ`; pull-up on `FP_SPI_CS_N` to FP_3V3. **Closed** in BOM v1.9 line 141 | C20, C21, C27; DS p. 53 |
| B10 | BOM §5 | Series parts per HDG: 22 Ω on I2S3 SCLK and LRCK, PDM CLK0 and CLK1, SDMMC0 D0–D3, CMD, CLK, SDMMC1 CLK, eMMC CLK; 22 Ω on BCLK and LRCK at the DAC (the source; HDG p. 70); 100 Ω on `SD_DET_N`; 2.2 Ω on six USB 2 lines (OTG0, HOST1 USB 2 half, HOST2); 120 Ω 1 % `DDR_RZQ`; 24 MHz network (2 × 18 pF matched to CL, 22 Ω, 1 MΩ); 100 nF on nPOR; 1 nF on SARADC VIN0–3, 10 kΩ on VIN0; eMMC 10 kΩ on D0 and CMD, DS pull-down. **Closed** in BOM v1.9 line 141 | HDG pp. 16–17, 25–26, 52, 54, 59–60, 70–72 |
| B11 | BOM line 93 | The expander port map of §3. **Closed** in BOM v1.9 line 93 (with P06 `WL_PWR_EN`) | — |
| B12 | BOM line 2 | RK809 codec unused: tie MCLK, BCLK, LRCLK, SDI, PDMCLK and HP_SNS to ground; SDO/PDMDATA, CPn/CPp, VCC_CPVDD/CPVSS, HPL/HPR_OUT, SPK_OUTn/p, MIC1p/n may float. **Closed** in BOM v1.9 line 2 | HDG p. 73 |
| B13 | BOM §4.2 table | Replace the IO-domain table with §1 (adds PMUIO0; VCCIO1 now also `RP_PWR_EN` and `HAT_ID_EN`; VCCIO2 no longer carries OPA1622 EN, SD_MODE or RP SWD; VCCIO4 carries the PN7160 controls; VCCIO7 the MCLK and HP-rail enables). **Closed** in BOM v1.9 §4.2 | §1, §3 |
| B14 | BOM line 95 | The AXC translators' B side on HAT_3V3, so Ioff isolates them with the HAT unpowered. **Closed** in BOM v1.9 lines 94, 95 and power tree v0.3 | Feature blocks `blk.hat-audio` absent state |
| B15 | BOM line 12 note | BOOTSEL: N-FET to QSPI_SS (QSPI_IOVDD on RP_3V3); RUN with 4.7 kΩ to RP_IOVDD_1V8. **Closed** in BOM v1.9 line 12 | C6, C20 |
| B16 | Power tree §3 | `USB_AVDD1_3V3`/`USB_AVDD2_3V3` rail: vcc3v3_sys assumed, reference schematic source **UNVERIFIED**. **Closed** in power tree v0.3 §3 (rail still **UNVERIFIED** against the reference schematic) | CSV supply rows |

No new level shifter is needed: the master-clock and headphone-rail enables move to native 3.3 V balls, the TPM controls to native 1.8 V balls (the PN7160 controls too, until the reader was withdrawn on 2026-10-27), and the faceplate stays at 3.3 V on its own bank.

## 10. Open items

- 2026-10-26: RP2354A GPIO allocation recorded (§3 Coprocessor): `RP_UART_TX` GPIO0, `RP_UART_RX` GPIO1, `RP_IRQ` GPIO2, spare GPIO3, taps `I2S_BCLK`, `I2S_LRCK`, `I2S_SDO0`, `DSD_L`, `DSD_R` on GPIO4–GPIO8; notes of 1T19, 1R18, 1V20, 1U1, AP1, AN2, 1L2, AG2.
- 2026-10-25 (CRAFT-84): `DDR_CS0n_A`, `DDR_CS0n_B` and `DDR_RESETn` renamed `DDR_CS0_A_N`, `DDR_CS0_B_N` and `DDR_RESET_N` (B3, 1B5, 1C7); net names only.
- 2026-10-25 ([RFC 0014](https://github.com/opendap-project/rfcs/blob/main/text/0014-hat-interface-v2-usb-only.md), BOM v1.13): HATs are USB only. AG37 `HAT_DET_N` → `HAT_PD_INT_N` (HAT port controller interrupt, wake); 23 HAT GPIO balls → spares (§3 HAT table, spare table); the 10 CSI-2 and 6 PCIe PHY balls → `NC` (O2); 1A19 → eFuse #C IMON; I2C1 also carries the FUSB302B01MPX at 0x23; expander P01 → `HAT_VBUS_DISCH`, P16 → spare. Closes C1, C10 and gap G14; C8, C27, C28 and the HAT part of O13 no longer apply.
- 2026-10-24 (hats `standard/` interface v1.1, ADR 0005; BOM v1.11): A22 `HAT_DBG_SWCLK` → `HAT_EXT_SEL` (10 kΩ pull-down) and B22 `HAT_DBG_SWDIO` → `HAT_EXT_PD` (10 kΩ pull-up): the extension switch's select and power-down; SWD to the HAT becomes the bit-banged L2 alternate on `HAT_GPIO2` (SWCLK, 1P3) and `HAT_GPIO3` (SWDIO, 1P4); B26 `SOC_PCIE_PERST_N` → `SOC_EXT_SB0` (out of G14 as `HAT_EXT_SB0`), 1B13 `PCIE_CLKREQ_N` → `HAT_EXT_SB1`, A26 `PCIE_WAKE_N` → `HAT_EXT_SB2` (PCIe sideband in PCIe mode, GPIO in CSI-2 mode); the PCIe REFCLK, TX and RX balls go to port A and the CSI-2 balls to port B of the two TMUXHS4412 (CLK0 and D0–D2 in the first package, D3 in the second). `HAT_DET_N` (AG37) is unchanged and sits at position 33 of the single DF40C-100. No line-out ball was ever assigned here (the pin plan v0 §4.3 row stays as history), so nothing is removed. The faceplate interface is v1.0 (2026-10-24); contact positions unchanged; sources of contacts 40–46 follow BOM v1.11.
- 2026-10-25 (BOM v1.12, ADR 0021, ADR 0022): I2C0 carries the TPS62869 at 0x42 instead of the RK860-0 at 0x40 (AJ37, AK38; no ball change); `vdd_cpu` rows read 0.85–1.15 V with the remote sense to the TPS62869 VOS; the rank-1 outputs `LPDDR4_CS1n_A`/`_B`, `LPDDR4_CKE1_A`/`_B` and `LPDDR4_ODT1_CA_A`/`_B` (A3, 1A5, 1C3, 1A2, 1C2, 1A4) become `unused`, net `NC`, because both DRAM parts are single rank (closes O14).
- 2026-10-24: `MCLK_DIV_RUN` on GPIO4_C4, `WL_PWR_EN` on expander P06 and `WL_PDN_HOLD` on expander P07 through an SN74AXC1T45; GPIO2_B7 becomes a spare (was `WL_PDN`), its 0 Ω option to the translator output kept as a fallback. Closes BOM v1.9 items 39 and 40.

| # | Item | What closes it |
|---|---|---|
| O1 | I2C5 M1 on the HDMI DDC balls (C1) | First prototype (M-CORE). Fallback: `i2c-gpio` on the spare 3.3 V balls GPIO1_A3/A4 |
| O2 | Unused-ball and unused-PHY handling (eDP, HDMI, DSI1, CSI CLK1, the CSI-2 receiver and PCIe 2.0 (2026-10-25, RFC 0014), USB host 3, OTG0 ID, the DDR ball without an LPDDR4 function, spare GPIO) | Rockchip *RK3566_PinOut* (HDG p. 4), not retrieved; until then, supplies of unused PHYs are connected as the reference boards do |
| O3 | Rockchip IO Power Domain Checklist (HDG pp. 4, 31) | Retrieve and fill in from §1 |
| O4 | I2S1 RX on the TX clocks | HDG p. 69 states that SDI lines referring to one clock group use SCLKTX/LRCKTX by default, which supports it; the DNP links to GPIO4_A6/A7 stay until the first prototype |
| O5 | Native DSD on SDO1/SDO2 | v0 §3.4, unchanged |
| O6 | The Type 2EL 802.15.4 SPI (pins 4–8) is not connected; SPI2 M0 (GPIO2_C1–C4, VCCIO4) is kept free because it is the only 1.8 V SPI that reaches it | **Closed** by the decision of 2026-10-24 (BOM v1.9 item 4): the four balls stay unassigned spares reserved for a variant; no requirement asks for 802.15.4 and T1-077 keeps it disabled while it is not wired |
| O7 | GT911 address selected by INT low at reset | GT911 v09 timing figures (pp. 9–10) read as images |
| O8 | FH35C contact voltage rating against BL_LEDA (16.5 V) | RFC 0001 open question |
| O9 | Radio wake from standby | B4. **Power side closed** by the decision of 2026-10-24 (BOM v1.9 item 2, power tree v0.3 §6.5): the radio can stay powered in suspend while item tracking is enabled. Open: `WL_PWR_EN` on expander P06 to record in §3, and `WL_PDN` on a line that holds through standby (BOM §7 item 40) |
| O10 | Closed 2026-10-27 by withdrawal (the NFC reader removed). Was: PN7160 VEN back-powering if VEN is high while NFC_VBAT is off | Driver order (VBAT first, §10.5.2.1 of the PN7160 sheet per BOM line 127), plus the series-resistor footprint |
| O11 | NSC5083D ST pin rating at 3.3 V drive with MCLK_3V1 at 3.1 V or off | NDK datasheet |
| O12 | Type 2EL WL_WAKE_IN, IND_RST_WL/BT, SD_INT and wake polarity | Module datasheet (missing) |
| O13 | Which FSPI balls the BootROM drives (x1 or quad probe) | Scope capture on M-CORE; affects only `TPM_PIRQ_N` and `HAT_AUD_OE_N`. 2026-10-25: `HAT_AUD_OE_N` is removed; 1C15 is an unconnected spare (RFC 0014) |
| O14 | Rank count of the 4 GB LPDDR4X (CS1n, CKE1, ODT1 rows in the CSV) | **Closed** 2026-10-25 by [ADR 0022](../adr/0022-lpddr4x-micron-mt53e1g32d2fw-with-cxmt-second-source.md): both parts are single rank, so A3, 1A2, 1A4, 1A5, 1C2 and 1C3 are not connected (CSV) |
