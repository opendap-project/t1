# ADR 0013: Production variant and population options

- **Status:** Accepted
- **Date:** 2026-10-22

## Context

BRD-053 lets prototypes populate every option while production leaves optional parts unpopulated or fits same-footprint equivalents. Every BOM line outside the audio chain was classified as fitted in every variant, a population option, or a same-footprint substitute. Requirement priorities were revised the same day: BRD-014 (coprocessor), BRD-031 (ambient-noise microphone) and BRD-032 (IMU) are *should*.

## Decision

- **Never changed between variants:** the audio chain, the power-safety margins (BRD-049), mainline support and availability.
- **Memory:** 4 GB LPDDR4X in every variant; 2 GB only as a qualified supply fallback, never the default, because it risks responsiveness and long sessions (T1-046, T1-047, T1-056).
- **Storage (BRD-037):** 32 GB eMMC on prototypes. Production fits 16 GB or 32 GB on the same footprint; the other capacity is a population option. Music lives on microSD; the A/B system image and user data fit in 16 GB.
- ***Should* parts stay in production** (maintainers' decision, 2026-10-22): all four INA236 current monitors, the IMU, the ambient-noise microphone and the RP2354A coprocessor are fitted in every variant. They remain population options (BRD-053) and Blackbird OS still detects each part instead of assuming it (T1-045), so a future variant can leave one off without a respin.
- **Capacitor voltage ratings** on the non-audio buck outputs are set to the rail with BRD-049 margin, not to a blanket higher rating.
- **Not adopted:** the second-source display with a DSI-to-RGB bridge (the bridge has no authorized source and the panel drops to 16-bit colour), cheaper Wi-Fi modules without BT 5.4 or a confirmed mainline driver, and generic pogo pins that do not fit the HAT grid.
- **Both editions** (Commercial and DIY) use the same production population (T1-004).
- **Production sourcing** goes through authorized channels (franchised distributors or the makers), for traceability and part authenticity (BRD-049).

## Consequences

- The BOM marks every optional part with its variant (BRD-053), and the schematic gives each one safe defaults when unpopulated (pull-ups, straps, enables).
- The RP2354A stays fitted, so its wake lines can stay; moving them is needed only if a future variant leaves it off.
- Open, for the maintainers: whether the HAT device-side piece is fitted to every T1 (HCS-012) or is a fitted option.
