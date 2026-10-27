# RK3566 BGA escape and core-plane study

A KiCad study of how the RK3566 (FCCSP565L, 0.4 mm ring and 0.65 mm core) escapes on the T1 main board and how its power and ground planes connect under it, on the six-layer [stackup v3](../../../docs/specs/stackup-v3.md) (stack `v3`), with the composed T1 rules (KiCad 10.0.7). The SoC sits on the back (L6, ADR 0016) and its decoupling on the front under it (PCB-P-10). A grid router places and routes every used ball of `hardware/pinout/pinout-v1.csv`; the script places a ground microvia stack for every decoupling capacitor, draws one plane zone per rail on its plane layer, lets KiCad fill them, repairs cut-off ground, joins split rails, and KiCad's DRC is the judge.

| File | What it is |
|---|---|
| `escape.py` | Builds the study board for one stack (`ESCAPE_STACK`: `v3` stackup v3, the default; `z8` the superseded stackup v2; `v1-10l` stackup v1). Run with KiCad's Python |
| `bga-escape-v3.result.json` | Stackup v3: escaped balls per layer, via counts, decoupling ground stacks, ground clusters, joins, neck reliefs, DRC summary, and per rail its plane layers, vias, pieces and feed width at the package edge |
| `plots/` | Copper of the `v3` board on L6, L5, L4, L2 and L1, exported with `kicad-cli pcb export svg` and converted to PNG |

The boards (`bga-escape-<stack>.kicad_pcb`, `.kicad_pro` and the rule copy `.kicad_dru`) are generated, not committed (`.gitignore`).

## Run

```sh
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
$PY hardware/studies/bga-escape/escape.py        # stack v3, about 80 s, then KiCad's DRC
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
$K pcb drc --format json --severity-all -o drc-v3.json hardware/studies/bga-escape/bga-escape-v3.kicad_pcb
```

The RK3566 footprint is read from kicad-lib through the workspace `repos.tsv` (or `ODAP_KICAD_LIB_DIR`). The script runs KiCad's DRC itself (`KICAD_CLI` overrides the path) and writes its summary to the result. `ESCAPE_OUT=<dir>` writes elsewhere. `ESCAPE_HOLE_CU_IN_MIL=<mil>` runs the router at another inner hole-to-copper value and adds, to the study's rule copy only, a rule at that value limited to `BGA_ESCAPE`; `ESCAPE_DECAP=0` runs without the decoupling model.

## Stack v3 (stackup v3, core zone)

Study roles from the SoC side: L6 signal (the SoC), L5 ground, L4 signal (stacked microvias, two laser levels), L3 ground, L2 the core and system rails, L1 front (decoupling, core-rail pours between the capacitors, joins). Microvias: L6–L5 0.10 / 0.25 mm, L5–L4 0.125 / 0.275 mm; front ground stacks L1–L2–L3 the same; through vias 0.20 / 0.46 mm, non-functional inner pads removed on signal and ground vias, kept on power vias.

**Decoupling model.** Every capacitor of Rockchip's list near the SoC (HDG 1.1 pp. 35–41: 36 capacitors on 15 rails) gets a front-side ground microvia stack (L1–L2–L3) within 1.0 mm of one of its rail's through vias, where its power pad lands; its body (0.30 mm wide, 0201) is an obstacle on L1 and keeps the L1 fill out. Ground through vias around the package join the front ground, as the board's stitching will (PCB-S-19); a capacitor whose ground stack lands on a ground island is moved. The model has no footprints and one ground stack per capacitor: placement replaces it.

**Joins.** A rail left in pieces is joined by a short track on L4, on L2 through the other rails' pours (never on a core rail's feed), or on L1. Where two joins of one rail meet on L2, the rail's own fill can leave a sliver against their corner (a PCB-W-01 neck); the study keeps the rail's fill 0.15 mm off that corner (rule area `NECK_RELIEF`). A layout draws such joins as one track.

## Results (2026-10-25, pinout v1, 9 mil inner hole-to-copper)

