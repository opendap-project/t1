# T1 electronics integration and verification

- **Status:** Draft v0.1 (2026-10-24): specialised modules per domain are built, provided the integration is verified as well and never inferred from the parts.
- **Updated 2026-10-25 ([RFC 0014](https://github.com/opendap-project/rfcs/blob/main/text/0014-hat-interface-v2-usb-only.md), [RFC 0015](https://github.com/opendap-project/rfcs/blob/main/text/0015-hat-connector-pogo-field-and-usb-c-port-hat.md)):** HATs are USB only (hat-standard interface v2): M-HAT, the interaction matrix, V2-P02, V2-H01, V2-H02 and V3-07 cover one USB port with USB PD through the DF40C-50, the flat cable and the 2 × 10 pogo field; the PCIe, CSI-2, DLN2-on-the-board, I2S, power-class and `HAT_3V3` items are gone.
- **Method:** this spec applies the OpenDAP electronics integration and verification method to the T1: integration levels L0–L6, domain modules with rules M1–M4, an interaction matrix, evaluation rows and gates between levels. This file holds the T1's modules, its interaction matrix, its evaluation rows and how its gates apply.
- **Levels:** `[Qn]` after a row ID is the RFC 0010 quality level at which the row becomes mandatory; a row without it is Q1. Compliance rows follow T1-071 to T1-086.
- **Scope:** the T1's electronics, from parts to the assembled product. Case, mechanical and physical-simulation work is out of scope; the levels that need it (L5, L6) list only their electrical evaluations.

## 0. Principles

Five principles apply:

1. **Parts passing does not make the whole pass.** An interaction between two domains is signed off only at the lowest level that reproduces its physical mechanism (conduction, proximity, shared ground, shared clock, heat, software timing). A mechanism that a level cannot reproduce is marked there as *not representative*, never as passed.
2. **What is tested is what ships.** Every module is built from the same hierarchical schematic sheets as the main board, and its layout block is copied from or into the main board's, with the same stackup class, part numbers and values (rule M4).
3. **Every row traces to a requirement or a constraint** and carries the three thresholds where the metric has them.
4. **Regression follows the dependency graph.** A change to a block reruns its L1 and L2 rows and every L3 and L4 row of each interaction it takes part in (§3).
5. **Measurement before shrinking.** A level's exit gate is evidence (data file, capture, photo), stored with the component that was tested; a result without evidence counts as not run.

For the T1, the IDs a row names are T1-, BRD-, PCB-, ADR and BOM §7 items, and the thresholds are those of T1-048 (ideal, warning, hard limit).

## 1. Integration levels

Each level integrates more of the product: L0 one part against its datasheet, L1 one circuit block, L2 one domain on its own test board, L3 two or more modules connected through the core module (conducted coupling, protocol, sequencing; not proximity, radiated or thermal coupling), L4 the integrated main board, L5 the product assembly in the case, L6 the product in use. Each level's exit gate is that every row of the level passes with evidence. For the T1:

| Level | T1 specifics |
|---|---|
| **L0 Part** | parts-lib sheet, kicad-lib symbol/footprint, fab rule test boards; lifecycle and second source recorded per PLIB-003 |
| **L1 Block** | board `sim/` studies |
| **L2 Domain module** | Module boards of §2; the bench items of BOM §7 |
| **L3 Domain pair** | Module stack of §2.2 |
| **L4 Integrated board** | Main board (prototype 1) with faceplate and HAT device-side piece on the bench; lives in board |
| **L5 Product assembly** | Board, faceplate, battery pack and HAT piece in the case; lives in t1 |
| **L6 Product in use** | The T1 running Blackbird OS through real sessions; lives in t1 and toolkit-verify. Autonomy (T1-039), endurance and scale (T1-046, T1-047), experience budgets (T1-048), compliance pre-scans |

## 2. Domain modules (L2) and the module stack (L3)

### 2.1 Modules

| Module | Contents (BOM v1.7) | Main questions it answers | IDs |
|---|---|---|---|
| **M-CORE** | RK3566, LPDDR4X, eMMC, RK809-5, RK860-0, 24 MHz crystal, boot and MaskROM circuit, USB-C OTG0 for flashing, UART pads | HDI stackup and BGA escape; LPDDR4X at full speed; PMIC power-up defaults (measured on the module); SoC power by mode, the measurement t1 ADR 0003 waits for; MaskROM and eMMC timing | BRD-001, BRD-016, BRD-019, BRD-035, BRD-043, BRD-047; PCB-S, PCB-G-02/03, PCB-I-05/06 |
| **M-PWR** | 2S battery path, BQ25798, BQ28Z610-R1, TPS2121, FUSB302B + USB-C, TPS62136, TPS62903 5.1 V, eFuses ×3 (#A HAT, #C USB-C, #D shared limiter), fuse, ship FET, protections | Charging and power path across sources; full output budget on battery; converter stability (§7.27), thermal (§7.24); VBUS surge; eFuse limits and inrush | BRD-007, BRD-026, BRD-049, BRD-050; ADR 0014; PCB-P |
| **M-AUD** | 2 × CS43198, 6 × OPA1622, TPS65131, LMR33630C, LT3045/LT3094 pairs, AUDIO_2V2, master clocks and attenuator, both jacks with detection, output networks | Noise floor, distortion, output power and impedance, channel balance, pops at every transition, rail and clock behaviour; BOM §7.1, §7.29–§7.31 | BRD-011, BRD-022 to BRD-024, BRD-052, T1-049, T1-050, ADR 0010, 0012, 0015; PCB-A |
| **M-RF** | Murata Type 2EL, U.FL ×2, matching networks, antennas | Throughput and range per band, Bluetooth audio, coexistence; adherence to Murata's reference design (pre-certification) | BRD-025, BRD-029; PCB-R |
| **M-UI** | Board side of the faceplate interface: FH35C, backlight driver, LP5521, level shifting; with the touch faceplate prototype | DSI 1-lane bring-up, touch over I2C, HID-over-I2C controls, LED, PDM microphone | T1-018, T1-036, BRD-048; faceplate interface v0 |
| **M-IO** | RP2354A, buttons, IMU, DRV2605L + LRA, NTAG / PN7160, SLB9673 TPM, MAX98357A + speaker, microSD (SDR104) | Coprocessor flashing from the SoC; button behaviour with the screen off; peripherals on mainline or DKMS drivers; SD at SDR104 | BRD-014, BRD-015, BRD-036, BRD-051, BRD-056 to BRD-059, T1-060 |
| **M-HAT** | HAT port controller (FUSB302B01MPX) and `VBUS` source and sink paths, DF40C-50 pair, flat cable, device-side piece with the 2 × 10 pogo field (Mill-Max 0965) and its ESD, a test HAT: USB 3 Gen 1 and USB 2.0 loopback or test device, a USB PD sink and a USB PD source (powerbank role), the identity capability | Signal integrity at 5 Gb/s through DF40, FPC and pogo pins (hat-standard ADR 0004 coupon); USB PD roles, attach and detach, `VBUS` limits and discharge, 5 V only from a HAT; identity read over USB; HAT firmware recovery over USB | BRD-004, BRD-006, BRD-013, BRD-026, BRD-044, BRD-049; hat-standard interface v2 |
| **M-SI** | Impedance and loss coupons of the main-board HDI stackup and of the two flat cables | Impedance per class (TDR), loss, microvia reliability (cross-section) | PCB-I-01 to PCB-I-07, PCB-S |

Module rules: **M1** each module is a KiCad project built from the same hierarchical sheets as the main board; **M2** the core module uses the main board's stackup and fab process, and a module whose performance depends on the ground and plane arrangement keeps the main board's arrangement under its block; **M3** modules connect to the core module through one documented module connector per boundary, whose map is a machine-readable interface file checked against the main-board netlist; **M4** after the main board is laid out, a module whose layout block differs is updated and re-tested, or its L2 results are marked *superseded by L4*. For the T1: M-CORE uses the main board's stackup and fab process (M2); M-AUD keeps the main board's ground and plane arrangement under the audio block (M2); the module connector maps are interface files checked against the main-board netlist (M3).

### 2.2 Module stack (L3)

M-CORE is the hub: every other module attaches to it, so pairs and the full stack run real Blackbird OS. M-PWR powers the stack through the same rails as on the board. The stack is representative for conducted effects through its defined interconnect only; every proximity, radiated or thermal interaction is first signed off at L4.

## 3. Interaction matrix

Each cell names the coupling mechanism, the level where it is first testable, and the level where it is signed off (the lowest level that reproduces the mechanism). Domains: PWR (power and charging), CORE (SoC, memory, storage), AUD (DAC, amplifiers, clocks, jacks), RF (radio), UI (faceplate), HAT, IO (coprocessor and peripherals), EXT (USB-C and the outside world).

| | CORE | AUD | RF | UI | HAT | IO | EXT |
|---|---|---|---|---|---|---|---|
| **PWR** | Load transients of DVFS on VSYS_LV and vdd_cpu; sequencing; suspend and wake. First L3, signed off L4 | Converter ripple and PFM bursts into the amplifier rails and DAC supplies (PSRR budget, §7.31); ground return of the switchers. First L3 (conducted), signed off L4 (proximity) | Switching harmonics in the radio bands (desense). L4 | Backlight current steps on VSYS_LV. L3 | HAT inrush and fault on the shared 5.1 V converter and its shared limiter; a source HAT under USB PD; dead-battery charge from a HAT. L3, signed off L4 | Haptic and speaker current pulses. L3 | Source switching, PD negotiation, surge and ESD on VBUS. L2, signed off L5 |
| **CORE** | | I2S/DSD timing, DAC as clock master, bit-perfect paths, sample-rate changes without pops. First L3. DDR and SoC noise coupling into analog: L4 | DDR and SDIO harmonics into the radio bands; SDIO timing. L3 (protocol), L4 (desense) | DSI timing, touch interrupt latency against the experience budgets. L3 | USB 3 link training through the cable and pogo field; enumeration, identity capability, remote wakeup. L3, signed off L4 | I2C bus loading and addresses; coprocessor flashing (BRD-015). L3 | USB OTG roles, MaskROM recovery, USB serial console (BRD-046). L3 |
| **AUD** | | | Radio bursts (TDMA, BT) demodulated in the amplifiers: audible buzz. L4, signed off L5 | Display and backlight noise into the headphone path. L4 | A USB audio HAT on its own clock (no shared clock with the DACs); ground return of HAT `VBUS` current near the audio reference. L3, signed off L4 | Speaker amplifier and haptics against the headphone path; jack detect and speaker never chosen unasked (T1-053). L3 | Ground loops when USB-connected to a computer (USB DAC mode, T1-054). L4, signed off L5 |
| **RF** | | | | Faceplate and display as antenna loading. L5 | HAT shielding and metal near the antennas. L5 | NFC field against nearby metal and the TPM I2C. L4 | Antenna in the enclosure; certification adherence. L5 |
| **UI** | | | | | — | Buttons and faceplate controls agree (one press, one action). L3 | ESD into the faceplate through the cover. L5 |
| **HAT** | | | | | | — | ESD and hot-plug at the pogo field. L4, signed off L5 |
| **IO** | | | | | | | ESD at the side buttons and the microSD slot. L5 |

## 4. Evaluation matrices

Row IDs: `V0-nn` (L0), `V1-nn` (L1), `V2-<module letter><nn>` (L2), `V3-nn` (L3, with the pair named), `V4-nn` (L4), `V5-nn` and `V6-nn` (L5 and L6); at L4 every L2 and L3 row is repeated on the board. Columns: `ID | case | steps | expected (with thresholds) | observed | evidence`. The tables below fix the cases and their expected values; *observed* and *evidence* are filled when the level runs, stored next to the module or board that was tested. Thresholds come from the requirement, the ADR or the constraint named; where none exists yet, the case says what sets it.

### 4.1 L0 Part

| ID | Case | Expected |
|---|---|---|
| V0-01 | Footprint against the manufacturer's drawing (pads, courtyard, pin 1, 3D model height) | Matches; reviewed by a second reading |
| V0-02 | Symbol pin map against the datasheet pin table | Matches; Manufacturer and MPN fields (PCB-T-05) |
| V0-03 | Lifecycle and second source recorded | PLIB-003, T1-028, T1-029 |
| V0-04 | Simulation model available and its hash recorded | `odapkit sim fetch` succeeds or the block's checks are marked blocked |

### 4.2 L1 Block

| ID | Case | Expected |
|---|---|---|
| V1-01 | Converter stability over line, load and temperature corners | Phase margin ≥ 45° (board sims), peak currents ≤ 80 % continuous and ≤ 100 % at a limiter trip (BRD-049) |
| V1-02 | MaskROM entry and normal boot over corners | `sim/maskrom` checks |
| V1-03 | Master clock levels, duty and edges into the CS43198 | `sim/mclk-attenuator` checks |
| V1-04 | Headphone stage at full scale into 16 and 32 Ω, both outputs | ADR 0012 and 0015 figures; rail headroom |
| V1-05 | Every block reviewed against its datasheet application circuit | Checklist item per part, deviations justified |

### 4.3 L2 Domain modules

| ID | Module | Case | Expected |
|---|---|---|---|
| V2-C01 | M-CORE | Power-up sequence captured on every rail | Matches the RK809-5 defaults recorded for the board; rails within RK3566 recommended ranges |
| V2-C02 | M-CORE | LPDDR4X memory test at the highest supported rate, hot and cold | No errors over the test duration; eye or margin data where the SoC exposes it |
| V2-C03 | M-CORE | eMMC HS200 and boot; MaskROM and SD recovery | BRD-016, BRD-043; boot every time over 100 power cycles |
| V2-C04 | M-CORE | SoC and memory power per mode (idle, playback-equivalent load, suspend) | Feeds the battery-life model; T1-039 thresholds evaluated with the measured draw |
| V2-C05 | M-CORE | Impedance coupon on the same panel | PCB-I classes within the fab's ±10 % or the standard's window |
| V2-P01 | M-PWR | Charge from USB-C PD and from a HAT source, every transition | No brown-out of VSYS_LV; TPS2121 interlock holds (power tree finding 10) |
| V2-P02 | M-PWR | Full output budget on battery: 5.1 V source 1.5 A (HAT `VBUS` or USB-C) + headphone full scale | VSYS ≥ 6.6 V shed point respected; every part within 70–80 % of its rating (BRD-049, BRD-050) |
| V2-P03 | M-PWR | Converter load steps and Bode plots | Phase margin ≥ 45°, closes BOM §7.27 |
| V2-P04 | M-PWR | eFuse limits, short circuit, inrush with 470 µF | ILIM within the RILM tolerance; no upstream disturbance |
| V2-P05 | M-PWR | VBUS surge and ESD at the connector | No damage; downstream absolute maxima respected (power tree risk 5) |
| V2-P06 | M-PWR | Thermal at the full budget, 30 min | Part temperatures within ratings with margin (BRD-049); measured, not simulated |
| V2-A01 | M-AUD | Noise floor, both outputs, into 16 Ω and 32 Ω and open | Sets the T1-048 thresholds (experience budgets §Audio output) from ADR 0012's design figures |
| V2-A02 | M-AUD | THD+N and output power versus level and load | ADR 0012 and 0015 figures |
| V2-A03 | M-AUD | Output impedance | ≤ 0.5 Ω ideal, > 2 Ω hard limit (experience budgets) |
| V2-A04 | M-AUD | Channel balance at low volume, volume step | ≤ 0.1 dB ideal / > 1 dB hard; ≤ 0.5 dB step (T1-050) |
| V2-A05 | M-AUD | Pops at power, play, pause, seek, rate change, PCM/DSD change, output change, gain change, plug and unplug | None audible (T1-049); measured peak at the jack recorded |
| V2-A06 | M-AUD | Both clock families, every sample rate, PCM and DSD | Bit-perfect (OS-020); DAC locked; no resampling (BRD-023) |
| V2-A07 | M-AUD | Boost, inverter and LDO bench items | Closes BOM §7.29–§7.31 |
| V2-R01 | M-RF | Throughput, range and Bluetooth audio stability per band, shared and dedicated antenna configurations | The Radio targets of the [experience budgets](experience-budgets.md#radio); the measured configuration decides board ADR 0018's production choice |
| V2-R02 | M-RF | Layout against Murata's reference design | No deviation (BRD-025) |
| V2-U01 | M-UI | Display at full frame rate, touch report rate and latency | T1-056 and the experience budgets |
| V2-U02 | M-UI | Faceplate identification, controls over HID, LED states | Faceplate interface v0, controls and status LED spec |
| V2-I01 | M-IO | Coprocessor flashed and updated from the SoC; SoC boots without it | BRD-015, BRD-019 |
| V2-I02 | M-IO | microSD at SDR104 | BRD-051; sustained read rate recorded |
| V2-I03 | M-IO | Every peripheral bound by its mainline or DKMS driver | BRD-001 |
| V2-H01 | M-HAT | USB 3 Gen 1 and USB 2.0 through DF40C-50, FPC and pogo field: eye or link margin, error rate | hat-standard ADR 0004 coupon criteria |
| V2-H02 | M-HAT | USB PD on the HAT port: sink HAT at Default and 1.5 A, source HAT at 5 V, power-role swap, dead battery, attach and detach, `VBUS` discharge to vSafe0V, eFuse #A and #D trips, OV2 above vSafe5V | Interface v2 §5–§6; never sources and sinks at once (OV2 interlock); 5 V only accepted; BRD-026, BRD-049 |
| V2-S01 | M-SI | TDR per impedance class, microvia cross-section | PCB-I targets; the fab's acceptance class |

### 4.4 L3 Domain pairs

| ID | Pair | Case | Expected |
|---|---|---|---|
| V3-01 | PWR + CORE | DVFS and load steps from the SoC with the real converters | VSYS_LV and vdd_cpu within range; no reset |
| V3-02 | PWR + CORE | Suspend, resume, shutdown, battery cut-off, ship mode | Resume state kept (T1-051); no rail left floating |
| V3-03 | PWR + AUD | Converters running at worst load while measuring V2-A01 and V2-A02 | No degradation beyond the L2 values; spurs listed with their frequency (upper bound for L4) |
| V3-04 | CORE + AUD | Playback of every rate and format from Blackbird OS; rate changes; pause and seek | Bit-perfect; no pops (T1-049); latency within T1-057 budgets |
| V3-05 | CORE + RF | Wi-Fi and Bluetooth under SDIO and DDR load | Throughput within 10 % of V2-R01 **UNVERIFIED** threshold |
| V3-06 | CORE + UI | Interface at full frame rate during library scan and DSD playback | T1-056 |
| V3-07 | CORE + HAT | USB 3 and USB 2.0 devices on the test HAT, identity read, a HAT chip reflashed over USB (DFU), remote wakeup, hot-plug | Links train at full rate; no error growth over 1 h; identity verified before the HAT's software loads; recovery with no working HAT firmware (HCS-031) |
| V3-08 | CORE + IO | Every I2C peripheral on its bus at once; coprocessor flashing during playback | No bus errors; audio unaffected |
| V3-09 | Full stack | Blackbird OS running every domain at once for 24 h | No resets, no driver errors, no memory growth (T1-047) |

### 4.5 L4 Integrated board

Every L2 and L3 row is repeated on the board (the L2/L3 values become the reference), and these are added:

| ID | Case | Expected |
|---|---|---|
| V4-01 | Audio noise and THD+N with every other domain active (radio transmitting, display on, HAT loaded, charging) | Within the T1-048 thresholds set at L2; no spur above the warning value |
| V4-02 | Radio sensitivity with the board's own noise (desense), per band, in both antenna configurations | Desense ≤ the budget set at L2; the Radio targets of the experience budgets still met on the board |
| V4-03 | Thermal map at the full budget and at playback | Measured part temperatures; data handed to the out-of-scope thermal work |
| V4-04 | Power by use case on the board | Updates the battery-life model; T1-039 evaluated |
| V4-05 [Q2] | ESD at every connector on the bare board | ±4 kV contact, ±8 kV air (IEC 61000-4-2): no damage, criterion B |
| V4-06 | USB DAC mode connected to a computer | Bit-perfect, no added noise (T1-054); ground-loop noise recorded |
| V4-07 [Q2] | Near-field scan and radiated pre-scan, every domain active; spread spectrum on and off; harmonics of every switching frequency listed against the radio bands | Peaks recorded; no harmonic in a radio channel above the desense budget of V4-02 |
| V4-09 [Q2] | Conducted transmit power per band, rate and regulatory domain with the shipped driver and firmware | At or below Murata's certified values for each domain (T1-075) |
| V4-10 [Q2] | Maximum wide-band output voltage per EN 50332-2 on each output, gain and load; 1 kHz full-scale sine for reference | Recorded; sets the dose calibration (T1-072, T1-074) |
| V4-11 [Q2] | Battery single faults: charger misprogrammed, pack NTC open and shorted, cell imbalance, output short | Cell limits never exceeded; the PCM or charger hardware stops each fault (T1-086) |
| V4-12 [Q3] | HAT and USB-C source outputs with the eFuse shorted | Available power after 3 s ≤ 15 W (PCB-P-11) |
| V4-13 [Q2] | USB Type-C and PD with a PD analyser: 5 V and 9 V sink, 5 V 1.5 A source, dead battery, OS not running, hot plug, legacy and non-PD chargers | Charges in every case; no back-feed (T1-081) |

### 4.6 L5 Product assembly and L6 in use (electrical rows only)

| ID | Level | Case | Expected |
|---|---|---|---|
| V5-01 | L5 | Radio range, throughput, latency and Bluetooth dropouts in the case, on body and through walls, on the radio courses of the experience budgets (LOS, W1, W2, BODY, COEX) | The Radio targets of the experience budgets; each must also beat the measured benchmark median |
| V5-02 [Q2] | L5 | ESD at the product surface (cover, buttons, jacks, USB-C) | ±4 kV contact, ±8 kV air, criterion B; no audible event beyond a recovery |
| V5-03 | L5 | Audio rows of L4 with the final jacks and ground | No change beyond measurement repeatability |
| V6-01 | L6 | Core audiophile session autonomy | T1-039: > 12 h ideal, < 8 h warning, < 6 h hard limit |
| V6-02 | L6 | Endurance and scale | T1-046, T1-047, experience budgets |
| V6-03 [Q2] | L6 | Compliance pre-scans repeated on each release candidate in the V5-04 configurations | No regression beyond 2 dB from the last pass |
| V5-04 [Q2] | L5 | Radiated emissions pre-scan in the case, 30 MHz–6 GHz: no HAT, representative HAT, charging, USB device mode, playback on both jacks, radios transmitting | ≥ 6 dB below FCC 15.109 / CISPR 32 Class B in every configuration |
| V5-05 [Q2] | L5 | Headphone output during ESD at every discharge point, with a sensitive IEM load (±8 / ±15 kV at Q4) | No transient above the RS2 equivalent (value set with the lab) |
| V5-06 [Q2] | L5 | RF exposure pre-assessment with and without the representative HAT | Below the FCC, EU and ISED limits with margin; fixes PCB-R-05 (T1-076) |
| V5-07 [Q2] | L5 | Radiated spurious emissions of the radio in the case | ≥ 6 dB margin |
| V5-08 [Q2] | L5 | Surface temperatures in the worst case of T1-083, 2 h at 25 °C | Within the IEC 62368-1 TS1 limits |
| V5-09 [Q3] | L5 | Battery replacement with the manual and commercially available tools | Completed without heat, solvents or special tools; time recorded (T1-055, T1-080) |
| V6-04 [Q2] | L6 | Sound dose against EN 50332-3 test signals; warnings; gradual return to RS1; persistence across power-off, crash and battery cut-off; every output and USB DAC mode | Within the standard's tolerance (T1-072, T1-073) |
| V6-05 [Q3] | L6 | EN 18031-1/-2 assessment | Every applicable requirement met (T1-078) |
| V6-06 [Q2] | L6 | Regulatory domain: a country change applies channels, power and access-point restrictions, and shows the domain | As T1-075 |
| V6-07 [Q3] | L6 | Formal tests at accredited labs for the declared markets | Passed; reports in the technical file (T1-071) |

## 5. Gates between levels

The gates between levels, for the T1:

- A module goes to L3 only after its L2 rows pass or each failure has a recorded fix in the main-board design.
- The main board is released for fabrication only after every L2 bench item of BOM §7 is closed or carried into the board with a decision, and every L3 row that can fail on the board's design (not only on the module interconnect) has passed.
- The product enters L6 only when every interaction of §3 is signed off at its level.

## 6. Open

- Open for the first modules: instruments and their residuals (a measurement's instrument residual sits at least 10 dB below the expected value, **UNVERIFIED** margin), KiCad layout-block reuse between projects (rules M1, M4), and thresholds marked "set at L2", which are filled from the first measurements and confirmed by the maintainers in the [experience budgets](experience-budgets.md).
