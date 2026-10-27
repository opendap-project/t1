# T1 main board floorplan study

A KiCad study board for [floorplan v1](../../../docs/specs/floorplan-v1.md): the outline, the zones and corridors as named rule areas (`ZONE_<NAME>`, `ZONE_CORRIDOR`), the height and battery areas, the mounting holes and every part whose position the product fixes, placed from libs footprints, checked with the composed T1 rules (KiCad 10.0.7).

| File | What it is |
|---|---|
| `floorplan.py` | Builds the study board and the area budget. Run with KiCad's Python |

What it writes, generated and not committed (`.gitignore`): the board `floorplan-v1.kicad_pcb` with its `.kicad_pro` and `.kicad_dru` (no wiring, only placed parts and rule areas), and `floorplan-v1.result.json`, the area budget per zone and side (courtyards from libs or estimates, the placement factor, the band, back and front use). Floorplan v1 §2.1 states the budget.

## Run

```sh
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
$PY hardware/studies/floorplan/floorplan.py            # six layers (stackup v3)
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
$K pcb drc --format json --severity-all -o drc.json hardware/studies/floorplan/floorplan-v1.kicad_pcb
```

`FLOORPLAN_OUT=<dir>` writes elsewhere; `FLOORPLAN_LAYERS` sets the copper layer count. libs is read through the workspace `repos.tsv`, `ODAP_KICAD_LIB_DIR` or the `hardware/lib/opendap` submodule.

## What it establishes

DRC with the composed rules: 0 errors. The warnings are PCB-L-01 for the SoC, the PMIC and the TPS62903 under the pocket (floorplan v1 §6 item 3), silkscreen at the board edge from the edge connectors' footprints, and the libraries the study project does not list.
