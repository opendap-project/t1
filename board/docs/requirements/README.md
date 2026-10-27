# Board requirements

Electrical and system requirements for the OpenDAP T1 main board.

| ID | Requirement | Priority | Status |
|---|---|---|---|
| BRD-001 | Every component shall have a Linux driver that Blackbird OS ships without a custom kernel: a mainline driver first, built as a DKMS module when Debian does not enable it; a vendor driver as a DKMS module only when mainline has none. A board device tree and overlays are acceptable. | must | Confirmed |
| BRD-002 | The SoC shall meet the project requirements without raising the product price significantly. | must | Confirmed |
| BRD-003 | The board shall be a general-purpose Linux platform, not a DAP-only design, able to serve the HAT ecosystem and on-board AI uses. | must | Confirmed |
| BRD-004 | The SoC shall reach every chip on the board directly, and every chip on an attached HAT through the HAT's USB port, for debugging, flashing and operation. | must | Confirmed |
| BRD-005 | Helper microcontrollers may assist and orchestrate, but shall never sit in a data path or limit capabilities. | must | Confirmed |
| BRD-006 | The HAT interface shall be one USB port (USB 3 SuperSpeed, USB 2.0 and CC with USB Power Delivery), wired directly from the SoC's USB controller and PHYs. | must | Confirmed |
| BRD-007 | The board shall include protection and safety mechanisms. | must | Confirmed |
| BRD-008 | The board shall power down specific hardware blocks when they are not in use. | must | Confirmed |
| BRD-009 | The board shall support a low-power mode. | must | Confirmed |
| BRD-010 | The board shall monitor CPU and temperature. | must | Confirmed |
| BRD-011 | The board shall provide a 3.5 mm and a 4.4 mm headphone output. | must | Confirmed |
| BRD-012 | The integrated mono speaker shall be driven independently of the DAC. | must | Confirmed |
| BRD-013 | The board repository shall own the specification of the flat cable that carries the HAT port (USB 3, USB 2.0, CC, VBUS and GND) from the board to the HAT case side. | must | Confirmed |
| BRD-014 | The board shall include a Raspberry Pi RP-series microcontroller as an orchestration coprocessor. The exact part is not fixed yet. | should | Confirmed |
| BRD-015 | Blackbird OS shall be able to flash and update the RP coprocessor. | must | Confirmed |
| BRD-016 | The board shall provide a MaskROM button for recovery flashing. | must | Confirmed |
| BRD-017 | The board shall provide a recovery key. | must | Confirmed |
| BRD-018 | The board shall provide USB-C OTG, so it can be flashed over USB. | must | Confirmed |
| BRD-019 | The SoC shall boot without the RP coprocessor firmware. | must | Confirmed |
| BRD-020 | The PMIC shall be the Rockchip RK809, the companion PMIC of the RK3566. | must | Draft |
| BRD-021 | Memory: 4 GB LPDDR4X and 32 GB eMMC. | should | Withdrawn |
| BRD-022 | The audio stage shall use two Cirrus Logic CS43198 DACs in dual mono, followed by six OPA1622 headphone amplifiers (both halves of one package in parallel on each balanced leg), sized for full-scale output into low-impedance headphones (ADR 0012). | must | Confirmed |
| BRD-023 | The audio stage shall have two master clocks, 22.5792 MHz and 24.576 MHz (44.1 kHz and 48 kHz families) at the CS43198's 1.8 V clock input, with the DAC as clock master, so every sample rate plays bit-perfect without resampling. | must | Confirmed |
| BRD-024 | The 3.5 mm output shall be single-ended and the 4.4 mm output balanced, on the 5-pole 4.4 mm connector of JEITA RC-8141C (the format known by the Pentaconn brand). The part is chosen in the BOM. | must | Confirmed |
| BRD-025 | Every radio (Wi-Fi, Bluetooth and any other) shall prioritize certified or pre-certified modules. | must | Confirmed |
| BRD-026 | The HAT port's VBUS shall be sourced through an eFuse and sunk through the power mux, with its power role, voltage and current set over USB Power Delivery. | must | Draft |
| BRD-027 | The microphone privacy LED shall be wired to the microphone power, so it cannot be lit independently of the microphone. | must | Draft |
| BRD-028 | The first intention is a single PCB carrying the SoC, the DAC chipset and the rest of the electronics (no system-on-module). Not final. | should | Confirmed |
| BRD-029 | The T1 shall have Wi-Fi and Bluetooth. | must | Confirmed |
| BRD-030 | The T1 should support item tracking over Bluetooth, in the style of an AirTag. | should | Confirmed |
| BRD-031 | An ambient-noise microphone shall sit at the top right of the device, in addition to the main microphone on the faceplate. | should | Confirmed |
| BRD-032 | The board shall include an IMU. | should | Confirmed |
| BRD-033 | PCIe on the board PCB is nice to have, not required. | should | Confirmed |
| BRD-034 | The main USB-C port shall support as much as possible: OTG, flashing, debugging, working with the device, file transfer, charging, and acting as a host when needed. | must | Confirmed |
| BRD-035 | The main / power button shall also be the boot-mode (MaskROM) button. | must | Confirmed |
| BRD-036 | The Action button shall be accessible to developers. | must | Confirmed |
| BRD-037 | Memory: 4 GB of RAM; storage 16 GB eMMC in production with 32 GB as a population option, prototypes 32 GB (ADR 0013). | must | Confirmed |
| BRD-038 | The T1 shall have an SD/TF card slot; the more storage, the better. | must | Confirmed |
| BRD-039 | The early serial console shall follow the same path as the main USB-C port. | must | Confirmed |
| BRD-040 | The board shall expose test pads on the I2S/DSD lines to the DAC, so the digital audio stream can be captured passively. | must | Confirmed |
| BRD-041 | The RP2350 shall be able to capture those lines passively (for example with PIO) and stream them to a host, without being in the data path. | should | Draft |
| BRD-042 | Nothing in the high-speed paths shall limit or interfere with the most the hardware can offer, and every function shall be offered in a standard way, with standard parts and protocols and no odd tricks. A standard switch or multiplexer is acceptable when it keeps the full rate with margin. | must | Confirmed |
| BRD-043 | Recovery flashing shall also work by booting from the SD/TF card, which then flashes the internal storage, besides MaskROM over the main USB-C. | must | Confirmed |
| BRD-044 | The single USB 3 lane shall go to the HAT only; the main USB-C carries USB 2.0 (OTG0: MaskROM, gadget, host) and USB-PD. | must | Confirmed |
| BRD-045 | PCIe shall go straight to the HAT. | must | Withdrawn |
| BRD-046 | Ideally everything goes through the main USB-C, including the serial console from as early in boot as possible: U-Boot and Linux expose a USB serial (CDC-ACM) console on it. | should | Confirmed |
| BRD-047 | UART test pads shall exist for bring-up of the earliest boot stages (BootROM, TPL/SPL), which cannot use USB. | must | Confirmed |
| BRD-048 | The board shall route enough dedicated signals to the faceplate for almost any display and touch connection standard, so that a change of display or touch part needs no board redesign. | must | Confirmed |
| BRD-049 | Power safety comes first: every rail, converter, connector and cable shall run with margin below its rating and shall be protected. A safer power design is preferred over a smaller or cheaper one. | must | Confirmed |
| BRD-050 | The battery path shall carry enough current for the full HAT and USB-C output budget on battery, with a more robust battery connection if the off-the-shelf lead or connector cannot. | must | Confirmed |
| BRD-051 | The microSD/TF slot shall run in the fastest mode the SoC supports, for performance: UHS-I SDR104 on the RK3566 (SD 3.0), with 1.8 V signalling. | must | Confirmed |
| BRD-052 | Both headphone jacks shall detect plug insertion and removal, so playback can pause when headphones are unplugged and never move to the speaker unasked. | must | Confirmed |
| BRD-053 | The board shall support assembly variants: prototypes populate every option to validate the full functionality, and production variants may leave optional parts unpopulated (DNP) or fit lower-cost equivalents on the same footprint, without a board respin. Every optional part is marked as such in the BOM, with its variant. | must | Confirmed |
| BRD-054 | The main board may use every technique that gets the most from the device: HDI (laser microvias, via-in-pad), both sides populated, as many inner layers as the routing and signal integrity need, and shielding cans. | must | Confirmed |
| BRD-055 | Every board, flat cable (FPC and rigid-flex) and assembly shall be producible as a prototype within the published processes of the prototype fab (fabrication, HDI, flex, stencils, SMT and BGA assembly) that the kicad-lib fab rule sets implement. | must | Confirmed |
| BRD-056 | Every other button of the T1 should be accessible to developers too (split from BRD-036). | should | Confirmed |
| BRD-057 | The T1 should have NFC, for tap-to-pair and tap-to-hand-off with the listener's other devices. | should | Confirmed |
| BRD-058 | The T1 should have a haptic actuator, for eyes-free confirmation of actions. | should | Confirmed |
| BRD-059 | The T1 should have a hardware key holder for the keystore (OS-032), so device and pairing keys are protected even from root. | should | Confirmed |
| BRD-060 | The board shall have a PCB design-constraints specification derived from the product, part and fab requirements, and its own design rules composed on top of the fab's, so DRC enforces every constraint a tool can check. | must | Confirmed |
| BRD-061 | The antennas should keep Wi-Fi and Bluetooth working in an anodised-aluminium case (CASE-022) as well as in the polymer case, without a board respin. Every radiator, feed and tuning part shall live in the main body (board and case core), never in the faceplate, so any faceplate works with any radio configuration. The preferred antenna zone is the core's frame (top or side walls) and the board's own edge; the back cover is a last resort, because a HAT case replaces it and a HAT, possibly metal, would cover or detune the antenna. HATs keep the antenna keep-out. | should | Confirmed |

