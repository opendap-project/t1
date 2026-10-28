# Stackup v3 of the T1 main board

- **Status:** Draft v3 (2026-10-25). **Approved by the maintainers on 2026-10-25**, with the nine trades of §0.1. Replaces [stackup v2](stackup-v2.md) (eight layers). The maintainers' rule for the layer count: *fewer layers is better; the layers that are needed in the end are fine* (PCB-S-03). **The stack is to be confirmed by the fab's DFM review**; nothing here is laid out or measured.
- **Machine-readable copy:** [`../../hardware/stackup/stackup-v3.toml`](../../hardware/stackup/stackup-v3.toml), computed and checked with `odapkit stackup design`, `check` and `coupling` ([tools/hardware](https://github.com/opendap-project/tools/tree/main/hardware), [stackup method](https://github.com/opendap-project/tools/blob/main/hardware/docs/specs/stackup-method.md)); a change edits the TOML, reruns the check and then this page.
- **Inputs:** [floorplan v1](floorplan-v1.md) (zones; its layer references follow this page); [PCB design constraints](pcb-design-constraints.md) v0.15; the [BGA escape study](../../hardware/studies/bga-escape/README.md) (escape, decoupling and core planes on this stack); the sources of stackups v1 and v2 ([PW-ST], [PW-PP], [P1]–[P3], [P12]), which this page does not repeat.

## 0. Summary

1. **Six layers, HDI 2+2+2, 1.046 mm nominal** (0.946–1.146 mm with the fab's ±0.10 mm), inside PCB-S-01's 1.0–1.2 mm. Dielectrics top to bottom: **2116 / 3313 / core 0.43 mm / 3313 / 2116**. Three routing layers carry impedance classes (L1, L4, L6); **one full-layer ground (L5)**; zone-local grounds on L2 (every zone but the core) and L3 (every zone but the power zone).
2. **It meets every must constraint** of the constraints set: the RK3566 escape and the core planes close with Rockchip's decoupling under the SoC ([BGA escape study](../../hardware/studies/bga-escape/README.md): 238 balls on L6 and L4, no via in a pad, every rail one piece, DRC 0 errors and 0 unconnected); every impedance class has a geometry at its target (§5); the RF line has its 235 µm ground on both sides (PCB-R-03); MCLK runs between two grounds (PCB-I-09).
3. **Against stackup v2** it has two copper layers and one lamination cycle fewer, with the same laser levels (four, stacked, copper-filled) and the same through drill.

### 0.1 Trades accepted by the maintainers (2026-10-25)

| # | Trade | Where it is applied |
|---|---|---|
| 1 | In the core zone the SoC core rails and the system rails share one plane layer (L2), and the core rails also pour on L1 between the decoupling capacitors to reach the package edge | §4.3; PCB-S-20, S-12 |
| 2 | The two interleaved analog rails (vcca_1v8, vdda_0v9) are joined by short tracks on L4, L2 or L1 | §4.3; PCB-S-21 |
| 3 | The I/O zone has no inner power layer: HAT `VBUS` and USB-C `VBUS` run as outer pours, ≥ 2.4 mm and ≥ 1.4 mm | §4.3; PCB-P-22, P-20, P-03 |
| 4 | The power zone has two inner pour layers (L3, L4) for the battery path and VSYS | §4.3; PCB-P-01, P-23 |
| 5 | The audio rails run as tracks; there is no audio power layer | §4.6; PCB-A-20, P-06 |
| 6 | Outer impedance traces are wider (SE50 188 µm, from the 120 µm 2116 outer prepreg), which costs LPDDR4X routing room on the SoC side | §5; PCB-I-01 to I-09 |
| 7 | Edge crosstalk on L4 is higher (430 µm to L3, 90 µm to L5): LPDDR4X keeps 3 × W from every other net on L4 | §4.4; PCB-S-24 |
| 8 | The core zone has no spare routing layer: it routes on L4 and L6, with low-speed nets on L1 | §4.7; PCB-S-22 |
| 9 | The board is 1.046 mm (v2: 1.002 mm), and fewer copper planes spread the SoC's heat: a thermal check at Q2 | §1; PCB-S-01, S-23 |

## 1. Build

| Item | Value | Source |
|---|---|---|
| Layers | 6 | PCB-S-03 (v0.15) |
| Build | HDI 2+2+2: one double-sided 0.43 mm core (L3–L4), then two sequential laminations per side | The fab 1+N+1 to 6+N+6 [P3] |
| Microvias | L1–L2 and L6–L5: 0.10 mm laser, 0.25 mm land (PCB-G-03), in 120 µm of 2116: aspect 1.2 (**UNVERIFIED**, DFM review; the fab's published limit is a dielectric ≤ 0.15 mm [P3]). L2–L3 and L5–L4: in 90 µm of 3313 (aspect 0.9 at 0.10 mm); the escape study models this level at 0.125 mm / 0.275 mm. Stacked and copper-filled | Laser 4 mil standard, 8 mil maximum, dielectric ≤ 0.15 mm [P3]; copper-filled stacking [P2, P16] |
| Through vias | 0.20 mm drill, 0.46 mm pad (PCB-G-04's 0.45 mm raised to keep the fab's 5 mil ring [P1]); aspect ratio 1.046 / 0.20 = 5.2 | [P1] |
| Non-functional pads | Removed on inner layers for signal and ground through vias under the SoC (KiCad padstack "remove unconnected layers", start and end kept); power vias keep theirs | BGA escape study; the fab's handling **UNVERIFIED** (DFM review) |
| Buried vias | None | — |
| Via in pad | Not needed by the escape; a decoupling capacitor on L1 reaches L2 through one copper-filled microvia, which is the build's own (no extra process) | BGA escape study |
| Material, finish | FR-4 Tg 170 (S1000-2M offered), ENIG | As v1 |
| Thickness | 1.046 mm nominal, ±0.10 mm | PCB-S-01 |

## 2. Layer table

Top is the front (faceplate side); the SoC, LPDDR4X and eMMC sit on the back (L6, ADR 0016). The role in the table is the layer's role where impedance classes route; the role per zone is in §3.

| Layer | KiCad | Role | Copper | Dielectric below | Dk |
|---|---|---|---|---|---|
| L1 | `F.Cu` | Signal: front parts, microstrip over L2, RF option over L3; in the core zone the SoC decoupling and core-rail pours | 35 µm (18 plated) | 120 µm prepreg 2116 (laser) | 4.45 |
| L2 | `In1.Cu` | Ground (the core and system rails' plane in the core zone) | 25 µm (12 plated) | 90 µm prepreg 3313 (laser) | 4.45 |
| L3 | `In2.Cu` | Ground (pours in the power zone); L4's upper reference; RF ground under an L1 line | 18 µm | 430 µm core | 4.6 |
| L4 | `In3.Cu` | Stripline between L3 and L5: SoC escape, LPDDR4X, eMMC, fast I/O, MCLK | 18 µm | 90 µm prepreg 3313 (laser) | 4.45 |
| L5 | `In4.Cu` | Ground, full layer | 25 µm (12 plated) | 120 µm prepreg 2116 (laser) | 4.45 |
| L6 | `B.Cu` | Signal: RK3566, LPDDR4X, eMMC, microstrip over L5; RF option over L4 | 35 µm (18 plated) | — | — |

Laminate 1.006 mm, finished 1.046 mm with 20 µm mask per side (assumed). The 0.43 mm core is read as dielectric thickness; the fab's table lists cores "with copper" (**UNVERIFIED**: if the copper is included, the board is about 36 µm thinner, still inside PCB-S-01, and the DFM review confirms the core).

## 3. Layer roles per zone

Zones as [floorplan v1](floorplan-v1.md) §2. F fast routing (every neighbour ground), G ground, P power plane or pour.

| Zone | L1 | L2 | L3 | L4 | L5 | L6 |
|---|---|---|---|---|---|---|
| Core | P: SoC decoupling; core-rail pours between the capacitors; low-speed routing | P: SoC core and system rails (with L3 across 90 µm) | G | F: escape, LPDDR4X, eMMC, microSD, SDIO | G | F: SoC, LPDDR4X, eMMC |
| Audio | F | G | G | F: MCLK, I2S, audio analog; audio rails as tracks | G | F |
| Power | F: switch nodes over the L2 ground | G | P: battery path, VSYS | P: battery path, VSYS | G | F |
| Radio | F: RF line option (over L3, L2 cut out) | G | G | P, or G under an L6 RF line | G (cut out under an L6 RF line) | F: module, RF line |
| I/O | F: HAT and USB-C `VBUS` pours | G | G | F: USB 2, USB 3, DSI | G | F |
| Faceplate (front only) | F: FH35C | G | — | — | — | — |
| Corridors | F | G | G | F | G | F |

L5 is ground under every zone: the full-layer ground. L2 is ground under every zone but the core, L3 under every zone but the power zone, and L4 under an L6 RF line: the zone-local grounds, each stitched to L5 (§4.2). DRC refuses copper of any other net on L5, on L2 outside the core zone and on L3 outside the power zone (PCB-S-25).

**Why these maps.** The SoC side (L6) needs ground under it (L5); the escape's inner layer, two laser levels in, is L4, and it needs ground on both sides (L3, L5); that leaves L1 and L2 for the core's power, and L1 holds the SoC's decoupling (PCB-P-10). So the core and system rails share L2, paired with the L3 ground, and the core rails also pour on L1 between the capacitors. MCLK needs a stripline between two grounds (PCB-I-09): L4 between L3 and L5 in the audio zone. The I/O zone's nine pairs use L4 besides the outer layers. The power zone uses L3 and L4 for the 5 A battery path and VSYS (PCB-P-01), with L2 and L5 ground under the switch nodes (PCB-P-08). The radio zone makes L4 ground under an L6 RF line, 235 µm under it (PCB-R-03), or runs the line on L1 over L3.

## 4. Rules

### 4.1 Reference planes

1. **Impedance classes route only on L1, L4 and L6** (PCB-S-14), and only where the layer's references are ground in its zone: not on L1 in the core zone (L2 is the rail plane there), not on L4 in the power zone (pours) nor in the radio zone (power or RF ground). DRC checks it by zone.
2. **Edge margins.** A fast pair runs at least 1.02 mm from the edge of its reference area, a DDR line at least 0.30 mm (Rockchip HSPCB pp. 11, 28; as v1 §4.1.3), at a cut-out, at the board edge and at the edge of a zone-local ground.
3. **Corridors.** A crossing between zones happens inside a declared corridor, where L2, L3 and L5 are ground (PCB-S-18, DRC), so the crossing changes no reference.
4. **Pad voids (PCB-I-10).** Under an SMD pad of a fast class on L1 the void is on L2 only, so the pad references L3, 235 µm below. On L6 the void is on L5 only and L4 under the pad is a ground fill with no route through it, so the pad references L4, 235 µm above (arithmetic: 120 + 25 + 90 µm). Chosen to mirror L1.

### 4.2 Return vias and stitching

1. **L6↔L4** through stacked microvias (L6–L5–L4): L4's references are L3 and L5, and no microvia crosses the core, so a ground through via within 0.76 mm (0.64 mm for `DDR_*`) of the signal via joins L5 and L3, symmetric for pairs (PCB-S-10). **L1↔L3 is not a signal change** (L3 is not a routing layer).
2. **L1↔L4 and L1↔L6** through a through via: L1's reference L2 and L4/L6's references L3/L5 are all ground only outside the core zone and in the corridors, so such a change happens there, with one ground through via within 0.76 mm (PCB-S-10).
3. **One ground.** L5 is continuous; every zone-local ground (L2, L3, L4 under an RF line) is stitched to it by ground vias on the PCB-S-13 grid and along every edge of its area (PCB-S-19). No split anywhere (PCB-A-01).
4. **Delay** differs per layer: 5.84–6.18 ps/mm outer, 7.07–7.08 ps/mm on L4 (§5). A matched group that changes layers is matched in delay, not in length (PCB-S-15).

### 4.3 Power

1. **Core zone (trades 1 and 2).** L2 carries the SoC core and LPDDR4X rails (vdd_cpu, vdd_logic, vdd_gpu, vdd_npu, vcc_ddr, vcc0v6_ddr) and the system rails (vcca_1v8, vdda_0v9, vcc3v3_sys, vcc_1v8 and the PMU and I/O rails), paired with the L3 ground across 90 µm of 3313 (PCB-S-12): 43.8 pF/cm² (arithmetic, ε0·4.45 / 90 µm). On one layer the system rails' areas reach the package edge and the core rails' do not, so the core rails also pour on L1, between the decoupling capacitors, from their regulators on the front: with that feed every core rail has more copper at the package edge than its design current needs (IPC-2221 inner, ΔT 10 °C; escape study table) (PCB-S-20). vcca_1v8 and vdda_0v9 interleave under the package and are joined by short tracks on L4, on L2 through the other rails' pours, or on L1; a layout draws each join as one track, with no neck where two meet (PCB-S-21, PCB-W-01). vcc0v6_ddr, vccio6_1v8, vccio_sd and vdda_0v9 (0.1–0.4 A) do not reach the package edge on their plane and are fed by a track at layout.
2. **Power zone (trade 4):** L3 and L4 carry the battery path (5 A, PCB-P-01: a pour on two or more inner layers, met with two) and the VSYS trunk (PCB-P-02), with L1 and L6 copper where the width asks for it; L2 and L5 stay ground under the switch nodes (PCB-P-08) (PCB-P-23).
3. **I/O zone (trade 3):** no inner layer carries power there (L2, L3, L5 ground, L4 the fast layer). The HAT `VBUS` (`HAT_5V`, 4.5 A fault ceiling, PCB-P-20) runs as an outer pour at least 2.4 mm wide, the USB-C `VBUS` (PCB-P-03) at least 1.4 mm and the 5.1 V source (PCB-P-04) at least 1.1 mm, on L1 (the I/O front is 20 % used in floorplan v1) and on L6 where the battery-contact window leaves room. DRC refuses these nets on an inner layer in the I/O zone (PCB-P-22).
4. **Audio zone (trade 5):** no audio power layer; §4.6.
5. **Power next to power** (L3–L4 in the power zone) is allowed; no impedance class or clock routes next to a power layer.

### 4.4 Crosstalk on L4 (trade 7)

L4 lies 430 µm under L3 and 90 µm over L5, so two traces on it couple more at a given spacing than on an inner layer between two near grounds. Near-end coefficient Kb of two SE50 traces (102.5 µm) on L4, `odapkit stackup coupling` on the `[[coupling]]` cases of the TOML:

| Spacing (edge to edge) | Offset centre to centre | Kb |
|---|---|---|
| 1 × W (102.5 µm) | 205 µm | 8.82 % |
| 2 × W (205 µm) | 307.5 µm | 3.81 % |
| 3 × W (307.5 µm) | 410 µm | 1.85 % |

So LPDDR4X (`DDR_50SE`, `DDR_100D`) on L4 keeps at least 3 × W = 307.5 µm from every other net, the two halves of a DQS or CK pair excepted (PCB-S-24, DRC); MCLK keeps 3 × W = 307.5 µm, held as 0.31 mm (PCB-I-09, DRC). On the outer layers PCB-I-05's 2 × W (3 × W around DQS and CK) stays.

### 4.5 RF ground (PCB-R-03)

1. RF microstrip on L6 over the radio zone's L4 ground with L5 cut out under the line, or on L1 over L3 with L2 cut out. Line to ground: 235 µm (230–240 µm required).
2. The cut-out is 1.6 mm wide, centred on the line, along its whole length and 0.6 mm past each end (rule area `RF_CUTOUT` on the cut layer and the pour layer of the line's side: `In4.Cu` and `In3.Cu` for an L6 line, `In1.Cu` and `In2.Cu` for an L1 line). Geometry, same-layer ground at ≥ 0.6 mm and the U.FL keep-out as v1 §4.4.

### 4.6 Audio area (PCB-A-01, A-07, A-20; trade 5)

Under `AUDIO_ANALOG`: L2, L3 and L5 ground (PCB-S-25); L4 carries only the zone's analog, reference, MCLK and DAC serial-port nets and the audio rails; the audio rails (`PWR_AMP`, `PWR_AUDIO`) run as tracks at PCB-P-06's 0.3 mm on L1, L4 or L6, and no inner layer carries a pour of any net but ground there (PCB-A-20, DRC). The partition itself (one ground, no foreign track under the analog area) is unchanged.

### 4.7 Core-zone routing (trades 6 and 8)

The core routes on L4 and L6, with low-speed nets on L1 between the decoupling capacitors; there is no spare routing layer, and no fallback layer: L1 holds the decoupling (PCB-P-10). The outer widths (§5) are wider than v2's, which costs LPDDR4X room on L6. The routing capacity is proven at placement (§7); a shortfall there goes back to the maintainers as a stackup question (PCB-S-22).

## 5. Trace geometry per class

Computed with `odapkit stackup design`, checked with `check` (2D quasi-static field solver; etch and fab corners assumed as v1). Widths drawn; gaps edge to edge.

| Geometry | Net classes | Layer (reference) | Target | Width | Gap | Z (solver) | ε_eff | Delay ps/mm |
|---|---|---|---|---|---|---|---|---|
| SE50 outer | `DDR_50SE`, `EMMC_SD_50SE`, `I2S_50SE` | L1 (L2), L6 (L5) | 50 Ω | 188.0 µm | — | 50.00 Ω | 3.43 | 6.18 |
| D90 outer | `USB2_90D`, `USB3_90D` | L1 (L2), L6 (L5) | 90 Ω | 126.0 µm | 100 µm | 90.00 Ω | 3.06 | 5.84 |
| D100 outer | `MIPI_100D`, `DDR_100D` | L1 (L2), L6 (L5) | 100 Ω | 135.5 µm | 175 µm | 100.02 Ω | 3.10 | 5.87 |
| SE50 inner | `DDR_50SE`, `EMMC_SD_50SE`, `I2S_50SE`, `MCLK_50SE` | L4 (L3/L5) | 50 Ω | 102.5 µm | — | 50.00 Ω | 4.50 | 7.07 |
| D90 inner | `USB2_90D`, `USB3_90D` | L4 (L3/L5) | 90 Ω | 97.0 µm | 150 µm | 89.98 Ω | 4.51 | 7.08 |
| D100 inner | `MIPI_100D`, `DDR_100D` | L4 (L3/L5) | 100 Ω | 89.0 µm | 250 µm | 100.05 Ω | 4.50 | 7.08 |
| RF50 | `RF_50SE` | L1 (L3, L2 cut out), L6 (L4, L5 cut out) | 50 Ω | 391 µm | ground ≥ 600 µm | 50.01 Ω | 3.35 | 6.11 |

No class needs the 0.075 mm option: the narrowest is 89.0 µm (84.6 µm at the −5 % DRC band).

### 5.1 Tolerance sensitivity

Each parameter moved alone to the end of an assumed fab range (dielectric ±10 %, Dk ±5 %, width ±10 µm, copper ±15 %); change in Z at the low and high end, Ω.

| Geometry | Dielectric | Dk | Width | Copper | RSS | Arithmetic worst case | ±10 % window |
|---|---|---|---|---|---|---|---|
| SE50 outer | −2.9 / +2.7 | +1.2 / −1.1 | +1.4 / −1.3 | +0.4 / −0.4 | 3.5 | 44.3–55.7 | 45–55 |
| D90 outer | −2.4 / +2.0 | +2.0 / −1.8 | +5.1 / −5.0 | +1.9 / −1.8 | 6.3 | 79.0–101.0 | 81–99 |
| D100 outer | −3.7 / +3.2 | +2.2 / −2.1 | +4.1 / −3.9 | +1.6 / −1.5 | 6.2 | 88.9–111.1 | 90–110 |
| SE50 inner | −2.5 / +2.4 | +1.3 / −1.2 | +2.2 / −2.0 | +0.6 / −0.5 | 3.7 | 43.7–56.4 | 45–55 |
| D90 inner | −3.0 / +2.6 | +2.3 / −2.2 | +4.9 / −4.5 | +1.4 / −1.4 | 6.4 | 78.9–101.3 | 81–99 |
| D100 inner | −3.9 / +3.4 | +2.6 / −2.4 | +5.1 / −4.7 | +1.4 / −1.4 | 7.1 | 87.7–112.7 | 90–110 |
| RF50 | −2.6 / +2.4 | +1.2 / −1.1 | +0.7 / −0.7 | −0.2 / +0.2 | 2.9 | 45.5–54.4 | 45–55 |

The RSS fits every window; the arithmetic worst case fits only RF50, as in v1 and v2: the fab order requests impedance control with coupons for every class (PCB-S-05). A 5 % width error moves Z by about 2–3 %; the DRC width bands are ±5 %.

## 6. Changes from v2

| Where | v2 | v3 |
|---|---|---|
| Layers, build, thickness | 8, 2+4+2, 1.002 mm | 6, 2+2+2, 1.046 mm |
| Dielectrics | 3313 / 2116 / core 130 / 3313 / core 130 / 2116 / 3313 | 2116 / 3313 / core 430 / 3313 / 2116 |
| Press cycles | 3 | 2 |
| Grounds | L7 full; L2, L3, L5, L6 zone-local | L5 full; L2, L3 (and L4 under an L6 RF line) zone-local |
| Power | L4 core rails, L2 system rails (core zone); L3–L6 pours (power zone); L4 audio rails and I/O `VBUS` | L2 core and system rails, L1 core-rail pours (core zone); L3–L4 pours (power zone); audio rails as tracks; I/O `VBUS` as outer pours |
| Core-rail pairing | L4/L5, 90 µm (3313) | L2/L3, 90 µm (3313), on the front side |
| Routing layers for impedance classes | L1, L6, L8 | L1, L4, L6 |
| KiCad layer of the inner routing layer | `In5.Cu` | `In3.Cu` |
| RF cut-out and pour, back side | `In6.Cu`, `In5.Cu` | `In4.Cu`, `In3.Cu` |
| Outer widths | SE50 134.5, D90 101.5, D100 104.5 µm | 188.0, 126.0, 135.5 µm |
| Inner widths | SE50 90.5, D90 95.5, D100 85.5 µm | 102.5, 97.0, 89.0 µm |
| LPDDR4X spacing on the inner layer | 2 × W (3 × W around DQS and CK) | 3 × W, DRC (PCB-S-24) |
| Applied in | — | `hardware/rules/netclasses.toml`, `t1-main-board.kicad_dru` (layer names, widths, PCB-S-14 by zone, S-18, S-24, S-25, P-22, A-20), constraints v0.15 |

## 7. Debt by level (RFC 0010)

| Item | Level | Closes it |
|---|---|---|
| The fab confirms the stack, the 0.43 mm core as dielectric thickness, Dk at frequency, the 25 µm on L2/L5, the 0.10 mm laser in 120 µm of 2116 (aspect 1.2) on the first level, the thickness tolerance at 1.046 mm, the removal of non-functional pads | Q0 | DFM review |
| Core-rail PDN impedance with the 90 µm pairing, the shared L2 plane, the L1 feeds and the front decoupling, against Rockchip's targets | Q1 | PDN simulation at layout |
| Coupons for every class in §5, measured | Q1 | First fab order |
| Loss budget of USB 3 at these widths | Q1 | Layout |
| Core-zone routing capacity on L4 and L6 at the v3 widths and the 3 × W LPDDR4X spacing (escape proven; LPDDR4X, eMMC and onward routes at placement) | Q1 | Placement and routing |
| Zone-local ground stitching pitch and fence pitch (PCB-S-13, S-19) measured on the pre-compliance scan | Q2 | Pre-compliance |
| Heat spreading under the SoC with six copper layers (PCB-S-23) | Q2 | Thermal check, V4-03 |
| Board flex at 1.046 mm under the SoC (screw torque, drop) | Q2 | First articles |
