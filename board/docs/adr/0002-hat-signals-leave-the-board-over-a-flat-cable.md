# ADR 0002: HAT signals leave the board over a flat cable

- **Status:** Accepted
- **Date:** 2026-10-21
- **Amended (2026-10-25):** the HAT interface is one USB port (hat-standard ADR 0006, RFC 0014); the flat cable carries it. See [Amendment 2026-10-25](#amendment-2026-10-25).

## Context

The HAT interface sits on a separate device-side piece defined by the HAT Case Standard.

## Decision

Everything the HAT interface needs leaves the board over a flat cable to that device-side piece.

## Amendment 2026-10-25

HATs are USB only (hat-standard [ADR 0006](https://github.com/opendap-project/hats/blob/main/standard/docs/adr/0006-hats-are-usb-only.md), [RFC 0014](https://github.com/opendap-project/rfcs/blob/main/text/0014-hat-interface-v2-usb-only.md)). What leaves the board over the flat cable is now one USB port: `SSTX±`, `SSRX±`, `D±`, `CC`, `VBUS` and `GND` (hat-standard interface v2). The decision stands: the HAT port leaves the board over a flat cable. Which part the cable reaches on the HAT case side, a pogo field on the device-side piece or a USB-C receptacle, is still open; the board's connector, the pogo part and the cable (BOM v1 lines 66, 67, 102) follow that choice.

Later the same day the choice was made ([RFC 0015](https://github.com/opendap-project/rfcs/blob/main/text/0015-hat-connector-pogo-field-and-usb-c-port-hat.md)): the cable reaches the pogo field on the device-side piece, one DF40C-50 per end (BOM v1.14 lines 66, 67, 102; [HAT flat cable](../specs/hat-flat-cable.md) spec v1).
