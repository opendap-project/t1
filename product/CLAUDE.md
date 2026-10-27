# T1

Product integration of the OpenDAP T1: product requirements, the complete assembly and system simulations.

<!-- >>> odapkit sync: managed block from the workspace templates; edit them, not this block -->
Part of [OpenDAP](https://github.com/opendap-project). This repository is Open Source.

Contributor rules (English, confirmed information only, REUSE licensing, the `docs/` layout and its skills): the [contributor guide](https://github.com/opendap-project/.github/blob/main/CONTRIBUTING.md).
<!-- <<< odapkit sync -->

## Working here

- Product requirements are in `docs/requirements/`. Update them with the `/opendap:requirement` skill; write an ADR (`/opendap:adr`) only for decisions taken.
- Build the assembly and simulations only from components' `export/` folders, pinned in `components.yaml`, following the [component export contract](https://github.com/opendap-project/toolkit-hardware/blob/main/docs/specs/component-export.md). Never copy component sources here.
