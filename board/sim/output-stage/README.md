# Headphone output stage: ngspice simulation

The question: does the ADR 0012 output stage hold its BRD-049 margins? The study checks
the TPS65131 ±7 V pre-rails under the worst-case output load, current sharing between
the paralleled OPA1622 halves, and the LT3045 / LT3094 headroom; then the replacement
−7 V converter (LMR33630C inverting buck-boost) and the paired-LDO current limits. Results are
below.

## Files

| File | What it is |
|---|---|
| `tps65131-switch-model.cir` | Switch-level TPS65131 model (subcircuits) built from SLVS493E parameters. Not a TI model: TI publishes none. |
| `tps65131-dc-load.cir` | Both pre-rails at one DC load point; prints the peak switch current and % of the 1.8 A minimum limit. |
| `tps65131-audio-load.cir` | Both pre-rails under a full-wave rectified sine load (full-scale sine, both channels). |
| `lmr33630-ibb.cir` | −7 V pre-rail from VSYS with an LMR33630C as an inverting buck-boost (follow-up), TI transient model. |
| `opa1622-model-check.cir` | TI OPA1622 model against SBOS727B Table 2 (±5 V, 16 and 32 Ω). |
| `opa1622-paralleled-halves.cir` | One balanced channel: two legs, each two paralleled halves with 1.0 Ω ballast, worst-case offset and resistor spread. |
| `sweep.py` | Runs the TPS65131 sweeps into `results/*.csv` (standard library only). |
| `.spiceinit` | Sets ngspice's PSpice compatibility mode, needed by the TI OPA1622 and LMR33630C models. |

## Vendor models (not in this repository)

Two netlists need TI models, which are TI copyright with all rights reserved, so they
are not redistributed here. `odapkit sim fetch` downloads both through the libs parts manifest
(`kind = "spice"`; the links serve SBOM958D and SNVMBG5A without login), checks the hashes in
`checks.toml` and puts them in `models/` (ignored by git); or place them there by hand:

