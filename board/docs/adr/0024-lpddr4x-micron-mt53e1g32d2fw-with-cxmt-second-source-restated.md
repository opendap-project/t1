# ADR 0024: LPDDR4X: Micron MT53E1G32D2FW-046, CXMT CXDB5CBAM-MA-B as second source (restated)

- **Status:** Accepted. Supersedes [ADR 0022](0022-lpddr4x-micron-mt53e1g32d2fw-with-cxmt-second-source.md).
- **Date:** 2026-10-27 (decision taken 2026-10-25)
- **Why restated:** ADR 0022 cited the parts library's spec sheets, which libs v0.3.0 no longer publishes. This ADR states the same decision with the facts those sheets carried, cited to their sources and to the libs manifest and generator data. The decision is unchanged.
- **Replaces:** the BOM v1 line 8 choice, Samsung K4UBE3D4AB-MGCL, and its SK hynix H9HCNNNCPMMLXR-NEE alternate

## Context

BOM v1 line 8 is the Samsung K4UBE3D4AB-MGCL, 4 GB LPDDR4X, dual rank, 200-ball FBGA 10 × 15 mm. Samsung lists it as discontinued (Samsung Semiconductor product page for K4UBE3D4AB-MGCL, read 2026-10-24). No authorized channel offers it (2026-10-25). A part without supply fails T1-028 and T1-029, and dropping to 2 GB is excluded by ADR 0013.

LPDDR4X supply narrowed at the same time: Samsung no longer takes LPDDR4/LPDDR4X orders (Profesional Review, 2026-04-19), and Micron continues LPDDR4 only for long-term automotive, industrial and networking customers (Micron customer notice of June 2025, reported by TrendForce, 2025-06-13). The candidates below are the industrial and automotive grades of the large makers and the parts of other makers on the RK3566 support list.

### Requirements for the replacement

- LPDDR4X (or LPDDR4 if the RK3566 and the power tree allow), 32 Gb (4 GB) in one package, x32 (two channels x16), 200-ball FBGA on the RK3566's 32-bit interface.
- At least the rate the RK3566 runs: the DDR blob is `rk3566_ddr_1056MHz_v1.26.bin` (blackbird-os ADR 0003), 2112 Mb/s.
- Supported by that blob. Rockchip's *DDR SDRAM Support List* Ver 2.65 (2025-03-17) is the evidence: "T/A" = "Sample Tested and Applicable, Applicable and Ready for Mass Production" (p. 2), and "Rockchip platform can support all the chips that match the first part of Part Number" (p. 3). Notes [7] and [12] ask for blob v1.09 and v1.13 or later on RK3566 (p. 4): v1.26 meets both. The rkbin RK3566 release notes add capacity-detection and tDQS2DQ fixes in v1.26 (2026-05-21).
- Supplies within the board's rails: VDD1 on vcc1v8_ddr (1.8 V), VDD2 on vcc_ddr (1.113 V nominal, ≈ 1.08–1.14 V worst case, BOM v1.8 item 3), VDDQ from the TPS7A1006 (0.60 V).
- Active lifecycle, a public datasheet with the ball map, and stock or orders through authorized channels (ADR 0013).

### Candidates

Channels checked 2026-10-25; lifecycle as distributors listed it that day. RK3566 status from the support list Ver 2.65 (page).