## Open questions

- Exact DAC part.

## Context

- BRD-033 (2026-10-25, maintainers): PCIe stays unwired on the v1 board. A possible radio variant with a PCIe + USB 2×2 module keeps its SoC resources reserved: the PCIe sideband balls B26, 1B13 and A26 (`RSVD_PCIE_PERST_N`, `RSVD_PCIE_CLKREQ_N`, `RSVD_PCIE_WAKE_N`) and USB 2.0 HOST3, all unconnected; the 16 PCIe and CSI PHY balls stay unconnected ([pinout v1](../specs/pinout-v1.md)). Fitting such a module is a `blk.radio` revision.
- BRD-006, BRD-013 and BRD-026 reworded on 2026-10-25 to the maintainers' decision that HATs are USB only and that HAT power follows USB Power Delivery ([hat-standard ADR 0006](https://github.com/opendap-project/hat-standard/blob/main/docs/adr/0006-hats-are-usb-only.md), [RFC 0014](https://github.com/opendap-project/rfcs/blob/main/text/0014-hat-interface-v2-usb-only.md)). The physical HAT connector is still open, so BRD-013 names the flat cable's content, not its connectors. BRD-042 has no HAT switch left to govern.
- BRD-042 reworded on 2026-10-24 to the maintainers' intent: the rule was never "no switches" but "nothing that ends up limiting or interfering with the maximum we can offer, offered in a standard way without odd tricks". The earlier wording set aside a USB 3 switch to the main USB-C and a debug USB hub; those choices stand on their own merits (USB 3 to the HAT only, BRD-044), not on this rule.
- BRD-061 (maintainers, 2026-10-24): nice to have; the faceplate exclusion and the back-cover preference were set the same day. Preferred: a non-metallic top end cap with the listed Molex 146153-0050; kept open on the board: the aluminium frame as antenna, fed through a spring contact. The board holds PCB-R-08 to PCB-R-13; [ADR 0018](../adr/0018-antennas-and-certification-route.md), note of 2026-10-24.
- BRD-001, BRD-022, BRD-024, BRD-037 (2026-10-24). BRD-001 is reworded to what Blackbird OS already decided: no custom kernel (OS-002), mainline drivers Debian does not enable ship as DKMS modules ([blackbird-os ADR 0007](https://github.com/opendap-project/blackbird-os/blob/main/docs/adr/0007-kernel-modules-through-dkms.md)), vendor drivers as DKMS modules only when mainline has none ([ADR 0008](https://github.com/opendap-project/blackbird-os/blob/main/docs/adr/0008-vendor-linux-drivers-allowed.md)); a changed kernel configuration is not an option. BRD-024 names the standard instead of a brand: Pentaconn is Nippon DICS's brand for the JEITA RC-8141C 4.4 mm connector, and the BOM primary is the G-Switch GT-3321667P-01 (its RC-8141C contact layout is still **UNVERIFIED**, BOM line 31). BRD-022 and BRD-037 move to Confirmed because their ADRs (0012, 0013) are Accepted. BRD-020 stays Draft while the RK809-5 is Proposed in the BOM.
- BRD-060 (maintainers, 2026-10-24): constraints with limits, maximum and minimum values, and an own DRC complementing the fab's that fits the project's quality requirements. Specification: [`../specs/pcb-design-constraints.md`](../specs/pcb-design-constraints.md). Priority confirmed by the maintainers on 2026-10-24.
- BRD-057 to BRD-059 parts (2026-10-23): [BOM v1.7](../specs/bom-v1.md) lines 122–128: TPM 2.0 SLB9673 (key holder), DRV2605L with a coin LRA (haptics), an NTAG I2C plus dynamic tag for tap-to-pair and the PN7160 reader as a population option for T1-to-T1 hand-off.
- BRD-059 (maintainers, 2026-10-23): there is no mainline OP-TEE on the RK3566 and a read-only OTP ([RFC 0004](https://github.com/opendap-project/rfcs/blob/main/text/0004-opendap-protocol.md) §5), so the keystore needs a chip of its own to be hardware-backed. Direction: a discrete TPM 2.0 (SPI or I²C), the most standard choice on Linux: mainline drivers `tpm_tis_spi` and `tpm_tis_i2c`, and the standard user-space stack (`tpm2-tss`, PKCS#11, systemd). Secure elements (for example NXP SE050, Microchip ATECC608) and the RP2350 are the alternatives. Part and bus to be chosen in the BOM (BRD-053).
- BRD-057, BRD-058 (maintainers, 2026-10-23): yes, as soon as suitable parts are available; the short pairing code stays the baseline without NFC.
- BRD-004 reworded on 2026-10-25 as a consequence of the maintainers' decision that HATs are USB only ([RFC 0014](https://github.com/opendap-project/rfcs/blob/main/text/0014-hat-interface-v2-usb-only.md), hat-standard ADR 0006): the HAT connector carries no native lines, so the SoC reaches a HAT's chips through the HAT's USB port. Flashing and debugging go over USB (DFU, a ROM USB loader or a CMSIS-DAP function on the HAT), as hat-standard HCS-013 and HCS-031 require; [RFC 0015](https://github.com/opendap-project/rfcs/blob/main/text/0015-hat-connector-pogo-field-and-usb-c-port-hat.md) records the HAT connector that carries it.
- BRD-004 and BRD-005 govern the T1 main board. HAT hardware follows the HAT standard's HCS-013 (every programmable HAT chip flashable and debuggable from Blackbird OS) and HCS-031 (firmware recoverable over USB, interface v2 §8).
- Priorities revised on 2026-10-22: BRD-014 (RP2354A coprocessor), BRD-031 (ambient-noise microphone) and BRD-032 (IMU) are should and become population options (BRD-053). BRD-014 holds as should only while no must function depends on the coprocessor; the pin plan currently routes wake lines to it, so those move to the SoC or the expander before the coprocessor can be left unpopulated. BRD-036 split into BRD-036 (must) and BRD-056 (should).
- BRD-054, BRD-055 (maintainers, 2026-10-22): HDI and advanced build-ups are welcome as long as they stay within the prototype fab's published processes. The fab rules live in kicad-lib (KLIB-002), one rule set per fab process (`pcbway-*`).
- BRD-053 (maintainers, 2026-10-22): prototypes populate everything to validate it; production variants may omit optional parts. Optional parts are designed in as population options from the start.
- BRD-051: UHS-II (SD 4.0) needs a second row of contacts and SoC support the RK3566 does not have (RK3568 datasheet Rev 1.0, p. 8: SD 3.0, 4-bit). The board already provides the switchable 1.8/3.3 V VCCIO3 and 1.8 V-rated ESD for SDR104 (BOM lines 11, 73).
- BRD-020 to BRD-027: Adopted from the earlier experiments on 2026-10-21 as **Draft**: consistent with the decisions already taken and with the product philosophy, pending the maintainers' confirmation. Parts are checked against T1-010.
- Experiment parts worth evaluating: charger BQ25895 (or BQ25792, which can also source power to a powerbank HAT; the T1 now uses the 2S BQ25798 charger and BQ28Z610-R1 gauge, [ADR 0014](../adr/0014-two-cell-battery.md)), fuel gauge BQ27Z561, power-path TPS2121, USB-PD FUSB302B, HAT eFuse TPS25947, radio module Murata Type 2EL (NXP IW612; its mainline driver status must be verified), coprocessor variant RP2354B (RP2350 with in-package flash).
- The experiments split the electronics into a compute module (8-layer HDI), an audio module and a base board. Not adopted: the first intention is a single PCB (see the last requirement).
- Withdrawn on 2026-10-21: BRD-021. Withdrawn on 2026-10-25: BRD-045 (HATs are USB only, RFC 0014).
- BRD-016 (MaskROM button) is met by the main / power button (BRD-035).
- Pending: deep suspend on the RK3566 (see `blackbird-os`).
- High-speed I/O topology: a USB 3 switch to the main USB-C and a debug USB hub were set aside by the "no unusual switches or tricks" rule. Early serial console: USB serial (CDC-ACM) on the main USB-C from U-Boot onward, plus UART test pads for the earliest stages.
- Candidate signal set for the faceplate connector, to validate against the RK3566 pin multiplexing (some display interfaces share pins with audio and other peripherals): MIPI DSI 4-lane, parallel RGB, SPI/DBI, I2C and interrupt/reset lines for touch, PWM backlight control and enable, and the usual panel supply rails.
- BRD-023 corrected on 2026-10-22: the CS43198 datasheet only accepts a 22.5792 or 24.576 MHz external master clock at 1.8 V; the earlier 45.1584 / 49.152 MHz figures came from the experiments and were wrong.
