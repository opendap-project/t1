# Flat-cable impedance: 2D field solver

The question: which trace geometry gives each pair class its target impedance on the fab's standard flexible-circuit stack-ups, what changes it (dielectric constant, width tolerance, an EMI shielding film), how much the conductors lose, and how wide the power conductors must be? It serves two specifications:

- the board's [HAT flat-cable specification](../../docs/specs/hat-flat-cable.md) (BRD-013);
- faceplate-touch's [faceplate flex specification](../../../faceplates/touch/docs/specs/faceplate-flex.md).

`odapkit stackup` (toolkit-hardware) landed on 2026-10-24 while this study was written; the specifications take their impedance figures from it (`hardware/hat-flat-cable/stackup-v0.toml`, faceplate-touch `hardware/faceplate-flex/stackup-v0.toml`). This study cross-checks them and adds what `odapkit stackup` does not compute: conductor loss, coupling between lines, the effect of an EMI shielding film, and power-conductor sizing.

## Method

- 2D electrostatic finite differences on a uniform square grid (1 µm for the HAT cable, 1.5 µm for the faceplate flex), permittivity per cell, zero-flux outer boundaries unless a ground plane closes them. Capacitance per unit length from the field energy.
- Odd and even mode impedances from the capacitance with the dielectrics and in vacuum; Zdiff = 2 × Zodd.
- Conductor loss by Wheeler's incremental-inductance rule (every conductor surface receded by one grid step), smooth copper. Dielectric loss from the effective permittivity and an assumed loss tangent, printed as a range because the fab publishes none.
- Power conductors by the IPC-2221B design equation, at a 10 °C rise.
- Validation, printed first: symmetric stripline against the Wheeler/Cohn closed form, microstrip against Hammerstad; both within 1 %.

## Inputs and their sources

| Input | Value | Source |
|---|---|---|
| HAT cable stack-up | The fab standard 4-layer FPC, 0.268 mm: coverlay 12.5 µm PI + 15 µm adhesive; L1 18 µm (24 µm finished); 13 adhesive / 25 PI / 13 bonding sheet; L2 12 µm; 13 / 25 / 13; L3 12 µm; 13 / 25 / 13; L4 18 µm (24 finished); coverlay | The fab, *Stack-up for FPC*, <https://www.pcbway.com/pcb_prototype/Stack_up_for_FPC.html>, fetched 2026-10-24 |
| Faceplate flex stack-up | The fab standard 2-layer FPC, 0.156 mm: coverlay 12.5 PI + 15 adhesive; L1 18 µm (24 finished); 20 adhesive / 25 PI / 20 adhesive; L2 18 µm (24 finished); coverlay | Same page |
| Comparison stack-up | The fab standard 4-layer FPC, 0.204 mm (25 PI + 13 bonding sheet between L1 and L2) | Same page |
| Dielectric constant | PI 3.3 (adhesiveless), 3.5 with adhesive; adhesive and bonding sheet not published: 3.5 assumed, 3.3 and 3.6 printed as sensitivity | Same page |
| Copper resistivity | 1.72 × 10⁻⁸ Ω·m at 20 °C | Annealed copper |

## Run

```sh
uv run flex_impedance.py
```

Output goes to the terminal and to `results/flex-impedance.txt` (not committed). About one minute on a laptop.

## Results (2026-10-25)

The HAT cable rows follow hat-standard interface v2 (one USB port; RFC 0014, RFC 0015): the 100 Ω extension, 50 Ω I2S and `HAT_3V3` cases of 2026-10-24 are removed from the script.

| Line class | Layer and references | Geometry | Result |
|---|---|---|---|
| USB 3 and USB 2, 90 Ω (the HAT port, interface v2) | HAT cable L2; L1 above (51 µm), L4 below (114 µm, L3 voided) | w 70 µm, gap 100 µm | 89.9 Ω differential, 25.4 Ω common; 1.34 dB per 100 mm conductor loss at 2.5 GHz; −69 dB backward coupling at 0.35 mm |
| HAT cable `VBUS` | L3, 12 µm | IPC-2221B, 10 °C at 4.5 A | ≥ 18.15 mm; 102 mV round trip at 3.0 A over 100 mm with both DF40C-50 pairs at their maximum contact resistance |
| Faceplate DSI | Faceplate flex L1 over L2 (65 µm), coverlay | w 85 µm, gap 150 µm | 99.9 Ω |

Against `odapkit stackup` (finite elements, trapezoidal etch, conformal coverlay): the HAT stripline agrees within 1 Ω at the same mean width (89.9 Ω at 72.5 µm drawn). The faceplate microstrip differs by about 3 Ω: this study fills the gaps between L1 traces with coverlay adhesive, `odapkit stackup` models a conformal coverlay, so it needs 91 µm (mean) where this study needs 85 µm; the pressed coverlay lies between the two, and the fab's coupon settles it.

Sensitivity, coupling, the EMI-film comparison and the power sizing are in the script's output; the specifications quote them.

## Limits

- 2D quasi-static: no connector, via, bend or pad transition is modelled. Those are what the signal-integrity coupon measures (hat-standard ADR 0004).
- Lamination thicknesses are the fab's nominal figures; the bonding sheet's thickness after pressing around L2 is assumed equal to the published 13 µm.
- Dielectric loss tangent is not published by the fab (**UNVERIFIED**); the printed range (0.005–0.02) is an assumption.
