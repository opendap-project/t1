# Faceplate flex

- **Status:** Draft v0 (2026-10-24). Nothing here is built or measured.
- **Requirements:** FPT-002 to FPT-005, FPT-014, FPT-016, FPT-017, FPT-023 to FPT-025; T1-019 (faceplate not swapped regularly); board BRD-027 (microphone privacy indicator), BRD-049 (margin below every rating).
- **Inputs:** t1 [faceplate interface v1.0](../../../../product/docs/specs/faceplate-interface.md) §1, §2, §8 and [ADR 0005](../../../../product/docs/adr/0005-faceplate-supply-classes-and-protection.md) (rail classes); [ADR 0001](../adr/0001-focus-lcds-e35gh-display.md) (display); board [BOM v1](../../../../board/docs/specs/bom-v1.md) lines 34, 60, 71, 79–85, 96; board [ADR 0016](../../../../board/docs/adr/0016-front-side-height-under-the-display.md) (1.3 mm gap); Hirose FH35C catalog (edition 2013.11, Aug. 1, 2019 stamp) pp. 1–6 and FH12 catalog (Jan. 1, 2021); parts-lib sheets `Hirose/FH35C-51S-0.3SHW.md`, `Hirose/FH12-20S-0.5SH.md`, `Hirose/FH12-6S-0.5SH.md`, `Focus-LCDs/E35GH-I-MW800-CB.md`; the prototype fab's published flexible-PCB capabilities [P5] and kicad-lib [`pcbway-flex`](https://github.com/opendap-project/libs/tree/main/kicad/design-rules/pcbway-flex); the fab's published 2-layer FPC stack-up (fetched 2026-10-24).
- **Computation:** impedance with toolkit-hardware's `odapkit stackup` (2D finite-element field solver, [method](https://github.com/opendap-project/tools/blob/main/hardware/docs/specs/stackup-method.md)) on [`hardware/faceplate-flex/stackup-v0.toml`](../../hardware/faceplate-flex/stackup-v0.toml); coupling, the EMI-film comparison and the conductor sizing with the board's [`sim/flex-impedance`](../../../../board/sim/flex-impedance) finite-difference solver, shared with the HAT flat cable.
- **Conventions:** **UNVERIFIED** = no primary source checked. *Input from the mechanics* = a value this repository's faceplate mechanics or the case sets. Rule IDs `FFX-nn` carry their RFC 0010 quality level; an untagged item is Q1. Contact numbers are the faceplate interface's (FH35C contact numbers).

## Summary

The faceplate flex connects the touch faceplate to the body. It is one 2-layer polyimide circuit:

- a **tail** that mates the board's FH35C-51S: 0.2 ± 0.03 mm thick at the mating area with a PI stiffener, 15.6 ± 0.05 mm wide, contacts on one face, no copper on the other (Hirose catalog pp. 2, 5, 6);
- a **component area** on an FR-4 stiffener that carries the two FH12 connectors for the display module's own tails (FH12-20S for the TFT, FH12-6S for the touch panel), the reset translator and the faceplate's parts (identity controller, ambient light sensor, RGB status LED, microphone, privacy LED), or arms to the ones that sit elsewhere on the front;
- **DSI** clock and lane 0 as 94 / 150 µm (drawn) microstrip on L1 over the L2 ground plane: 100.0 Ω differential (computed);
- **supply conductors** sized for each rail class of t1 ADR 0005, every one rated far above its fault ceiling; widths set by the voltage drop.

Stack-up: the prototype fab's standard 2-layer FPC, 0.156 mm. The touch faceplate uses 32 of the 51 contacts. Two findings need other owners before layout: the FH12 connectors cannot sit in the 1.3 mm display-to-board gap (§1), and the DSI pairs of pinout v1 may straddle the FH35C's two contact rows (§2.3).

## 1. Scope and topology

```text
board FH35C-51S ── tail (PI stiffener) ── flex ── component area (FR-4 stiffener) ── FH12-20S ── display TFT tail (20)
                                                     │                             └ FH12-6S  ── display CTP tail (6)
                                                     ├ SN74AXC1T45 (LCD reset, 3.3 V → 1.8 V)
                                                     ├ identity controller (HID over I2C, 0x2C; part open)
                                                     └ arms or traces to: VEML6030 and RGB LED (above the display),
                                                       microphone and privacy LED (below the display)
```

