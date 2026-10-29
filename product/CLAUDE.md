# T1

Product integration of the OpenDAP T1: product requirements, the complete assembly and system simulations.

## Working here

- Product requirements are in `docs/requirements/`. Update them with the `/opendap:requirement` skill; write an ADR (`/opendap:adr`) only for decisions taken.
- Build the assembly and simulations only from components' `export/` folders, pinned in `components.yaml`, following the [component export contract](https://github.com/opendap-project/tools/blob/main/hardware/docs/specs/component-export.md). Never copy component sources here.
