# ADR 0004: Faceplate identity and HID transport parameters

- **Status:** Accepted
- **Date:** 2026-10-24
- **Basis:** the product rules (most standard Linux option, T1-011; identification through the pinout, T1-020; software never limited by one hardware, SYS-040)

## Context

[ADR 0002](0002-faceplate-controls-use-hid-over-i2c.md) chose HID over I2C for faceplate controls and the HID descriptor's vendor ID, product ID and version for identification. The [faceplate interface](../specs/faceplate-interface.md) left open the I2C address, the HID descriptor register, the report layout, the vendor usage page and where the identity numbers come from. Three facts, checked on 2026-10-24 against mainline Linux (torvalds/linux `master`):

- `i2c-hid` copies `bcdVersion` (always 0x0100), not `wVersionID`, into the HID device's version (`drivers/hid/i2c-hid/i2c-hid-core.c`), so the faceplate's own version is not visible to userspace through the kernel.
- `hid-input` ignores usages on page 0xFF00 (`HID_UP_MSVENDOR`), but maps input and output usages on any other unknown vendor page to `BTN_MISC`, `ABS_MISC`, `REL_MISC` or `LED_MISC` (`drivers/hid/hid-input.c`).
- A faceplate without physical controls (the touch faceplate) has no HID device today, so it could not be identified at all.

OpenDAP has no USB vendor ID. [pid.codes](https://pid.codes/1209/) allocates product IDs under VID 0x1209 to projects with published, openly licensed hardware and firmware; its prerequisites mention a device with a USB interface, and its test PIDs 0x0001–0x0010 must not be used on any device that is redistributed, sold or manufactured.

## Decision

1. **Every faceplate carries the identity device**, an HID-over-I2C controller at **I2C address 0x2C** with its **HID descriptor at register 0x0001**, on the faceplate I2C (contacts 17, 18), interrupt on `HID_INT#` (contact 28), powered from FP_3V3 only. A faceplate without controls still presents it, with the identity report alone.
2. **No reset contact.** Reset is the HID-over-I2C RESET command; a hard reset is a power cycle of FP_3V3.
3. **Vendor-defined usage page 0xFF00.** Mainline `hid-input` ignores it, so OpenDAP commands never become stray input events and reach Blackbird OS only through `hidraw`. The page's meaning is valid only together with an OpenDAP faceplate identity.
4. **Identity numbers:** `wVendorID` 0x1209 with one pid.codes PID per faceplate model; `wVersionID` is the faceplate's hardware revision. A mandatory **identity feature report** (report ID 0x10, page 0xFF00) repeats the hardware revision and adds the interface revision and firmware version, so userspace can read them through `hidraw`.
5. **Test PIDs only in the lab:** pid.codes test PIDs are allowed up to quality level Q1 (RFC 0010); a faceplate built at Q2 or above carries a granted PID.
6. **The identity node belongs to the body**, not to the faceplate's overlay: the board devicetree (layer H1) carries the `hid-over-i2c` node at 0x2C, because identification must work before the faceplate's description is known.

## Consequences

- The touch faceplate gains a small controller and its firmware (faceplate-touch, board BOM faceplate lines).
- Requesting the PIDs is an action under the project's name: the maintainers submit it. If pid.codes declines a non-USB use, the fallbacks are a USB-IF vendor ID or a microcontroller vendor's PID programme; both are maintainers' calls.
- Address 0x2C is reserved on the faceplate bus for every faceplate.
