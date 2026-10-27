# MCLK divider: ngspice simulation and phase-noise budget

The question: does the master-clock path of [ADR 0019](../../docs/adr/0019-master-clock-divided-from-twice-the-frequency.md)
(an NDK NSC5083D at 45.1584 or 49.152 MHz on MCLK_3V1, divided by two in one TI SN74AUC1G74
flip-flop per DAC on a 1.8 V MCLK_1V8 rail) deliver 22.5792 and 24.576 MHz to the XTI/MCLK inputs
of the two CS43198 inside their VL-domain limits, with a 45–55 % duty cycle that follows from
datasheet limits alone, without loading the oscillator beyond its 15 pF rating, and with phase noise
well inside the CS43198 mask? It replaces the passive attenuator of
[`../mclk-attenuator/`](../mclk-attenuator/README.md), which could not guarantee the duty cycle or
the oscillator load.

## Circuit

```text
XO 45.1584 MHz --[RX]--+                               +-- CLK  SN74AUC1G74 #1  Q --[RS]-- 5..15 mm -- XTI DAC1
                       +-- trace D (5..10 mm) ---------+   (D = /Q, PRE high, CLR = run)
XO 49.152 MHz  --[RX]--+   (one XO tri-stated,         +-- CLK  SN74AUC1G74 #2  Q --[RS]-- 5..15 mm -- XTI DAC2
                            100 kOhm pull-down)
```

Each flip-flop toggles on every rising edge of the oscillator (Q̅ to D), so its output period is
exactly two oscillator periods, whatever the oscillator's symmetry. The high time is one
oscillator period plus tPHL − tPLH of the flip-flop. At VCC 1.8 V ± 0.15 V and CL = 15 pF,
CLK → Q is 1.0 to 1.7 ns over process, supply and temperature (SCES537D p. 4), so
|tPHL − tPLH| ≤ 0.7 ns: 50 ± 1.7 % at 24.576 MHz and 50 ± 1.6 % at 22.5792 MHz from the
datasheet alone.

| Part | Value | Where |
|---|---|---|
| RX | 33 Ω | in series at each oscillator output |
| RPD | 100 kΩ | oscillator net to ground at the flip-flops (both oscillators may be tri-stated) |
| RS | 27 Ω | in series at each flip-flop Q output |
| Flip-flop supply | MCLK_1V8, TPS7A2018 (1.76–1.84 V) | enabled by DAC_DIG_1V8 |

## Inputs and their sources

| Input | Value | Source |
|---|---|---|
| Oscillator supply | 3.054–3.147 V | TPS7A2031 3.1 V ± 1.5 %, SBVS338H p. 6 |
| Oscillator output | Tr/Tf ≤ 6 ns at CL ≤ 15 pF, VOH ≥ 0.9 VCC, symmetry 40 % and 60 % run | NDK NZ2520SDA catalogue 1703A |
| Oscillator drive | 10 Ω ("strong"), 30 Ω ("typ"), 181 Ω ("bound") behind a 1 ns edge | 10 and 30 Ω **UNVERIFIED**; 181 Ω is the weakest linear driver that meets 6 ns into 15 pF (`xo-calibration.cir`) |
| Tri-stated oscillator | 2 pF | **UNVERIFIED** |
| Flip-flop clock input | 2.5 pF typ; 4 pF run as a bound | SCES537D p. 4 (typ only); 4 pF **UNVERIFIED** |
| Flip-flop input limits | VIH ≥ 0.65 VCC, VIL ≤ 0.35 VCC, VI 0–3.6 V (−0.5 V absolute), ≤ 20 ns/V, tw ≥ 1 ns | SCES537D pp. 3–4 |
| Flip-flop supply | 1.76–1.84 V | TPS7A2018 DBV, 1.8 V ± 40 mV, SBVS338H p. 6 |
| Flip-flop output | 56 Ω ("bound": VOH ≥ 1.2 V at −8 mA and VOL ≤ 0.45 V at 8 mA, VCC 1.65 V) or 15 Ω ("strong", **UNVERIFIED**), 0.3 ns intrinsic edge (**UNVERIFIED**) | SCES537D p. 4 |
| tPHL − tPLH | −0.7, 0, +0.7 ns | SCES537D p. 4: CLK → Q 1.0–1.7 ns at CL = 15 pF |
| XTI input capacitance | 1, 4 and 10 pF | 10 pF maximum, DS1156F2 Table 3-11 p. 19; no minimum given |
| XTI levels | VIH ≥ 0.7·VL, VIL ≤ 0.3·VL, pin −0.3 to VL + 0.3 V, VL 1.66–1.94 V | DS1156F2 Table 3-11 p. 19, Table 3-2 p. 12 |
| XTI duty cycle | 45–55 % | DS1156F2 §4.5.1 p. 35 |
| Traces | 50 Ω lossless, 7 ps/mm; oscillator to flip-flops 5 and 10 mm; flip-flop to XTI 5 and 15 mm | PCB-I-09 (50 Ω); lengths assumed, no layout yet |
| Pads and vias | 0.5 pF per pin, 0.3 pF per trace end | **UNVERIFIED** |