- **Where things can sit.** Board ADR 0016 leaves a 1.3 mm gap between the display module and the board, and "nothing of the faceplate enters it except the tail and its stiffener at the connector" (interface §8). The FH12 is 2 mm high (FH12 catalog p. 4) before its stiffener and the flex, so **the component area and both FH12 sit outside the display footprint**, in front zone PCB-Z-04 or on the faceplate frame (FFX-01 [Q0]). The Focus drawing shows both module tails bent behind the module ("Bend and Ship", spec p. 3), which would bring their contact ends into the gap. Whether the tails reach the component area unbent, and how long they are, needs the master drawing from Focus LCDs (the tail lengths are **UNVERIFIED** in the parts-lib sheet) and the faceplate mechanics.
- **Front layout.** FPT-023 puts the ambient light sensor and the status LED above the display, FPT-024 the microphone below it. Whether they sit on arms of this flex, on a second small flex, or on the faceplate frame with their own wiring is input from the mechanics; their nets are in §4 either way.
- **Not in scope:** the board side of the FH35C (board PCB constraints), the display module and its tails (Focus LCDs), the faceplate mechanics (this repository's `case/`).

## 2. Tail at the FH35C

### 2.1 Dimensions

From the FH35C catalog; every value is Hirose's.

| ID | Item | Value | Source |
|---|---|---|---|
| FFX-02 [Q0] | Thickness at the mating area | **0.2 ± 0.03 mm**, gold-plated contacts | p. 2 |
| FFX-03 [Q0] | Outline width F (51 contacts) | **15.6 ± 0.05 mm**; corner radius ≤ 0.2 mm | p. 5 |
| FFX-04 [Q0] | Contact pads | Two staggered rows, 26 ((n+1)/2) and 25 ((n−1)/2), 0.6 mm pitch within a row, offset 0.3 mm; pad width 0.3 +0.04 / −0.03 mm; position tolerance 0.02 mm to datum Z; first pad edges 0.3 ± 0.07 mm and 0.6 ± 0.07 mm from the outline; spans B 14.4 and C 15 mm | p. 5 |
| FFX-05 [Q0] | Pad lengths from the tip | As drawn on p. 5: 0.2 ± 0.1, 0.75 ± 0.1, 0.85 ± 0.1, 1.75 ± 0.3, 2.1 ± 0.1 and 2.25 ± 0.1 mm, the 26-pad row nearest the tip and the 25-pad row behind it with their traces between the front pads | p. 5 (figure) |
| FFX-06 [Q0] | Stiffener | Stiffener film on the back of the mating area, 2.85 ± 0.3 mm from the tip; overlap N between the coverlay and the stiffener ≥ 0.5 mm | p. 5, note 6 |
| FFX-07 [Q0] | Back-side copper | None in the mating area (on a double-sided FPC it can unlock the connector) | p. 6 |
| FFX-08 [Q1] | Contact finish | Gold over nickel; Hirose's reference composition: nickel 1–5 µm, gold 0.2 µm. At the prototype fab: hard gold, or ENIG with the gold thickness specified (the fab's flex finishes include both [P5]; the gold thickness reachable on flex is **UNVERIFIED**) | p. 6; [P5] |
| FFX-09 [Q1] | Mating cycles | 10 (a service operation, T1-019) | p. 2 |

### 2.2 Thickness budget at the mating area

The tail reuses the flex's own layers; the top coverlay is open over the pads, L2 is removed (FFX-07), and a PI stiffener brings the total to 0.2 mm.

