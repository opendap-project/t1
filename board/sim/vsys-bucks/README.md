# VSYS bucks: ngspice simulation

The question: do the two bucks that the 2S battery adds ([ADR 0014](../../docs/adr/0014-two-cell-battery.md),
BOM v1.5) hold their load steps, ripple, loop stability and BRD-049 current margins across
VSYS 6.0–8.8 V?

- **TPS62903** (line 91): VSYS → 5.1 V for HAT_5V and the USB-C source, 1.6 A design output.
- **TPS62136** (line 113): VSYS → 3.8 V VSYS_LV, the rail that feeds the former 1S tree, 2.0 A peak.

Results are below.

## Files

| File | What it is |
|---|---|
| `dcs-buck-generic.lib` | Open behavioural model of a DCS-Control-class buck (constant on-time, ripple emulation, integrator, current limits, power save). Not a TI model. Calibrated against TI's TPS62136 model (`check` group). |
| `tps62903-5v1-step.cir` | TPS62903 load step 0.1 → 1.6 → 0.1 A, generic model. TI's TPS62903 models are encrypted PSpice (SLVMDN8) or SIMPLIS (SLVMDP3) and do not run in ngspice. |
| `tps62903-5v1-loop.cir` | TPS62903 loop gain at one frequency (voltage injection), generic model. |
| `tps62136-3v8-step.cir` | TPS62136 load step 0.1 → 2.0 → 0.1 A with TI's transient model. |
| `tps62136-3v8-loop.cir` | TPS62136 loop gain at one frequency with TI's transient model. |
| `generic-check-step.cir`, `generic-check-loop.cir` | The generic model with TPS62136 values, for comparison with TI's model. |
| `run.py` | Runs the corner sets and prints the result tables; `--json` prints one JSON document (one case per line) that `checks.toml` reads. |
| `.spiceinit` | ngspice PSpice compatibility mode, needed by TI's model. |

## Vendor model (not in this repository)

`tps62136-3v8-*.cir` need TI's **TPS62136 PSpice Unencrypted Transient Model**,
[SLVMC09](https://www.ti.com/lit/zip/SLVMC09) (model "Final 1.1", 20MAR2017; the link serves
revision SLVMC09A without login). It is TI copyright, all rights reserved, so it is not
redistributed. `odapkit sim fetch` downloads it through the libs parts manifest (`kind = "spice"`),
checks both hashes and places `TPS62136_PSPICE_TRANS/TPS62136_TRANS.lib` in `models/` (ignored
by git); or unzip it by hand. The copy used on
2026-10-22: `SLVMC09.zip` sha256 `764f65e3e817b73ef0690637fb1a08ab7fa04ec5a1858b203dc7cf555a04ad99`,
`TPS62136_TRANS.lib` sha256 `252dce79505a414bd31e4bd2209334de90761d277894c759c3f88da003439a56`.

The generic netlists need no vendor file.

## Run

Tools: ngspice 47 or later, Python 3.10+ through `uv`. Run from this folder, so `.spiceinit`
applies:

```sh
ngspice -b tps62903-5v1-step.cir     # one case; edit the .param line; writes step.dat
JOBS=2 uv run run.py step903 loop903 check
JOBS=2 uv run run.py step136 loop136 # TI model, about 2-4 min per case
uv run run.py --json step903         # the same results as JSON
odapkit sim run .                    # the regression checks
```

`JOBS` sets how many ngspice processes run at once (default 2; keep it low on a shared
machine). Results go to `results/` (not committed); a case already in `results/` is not
run again. A generic case takes a few seconds; a TI-model case takes 2–4 minutes.

## Results (2026-10-22, ngspice 47)

The TPS62903 is simulated with the open generic model, calibrated against TI's TPS62136 model (TI's TPS62903 models do not run in ngspice); in that calibration the generic model is 10–12° optimistic on phase margin and overstates the dip at low headroom. Inductor peaks use L −20 % and VSYS 9.9 V (charger OVP ceiling).

**TPS62903, HAT_5V / USB-C source, 5.1 V at 1.6 A (BOM line 91, generic model): margins, load steps and ripple pass; phase margin ≥ 45° is not demonstrated at low VSYS; one value to change.**

