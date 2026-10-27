# ADR 0005: Faceplate supply classes and protection

- **Status:** Accepted
- **Date:** 2026-10-24
- **Basis:** BRD-049 (power safety first: margin below every rating, every rail protected)

## Context

The FH35C-51S is rated 0.2 A per contact, 0.14 A when all contacts carry current, and **30 V AC rms** (Hirose FH35C catalog p. 2, via the parts-lib sheet). The body's faceplate supplies, as drawn in board BOM v1.10 and power tree v0.4:

- FP_3V3 (two contacts), FP_1V8 and MIC_1V8 (one each) come from TPS22919 load switches, whose short-circuit limit is 30–900 mA on a hard short and about 3 A while the output is above the hard-short threshold (SLVSEN5B p. 5, via the parts-lib sheet). A faceplate fault can therefore push several times the contact rating through the connector.
- FP_VCI comes from RK809 LDO4, rated up to 400 mA in the DC table; its current limit is not in the parts-lib sheet (**UNVERIFIED**).
- BL_LEDA comes from a TPS61169 whose output over-voltage threshold is 36–39 V (SNVSA40B p. 5). After an open string the output capacitor stays at that voltage, on contact 46, above the connector's 30 V figure. Whether Hirose's AC rms rating also covers 39 V DC is not stated (**UNVERIFIED**).

## Decision

1. **Each faceplate rail has a class:** a continuous budget of about 70 % of the derated contact capacity (0.14 A per contact), and a fault ceiling at or below 100 % of the contact rating (the HAT standard's margin rule applied to the FH35C):

   | Rail | Contacts | Faceplate budget | Fault ceiling at the body |
   |---|---|---|---|
   | FP_3V3 | 2 | 200 mA | ≤ 0.4 A |
   | FP_1V8 | 1 | 100 mA | ≤ 0.2 A |
   | MIC_1V8 | 1 | 20 mA | ≤ 0.2 A |
   | FP_VCI | 1 | 100 mA | ≤ 0.2 A |
   | BL_LEDA / BL_LEDK | 1 + 1 | 60 mA (set by the body) | ≤ 0.2 A |

2. **The body limits current on every faceplate rail** to its fault ceiling. The TPS22919 does not meet it; the board owner chooses current-limited switches (and confirms or limits LDO4).
3. **BL_LEDA never exceeds 30 V, in any state, fault included,** until Hirose confirms a DC rating of at least 40 V in writing. The board meets it with a backlight driver whose maximum over-voltage threshold is at most 30 V. A faceplate's string forward voltage stays at or below **22 V** at its maximum current (provisional: the minimum threshold of the chosen driver less 3 V).
4. Every faceplate stays within its class and declares its real figures in its device description; Blackbird OS caps the backlight and status LED currents to what the description declares, a documented safety limit (T1-045).

## Consequences

- Board changes: current-limited faceplate switches; LDO4 limit confirmed or added; backlight driver over-voltage at most 30 V (the BOM alternate TPS61160 has a 26 V threshold per BOM line 51; its limits and land are **UNVERIFIED**).
- Backlight strings longer than about six white LEDs in series no longer fit without a faceplate-side change. Power tree §4.5's "up to about 10 series LEDs" no longer holds.
- If Hirose confirms the DC rating, item 3 can be relaxed by a later ADR; nothing else changes.
