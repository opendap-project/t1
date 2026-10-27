# Electronics

Tool: [KiCad](https://www.kicad.org) 10.

## Layout

- `<project>/`: one KiCad project per PCB, holding `<project>.kicad_pro`, `<project>.kicad_sch` and `<project>.kicad_pcb`.
- `lib/`: project-local libraries shared by every project in this folder.
  - `lib/symbols/`: symbol libraries (`*.kicad_sym`).
  - `lib/footprints/`: footprint libraries (`<name>.pretty/`).
  - `lib/3dmodels/`: 3D models (STEP) for footprints.

Reference `lib/` from each project's library tables with `${KIPRJMOD}/../lib/…`, so the projects work on any machine.

Generated outputs (Gerbers, drill files, BOM, renders) go to `<project>/fab/`, which is not committed. Generate them with `kicad-cli`.
