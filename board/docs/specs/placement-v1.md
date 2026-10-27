# Placement v1 of the T1 main board

- **Status:** Draft v1 (2026-10-27; compaction of §4 decision 12 applied the same day). The board setup and the placement stage of the T1 main board: every part of the schematic placed, nothing routed. It applies [floorplan v1](floorplan-v1.md) with the changes of §4, each recorded as a decision.
- **Board:** [`hardware/t1-main-board/t1-main-board.kicad_pcb`](../../hardware/t1-main-board/t1-main-board.kicad_pcb), written by the placement tool [`hardware/t1-main-board/pcb/`](../../hardware/t1-main-board/pcb/) (`build.py`) from the schematic; the tool's report is [`pcb/placement-result.json`](../../hardware/t1-main-board/pcb/placement-result.json). The same inputs give a byte-identical board.
- **Inputs:** the schematic (hardware/t1-main-board, 1,012 parts, 1,081 nets), [floorplan v1](floorplan-v1.md), [stackup v3](stackup-v3.md) and `hardware/stackup/stackup-v3.toml`, the [PCB design constraints](pcb-design-constraints.md) v0.15, [ADR 0016](../adr/0016-front-side-height-under-the-display.md), [ADR 0018](../adr/0018-antennas-and-certification-route.md), [ADR 0020](../adr/0020-battery-connected-through-contacts.md), the composed design rules (`t1-main-board.kicad_dru`), the [BGA escape study](../../hardware/studies/bga-escape/README.md). Footprints: kicad-lib as pinned in `hardware/lib/opendap` and KiCad 10.0.7's stock libraries.

## 1. Board setup

| Item | Value | Source |
|---|---|---|
| Outline | 55.3 × 90.1 mm, square corners, origin at the board centre (KiCad (100, 100) mm) | PCB-M-02 (cavity less 0.5 mm per side, **UNVERIFIED**), PCB-M-04; corner radii wait for the case (CRAFT-35) |
| Mounting holes | H1–H4, 2.2 mm non-plated at (±24.15, 41.55) and (±24.9, −27.0) mm | PCB-M-08, floorplan v1 §1 (positions **UNVERIFIED** until the case) |
| Stackup | Six layers, 1.046 mm: mask 20 µm / L1 35 µm / 2116 120 µm / L2 25 µm / 3313 90 µm / L3 18 µm / core 430 µm / L4 18 µm / 3313 90 µm / L5 25 µm / 2116 120 µm / L6 35 µm / mask 20 µm, ENIG; Dk as the TOML | stackup v3, `stackup-v3.toml` |
| Net classes | The project's classes and patterns, generated from `hardware/rules/netclasses.toml` | netclasses.toml |
| Design rules | `t1-main-board.kicad_dru`, the composition of the PCBWay HDI, OpenDAP craft and T1 product rules | `t1-main-board.dru.toml` |
| Rule areas | `ZONE_CORE`, `ZONE_AUDIO`, `ZONE_POWER`, `ZONE_IO`, `ZONE_RADIO`, `ZONE_FACEPLATE` per copper layer, five `ZONE_CORRIDOR`, `BATTERY_POCKET`, `BATTERY_CONNECTOR`, `BATTERY_CONTACT_EMPTY`, `BATTERY_ESD`, `AUDIO_ANALOG`, `BGA_ESCAPE` | floorplan v1 §2, §4; PCB-L-01, L-02, L-04, L-08; PCB-A-07; hardware/rules/README.md |
| Height areas | Drawn on User.1 (front: display footprint, faceplate connection area) and User.2 (back: pocket, bands, speaker body) | PCB-Z-01 to Z-04, ADR 0016 |
| Fiducials | FID1–FID3 front, FID4–FID6 back (global, not symmetric), FID7–FID8 back at the RK3566 (local); 1 mm dot, 2 mm mask, 3.2 mm kept free | PCB-M-09, PCB-D-02, D-03 |
| Identity | `${TITLE}` and revision with the issue date on the back silk, in an area kept free of parts | CRAFT-20 |

## 2. What is placed

All 1,012 parts: 833 on the front, 179 on the back, plus the eight fiducials and four holes. The schematic parity check finds no difference. Four parts stand on courtyard-only placeholders, because their lands are not drawn yet (hardware/t1-main-board/README.md, open items): L5401 (Murata LQH3NP), SW6901–SW6903 (C&K PTS815).

