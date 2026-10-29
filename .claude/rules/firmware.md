---
paths:
  - "firmware/**"
---

# Firmware

- All custom firmware is Rust. One folder per programmable chip, each a self-contained Rust project with its own target configuration.
- Which chips are programmable, and their targets, are not defined yet: do not assume.
- The SoC must keep direct access to every chip (BRD-004/BRD-005): firmware assists, it never sits in a data path.