| Part | Type, ranks | RK3566 | Lifecycle | Public datasheet | Authorized channel |
|---|---|---|---|---|---|
| **Micron MT53E1G32D2FW-046 :C** (IT:C / WT:C / AAT:C) | LPDDR4X/LPDDR4 unified, 1 rank | T/A: WT:B (p. 7), IT:C (p. 20) | Active; `:A` Obsolete | Yes (z42n Rev. C) | Yes (AAT:C in distributor stock; IT:C and WT:C by order) |
| **CXMT CXDB5CBAM-MA-B** | LPDDR4X, 1 rank | T/A (p. 11) | 3rd generation, no EOL found | Yes (V1.0, LCSC copy) | No franchised distributor; maker channel |
| CXMT CXDB5CCBM-MA-A | LPDDR4X | S/A (`CXDB5CCBM-M*-A`, p. 11) | not stated | No | No franchised distributor |
| Samsung K4UBE3D4AB-MGCL (today) | LPDDR4X, 2 ranks | T/A (p. 8) | Discontinued | Yes | No authorized channel |
| SK hynix H9HCNNNCPMMLXR-NEE | LPDDR4X, 2 ranks | S/A [7] (p. 9) | not stated | No (NDA) | Brokers only |
| Kingston B3221XM3BDGVI-U | LPDDR4X | not listed | not stated | No ball map found | Yes |
| ISSI IS43LQ32K01B-046BLI | LPDDR4/4X | not listed | Active | Link dead (404); the S2A version is "NR" at ISSI | Yes, none in stock |
| Alliance AS4C1G32MD4V-046BIN | LPDDR4X | not listed | Discontinued | — | No |
| FORESEE FLXC2004G-N1 | LPDDR4/4X | T/A (p. 15) | not stated | No | No |
| Rayson RS1G32LO4D2BDS-53BT | LPDDR4/4X | T/A (p. 16) | not stated | No | No |
| Micron MT53D1024M32D4DT-046 WT:D | LPDDR4 only, 4 dies | T/A [11] (`-053`, p. 7) | not stated | not read | No authorized channel |

**LPDDR4 compared.** The RK3566 runs LPDDR4 with VDDQ at 1.1 V: the board could take it by feeding VDDQ from vcc_ddr and leaving the TPS7A1006 unfitted. It is not adopted: the only available LPDDR4 part (MT53D1024M32D4DT) is an older die generation (T1-027), its RK3566 entry carries note [11] (LPDDR4 mode only), and the I/O swings at 1.1 V instead of 0.6 V, which costs I/O power for the battery. The Micron `:C` part is itself a unified LPDDR4/LPDDR4X device, so the LPDDR4 fallback stays open on the same land without a new part.

## Decision

