# ADR 0018: Antennas for the Type 2EL module

- **Status:** Accepted
- **Date:** 2026-10-24

## Context

BOM line 57 fits two Molex 146187-0050 antennas, which are on Japan's list of the Murata Type 2EL certification but not on the FCC or ISED lists, and the module's FCC and ISED grants are for mobile use only, while the T1 is handheld, so a host-level RF exposure (SAR) assessment applies (BRD-025; PCB-R-04, PCB-R-05, PCB-R-07).

Findings (Murata certification report CER-0248, the FCC, ISED and Japan antenna lists, Molex drawings, 2026-10-24):

- Four external antennas are on the FCC, ISED and Japan lists: Molex 146153, Molex 219611, Unictron WT32D1-KX and Inventek W24P-U (2.4 GHz only). Only the 146153 and 219611 cover both bands and have authorized sources. Murata's trace antenna needs 20 mm of clearance and is out.
- The Molex 146153-0050 (34.9 × 9.0 × 0.1 mm flex, U.FL, 3.2 / 4.25 dBi registered) has multiple authorized sources.
- In the 59.5 × 94.3 × 25.0 mm body the top band is 7.0 mm deep. The 146153 fits on the inside of the top wall (56.3 × 14.2 mm), 7.0 mm from the battery; the 219611 (15.4 mm tall) does not, and no second antenna fits with a provisional 5 mm keep-out to metal.
- Molex's "-0050" is its 50 mm length class (43.3 mm of bare cable is drawn); the 146187-0050's cable is most likely not short of Japan's "50 mm or more" (**UNVERIFIED** until Murata confirms).
- SAR cannot be avoided by placement: at the T1's separations (below 5 mm) the FCC exemption threshold is 2.74 mW at 2.45 GHz and 1.44 mW at 5.5 GHz and RSS-102's 3 mW and 1 mW, against up to 100 mW (2.4 GHz) and 63 mW (5 GHz) conducted from the module under FCC.

## Decision

1. **Antenna: Molex 146153-0050**, one per T1, on ANT0, mounted on the inside of the top wall with its long axis along the width and away from the microSD corner. It is the prototype antenna (Q1, by availability and fit) and the production antenna of every certified variant (item 3), so prototype measurements carry over to the products.
2. **Configuration: Murata's shared antenna** (Wi-Fi 2.4 / 5 GHz and Bluetooth on ANT0; 10 pF from pin 18 to pin 23). The dedicated configuration (Bluetooth on ANT1) stays open in the layout and on the prototype. It becomes the production configuration only if the coexistence gate below fails, and then with a case change that gives a second antenna its keep-out.
3. **Certified variants (Q3; T1-075, T1-077):** every certified variant uses the 146153-0050 and the TX-power table of Murata's certification for its declared markets (CER-0248 Tables 6–18, 22–34, 38–47, 49–53), capped at the level its SAR report covers, and carries no transmitter without a grant for those markets. The tuned antenna stays within the certified type: same type, gain ≤ 3.2 / 4.25 dBi, spurious emissions no more than 3 dB worse than Murata's report (CER-0248 §2.1.5.1). Each variant is verified and certified on its own (RFC 0011). If the 146153 fails in the case, the fallback is another listed antenna (219611 needs 15.4 mm of wall height) or an equivalent type at no higher gain added to Murata's certification.
4. **The layout holds every option (no respin):** both ANT0 and ANT1 paths as Murata's copy, with U.FL, 0603 matching positions, the 10 pF shared link and the dedicated-configuration positions; U.FLs in the top band near the top wall; ≥ 0.8 mm keep-out under each U.FL (PCB-R-02, PCB-R-03).
5. **Keep-out:** the radiating element stays ≥ 5 mm (provisional, **UNVERIFIED**) from any metal: battery, metal pocket floor, microSD shell, screw inserts, display frame and HAT metal. The case keeps that zone free and uncoated. The figure is confirmed or changed by measurement on the prototype.
6. **Software guarantees (Blackbird OS):** the variant's certified TX-power table is selected from variant data; the time-averaged power never exceeds the SAR-tested level, as a documented and visible safety and legal limit (BRD-049); the calibration file follows the fitted configuration; 802.15.4 stays off (not wired).
7. **RF exposure:** SAR pre-assessment at Q2 (V5-06); a formal SAR report for each certified variant at Q3.

## Consequences

