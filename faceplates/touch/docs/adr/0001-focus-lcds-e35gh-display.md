# ADR 0001: Focus LCDs E35GH-I-MW800-CB display

- **Status:** Accepted
- **Date:** 2026-10-22

## Context

The touch faceplate display must fit the product (T1-030), keep a 2:3-preferred portrait ratio (FPT-020), be commercially available (T1-028, T1-029) and preferably have a mainline driver (FPT-018). No commercially available touch display with an allowed ratio fits the ideal 54 mm body.

## Decision

- Use the **Focus LCDs E35GH-I-MW800-CB**: 3.5" IPS, 320 × 480 (2:3), 800 nit, 1-lane MIPI DSI, Goodix GT911 touch, 54.46 × 82.94 × 5.5 mm. Mainline Linux already has its panel compatible; Debian does not enable it, so it ships through DKMS.
- Chosen over the Displaytech DT035CTFT-IPS-SHB-PTS because it has a driver. The maker lists it as "Recommended for New Designs" (checked 2026-10-22).
- The Displaytech DT035CTFT-IPS-SHB-PTS stays as the second source.

## Consequences

The body grows from the ideal toward the maximum, to about 59.5 × 91.5 mm (ratio about 1.54), within T1-031 and T1-033.

Note (2026-10-24): [t1 ADR 0003](../../../../product/docs/adr/0003-tentative-body-size.md) (Accepted) later set the tentative body at 59.5 × 94.3 × 24 mm (credit-card proportions at this width), taller than the 91.5 mm the display alone needs; that ADR is the current body size.