| Part | Where (device frame, mm) | Side | Basis |
|---|---|---|---|
| RK3566 U1301 | (0, 10) | back | floorplan v1, BGA escape study, ADR 0016 item 3 |
| LPDDR4X U2101 | (16.9, 11) | back | floorplan v1 (16.75); 2.05 mm courtyard gap to the SoC (PCB-D-01) |
| eMMC U3801 | (−17.75, 12) | back | floorplan v1 |
| SoC, LPDDR4X and eMMC decoupling | front, each capacitor at a ball of its rail under the package | front | ADR 0016 item 3, PCB-P-10; the escape study's one ground stack per capacitor next to a rail via |
| RK809-5 U1101 | (−6.0, 25.7), its five inductors around it | back | §4 decision 5 |
| vdd_cpu buck U1201, inductor L1201 | inductor (11.95, 23.9) under the pocket, above the LPDDR4X and 4 mm right of the SoC's courtyard; converter on the front opposite | back / front | §4 decision 12 (was the top band, decision 3) |
| RP2354A U3501 | (−16.0, 24.5) | front | §4 decision 6 |
| CS43198 U2501, U2601 | (−20, −18), (−11.5, −18), mirrored about x = −15.75 | back | floorplan v1 |
| NZ2520 oscillators Y2401, Y2402 | (−17.3, −11), (−14.2, −11), mirrored about x = −15.75 | back | floorplan v1 (moved to clear each other) |
| 3.5 mm jack J3401, 4.4 mm jack J4001, USB-C J4601 | bottom edge at x −22.3, −11.55, 0 | back | PCB-M-05, floorplan v1 |
| microSD J6201 | top edge, x 13.5 | back | floorplan v1 (13.0); §4 decision 3 |
| U.FL J5201 (ANT0), J5202 (ANT1) | (−14.0, 41.5), (−8.3, 41.5), top band | back | ADR 0018 item 4, PCB-R-02 |
| Type 2EL U5001 | (−17, 32.5) | back | floorplan v1 |
| FH35C J5301 | (2.5, −32.9), faceplate connection area | front | floorplan v1 §5 |
| DF40C-50DS J4701 | (13.1, −31.0), bottom band | back | floorplan v1 §5 |
| Battery contacts J701–J706 | row at y −23.5, x −2.0 to 19.0, 3.5 mm pitch, third position empty | back | ADR 0020 item 2, PCB-L-04 |
| Battery-contact ESD D702, D703 | at the mid-cell and NTC contacts, inside `BATTERY_ESD` | back | PCB-L-08 |
| Side buttons | Action SW6904, Vol+ SW6902, Vol− SW6903 on the left edge from y 35 down; Main SW6901 on the right edge | back | controls spec §1.4 (positions **UNVERIFIED**) |
| Speaker pads TP5503, TP5504 | under the speaker body, (10.5, −39.5) and (16.5, −39.5) | back | BOM v1 line 33 (pad spacing **UNVERIFIED**) |

Every other part is placed by the tool: tall parts in the bands, then parts with through holes (their thermal vias need the other side free), then the converters' inductors, then the parts over 1.0 mm (back only), then the rest, each at the nearest free spot to the pads it connects to (pads of its own block first; a converter next to its inductor's switch-node pad), and test pads on the front.

## 3. Area budget and occupancy

### 3.1 The floorplan's method with the real footprints

Floorplan v1 §2.1 estimated the over-budget bands with a placement and routing factor of 1.7 (1.2 for edge parts) on courtyard estimates. The same method on the real courtyards of the schematic's parts, on the floorplan's zones and block assignment:

| Zone | Courtyard (mm²) | Need ×1.7 (mm²) | Band use | Back use | Front use | Floorplan v1 (band / back / front) |
|---|---|---|---|---|---|---|
| CORE | 2,794 | 4,750 | **203 %** of 304 mm² | 100 % | **94 %** | 205 % / 100 % / 48 % |
| AUDIO | 1,665 | 2,642 | **123 %** of 370 mm² | 100 % | **254 %** | 115 % / 100 % / 79 % |
| POWER | 1,458 (speaker body included) | 2,396 | **233 %** of 295 mm² | **165 %** | **164 %** | 139 % / 108 % / 112 % |
| IO | 379 | 595 | 82 % | 100 % | 29 % | 67 % / 100 % / 20 % |
| RADIO | 286 | 486 | 0 % | 100 % | 11 % | 0 % / 88 % / 0 % |
| FACEPLATE | 121 | 206 | — | — | **109 %** of 190 mm² | — / — / 106 % |
| **Board** | **6,703** | **11,075** | | | **111 % of 9,965 mm²** (113 % before decision 12) | 77 % |

