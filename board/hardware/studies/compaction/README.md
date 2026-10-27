# T1 main board compaction study

The matrix tool behind [placement v1](../../../docs/specs/placement-v1.md) §4 decision 12 and [BOM v1.15](../../../docs/specs/bom-v1.md#changes-in-v115): which parts of the placed board can be lower or smaller without giving up a margin, checked against the design's stresses.

| File | What it is |
|---|---|
| `candidates.toml` | The rules, each converter's stresses (power tree v0 §4.10), the candidate parts and the capacitor positions, every value with its source |
| `compaction.py` | The matrices: inductors, capacitors over 1.0 mm, and with `--netlist` the test pads and the 0201 decoupling of the schematic |
| `compaction.result.json` | The last run's result |
| `tests/` | Fixture tests: `python3 -m unittest discover -s hardware/studies/compaction/tests` |

## Rules

| Family | Gate | Source |
|---|---|---|
| Inductors | Same inductance; design peak ≤ 70 % and the converter's maximum current limit ≤ 100 % of Isat (30 % drop); continuous current ≤ 70 % of Irms; height ≤ 1.5 mm to stand under the pocket; the XxL4020 land | BRD-049 as power tree v0 §4.10 applies it; PCB-Z-01; the makers' drawings |
| Capacitors over 1.0 mm | Same value, rating and dielectric, ≤ 1.0 mm (front, PCB-Z-03); lifecycle active; sourcing; DC bias carried as stated (DRV-107) | Sourcing matrix (T1-029) |
| 0201 decoupling | 100 nF on a rail of at most half the 0201 part's 10 V rating, in the core, I/O or radio zone; the audio zone keeps its parts (T1-040) | The sheets' rule "rated at least twice the rail"; ADR 0016 item 3 (the part under the BGA) |
| Test pads | 0.8 mm on signal nets, 1.0 mm on power and ground nets | PCB-D-06 v0.16 (JLCPCB DFT guide) |

Availability and cost are read by `odapkit parts matrix` and kept privately; `candidates.toml` carries only each part's outcome (`sourcing`: pass, conditional, fail, or open when no channel the matrix reads lists a line its maker sells in its own store; open ranks as conditional and is closed before the BOM freeze).

## Run

```sh
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
$K sch export netlist --format kicadsexpr -o /tmp/t1.net hardware/t1-main-board/t1-main-board.kicad_sch
python3 hardware/studies/compaction/compaction.py --netlist /tmp/t1.net
```

## Result (2026-10-27)

| Position | Part | h (mm) | Peak / Isat30 | Limit / Isat30 | Irms use | DCR loss vs current (mW) | Sourcing | Verdict (under the pocket) |
|---|---|---|---|---|---|---|---|---|
| L601 BQ25798 charger | XGL4015-102MEC **chosen** | 1.5 | 48 % | 86 % | 35 % | 8.9 | open | conditional |
| L601 BQ25798 charger | XGL4012-102MEC | 1.2 | 53 % | 95 % | 43 % | 59.5 | fail | fail |
| L601 BQ25798 charger | XAL4020-102MEC (current) | 2.1 | 40 % | 72 % | 34 % | 0.0 | conditional | fail |
| L901 TPS62136 VSYS_LV | XGL4015-152MEC | 1.5 | 62 % | 103 % | 39 % | 29.1 | fail | fail |
| L901 TPS62136 VSYS_LV | XGL4020-152MEC (current) **kept** | 2.1 | 52 % | 87 % | 26 % | 0.0 | conditional | fail |
| L2802 LMR33630C −7 V | XGL4015-222MEC | 1.5 | 43 % | 103 % | 40 % | 34.0 | fail | fail |
| L2802 LMR33630C −7 V | XGL4020-222MEC (current) **kept** | 2.1 | 34 % | 81 % | 27 % | 0.0 | conditional | fail |
| L4401 TPS62903 5.1 V | XGL4015-102MEC **chosen** | 1.5 | 29 % | 78 % | 25 % | 17.4 | open | conditional |
| L4401 TPS62903 5.1 V | XGL4020-102MEC (current) | 2.1 | 24 % | 65 % | 18 % | 0.0 | conditional | fail |
| L1001 TPS62827 vcc3v3_sys | XGL4015-471MEC **chosen** | 1.5 | 25 % | 61 % | 26 % | — | conditional | conditional |
| L1001 TPS62827 vcc3v3_sys | XFL4015-471MEC | 1.6 | 40 % | 97 % | 27 % | — | conditional | fail |
| L1001 TPS62827 vcc3v3_sys | 744373240047 (current) | 1.8 | 39 % | 94 % | 28 % | — | pass | fail |
| L5101 TPS62826 vcc1v8_wl | XGL4015-471MEC **chosen** | 1.5 | 14 % | 48 % | 4 % | — | conditional | conditional |
| L1201 TPS62869 vdd_cpu | XGL4012-221MEC (current) **kept** | 1.2 | 26 % | 59 % | 28 % | 0.0 | conditional | conditional |

Capacitors over 1.0 mm: none passes. The thinner 0805 parts of the same value, rating and dielectric are obsolete (GRM219R61E106KA12D), not for new designs (C2012X5R1E106K085AC, C2012X5R1C226M085AC) or not listed at an authorized channel (C2012X7R1C106K085AC, C2012X7R1E475K085AC); a smaller case needs DC-bias figures first (DRV-107).

With the schematic of 2026-10-27: 166 test pads, 51 of 0.8 mm (signal nets) and 115 of 1.0 mm (rails, ground, measurement links, contact pads), none under its net's minimum; 58 capacitors of 100 nF on eligible rails, all 0201. The board need with the floorplan's method falls from 113 % to 111 % of both sides (placement v1 §3.1).
