# MCLK attenuator: ngspice simulation

Superseded on 2026-10-24 by [ADR 0019](../../docs/adr/0019-master-clock-divided-from-twice-the-frequency.md)
and the [`mclk-divider`](../mclk-divider/README.md) study: the attenuator is removed. This study stays as
the record of why.

The question: does the passive attenuator of [ADR 0010](../../docs/adr/0010-audio-master-clock-source.md)
bring the 3.1 V master clock of the NDK NSC5083D oscillators (BOM v1 lines 20, 21, on the
TPS7A2031 MCLK_3V1 rail, line 29) into the XTI/MCLK inputs of the two CS43198 (line 18) inside
their 1.8 V VL-domain limits, with clean edges and a 45–55 % duty cycle at 22.5792 and 24.576 MHz,
without loading the oscillator beyond its rating? BOM v1 §7 item 1.

## Circuit

```text
XO 22.5792 MHz --[R1 || C1]--+                      +--[RD]--+-- XTI DAC1: 2·R2 || C2/2 to GND
                             +-- trace A -- split --+
XO 24.576 MHz  --[R1 || C1]--+   (one XO tri-stated)+--[RD]--+-- XTI DAC2: 2·R2 || C2/2 to GND
```

A compensated divider: R1 and R2 set the level (ratio 0.55), C1 carries the edge so the pin
capacitance does not slow it, and RD damps the trace inductance against the pin capacitance.
Values simulated (the defaults of `mclk-attenuator.cir`, proposed, not decided):

| Part | Value | Where |
|---|---|---|
| R1 | 820 Ω 1 % | at each oscillator output |
| C1 | 27 pF C0G | across each R1 |
| RD | 47 Ω | in series at each XTI pin |
| 2·R2 | 2.0 kΩ 1 % | XTI to ground, at each DAC |
| C2/2 | 2.2 pF C0G | XTI to ground, at each DAC |

DC load on the running oscillator at the high level: 1.7 mA (VCC / (R1 + R2)).

## Inputs and their sources

| Input | Value | Source |
|---|---|---|
| Oscillator supply | 3.054–3.147 V | TPS7A2031 3.1 V ±1.5 %, SBVS338H p. 6 |
| Oscillator output | Tr/Tf ≤ 6 ns at CL ≤ 15 pF, VOH ≥ 0.9 VCC, symmetry 40–60 % | NDK NZ2520SDA catalogue 1703A |
| Oscillator drive | 30 Ω behind a 1 ns edge ("typ") | **UNVERIFIED**: NDK publishes no output impedance |
| Oscillator drive, catalogue bound | 181 Ω behind a 1 ns edge ("bound") | The weakest linear driver that still gives Tr = 6 ns into 15 pF (`xo-calibration.cir`: 5.996 ns) |
| Tri-stated oscillator | 2 pF | **UNVERIFIED** |
| XTI input capacitance | 1, 4 and 10 pF | 10 pF maximum, DS1156F2 Table 3-11 p. 19; no minimum given |
| XTI pull-down | 550 kΩ | Minimum of Table 3-11 p. 19 |
| XTI levels | VIH ≥ 0.7·VL, VIL ≤ 0.3·VL, pin −0.3 to VL + 0.3 V, VL 1.66–1.94 V | DS1156F2 Table 3-11 p. 19, Table 3-2 p. 12 |
| XTI duty cycle | 45–55 % | DS1156F2 §4.5.1 p. 35 |
| Traces | 50 Ω lossless, 7 ps/mm; "short" 10/10/10 mm and "limit" 20/20/20 mm (trace A / to DAC1 / to DAC2) | PCB-I-09 (50 Ω); delay √4.4 / c (stripline FR-4); lengths assumed, no layout yet |
| Pads and vias | 0.5 pF per pin, 0.3 pF per trace end | **UNVERIFIED** |

Duty is measured for an ideal 50 % source with the switching points anywhere between VIL and VIH
(rising point at or above the falling point), at VL 1.66 and 1.94 V and both supply limits. The
oscillator's own symmetry (40–60 %) is not in it.

## Results (2026-10-24, ngspice 47)

`odapkit sim run sim/mclk-attenuator`: 10 checks pass, `xo-load` fails.

| Quantity, worst over corners | "typ" driver | "bound" driver | Limit |
|---|---|---|---|
| XTI high level | 1.413 V | 1.052 V | ≥ 1.358 V |
| XTI low level | 0.221 V | 0.467 V | ≤ 0.498 V |
| XTI peak / valley | 1.900 / −0.223 V | 1.693 / −0.141 V | ≤ 1.96 / ≥ −0.3 V |
| XTI 10–90 % rise / fall | 2.09 / 2.03 ns | 8.05 / 7.74 ns | ≤ 6 ns |
| XTI duty | 45.6–51.9 % | 9.8–57.5 % | 45–55 % |
| Extra crossings of VIL/VIH | 0 | 0 | 0 |
| Oscillator edge into the network | 1.75 ns | 3.91–6.38 ns | ≤ 6 ns (its 15 pF rating) |

Reading:

1. With a typical CMOS oscillator output, the proposed values meet every XTI limit at both
   frequencies, for any input capacitance up to the 10 pF maximum and branches up to 20 mm. The
   duty margin is thin (45.6 % at 10 pF). Exploration with `run.py TDB=…`: a 30 mm branch to one
   DAC gives 1.97 V peak and 44.8 % duty, a 60 mm branch rings back across VIL/VIH; a resistive
   divider without C1 cannot keep the duty inside 45–55 % at 10 pF per pin.
2. With the weakest drive the NDK catalogue allows, nothing passes: the network loads the
   oscillator beyond its 15 pF rating when both DAC pins are at 10 pF (`xo-load`, 6.03–6.38 ns),
   and the XTI levels and duty fail. No passive values were found that pass this corner with two
   DAC inputs on one net.
3. The NZ2520SDA symmetry (40–60 %) is wider than the CS43198's 45–55 %: the oscillator alone
   can violate the DAC requirement, whatever the attenuator does.

Open: the NSC5083D output drive (impedance or VOH at a stated IOH) and its typical symmetry from
NDK, or a measurement on the first boards; the XTI input capacitance (typical) from Cirrus Logic;
layout keeping each clock branch at or under 20 mm.

## Files

| File | What it is |
|---|---|
| `mclk-attenuator.cir` | The clock path: running and tri-stated oscillator, attenuator, traces, two XTI pins. Writes `mclk.dat`. |
| `xo-calibration.cir` | Check of the "bound" oscillator model against the catalogue's 6 ns into 15 pF. |
| `run.py` | Runs the corner set, prints the table or `--json`; `NAME=value` arguments override netlist parameters for exploration. |
| `checks.toml` | Regression checks for `odapkit sim`. |
| `.spiceinit` | ngspice start-up file (no compatibility mode: no vendor model). |

## Run

Tools: ngspice 47 or later, Python 3.10+ through `uv`. No vendor model is needed. Run from this
folder:

```sh
ngspice -b xo-calibration.cir | grep xo_t
JOBS=2 uv run run.py              # 24 cases, a few seconds
uv run run.py --json
uv run run.py RD=68 C1=33p        # exploration
odapkit sim run .                 # the regression checks
```

Results go to `results/` (not committed); a case already in `results/` is not run again.

## Regression

Superseded by [`../mclk-divider/`](../mclk-divider/) and [ADR 0019](../../docs/adr/0019-master-clock-divided-from-twice-the-frequency.md). Its checks are kept as `checks.superseded.toml`, which `odapkit sim` does not run, so the board regression reflects the design in force.
