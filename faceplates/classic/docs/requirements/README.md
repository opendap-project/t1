# Classic faceplate requirements

Requirements for the classic faceplate of the OpenDAP T1.

| ID | Requirement | Priority | Status |
|---|---|---|---|
| FPK-001 | The classic faceplate shall be inspired by classic portable music players. | must | Confirmed |
| FPK-002 | The classic faceplate shall meet the [faceplate interface](https://github.com/opendap-project/t1/blob/main/docs/specs/faceplate-interface.md) defined in the t1 repository. | must | Confirmed |
| FPK-003 | The classic faceplate shall keep its own mechanics in this repository. | must | Confirmed |
| FPK-004 | The classic faceplate shall have a display and an ambient light sensor for dimming it (every faceplate has a display). | must | Confirmed |
| FPK-005 | The display driver shall be on the classic faceplate. | must | Confirmed |
| FPK-006 | The classic faceplate's status LED shall be controllable by developers, like the user LED on development boards. | must | Confirmed |
| FPK-007 | The classic faceplate will most likely use an OLED or AMOLED display, without touch. | should | Confirmed |
| FPK-008 | Instead of touch, the classic faceplate will most likely use physical controls: buttons, switches or dials. | should | Confirmed |
| FPK-009 | The classic faceplate's controls shall reach Blackbird OS as standardized binary commands (see the faceplate interface in `t1`), not as raw signals. | must | Confirmed |

## Context

- FPK-001 (maintainers, 2026-10-26): reworded without a product name; the intent is unchanged.
