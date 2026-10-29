# ADR 0002: Faceplate controls use HID over I2C

- **Status:** Accepted
- **Date:** 2026-10-21

## Context

Faceplate controls (buttons, switches, dials) must reach Blackbird OS as standardized binary commands, not raw signals, with a well-standardized core set that is not minimal and room for new commands (T1-023, T1-024). Software must prefer the most standard Linux option (T1-011), and faceplate identification should rely on the interface pinout rather than an EEPROM (T1-020).

## Decision

- Each faceplate exposes its controls as an **HID-over-I2C** device, read by the mainline `i2c-hid` driver. No OpenDAP kernel driver is needed.
- Commands are **usages from the USB-IF HID Usage Tables**. The core set is defined in the [faceplate interface](../specs/faceplate-interface.md#control-commands).
- New commands go in an **OpenDAP vendor-defined usage page**, read by Blackbird OS services through `hidraw`.
- The faceplate's HID descriptor (vendor ID, product ID, version) identifies the faceplate and its controls.

## Notes

- Note (2026-10-24): [ADR 0004](0004-faceplate-identity-and-hid-transport.md) (Accepted) sets the transport parameters, the vendor page (0xFF00) and the identity numbers. Because mainline `i2c-hid` does not pass `wVersionID` to userspace, the faceplate's hardware revision is also carried in a vendor identity report. The decision above is unchanged.
