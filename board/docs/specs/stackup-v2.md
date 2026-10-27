# Stackup v2 of the T1 main board

- **Superseded (2026-10-25)** by [stackup v3](stackup-v3.md): six layers, HDI 2+2+2, approved by the maintainers with its trades. Kept as the record of the eight-layer stack; the rules, net classes and constraints follow v3.
- **Status:** Draft v2 (2026-10-25). Replaces [stackup v1](stackup-v1.md) (ten layers, four full-layer grounds). Basis: the maintainers' direction of 2026-10-25: the board is grouped into isolated zones that share the physical layers, each zone using the layers under it for its own needs, so that the layer count, and then the number of full-layer grounds, come down to the minimum the zones allow. **The stack is to be confirmed by the fab's DFM review**, as v1 was; nothing here is laid out or measured.
- **Machine-readable copy:** [`../../hardware/stackup/stackup-v2.toml`](../../hardware/stackup/stackup-v2.toml), computed and checked with `odapkit stackup design` and `check` ([toolkit-hardware](https://github.com/opendap-project/toolkit-hardware), [stackup method](https://github.com/opendap-project/toolkit-hardware/blob/main/docs/specs/stackup-method.md)); a change edits the TOML, reruns the check and then this page.
- **Exploration input:** [`../../hardware/stackup/explore-zoned.toml`](../../hardware/stackup/explore-zoned.toml), run with `odapkit stackup explore` (every stack of 4, 6, 8 and 10 layers, every build, every symmetric dielectric sequence from the fab's published list, every role per layer per zone). The dual-stripline numbers of §4.4: [`../../hardware/stackup/dual-stripline-8l.toml`](../../hardware/stackup/dual-stripline-8l.toml) with `odapkit stackup coupling`.
- **Inputs:** [floorplan v1](floorplan-v1.md) (zones and their layer maps); [PCB design constraints](pcb-design-constraints.md) v0.14; the [BGA escape study](../../hardware/studies/bga-escape/README.md) (escape and core planes on this stack); the sources of stackup v1 ([PW-ST], [PW-PP], [P1]–[P3], [P12]), which this page does not repeat.

## 0. Summary

1. **Eight layers, HDI 2+4+2, 1.002 mm nominal** (0.902–1.102 mm with the fab's ±0.10 mm), inside PCB-S-01's 1.0–1.2 mm. Three routing layers carry impedance classes (L1, L6, L8); **one full-layer ground (L7)**; four zone-local grounds (L2, L3, L5, L6 by zone); power on L4 everywhere and on L2, L3, L5 where a zone needs it.
2. **Why eight.** No four-layer stack escapes the RK3566 (its 0.4 mm ring needs microvias reaching an inner fast layer). The only six-layer stack that passes the exploration (2116/3313/0.43 mm core) puts the system rails on L1 with the SoC's decoupling; its plane check leaves a rail split under the SoC with no decoupling placed yet (§0.2). Eight is the fewest that passes every constraint and the SoC plane check, and this sequence is the only eight-layer one with a single full-layer ground.
3. **What made eight possible.** With RFC 0014 the I/O zone needs one inner fast layer, not two (nine pairs leave the core: USB-C USB 2, HAT USB 3 and USB 2, five DSI). PCB-S-12 pairs the core-rail plane with ground across a laser-class prepreg up to 90 µm (constraints v0.14; 65 µm before), the thinnest dielectric of this stack. With 65 µm, no stack under ten layers meets the 1.0–1.2 mm window together with the RF ground at 230–240 µm.
4. **Every class has a geometry at its target** (§5). Outer widths as v1; inner widths on L6: 85.5–95.5 µm (v1: 75.0–86.0 µm), so no impedance class needs the 0.075 mm option.
5. **The SoC escape and its planes close on this stack** ([BGA escape study](../../hardware/studies/bga-escape/README.md)): every used ball escapes on L8 and L6, no via in a pad, and DRC with the composed rules reports 0 errors and 0 unconnected items at the fab's normal 9 mil hole-to-inner-copper. No `BGA_ESCAPE` override of that value is needed.

### 0.1 Selection

| Rank (exploration) | Layers, build | Dielectrics (top to bottom) | Thickness | Full-layer grounds | Result |
|---|---|---|---|---|---|
| 1 | 6, 2+N+2 | 2116 / 3313 / core 0.43 / 3313 / 2116 | 1.046 mm | 1 (L5) | Fails the SoC plane check (§0.2) |
| **2** | **8, 2+N+2** | **3313 / 2116 / core 0.13 / 3313 / core 0.13 / 2116 / 3313** | **1.002 mm** | **1 (L7)** | **Chosen** |
| 3–13 | 8, 2+N+2 | other core and middle-prepreg pairs | 1.013–1.098 mm | 2 (L2, L7) | More full-layer grounds |
| 14 and after | 10, 1+N+1 and 2+N+2 | — | 1.019–1.098 mm | 1 | More layers |

Every 1+N+1 eight-layer sequence fails: the RF ground at 230–240 µm, the 90 µm pairing and the thickness window do not meet in the fab's dielectrics. Through-hole builds fail the SoC ring.

### 0.2 The six-layer candidate

On six layers the core zone has L1 (front, decoupling), L2 (core rails, paired with the L3 ground), L4 (the only inner routing layer) and L6 (the SoC). The system rails then share L1 with the SoC's decoupling (PCB-P-10). The escape closes (238 used signal balls on L6 and L4), but the plane check leaves vdda_0v9 in two pieces: one unconnected item, with the front still empty of the decoupling capacitors that will take most of that layer. The six-layer stack is therefore not taken.

## 1. Build

| Item | Value | Source |
|---|---|---|
| Layers | 8 | PCB-S-03 (v0.14) |
| Build | HDI 2+4+2: core L3–L6 (two 0.13 mm cores and one prepreg), then two sequential laminations per side | The fab 1+N+1 to 6+N+6 [P3] |
| Microvias | L1–L2 and L8–L7: 0.10 mm laser, 0.25 mm land, in 90 µm of 3313. L2–L3 and L7–L6: 0.125 mm laser, 0.275 mm land, in 120 µm of 2116 (**UNVERIFIED**, as v1). Stacked and copper-filled | As v1 §1; laser dielectric ≤ 0.15 mm [P3] |
| Through vias | 0.20 mm drill, 0.46 mm pad (0.45 mm is PCB-G-04's minimum; 0.46 mm keeps the fab's 5 mil ring [P1]); aspect ratio 1.002 / 0.20 = 5.0 | [P1] |
| Non-functional pads | Removed on inner layers for signal and ground through vias under the SoC (KiCad padstack "remove unconnected layers", start and end kept); power vias keep theirs | BGA escape study; the fab's handling **UNVERIFIED** (DFM review) |
| Buried vias | None | — |
| Material, finish | FR-4 Tg 170 (S1000-2M offered), ENIG | As v1 |
| Thickness | 1.002 mm nominal, ±0.10 mm | PCB-S-01 |

## 2. Layer table

Top is the front (faceplate side); the SoC, LPDDR4X and eMMC sit on the back (L8). The role in the table is the layer's role where impedance classes route; the role per zone is in §3.

| Layer | KiCad | Role | Copper | Dielectric below | Dk |
|---|---|---|---|---|---|
| L1 | `F.Cu` | Signal: front parts, decoupling, microstrip over L2; RF option over L3 | 35 µm (18 plated) | 90 µm prepreg 3313 (laser) | 4.45 |
| L2 | `In1.Cu` | Ground (system-rail plane in the core zone) | 25 µm (12 plated) | 120 µm prepreg 2116 (laser) | 4.45 |
| L3 | `In2.Cu` | Ground (pours in the power zone); RF ground under an L1 line | 18 µm | 130 µm core | 4.6 |
| L4 | `In3.Cu` | Power by zone | 18 µm | 90 µm prepreg 3313 | 4.45 |
| L5 | `In4.Cu` | Ground (pours in the power zone); paired with L4 | 18 µm | 130 µm core | 4.6 |
| L6 | `In5.Cu` | Stripline between L5 and L7: SoC escape, LPDDR4X, eMMC, fast I/O, MCLK | 18 µm | 120 µm prepreg 2116 (laser) | 4.45 |
| L7 | `In6.Cu` | Ground, full layer | 25 µm (12 plated) | 90 µm prepreg 3313 (laser) | 4.45 |
| L8 | `B.Cu` | Signal: RK3566, LPDDR4X, eMMC, microstrip over L7; RF option over L6 | 35 µm (18 plated) | — | — |

Laminate 0.962 mm, finished 1.002 mm with 20 µm mask per side (assumed). The 0.13 mm cores are read as dielectric thickness; the fab's table lists cores "with copper" (**UNVERIFIED**: if the copper is included, the board is about 70 µm thinner and the DFM review picks the next core).

## 3. Layer roles per zone

As [floorplan v1](floorplan-v1.md) §3. F fast routing, G ground, P power plane or pour.

| Zone | L1 | L2 | L3 | L4 | L5 | L6 | L7 | L8 |
|---|---|---|---|---|---|---|---|---|
| Core | P (decoupling) | P: system rails | G | P: SoC core and LPDDR4X rails | G | F | G | F |
| Audio | F | G | G | P: audio rails only | G | F | G | F |
| Power | F | G | P | P | P | P | G | F |
| Radio | F | G | G | P | G | G | G | F |
| I/O | F | G | G | P: HAT and USB-C `VBUS` | G | F | G | F |
| Corridors | F | G | G | P | G | F | G | F |

L7 is ground under every zone: the full-layer ground. L2, L3 and L5 are ground under every zone but one, and L6 under the radio zone only: the zone-local grounds, each stitched to L7 (§4.2).

## 4. Rules

### 4.1 Reference planes

1. **Impedance classes route only on L1, L6 and L8** (PCB-S-14), and only where the layer's references are ground in its zone: not on L1 in the core zone (L2 is the system-rail plane there), not on L6 in the power zone (pours) nor in the radio zone (ground). DRC checks it by zone.
2. **Edge margins.** A fast pair runs at least 1.02 mm from the edge of its reference area, a DDR line at least 0.30 mm (Rockchip HSPCB pp. 11, 28; as v1 §4.1.3), at a cut-out, at the board edge and at the edge of a zone-local ground.
3. **Corridors.** A crossing between zones happens inside a declared corridor, where L2, L5 and L7 are ground (PCB-S-18, DRC), so the crossing changes no reference.
4. **Pad voids (PCB-I-10).** Under an SMD pad of a fast class on L8 the void is on L7 and L6, so the pad references L5, 383 µm below (arithmetic). On L1 it is on L2 only, so the pad references L3, 235 µm below: L4 under it is a power area in most zones.

### 4.2 Return vias and stitching

1. **L1↔L3 is not a signal change** on this stack (L3 is not a routing layer). L8↔L6 through stacked microvias: one ground microvia stack within 0.76 mm (0.64 mm for `DDR_*`) of the signal via, symmetric for pairs (PCB-S-10).
2. **L1↔L6 and L1↔L8** through a through via: L1's reference L2 and L6/L8's references L5/L7 are all ground only outside the core zone and in the corridors, so such a change happens there, with one ground through via within 0.76 mm (PCB-S-10).
3. **One ground.** L7 is continuous; every zone-local ground (L2, L3, L5, L6) is stitched to it by ground vias on the PCB-S-13 grid and along every edge of its area (PCB-S-19). No split anywhere (PCB-A-01).
4. **Delay** differs per layer: 5.9–6.2 ps/mm outer, 7.09 ps/mm on L6 (§5). A matched group that changes layers is matched in delay, not in length (PCB-S-15).

### 4.3 Power

1. **Core rails** (vdd_cpu, vdd_logic, vdd_gpu, vdd_npu, vcc_ddr, vcc0v6_ddr) on L4, paired with the L5 ground across 90 µm of 3313 (PCB-S-12): 43.8 pF/cm² (arithmetic, ε0·4.45 / 90 µm; 57.3 pF/cm² at v1's 65 µm of 1080). vdd_logic, whose balls the other core rails surround, reaches the package edge through feed corridors on L4 between the other rails' areas: 5.52 mm of plane against 5.38 mm (IPC-2221 inner, 2.5 A, ΔT 10 °C); every core rail has more copper at the edge than its design current needs (BGA escape study).
2. **System rails** (vcca_1v8, vdda_0v9, vcc3v3_sys, vcc_1v8 and the PMU and I/O rails) on L2 in the core zone, over the L3 ground; rails whose areas interleave are joined by short tracks on L6 or L1. vcc0v6_ddr (L4), vdda_0v9 and vccio_sd (L2), 0.1–0.4 A, do not reach the package edge on their plane and are fed by a track or a short pour on another layer.
3. **Power zone:** L3 to L6 carry the battery path (5 A, PCB-P-01: a pour on two or more inner layers) and the VSYS trunk (PCB-P-02); L2 and L7 stay ground under the switch nodes (PCB-P-08).
4. **I/O zone:** L4 carries the HAT `VBUS` (`HAT_5V`, 4.5 A fault ceiling, PCB-P-20) and the USB-C `VBUS` paths as pours, with L1 or L8 copper where the width asks for it.
5. **Power next to power** (L3–L4–L5 in the power zone) is allowed; no impedance class or clock routes next to a power layer.

### 4.4 Dual stripline (not used)

No zone of this stack routes fast classes on two adjacent layers between the same grounds. For the record, on these dielectrics a dual stripline L3/L4 between the L2 and L5 grounds gives SE50 widths of 118.5 µm (L3) and 95.0 µm (L4) and a near-end coupling coefficient Kb of 13.9 % stacked, 10.9 % at one width of lateral offset, 2.6 % at three and 0.47 % at five (`odapkit stackup coupling`, 107 µm traces): a zone that ever needs it routes the two layers orthogonally, or offset by five widths in a parallel run.

### 4.5 RF microstrip (PCB-I-07, PCB-R-03)

1. On the module's side: L8 over the radio zone's L6 ground with L7 cut out, or L1 over L3 with L2 cut out. Line to ground: 235 µm (230–240 µm required).
2. The cut-out is 1.6 mm wide, centred on the line, along its whole length and 0.6 mm past each end (rule area `RF_CUTOUT` on the cut layer and the pour layer: `In6.Cu` and `In5.Cu` for an L8 line, `In1.Cu` and `In2.Cu` for an L1 line). Geometry, same-layer ground at ≥ 0.6 mm and the U.FL keep-out as v1 §4.4.

### 4.6 Audio area (PCB-A-01, A-07, A-20)

Under `AUDIO_ANALOG`: L2, L3, L5 and L7 ground; L6 carries only audio analog, reference, MCLK and the DAC serial port; L4 only the audio rails (`PWR_AMP`, `PWR_AUDIO`) or ground (PCB-A-20, DRC).

## 5. Trace geometry per class

Computed with `odapkit stackup design`, checked with `check` (2D quasi-static field solver; etch and fab corners assumed as v1). Widths drawn; gaps edge to edge.

| Geometry | Net classes | Layer (reference) | Target | Width | Gap | Z (solver) | ε_eff | Delay ps/mm |
|---|---|---|---|---|---|---|---|---|
| SE50 outer | `DDR_50SE`, `EMMC_SD_50SE`, `I2S_50SE` | L1 (L2), L8 (L7) | 50 Ω | 134.5 µm | — | 50.02 Ω | 3.45 | 6.19 |
| D90 outer | `USB2_90D`, `USB3_90D` | L1 (L2), L8 (L7) | 90 Ω | 101.5 µm | 100 µm | 89.99 Ω | 3.11 | 5.89 |
| D100 outer | `MIPI_100D`, `DDR_100D` | L1 (L2), L8 (L7) | 100 Ω | 104.5 µm | 175 µm | 100.00 Ω | 3.16 | 5.93 |
| SE50 inner | `DDR_50SE`, `EMMC_SD_50SE`, `I2S_50SE`, `MCLK_50SE` | L6 (L5/L7) | 50 Ω | 90.5 µm | — | 50.01 Ω | 4.52 | 7.09 |
| D90 inner | `USB2_90D`, `USB3_90D` | L6 (L5/L7) | 90 Ω | 95.5 µm | 150 µm | 90.06 Ω | 4.52 | 7.09 |
| D100 inner | `MIPI_100D`, `DDR_100D` | L6 (L5/L7) | 100 Ω | 85.5 µm | 250 µm | 99.92 Ω | 4.52 | 7.09 |
| RF50 | `RF_50SE` | L1 (L3, L2 cut out), L8 (L6, L7 cut out) | 50 Ω | 391 µm | ground ≥ 600 µm | 50.00 Ω | 3.35 | 6.11 |

### 5.1 Tolerance sensitivity

Each parameter moved alone to the end of an assumed fab range (dielectric ±10 %, Dk ±5 %, width ±10 µm, copper ±15 %); change in Z at the low and high end, Ω.

| Geometry | Dielectric | Dk | Width | Copper | RSS | Arithmetic worst case | ±10 % window |
|---|---|---|---|---|---|---|---|
| SE50 outer | −2.9 / +2.7 | +1.2 / −1.1 | +1.8 / −1.7 | +0.5 / −0.5 | 3.6 | 43.9–56.2 | 45–55 |
| D90 outer | −2.8 / +2.4 | +2.0 / −1.9 | +5.7 / −5.4 | +2.0 / −1.9 | 6.9 | 78.0–102.0 | 81–99 |
| D100 outer | −4.1 / +3.6 | +2.2 / −2.1 | +4.9 / −4.6 | +1.7 / −1.6 | 7.0 | 87.7–112.4 | 90–110 |
| SE50 inner | −2.6 / +2.4 | +1.3 / −1.2 | +2.5 / −2.2 | +0.7 / −0.6 | 3.9 | 43.3–56.9 | 45–55 |
| D90 inner | −3.4 / +2.9 | +2.3 / −2.2 | +5.0 / −4.6 | +1.5 / −1.4 | 6.7 | 78.5–101.8 | 81–99 |
| D100 inner | −4.5 / +3.9 | +2.6 / −2.4 | +5.3 / −4.8 | +1.5 / −1.4 | 7.6 | 86.8–113.3 | 90–110 |
| RF50 | −2.6 / +2.4 | +1.2 / −1.1 | +0.7 / −0.7 | −0.2 / +0.2 | 2.9 | 45.5–54.4 | 45–55 |

The RSS fits every window; the arithmetic worst case fits only RF50, as in v1: the fab order requests impedance control with coupons for every class (PCB-S-05). A 5 % width error moves Z by about 2–3 %; the DRC width bands are ±5 %.

## 6. Changes from v1

| Where | v1 | v2 |
|---|---|---|
| Layers, build, thickness | 10, 2+6+2, 1.074 mm | 8, 2+4+2, 1.002 mm |
| Dielectrics | 3313 / 2116 / core 103 / 1080 / core 50 / 1080 / core 103 / 2116 / 3313 | 3313 / 2116 / core 130 / 3313 / core 130 / 2116 / 3313 |
| Grounds | L2, L4, L7, L9, full layers | L7 full; L2, L3, L5, L6 zone-local |
| Power planes | L5 (core rails), L6 (system rails), full layers | L4 (core rails in the core zone; other rails by zone); L2 system rails in the core zone; L3–L6 pours in the power zone |
| Core-rail pairing | 65 µm (1080) | 90 µm (3313) |
| Routing layers for impedance classes | L1, L3, L8, L10 | L1, L6, L8 (by zone) |
| KiCad layer of the inner routing layer | `In2.Cu`, `In7.Cu` | `In5.Cu` |
| RF cut-out and pour, back side | `In8.Cu`, `In7.Cu` | `In6.Cu`, `In5.Cu` |
| Inner widths | SE50 78.5, D90 86.0, D100 75.0 µm | 90.5, 95.5, 85.5 µm |
| Applied in | — | `hardware/rules/netclasses.toml`, `t1-main-board.kicad_dru` (layer names, widths, zone-aware PCB-S-14, PCB-S-17, S-18, A-20), constraints v0.14 |

## 7. Debt by level (RFC 0010)

| Item | Level | Closes it |
|---|---|---|
| The fab confirms the stack, the 0.13 mm cores as dielectric thickness, Dk at frequency, the 25 µm on L2/L7, the 0.125 mm second laser level, the thickness tolerance at 1.0 mm, the removal of non-functional pads | Q0 | DFM review |
| Core-rail PDN impedance with the 90 µm pairing and the front decoupling, against Rockchip's targets | Q1 | PDN simulation at layout |
| Coupons for every class in §5, measured | Q1 | First fab order |
| Loss budget of USB 3 at these widths | Q1 | Layout |
| Core-zone routing capacity on L6 and L8 (escape proven; DDR, eMMC and onward routes at placement) | Q1 | Placement and routing |
| Zone-local ground stitching pitch and fence pitch (PCB-S-13, S-19) measured on the pre-compliance scan | Q2 | Pre-compliance |
| Board flex at 1.0 mm under the SoC (screw torque, drop) | Q2 | First articles |
