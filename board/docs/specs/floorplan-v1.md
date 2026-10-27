# Floorplan v1 of the T1 main board

- **Status:** Draft v1 (2026-10-25; §7 added 2026-10-27 from [placement v1](placement-v1.md)). Basis: the maintainers' direction of 2026-10-25: the board is dense, with parts on both sides; functions are grouped into isolated zones that share the physical layers, each zone using the layers under it for its own needs, so the board needs as few layers and as few full-layer grounds as the zones allow. Nothing here is placed by a designer, routed or measured: it is the plan placement starts from.
- **Study board:** [`hardware/studies/floorplan/`](../../hardware/studies/floorplan/): `floorplan.py` builds a KiCad board with the outline, the zones and corridors as named rule areas, the height and battery areas, the mounting holes and every part whose position the product fixes (libs footprints), and computes the area budget of §2.1 (written on each run to `floorplan-v1.result.json`, not committed). DRC with the composed T1 rules: **0 errors**; warnings in §6 item 3.
- **Inputs:** [PCB design constraints](pcb-design-constraints.md) v0.14 (PCB-M, PCB-Z, PCB-L, PCB-R rows), [ADR 0016](../adr/0016-front-side-height-under-the-display.md), [ADR 0020](../adr/0020-battery-connected-through-contacts.md), [feature blocks](feature-blocks.md), [BOM v1](bom-v1.md) v1.14, the [HAT flat cable](hat-flat-cable.md) v1 ([RFC 0014](https://github.com/opendap-project/rfcs/blob/main/text/0014-hat-interface-v2-usb-only.md), [RFC 0015](https://github.com/opendap-project/rfcs/blob/main/text/0015-hat-connector-pogo-field-and-usb-c-port-hat.md)), [pinout v1](pinout-v1.md), [stackup v3](stackup-v3.md) (layer references updated from stackup v2 on 2026-10-25). Footprints: kicad-lib `88508b6`.

## 1. Outline, sides and heights

| Item | Value | Source |
|---|---|---|
| Outline | 55.3 × 90.1 mm (cavity 56.3 × 91.1 mm less 0.5 mm per side, **UNVERIFIED**) | PCB-M-02 |
| Frame | Origin at the board centre, x across, y along, +y towards the top wall | PCB-M-04 |
| Front (L1), under the display | Parts ≤ 1.0 mm; display 54.46 × 82.94 mm, centred (**UNVERIFIED** position) | PCB-Z-03, ADR 0016 |
| Front, faceplate connection area | ≈ 54 × 10 mm at the display's bottom edge: FH35C and its ESD only | ADR 0016 item 1 (size **UNVERIFIED**) |
| Back (L6), under the pocket | 51.3 mm wide, from 16.5 mm above the bottom edge to 6.5 mm below the top edge; parts ≤ 1.5 mm; battery-contact window exception | PCB-Z-01, PCB-L-05 |
| Back, bands | Bottom band 16.5 mm, top band 6.5 mm, side strips 2.0 mm; parts ≤ 14.2 mm | PCB-Z-02 |
| Mounting holes | (±24.15, 41.55) and (±24.9, −27.0) mm, 2.2 mm (**UNVERIFIED** until the case) | PCB-M-08, PCB-H |

## 2. Zones

Six zones, each a set of rectangles through every layer (an area may cover only some layers where two zones share a spot on opposite sides), named `ZONE_<NAME>` in KiCad; corridors are `ZONE_CORRIDOR`.

| Zone | Blocks (feature-blocks catalog) | Where (device frame, mm) | Fixed parts placed |
|---|---|---|---|
| **CORE** | `blk.soc`, `lpddr4x`, `emmc`, `microsd`, `pmic`, `vdd-cpu`, `pwr-3v3-sys`, `rp2354`, `tpm`, `gpio-expander`, `board-id`, `imu`, `haptics`, `nfc-*`, `status-led`, `maskrom`, `buttons`, `debug` | y −8 to 30, full width; the top band right of x 3 | RK3566 at (0, 10) on the back, LPDDR4X (Micron FBGA-200) to its right and eMMC to its left (the sides their balls face after the flip); RK809 below the SoC; RP2354A on the front; microSD at the top edge, right |
| **AUDIO** | `blk.audio` and its children, `jack-se`, `jack-bal`, `mic-ambient` | x < −6.2, y < −8 (the front strip x −9.5 to −6.2 inside the faceplate area excluded) | CS43198 × 2 and the two NZ2520 oscillators on the back under the pocket; 3.5 mm and 4.4 mm jacks in the bottom band |
| **POWER** | `blk.charger`, `gauge`, `pwr-vsys-lv`, `pwr-5v1`, `hat-5v`, `usb-vbus-out`, `current-monitors`, `hpa-rails`, `speaker`, `fp-backlight`, `cover-detect` | x > 6.2, y < −8, less the HAT strip; the back layer of the battery-contact window | Six battery contacts in a row at y −23.5 (P+, P+, empty, mid, NTC, P−, P−; x −2.0 to 19.0); the TPS62903; speaker shadow and three 4020 inductors in the band (drawn) |
| **IO** | `blk.usb-c`, `hat-signals`, `fp-connector` (supplies), `mic-main` | x −6.2 to 6.2, y < −8, with the HAT strip (x 6.2 to 20, y −34 to −28); every layer but the back over the contact window | USB-C centred at the bottom edge; the HAT flat-cable receptacle DF40C-50DS at (13.1, −31.0) on the back (drawn: kicad-lib has no footprint yet) |
| **RADIO** | `blk.radio`, `antennas` | Top-left: x < 3, y > 30 | U.FL × 2 in the top band; the 2EL module under the pocket (drawn) |
| **FACEPLATE** | `blk.fp-connector` (FH35C, ESD), `fp-display` lanes, `fp-controls` | Front only, x ±9.5, the faceplate connection area | FH35C at (2.5, −32.9) on the front, clear of the USB-C and jack through-hole pins |

The SoC's interfaces set the arrangement: after the flip to the back, its DDR balls face top-right, eMMC and SDIO top-left, USB left, DSI the bottom, I2S the bottom-right (pinout v1 ball positions on the kicad-lib footprint). The radio sits above the SDIO side; the I/O column runs from the SoC's bottom edge to the USB-C, the HAT receptacle and the FH35C; the I2S bus reaches the DACs through the core–audio corridor. With HATs USB only (RFC 0014), the pairs that leave the core for the I/O zone are nine: the USB-C D± pair, the HAT USB 3 SSTX±, SSRX± and D± pairs, and five DSI pairs.

### 2.1 Area budget per zone and side

Courtyard from kicad-lib footprints where a part is placed, estimates otherwise (marked in `floorplan.py`), times 1.7 (1.2 for edge parts); passives shared out by an estimated share. "Band" is the back area outside the pocket (tall and edge parts); "back" counts the band, the ≤ 1.5 mm parts and the ≤ 1.0 mm parts that fit on the back's remainder; the rest of the ≤ 1.0 mm parts go to the front.

| Zone | Need (mm²) | Back area | Band area | Band use | Back use | Front area | Front use |
|---|---|---|---|---|---|---|---|
| CORE | 3,622 | 2,447 | 329 | **205 %** | 100 % | 2,447 | 48 % |
| AUDIO | 1,349 | 770 | 395 | **115 %** | 100 % | 737 | 79 % |
| POWER | 1,597 | 792 | 320 | **139 %** | **108 %** | 662 | **112 %** |
| IO | 548 | 437 | 280 | 67 % | 100 % | 542 | 20 % |
| RADIO | 385 | 436 | 216 | 0 % | 88 % | 436 | 0 % |
| FACEPLATE | 201 | — | — | — | — | 190 | **106 %** |
| **Board** | **7,701** | | | | | | **77 % of 9,965 mm² (both sides)** |

The board as a whole fits at 77 %. The tall parts do not fit their bands (§6 items 1–2). The I/O zone dropped from 722 to 548 mm² with RFC 0014 (no extension switches, a 50-position receptacle instead of a 100-position one) and now has room: the power zone's front overflow and the core's band overflow move into the I/O zone and the core's front (48 % used) when placement starts.

## 3. Layer roles per zone

On [stackup v3](stackup-v3.md) (§3 there is the reference): six layers, one full-layer ground (L5). Roles: **F** fast routing (every neighbour ground), **G** ground, **P** power plane or pour.

| Zone | L1 | L2 | L3 | L4 | L5 | L6 |
|---|---|---|---|---|---|---|
| CORE | P: SoC decoupling, core-rail pours between the capacitors, low-speed routing | P: SoC core and system rails (with L3 across 90 µm) | G | F: escape, LPDDR4X, eMMC, microSD, SDIO | G | F: SoC, LPDDR4X, eMMC |
| AUDIO | F | G | G | F: MCLK, I2S, audio analog; audio rails as tracks | G | F |
| POWER | F: switch nodes over the L2 ground | G | P: battery path, VSYS | P: battery path, VSYS | G | F |
| RADIO | F: RF line option (over L3, L2 cut out) | G | G | P, or G under an L6 RF line | G (cut out under an L6 line) | F: module, RF line |
| IO | F: HAT `VBUS` and USB-C `VBUS` pours | G | G | F: USB 2, USB 3, DSI | G | F |
| FACEPLATE (front only) | F: FH35C | G | — | — | — | — |
| Corridors | F | G | G | F | G | F |

**Why these maps** (stackup v3 §3): the SoC's escape needs one inner fast layer two laser levels from the SoC side, L4, with ground on both sides (L3, L5); the core and system rails then share L2, paired with the L3 ground (PCB-S-12, S-20), and the core rails also pour on L1 between the decoupling capacitors. MCLK runs on L4 between L3 and L5 (PCB-I-09). The I/O zone's nine pairs use L4 besides the outer layers; its `VBUS` paths are outer pours (PCB-P-22). The power zone pours on L3 and L4 (PCB-P-01, P-23), with L2 and L5 ground under the switch nodes (PCB-P-08). The radio zone makes L4 ground under an L6 RF line, 235 µm under it (PCB-R-03), or runs the line on L1 over L3.

## 4. Isolation

1. **One ground.** L5 is the full-layer ground. L2 (all zones but the core), L3 (all zones but the power zone) and L4 (under an L6 RF line) are zone-local grounds, each stitched to L5 by ground vias on the PCB-S-13 grid and along every edge of its area (PCB-S-19). No split, no slot along a zone boundary (PCB-A-01).
2. **Fences.** Ground via fences along every boundary of the power and radio zones and along the audio zone's boundary with the power zone, at ≤ 2.5 mm pitch (**UNVERIFIED**: λ/10 at 6 GHz in FR-4, the PCB-S-13 value), CHK.
3. **Corridors.** Nets cross zones only in the declared corridors: core–audio (x −11 to −5, y −11 to −5: I2S, DAC control, enables), core–IO (x −4 to 4, y −11 to −5: USB-C USB 2, HAT USB 3 and USB 2, DSI), core–power (x 8 to 14, y −11 to −5: converter control, sense, enables), core–radio (x −22 to −12, y 27 to 33: SDIO, UART, PCM, control), IO–faceplate (x ±9.5, y −31.5 to −27.5: DSI and faceplate control). Under a corridor L2, L3 and L5 are ground (PCB-S-18, DRC), so no crossing changes reference; at a layer change in a corridor the ground via of PCB-S-10 sits next to the signal via.
4. **Edges of zone-local grounds.** A fast trace keeps 1.02 mm (pairs) or 0.30 mm (DDR) from the edge of its reference area (stackup v3 §4.1), the same values as from a cut-out.
5. **Audio.** The `AUDIO_ANALOG` area (x < −6.2, y < −14) keeps foreign tracks out on every layer (PCB-A-07) and every pour but ground off its inner layers, the audio rails running as tracks (PCB-A-20); switch nodes ≥ 5 mm away (PCB-A-06); the amplifier-rail converters (TPS65131, LMR33630C) sit in the power zone next to the audio boundary, their LDOs inside it.
6. **Switch nodes** stay in the power zone, except the PMIC's and the vdd_cpu buck's next to the SoC (core zone), which have ground on L3 and L5 under them and keep their switch-node copper off L1 over the L2 rail plane (PCB-P-08).

The DRC side (rules and test rows in [`hardware/rules/`](../../hardware/rules/)): PCB-S-17 (foreign track in a zone, six rules), PCB-S-18 (corridor references), PCB-S-14 per zone (no impedance class on L1 in the core zone nor on L4 in the power and radio zones), PCB-S-25 (ground layers per zone), PCB-P-22 (I/O zone `VBUS` on the outer layers only), PCB-A-20 (no inner pour in the analog audio area). Fences, stitching pitch, edge margins and layer-change vias are CHK items.

## 5. What the fixed parts showed

- **The faceplate connector cannot sit centred over the USB-C.** The USB4105's shell stakes and the 4.4 mm jack's plated slots go through the board inside the faceplate connection area; at (0, −36.5) the FH35C's courtyard covers them (DRC: PTH inside courtyard). At (2.5, −32.9) it clears them; the faceplate flex's arrival point is therefore an input to the faceplate.
- **The HAT receptacle sits in the bottom band.** The DF40C-50DS is 1.45 ± 0.15 mm high, up to 0.1 mm over the 1.5 mm under the pocket (PCB-Z-01), so it stays in the band, beside the USB-C, with its 12.6 mm length along the edge; the flat cable leaves towards the back cover.
- **The 4.4 mm jack reaches 22.0 mm into the board** (kicad-lib courtyard), 5.5 mm past the 16.5 mm bottom band and under the pocket at 6.5 mm height.
- **The microSD socket reaches 18.3 mm from the top edge**, 11.8 mm past the top band, at 1.68 mm under a 1.5 mm zone.
- **The battery-contact row is 24.5 mm long** and fits the pocket's bottom end only across the I/O column; the I/O zone's routes pass over the window on inner layers, the contacts own the back layer there (PCB-L-02 keeps every other net's copper off it).
- **The bottom bosses do not fit the bottom band** next to the jacks, the USB-C, the speaker and the HAT receptacle; the floorplan puts them at the pocket's bottom corners (±24.9, −27.0), which the pack's corner radius must allow (**UNVERIFIED**, case).

## 6. Open items

1. **Band capacity:** the core band holds the microSD (needs a local pocket-floor relief or a ≤ 1.5 mm socket) and the haptic actuator (candidate: in the case, off the board); the power band holds five 4020 inductors, the fuse and the speaker shadow (candidate: ≤ 1.5 mm inductors for the converters that allow them). Both are decisions for the BOM and the case.
2. **The 4.4 mm jack** needs ≈ 5.5 mm of pocket relief at the bottom-left, or the pocket's bottom end moves up there (case).
3. **PCB-L-01 against ADR 0016.** PCB-L-01 keeps every part with `Thermal` = `hot` out of `BATTERY_POCKET` (pocket + 3 mm), while ADR 0016 puts the SoC there; the floorplan draws the area on the back layer only, and DRC warns for the SoC, the PMIC and the TPS62903. The constraint's owner decides whether L-01 means the back side only, a dissipation threshold, or another place for the converters.
4. **Faceplate connection area** size and the FH35C position; the area is at 106 %.
5. **Mounting holes** and the screw (PCB-M-08, PCB-H): positions above are placeholders.
6. **Zone net classes:** closed (2026-10-27): every net gets its zone class (or `ZONE_SHARED`) besides its signal class ([`netclasses.toml`](../../hardware/rules/netclasses.toml)), from the schematic generator ([placement v1](placement-v1.md) §6 item 2).
7. **The DF40C-50DS footprint:** closed (2026-10-27): kicad-lib carries it, and [placement v1](placement-v1.md) places it.

## 7. Placement

[Placement v1](placement-v1.md) (2026-10-27) places every part of the schematic on this floorplan, with the board file `hardware/t1-main-board/t1-main-board.kicad_pcb`. Facts it adds here:

- **Real courtyards.** §2.1's method on the real footprints gives a board need of 113 % of both sides (77 % above; 111 % after the part swaps of placement v1 §4 decision 12): core band 227 %, power band 258 %, power back and front 165 %, audio front 254 %, faceplate area 109 % (placement v1 §3.1). The courtyards alone cover 68 % of both sides.
- **Zone changes** (placement v1 §4): the audio zone grows to y 2.4 (every layer) and y 14 (front); the power zone to y 0, to x 4.0 above the contact window, over the HAT strip's front and over part of the I/O column's back; the core takes the top band from x −5.5 to 3; the faceplate area's front is the faceplate zone's alone; the core–audio and core–power corridors move with their boundaries; `blk.audio-supply` (a buck) belongs to the power zone.
- **Fixed parts moved:** the RK809-5 above the SoC at (−6.0, 25.7), the RP2354A at (−16.0, 24.5), the microSD at x 13.5, the LPDDR4X at x 16.9, the U.FLs at x −14.0 and −8.3.
- §6 items 1 (band capacity), 2 (4.4 mm jack), 3 (PCB-L-01), 4 (faceplate area), and 5 (mounting holes) stay open, 6 (zone net classes) is closed; placement v1 §5 and §6 give their state.
