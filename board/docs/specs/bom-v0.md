# BOM v0

- **Status:** Superseded by [BOM v1](bom-v1.md). Kept as history.
- **Date:** 2026-10-22
- **Sources:** the part datasheets listed in [BOM v1](bom-v1.md#datasheets).
- **Driver path:** *mainline + Debian* (enabled in Debian's kernel), *DKMS* (mainline driver Debian does not enable, or not in 7.2 yet; [blackbird-os ADR 0007](https://github.com/opendap-project/blackbird/blob/main/os/docs/adr/0007-kernel-modules-through-dkms.md)), *none* (no driver needed).

## Core

| # | Function | Part | Status | Driver path | Second source / note |
|---|---|---|---|---|---|
| 1 | SoC | Rockchip RK3566 | Decided (ADR 0003) | mainline + Debian | Upgrades: RK3576, i.MX 8M Plus |
| 2 | PMIC | Rockchip RK809 | Proposed | mainline + Debian (`rk8xx`) | RK817 |
| 3 | LPDDR4X 4 GB | Samsung K4UBE3D4AB-MGCL | Proposed | none (rkbin DDR blob ≥ v1.26) | SK hynix H9HCNNNCPMMLXR-NEE |
| 4 | eMMC 32 GB | Samsung KLMBG2JETD-B041 | Proposed | none | Micron, Kioxia, Longsys FORESEE |
| 5 | microSD socket | Hirose DM3AT-SF-PEJM5 | Proposed | none | Molex 104031-0811 |
| 6 | Coprocessor | Raspberry Pi RP2354A (RP2350 with flash) | Decided family (ADR 0004); part Proposed | none (flashed from Blackbird OS) | RP2350A + QSPI flash |

## Audio

| # | Function | Part | Status | Driver path | Second source / note |
|---|---|---|---|---|---|
| 7 | DAC ×2 (dual mono) | Cirrus Logic CS43198-CNZR | Decided family (ADR 0001); part Proposed | DKMS (`SND_SOC_CS43130` off in Debian) | None. DSD128 cap in the driver (blackbird-os ADR 0006) |
| 8 | Headphone amp ×4 | TI OPA1622IDRCR | Proposed | none | None |
| 9 | MCLK 44.1 kHz family | NDK NZ2520SDA, 45.1584 MHz | Proposed | none | Crystek CCHD-957 for prototypes. Confirm the catalog "45.158" label is 45.1584 MHz |
| 10 | MCLK 48 kHz family | NDK NZ2520SDA, 49.152 MHz | Proposed | none | Crystek CCHD-957 |
| 11 | 3.5 mm jack | Same Sky SJ2-35954D-SMT-TR | Proposed | none | SJ2-35894D-SMT-TR |
| 12 | 4.4 mm balanced jack | Pentaconn 4.4 mm (Nippon DICS) | Proposed | none | **Risk:** single source, at no distributor. G-Switch GT-3321667P-01 unverified |
| 13 | Speaker amp | ADI MAX98357AETE+T | Proposed | mainline + Debian | MAX98360A (same driver) |
| 14 | Speaker | Same Sky CMS-151125-078S-67 | Proposed | none | PUI AS01508MR-6-R |
| 15 | Microphones ×2 (main on faceplate, ambient-noise on the body) | Infineon IM73D122V01XTMA1 (PDM) | Proposed | mainline + Debian | Infineon IM72D128 |

## Power

| # | Function | Part | Status | Driver path | Second source / note |
|---|---|---|---|---|---|
| 16 | Charger / power path | TI BQ25895RTWR | Proposed | mainline + Debian | Newer: BQ25798 (needs a mainline entry + DKMS) |
| 17 | USB-PD controller | onsemi FUSB302BMPX | Proposed | mainline + Debian | Richtek RT1715 |
| 18 | Fuel gauge | ADI MAX17055EWL+T | Proposed | DKMS (`BATTERY_MAX17042` off) | TI BQ27Z561 |
| 19 | HAT power eFuse ×2 | TI TPS259470ARPWR | Proposed | none | TPS259472A / TPS259474L |
| 20 | Power mux | TI TPS2121RUXR | Proposed | none | — |
| 21 | Battery | Adafruit 328 (2,500 mAh, 9.4 Wh), off the shelf | Decided (ADR 0007) | none | Adafruit 2011 (2,000 mAh). NTC on the board. Safety reports to confirm for the Commercial edition |

## Connectivity and sensors

| # | Function | Part | Status | Driver path | Second source / note |
|---|---|---|---|---|---|
| 22 | Wi-Fi 6 + BT 5.4 (pre-certified) | Murata LBES5PL2EL-923 (Type 2EL, NXP IW612) | Proposed | DKMS (`nxpwifi` arrives in 7.3; `BT_NXPUART` off) | u-blox MAYA-W271-00B (same chip) |
| 23 | IMU | ST LSM6DSV16XTR | Proposed | mainline + Debian | LSM6DSOXTR (same driver and footprint) |
| 24 | Ambient light sensor | Vishay VEML6030 | Proposed | mainline + Debian | LTR-303ALS-01 |

## Connectors and protection

| # | Function | Part | Status | Driver path | Second source / note |
|---|---|---|---|---|---|
| 25 | Main USB-C (USB 2.0 OTG + PD) | GCT USB4105-GF-A | Proposed | none | Amphenol 12402012E212A. IP67 option for the Commercial edition: GCT USB4730-GF-A |
| 26 | USB ESD | TI TPD4E05U06DQAR | Proposed | none | Tech Public, MSKSEMI |
| 27 | CC/SBU protection | TI TPD8S300ARUKR | Proposed | none | — |
| 28 | HAT pogo pins (~128) | Harwin P70-1000045R | Proposed | none | Mill-Max 0906 (through-hole) |
| 29 | Faceplate FPC connector | Hirose FH35C family, with at least ~10 % spare contacts (part chosen with pinout v1) | Decided approach (ADR 0006) | none | Hirose FH26W family |

## Faceplate (touch)

| # | Function | Part | Status | Driver path | Note |
|---|---|---|---|---|---|
| 30 | Display | Focus LCDs E35GH-I-MW800-CB (3.5" 320×480 IPS, MIPI DSI) | Decided (faceplate-touch ADR 0001) | DKMS (mainline compatible, off in Debian) | Displaytech DT035CTFT-IPS-SHB-PTS |
| 31 | Touch controller | Goodix GT911 (on the display module) | Decided with the display | mainline + Debian | Best available touch technology (FPT-021) |
| 32 | Cover glass (lens) | The touch module's own cover lens or an off-the-shelf cover glass; a custom glass is the one allowed exception (T1-038) | Open | none | FPT-022 |

## Removed by decisions

- USB 3 switch and Type-C orientation mux for the main USB-C (BRD-044: USB 3 goes to the HAT only).
- Debug USB hub and USB-to-serial chip (BRD-046/047: console over CDC-ACM on the main USB-C, UART pads for early bring-up).
- PCIe switch (BRD-045: PCIe goes straight to the HAT).

## Known risks

1. Memory lifecycle (lines 3–4).
2. 4.4 mm jack single source (line 12).
3. Display: no production channel confirmed (line 30).
4. Battery safety reports to confirm for the Commercial edition (line 21).
5. Several drivers need DKMS until Debian enables them (lines 7, 18, 22).
