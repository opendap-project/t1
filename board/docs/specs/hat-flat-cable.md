# HAT flat cable

- **Status:** Draft v1 (2026-10-25). Nothing here is built or measured; every impedance, loss and temperature figure is computed and is confirmed only by the test coupon (§14).
- **v1 (2026-10-25, [RFC 0014](https://github.com/opendap-project/rfcs/blob/main/text/0014-hat-interface-v2-usb-only.md), [RFC 0015](https://github.com/opendap-project/rfcs/blob/main/text/0015-hat-connector-pogo-field-and-usb-c-port-hat.md)):** HATs are USB only (hat-standard [interface v2](https://github.com/opendap-project/hats/blob/main/standard/docs/specs/interface-v2.md)) and the HAT connector is the pogo field on the device-side piece. The cable carries one USB port on a DF40C-50 at each end: the 100 Ω extension pairs, the 50 Ω I2S lines, `HAT_3V3` and the low-speed and reserved lines of v0 (interface v1.1, DF40C-100) are gone. v0 is in this file's history.
- **Requirements:** BRD-013 (this repository owns the flat cable), BRD-042 (nothing in the high-speed paths limits the link), BRD-049 (margin below every rating), BRD-055 (prototype fab processes), BRD-060 (constraints with limits); hat-standard HCS-004, HCS-023, HCS-027, HCS-028.
- **Inputs:** hat-standard interface v2 §4, §5.1 and §9.2, [ADR 0004](https://github.com/opendap-project/hats/blob/main/standard/docs/adr/0004-pogo-part-and-field-geometry.md) (coupon); [ADR 0002](../adr/0002-hat-signals-leave-the-board-over-a-flat-cable.md); [BOM v1](bom-v1.md) lines 65–69, 102; [PCB design constraints](pcb-design-constraints.md) PCB-I-01, PCB-I-02, PCB-I-14, PCB-R-06, PCB-P-20, PCB-P-21; kicad-lib [`pcbway-flex`](https://github.com/opendap-project/libs/tree/main/kicad/design-rules/pcbway-flex); libs generator data `kicad/generator/parts/hirose/DF40C-50DS-0.4V(51).toml`; the Hirose DF40 catalog; the fab's *Stack-up for FPC* page (fetched 2026-10-24).
- **Computation:** impedance with toolkit-hardware's `odapkit stackup` (2D finite-element field solver, [method](https://github.com/opendap-project/tools/blob/main/hardware/docs/specs/stackup-method.md)) on [`hardware/hat-flat-cable/stackup-v0.toml`](../../hardware/hat-flat-cable/stackup-v0.toml); loss, coupling, the EMI-film comparison and the power sizing with [`sim/flex-impedance`](../../sim/flex-impedance/README.md), a 2D finite-difference solver that agrees with `odapkit stackup` within 1 Ω on these striplines. Both run 2026-10-25.
- **Conventions:** **UNVERIFIED** = no primary source checked. *Input from the case* = a value the case repository sets; this spec assumes a range and says so. Rule IDs `HFC-nn` carry their RFC 0010 quality level; an untagged item is Q1. Positions are DF40 contact numbers as in interface v2 §9.2.

## Summary

The flat cable carries the HAT USB port, signals and power, from the board to the device-side piece that holds the pogo field. It is a fabricated 4-layer polyimide circuit:

- **Stack-up:** the fab's standard 4-layer FPC, 0.268 mm, adhesive-based cores, 12 µm inner and 18 µm (24 µm finished) outer copper (§4).
- **Connectors:** one Hirose DF40C-50 at each end. The cable carries two **DF40C-50DP-0.4V(51) headers**; the board and the device-side piece carry the **DF40C-50DS-0.4V(51) receptacles** (Hirose recommends the header on the FPC). 42 of 46 usable positions (§2, §3).
- **Pairs:** `SSTX±`, `SSRX±` and `D±` on L2 as striplines, ground on L1 above (51 µm) and L4 below (114 µm, L3 voided under the pairs): **72.5 / 100 µm drawn for 89.9 Ω** differential. Pairs ≥ 0.35 mm apart (backward coupling −69 dB, computed). No guard traces; the ground is the two planes and the via fences (§6, §8).
- **Power:** `VBUS` **≥ 18.2 mm** on L3 (18.5 mm used), return on the L1 and L4 planes, sized by IPC-2221B for a 10 °C rise at the 4.5 A fault ceiling and about 4 °C at the 3.0 A continuous rating. Drop for a 100 mm cable with both DF40 pairs at their maximum contact resistance: 102 mV (2.0 %) at 3.0 A (§9).
- **Shielding:** none added (§10). **Stiffeners:** 0.2 mm stainless steel under each DF40 (§11). **Bend:** static only, inside radius ≥ 4.0 mm, never below 2.7 mm (§12).
- **Length and width:** input from the case. This spec assumes 40–100 mm; the cross-section needs **22.5 mm** (§5).
- **Coupon:** seven cable members join the hat-standard ADR 0004 coupon (§14).

## 1. Scope and topology

```text
board DF40C-50DS ── FPC DF40C-50DP ══ flat cable (4-layer FPC) ══ FPC DF40C-50DP ── device-side piece DF40C-50DS ── pogo field (2 × 10)
                    └ steel stiffener                               └ steel stiffener
```

This spec covers the cable: conductors, stack-up, geometry, stiffeners, bend, fab notes and its coupon members. It does not cover the board-side routing (PCB design constraints), the device-side piece and its pogo field (hat-standard), or the case (case repository); §15 lists what the cable needs from the case. The ESD protection of the port sits on the device-side piece at the field (BOM lines 65, 68, 69); the cable carries none.

## 2. Connectors

| Item | Value | Source |
|---|---|---|
| Part on the cable, both ends | Hirose **DF40C-50DP-0.4V(51)** header, 50 positions, 0.4 mm pitch, 11.52 × 2.97 mm, 1.14 mm high | Catalog p. 10; Hirose recommends the header on the FPC, as the receptacle "may peel away" from an FPC without enough rigidity (catalog p. 19) |
| Mating part on the board and on the device-side piece | DF40C-50DS-0.4V(51) receptacle, 12.6 × 3.38 mm, 1.45 ± 0.15 mm high | BOM line 66; catalog p. 4 |
| Stack height | 1.5 mm (DS + DP) | Catalog p. 3 |
| Usable positions | 46: the four corner contacts are metal fittings | Catalog p. 10 note 3 |
| Rating | 0.3 A per contact, 30 V; contact resistance ≤ 90 mΩ; 30 mating cycles | Catalog p. 2 |
| Lock | Yes: the 10- to 50-position parts have the locking feature | Catalog p. 1, p. 10 note 2 |
| Polarization | None; a 180° mating would put `VBUS` on the pair positions | Catalog p. 10 note 5 |
| Header land pattern (on the cable) | 0.23 ± 0.02 mm lands at 0.4 mm; outer edge to edge 3.37 mm, inner 2.05 mm; span 9.6 mm; fitting lands 0.35 mm | Catalog p. 10 |
| Flatness under the connector | ≤ 0.02 mm at the connector's centre against its two ends | Catalog p. 16, item 4 |
| Data rate | Not published by Hirose for the standard type (**UNVERIFIED**) | — |

**Contact numbering (UNVERIFIED).** Interface v2 §9.2 numbers contacts 1, 3, 5 … on row A and 2, 4, 6 … on row B, 1 and 2 at the same end; which end is contact 1, and that receptacle contact *n* mates header contact *n*, are confirmed on Hirose's drawing for approval before the cable layout (interface v2 §11 item 5).

## 3. Conductor map, end to end

The cable joins position *n* at the board end to position *n* at the device-side end, for every *n*: the two headers are placed with contact 1 on the same cable edge, so every conductor runs straight and none crosses another outside the stiffened areas. A fold in the case changes which face a connector is on, never the map.

Classes: **P** `VBUS` pour, **G** ground (L1 and L4 planes), **D90** 90 Ω pair, **LS** low-speed, **—** spare (pad only, no conductor), **MF** metal fitting.

| Row A | Net | Class, cable layer | Row B | Net | Class, cable layer |
|---|---|---|---|---|---|
| 1 | metal fitting | MF | 2 | metal fitting | MF |
| 3–31 (odd) | VBUS ×15 | P, L3 | 4–32 (even) | GND ×15 | G |
| 33 | GND | G | 34 | CC | LS, L2 |
| 35 | SSTX+ | D90, L2 | 36 | spare | — |
| 37 | SSTX− | D90, L2 | 38 | spare | — |
| 39 | GND | G | 40 | spare | — |
| 41 | SSRX+ | D90, L2 | 42 | GND | G |
| 43 | SSRX− | D90, L2 | 44 | D+ | D90, L2 |
| 45 | GND | G | 46 | D− | D90, L2 |
| 47 | spare | — | 48 | GND | G |
| 49 | metal fitting | MF | 50 | metal fitting | MF |

Count, as interface v2 §9.2: 42 conductors (`VBUS` 15, `GND` 15 + 5 pair grounds, 3 pairs, `CC`), 4 spare positions, 4 metal fittings. Spare positions get pads and no conductor; a later interface revision that uses them comes with a new cable revision.

## 4. Stack-up

The fab's standard 4-layer FPC, 0.268 mm (nominal, base copper; 0.280 mm finished, `odapkit stackup stack`). Every layer thickness is the fab's published figure.

| Layer | Material | Thickness | Use |
|---|---|---|---|
| Coverlay | PI 12.5 µm + adhesive 15 µm | 27.5 µm | — |
| **L1** | Copper 18 µm base, 24 µm finished | 18 (24) µm | `GND` plane; DF40 lands at both ends |
| Dielectric | Adhesive 13 / PI 25 / bonding sheet 13 | 51 µm | — |
| **L2** | Copper 12 µm | 12 µm | Pairs, `CC` |
| Dielectric | Adhesive 13 / PI 25 / adhesive 13 | 51 µm | — |
| **L3** | Copper 12 µm | 12 µm | `VBUS` pour; **void under the pair band** |
| Dielectric | Bonding sheet 13 / PI 25 / adhesive 13 | 51 µm | — |
| **L4** | Copper 18 µm base, 24 µm finished | 18 (24) µm | `GND` plane |
| Coverlay | Adhesive 15 µm + PI 12.5 µm | 27.5 µm | — |

- Dielectric constant: PI 3.3 adhesiveless, 3.5 with adhesive (the fab); the adhesive and bonding-sheet DK is not published, so 3.5 is assumed and 3.3–3.6 is the computed sensitivity. Loss tangent not published (**UNVERIFIED**).
- This stack has the fab's thickest standard 4-layer dielectrics (51 µm); the 0.204 mm stack would need pair traces below the fab's 0.06 mm floor.
- Thickness tolerance: ±1.2 mil (±0.03 mm) for a multilayer flex up to 12 mil [P5].

## 5. Layer use and cross-section

Across the cable body, from the edge on the `VBUS` side (layout estimate; the KiCad layout checks it):

| Band | Width | L1 | L2 | L3 | L4 |
|---|---|---|---|---|---|
| Edge, via fence | 0.6 mm | GND | — | — | GND |
| Power | 18.5 mm | GND | `CC` (0.10 mm), ≥ 0.4 mm from the pair band | `VBUS` | GND |
| Pair band | 2.8 mm | GND | `SSTX±`, `SSRX±`, `D±` | **void** | GND |
| Edge, via fence | 0.6 mm | GND | — | — | GND |
| **Total** | **22.5 mm** | | | | |

Pair band detail (L2): 0.65 mm margin to the `VBUS` pour edge (room for the band's via fence), SSTX, SSRX, `D±` (0.245 mm each), 0.35 mm between pairs, 0.65 mm to the band edge. The L3 pour edge stays ≥ 0.65 mm from the nearest pair trace so it does not change their impedance.

**Fan-out zone.** At the connector the power positions 3–32 sit at one end and the pairs at positions 35–46 at the other, the same order as the body. Inside the stiffened area the `VBUS` pour widens from the connector's ≈ 6 mm to its body width and the pairs move on L2 to the pair band; `CC` (position 34) runs on L2 over the power band. No line crosses a pair outside the stiffened areas.

## 6. Impedance geometry

Computed with `odapkit stackup design` and `check` on `hardware/hat-flat-cable/stackup-v0.toml` (2026-10-25). Pairs are edge-coupled striplines on L2: L1 51 µm above the trace, L4 114 µm below it (L3 voided). Widths are drawn widths with an assumed 4 µm etch reduction on the 12 µm inner copper. Corners move one parameter at a time: dielectric thickness ±10 %, DK ±5 %, width ±10 µm, copper ±15 % (assumed ranges, as the main board's stack-up).

| ID | Class (net classes on the cable) | Signals | Target | Trace / gap, drawn | Computed | Worst case, corners |
|---|---|---|---|---|---|---|
| HFC-02 [Q1] | D90 (`USB3_90D`, `USB2_90D`) | `SSTX±`, `SSRX±`, `D±` | 90 Ω ± 10 % differential (interface v2 §4, PCB-I-01, PCB-I-02) | 72.5 / 100 µm | 89.9 Ω diff, 25.3 Ω common | 75.9–104.4 Ω (check: pass, warning) |
| HFC-04 [Q1] | LS | `CC` | Not controlled (PCB-I-14 on the board) | ≥ 0.10 mm, ≥ 0.4 mm from the pairs | — | — |

HFC-01 (100 Ω extension) and HFC-03 (50 Ω I2S) are withdrawn with v1; their IDs are not reused.

- The width term dominates; the arithmetic worst case lies outside ±10 %, which `odapkit stackup` reports as a warning: the fab's width compensation (±7 % above 50 Ω, [P5]) and the coupon (C1) hold it, as the stack-up method sets out. `sim/flex-impedance` gives 89.9 Ω at the 70 µm mean width (87.7–91.6 Ω over DK 3.3–3.6; 83.3–97.4 Ω at ±10 µm). The order names L2 as the signal layer and L1 and L4 as its references, with L3 void under the pair band (a custom impedance request, **UNVERIFIED** as a standard fab case).
- 72.5 µm sits below the `pcbway-flex` 3 mil (76 µm) default and above the fab's 0.06 mm order-form floor: the cable's product rules allow it in the D90 class only (§13).
- Propagation: effective DK 3.42, 6.17 ps/mm.
- Matching on the cable: within each pair ≤ 0.1 mm (HFC-05 [Q1]), met by construction (straight, parallel). HFC-06 (extension lane matching) is withdrawn.
- Both members of a pair take the same number of vias, side by side, at each end (HFC-07 [Q1], as PCB-I-10).

## 7. Loss and length

Estimates for the assumed maximum length, 100 mm; the coupon measures the real channel (§14).

| Item | D90 | Method |
|---|---|---|
| Conductor loss at 2.5 GHz (Nyquist of 5 Gb/s), smooth copper | 1.34 dB | Wheeler incremental inductance, field solver |
| Dielectric loss at 2.5 GHz, loss tangent 0.005–0.02 (**UNVERIFIED**, assumed range) | 0.21–0.84 dB | 42.1 × tan δ dB per 100 mm at effective DK 3.42 |
| Cable total at 2.5 GHz | 1.6–2.2 dB | Sum; roughness and the DF40 transitions not included |
| Conductor loss at 1.25 GHz | 0.95 dB | Same |

- Loss scales with length: a 40 mm cable has 0.6–0.9 dB at 2.5 GHz.
- The USB 3 Gen 1 channel budget through the whole path (board traces, two DF40 pairs, cable, pogo field, HAT pads) is not set here: neither the DF40 nor the pogo field has a published loss figure. The measured channel decides (§14). Until then the cable is held at ≤ 100 mm (HFC-08 [Q1]); a longer route from the case needs this section redone.

## 8. Grounds around the pairs

- **No guard traces between pairs** on L2 (HFC-09 [Q1]): an unstitched guard across a bend would be a resonant stub (the board allows a guard only when stitched along its length, PCB-I-09). Isolation comes from spacing between two planes: two 70 µm lines 0.30 / 0.35 / 0.40 mm apart couple at about −62 / −69 / −77 dB backward (computed). Pairs keep ≥ 0.35 mm from each other and `CC` ≥ 0.4 mm from any pair.
- **Planes:** L1 and L4 are solid ground over the whole body (HFC-10 [Q1]); PCB-R-06's "ground on both sides of the flex" is met by them.
- **Via fences:** through vias tie L1 to L4 along both cable edges and along the pair band's edge on the power side, at ≤ 2.0 mm pitch (about λ/10 at 7.5 GHz in effective DK 3.42), everywhere except in bend zones (HFC-11 [Q1]).
- **At each connector:** every `GND` position (the 15 power returns and the 5 pair grounds) has its own via to L1 and L4 inside the stiffened area (HFC-12 [Q1]).

## 9. Power conductors

Sizing rule (BRD-049, as the interface's contacts): each conductor is rated at a 10 °C rise, the rating is at least the fault ceiling (100 %), and the continuous current is at most 70 % of it. Method: IPC-2221B design equation, I = k · ΔT^0.44 · A^0.725 (A in mil², k = 0.024 for an inner layer, 0.048 for an outer one), conservative for a thin polyimide circuit; the coupon measures the real rise.

| ID | Rail | Continuous (interface v2) | Fault ceiling | Conductor | Minimum width | Rise at continuous |
|---|---|---|---|---|---|---|
| HFC-13 [Q0] | `VBUS`, both directions | 3.0 A (67 % of the ceiling) | 4.5 A | L3 pour, 12 µm | **18.15 mm** (18.5 mm used) | ≈ 4 °C |
| HFC-15 [Q0] | `GND` return | 3.0 A | 4.5 A | L1 + L4 planes, 18 µm base | 4.65 mm on one outer layer; the planes give about 42 mm | < 1 °C |

HFC-14 (`HAT_3V3`) is withdrawn with v1.

- **At the connectors:** each power pad carries ≤ 0.3 A at the fault ceiling (the DF40 rating; 0.20 A, 67 %, at 3.0 A) and has at least one via to its pour, two where they fit (HFC-16 [Q0]). A 0.15 mm via with 15 µm plating (plating **UNVERIFIED** for the fab flex) rates about 0.75 A at 10 °C by the same equation.
- **The T1's own limits** stay inside the ceiling: eFuse #A 1.981 A maximum out (44 %), TPS2121 IN2 2.95 A maximum in (66 %) (BOM lines 44, 45).
- **Neck-downs:** none along the body; a narrower route from the case changes the width (the fab's 18 µm inner-copper option [P13] would take `VBUS` to about 12 mm, at a new impedance computation).

**Voltage drop** (round trip, `VBUS` and `GND` conductors plus both DF40 pairs at the catalog's 90 mΩ maximum per contact, 15 contacts per rail; copper at 20 °C):

| Length | Case | `VBUS` loop | Of which DF40 contacts |
|---|---|---|---|
| 40 mm | Continuous, 3.0 A | 84 mV (1.7 %) | 72 mV |
| 40 mm | Fault ceiling, 4.5 A | 126 mV (2.5 %) | 108 mV |
| 100 mm | Continuous, 3.0 A | 102 mV (2.0 %) | 72 mV |
| 100 mm | Fault ceiling, 4.5 A | 153 mV (3.1 %) | 108 mV |

At the T1's 1.5 A offer the drop is half the continuous figure: 51 mV at 100 mm, so a sink HAT sees about 4.97 V from the T1's nominal 5.02 V at the board (5.1 V less the drops of eFuses #D and #A, power tree v0.8), inside vSafe5V.

## 10. Shielding

- **No EMI shielding film in the baseline** (HFC-17 [Q2]). The pairs are striplines between the L1 and L4 planes: a film on either coverlay sits outside a solid plane and does not change their impedance.
- **Why not microstrip with a film:** on the 0.204 mm stack a 70 / 150 µm microstrip pair on L1 is 87.7 Ω bare and 56.8 Ω with a film on its coverlay (−35 %, computed).
- **If pre-compliance (Q2) asks for more:** the fab offers HCF-6000G or PC800 film [P13]; over the L1 and L4 planes it adds thickness (recheck the bend radius) and nothing else. Coupon member C6.

## 11. Stiffeners

| ID | Item | Value | Source or reason |
|---|---|---|---|
| HFC-18 [Q0] | Material and thickness | Stainless steel 0.2 mm, under each DF40 header, on the opposite face | The fab offers 0.1–0.5 mm steel [P13]; FR-4 0.4 mm is the alternative where the case gives more height |
| HFC-19 [Q0] | Extent | The header's land pattern and the fan-out zone (§5), plus ≥ 1.0 mm on every side (the layout sets it) | Hirose: flatness ≤ 0.02 mm under the connector (p. 16) and enough FPC rigidity (p. 19) |
| HFC-20 [Q0] | Bond | Heat-cured adhesive rated for the DF40 reflow (peak 250 °C, two cycles, catalog p. 16); not the tapes the fab marks "not for reflow" | The fab [P13]; which adhesive the fab uses is **UNVERIFIED** (DFM) |
| HFC-21 [Q1] | Edges | Stiffener edges ≥ 1.0 mm from any bend zone; coverlay overlaps the stiffener edge | Strain relief |
| HFC-22 [Q1] | Mating surface | The stiffener is the surface the case presses to keep the DF40 mated, on top of its lock (§15) | Catalog p. 16: hold the connector with the case if impact or the FPC's counterforce can unmate it |

## 12. Bend, length and routing

| ID | Item | Value | Source |
|---|---|---|---|
| HFC-23 [Q0] | Bend type | Static: folded once at assembly, held in place; never flexed in use | A 4-layer circuit with solid planes is not a dynamic flex |
| HFC-24 [Q0] | Minimum inside bend radius | **2.7 mm absolute** (10 × 0.268 mm) | The fab: multilayer 10–15 × thickness [P5] |
| HFC-25 [Q1] | Design inside bend radius | **≥ 4.0 mm** (15 ×) | Same, upper end |
| HFC-26 [Q1] | Bend zones | No vias, pads, stiffener edges, plane or pour edges, or changes of trace width within a bend zone and 1.0 mm either side; traces cross the bend axis at right angles; both members of a pair bend together | kicad-lib `pcbway-flex` README (bend keep-outs) |
| HFC-27 [Q1] | Length | Assumed 40–100 mm (input from the case); ≤ 100 mm unless §7 is redone | §7 |
| HFC-28 [Q1] | Width | ≥ 22.5 mm body (input from the case) | §5 |
| HFC-29 [Q2] | Placement in the case | Away from the antennas and their feeds; distance **UNVERIFIED** (PCB-R-06) | PCB-R-06 |

The board sits behind the display and the device-side piece on the back of the body, with the battery layer between them (board ADR 0016); the cable rises past the battery's edge plus the lateral run to the pogo field, which gives the assumed 40–100 mm. The real route is the case's.

## 13. Fab notes

- **Rules:** kicad-lib `pcbway-flex` (3 mil track and gap, 0.15 / 0.35 mm vias, 0.20 mm copper to outline **UNVERIFIED** for flex), with the cable's product rules on top: 72.5 µm track in the D90 class only (above the fab's 0.06 mm floor); `VBUS` ≥ 18.15 mm; HFC-26 keep-outs as rule areas.
- **Coverlay at the DF40:** the header lands are 0.23 mm at 0.4 mm pitch, a 0.17 mm gap, below the 8 mil coverlay bridge [P5]: one coverlay opening per land row, or LPI solder mask in that area.
- **Finish:** ENIG (soldered lands only). **Outline:** laser routed, ±2 mil [P5]; keying features (§15) in the outline if the case uses them.
- **Assembly:** DF40 headers placed on the steel-stiffened areas; flex assembly is "contact us" at the fab [P8] (**UNVERIFIED**, DFM). No other part on the cable.
- **Impedance coupon** on the production panel (§14 member C1).

## 14. Test coupon

Hat-standard ADR 0004 requires a coupon (pogo field, DF40 flat cable, HAT pads: TDR, S-parameters to 10 GHz, crosstalk, a real USB 3 link, mating cycles and contact resistance) before the pad map freezes. The cable contributes these members:

| Member | What | Measured | Proposed pass | Level |
|---|---|---|---|---|
| C1 | Fab impedance coupon on the cable panel, D90 | TDR | Within HFC-02 (± 10 %) | Q1 |
| C2 | The production cable at 100 mm with both DF40 headers, mated to fixture boards carrying DF40C-50DS receptacles and coaxial launches, plus a 2×-thru fixture for de-embedding (IEEE P370 style) | TDR mated; SDD21, SDD11, NEXT and FEXT to 10 GHz between the three pairs | TDR within ± 15 % across the connector region and ± 10 % on the cable; SDD21 against §7; crosstalk recorded against the USB 3 Gen 1 budget (**UNVERIFIED** until derived) | Q1 |
| C3 | The same at 40 mm | As C2 | As C2 | Q1 |
| C4 | C2 folded at the 4.0 mm and 2.7 mm radii, held as in the case | TDR across the fold; SDD21 | Change within the ± 10 % band | Q1 |
| C5 | C2 under current: `VBUS` and `GND` at 4.5 A, then 3.0 A, in still air at 25 °C | Temperature rise of the body and at each DF40 (thermocouple or IR), four-wire drop | ≤ 10 °C at 4.5 A on the body; drop ≤ §9 figures | Q0 |
| C6 | C2 with EMI film on both coverlays (only if Q2 pre-compliance asks for it) | As C2 | Impedance unchanged within ± 3 % | Q2 |
| C7 | DF40 mating cycles on C2: 30 cycles (the catalog rating), contact resistance every 5 cycles | Four-wire per power position | ≤ 90 mΩ per contact (catalog p. 2) | Q1 |

C2 and C3 also go into the end-to-end channel of hat-standard ADR 0004 (pogo field and HAT pads), where a real USB 3 Gen 1 and USB 2.0 link runs.

## 15. Inputs needed from the case

1. **Route:** the path from the board DF40 to the device-side piece's DF40, the folds (count, position, axis) and the inside radius each fold has room for (≥ 4.0 mm wanted, 2.7 mm absolute).
2. **Length** of that route (assumed 40–100 mm).
3. **Width** available along the route (≥ 22.5 mm needed).
4. **Position and orientation** of the device-side piece's DF40 relative to the board's, which sets the face each cable end mates on.
5. **Height above each mated DF40:** stack 1.5 mm + cable 0.27 mm + steel 0.2 mm + adhesive, about 2.0 mm, plus the retention part.
6. **Retention:** a pad or bracket pressing each stiffener so the DF40 stays mated under drop and the cable's counterforce (catalog p. 16), on top of its lock; force from Hirose's data (**UNVERIFIED**).
7. **Keying** at both ends against a 180° mating.
8. **Fixing** of the cable body so the folds stay static, clear of sharp edges, the battery and its contacts.
9. **Keep-out** from the antennas and their feeds (PCB-R-06).
10. **Assembly and service sequence:** when the cable is mated and how it is reached (the device-side piece is a user-fitted accessory, HCS-023).
11. **Grounding** of the stiffeners or the cable's planes to the frame, if the case wants that path for ESD or EMC.

## 16. Open items

1. DF40 contact numbering, and receptacle *n* mating header *n*: Hirose's drawing for approval (interface v2 §11 item 5).
2. Hirose's FPC-rigidity data for the header on an FPC (catalog p. 19); stiffener thickness and the retention force follow it.
3. Fab DFM review: the L2 impedance with L3 voided as a custom request; DK and post-lamination thickness of the bonding sheet; loss tangent; reflow-capable stiffener adhesive; flex assembly of a 0.4 mm DF40 on a steel stiffener; coverlay openings; plating thickness in flex vias.
4. The USB 3 Gen 1 channel budget through the full path, with the DF40 and the pogo field measured (C2, C3).
5. Route, length and width from the case (§15).
6. Replace the assumed DK, etch and corner ranges in `stackup-v0.toml` with the fab's answer and rerun `odapkit stackup check` before the net classes freeze.

## 17. Board changes

Applied in [BOM v1.14](bom-v1.md#changes-in-v114) (RFC 0015): line 66 DF40C-50DS receptacles on the board and the device-side piece; line 102 this cable with DF40C-50DP headers; lines 65, 68, 69 ESD on the device-side piece. PCB-Z-05 takes the DF40C-50DS height (1.45 ± 0.15 mm). The board's own net classes do not change: the cable is its own KiCad project with `pcbway-flex` and the D90 product rule of §13.

## 18. KiCad project

`hardware/hat-flat-cable/` holds the stack-up file (`stackup-v0.toml`) and no KiCad project yet. The KiCad project there carries the stack-up of §4, the D90 and `VBUS` classes, the DF40C-50DP footprint at both ends, the conductor map of §3 as the netlist, the stiffener and bend-zone areas on user layers, and the coupon members C1–C4 as separate boards on the same panel.

## 19. Sources

- Hirose Electric, DF40 Series catalog (libs parts manifest): pp. 1–4, 10, 16, 19.
- The fab, *Stack-up for FPC*, <https://www.pcbway.com/pcb_prototype/Stack_up_for_FPC.html>, fetched 2026-10-24; [P5], [P8], [P13] as cited in kicad-lib's `pcbway-*` rule sets (fetched 2026-10-22).
- IPC-2221B, *Generic Standard on Printed Board Design*, conductor current-carrying design equation.
- Hat-standard interface v2, ADR 0004 and its amendment; RFC 0014, RFC 0015.
- `odapkit stackup` (toolkit-hardware) on `hardware/hat-flat-cable/stackup-v0.toml`; `sim/flex-impedance` (this repository); both run 2026-10-25.