| Layer | Thickness | Source |
|---|---|---|
| L1 copper, finished | 24 µm | Fab 2-layer stack-up |
| Contact finish | ≈ 3 µm | Hirose reference (Ni 1–5 µm + Au 0.2 µm) |
| Adhesive 20 / PI 25 / adhesive 20 | 65 µm | Fab 2-layer stack-up |
| L2 copper | removed | FFX-07 |
| Bottom coverlay (adhesive 15 + PI 12.5) | 27.5 µm | Fab 2-layer stack-up |
| Stiffener adhesive | ≈ 25–30 µm (**UNVERIFIED**; Hirose's reference uses 25 µm thermoset) | — |
| PI stiffener | 50 µm (the fab offers PI 0.05–0.25 mm [P13]) | — |
| **Total** | **≈ 195–200 µm**, against 200 ± 30 µm | Arithmetic |

The fab's ±1.2 mil (±0.03 mm) for a two-layer flex up to 12 mil [P5] alone spans Hirose's whole tolerance, and no tolerance is published with a PI stiffener: the fab drawing states 0.200 ± 0.03 mm at the mating area as a requirement, the fab confirms it in its DFM review, and the first articles are measured (interface FI-M01).

### 2.3 Contact numbering and the DSI rows

- **Which contact numbers fall in which row is not in the catalog** (**UNVERIFIED**; parts-lib sheet; interface §1.1). The tail's pad order is drawn from Hirose's drawing for approval and from the face the tail is inserted with (the FH35C is a dual-sided connector, catalog p. 1); the pinout's contact numbers never change for it, only the drawing (FFX-10 [Q0]).
- **Possible conflict with pinout v1.** Hirose asks for each differential pair on "identical contacts" (p. 1, feature 3), and interface §8 requires each DSI pair on contacts of the same row. Pinout v1 pairs consecutive contacts: (2, 3), (5, 6), (8, 9), (11, 12), (14, 15). If the drawing numbers the contacts alternately between the two rows, as a staggered 0.3 mm series may (**UNVERIFIED**), every one of those pairs straddles both rows. That is a pinout change for the t1 owner, before any faceplate is built (§10).
- **Reference at the tail.** With no L2 copper in the mating area, the DSI pads lose their ground plane over about 2.9 mm; they are referenced to the ground contacts beside them (G-S-S-G, contacts 10–16), and the L2 plane ends no closer to the tip than the stiffener end (FFX-11 [Q1]).

## 3. Stack-up and impedance

The prototype fab's standard 2-layer FPC, 0.156 mm (base copper; about 0.168 mm finished):

| Layer | Material | Thickness | Use |
|---|---|---|---|
| Coverlay | PI 12.5 µm + adhesive 15 µm | 27.5 µm | Open over the FH35C pads and the SMT lands |
| **L1** | Copper 18 µm base, 24 µm finished | 18 (24) µm | DSI, low-speed, supplies, pads |
| Dielectric | Adhesive 20 / PI 25 / adhesive 20 | 65 µm | — |
| **L2** | Copper 18 µm base, 24 µm finished | 18 (24) µm | `GND` plane; short crossovers away from DSI |
| Coverlay | Adhesive 15 µm + PI 12.5 µm | 27.5 µm | — |

The thinner 0.116 mm stack (25 µm adhesiveless PI) would need DSI traces near 30 µm, below the fab's 0.06 mm floor; the 65 µm dielectric gives traces of about 90 µm.

| ID | Item | Value | Computed |
|---|---|---|---|
| FFX-12 [Q1] | DSI pairs, `MIPI_100D` | **94 µm traces (drawn), 150 µm gap**, L1 over the L2 plane, coverlay on top | **100.0 Ω** differential, 30.0 Ω common (target 100 Ω ± 10 %, interface §2.1); dielectric −10 / +10 %: −4.5 / +4.0 Ω; DK −5 / +5 %: +2.3 / −2.1 Ω; width −10 / +10 µm: +5.8 / −5.3 Ω; copper ±15 %: ±1.6 Ω; worst case 86.6–113.7 Ω, RSS ±7.8 Ω; effective DK 2.82, 5.61 ps/mm |
| FFX-13 [Q1] | Spacing | ≥ 0.45 mm from a DSI pair to the other pair and to any other line | Backward coupling about −40 dB at 0.45 mm, −34 dB at 0.3 mm (computed) |
| FFX-14 [Q1] | Matching on the flex | Within each pair ≤ 0.1 mm; clock to lane 0 ≤ 0.3 mm | Interface §2.1 (length-matched pairs); the board's PCB-I-04 holds 0.91 mm data to clock on its side |
| FFX-15 [Q1] | Plane under DSI | L2 solid under both pairs from the tail's stiffener end to the FH12-20S; no L2 crossover under a pair | — |
| FFX-16 [Q2] | Impedance check | TDR on a coupon of the production panel | Interface FI-E11 |

- Assumptions (in the stack-up file): adhesive DK 3.5, a 6 µm etch reduction on the 24 µm outer copper, a conformal 27.5 µm coverlay. The board's finite-difference solver, which fills the gaps between traces with coverlay adhesive instead, gives 100 Ω at 85 µm (mean) against `odapkit stackup`'s 91 µm (mean); the pressed coverlay lies between the two models.
- The prototype fab controls flex impedance to ±7 % above 50 Ω [P5] by adjusting the width; the arithmetic worst case is outside ±10 %, which `odapkit stackup` reports as a warning that the fab's compensation and the coupon (FFX-16) absorb.
- The panel uses one lane at about 337 Mb/s (BOM line 81). The flex is drawn to the interface's class so a later faceplate revision with more lanes can reuse the method; the touch flex routes only clock and lane 0.
- **No EMI film over the DSI pairs** (FFX-17 [Q1]): on this stack a film on the coverlay takes the pair from about 100 to about 56 Ω (computed, finite-difference solver). If a film is ever needed it is designed in with its own geometry.

## 4. Conductor map

Every ground contact is connected (interface §3); reserved contacts get a pad and nothing else (interface §2.7); unused contacts get a pad and no conductor.

| Contact | Line | Touch faceplate | Destination on the faceplate | Conductor |
|---|---|---|---|---|
| 1 | GND | used | L2 plane | via at the pad, outside the mating area |
| 2, 3 | DSI_D3± | not used | — | pad only |
| 4 | GND | used | L2 plane | via |
| 5, 6 | DSI_D2± | not used | — | pad only |
| 7 | GND | used | L2 plane | via |
| 8, 9 | DSI_D1± | not used | — | pad only |
| 10 | GND | used | L2 plane | via |
| 11 | DSI_D0+ | used | FH12-20S contact 17 (MIPI_D0P) | `MIPI_100D` |
| 12 | DSI_D0− | used | FH12-20S contact 18 (MIPI_D0N) | `MIPI_100D` |
| 13 | GND | used | L2 plane | via |
| 14 | DSI_CLK+ | used | FH12-20S contact 14 (MIPI_CLP) | `MIPI_100D` |
| 15 | DSI_CLK− | used | FH12-20S contact 15 (MIPI_CLN) | `MIPI_100D` |
| 16 | GND | used | L2 plane | via |
| 17 | I2C_SCL | used | FH12-6S contact 4 (SCL); identity controller; VEML6030 | low-speed |
| 18 | I2C_SDA | used | FH12-6S contact 3 (SDA); identity controller; VEML6030 | low-speed |
| 19–23 | SPI_SCLK, SPI_MOSI, SPI_MISO, SPI_CS#, DBI_D/C | not used | — | pad only |
| 24 | TP_INT | used | FH12-6S contact 2 (INT) | low-speed |
| 25 | TP_RST# | used | FH12-6S contact 1 (RST) | low-speed |
| 26 | LCD_RST# | used | SN74AXC1T45 A input (3.3 V side); its B output (1.8 V side) to FH12-20S contact 9 (RESET) | low-speed |
| 27 | LCD_TE | not used | — (the panel tail has no TE pin, BOM line 81) | pad only |
| 28 | HID_INT# | used | Identity controller interrupt, open drain | low-speed |
| 29 | ALS_INT# | used | VEML6030 INT, open drain | low-speed |
| 30, 31, 32 | LED_R, LED_G, LED_B | used | RGB LED anodes (Everlight 19-337/R6GHBHC-A01/2T, BOM line 79); cathodes to faceplate `GND` | low-speed, ≥ 0.2 mm |
| 33 | GND | used | L2 plane | via |
| 34 | PDM_CLK | used | Microphone clock (Infineon IM73D122, BOM line 34) | low-speed, 1.8 V |
| 35 | PDM_DATA | used | Microphone data | low-speed, 1.8 V |
| 36 | FP_DET# | used | Faceplate `GND`, ≤ 100 Ω (interface §2.1) | short to the plane |
| 37, 38 | GPIO0, GPIO1 | not used | — | pad only |
| 39 | GND | used | L2 plane | via |
| 40 | MIC_1V8 | used | Microphone VDD; privacy LED (BOM line 80) and its resistor, so the LED cannot light without microphone power (BRD-027) | supply |
| 41 | FP_1V8 | used | FH12-20S contact 7 (IOVCC); SN74AXC1T45 VCCB | supply |
| 42, 43 | FP_3V3 | used | FH12-6S contact 6 (CTP VDD, GT911); identity controller; VEML6030; SN74AXC1T45 VCCA | supply, both contacts joined on the flex |
| 44 | FP_VCI | used | FH12-20S contact 6 (VCI) | supply |
| 45 | BL_LEDK | used | FH12-20S contact 2 (LEDK) | backlight |
| 46 | BL_LEDA | used | FH12-20S contact 4 (LEDA) | backlight |
| 47–51 | Reserved | — | — | pad only; contact 47 stays reserved |

Count: 32 contacts used, as interface §7.5 lists for the touch faceplate (DSI lane 0 and clock 4, ground 8, I2C 2, touch 2, LCD_RST# 1, interrupts 2, LED 3, PDM 2, FP_DET# 1, supplies 7); 19 pads without a conductor.

- **FH12-20S, other contacts** (display spec p. 5): `GND` 10, 13, 16, 19, 20 to the L2 plane; NC 1, 3, 5, 8, 11, 12 left unconnected.
- **FH12-6S contact 5** (`GND`) to the L2 plane.
- **Reset translator.** BOM line 96 lists two SN74AXC1T45 (reset out, TE in); this panel has no TE pin, so the touch faceplate fits one (§10).
- **Microphone channel select** and the microphone's other pins follow its datasheet and the board's PDM channel plan (not transcribed here, **UNVERIFIED**).
- **Identity controller:** part not chosen yet (interface BC7); its pins are placeholders: VDD from FP_3V3, I2C, HID_INT#, `GND`, and its programming pads.
- **FH12 orientation.** Both FH12 are bottom-contact: the module tail's conductors face the faceplate flex (FH12 catalog p. 3). Contact 1's position on each connector and the tail's insertion side are checked on the Hirose drawing and the Focus master drawing (**UNVERIFIED**).

## 5. Supply conductors

Rail classes from t1 ADR 0005; every conductor is rated (IPC-2221B, external layer, 24 µm, 10 °C rise) far above its fault ceiling, so the flex is never the weak element; the widths are set by the voltage drop.

| ID | Rail | Contacts | Budget | Fault ceiling | Width on L1 | Rating at 10 °C | Drop at the budget, 80 mm |
|---|---|---|---|---|---|---|---|
| FFX-18 [Q0] | FP_3V3 | 42, 43 | 200 mA | ≤ 0.4 A | **0.5 mm** | ≈ 1.1 A | 23 mV |
| FFX-19 [Q0] | FP_1V8 | 41 | 100 mA | ≤ 0.2 A | **0.3 mm** | ≈ 0.76 A | 19 mV |
| FFX-20 [Q0] | MIC_1V8 | 40 | 20 mA | ≤ 0.2 A | **0.2 mm** | ≈ 0.57 A | 6 mV |
| FFX-21 [Q0] | FP_VCI | 44 | 100 mA | ≤ 0.2 A | **0.3 mm** | ≈ 0.76 A | 19 mV |
| FFX-22 [Q0] | BL_LEDA, BL_LEDK | 46, 45 | 60 mA (set by the body) | ≤ 0.2 A | **0.3 mm** each | ≈ 0.76 A | 12 mV |
| FFX-23 [Q0] | `GND` | 8 contacts | all returns | — | L2 plane | — | — |

- The minimum width for 0.4 A at 10 °C on 24 µm is 0.124 mm; 80 mm is an assumed upper length (input from the mechanics). The FH35C adds ≤ 100 mΩ per contact, conductor included (catalog p. 2): 10 mV on FP_3V3 at 200 mA over its two contacts.
- **Backlight lines (FFX-24 [Q0]):** BL_LEDA and BL_LEDK run side by side from contacts 45, 46 to FH12-20S contacts 2 and 4, keeping the string's current loop small. BL_LEDA is a 30 V class line (interface §2.3): ≥ 0.2 mm from every other conductor (a design choice above the 3 mil fab rule). BL_LEDK never touches `GND`: it is the driver's feedback, and grounding it drives the string to the over-voltage threshold (interface §2.7).
- **Decoupling on the faceplate** stays within interface §2.2's capacitance limits: FP_3V3 ≤ 10 µF, FP_1V8, MIC_1V8 and FP_VCI ≤ 4.7 µF each, placed at the FH12 and at each part.
- **No back-powering** (interface §2.7): no faceplate output drives a contact while its rail is off; the translator's A side is on FP_3V3 and its B side on FP_1V8, both from the body.

## 6. Stiffeners

| ID | Where | Stiffener | Source or reason |
|---|---|---|---|
| FFX-25 [Q0] | FH35C mating area | PI, 50 µm (with its adhesive the tail reaches 0.2 mm, §2.2), 2.85 ± 0.3 mm from the tip, overlap N ≥ 0.5 mm | FH35C catalog p. 5; fab PI 0.05–0.25 mm [P13] |
| FFX-26 [Q1] | Component area with both FH12 | FR-4, 0.2–0.4 mm (fab 0.2–1.5 mm [P13]); thickness from the height the mechanics give | The FH12 is a flip-lock connector worked by hand at assembly; it needs a rigid base. Hirose's FH12 catalog gives no stiffener figure for the board side (**UNVERIFIED**) |
| FFX-27 [Q1] | Other parts on arms (LED, sensor, microphone) | FR-4 or PI under each part, as the mechanics fix them | Solder joints on a bending area |
| FFX-28 [Q1] | All | Stiffener edges ≥ 1.0 mm from any bend; bonded with a reflow-capable adhesive where parts are soldered after bonding | — |

## 7. Bend

| ID | Item | Value | Source |
|---|---|---|---|
| FFX-29 [Q0] | Minimum inside bend radius | **1.2 mm absolute** (7 × 0.168 mm) | fab, two layers 7–10 × thickness [P5] |
| FFX-30 [Q1] | Design inside bend radius | **≥ 1.7 mm** (10 ×) | Same, upper end |
| FFX-31 [Q1] | Bend type | Static, folded at assembly; the faceplate is serviced, not swapped regularly (T1-019) | — |
| FFX-32 [Q1] | Bend zones | No vias, pads, stiffener edges or plane edges within a bend and 1.0 mm either side; the DSI pairs cross the bend axis at right angles, both members together; the L2 plane stays solid through the bend under the DSI | kicad-lib `pcbway-flex` README |
| FFX-33 [Q0] | Never bent | The FH35C mating area and every stiffened area | — |

## 8. Fab notes

- **Rules:** kicad-lib `pcbway-flex` (3 mil track and gap, 0.15 / 0.35 mm vias, 8 mil coverlay web, 0.20 mm copper to outline **UNVERIFIED** for flex). The DSI class at 94 µm is above the 3 mil default; nothing needs the 2 mil floor.
- **FH35C pads:** the coverlay opens over the whole mating area; the 0.3 mm pads at 0.6 mm pitch per row keep a 0.3 mm gap, so the 8 mil web is not needed there (no coverlay between them).
- **FH12 lands:** 0.3 ± 0.03 mm at 0.5 mm pitch (FH12 catalog p. 10) leave a 0.2 mm gap, below the 8 mil web: one coverlay opening per row, or LPI mask in that area.
- **Outline:** laser routed, ±2 mil (±0.05 mm) [P5], the same as Hirose's F tolerance: the tail outline is a stated requirement on the fab drawing.
- **Finish:** gold per FFX-08 on the FH35C pads; ENIG on the SMT lands (selective finishes, or the gold finish everywhere: DFM).
- **Assembly:** two FH12, the translator, the identity controller, the sensor, LEDs, microphone and passives on stiffened areas; the fab's flex assembly is "contact us" [P8] (**UNVERIFIED**, DFM).

## 9. Inputs needed from the mechanics and the case

1. **Tail:** the FH35C's position and orientation on the board (contact 1's side), the face the tail is inserted with, the tail's exit direction, and room to work the back-flip actuator with the tail inserted (interface §8).
2. **Route** from the FH35C to the component area within the 1.3 mm gap (only the tail and its stiffener enter it), the folds and the radius each has (≥ 1.7 mm wanted, 1.2 mm absolute).
3. **Component area:** where it sits outside the display footprint, and the height there for FH12 (2.0 mm) + stiffener + flex.
4. **Display tails:** whether they reach the FH12 unbent, from the Focus master drawing (tail lengths, TFT tail pitch).
5. **Front parts:** positions of the ambient light sensor, status LED (FPT-023) and microphone port (FPT-024) on the front, and whether they sit on arms of this flex.
6. **Length** of each segment (80 mm assumed as the upper bound for the drops of §5).
7. **Fixing** of the flex in the faceplate, and the ground bond to the frame for ESD (interface §2.4, §8).

## 10. Open items and changes others need

| # | Owner | Item |
|---|---|---|
| F1 | t1 (faceplate interface), board (pinout v1 §8) | FH35C row assignment from Hirose's drawing for approval; if contacts alternate between rows, move the DSI pairs so each pair sits on one row (§2.3). A contact change before any faceplate is built |
| F2 | Board (BOM line 96) | The touch faceplate fits one SN74AXC1T45 (reset), not two: the panel tail has no TE pin (BOM line 81). Keep the second footprint only if a later panel needs TE |
| F3 | Board (BOM lines 84, 85) | Note that both FH12 sit on the faceplate flex's FR-4-stiffened component area outside the display footprint (§1), not in the 1.3 mm gap |
| F4 | Board (ADR 0016, PCB-Z-03 connection area) | The 10 × 54 mm connection area holds the FH35C (16.9 × 3.2 mm), its ESD parts and the tail's insertion with actuator access; confirm with the tail position (§9 item 1) |
| F5 | Faceplate mechanics (this repository) | All inputs of §9 |
| F6 | Fab DFM review | Mating-area thickness 0.200 ± 0.03 mm with the PI stiffener; gold thickness on flex; flex assembly; stiffener adhesive |
| F7 | Focus LCDs | Master drawing: tail lengths, TFT tail pitch, contact side |
| F8 | Faceplate-touch | Replace the assumed DK, etch and coverlay model in `stackup-v0.toml` with the fab's answer and rerun `odapkit stackup check` |
| F9 | Faceplate-touch | Identity controller part (interface BC7) and microphone pins |
| F10 | Faceplate-touch | The KiCad project in `hardware/faceplate-flex/`, once the outline of §9 exists: the 2-layer stack-up of §3, `pcbway-flex` rules plus the `MIPI_100D` class (94 / 150 µm), the FH35C tail as a footprint drawn from catalog p. 5 and the drawing for approval, the FH12-20S and FH12-6S footprints, the parts of §4, and the stiffener and bend areas on user layers |

## 11. KiCad project

`hardware/faceplate-flex/` holds the stack-up file only (`stackup-v0.toml`): the flex needs the mechanics' outline (§9) before a KiCad project is more than a placeholder. What the project contains is item F10 of §10.

## 12. Sources

- Hirose Electric, FH35C Series catalog, edition 2013.11 (Aug. 1, 2019 stamp): pp. 1, 2, 4, 5, 6; FH12 Series catalog, Jan. 1, 2021: pp. 2–4, 10; parts-lib sheets (hashes there).
- Focus LCDs, E35GH-I-MW800-CB specification Rev 1.0: pp. 3, 5, 6 (parts-lib sheet).
- The prototype fab's published 2-layer FPC stack-up, fetched 2026-10-24; [P5] its published flexible-PCB capabilities, [P8] its published assembly capabilities and [P13] its FPC stiffener and copper options, as cited by the kicad-lib `pcbway-flex` rule set.
- IPC-2221B, conductor current-carrying design equation.
- `odapkit stackup` (toolkit-hardware `cf83c68`) on `hardware/faceplate-flex/stackup-v0.toml`; board `sim/flex-impedance`; both run 2026-10-24.