1. **Primary: Micron MT53E1G32D2FW-046 IT:C.** 32 Gb, two 16 Gb single-channel dies, one per channel, **single rank**; 4266 Mb/s; VDD1 1.70–1.95 V, VDD2 1.06–1.17 V, VDDQ 0.57–0.65 V; −40 to +95 °C; 200-ball TFBGA 10 × 14.5 mm (z42n Rev. C pp. 1, 4, 21–22, 26, 43, 235–236). It is the exact entry Rockchip lists T/A on RK3566 (p. 20), Micron keeps industrial grades in supply, and it is the only active part in authorized stock with a public datasheet. Same-land grades: **WT:C** (same data sheet, −25 to +85 °C) is accepted; **AAT:C**, the grade in distributor stock today, is accepted for prototype builds once its automotive data sheet confirms the FW package (**UNVERIFIED**).
2. **Second source on the same land: CXMT CXDB5CBAM-MA-B.** Same organisation (one die per channel, one rank, ZQ0 shared), same supplies, T/A on RK3566 (p. 11), CXMT's current generation. It is fitted only after one qualification build (DDR blob training log, a long memory test) and once it is available through the maker's channel.
3. **One land for both.** libs part `micron:MT53E1G32D2FW-046`, footprint `micron:LPDDR4_FBGA-200_10.0x15.0mm_Layout12x22_P0.8x0.65mm_Pad0.3mm_NSMD` (generated from libs `kicad/generator/bga/micron/`): 0.30 mm NSMD land sized for both ball diameters (Micron 0.436 mm, CXMT 0.31 mm), outline and courtyard on the 10 × 15 mm envelope. `test_bga.py` re-reads the Micron ballout from the PDF and compares the CXMT ballout ball for ball: they differ only on balls one maker leaves NC.
4. **Rank-1 signals not connected.** Both parts are single rank: the RK3566 CS1, CKE1 and ODT1_CA outputs of both channels stay unconnected (the board pinout notes already make them conditional on a dual-rank DRAM), and ball A8 (ZQ1 on the Samsung part) gets no resistor. The land therefore takes single-rank parts only; a dual-rank part would need a new decision.
5. **Not adopted:** CXDB5CCBM-MA-A (no public datasheet and S/A only), SK hynix (no datasheet, broker supply), Kingston and ISSI (not on Rockchip's list, no usable public ball map), Alliance (discontinued), FORESEE and Rayson (no datasheet, no authorized channel; each would need its own decision), LPDDR4-only parts (above). Broker stock is never bought (ADR 0013).
6. **Still 4 GB in every variant** (ADR 0013); the 2 GB fallback part stays unnamed (feature-block gap G18).

## Consequences

- **Boot:** no change. The RK3566 DDR blob detects the DRAM type and capacity at run time (UNVERIFIED in detail; the rkbin notes fix capacity detection in v1.26); both parts are on Rockchip's list for RK3566 with no note. Bring-up records the blob's training log (it prints the DRAM maker ID since v1.22) for each part.
- **Power tree:** no change. Both parts take the same windows as the Samsung part: vcc_ddr's 1.08–1.14 V worst case sits inside VDD2 1.06–1.17 V; VDDQ 0.60 V and VDD1 1.8 V unchanged. The Micron IDD tables are public (z42n pp. 50–57), so BOM §7 item 33 (VDD1 and VDD2 currents) can now be closed from them; not transcribed here.
- **Peak bandwidth** is set by the RK3566 (32 bits at the blob's 1056 MHz) and does not change; the second rank of the Samsung part, which the controller could interleave, is gone (effect on the experience budgets **UNVERIFIED**, measured at bring-up with the long-session tests of T1-046 and T1-047).
- **Height:** the Micron package is 1 ± 0.1 mm (1.10 mm in the part chart) against 0.90 ± 0.10 mm for the Samsung part, on the back side: +0.10 mm to check against the case's back clearance.
- **libs:** the board takes the LPDDR4X symbol and footprint from libs (`micron:MT53E1G32D2FW-046` and the footprint above). Same ball positions as today; the land grows from 0.25 to 0.30 mm, so the DRAM fan-out is re-checked against the DRU (copper gap 0.35 mm, mask web 0.25 mm at the 0.65 mm pitch).
- **BOM v1 changes** (for the BOM owner; this ADR does not edit `bom-v1.md`):
  - **Line 8:** Samsung K4UBE3D4AB-MGCL → **Micron MT53E1G32D2FW-046 IT:C** (WT:C accepted; AAT:C after its data sheet check), Decided (ADR 0022), driver none (rkbin DDR blob ≥ v1.26). Second source: **CXMT CXDB5CBAM-MA-B** (qualification build first).
  - **Line 8 alternates:** remove SK hynix H9HCNNNCPMMLXR-NEE.
  - **Passives:** one ZQ resistor (240 Ω ± 1 % to VDDQ, ball A5) instead of two; no change to decoupling.
  - **Datasheet table (§ datasheets, rows K4UBE3D4AB-MGCL and H9HCNNNCPMMLXR-NEE):** replace with the Micron z42n Rev. C and the CXMT V1.0 datasheets (libs `parts/manifest.toml`: z42n Rev. C, 2023-02, sha256 `da659aad…`; CXMT Version 1.0, 2024-04-17, sha256 `becc7fc2…`).
  - **§7 item 38 (G18):** the 4 GB second source now has its land and blob support checked (libs `test_bga.py`, Rockchip list p. 11); the 2 GB fallback stays open.
- **Feature-block catalog changes** (for its owner; this ADR does not edit `feature-blocks.md`):
  - `blk.lpddr4x` alternates: `hynix-4gb` → **`cxmt-4gb`: CXMT CXDB5CBAM-MA-B** (land checked by libs `test_bga.py`, RK3566 T/A); `samsung-2gb` → `2gb` (part not named, ADR 0013).
  - `blk.lpddr4x` holds: "same-package LPDDR4X ... that the rkbin DDR blob supports" becomes "single-rank 200-ball LPDDR4X on the MO-311 grid, 10 × 14.5 or 10 × 15 mm, listed T/A for RK3566".
  - Gap G18: 4 GB alternate closed; 2 GB fallback still open.
- **Pinout v1:** the rank-1 notes (balls A3, 1A2, 1A4, 1A5 and the other CS1/CKE1 lines) resolve to "not connected: the DRAM is single rank (ADR 0022)".
- **libs:** manifest entries for both datasheets (above); the generator data `kicad/generator/bga/micron/MT53E1G32D2FW-046.toml` and its ball map, from which the symbol and the shared footprint are generated; `kicad/generator/test_bga.py` compares the CXMT ballout with it.
- **Open (UNVERIFIED until checked):** AAT:C package identity; a formal lifecycle statement from Micron for the `:C` grades and from CXMT; the experience-budget effect of single rank.