- **BOM line changes** (applied in BOM v1):
  - Line 57: Molex 146187-0050 × 2 → **Molex 146153-0050 × 1** (Wi-Fi/Bluetooth antenna, 2.4/5 GHz flexible dipole, U.FL, 50 mm class); multiple authorized sources; alternates Molex 219611-0050 (listed in all three, needs 15.4 mm of wall) and, Japan only, Molex 146187-0050. Notes: top-wall mount, shared configuration; a second antenna only under the dedicated option (prototype experiment: Inventek W24P-U, 2.4 GHz, listed in all three).
  - Line 56: Hirose U.FL-R-SMT-1(10) quantity stays **2** (ANT0 fitted; ANT1 footprint kept, fitted on the prototype for the dedicated-configuration experiment, DNP in production unless decision 2 changes); the note "number of RF pins on Type 2EL **UNVERIFIED**" becomes "ANT0 pin 15, ANT1 pin 23 (E2B-54-1953 Table 3)".
  - Line 58: matching positions in **0603** as in Murata's reference (E2B-09-1413 Figures 9–10), not 0402, plus the 10 pF pin 18–pin 23 link (fitted for shared) and the dedicated-configuration positions (DNP).
- **Constraints updated in the PCB design constraints:** PCB-R-04 names the 146153-0050 and the certified variants of this ADR; PCB-R-07 takes the 5 mm provisional keep-out and the top-wall position instead of "Molex 146187 data".
- **Verification rows to add** (electronics integration and verification, prototype level): antenna return loss and efficiency in the prototype case, gain at or below 3.2 / 4.25 dBi after tuning, spurious no more than 3 dB worse than Murata's report; isolation and coexistence of the dedicated option; and the **coexistence gate**: Bluetooth audio at the highest codec rate the T1 offers, with Wi-Fi streaming at the same time, over a long session, without dropouts. If shared fails it, decision 2 switches to dedicated with a case change before Q2.
- **Case input:** the top-wall antenna area and its metal-free zone; HATs keep the antenna keep-out (hat-standard).
- **Software input (system):** a TX-power table loader or equivalent cap for mainline `nxpwifi` is needed before Q2; how Murata's tables reach the mainline driver is **UNVERIFIED**.
- **parts-lib:** new sheets for Molex 146153-0050 and Inventek W24P-U; the 146187-0050 sheet gets a note on Molex's length classes.

## Note (2026-10-24): anodised-aluminium case

BRD-061 (should, confirmed by the maintainers on 2026-10-24) asks that the antennas work in an anodised-aluminium case (CASE-022), with every radiator, feed and tuning part in the main body (never in the faceplate) and the back cover only as a last resort, because HAT cases replace it.

- **The decision stands for the polymer T1 and is compatible with a metal core under one condition:** the top end of the core is non-metallic (polymer, glass or ceramic) over the whole top wall and far enough onto the sides and back to keep the 146153-0050 ≥ 5 mm (provisional) from metal. Then the antenna, the board, the shared configuration and the certified variants of item 3 are unchanged; the metal variant retunes the match (Class I documentation: same type, gain ≤ 3.2 / 4.25 dBi, spurious ≤ 3 dB worse) and has its own SAR report and TX-power cap. This is the preferred path.
- **A fully metal top changes the antenna, not the board:** the aluminium frame becomes the antenna (split band or dielectric-filled slot in the top or upper side walls), fed from ANT0 through a spring-contact branch the board already holds (PCB-R-09 to R-12: stub-free selection against the U.FL, DC-block, pi matching, shunt inductor and ≤ 0.2 pF ESD at the feed pad, case-ground contacts). It is a new antenna type, so Murata's certification must cover it, and the metal variant gets its own radiated tests and SAR report; it is certified on its own (RFC 0011, T1-077).
- **Excluded:** antennas in the faceplate (it is a separate, interchangeable module); antennas in the back cover except as a flagged last resort with the HAT keep-out extended over them.
- **Item 4 extended:** the layout also holds the case-antenna branch and the case-ground contacts (PCB-R-08 to R-13), all DNP in the polymer production variant (BRD-053).

## Note (2026-10-24): radio performance aim

The maintainers want radios that beat commercial devices at distance and through walls. Murata's certified EDR power (5 ± 3 dBm FCC, 0 dBm EU) rules out winning by power, so the aim is met by antenna efficiency, placement, the Bluetooth configuration, LE Audio and codec adaptation. Consequences for this ADR:

- **The dedicated Bluetooth antenna becomes the target configuration**; the shared configuration stays as the fallback. Prototype 1 fits both paths and measures both (V2-R01, V3-05); the measured result decides the production configuration.
- **The second antenna zone is not reserved by changing the body now.** The 5 mm keep-out that excludes it is UNVERIFIED; prototype 1 measures the real clearance in the main body frame (never the faceplate, ideally not the back cover). The body grows, or the battery narrows, only if those measurements show the second antenna cannot fit and the dedicated configuration is worth it.
- A certified variant may be tested and certified at a higher power than Murata's figures where its grant allows it; each variant is verified and certified on its own (RFC 0011).
