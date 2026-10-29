# Board

Main board of the OpenDAP T1: the SoC-based single board computer, its auxiliary MCUs and simulations.

## Layout

- `hardware/`
- `firmware/`
- `sim/`
- `export/`
- `outputs/`: the [committed visual outputs](outputs/README.md) of the main board (RFC [0021](https://github.com/opendap-project/rfcs/blob/main/text/0021-committed-visual-outputs.md)): the schematic as PDF and one SVG per sheet, one SVG per board layer, 3D renders from four fixed views. Declared in `outputs.toml`; `odw render update .` regenerates them, never by hand
- `outputs.toml`
- `docs/`

## License

This repository follows the [REUSE](https://reuse.software) layout: license texts live in `LICENSES/` and `REUSE.toml` maps each path to its license.

- Default: **Creative Commons Attribution-ShareAlike 4.0** (`CC-BY-SA-4.0`)
- `hardware/`: **CERN Open Hardware Licence v2 – Strongly Reciprocal** (`CERN-OHL-S-2.0`)
- `firmware/`: **MIT** (`MIT`)
- `sim/`: **GNU GPL v3.0 or later** (`GPL-3.0-or-later`)
- `export/`: **CERN Open Hardware Licence v2 – Weakly Reciprocal** (`CERN-OHL-W-2.0`)
- `docs/`: **Creative Commons Attribution-ShareAlike 4.0** (`CC-BY-SA-4.0`)

Copyright © 2026 The OpenDAP Project.
