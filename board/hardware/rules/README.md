# Main board rules

The T1 main board's own design rules, from the [PCB design constraints](../../docs/specs/pcb-design-constraints.md) (BRD-060). The sources of the manufacturing, assembly and reliability values are keyed at the end of this file.

- `t1-main-board.kicad_dru`: the product rules. Each rule is named after the constraint it enforces and the lowest quality level at which it is mandatory ([RFC 0010](https://github.com/opendap-project/rfcs/blob/main/text/0010-quality-levels.md)): `T1 PCB-H-01 [Q1]: …`.
- `netclasses.toml`: the net classes the rules and the schematic share, with their constraint IDs, design currents and impedance targets.
- `test/`: a test board with one failing and one passing object per rule, built by `make_test_board.py` on libs' `kicad/` test-board tools (submodule `../lib/opendap`).

The KiCad project's rules, [`../t1-main-board/t1-main-board.kicad_dru`](../t1-main-board/), are the composition of the PCBWay HDI fab rules (libs `kicad/` `design-rules/pcbway-hdi`), the OpenDAP craft rules (libs `kicad/` `design-rules/opendap-craft`) and these product rules, in that order, made and checked with `odapkit dru` from `t1-main-board.dru.toml`.

Impedance-controlled net classes are named `<name>_<ohms>D` (differential) or `<name>_<ohms>SE` (single-ended), so the craft rules exempt them from their general width rules (CRAFT-40, CRAFT-43; the composition was checked with every impedance class: no craft or fab report on their tracks). The product rules find the same classes with the same wildcards (PCB-S-14, PCB-W-01). `BAT_SENSE` also matches the `*_???SE` wildcard and is not an impedance class: the product rules leave it out by name.

## Layers

The board is the 6-layer [stackup v3](../../docs/specs/stackup-v3.md), with layer roles by zone (its §3). The rules name KiCad's layers:

| Stackup | L1 | L2 | L3 | L4 | L5 | L6 |
|---|---|---|---|---|---|---|
| KiCad | `F.Cu` | `In1.Cu` | `In2.Cu` | `In3.Cu` | `In4.Cu` | `B.Cu` |
| Role | signal (decoupling and core-rail pours in the core zone) | ground (core and system rails in the core zone) | ground (pours in the power zone) | signal (stripline; pours in the power zone, power or RF ground in the radio zone) | ground, full layer | signal |

Per-class widths are rules on `(layer outer)` (L1, L6) and `(layer inner)` (L4); PCB-S-14 keeps impedance classes off every other inner layer, so "inner" means L4 for them, and its zone rules keep them off L1 in the core zone and off L4 in the power and radio zones. Each width rule is min / opt / max = the stackup width −5 % / exact / +5 %: a 5 % width error moves the impedance by 2–3 %, a third of the fab's ±10 % window, so the rule catches a wrong width while leaving the fab's own corners alone. LPDDR4X keeps 3 × W from every other net on L4 (PCB-S-24). The ground layers of each zone take no other net's tracks or fills (PCB-S-25: L5 everywhere, L2 outside the core zone, L3 outside the power zone), and the I/O zone's `VBUS` nets stay on the outer layers (PCB-P-22).

## Severity

- A rule at Q0 or Q1 whose value has a source is an **error**.
- A rule at Q2 to Q4 is a **warning**, whatever its source (RFC 0010: items above the build's target level are debt, not blockers).
- A rule whose value is still **UNVERIFIED** is a **warning** at any level, and becomes an error when the value is sourced and the level is Q0 or Q1.

Each rule's comment in the `.kicad_dru` names its source; [Sources of the rule values](#sources-of-the-rule-values) lists the keys.

## Conventions the rules rely on

The rules find objects by reference prefix, footprint field, pad fabrication property and rule-area name. The schematic symbols and footprints carry them; a footprint that does not follow them escapes its rules.

| Object | Convention | Rules |
|---|---|---|
| Mounting hole | Footprint reference `H*` (`H1`…`H4`); one pad, NPTH or plated | PCB-H-01 to H-06 |
| Ceramic capacitor (MLCC) | Reference `C*`. A capacitor that is not an MLCC still gets the MLCC rules, which only cost distance | PCB-H-05, PCB-B-03 |
| Edge-mounted part | Reference `J*` (connectors) or `SW*` (side buttons): exempt from the part-to-edge rule, may overhang the edge | PCB-B-01 |
| BGA needing rework access | Footprint field `Rework` = `BGA` (RK3566, LPDDR4X, eMMC) | PCB-D-01 |
| BGA ball pads | Pad fabrication property "BGA pad" (also used by the fab rules) | PCB-H-06 |
| Fiducial | Reference `FID*`; pad fabrication property "Fiducial, global to board" or "Fiducial, local to footprint" | PCB-D-02 to D-04 |
| Test point | Reference `TP*`; pad fabrication property "Test point pad" | PCB-D-06 to D-09 |
| Via in a pad | Via property Filling = Filled and Capping = Capped (IPC-4761 type VII) | PCB-D-10 |
| Heat source | Footprint field `Thermal` = `hot` (converters, eFuses, charger, SoC, PMIC) | PCB-L-01 |
| Battery pocket | Rule area `BATTERY_POCKET`: the pocket's footprint on the board, grown by a 3 mm margin (**UNVERIFIED**) | PCB-L-01 |
| Battery contacts | Rule area `BATTERY_CONNECTOR`: the pocket-floor contact window plus 1 mm, around the six battery contacts and their unfused copper (ADR 0020) | PCB-L-02, L-05 |
| Battery nets | Net classes `PWR_BAT` (P+, P−) and `BAT_SENSE` (mid-cell tap, NTC) in `netclasses.toml` | PCB-L-02, L-05 |
| Empty contact position | Rule area `BATTERY_CONTACT_EMPTY`: the 7.00 × 2.70 mm pad position left empty between P+ and the mid-cell tap | PCB-L-04 |
| Battery contact ESD | Footprint field `ESD` = `battery` on the TPD1E10B06 of the mid-cell tap and NTC; rule area `BATTERY_ESD`: the contact pads grown by 3 mm (**UNVERIFIED**) | PCB-L-08 |
| Panel break tab | Rule area `BREAK_TAB` around each tab or mouse-bite position on the outline, reaching at least 5.08 mm (PCB-B-03) into the board | PCB-B-02, B-03 |
| RK3566 escape | Rule area `BGA_ESCAPE` (existing) | PCB-G-02, W-01, V-01 |
| Analog audio | Rule area `AUDIO_ANALOG` (existing) | PCB-A-07, A-20 |
| Differential pair | Net names ending in `_P` / `_N` (or `+` / `-`), so KiCad couples the pair | PCB-I-01, I-02, I-04, I-05 (pair gap) |
| RF ground cut-out | Rule area `RF_CUTOUT`: the L2 (L5) cut-out under the RF line, 1.6 mm wide and 0.6 mm past each end, on the cut layer and the pour layer of the line's side only (`In1.Cu` + `In2.Cu` for an L1 line, `In4.Cu` + `In3.Cu` for L6), with "keep out copper fills" set so the plane's fill stays out | PCB-R-03 |
| Zones | Rule areas `ZONE_CORE`, `ZONE_AUDIO`, `ZONE_POWER`, `ZONE_IO`, `ZONE_RADIO`, `ZONE_FACEPLATE` (one or more per zone, an area may cover only some layers) and `ZONE_CORRIDOR` ([floorplan v1](../../docs/specs/floorplan-v1.md)) | PCB-S-14 by zone, S-17, S-18, S-25, P-22 |
| Zone of a net | Net class `ZONE_<NAME>` or `ZONE_SHARED` besides the signal class (`netclasses.toml`) | PCB-S-17 |

## Check

```sh
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
$PY hardware/rules/test/make_test_board.py
python3 hardware/lib/opendap/kicad/design-rules/tools/check_drc.py hardware/rules/test/t1-main-board-rules-test.kicad_pcb
```

Every rule fires exactly once in the FAIL column and nothing fires in the PASS column.

Rules that overlap the fab and craft rule sets are left to them: silkscreen to pads and vias, silk sizes, 45° routing, acute angles (CRAFT-41, 135° minimum), short segments and the via set live in libs `kicad/` `opendap-craft`. The composition `pcbway-hdi` + `opendap-craft` + these rules compiles under KiCad 10.0.7 with every T1 rule still firing on the test board. The test board has six copper layers (stackup v3); its GND objects are joined by a bus on L5 (`In4.Cu`, the full-layer ground, which takes GND), so the board reports no unconnected items.

## Not checked by DRC

Impedance itself, zone-local ground stitching and zone-boundary fences (PCB-S-19, S-13), the edge margin from a zone-local ground, the maximum pair gap, spacing to other nets (3–5 × W; LPDDR4X on L4 is DRC, PCB-S-24), length matching, skew and delay matching across layers (PCB-I, PCB-S-15), height zones (PCB-Z, including the battery-contact exception of PCB-L-05), copper area per net and via counts for current (PCB-P-01 to PCB-P-03, PCB-P-09), the battery contacts' pad size, pitch and order (PCB-L-04), via count per contact pad and pour symmetry (PCB-L-07), ESD distance (PCB-E-01) and test-pad coverage (PCB-T-02) are layout checks. The contact working height and the liner distance (PCB-L-06) are 3D review and case items. Review items are listed in the specification.

KiCad 10.0.7 can express three more rules, thermal-relief spoke count (`min_resolved_spokes`), differential-pair uncoupled length (`diff_pair_uncoupled`) and differential-pair gap (`diff_pair_gap`, with its maximum and the router's gap), but its report does not name the rule for them ("zone min spoke count", "(<rule> maximum uncoupled length", "(<rule> maximum gap"), so `check_drc.py` cannot attribute them. The pair gap's minimum is checked as a clearance instead (see Layers). They wait for a libs `kicad/` `check_drc.py` that reads those messages; until then they are CHK items below, with the other checks DRC cannot make.

## Review and script items (CHK)

Checklist wording; the level is the lowest at which the item is mandatory.

| ID | Level | Kind | Checklist wording |
|---|---|---|---|
| CHK-H-01 | Q1 | REV | The screw, washer and hole are chosen with the case; the PCB-H rules' 1.4 mm ring is recomputed from them, and H-01, H-02 become errors. |
| CHK-H-02 | Q2 | REV | Plated or non-plated mounting holes decided; if plated, on GND and stitched to the ground planes, and the case boss is insulating or its contact is part of the ESD path. |
| CHK-H-03 | Q1 | REV | No MLCC within the bending zone of a screw is oriented with its length towards the screw; parts near screws are placed with their long axis tangential to the hole. |
| CHK-B-01 | Q1 | REV | Tab and mouse-bite positions agreed with the fab's panel drawing; a `BREAK_TAB` area drawn at each, reaching 5.08 mm into the board. |
| CHK-B-02 | Q1 | REV | MLCCs within 5.08 mm of any broken edge lie parallel to the break line (KYOCERA AVX, Murata guidance; distance in PCB-B-03). |
| CHK-B-03 | Q1 | REV | Every part that overhangs the edge (J*, SW*) matches its case opening in the t1 interface files. |
| CHK-D-01 | Q1 | CHK | Three global fiducials per populated side, not symmetric, and two local fiducials at the RK3566 (PCB-M-09): count pads with the fiducial property per side. |
| CHK-D-02 | Q1 | REV | Polarity and pin-1 marks visible after assembly for every polarised part (diodes, tantalum or polymer capacitors, ICs, connectors). |
| CHK-D-03 | Q1 | REV | Paste on exposed thermal pads in a window pattern per each part's datasheet layout; coverage within the datasheet's range (**UNVERIFIED** generic figure, no IPC-7525 text retrieved). |
| CHK-D-04 | Q1 | CHK | Parts taller than the BGA within the rework clearance of a `Rework` = `BGA` part flagged from the 3D model heights. |
| CHK-D-05 | Q2 | CHK | Test pads 1.0 mm from component bodies (3D model outline), 5 mm from parts over 6.4 mm tall [JD]. |
| CHK-D-06 | Q1 | CHK | One test pad per net where required (PCB-T-02 rails, BRD-040 I2S, BRD-047 UART, BRD-015 SWD). |
| CHK-D-07 | Q1 | CHK | Via tenting set at board level (front and back tented), so only vias the layout opens on purpose are open; the fab order option matches. |
| CHK-D-08 | Q1 | CHK | Naming conventions followed: every mounting hole H*, fiducial pads carry the fiducial property, test pads the test-point property, BGA rework candidates and heat sources their fields. |
| CHK-W-01 | Q1 | CHK | Thermal relief on plane connections of connectors and test pads, at least 2 spokes resolved (PCB-G-07). KiCad `min_resolved_spokes` works but reports "zone min spoke count" without the rule name. |
| CHK-W-02 | Q2 | CHK | Differential-pair uncoupled length within the class limit. KiCad `diff_pair_uncoupled` works but reports "(<rule> maximum uncoupled length" without "rule '…'". The limit itself is **UNVERIFIED** (no source retrieved). |
| CHK-W-03 | Q2 | SIM | Via stubs over 0.30 mm on high-speed pairs simulated (Rockchip HSPCB p. 10 [RK]). |
| CHK-W-04 | Q2 | CHK | No test pad on a high-speed pair (Rockchip HSPCB p. 12 [RK]). Expressible in DRC as a later rule. |
| CHK-L-01 | Q0 | REV | `BATTERY_POCKET` drawn from the case's pocket outline plus the margin; the margin confirmed by the thermal analysis (V4-03). |
| CHK-V-01 | Q3 | REV | Creepage and clearance needs of IEC 62368-1 for the declared markets confirmed for ES1 circuits. |

## KiCad 10.0.7 behaviour found while testing

- **Angles are bare numbers.** `track_angle (min 90deg)` makes KiCad drop the whole file silently; `(min 90)` works. Each acute corner is reported twice, once per segment order.
- **A rule with `min 0` loses its name.** A `courtyard_clearance (min 0mm)` overlap is reported as the built-in "Courtyards overlap" without "(rule …)", so it cannot be tested; any value above zero is named.
- **Courtyards are measured from the line's centre; Edge.Cuts lines from their outer edge** in physical rules, and from their centre in `edge_clearance`.
- **Courtyard distance is per side.** A front part and a back footprint are not compared; hence the area-based PCB-L-01.
- **`physical_clearance` against a courtyard needs `A.Type == 'Footprint'`.** Without it the courtyard graphic and the footprint are both reported (two violations for one fault). A pad and a courtyard are on different layers and are never compared.
- **Silk to edge:** a silk line within the distance is reported only when the edge clips it; text is reported, but its distance to an internal cutout does not follow the text's position, so the test uses a clipped line.
- **`connection_width` fires** (tested with zone necks), but only about 0.01 mm or more below the limit; the test board uses 0.02 mm.
- **`min_resolved_spokes` and `diff_pair_uncoupled` work but are not named** in the report (CHK-W-01, CHK-W-02).
- **Unknown properties fail silently**: an assertion on a misspelt property fails on every object, which the PASS column catches. Via properties `Filling`, `Capping`, `Front_tenting`, `Back_tenting` and `Enable_Teardrops` exist with values `Filled`, `Capped`, `Tented`, `Not tented`.
- **`memberOfFootprint('H*')` is false for the footprint itself**; conditions on footprints use `Reference == 'H*'`.

## Sources of the rule values

Fetched 2026-10-24 unless stated.

| Key | Source | Kind |
|---|---|---|
| IPC | IPC-2221B Table 6-1 as reproduced in Altair Pollex documentation, "IPC Material": <https://help.altair.com/pollex/topics/pollex/verification/dfe_ipc_material_r.htm> | Secondary |
| F1 | ISO 7089 flat washer dimensions, fasten.it norm table: <https://www.fasten.it/en/norms/norm/iso_7089> (M2: d1 2.2, d2 5, h 0.3; M1.6: 1.7, 4, 0.3) | Secondary (vendor copy of the standard) |
| MU | Murata FAQ on chip capacitor mounting near screw holes: <https://www.murata.com/en-global/support/faqs/capacitor/ceramiccapacitor/mnt/0030> and the GRM data-sheet caution ("as far away from the screw holes as possible") | Primary |
| DK | DigiKey TechForum, "Ceramic Capacitor Failure: Design Solutions & Mitigating Board Flex Cracking", quoting KYOCERA AVX: <https://forum.digikey.com/t/ceramic-capacitor-failure-design-solutions-mitigating-board-flex-cracking/26195> | Secondary |
| JL | JLCPCB PCB capabilities (Legend, Outline, panelisation): <https://jlcpcb.com/capabilities/pcb-capabilities> | Primary (another fab) |
| JD | JLCPCB blog, "PCB Test Points and Smart DFT": <https://jlcpcb.com/blog/pcb-test-points-and-smart-dft> | Secondary |
| LC | LCSC blog, "How to Properly Place Fiducial Marks on PCBs": <https://www.lcsc.com/blog/how-to-properly-place-fiducial-marks-on-pcbs-a-step-by-step-guide/> | Secondary |
| AP | ALLPCB, "Non-Plated Through Holes: Design Rules": <https://www.allpcb.com/allelectrohub/non-plated-through-holes-design-rules-for-optimal-performance-and-reliability> | Secondary |
| RK | Rockchip RK3568 High Speed PCB Design Guide V1.0.0, cited by page | Primary |
| P1–P20 | The prototype fab's published pages, as keyed in libs' `kicad/` `pcbway-*` rule sets (fetched 2026-10-22): P1 capabilities, P2 advanced, P3 HDI, P11 via-in-pad, P16 order options, P20 assembly reminders | Primary |
| KiCad | KiCad 10.0.7 PCB Editor manual, custom rules (bundled `pcbnew.html`), and the behaviour listed above | Primary |

Not retrieved, so not used for any value: IPC-7351B courtyard excess table, IPC-7095 rework clearances, IPC-A-610, IPC-2152, IPC-7525 paste, SMEMA 3.1 text, TI and Intel high-speed layout guides for uncoupled length, the fab's pages on fiducials, test points and tab clearance, and any Li-ion cell maker's heat-source distance.
