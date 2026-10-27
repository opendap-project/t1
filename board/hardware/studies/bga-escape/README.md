# RK3566 BGA escape and core-plane study

A KiCad study of how the RK3566 (FCCSP565L, 0.4 mm ring and 0.65 mm core) escapes on the T1 main board and how its power and ground planes connect under it, on the six-layer [stackup v3](../../../docs/specs/stackup-v3.md) (stack `v3`), with the composed T1 rules (KiCad 10.0.7). The SoC sits on the back (L6, ADR 0016) and its decoupling on the front under it (PCB-P-10). A grid router places and routes every used ball of `hardware/pinout/pinout-v1.csv`; the script places a ground microvia stack for every decoupling capacitor, draws one plane zone per rail on its plane layer, lets KiCad fill them, repairs cut-off ground, joins split rails, and KiCad's DRC is the judge.

| File | What it is |
|---|---|
| `escape.py` | Builds the study board for one stack (`ESCAPE_STACK`: `v3` stackup v3, the default; `z8` the superseded stackup v2; `v1-10l` stackup v1). Run with KiCad's Python |

What it writes, generated and not committed (`.gitignore`): the board `bga-escape-<stack>.kicad_pcb` with its `.kicad_pro` and rule copy `.kicad_dru`, and `bga-escape-<stack>.result.json` (escaped balls per layer, via counts, decoupling ground stacks, ground clusters, joins, neck reliefs, DRC summary, and per rail its plane layers, vias, pieces and feed width at the package edge). Copper plots, when needed, are exported from the board (below) into `plots/`, also ignored.

## Run

```sh
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
$PY hardware/studies/bga-escape/escape.py        # stack v3, about 80 s, then KiCad's DRC
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
$K pcb drc --format json --severity-all -o drc-v3.json hardware/studies/bga-escape/bga-escape-v3.kicad_pcb
$K pcb export svg --mode-multi --layers B.Cu,In4.Cu,In3.Cu,In1.Cu,F.Cu -o hardware/studies/bga-escape/plots/ hardware/studies/bga-escape/bga-escape-v3.kicad_pcb   # copper plots (L6, L5, L4, L2, L1)
```

The RK3566 footprint is read from libs through the workspace `repos.tsv` (or `ODAP_KICAD_LIB_DIR`). The script runs KiCad's DRC itself (`KICAD_CLI` overrides the path) and writes its summary to the result. `ESCAPE_OUT=<dir>` writes elsewhere. `ESCAPE_HOLE_CU_IN_MIL=<mil>` runs the router at another inner hole-to-copper value and adds, to the study's rule copy only, a rule at that value limited to `BGA_ESCAPE`; `ESCAPE_DECAP=0` runs without the decoupling model.

## What the study models (stack v3, core zone)

Study roles from the SoC side: L6 signal (the SoC), L5 ground, L4 signal (stacked microvias, two laser levels), L3 ground, L2 the core and system rails, L1 front (decoupling, core-rail pours between the capacitors, joins). Microvias: L6–L5 0.10 / 0.25 mm, L5–L4 0.125 / 0.275 mm; front ground stacks L1–L2–L3 the same; through vias 0.20 / 0.46 mm, non-functional inner pads removed on signal and ground vias, kept on power vias.

- **Decoupling.** Every capacitor of Rockchip's list near the SoC (HDG 1.1 pp. 35–41: 36 capacitors on 15 rails) gets a front-side ground microvia stack (L1–L2–L3) within 1.0 mm of one of its rail's through vias; its body (0.30 mm wide, 0201) is an obstacle on L1. Ground through vias around the package join the front ground (PCB-S-19). The model has no footprints and one ground stack per capacitor: placement replaces it.
- **Joins.** A rail left in pieces is joined by a short track on L4, on L2 through the other rails' pours (never on a core rail's feed), or on L1. Where two joins of one rail meet on L2, the rail's fill is kept 0.15 mm off their corner (rule area `NECK_RELIEF`) so it leaves no PCB-W-01 neck.

## What it establishes (pinout v1, stackup v3, 9 mil inner hole-to-copper)

1. **Every used signal ball escapes on two layers, L6 and L4**: 238 used signal balls, 136 on L6 and 102 on L4 through stacked microvias. None needs L1, and no ball needs a via in its land.
2. **The decoupling fits**: one front ground stack for each of the 36 capacitors.
3. **The planes close**: one ground cluster, no ground island; every rail is one piece after joins on L4, L2 and L1 (vcca_1v8, vdda_0v9, vcc3v3_sys, vcc_1v8 and vcca1v8_pmu need them).
4. **DRC with the composed rules: 0 errors, 0 unconnected items** at the fab's normal 9 mil hole-to-inner-copper.
5. **Plane feed at the package edge** against IPC-2221 inner width at ΔT 10 °C on 18 µm for the rail's design current (power tree v0.6; the SoC's own draw per rail **UNVERIFIED**): with the L1 pours between the capacitors, every core rail has more copper than it needs. Four small rails (vcc0v6_ddr, vccio6_1v8, vccio_sd, vdda_0v9; 0.1–0.4 A) do not reach the package edge on their plane and are fed by a track at layout, at the width in the table.

| Rail | Plane | Design current | Balls | Through vias (PCB-P-09 needs) | Feed at the edge | IPC-2221 width |
|---|---|---|---|---|---|---|
| vdd_cpu | L2 + L1 | 3.0 A | 11 | 9 (6) | 15.28 mm | 6.91 mm |
| vdd_gpu | L2 + L1 | 2.5 A | 5 | 5 (5) | 15.08 mm | 5.38 mm |
| vdd_logic | L2 + L1 | 2.5 A | 9 | 8 (5) | 5.52 mm | 5.38 mm |
| vcc_ddr | L2 + L1 | 1.5 A | 8 | 8 (3) | 21.83 mm | 2.66 mm |
| vdd_npu | L2 + L1 | 1.5 A | 5 | 5 (3) | 15.85 mm | 2.66 mm |
| vcca_1v8 | L2 | 0.4 A | 11 | 9 (1) | 10.58 mm | 0.43 mm |
| vdda_0v9 | L2 | 0.4 A | 10 | 7 (1) | track | 0.43 mm |
| vcc0v6_ddr | L2 + L1 | 0.3 A | 5 | 5 (1) | track | 0.29 mm |
| vcc3v3_sys | L2 | 0.3 A | 6 | 6 (1) | 6.10 mm | 0.29 mm |
| vcc_1v8 | L2 | 0.3 A | 2 | 2 (1) | 0.56 mm | 0.29 mm |
| other PMU and I/O rails | L2 | 0.1 A each | 1–2 | 1–2 (1) | 0–8.25 mm | 0.06 mm |

vdd_logic's balls sit in the middle of the core, surrounded by the other core rails; the script opens feed corridors for it on L2 between the other rails' areas.

The superseded stack `z8` (stackup v2) remains runnable without the decoupling model.