1. **Every used signal ball escapes on two layers, L6 and L4.** 238 used signal balls: 136 on L6, 102 on L4 through stacked microvias. None needs L1, and no ball needs a via in its land.
2. **The decoupling fits.** 36 front ground stacks placed for 36 capacitors (2 moved off ground islands); 16 ground through vias around the package.
3. **The planes close.** One ground cluster, no ground island, no ground through via added. Every rail is one piece after joins (two rounds): vcca_1v8 (9 pieces before joins), vdda_0v9 (5), vcc3v3_sys (4), vcc_1v8 and vcca1v8_pmu (2 each) were joined on L4, L2 and L1; two neck reliefs on L2 (vcca_1v8).
4. **DRC with the composed rules: 0 errors, 0 unconnected items** at the fab's normal 9 mil hole-to-inner-copper.
5. **Plane feed at the package edge** against IPC-2221 inner width at ΔT 10 °C on 18 µm for the rail's design current (power tree v0.6; the SoC's own draw per rail **UNVERIFIED**): with the L1 pours between the capacitors, every core rail has more copper than it needs (table). Four small rails (vcc0v6_ddr, vccio6_1v8, vccio_sd, vdda_0v9; 0.1–0.4 A) do not reach the package edge on their plane; they are fed by a track at layout, at the width in the table.

| Rail | Plane | Design current | Balls | Through vias (PCB-P-09 needs) | Pieces before joins | Feed at the edge | IPC-2221 width |
|---|---|---|---|---|---|---|---|
| vdd_cpu | L2 + L1 | 3.0 A | 11 | 9 (6) | 1 | 15.28 mm | 6.91 mm |
| vdd_gpu | L2 + L1 | 2.5 A | 5 | 5 (5) | 1 | 15.08 mm | 5.38 mm |
| vdd_logic | L2 + L1 | 2.5 A | 9 | 8 (5) | 1 | 5.52 mm | 5.38 mm |
| vcc_ddr | L2 + L1 | 1.5 A | 8 | 8 (3) | 1 | 21.83 mm | 2.66 mm |
| vdd_npu | L2 + L1 | 1.5 A | 5 | 5 (3) | 1 | 15.85 mm | 2.66 mm |
| vcca_1v8 | L2 | 0.4 A | 11 | 9 (1) | 9 | 10.58 mm | 0.43 mm |
| vdda_0v9 | L2 | 0.4 A | 10 | 7 (1) | 5 | 0.12 mm (track) | 0.43 mm |
| vcc0v6_ddr | L2 + L1 | 0.3 A | 5 | 5 (1) | 1 | 0 (track) | 0.29 mm |
| vcc3v3_sys | L2 | 0.3 A | 6 | 6 (1) | 4 | 6.10 mm | 0.29 mm |
| vcc_1v8 | L2 | 0.3 A | 2 | 2 (1) | 2 | 0.56 mm | 0.29 mm |
| other PMU and I/O rails | L2 | 0.1 A each | 1–2 | 1–2 (1) | 1–2 | 0–8.25 mm | 0.06 mm |

vdd_logic's balls sit in the middle of the core, surrounded by the other core rails; the script opens feed corridors for it on L2 between the other rails' areas, which with its L1 pour gives 5.52 mm against 5.38 mm.

| | v3 (stackup v3) |
|---|---|
| Signal balls escaped: L6 / L4 / L1 | 136 / 102 / 0 |
| Signal balls not escaped | 0 |
| Microvias into the L5 ground | 188 |
| Stacked microvias L6–L5–L4 (signals) | 102 |
| Front ground stacks L1–L2–L3 (decoupling) | 36, one per capacitor |
| Through vias | 88 (8 shared by two balls of one rail; 16 ground stitching outside the package) |
| Via in pad | 0 |
| Ground clusters / islands | 1 / 0 |
| Rails split after joins | 0 |
| DRC errors / unconnected | 0 / 0 |
| DRC warnings | 199 track ends (study stubs that stop outside the body), 148 PCB-W-02 teardrops (Q2), 74 PCB-D-10 open via near an SMD pad (Q1, tenting at layout), 51 CRAFT-45 via set (the second laser level), 36 vias on one layer (the decoupling stacks' L1 end, which the model gives no capacitor pad), 11 isolated fill, 6 silk, 1 library |

The superseded stack `z8` (stackup v2) remains runnable without the decoupling model, as it was run for stackup v2.