The real parts are larger than the floorplan's estimates (6,703 mm² of courtyard after decision 12, 6,785 mm² before, against 4,719 mm² in floorplan v1, all with the speaker body). With the factor 1.7 the board needs 111 % of both sides (113 % before); the courtyards alone cover 67 %. The class split moves with the lower parts: an inductor at 1.5 mm counts as a back part, no longer a band part, which is most of the core and power bands' fall (227 → 203 %, 258 → 233 %) and empties the radio band.

### 3.2 The placed board

Courtyard area over zone area, per side, without a factor (zones with the changes of §4; the back's band is the back outside the pocket; the power band counts the speaker body):

| Zone | Front | Back | Band (back) |
|---|---|---|---|
| CORE | 1,341 of 1,867 mm² (72 %) | 1,349 of 2,115 mm² (64 %) | 167 of 348 mm² (48 %) |
| AUDIO | 882 of 1,234 mm² (71 %) | 755 of 1,018 mm² (74 %) | 328 of 416 mm² (79 %) |
| POWER | 653 of 984 mm² (66 %) | 719 of 1,208 mm² (59 %) | 330 of 428 mm² (77 %) |
| IO | 203 of 302 mm² (67 %) | 197 of 256 mm² (77 %) | 165 of 187 mm² (88 %) |
| RADIO | 118 of 406 mm² (29 %) | 153 of 406 mm² (38 %) | 73 of 161 mm² (45 %) |
| FACEPLATE | 97 of 190 mm² (51 %) | — | — |

Every part found a place with its courtyard inside its zone, its height inside its height area (exceptions in §5) and no courtyard overlap. The routing factor left by this placement is about 1.5 over the board (9,965 / 6,703 mm²) and 1.3–1.4 in the core's and the audio zone's front; the floorplan assumed 1.7 (1.5–1.9). Whether the board routes at this density is the next stage's question; a shortfall goes back to the maintainers as a stackup question (PCB-S-22).

## 4. Decisions

Each changes floorplan v1 where the real footprints did not fit it; the tool's `plan.py` carries the same rows.

1. **Accepted (2026-10-27): the audio zone grows to y 2.4 on every layer and to y 14 on the front (x < −6.2).** Basis: its parts need 1,665 mm² of courtyard against 1,557 mm² of floorplan zone on both sides (§3.1); the core zone has room (§3.2); above y 2.4 the eMMC and its rework clearance (PCB-D-01) keep the back and inner layers; a zone may cover only some layers where two zones share a spot (floorplan v1 §2). The core–audio corridor moves to x −11 to −5, y −1 to 5, across the new boundary.
2. **Accepted (2026-10-27): the power zone grows to y 0 (x > 6.2), its left edge moves to x 4.0 between the battery-contact window and y 0, it takes the front of the HAT strip right of the faceplate area, and the back of x −2 to 4, y −18.8 to −8.** Basis: the power zone's parts over 1.0 mm stand on the back only (twelve 0805 capacitors of the charger, five INA236, the ship FET, diodes), and its back outside the contact window is full of them; the I/O zone uses 30 % of its front (§3.1); the I/O pairs pass the moved back area on L4 and L1. The core–power corridor moves to x 8 to 14, y −3 to 3.
3. **Accepted (2026-10-27): parts over 1.5 mm stand in the bands at fixed places.** The power band above the USB-C (taken from the I/O zone's back) holds the battery fuse under the P+ contacts, the 5.1 V output 1210 and one pre-rail 1206; the right band the VSYS_LV and pre-rail inductors (XGL4020, 2.1 mm). Decision 12 took the vdd_cpu, vcc3v3_sys, radio AVDD18, charger and 5.1 V inductors out of the bands; the core top band (x −5.5 to 5.6, taken from the radio zone left of the microSD) stays with the core. Basis: PCB-Z-01, Z-02; the converters stand opposite their inductors on the front. Cost (until decision 12): the vdd_cpu converter sat about 24 mm from the SoC's package edge.
4. **Accepted (2026-10-27): one capacitor over 1.0 mm stands on the front's bottom strip outside the display**: the VSYS_LV converter's 22 µF 0805 C904 (1.25 mm). Basis: PCB-Z-04 allows 6.8 mm there (**UNVERIFIED** until the faceplate mechanics); the power zone's back has no room left for it. After decision 12 the two pre-rail 1206 and C903 found room in the power band; before it, all four stood on the strip.
5. **Accepted (2026-10-27): the RK809-5 stands above the SoC, at (−6.0, 25.7) on the back.** Basis: below the SoC the grown audio and power zones leave about 10 × 8 mm, and the PMIC with its five 1.2 mm inductors (back only) needs about 150 mm²; above, it sits next to the vdd_cpu buck, 2 mm from the SoC's and the eMMC's courtyards (PCB-D-01). Floorplan v1 had it below the SoC.
6. **Accepted (2026-10-27): the RP2354A stands at (−16.0, 24.5) on the front**, clear of the eMMC. Basis: its exposed pad's thermal vias go through the board, so the other side under them must be free of pads (PCB-V-01, shorts); the audio zone took its floorplan place.
7. **Accepted (2026-10-27): `blk.audio-supply` (TPS62840 buck, its inductor and switches) belongs to the power zone.** Basis: switch nodes stay in the power zone except the PMIC's and the vdd_cpu buck's (floorplan v1 §4 item 6, PCB-A-06); floorplan v1 §2 listed the block under `blk.audio`.
8. **Accepted (2026-10-27): heat sources other than the SoC and the PMIC stand on the front** where their height allows it. Basis: PCB-L-01 (no heat source on the back over the pocket); the SoC and the PMIC are there by ADR 0016 (floorplan v1 §6 item 3).
9. **Accepted (2026-10-27): flat test pads stand on the front, in the zones of their nets.** Basis: ADR 0016 consequences (single-sided fixture); PCB-S-17 (a test pad's track stays in its net's zone). Contact pads of parts mounted in the case (speaker, LRA, NFC antennas, cover detect) stand on the back.
10. **Accepted (2026-10-27): the faceplate connection area's front belongs to the faceplate zone alone.** Basis: ADR 0016 item 1 (FH35C and its ESD only); floorplan v1's I/O rectangle overlapped it.
11. **Accepted (2026-10-27): DRC reports unconnected items as warnings at this stage** (project setting, generated). Basis: nothing is routed; the routing stage sets them back to errors, so the stage's own DRC errors stay visible.
12. **Accepted (2026-10-27): lower and smaller parts where the design's stresses allow them** ([compaction study](../../hardware/studies/compaction/README.md), [BOM v1.15](bom-v1.md#changes-in-v115)). Basis: the study's matrices: same inductance, design peak ≤ 70 % and maximum current limit ≤ 100 % of Isat at 30 % drop (BRD-049 as power tree v0 §4.10 applies it), heights PCB-Z-01 and Z-03, ratings at least twice the rail, PCB-D-06; sourcing check (T1-029), 2026-10-27: open for XGL4015-102MEC and conditional for XGL4015-471MEC (BOM v1.15), with the 2.1 mm parts on the same land as the fallback. The charger and 5.1 V inductors (XGL4015-102MEC) and the vcc3v3_sys and radio AVDD18 inductors (XGL4015-471MEC) are 1.5 mm and stand under the pocket; the vdd_cpu inductor is 1.2 mm (XGL4012-221MEC, Document 1718), so it moves next to the SoC (block target (6.0, 22.5); it lands 2.4 mm from its converter, as before) with its converter on the front opposite, as every other converter of this placement (decision 3; PCB-P-07 asks for one side, a review item); 58 decoupling capacitors of 100 nF on rails of 3.3 V or less in the core, I/O and radio zones are 0201; the 51 test pads on signal nets are 0.8 mm. The TPS62136 and LMR33630C inductors stay 2.1 mm in the band (their XGL4015 is at 103 % at the converter's limit), and no thinner 0805 or 1206 capacitor passes (obsolete, not for new designs or not listed).

## 5. Checks

**DRC** with the composed rules (KiCad 10.0.7, `pcb/build.py --drc`): **0 errors**, 499 unconnected items (expected: not routed), schematic parity 0. Warnings (607): 588 silk items of the library footprints against the craft rules (CRAFT-05, CRAFT-07, Q2) and 9 silk overlaps, 2 PCB-L-01 (the SoC and the PMIC over the pocket, floorplan v1 §6 item 3), 6 library issues (the placeholders), 2 PCB-D-05 (edge connectors' silk at the edge, Q2). PCB-I-09 leaves a footprint's own pads out since 2026-10-27, as PCB-V-01 does (it fired six times between the DAC's MCLK pin and its neighbours and between the dividers' pins).

**Placement checks** (`pcb/checks.py`): no courtyard overlap, no part outside its zone, no part in a hole ring or within 0.3 mm of the edge (J*, SW* exempt), no through hole under another part. Height findings:

| Part | Height | Area | Status |
|---|---|---|---|
| J4001 (4.4 mm jack) | 6.5 mm | reaches 5.55 mm into PCB-Z-01 | Pocket relief, PCB-Z-06 (case input); no catalog jack fits |
| J6201 (microSD) | 1.68 mm | reaches 11.8 mm into PCB-Z-01 | Pocket relief, PCB-Z-07 (case input), or the BOM alternate Molex 104031-0811 (1.42 mm, push-pull: a product choice) |
| SW6901–SW6904 (side buttons) | 1.9–2.5 mm | 2 mm side strips plus about 1.8 mm of PCB-Z-01 | Side-strip relief, PCB-Z-08 (case input); no lower side switch with a verified height; PTS815 height **UNVERIFIED** |
| C904 | 1.25 mm | front outside the display | Decision 4; PCB-Z-04 **UNVERIFIED** |

**3D envelope:** the case publishes no export yet (`case/export/` is empty), so no STEP check against ADR 0016 was made; part heights come from the footprints' 3D models (`pcb/heights.py`) and are checked against PCB-Z-01 to Z-04 above.

## 6. Open items

1. **Routing density.** The real parts need 111 % of the board with the floorplan's factor 1.7 (§3.1; 113 % before decision 12); the placement leaves a factor of about 1.5. Decision 12 applied the part swaps that the stresses allow. Left: capacitors over 1.0 mm (no thinner part of the same value passes; a smaller case needs DC-bias figures, DRV-107); the audio zone's front at 254 %, whose captured parts stay (T1-040); and, for the maintainers (product and case), the speaker on a case shelf above low parts, which frees 165 mm² of band.
2. **Zone net classes:** closed (2026-10-27). Every net but GND carries the `ZONE_<NAME>` class of each zone whose blocks it touches (the zones of `pcb/plan.py`; the faceplate connector's sheet also the faceplate zone), a rail used in more than one zone `ZONE_SHARED`; the generator writes them as net-class patterns (`zone_patterns` in `generator/generate.py`). Of 1,080 nets: 911 in one zone, 104 in two, 36 in three, 28 shared rails, GND none.
3. **Switch-node class:** closed (2026-10-27). The generator names every switch node `*_SW` (`VSYS_LV_SW`, `VCC3V3_SYS_SW`, `VDD_CPU_SW`, `RP_VREG_SW`, was `RP_VREG_LX`), and the faceplate display switch's output is `FP_VCI_OUT` (was `FP_VCI_SW`), so `SW_NODE` holds the 18 switch nodes and nothing else.
4. **Lands not drawn:** LQH3NP, PTS815 (placeholders, §2); the WE-LHMI 4020 is no longer fitted (decision 12).
5. **Case inputs:** mounting holes, corner radii, pocket reliefs (J4001, J6201, side buttons), speaker contacts and body, antenna and NFC contact positions.
6. **Legend:** reference designators are on the fabrication layers only; the silk legend (CRAFT-10, CRAFT-12) is placed at a later stage.
7. **Mirrored channels** (CRAFT-34, Q2): only the DACs and oscillators are mirrored; the output stages are not yet.
8. **Assembly variants:** the base design's DNP state is on the board; KiCad 10's design variants come with the next update from the schematic.