| Netlist | Model | File to place in `models/` | Copy used on 2026-10-22 (sha256 of the zip) |
|---|---|---|---|
| `opa1622-*.cir` | [SBOM958](https://www.ti.com/lit/zip/SBOM958), OPA1622 PSpice model, Rev. D | `OPA1622.LIB` | `1bafa50b657ea2ece0c1d3e1ab7684556093d824a7d749aaaf07a933b81e49b8` |
| `lmr33630-ibb.cir` | [SNVMBG5](https://www.ti.com/lit/zip/SNVMBG5), LMR33630C unencrypted inverting and non-inverting transient model, Rev. A | `LMR33630C_TRANS.lib` | `bf3d8f3b2d33a7e957147972194555b7883da88efde2ba4275be0a23c69bc2b7` |

No vendor model is needed for the TPS65131 netlists. TI lists no TPS65131 transient
model, and the LT3045 / LT3094 figures come from their datasheets (LTspice models are
not used).

## Run

Tools: ngspice 47 or later with XSPICE code models (the Homebrew build has them), and
Python 3.10+ through `uv`. Run from this folder, so `.spiceinit` and the relative
includes resolve:

```sh
ngspice -b tps65131-dc-load.cir          # one point (edit the .param lines)
ngspice -b tps65131-audio-load.cir
ngspice -b opa1622-model-check.cir
ngspice -b opa1622-paralleled-halves.cir
ngspice -b lmr33630-ibb.cir              # 15-25 min for 5 ms
uv run sweep.py margin                   # also: ceiling, calibration
```

`JOBS=n` sets how many ngspice runs `sweep.py` starts at once (default 2). A DC point
takes about 4 s; the margin sweep is 84 points.

## Results (2026-10-22, ngspice 47)

1. **The TPS65131 inverter passes the 80 % rule only for the average load the ADR used, not for the load it actually switches.**
   - At its new fixed input (3.8 V, band 3.7–3.9 V) and 275 mA DC per rail, the inverter peaks at **1.11 A typical / 1.24 A worst stack = 61 % / 69 %** of the 1.8 A minimum limit. Eq. 4 of SLVS493E gives 1.22 A (68 %). This part of ADR 0012 holds.
   - But a full-scale sine is not a DC load. Each rail supplies a full-wave rectified current: 275 mA is its average; its **peak is 433 mA** (2 legs × 200 mA + quiescent, ADR 0012 numbers). The 10 µF output capacitors cannot bridge an audio half-cycle, so the converter follows the peak. The switch current limit acts cycle by cycle, on that peak.
   - At 433 mA the inverter needs **1.82 A (101 %) typical** at 3.8 V and cannot regulate at all in the worst stack. Audio-rate runs confirm it: **1.83 A at 100 Hz, 1.89 A at 1 kHz** (typical). Scaling TI's own typical curve (Figure 6-4) gives about 1.55 A (86 %, est.). **Fail** on every basis.
   - The **boost passes**: 56–65 % at 433 mA, 69–78 % even at 520 mA.
   - On the interim 1S pack (reference only), the worst stack cannot hold −7 V at 275 mA at VIN 3.0 V; typical is 75 %.
2. **The LT3045 / LT3094 current limit (≈ 401 mA programmed) is below the peak the amplifiers ask for.** By ADR 0012's own figures the LDO output peaks at 421 mA; by the TI OPA1622 model at about 510 mA (both channels, balanced 32 Ω, DAC full scale). A full-scale balanced 32 Ω sine on both channels therefore clips at the LDO limit, whatever the TPS65131 does. The 640 mW expectation of ADR 0012 cannot be met with the current RILIM.
3. **Current sharing works.** With the worst-case spread (±500 µV offset, 0.1 % gain resistors and 1 % ballast in the worst direction) at DAC full scale into balanced 32 Ω:
   - per-half peak currents **128 mA and 112 mA** (53.3 % / 46.7 %); largest instantaneous difference 25 mA;
   - DC circulation **1.3 mA** per half (BOM estimate: 1.3 mA);
   - dissipation **0.277 W and 0.245 W** per half, **0.52 W per package (+25 °C at θJA 47.6 °C/W)**;
   - no overshoot on a step into 400 pF or 10 nF per leg (model).
   The 1.0 Ω ballast value is adequate. The TI model is about 15 % optimistic on output current against SBOS727B Table 2 at 16 Ω.
4. **The LDOs keep their headroom in typical conditions, and run out of it in the tolerance corner at the signal peak.**
   - Typical headroom is 0.94 V, 0.78–0.86 V at the signal peak, against ≈ 0.18–0.22 V typical dropout.
   - Worst corner: 0.60 V DC (pre-rail −3 %, LDO output +2 %), and 0.40 V at the signal peak on the negative rail, against a full-range maximum dropout of ≈ 0.38 V at 400 mA. That is at the edge.
   - Dissipation: 0.32 W typical, 0.41 W at maximum headroom, per LDO at 275 mA average (+11 to +14 °C).
   - Rejection of the 1.25–1.5 MHz ripple: ≈ 70 dB (LT3045) and ≈ 67 dB (LT3094) at 1 V headroom, from curves G45 / G47. The simulated 18–33 mVpp pre-rail ripple becomes ≈ 10–15 µVpp, out of band.
5. **Smallest compliant fix (first pass).** No inductor or input-voltage change brings the inverter under 80 % at the 433 mA peak: a low-DCR inductor gains 3–7 points, and VIN 5.0 V still gives 80–90 %. Two ways were left: (a) a software output ceiling, ≈ 310–400 mW per channel balanced 32 Ω instead of 640 mW, or (b) a new negative pre-rail converter. The design takes (b): a software cap is not acceptable on the audio path (ADR 0012).
6. **Follow-up: make −7 V with a TI LMR33630C as an inverting buck-boost from VSYS, and pair the LDOs.**
   - **Converter:** LMR33630C, 2.1 MHz, VQFN-HR (LMR33630CRNXR). TI documents it in this topology: SNVA856B uses it as the worked example, and TI publishes an inverting transient model, SNVMBG5. Inductor: Coilcraft XGL4020-222ME (2.2 µH), the same family and land as the BOM's XGL4020-102ME. Output: 100 kΩ / 16.5 kΩ → −7.06 V.
   - **Simulated with TI's model** at VSYS 6.0 V, the worst case for current:
     - 433 mA rectified-sine peak at 1 kHz: inductor peak **1.80 A = 47 %** of the 3.85 A minimum high-side limit;
     - LDO current-limit case, 0.78 A DC: peak **2.13 A = 55 %**, valley 1.39 A = 48 % of the 2.9 A minimum valley limit.
   - **Voltage stress:** VIN to the IC ground is VSYS + |VOUT| ≤ 9.9 + 7.24 = 17.1 V, **48 % of the 36 V recommended maximum** (45 % of the 38 V absolute maximum).
   - **Ripple and start-up:** 6 mVpp ripple at 0.78 A; 0.11 V dip at the load step; no start-up overshoot beyond 0.1 %.
   - **The TPS65131 keeps only its boost (+7 V).** Its inverter is disabled: ENN and PSN to GND, inductor, diode and output capacitors not fitted.
   - **LDOs:** one 500 mA LT3045 / LT3094 cannot pass the ≈ 0.46 A design peak with margin while its limit stays within its 500 mA rating. Both ADI datasheets describe direct paralleling. **Two LT3045 and two LT3094**, SET pins tied (RSET 2 × 60.4 kΩ, CSET 2 × 0.47 µF, same 65 ms ramp), 20 mΩ trace ballast, RILIM **523 Ω** (LT3045) and **13.0 kΩ** (LT3094). Result: ±516–646 mA per rail, **+13 %** over the 457 mA design peak (+23 % over ADR 0012's 421 mA). The bound is the TPS65131 boost, at ≈ 99 % of 1.8 A worst stack (≈ 90 % typical) when the positive pair sits at its maximum limit.
   - **Pre-rails stay at ±7.0 V:** worst-corner headroom at the signal peak is 0.50 V (positive) and 0.65 V (negative), against ≤ 0.35 V maximum dropout at the per-LDO current. The −7.3 V option is not needed.
