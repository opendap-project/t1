# Case

The physical case of the OpenDAP T1: the core with its basic back cover, the device-side HAT case mechanics, and the mount that faceplates attach to. Product requirements live in [`t1`](https://github.com/opendap-project/t1); each faceplate keeps its own mechanics in its repository.

## Layout

- `core/` — main enclosure, including the basic back cover. A HAT replaces the back cover with a HAT case, following the HAT Case Standard.
- `hat-mount/` — the HAT's device-side piece, fixed to the core.
- `renders/`
- `export/`
- `docs/` — requirements and ADRs

## License

This repository follows the [REUSE](https://reuse.software) layout: license texts live in `LICENSES/` and `REUSE.toml` maps each path to its license.

- Default: **CERN Open Hardware Licence v2 – Strongly Reciprocal** (`CERN-OHL-S-2.0`)
- Markdown files: **Creative Commons Attribution-ShareAlike 4.0** (`CC-BY-SA-4.0`)
- `renders/`: **Creative Commons Attribution-ShareAlike 4.0** (`CC-BY-SA-4.0`)
- `export/`: **CERN Open Hardware Licence v2 – Weakly Reciprocal** (`CERN-OHL-W-2.0`)
- `docs/`: **Creative Commons Attribution-ShareAlike 4.0** (`CC-BY-SA-4.0`)

Copyright © 2026 The OpenDAP Project.
