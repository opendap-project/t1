# ADR 0014: Two-cell (2S) battery with a made-to-order pack

- **Status:** Accepted. Supersedes [ADR 0011](0011-battery-path-rated-for-the-full-output-budget.md). Item 1 (battery connector) and the lead-and-plug criterion of item 2 amended by [ADR 0020](0020-battery-connected-through-contacts.md) (2026-10-24): the pack connects through contacts.
- **Date:** 2026-10-22

## Context

BRD-050 (must) asks the battery path to carry the full HAT and USB-C output budget on battery; BRD-049 (must) asks for margin and protection everywhere. T1-038 (must) allows no made-to-order part except the display cover glass.

[ADR 0011](0011-battery-path-rated-for-the-full-output-budget.md) set acceptance criteria for a 1S pack (≥ 6 A continuous) and kept the Adafruit 328 as an interim pack. No off-the-shelf pack meets them, in 1S or in 2S. With the interim pack, BRD-050 is not met, and the full headphone output of [ADR 0012](0012-headphone-output-stage.md) is reachable only under a Blackbird OS output ceiling. The audio experience is the product's first priority, and the T1 uses the hardware fully, with limits only for safety: a permanent ceiling caused by the battery is not acceptable.

Both remaining branches need a T1-038 exception for the pack: a made-to-order 1S pack needs a ≥ 6 A high-rate cell that no maker lists in this size, while a 2S pack carries the full budget at about half the 1S current (2.4–3.2 A) from two catalog pouch cells, with every board part available through authorized channels. The cost of 2S is one more conversion stage (about 9–12 % less core-session autonomy at the same pack energy, est.; still above the T1-039 warning) and a charger whose device ID is not yet in mainline Linux.

## Decision

1. **The T1 runs on a two-cell series (2S) Li-ion pack.** The board changes as follows:
   - **Charger:** TI BQ25798 (1–4S buck-boost, NVDC power path, 6 A continuous battery discharge), replacing the BQ25895. VSYS is 6.0–8.8 V.
   - **Pre-regulator:** TI TPS62136, VSYS → **3.8 V (VSYS_LV)**, feeding every part the 1S tree fed from VSYS (RK809-5, RK860-0, TPS62826, TPS65131, TPS61169, LP5521, MAX98357A, TPS22919, TPS62840, TPS7A2031) unchanged.
   - **5.1 V HAT_5V and USB-C source:** a TI TPS62903 buck from VSYS, replacing the TPS61089 boost. **HAT_3V3:** a second TPS62903, replacing the TLV62569 (one part number for both, at 55 % and 33 % of its 3 A rating).
   - **Gauge:** TI BQ28Z610-R1 as the 2S gauge, replacing the MAX17055. Primary protection and cell balancing are in the pack (item 2).
   - **Battery path:** sized for the worst continuous case, the full HAT and USB-C budget with full-scale balanced headphone output and the system at 3 W at once: about **3.2 A at VSYS 6.6 V** (BOM v1.5 §7). 5 A board fuse in series with BAT+ (64 %); Molex Micro-Fit 3.0 4-pin battery connector (P+, P−, mid-cell tap, NTC; 64 % per contact). The connector also prevents fitting a 1S pack.
2. **The pack is a T1-038 exception, as the cover glass is.** It is a made-to-order 2S1P pack built from two catalog Li-ion pouch cells, and is adopted only if it meets all of:
   - continuous discharge rating ≥ 4.0 A (3.2 A at 80 %);
   - PCM in the pack with over-charge, over-discharge, over-current (trip 4.0–5.0 A) and short-circuit protection, and cell balancing;
   - lead and Micro-Fit plug rated ≥ 4.6 A per pole (3.2 A at 70 %);
   - the largest energy that fits the battery pocket of [t1 ADR 0003](https://github.com/opendap-project/t1/blob/main/docs/adr/0003-tentative-body-size.md); UN 38.3 report, and IEC 62133-2 for the Commercial edition;
   - a pack specification that at least two independent makers can build, so the product never depends on one supplier;
   - cells of 4.2 V or LiHV chemistry ([ADR 0008](0008-battery-technology-ready-for-lihv.md) unchanged).
   An off-the-shelf pack that meets the same criteria replaces the made-to-order one if one appears.
3. **No output ceiling from the battery.** With a compliant pack, the full output budget is available on battery (BRD-050) and the ADR 0012 interim ceiling is removed. The only limits left are safety limits, documented and visible (BRD-049, T1-045).
4. **Bring-up** uses a bench supply or a protected 2S pack on the bench. The Adafruit 328 is no longer a T1 pack.
5. **Software:** the BQ25798 uses the mainline `bq257xx` driver: its register map matches the BQ25792 the driver supports, and the device-tree binding (`"ti,bq25798", "ti,bq25792"`) is already queued upstream. The BQ28Z610-R1 uses the mainline `bq27xxx_battery` driver. Debian builds neither `MFD_BQ257XX`/`CHARGER_BQ257XX` nor `BATTERY_BQ27XXX_I2C` for arm64, so Blackbird OS ships them through DKMS ([blackbird-os ADR 0007](https://github.com/opendap-project/blackbird/blob/main/os/docs/adr/0007-kernel-modules-through-dkms.md), OS-023) and asks Debian to enable them.
6. **Ship FET and watchdog:** the board fits the BQ25798's external ship FET (one N-FET, so a stored T1 does not drain its pack; the mainline driver already sets `SFET_PRESENT`). The charger watchdog stays disabled, as the mainline driver leaves it: Blackbird OS never programs charge settings above the pack's ratings, and the protections that matter for safety (pack PCM, charger thermal regulation and TS window, board fuse) work without the OS (BRD-049).

## Consequences

- BOM v1.5 and the power tree change as item 1 lists. BRD-050 is met once a compliant pack is fitted.
- T1-038 gains the battery pack as its second exception.
- Before the board freezes: confirm that at least two independent makers can build the pack specification; leave the charger's OTG output out of the device tree (the mainline regulator part does not handle the BQ2579x layout yet); program the gauge's cell, chemistry and protection configuration in production.
