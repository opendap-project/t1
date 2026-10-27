# Stackup v1 of the T1 main board

- **Superseded (2026-10-25)** by [stackup v2](stackup-v2.md): eight layers, zoned layer roles, one full-layer ground. Kept as the record of the ten-layer stack; the rules, net classes and constraints follow v2.
- **Status:** Draft v1 (2026-10-24). The layer stack and the trace geometry of every impedance class. The fab stack-up request is deferred, so every value comes from the fab's published data or is a stated assumption. **The stack is to be confirmed by the fab's DFM review**; their answer replaces the assumptions and the widths are recomputed before the net classes freeze. Nothing here is laid out or measured.
- **Note (2026-10-25, [RFC 0014](https://github.com/opendap-project/rfcs/blob/main/text/0014-hat-interface-v2-usb-only.md)):** HATs are USB only. The net classes `PCIE_85D`, `PCIE_REFCLK_100D` and `HAT_EXT_100D` are withdrawn from the board ([PCB design constraints](pcb-design-constraints.md) v0.12: PCB-I-03, I-12 and I-13 withdrawn; `MIPI_100D` is DSI only). Their rows below, the D85 classes included, stay as solved and are not used by any net; the stack itself is unchanged.
- **Machine-readable copy:** [`../../hardware/stackup/stackup-v1.toml`](../../hardware/stackup/stackup-v1.toml). The tables in §2 and §5 come from it through `odapkit stackup check` ([toolkit-hardware](https://github.com/opendap-project/toolkit-hardware), method in its [`docs/specs/stackup-method.md`](https://github.com/opendap-project/toolkit-hardware/blob/main/docs/specs/stackup-method.md)); a change edits the TOML, reruns the check and then this page.
- **Inputs:** [PCB design constraints](pcb-design-constraints.md) §3 (PCB-S-01 to S-13), §5 (PCB-I-01 to I-13), §7 (PCB-A), §8 (PCB-R-03); [ADR 0016](../adr/0016-front-side-height-under-the-display.md) (board 1.0–1.2 mm in the z stack); [`hardware/rules/netclasses.toml`](../../hardware/rules/netclasses.toml); Rockchip HDG 1.1 and HSPCB 1.0; the USB, PCIe and MIPI D-PHY specifications; industry practice for stackups (gaps G-01 to G-05); kicad-lib's [fab rule sets](https://github.com/opendap-project/kicad-lib/tree/main/design-rules) ([P1]–[P3], [P12], [P16] there); Murata LBES5PL2EL-923 (Type 2EL): *Hardware Application Note* E2B-09-1413 Rev. 9.0 §3.5.1, *Radio Law Certification Application Note* CER-0248 Rev. 6.0 §2.1.6.2; hat-standard [ADR 0005](https://github.com/opendap-project/hat-standard/blob/main/docs/adr/0005-interface-v1-1-shared-extension-and-contact-reduction.md) (TMUXHS4412 extension switch).

## Sources

| Key | Source | Read |
|---|---|---|
| [PW-ST] | The fab, *Multi-layer laminated structure* (298 standard stack-ups with prepreg and core Dk and pressed thicknesses), <https://www.pcbway.com/multi-layer-laminated-structure.html> | 2026-10-24 |
| [PW-PP] | The fab, *Cores, Foil & Prepreg for PCBs* (prepregs offered: 1080 0.080–0.086 mm, 2116 0.109–0.115 mm, 7628; cores; copper foils 12/18/36 µm; outer plating 20–30 µm), <https://www.pcbway.com/pcb_prototype/Cost_cores_Foil___Prepreg_for_PCBs.html> | 2026-10-24 |
| [P1], [P2], [P3], [P12], [P16] | The prototype fab's published capability pages, as cited in kicad-lib's `pcbway-*` rule sets (thickness tolerance, impedance ±10 %, minimum dielectric 50 µm, laser drill 4 mil standard and 8 mil maximum with dielectric ≤ 0.15 mm, HDI builds and examples, materials including Shengyi S1000-2M) | 2026-10-22 |
| [KC] | KiCad source, `common/transline_calculations/microstrip.cpp`, `MICROSTRIP::microstrip_Z0()` (master), the model behind KiCad's transmission-line calculator | 2026-10-24 |

The fab's stack-up table gives prepreg 1080 RC68 % Dk 4.21, 3313 and 2116 RC58 % Dk 4.45, 7628 RC46 % Dk 4.74, and core Dk 4.6 [PW-ST]. It names neither the laminate brand nor the frequency of those values. The Shengyi S1000-2M datasheet (PCB-S-06's material) was not retrieved, so applying the fab's table to S1000-2M is **UNVERIFIED**; no Df is used anywhere here.

## 0. Summary

1. **Ten layers, HDI 2+6+2, 1.07 mm nominal.** Four routing layers (L1, L3, L8, L10), each next to a solid ground plane; the two inner routing layers are true striplines between two grounds; four ground planes (L2, L4, L7, L9); two power planes (L5, L6), each paired with a ground at 65 µm. The stack is symmetric. 1.07 mm nominal plus the fab's ±0.10 mm stays within PCB-S-01's 1.2 mm.
2. **Why ten, not eight.** Eight layers give the same four routing layers but only three ground planes. One routing layer would then sit against a power plane, which PCB-S-11 forbids for every fast class and PCB-I-09 forbids for MCLK. Ten layers also give the SoC core and LPDDR4X rails a plane of their own, paired with ground (PCB-S-12), and keep the audio area's planes clean (§4.5). The cost difference is not quoted (**UNVERIFIED**).
3. **Why 2+N+2.** L9 (and L2) are ground planes, so an inner-ring RK3566 ball reaches a routing layer (L8) only through a second microvia level: L10→L9→L8, stacked and copper-filled. A 1+N+1 build would need L9 as a routing layer, which loses L10's adjacent ground (PCB-S-12). The fab publishes a 10-layer 2nd-order HDI example at 1.3 mm [P3]; this stack is thinner than that example.
4. **The RF microstrip gets its deep ground without a special stack.** L1→L3 (and L10→L8) is 235 µm, inside Murata's 230–240 µm (PCB-R-03). Under the RF line L2 is cut out 1.6 mm wide and L3 carries a local ground pour. The line is 391 µm wide; Murata's own rule (W = 1.8 × H) gives 423 µm, within the ±0.25 mm Murata allows.
5. **Every class has a geometry at its target** (§5). Outer widths are 101.5–134.5 µm. Inner widths are 75–98.5 µm: the inner 50 Ω and 100 Ω classes are below PCB-G-01's general 0.1 mm and need an exception for impedance classes (§7).
6. **Tolerances.** The root sum of the fab corners stays within ±10 % for every class (2.9–8.2 Ω). The arithmetic worst case does not, as is usual: the fab holds ±10 % by compensating the width against its coupon [P1], which the order must request.

## 1. Build

| Item | Value | Source |
|---|---|---|
| Layers | 10 | PCB-S-03 (8–10) |
| Build | HDI 2+6+2: core L3–L8 (three cores, two prepregs), then two sequential laminations per side | PCB-S-02; the fab 2nd order [P3] |
| Microvias | L1–L2 and L10–L9: 0.10 mm laser, 0.25 mm land (PCB-G-03), in 90 µm of 3313 (aspect 0.9). L2–L3 and L9–L8: 0.125 mm laser, 0.275 mm land, in 120 µm of 2116 (aspect 0.96). Stacked and copper-filled | Fab laser 4 mil standard, 8 mil maximum, dielectric ≤ 0.15 mm [P3]; copper-filled stacking [P2, P16]. The 0.125 mm second level is **UNVERIFIED** until the DFM review; if the fab accepts 0.10 mm in 120 µm (aspect 1.2), the land returns to 0.25 mm |
| Through vias | 0.20 mm drill, 0.45 mm pad (PCB-G-04), L1–L10; aspect ratio 1.07 / 0.20 = 5.4 | The fab 0.20 mm up to 1.6 mm thick [P1] |
| Buried vias | None in v1. L3 and L8 stay unplated at 18 µm, which the inner widths assume. If the escape study needs L3–L8 buried vias, L3 and L8 get plated and every inner width is recomputed | — |
| Stub of a through via used L3↔L8 | 270 µm to L1 and to L10 (arithmetic: 35 + 90 + 25 + 120) | Under Rockchip's 0.30 mm "simulate" threshold (HSPCB p. 10) |
| Material | FR-4 Tg 170 (Shengyi S1000-2M offered by the fab [P2, P16]); Dk from [PW-ST] | PCB-S-06. A high-speed class only if the USB 3 / PCIe loss budget asks for it |
| Finish | ENIG | PCB-S-07 |
| Thickness | 1.074 mm nominal (copper, dielectrics and 20 µm mask per side); by the fab's own convention (laminate with base outer copper, plus 0.10 mm) 1.10 mm. Either way ≤ 1.2 mm with ±0.10 mm | PCB-S-01; ±0.10 mm is the fab's T ≤ 1.0 mm row [P1], assumed to hold at 1.1 mm (**UNVERIFIED**) |

## 2. Layer table

Top is the front (faceplate side, +z); the SoC, LPDDR4X and eMMC sit on the back (L10), their decoupling on the front (ADR 0016, PCB-P-10). Dielectric thicknesses are pressed, copper surface to copper surface. "z" is the depth of the layer's top surface below the top of the mask.

| Layer | Role | Copper (finished) | Dielectric below | Dk | z (µm) |
|---|---|---|---|---|---|
| Mask | LPI solder mask | — | 20 µm (**assumed**) | 3.8 (**assumed**) | 0 |
| **L1** | Signal: front parts, SoC decoupling, FH35C breakout, microstrip, RF option | 35 µm (18 base + plating [PW-PP]) | 90 µm prepreg 3313 | 4.45 | 20 |
| **L2** | Ground plane | 25 µm (12 base + plating, **assumed**) | 120 µm prepreg 2116 | 4.45 | 145 |
| **L3** | Signal: stripline (L2/L4) | 18 µm | 103 µm core | 4.6 | 290 |
| **L4** | Ground plane | 18 µm | 65 µm prepreg 1080 | 4.21 | 411 |
| **L5** | Power: SoC core and LPDDR4X rails | 18 µm | 50 µm core | 4.6 | 494 |
| **L6** | Power: system rails, battery and VSYS pours, audio rails in the audio area | 18 µm | 65 µm prepreg 1080 | 4.21 | 562 |
| **L7** | Ground plane | 18 µm | 103 µm core | 4.6 | 645 |
| **L8** | Signal: stripline (L7/L9) | 18 µm | 120 µm prepreg 2116 | 4.45 | 766 |
| **L9** | Ground plane | 25 µm (**assumed**) | 90 µm prepreg 3313 | 4.45 | 904 |
| **L10** | Signal: RK3566, LPDDR4X, eMMC, microstrip, RF option | 35 µm | — | — | 1019 |
| Mask | LPI solder mask | — | 20 µm (**assumed**) | 3.8 (**assumed**) | 1054 |

Prepreg and core thicknesses are values the fab lists for these glass styles after pressing [PW-ST]; the real pressed thickness depends on each layer's copper density and is the fab's to state. The 50 µm L5–L6 core is the fab's minimum impedance dielectric [P12]; no impedance class references it.

**Copper for power.** PCB-P assumes 35 µm outer and 18 µm inner, which this stack keeps, so the PCB-P widths stand. 35 µm on L5 and L6 would halve the inner widths of PCB-P-01 to P-03 but costs 34 µm of thickness, which the 1.2 mm budget does not have; the battery and VSYS paths use pours on L6 plus the outer layers.

## 3. Assignment of interfaces to layers

A starting assignment for the escape study and placement. L3 and L8 are equivalent striplines, so an interface may move between them without new geometry.

| Interface | Class | Layers | Why |
|---|---|---|---|
| LPDDR4X byte lanes and CA, DQS, CK | `DDR_50SE`, `DDR_100D` | L10 (escape and short runs), L8 | SoC and LPDDR4X on the back; Rockchip's templates route DDR on an outer and an inner layer (RK3566 layout rules §1.1); L8 is the stripline next to them |
| eMMC (HS200) | `EMMC_SD_50SE` | L10, L8 | eMMC on the back next to the SoC |
| microSD (SDR104), SDIO to the radio | `EMMC_SD_50SE` | L8, L10 | Socket in the back top band (PCB-Z-02) |
| USB 3, PCIe, CSI-2 from the SoC through the two TMUXHS4412 to the DF40 | `USB3_90D`, `PCIE_85D`, `PCIE_REFCLK_100D`, `HAT_EXT_100D` | L8 | Inner, between grounds: Rockchip puts high-speed and clock routes inside above four layers (HDG p. 96); the switch and its short port segments on L10 (PCB-I-13) |
| USB 2 to the USB-C (bottom edge) and HAT | `USB2_90D` | L3 or L8 | Inner run to the bottom band |
| DSI to the FH35C (front, under the display) | `MIPI_100D` | L3, breakout on L1 | Front connector; L3 is the stripline nearest to it |
| MCLK (oscillators → divider → CS43198 XTI) | `MCLK_50SE` | L3 or L8 only | PCB-I-09: stripline between two grounds, no reference change |
| I2S to the DAC | `I2S_50SE` | L3, L8, outer near the pads | — |
| Radio RF (module pins to U.FL, case-antenna branch) | `RF_50SE` | L1 or L10, the module's side | §4.4 |
| SoC core, GPU, NPU, LPDDR4X VDD2/VDDQ | — | L5 (with L4 at 65 µm) | PCB-S-12: paired with ground, on the side nearer the front decoupling |
| VSYS, 3V3, 1V8, 5V1, HAT rails, battery path, amplifier and DAC rails | — | L6 (with L7 at 65 µm), outer pours | — |

## 4. Rules

### 4.1 Reference planes

1. L2, L4, L7 and L9 are solid ground: no routing, no split. Openings are limited to via antipads, the RF cut-outs (§4.4) and the pad voids of PCB-I-10.
2. Impedance-controlled and fast classes route only on L1, L3, L8 and L10, never on L5 or L6. Each routing layer is adjacent only to ground, so the ground-to-power reference swap of PCB-S-11 cannot occur on a signal layer change; PCB-S-11's stitching capacitor remains for routes forced onto L5/L6 by the escape study, which this stack does not plan.
3. A fast pair runs at least 1.02 mm from the edge of its reference plane (Rockchip HSPCB p. 11); a DDR line at least 0.30 mm (HSPCB p. 28). This applies to the RF cut-out edges and the board edge.
4. Pad voids of PCB-I-10 ("two layers deep"): under an SMD pad on L1 the void is on L2 and L3, so the pad references L4 (356 µm below, arithmetic); mirrored for L10.

### 4.2 Return vias at layer changes

1. **L1↔L3 and L10↔L8** through stacked microvias: both layers reference L2 (L9), which the via passes through; one ground microvia stack within 0.76 mm (0.64 mm for `DDR_*`) of the signal via, symmetric for pairs (PCB-S-10).
2. **L3↔L8** through a 0.20 mm through via: the references change from L2/L4 to L7/L9, all ground. One ground through via within 0.76 mm (0.64 mm for `DDR_*`), symmetric for pairs (PCB-S-10).
3. **Outer↔outer or outer↔inner across the core** (L1↔L8, L3↔L10): through via, same ground stitching rule.
4. Delay differs per layer: about 5.9–6.2 ps/mm outer and 7.09 ps/mm inner (§5). A matched group that changes layers is matched in delay, not in length.

### 4.3 Splits and power planes

1. No split ground anywhere (PCB-A-01).
2. L5 and L6 are divided into rail areas; each area stays over its loads with no neck narrower than its PCB-P width. No fast line crosses a power-area boundary, because none references L5 or L6 (rule 4.1.2).
3. No general pull-back of power planes from the ground edge (constraints §3 note; Hubing, IW-SR-05).

### 4.4 RF microstrip (PCB-I-07, PCB-R-03, PCB-R-10)

1. The line is on the module's side: L1 over a local ground pour on L3, or L10 over L8. The ground-to-line distance is 235 µm (230–240 µm required).
2. L2 (L9) is cut out 1.6 mm wide, centred on the line, along its whole length and 0.6 mm past each end. The cut-out width was set with the solver: 1.6 mm keeps the line within 0.25 Ω of an infinitely wide cut-out; 1.2 mm costs 0.6 Ω and 0.6 mm costs 6 Ω.
3. The L3 (L8) pour under the line is at least the cut-out plus 0.5 mm per side. It carries no other net, and it is stitched to L2 and L4 (L9 and L7) by a via row along each cut-out edge (pitch per PCB-S-13, ≤ 2.5 mm **UNVERIFIED**).
4. Same-layer ground copper stays at least 0.6 mm from the line edges: with a 1.2 mm cut-out, a pour at 0.6 mm lowers the line by 0.16 Ω and one at 0.2 mm by 3.8 Ω. The 391 µm width is solved with both the cut-out and this pour present.
5. The ≥ 0.8 mm copper keep-out under each U.FL (Murata E2B-09-1413 Figure 13) applies to L2 and to the L3 pour under the connector. That it must reach that deep is **UNVERIFIED** until Murata's U.FL layout file is copied.
6. The case-antenna branch of PCB-R-10 uses the same geometry and cut-out.

### 4.5 Audio area (PCB-A-01, A-07)

Under the `AUDIO_ANALOG` rule area: L2, L4, L7 and L9 stay solid ground; L3 and L8 carry only audio analog and reference nets; L5 and L6 carry only the audio rails (VA, the ±6 V and ±7 V amplifier rails) or ground fill, never a switching-converter or SoC rail.

### 4.6 Ground stitching

The four ground planes are joined by through vias on a grid with an edge fence (PCB-S-13; pitch **UNVERIFIED**). Every microvia stack that carries ground joins L1, L2 and L3 (or L10, L9, L8) to the through-via grid near it.

## 5. Trace geometry per class

Computed with `odapkit stackup check` (2D quasi-static field solver, toolkit-hardware). Widths are drawn widths; the solve uses the mean of a trapezoid narrower by 10 µm (outer) or 6 µm (inner) at the top (**assumed** etch). Gaps are drawn, edge to edge. Inner rows hold for L3 and L8, outer rows for L1 and L10; the mirrored layers give identical results.

| Geometry | Net classes | Layer (reference) | Target | Width | Gap | Z (solver) | ε_eff | Delay ps/mm | Z_odd / Z_common |
|---|---|---|---|---|---|---|---|---|---|
| SE50 outer | `DDR_50SE`, `EMMC_SD_50SE`, `I2S_50SE` | L1 (L2), L10 (L9) | 50 Ω | 134.5 µm | — | 50.02 Ω | 3.45 | 6.19 | — |
| D90 outer | `USB2_90D`, `USB3_90D` | L1 (L2), L10 (L9) | 90 Ω | 101.5 µm | 100 µm | 89.99 Ω | 3.11 | 5.89 | 45.0 / 33.4 Ω |
| D85 outer | `PCIE_85D` | L1 (L2), L10 (L9) | 85 Ω | 118.0 µm | 100 µm | 85.06 Ω | 3.13 | 5.90 | 42.5 / 31.1 Ω |
| D100 outer | `MIPI_100D`, `PCIE_REFCLK_100D`, `DDR_100D`, `HAT_EXT_100D` | L1 (L2), L10 (L9) | 100 Ω | 104.5 µm | 175 µm | 100.00 Ω | 3.16 | 5.93 | 50.0 / 30.8 Ω |
| SE50 inner | `DDR_50SE`, `EMMC_SD_50SE`, `I2S_50SE`, `MCLK_50SE` | L3 (L2/L4), L8 (L7/L9) | 50 Ω | 78.5 µm | — | 50.01 Ω | 4.52 | 7.09 | — |
| D90 inner | `USB2_90D`, `USB3_90D` | L3, L8 | 90 Ω | 86.0 µm | 150 µm | 90.03 Ω | 4.52 | 7.09 | 45.0 / 25.5 Ω |
| D85 inner | `PCIE_85D` | L3, L8 | 85 Ω | 98.5 µm | 150 µm | 84.96 Ω | 4.52 | 7.09 | 42.5 / 23.9 Ω |
| D100 inner | `MIPI_100D`, `PCIE_REFCLK_100D`, `DDR_100D`, `HAT_EXT_100D` | L3, L8 | 100 Ω | 75.0 µm | 250 µm | 100.10 Ω | 4.52 | 7.09 | 50.1 / 25.9 Ω |
| RF50 | `RF_50SE` | L1 (L3, L2 cut out), L10 (L8, L9 cut out) | 50 Ω | 391 µm | ground ≥ 600 µm | 50.00 Ω | 3.35 | 6.11 | — |

Gap choices: outer 90 Ω and 85 Ω pairs at the 0.1 mm general space (PCB-G-01); outer and inner 100 Ω pairs loosely coupled (175 and 250 µm), which keeps the width up and suits MIPI D-PHY, whose lanes also signal single-ended in low-power mode (the USB, PCIe and MIPI D-PHY specifications, TI note "must be loosely coupled"); inner 85/90 Ω pairs at 150 µm. Spacing to other nets follows each class's rule (3–5 × W, PCB-I-01 to I-06).

### 5.1 Tolerance sensitivity

Each parameter moved alone to the end of an assumed fab range: dielectric thickness ±10 %, Dk ±5 %, width ±10 µm, copper thickness ±15 % (ranges **assumed**; the fab publishes only the impedance tolerance ±10 % [P1]). Values are the change in Z at the low and high end.

| Geometry | Dielectric ±10 % | Dk ±5 % | Width ±10 µm | Copper ±15 % | RSS | Arithmetic worst case | ±10 % window |
|---|---|---|---|---|---|---|---|
| SE50 outer | −2.9 / +2.7 | +1.2 / −1.1 | +1.8 / −1.7 | +0.5 / −0.5 | 3.6 Ω | 43.9–56.2 Ω | 45–55 Ω |
| D90 outer | −2.8 / +2.4 | +2.0 / −1.9 | +5.7 / −5.4 | +2.0 / −1.9 | 6.9 Ω | 78.1–102.0 Ω | 81–99 Ω |
| D85 outer | −2.9 / +2.5 | +1.9 / −1.8 | +5.0 / −4.8 | +1.8 / −1.6 | 6.3 Ω | 73.9–96.2 Ω | 76.5–93.5 Ω |
| D100 outer | −4.1 / +3.6 | +2.2 / −2.1 | +4.9 / −4.6 | +1.7 / −1.6 | 7.0 Ω | 87.7–112.4 Ω | 90–110 Ω |
| SE50 inner | −2.6 / +2.4 | +1.3 / −1.2 | +2.8 / −2.5 | +0.8 / −0.7 | 4.1 Ω | 43.0–57.3 Ω | 45–55 Ω |
| D90 inner | −3.6 / +3.1 | +2.3 / −2.2 | +5.4 / −4.9 | +1.6 / −1.5 | 7.1 Ω | 77.9–102.5 Ω | 81–99 Ω |
| D85 inner | −3.7 / +3.2 | +2.2 / −2.1 | +4.7 / −4.4 | +1.4 / −1.3 | 6.5 Ω | 73.6–96.5 Ω | 76.5–93.5 Ω |
| D100 inner | −4.6 / +4.1 | +2.6 / −2.4 | +6.0 / −5.3 | +1.6 / −1.5 | 8.2 Ω | 86.3–114.4 Ω | 90–110 Ω |
| RF50 | −2.6 / +2.4 | +1.2 / −1.1 | +0.7 / −0.7 | −0.2 / +0.2 | 2.9 Ω | 45.5–54.4 Ω | 45–55 Ω |

Reading: width etch dominates the pairs, dielectric thickness the single-ended lines. The RSS fits every window; the arithmetic worst case fits only RF50. The fab order must therefore state impedance control with coupons for every class in this table, so the fab compensates the width (PCB-S-05, coupons). The same table is the reason not to go narrower than 75 µm.

### 5.2 Solver and its validation

The solver, its choice and its validation are in toolkit-hardware's [stackup method](https://github.com/opendap-project/toolkit-hardware/blob/main/docs/specs/stackup-method.md). In short: finite-element Laplace solves (scikit-fem, pinned and hash-locked, run through uv) give the capacitance matrices with and without dielectric. The solver is within 0.26 % of Cohn's exact stripline and within 0.14 % of Hammerstad and Jensen's microstrip (Wadell §3.5).

**KiCad's transmission-line calculator.** Its microstrip model [KC], evaluated as written in KiCad's source: with thin copper it agrees with the solver within 0.3 % (w 150 µm, h 90 µm, t 1 µm, Dk 4.45: 53.72 Ω against 53.55 Ω). With this stack's 35 µm outer copper on 90 µm it reads 3.3 % high (51.01 Ω against 49.36 Ω for the same 150 µm line), because it adds a thickness term to the filling factor that Hammerstad and Jensen do not; Hammerstad and Jensen give 49.37 Ω. **The width of an outer class read from KiCad's calculator would therefore come out about 7 µm too wide.** Use the TOML's values in the KiCad project. The check in KiCad's own window is open (§8).

IPC-2141A's simple formulas read 4–14 % low for these geometries and are not used.

## 6. Debt by level (RFC 0010)

| Item | Level | Closes it |
|---|---|---|
| The fab confirms the stack, pressed thicknesses, Dk at frequency, the 25 µm on L2/L9, the 0.125 mm second laser level and the thickness tolerance at 1.07–1.10 mm | Q0 (fab rules) | DFM review |
| Coupons for every class in §5, measured | Q1 | — |
| Loss budget of USB 3 and PCIe on FR-4 at the §5 widths | Q1 | — |
| Resin fill and Dk over the RF cut-out, cross-section | Q2 | Coupon with the RF line |
| U.FL keep-out depth from Murata's layout file | Q1 | Murata file copied (PCB-R-03) |

## 7. Changes for the net classes and the constraints (not applied here)

For the main session to apply in `hardware/rules/netclasses.toml` and `docs/specs/pcb-design-constraints.md`.

**`netclasses.toml`** (replace "widths and gaps from the stackup" in the header with "from `hardware/stackup/stackup-v1.toml` (stackup v1), to be confirmed by the fab's DFM"). Per class, add `stackup = "stackup-v1"` and, for outer (L1/L10) and inner (L3/L8):

| Class | Outer width / gap (µm) | Inner width / gap (µm) | Notes |
|---|---|---|---|
| `MCLK_50SE` | — (inner only) | 78.5 / — | `layers = ["L3", "L8"]` |
| `I2S_50SE` | 134.5 / — | 78.5 / — | |
| `DDR_50SE` | 134.5 / — | 78.5 / — | |
| `EMMC_SD_50SE` | 134.5 / — | 78.5 / — | |
| `USB2_90D` | 101.5 / 100 | 86.0 / 150 | |
| `USB3_90D` | 101.5 / 100 | 86.0 / 150 | |
| `PCIE_85D` | 118.0 / 100 | 98.5 / 150 | |
| `PCIE_REFCLK_100D` | 104.5 / 175 | 75.0 / 250 | |
| `MIPI_100D` | 104.5 / 175 | 75.0 / 250 | |
| `DDR_100D` | 104.5 / 175 | 75.0 / 250 | |
| `HAT_EXT_100D` (PCB-I-12; not yet in the file) | 104.5 / 175 | 75.0 / 250 | new class |
| `RF_50SE` | 391 / — | — (outer only) | `layers = ["L1", "L10"]`, reference L3 / L8, L2 / L9 cut out 1.6 mm, ground ≥ 0.6 mm |
| all impedance classes | — | — | `layers` limited to L1, L3, L8, L10 (rule 4.1.2) |

KiCad net classes hold one width per class. The schematic step either generates per-layer custom rules (`(constraint track_width)` with `(condition "A.NetClass == 'X' && A.Layer == 'In3.Cu'")`) and differential-pair gaps per layer, or splits the classes per layer; the per-layer rule keeps the class names stable.

**`pcb-design-constraints.md`:**

| Row | Change |
|---|---|
| PCB-S-01 | Target "1.07 mm nominal (stackup v1), ±0.10 mm, ≤ 1.2 mm"; source adds stackup v1 |
| PCB-S-02 | Target "2+N+2, stacked copper-filled microvias L1–L2–L3 and L10–L9–L8 (second level 0.125 mm laser **UNVERIFIED**), through vias, no buried vias in v1" |
| PCB-S-03 | Target "10 (stackup v1)"; reason: four routing layers each next to ground and two power planes paired with ground (S-11, S-12, I-09) |
| PCB-S-04, S-12 | Satisfied by stackup v1: every routing layer next to ground, L3 and L8 between two grounds, L5 and L6 each with a ground at 65 µm; enforcement "stackup v1 + REV" |
| PCB-S-05 | Target "per stackup v1: 50–120 µm"; enforced by `odapkit stackup check` |
| PCB-S-06 | Note that the Dk used is the fab's published table value (S1000-2M datasheet not retrieved, **UNVERIFIED**) |
| PCB-S-11 | Note: with stackup v1 no signal layer is next to a power plane; the stitching capacitor applies only to routes on L5/L6 |
| PCB-S-14 (new) [Q1] | Impedance-controlled classes route only on L1, L3, L8, L10, never on L5/L6; enforced by DRC (layer condition) |
| PCB-S-15 (new) [Q1] | A matched group that changes layers is matched in delay: 7.09 ps/mm inner, 5.9–6.2 ps/mm outer (stackup v1 §5); CHK |
| PCB-G-01 | Exception: impedance classes use their stackup widths, down to 0.075 mm on L3/L8 (the fab's published HDI 3/3 mil standard order option); the general 0.1 mm stays for every other net |
| PCB-I-01 to I-06, I-09, I-12 | Add the width/gap of §5 for outer and inner, citing stackup v1 |
| PCB-I-07 | "50 Ω coplanar with ground" → "50 Ω microstrip over the L3 (L8) ground, L2 (L9) cut out 1.6 mm, same-layer ground ≥ 0.6 mm (stackup v1 §4.4)"; the coplanar wording conflicts with PCB-R-03 |
| PCB-R-03 | Add "stackup v1: 235 µm (L1→L3, L10→L8), width 391 µm (Murata's rule gives 423 µm, within ±0.25 mm)"; DRC rule area `RF_CUTOUT` for the L2/L9 void and the L3/L8 pour |
| PCB-I-10 | Note: the two-layer pad void on L1 is L2 + L3, so the pad references L4 |
| §9 Open items | Add stackup v1's debt (§6) |

## 8. Open items

1. **Fab DFM review** (deferred): the whole stack, in particular pressed thicknesses per copper density, Dk at 1–5 GHz, the plated thickness of L2/L9, the 0.125 mm laser in 120 µm, the thickness tolerance around 1.1 mm, and whether the L3/L8 RF pour with an L2/L9 cut-out keeps a uniform dielectric (resin fill).
2. **Shengyi S1000-2M datasheet** not retrieved: Dk and Df at frequency, and whether the fab's table values describe it.
3. **KiCad calculator in its own window:** open. §5.2 evaluates KiCad's model as written in its source; one case entered in KiCad's PCB Calculator (Transmission lines → Microstrip, H 0.09 mm, T 0.035 mm, εr 4.45, W 0.15 mm, cover far away) should read about 51.0 Ω.
4. **Escape study:** confirms four routing layers, the absence of buried vias and of routes on L5/L6, and the L2–L3 via land at the 0.4 mm ring.
5. **Loss budget** at these widths: decides whether PCB-S-06 moves to a high-speed laminate, which changes every width.
6. **Murata's U.FL layout file:** its trace width (this stack's 391 µm must be within ±0.25 mm of it) and the keep-out depth.
