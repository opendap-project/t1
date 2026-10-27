# ADR 0006: Pin plan decisions

- **Status:** Accepted
- **Date:** 2026-10-22

## Context

The RK3566 pin allocation (pin plan v0, now [pinout v1](../specs/pinout-v1.md)) left open questions. Relevant rules: display flexibility without board changes (BRD-048, T1-036), no unusual switches or tricks, standard Linux software (T1-011), the main/power button is also the boot-mode button (BRD-035).

## Decision

- **No parallel RGB from the board:** the RK3566 has no balls for it. Faceplates with RGB or LVDS panels use a **DSI bridge on the faceplate**; the board exposes MIPI DSI 4-lane, so it never changes for a display.
- **Bluetooth audio over HCI**, not PCM: no I2S instance is left, and HCI audio is the standard Linux path (BlueZ, PipeWire).
- **The HAT gets camera input (CSI) only**, no DSI output: DSI goes to the faceplate.
- **MaskROM from the power button:** a small circuit on the board lets the main/power button force the boot mode at power-on; its exact design is part of the schematic.
- **The faceplate connector keeps spare contacts** (at least about 10 %), in the same connector family, so the faceplate interface can evolve (BRD-048); the exact part is chosen with pinout v1.