Duty at XTI is measured with the switching points anywhere between VIL and VIH (rising point at or
above the falling point), at VL 1.66 and 1.94 V and both MCLK_1V8 limits, as in the attenuator study.

## Results (2026-10-24, ngspice 47)

`odapkit sim run sim/mclk-divider`: 20 checks pass, none fail.

| Quantity, worst over corners | Value | Limit |
|---|---|---|
| Load on the oscillator net | 13.7 pF | ≤ 15 pF |
| Flip-flop clock: lowest peak / highest valley | 2.845 / 0.209 V | ≥ 1.196 / ≤ 0.616 V |
| Flip-flop clock: peak / valley | 3.146 / 0.000 V | ≤ 3.6 / ≥ −0.5 V |
| Flip-flop clock: shortest time above VIH or below VIL | 1.98 ns | ≥ 1 ns |
| Flip-flop clock: transition rate | 2.65 ns/V | ≤ 20 ns/V |
| Load on each flip-flop output | 12.6 pF | ≤ 15 pF |
| XTI high / low level | 1.737 / 0.023 V | ≥ 1.358 / ≤ 0.498 V |
| XTI peak / valley | 1.889 / −0.049 V | ≤ 1.96 / ≥ −0.3 V |
| XTI 10–90 % edge | 2.33 ns | (no limit) |
| XTI duty | 45.08–54.35 % | 45–55 % |
| Extra crossings of VIL/VIH (clock pins and XTI) | 0 | 0 |
| Phase-noise margin to the mask, 1 kHz / 100 kHz | 55.9 / 43.0 dB | ≥ 20 dB |
| RMS jitter (100 Hz–10 MHz mask: 46.3 ps) | 73 fs, margin 56.0 dB | ≥ 20 dB |

Reading:

1. Every limit holds at both frequencies, for any oscillator symmetry in the catalogue's 40–60 %,
   the weakest oscillator drive the catalogue allows, XTI capacitance up to the 10 pF maximum, and
   the full tPHL − tPLH spread of the flip-flop. The duty margin is 0.08 % at the corner where all
   of these stack: 56 Ω flip-flop output, 10 pF XTI, 15 mm, tPHL − tPLH = −0.7 ns, switching points
   at VIH rising and VIL falling.
2. Exploration (`run.py NAME=value`): a 20 mm branch gives 44.98 % (fails by 0.02 %); RS = 22 Ω
   gives 2.026 V peak with the strong output and 1 pF; RS = 33 Ω gives 44.24 % at 20 mm. A first
   run with one flip-flop driving both DACs (RS = 33 Ω, 20 mm, ±0.9 ns from the 30 pF column) gave
   41.8 % with the 56 Ω output: two 10 pF pins are too much for one AUC output, so each DAC has
   its own divider.
3. The phase-noise budget (`budget.py`) uses the NZ2520SDA catalogue figures at 49.152 MHz and
   3.3 V (−158 dBc/Hz at 1 kHz, −172 dBc/Hz at 100 kHz, 43 fs): −164 and −178 dBc/Hz after the
   ideal divide-by-two. Two divider terms are estimates, marked **UNVERIFIED**: the supply term
   (TPS7A20 10 µVrms through a 3.2 ns/V delay sensitivity bounded from SCES537D, −159.1 dBc/Hz,
   32 fs) and a floor taken from the LMK1C1102 maximum additive jitter (50 fs, −178.3 dBc/Hz). The
   supply term dominates the estimate: total −157.9 dBc/Hz at 1 kHz and −159.0 dBc/Hz at 100 kHz.

Open: the AUC1G74 supply sensitivity and additive phase noise (no TI data), the NSC5083D phase
noise at 45.1584 MHz and at 3.1 V, the XTI capacitance (typical) from Cirrus Logic, the
oscillator start-up waveform (whether the two dividers can start in opposite phase), and layout
keeping each divider-to-XTI branch at or under 15 mm and the oscillator-to-divider trace at or
under 10 mm.

## Files

| File | What it is |
|---|---|
| `xo-to-divider.cir` | Oscillator side: running and tri-stated oscillator, RX, trace, two flip-flop clock pins. Writes `xo.dat`. |
| `divider-to-xti.cir` | DAC side: one flip-flop output (behavioural, tPHL − tPLH as a parameter), RS, trace, XTI pin. Writes `xti.dat`. |
| `xo-calibration.cir` | Check of the "bound" oscillator model against the catalogue's 6 ns into 15 pF (same as the attenuator study). |
| `run.py` | Runs the corner set (48 + 72 cases), prints the tables or `--json`; `NAME=value` overrides netlist parameters. |
| `budget.py` | Phase-noise and jitter budget against DS1156F2 Figure 4-11; `--json` for the checks. |
| `checks.toml` | Regression checks for `odapkit sim`. |
| `.spiceinit` | ngspice start-up file (no compatibility mode: no vendor model). |

## Run

Tools: ngspice 47 or later, Python 3.10+ through `uv`. No vendor model is needed. Run from this
folder:

```sh
JOBS=2 uv run run.py              # 120 cases, under a minute
uv run run.py --json
uv run run.py RS=33 TDB=140p      # exploration
uv run budget.py
odapkit sim run .                 # the regression checks
```

Results go to `results/` (not committed); a case already in `results/` is not run again.
