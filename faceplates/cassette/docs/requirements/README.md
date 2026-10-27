# Cassette faceplate requirements

Requirements for the cassette faceplate of the OpenDAP T1.

| ID | Requirement | Priority | Status |
|---|---|---|---|
| FPC-001 | The cassette faceplate shall be inspired by cassette Walkmans. | must | Confirmed |
| FPC-002 | The cassette faceplate shall meet the [faceplate interface](https://github.com/opendap-project/t1/blob/main/docs/specs/faceplate-interface.md) defined in the t1 repository. | must | Confirmed |
| FPC-003 | The cassette faceplate shall keep its own mechanics in this repository. | must | Confirmed |
| FPC-004 | The cassette faceplate shall have a display and an ambient light sensor for dimming it (every faceplate has a display). | must | Confirmed |
| FPC-005 | The display driver shall be on the cassette faceplate. | must | Confirmed |
| FPC-006 | The cassette faceplate's status LED shall be controllable by developers, like the user LED on development boards. | must | Confirmed |
| FPC-007 | The cassette faceplate will most likely use an OLED or AMOLED display, without touch. | should | Confirmed |
| FPC-008 | Instead of touch, the cassette faceplate will most likely use physical controls: buttons, switches or dials. | should | Confirmed |
| FPC-009 | The cassette faceplate's controls shall reach Blackbird OS as standardized binary commands (see the faceplate interface in `t1`), not as raw signals. | must | Confirmed |
