# ADR 0020: Battery connected through contacts

- **Status:** Accepted. Amends [ADR 0014](0014-two-cell-battery.md) item 1 (battery connector) and item 2 (lead and plug criterion).
- **Date:** 2026-10-24

## Context

ADR 0014 connects the made-to-order 2S pack through a lead and a 4-pin Molex Micro-Fit 3.0 connector (P+, P−, mid-cell tap, NTC), with the lead and plug rated ≥ 4.6 A per pole (3.2 A worst continuous at 70 %). The maintainers asked (2026-10-24) for a pack that connects through contacts (spring, blade or pad contacts) instead: for the right to repair, and because battery problems are a common failure of portable players, replacing the pack should not mean replacing the device, unplugging a cable or desoldering. T1-055 (user-replaceable with common tools and a standard part), T1-079 (published pack specification) and T1-080 (labels, commercially available tools) apply, and Regulation (EU) 2023/1542 Art. 11 from 18 February 2027.

Findings that decide (contact battery interfaces of camera packs, phones with user-replaceable packs, two-way radios, power tools and drones, and the applicable standards):

- Contact interfaces are the usual design for user-replaceable packs, sealed ones included (the gasket is on the cover). Their recorded failure is loss of contact pressure after drops, not the contact.
- A side-acting contact at the pocket end needs about 6.5 mm of length for ≥ 4.6 A per pole, against the 2.5 mm allowance: about 6 % of pack energy. A face-compression contact fits the existing 1.9–2.1 mm between the board and the pack's underside, with no loss of battery volume.
- KYOCERA AVX 70-9258-001-120-006 carries 6 A per contact, works at 1.6–2.8 mm, is gold over nickel, rated 2,500 cycles, and has multiple authorized sources (2026-10-24). Its contact force and resistance are in a product specification not yet obtained.
- At ≤ 8.8 V no sustained arc forms (gold's minimum arc voltage is 15 V). The BQ25798's ship FET is off when a pack is inserted into an unpowered T1 and turns on through a 100 nA charge pump: a soft start by construction.

## Decision

1. **The pack connects to the board through contacts: no cable, cable connector or solder joint between them.** The Micro-Fit 3.0 connector and the pack lead are removed.
2. **Arrangement: face compression.** Six KYOCERA AVX **70-9258-001-120-006** spring-finger contacts on the board, in a window of the pocket floor at the pocket's bottom end, press on recessed gold pads on the underside of the pack's terminal board. Order at 3.5 mm pitch: P+, P+, empty position, mid-cell tap, NTC, P−, P−. The pack drops into the pocket; the back cover's foam preloads it onto the contacts; the case, never the contacts, retains it.
3. **Margins.** Two contacts per power pole. Worst continuous 3.2 A: 2.0 A on the hotter contact (sharing factor 1.25, assumed until measured), **33 %** of 6 A; 5 A protective limit (PCM trip, fuse): 52 %. Pole rating counted at 9.6 A, which replaces ADR 0014's "lead and Micro-Fit plug rated ≥ 4.6 A per pole" with "contact interface rated ≥ 4.6 A per pole". Working height 2.1 mm nominal (1.5 mm component zone + 0.4 mm floor + 0.2 mm pad recess), ± 0.3 mm assumed: 1.8–2.4 mm inside 1.6–2.8 mm. End-of-life resistance budget ≤ 20 mΩ per contact (**UNVERIFIED** until measured): 80 mV and 0.26 W in total at 3.2 A.
4. **No Kelvin sense contacts.** Coulomb counting stays on the board's 3 mΩ sense resistor, outside the contacts; cell voltages read at most ≈ 40 mV low per cell at 3.2 A and zero at rest; cell protection is in the pack PCM. Stability of the contact resistance is qualified instead.
5. **Sequencing:** power pads recessed 0.2 mm, signal pads 0.4 mm, so power usually makes first and breaks last; every mating order stays safe on its own (PCB-P-17). The NTC opening stops charging in hardware.
6. **Insertion and protection on the board:** BATP gets the 100 Ω series resistor and 47 nF of TI's hot-plug recommendation (SLUSDV2C Figure 8-2 note 2); one TPD1E10B06 on each of the mid-cell tap and NTC contacts; a TVS footprint on P+ (standoff ≥ 9 V, clamp < 20 V), fitted only if the insertion and ESD measurements ask for it. The ship FET stays as in ADR 0014 item 6 and is the insertion soft start.
7. **Cover detect (should):** a board input that changes state when the back cover is lifted, so Blackbird OS powers down in order (the ADR 0017 item 3 sequence when no adapter is present) before the pack can be reached. It protects data, not safety: no safety function depends on it (T1-086).
8. **The pack specification** (ADR 0014 item 2, T1-079) replaces the lead and plug with a terminal board: the pad row of item 2, pads ≥ 4.0 × 2.5 mm in electrolytic hard gold ≥ 0.76 µm over nickel, recessed and walled so a flat metal object cannot bridge them, keyed and polarity-marked, ≥ 5 A per power pad; the PCM's short-circuit threshold and delay stated, and its behaviour under the insertion pulse (≈ 63 A peak for ≈ 2 µs, est.); UN 38.3 and IEC 62133-2 on the pack as shipped with exposed pads; a terminal cover or separating packaging for spares. Full list: [battery pack specification](../specs/battery-pack.md) §1.
9. **Qualification:** rows CB-01 to CB-12 with the T1 values of the [battery pack specification](../specs/battery-pack.md) §2. Before the board freezes, obtain KYOCERA AVX product specification 201-01-252 (force, resistance, rating basis). Bring-up uses a bench terminal board with the pack's pad layout, so prototype 1 runs through the same contacts.

## Consequences

BOM v1 line changes (applied in BOM v1):

- **Line 47:** Molex Micro-Fit 3.0 43650-0400 → **KYOCERA AVX 70-9258-001-120-006 × 6** (P+ × 2, P− × 2, mid-cell tap, NTC), in the pocket-floor window; Decided (this ADR); multiple authorized sources. Alternates: none on the same land; Mill-Max 0965 / 0990 pogo pins (four per pole, own land) to qualify. Pack-side mating parts (43645-0400 receptacle, 43030-0001 crimps) leave the pack specification. Remove "The keyed Micro-Fit plug cannot mate with a 1S JST-PH pack": keying is now the pack's terminal end and the pocket.
- **Line 46:** "4-pin Micro-Fit 3.0 lead" → "terminal board with recessed hard-gold pads (ADR 0020 item 8)"; acceptance "lead and plug ≥ 4.6 A per pole" → "contact interface ≥ 4.6 A per pole (ADR 0020 item 3)"; add the pack specification items of ADR 0020 item 8.
- **Lines 42 and 48:** "through the battery connector (line 47)" → "through the battery contacts (line 47)".
- **Line 104:** "between the battery connector and the BQ25798 BAT pins" → "between the battery contacts and the BQ25798 BAT pins".
- **Line 115 (BQ25798 passives):** BATP 100 Ω series and 47 nF to GND (item 6), if not already listed.
- **New line, Protection:** battery-contact ESD, TI TPD1E10B06DPYR × 2 (mid-cell tap, NTC), as line 36; plus a P+ TVS footprint, DNP, part to choose.
- **New line, Power, should:** cover detect: pull-up, one TPD1E10B06DPYR, a board-edge contact pad; GPIO chosen in the pinout.
- **§7 and §8:** the 2.5 mm pocket-length allowance for the lead exit is free for the pack or the case; contact force × 6 is an input to the back cover's foam preload; the pocket floor needs the contact window with an insulating liner.

Elsewhere:

- **PCB design constraints:** PCB-L-04 to PCB-L-10 (applied in §6.1); wording changes to PCB-L-02, PCB-P-01, PCB-P-17.
- **Case (input only):** window in the metal pocket floor with an insulated edge, keying of the pocket's terminal end, foam preload above the contact force, the cover-detect actuator, and the tolerance stack that holds 2.1 ± 0.3 mm.
- **t1:** product requirement T1-088 (contact-based, user-replaceable battery connection).
- **parts-lib:** sheet and manifest entries for 70-9258-001-120-006.
- ADR 0014's other items (2S pack, PCM, fuse, gauge, ship FET, two pack makers) are unchanged.