1. **BRD-049 current margins hold.** Load 1.6 A = 53 % of 3 A. Inductor peak 2.22 A at 9.9 V with L −20 % = **55 % of the 4.0 A minimum high-side limit**, 25 % of the XGL4020-102MEC 8.8 A Isat (30 % drop). Simulated step peak 2.3–2.8 A (≤ 70 %). With both eFuses at their 1.66 A ceilings the limit (4.0–5.5 A, ≤ 5.8 A with the 50 ns overshoot of Eq. 2) bounds the fault below Isat.
2. **Load step 0.1 → 1.6 A with ≈ 10 µF effective (the BOM's single 22 µF):** dip **68 mV at VSYS 8.8 V, 143 mV at 6.6 V, 167 mV at 6.0 V**; overshoot 86–123 mV; settling 9 µs (up) and 20–23 µs (down). Lowest output 4.93 V; with the −1.25 % VSET tolerance 4.87 V, above the 4.75 V USB VBUS minimum. Highest, with the model's overshoot error (up to 30 % low) and a power-save offset like the TPS62136's (+1.6 %, est.): about 5.42 V, below 5.5 V. In the calibration the generic model overstates the dip at low headroom, so the dips are upper bounds.
3. **Ripple:** 5.5–6.9 mVpp in PWM at 1.6 A; **15–23 mVpp in power save** at 0.1 A.
4. **Loop:** the generic model gives crossover 178–197 kHz and phase margin 50–63° with 10 µF effective. Against TI's TPS62136 model the same generic model is **10–12° optimistic**. Corrected, the TPS62903 margin is **≈ 38–40° at VSYS 6.0 V** and ≈ 51–53° at 8.8 V (10 µF), and lower with more capacitance (≈ 34–36° / 43–45° at 20 µF). **Phase margin ≥ 45° is therefore not shown at low VSYS.** The part is internally compensated: the only lever is the L–C pair, and TI lists 1 µH with 10–100 µF nominal as stable (SLVSES3A Table 8-3). Closure needs TI's SIMPLIS model (SLVMDP3, does not run in ngspice) or a bench Bode plot.
5. **Recommended: keep one 22 µF, but a part with ≥ 12 µF effective at 5.1 V** (est. a 1206, 25 V X7R). A 22 µF 0805 sits at the 10 µF effective minimum of SLVSES3A §6.3 at 5.1 V bias (est.). Two 22 µF (≈ 20 µF) cut the dip to 50–128 mV and halve the PWM ripple (3.0–3.4 mVpp), but lower the model's phase margin by 4–8°; keep that option until the bench Bode plot.

**TPS62136, VSYS_LV 3.8 V pre-regulator at 2.0 A peak (BOM line 113, TI's model): pass; one BOM figure to correct.**

1. **Load step 0.1 → 2.0 A (TI model, 30 µF effective):** in auto PFM/PWM (the BOM setting) VSYS_LV stays within **3.788–3.883 V** (light-load level 3.855–3.861 V, +1.6 %; dip to 3.79 V; back to the light-load level plus 10–22 mV); settling 9–20 µs. In forced PWM: dip 42 mV, overshoot 57–58 mV, settling 8 µs. That band is inside the input range of every part on VSYS_LV (the MCLK LDO needs ≥ 3.4 V; the RK860-0 sits inside the 3.5–4.4 V the T1 uses for it).
2. **Loop (TI model):** crossover **232–234 kHz, phase margin 49° at VSYS 6.0 V and 54° at 8.8 V** (1.6 A, 30 µF effective). **Pass** (≥ 45°). The internal 15 pF feed-forward with 442 kΩ / 100 kΩ puts its zero at 24 kHz and its pole at 130 kHz; no external capacitor is needed.
3. **The BOM's inductor ripple figure (line 114) is low by 2.5×.** SLVSDV2 Eq. 10 uses 100 ns; the on-time of Eq. 1 (250 ns × VIN / (VIN − VOUT)) gives ΔIL = 250 ns × VIN / L, and TI's model agrees. Peak at 2.0 A, 9.9 V, L −20 %: **3.03 A, not 2.41 A** = 63 % of the 4.8 A minimum limit and 40 % of the 7.5 A Isat (30 % drop). Still compliant.
4. **Power save covers most of playback.** The PFM boundary is ΔIL / 2 = 0.5–0.8 A, so VSYS_LV runs in power save at typical playback loads, with 15–22 mVpp ripple and a load-dependent burst frequency. VSYS_LV reaches the DAC_VP switch (line 50) unregulated; the CS43198 VP rejection of that ripple is **UNVERIFIED** and is a bench item (forced PWM, MODE high, is the fallback at a few mA of quiescent cost).
5. **Start-up:** VSYS_LV is up ≤ 0.45 ms after VSYS (200–300 µs delay + 150 µs ramp, SS/TR open) and vcc3v3_sys ≤ 1.25 ms later (TPS62826). Both are always on, so they come up at battery attach, long before any PWRON press: they do not enter the MaskROM timing.
