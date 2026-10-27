# ADR 0005: Battery approach

- **Status:** Superseded by [ADR 0007](0007-off-the-shelf-battery.md)
- **Date:** 2026-10-22

## Context

The battery must be a standard commercial part of at least 2,000 mAh (T1 requirements), as large as fits (T1-035), certified and user-replaceable, and available (T1-028, T1-029). No off-the-shelf pack that fits has both IEC 62133-2 and UN 38.3 reports.

## Decision

- The board and case are designed around a **105060-class battery bay** (about 3,000–3,500 mAh), with a connector and an NTC on the board.
- **Commercial edition:** a certified 105060 pack (IEC 62133-2, UN 38.3, PCM, NTC, connector), from at least two independent makers; it is validated against its certificates.
- **Prototypes and DIY kit:** Adafruit 328 (2,500 mAh) first, Adafruit 2011 (2,000 mAh) as second source; they fit the same bay.
