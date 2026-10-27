# T1 main board project

The KiCad 10 project of the T1 main board. The schematic is captured block by block ([feature-block catalog](../../docs/specs/feature-blocks.md), [RFC 0011](https://github.com/opendap-project/rfcs/blob/main/text/0011-feature-blocks-and-variants.md)); the project has no layout yet. Prototype 1 targets quality level Q1 ([RFC 0010](https://github.com/opendap-project/rfcs/blob/main/text/0010-quality-levels.md)).

The schematic is generated: `generator/` writes every sheet, the project file, the library tables and the project-local library parts from the board's data. Edit the generator and run it again; never edit a generated file by hand. A rerun with no change in its inputs writes byte-identical files (every UUID is derived from a stable key).

## Layout

| Path | What it is |
|---|---|
| `t1-main-board.kicad_pro` | The project: drawing sheet, text variables, ERC severities (CRAFT-158), net classes and their patterns. Generated |
| `t1-main-board.kicad_sch` | The root sheet: the block diagram. Generated |
| `power.kicad_sch`, `interconnect.kicad_sch` | The power and interconnect overviews. Generated |
| `<block>.kicad_sch` | One sheet per feature block, named after its ID without `blk.` (CRAFT-82). Generated |
| `sym-lib-table`, `fp-lib-table` | Library tables: kicad-lib through `${KIPRJMOD}/../lib/opendap`, the project library through `${KIPRJMOD}/../lib`, KiCad's stock libraries through `${KICAD10_SYMBOL_DIR}` and `${KICAD10_FOOTPRINT_DIR}`. Generated |
| `t1-main-board.dru.toml`, `t1-main-board.kicad_dru` | The rule sources and the composed rules ([`../rules/`](../rules/)) |
| `t1-main-board.craft.toml` | The craft check configuration: target level and mirrored blocks (CRAFT-34) by hand; its `[schematic]` table (rails and each block's interface, CRAFT-85, -112) generated below the marker line |
| `generator/` | The generator (Python 3.11 or later, no other dependency) |
| `../lib/symbols/T1_Main_Board.kicad_sym`, `../lib/footprints/T1_Main_Board.pretty/` | Project-only parts kicad-lib does not carry yet: the TPS7A1006PDSER symbol and the Murata DFE252012F, DFE201610E and Abracon AOTA-B201610 lands. Generated |

## Blocks captured

Drawn from 2026-10-25. Every sheet carries the block's notes (function, absent state, constraint IDs, ADRs), an interface table and a rail table.

| Page | Sheet | Block | Content |
|---|---|---|---|
| 1 | `t1-main-board.kicad_sch` | root | Block diagram in reading rows; the LPDDR4X and eMMC buses wired pin for pin |
| 2 | `power.kicad_sch` | power | Rail table of the drawn blocks and the power tree (power tree v0.6) |
| 3 | `interconnect.kicad_sch` | interconnect | Connector list; pin maps come with the connector blocks |
| 4-7 | `charger*.kicad_sch` | `blk.charger`, `-input`, `-core`, `-battery` | TPS2121 input mux and OV interlocks; BQ25798 2S charger; CSD17575Q3 ship FET, 5 A fuse, BATP and the six battery contacts with ESD (board ADRs 0014, 0020) |
| 8 | `gauge.kicad_sch` | `blk.gauge` | BQ28Z610-R1 on the pack side, 3 mΩ low-side sense, board NTC (board ADR 0017) |
| 9 | `pwr-vsys-lv.kicad_sch` | `blk.pwr-vsys-lv` | TPS62136, VSYS to VSYS_LV 3.8 V |
| 10 | `pwr-3v3-sys.kicad_sch` | `blk.pwr-3v3-sys` | TPS62827, vcc3v3_sys 3.3 V |
| 11 | `pmic.kicad_sch` | `blk.pmic` | RK809-5: bucks, LDOs, RTC, control |
| 12 | `vdd-cpu.kicad_sch` | `blk.vdd-cpu` | TPS6286910C vdd_cpu (board ADR 0021) |
| 13-20 | `soc*.kicad_sch` | `blk.soc`, `blk.soc-*` | RK3566 by IO domain: PMU IO with clock, reset and pull-ups; DDR; VCCIO1-4; VCCIO5-7; the PHYs (USB 2.0 and 3, multi-PHY, CSI RX, DSI, HDMI, eDP); supplies; ground |
| 21 | `lpddr4x.kicad_sch` | `blk.lpddr4x` | Micron MT53E1G32D2FW-046 (board ADR 0022), TPS7A1006 VDDQ, links |
| 22-33 | `audio*.kicad_sch`, `mclk`, `dac-*`, `hpa-*` | `blk.audio` and its sub-sheets | DAC supplies, divided master clocks (ADR 0019), two CS43198, ±7 V and ±6 V rails, six OPA1622 |
| 34 | `jack-se.kicad_sch` | `blk.jack-se` | The 3.5 mm jack |
| 35-37 | `rp2354*.kicad_sch` | `blk.rp2354`, `-core`, `-power` | RP2354A (one reference, three units): system and GPIO units with the 12 MHz oscillator, BOOTSEL N-FET, 27 Ω USB series, the five I2S/DSD tap positions and test pads; the supply unit with its 3.3 µH core regulator, RP_3V3 and RP_IOVDD_1V8 switches, links #21 and #30 |
| 38 | `emmc.kicad_sch` | `blk.emmc` | Samsung KLMBG2JETD-B041 eMMC, 16 GB alternate |
| 39 | `jack-bal.kicad_sch` | `blk.jack-bal` | The 4.4 mm jack |
| 40 | `current-monitors.kicad_sch` | `blk.current-monitors` | Five INA236 on I2C1 (0x40-0x43, 0x48) and their shunts: VSYS 10 mΩ, audio VSYS_LV and VSYS sides 20 mΩ each, display 100 mΩ, HAT 20 mΩ |
| 41 | `debug.kicad_sch` | `blk.debug` | Debug UART2 and I2S/DSD pads with ground, reset and PMIC pads, the spare SoC GPIO pads (the `DEBUG` bus), a pad on every rail no other sheet probes |
| 42 | `pwr-5v1.kicad_sch` | `blk.pwr-5v1` | TPS62903 5.1 V source, enabled by either port (OR of HAT5V_EN, USB_SRC_ON) |
| 43 | `usb-vbus-out.kicad_sch` | `blk.usb-vbus-out` | eFuse #D (shared limiter) and eFuse #C (USB-C source), TPS259470A (RFC 0015) |
| 44 | `usb-c.kicad_sch` | `blk.usb-c` | USB4105 receptacle, TVS2200, TPD8S300A, TPD4E05U06, FUSB302B, VBUSDET divider |
| 45 | `hat-signals.kicad_sch` | `blk.hat-signals` | DF40C-50DS flat-cable receptacle (interface v2 §9.2), USB 3 TX AC coupling |
| 46 | `hat-5v.kicad_sch` | `blk.hat-5v` | eFuse #A, FUSB302B01 (USB PD on the HAT port), VBUS discharge (RFC 0014) |
| 47-49 | `radio*.kicad_sch` | `blk.radio`, `-module`, `-power` | Murata Type 2EL by unit with its SDIO series positions; TPS22919 AVDD33, TPS62826 AVDD18, links #11, #12, SN74AXC1T45 PDn hold |
| 50 | `antennas.kicad_sch` | `blk.antennas` | ANT0 and ANT1 paths with matching positions, U.FL, the 10 pF shared link (ADR 0018) |
| 51 | `fp-connector.kicad_sch` | `blk.fp-connector` | FH35C-51S contacts (pinout v1 §8.2), 6 × TPD4E05U06, TPS22950 FP_3V3, TPS22945 FP_1V8, links #23 and #31 |
| 52 | `fp-backlight.kicad_sch` | `blk.fp-backlight` | TPS61160, 22 µH, PMEG6010CEH, RSET 3.32 Ω |
| 53 | `speaker.kicad_sch` | `blk.speaker` | MAX98357A, gain 3 dB, SD_MODE position, speaker pads, link #17 |
| 54 | `board-id.kicad_sch` | `blk.board-id` | AT24C02D at 0x50 |
| 55 | `tpm.kicad_sch` | `blk.tpm` | SLB9673 TPM 2.0 at 0x2E, always on, link #20 |
| 56 | `nfc-reader.kicad_sch` | `blk.nfc-reader` | PN7160 at 0x28, NFC_VBAT switch and link #18, EMC filter, matching and RX path (AN13219 first-iteration values), 27.12 MHz crystal, antenna contacts |
| 57 | `fp-display.kicad_sch` | `blk.fp-display` | TPS22945 FP_VCI after RK809 LDO4, link #24 |
| 58 | `fp-controls.kicad_sch` | `blk.fp-controls` | I2C3, interrupt and SPI CS pulls on FP_3V3, the GT911 strap footprint |
| 59 | `microsd.kicad_sch` | `blk.microsd` | DM3AT socket, 22 Ω series, detect, 2 × TPD4E05U06, link #16 |
| 60 | `imu.kicad_sch` | `blk.imu` | LSM6DSV16X at 0x6A, INT1 wake, link #32 |
| 61 | `nfc-tag.kicad_sch` | `blk.nfc-tag` | NT3H2111 NTAG I2C plus at 0x55, field detect, loop antenna contacts, link #33 |
| 62 | `mic-main.kicad_sch` | `blk.mic-main` | TPS22945 MIC_1V8, PDM clock series resistor |
| 63 | `status-led.kicad_sch` | `blk.status-led` | LP5521 at 0x32 on I2C2, charge pump, LED_R/G/B to the faceplate as the `LED` bus, link #22 |
| 64 | `gpio-expander.kicad_sch` | `blk.gpio-expander` | TCA6416A at 0x21 with the off-state pull-downs and the input pull-ups |
| 65 | `haptics.kicad_sch` | `blk.haptics` | DRV2605L at 0x5A, LRA contacts, link #19 |
| 66 | `buttons.kicad_sch` | `blk.buttons` | Power, Vol+, Vol− (PTS815) and Action (part open) to ground, 4 × TPD1E10B06, the Vol− pull-up |

Not drawn yet: `blk.mic-ambient`, `blk.maskrom`, `blk.cover-detect` (their kicad-lib parts exist). Nets from the drawn sheets to those blocks end in a local label, which ERC lists as `isolated_pin_label` (a warning). The RK3566 USB, multi-PHY and CSI RX units are on `blk.soc-phy`; the reserved balls (`RSVD_*` in pinout v1), the spares pinout v1 leaves without a pad and the unused PHY balls carry no-connect flags.

The SoC is one catalog block, `blk.soc`, drawn as a parent sheet with seven sub-sheets. The craft check names a sheet's block by its file, so the sub-sheets carry IDs of their own (`blk.soc-ddr` and so on) and their parts carry them in the `Block` field. The charger, the coprocessor, the radio, the amplifier rails and the balanced stage are drawn the same way (`blk.charger-core`, `blk.radio-module`, `blk.hpa-rails-pre`, `blk.hpa-bal-l` and so on). The audio host-side parts (DAC I2C isolation, the enables' pull-downs, the RX-clock option) sit on `blk.soc-vccio-b`, next to the balls they serve.

## Conventions the generator applies

- Values carry their unit with an SI prefix and a space (CRAFT-141): `22 Ω`, `4.7 kΩ`, `100 nF`. Ratings the sheet's "unless noted" line does not cover go to `Spec`.
- Rails connect through power symbols named as the power tree; signals through labels, hierarchical labels where they cross the hierarchy. Global labels are not used.
- Net names are pinout v1's (active low ends in `_N`, upper case, CRAFT-84).
- Measurement links (BOM v1 line 137; numbered as power tree §4.12) carry their shunt in the base design (the full variant). The production variant fits 0 Ω jumpers (except H5), written into each link as a KiCad 10 design variant from `../variants/*.toml`; the eMMC's 16 GB alternate is written the same way. The generator writes this variant data itself; the feature-blocks spec §6 assigns it to `odapkit variant sync`, which does not exist yet.
- Parts the BOM does not name (generic capacitors and resistors) are capture choices from the Murata GRM and Yageo RC families (`generator/parts.py`). Their stock and effective capacitance under DC bias are **UNVERIFIED** until the BOM pass.
- `PWR_FLAG`s sit on the sheet that feeds each rail, on a branch of the rail's wire outside the block's groups (a link's load side, an inductor output). A local net fed through a passive part (`TPM_VDD` through its link, `RP_DVDD` through the inductor, `GAUGE_VC2` through its input resistor) stays a local net, not a power-tree rail, and takes its flag the same way: on a branch of the wire that leaves the feeding part, never in a detached label-and-flag row. KiCad 10.0.7's ERC reports a flag on a net island of power symbols alone as `pin_not_connected` (tested again on 2026-10-25, also with a project ERC exclusion), so the flags cannot go on the power overview.
- Buses cross the hierarchy through the project's bus aliases (`schematic.bus_aliases` in the `.kicad_pro`): `DDR_CHA` (with `DDR_RESET_N`), `DDR_CHB`, `EMMC`, `I2C0`, `I2C1`, `I2C2`, `PMIC_CTL`, for the audio block `AUDIO_I2S`, `AUDIO_CTL`, `DAC_L_OUT`, `DAC_R_OUT`, `HP_SE`, `HP_BAL`, and for the ports and IO `USB`, `IO_IRQ`, `IMON`, `WL`, `FP`, `EXP_IO` (the expander's port lines), `SDMMC0`, `SPK_I2S`, and for the control lines of the buttons, the I2C2 blocks and the coprocessor `KEYS`, `NFC`, `TPM`, `RP`, the status LED's current-source lines `LED`, and the debug UART with the spare SoC GPIOs `DEBUG`. A sheet pin `{ALIAS}` carries every member; inside a sheet the members keep local labels at their pins and one hierarchical label `{ALIAS}` on a bus stub joins them. The members keep their pinout names.
- Power symbols point up (GND down, CRAFT-85). A rail on an IC's side pin stands upright at the end of a stub long enough to clear the two rows above it; a column of rails on adjacent pins (the RK809's LDO outputs) turns its symbols outward, each value on its own row.
- Text never overlaps text or lines (CRAFT-175): fields go on a side of the body without pins, clear of capacitor plates; decoupling pitch follows the longest value or rating; table rows grow with wrapped text; a hierarchical label with a local label one row below it in the same pin column moves up half a row on a short dogleg; and `generator/overlaps.py` checks every plotted sheet (references included), group outlines and table borders among the lines. Bus ports stack above the interface table and fall back to rows when the column would meet a group. A vertical two-pin part's text keeps 1.27 mm to the next part's body.
- Zones (CRAFT-170, -174): groups, tables and the notes box never meet each other, the title block or the frame, and nothing drawn crosses the frame. The generator stops on a collision (`overlaps.zones`), and `generator/overlaps.py` reports frame and title-block crossings on the plots.
- The root (CRAFT-111) is laid out in titled rows; the page numbers are assigned from the same row list before anything is drawn, each parent's sub-sheets right after it, and the generator stops if the plot reads in another order or a block reaches the frame or the title block. Boxes stacked in one column share its width, in 7.62 mm steps. A column may leave a stack level empty, so a box sits in the next band below a shorter neighbour or the notes (checked against them); two facing sheet pins are joined directly only where the route meets no other symbol, otherwise each takes a label.
- Connector contacts on one side with one rail (VBUS, GND) join one vertical collector clear of the signal labels, one symbol at its end (`draw.side_collector`).
- Thermistors use kicad-lib's `OpenDAP_Device:Thermistor_NTC` (reference prefix RT, CRAFT-130); KiCad's stock symbol carries TH.
- A unit of a multi-unit part reads reference, dot, unit name (`U3501.System`, `U1101.BUCK`): the project's unit notation is KiCad's `.A` (`schematic.subpart_id_separator` 46); without it KiCad 10 runs the name into the designator (`U3501System`).
- The title block's Variant shows `full` on the base design: the project text variable `OPENDAP_BASE_VARIANT` comes from the variant file of kind `full` in `../variants/`, and kicad-lib's drawing sheet shows it when KiCad's `${VARIANT}` is empty (a plot with `--variant <name>` shows that name).
- Clearances (`generator/overlaps.py`, on the SVG plots): no text, pin numbers included, within 0.1 mm of a no-connect cross; labels, references and values at least 0.5 mm from a component outline, pin or cross; group outlines at least 3.81 mm inside the frame.

## Commands

From the repository root, with toolkit-hardware's `odapkit` on the path:

```sh
python3 hardware/t1-main-board/generator/generate.py      # after any input changes
kicad-cli sch erc hardware/t1-main-board/t1-main-board.kicad_sch
odapkit craft check hardware/t1-main-board/t1-main-board.kicad_sch
python3 hardware/t1-main-board/generator/overlaps.py                   # text collisions on the plots
kicad-cli sch export pdf --theme OpenDAP -o fab/t1-main-board.pdf hardware/t1-main-board/t1-main-board.kicad_sch
odapkit dru compose hardware/t1-main-board/t1-main-board.dru.toml   # after the rule sources change
odapkit dru check
```

The generator's inputs are the pinout (`../pinout/pinout-v1.csv`), the net classes (`../rules/netclasses.toml`; set `T1_NETCLASSES` to read another copy), the variant files (`../variants/*.toml`), kicad-lib (`../lib/opendap`) and the block definitions in `generator/`. Rerun it when any of them changes: the net classes and their patterns in the project, the variant data and the interface lists follow.

The PDF plot uses kicad-lib's OpenDAP colour theme (CRAFT-103): copy `../lib/opendap/colour-themes/opendap.json` into KiCad's `colors` folder first (on macOS `~/Library/Preferences/kicad/10.0/colors/`). Plots are generated outputs and are not committed.

## Status (2026-10-26)

ERC: no errors (warnings: `isolated_pin_label` for nets to blocks not drawn yet, six `footprint_link_issues` for the undrawn Würth, Murata LQH3NP and C&K PTS815 lands, one `lib_symbol_mismatch` for KiCad's stock DMP3099L, five `pin_to_pin` for inputs tied to ground next to a `PWR_FLAG`). `odapkit craft check`: Q1 met, Q2 reached (Q3 debt: CRAFT-114, -127). `generator/overlaps.py`: no text collides with text or lines on any sheet, and the clearances above hold (2026-10-26: 386 pin numbers met no-connect crosses before kicad-lib's pin lengths grew with their numbers, CRAFT-121; none after). Every new sheet was reviewed on its SVG plot, region by region. The generator's output does not depend on Python's hash seed (checked with two seeds on 2026-10-26).

On the root, the notes sit at the right end of the second row, so the bottom row keeps the space above the title block for blocks (the `blk.nfc-tag` symbol met the notes box on 2026-10-26).

The GUI review findings of 2026-10-25 are applied: the root carries the LPDDR4X and eMMC interfaces as bus aliases; sheet symbols are sized from their pin names, so vertical supply pins, names and headings stay apart; the eMMC reaches the SoC as one bus; on `blk.vdd-cpu` the VOS sense runs inside the output group at a height apart from the AGND/PGND junction and `vdd_cpu` leaves through an upright power symbol; each measurement link has its own group with its `PWR_FLAG` outside it; `blk.lpddr4x` is rearranged (regulator and links upper right, decoupling in its own band); SoC sub-sheet labels no longer mix hierarchical and local labels in one pin column; `blk.pmic`'s supply inputs clear the tables.

The audio block (pages 18-31) was reviewed on SVG plots of every sheet: its sheets lay their groups out in rows (`draw.Flow`), and the amplifier rails and the balanced stage are split into sub-sheets so that no sheet runs past its circuit band.

## Capture decisions

Details the board documents left open, decided at capture. Each sheet's notes repeat them.

- `blk.current-monitors`: Accepted (2026-10-26). The shunts sit on this sheet with their INA236, and each measured branch is a rail of its own, named in power tree §4.12: `VSYS_SRC` (BQ25798 SYS, the supply side of the VSYS shunt), `VSYS_LV_AUDIO`, `VSYS_AUDIO` (the LMR33630C with its enable shifter), `VSYS_LV_BL`, `VSYS_P5V1`; their PWR_FLAGs hang from the shunts' load-side wires. Shunt parts in the Vishay WSL family of line 43: WSL2512R0100FEA (VSYS, 10 mΩ, 1 W), WSL2010R0200FEA (HAT, 20 mΩ, 0.5 W), WSL1206R1000FEA (display), WSL1206R0200FEA (both audio channels, named by the BOM). A0 = GND, VS, SDA, SCL for 0x40-0x43; ALERT open; no input filter. Basis: BOM v1 lines 54 and 136 (values, ratings, addresses), power tree §4.12 (positions), Vishay doc 30100 (WSL2512 1 W, WSL2010 0.5 W, WSL1206 to 0.2 Ω), SBOSA81D Table 7-1 and §8.1.4 (the filter is only for transients near the 500 kHz sampling harmonics).
- `blk.status-led`: Accepted (2026-10-26). INT and GPO open, with no SoC line for them in pinout v1; ADDR_SEL0, ADDR_SEL1, TRIG and CLK_32K to ground (0x32, internal clock); CFLY 470 nF and VOUT 1 µF 10 V as the data sheet's typical application. Basis: BOM v1 line 105, SNVS441I p. 37 and §7.3.5, pinout v1 (no LP5521 interrupt ball).
- `blk.debug`: Accepted (2026-10-26). The I2S/DSD pads take I2S_BCLK as the DSD clock (the DACs take DSDCLK from it), and each DAC sheet carries the pad on its own MCLK; reset, PMIC and power-key pads cover PCB-T-09's SoC and PMIC items; every spare whose pinout v1 row names a test pad has one, the rest carry no-connect flags; rail pads are generated for each power-tree rail that no other sheet probes (PCB-T-02). Basis: BOM v1 lines 86-88, pinout v1 spare rows, PCB-T-01, -02, -09, feature-block record 49.

## Open items

Listed per sheet in each sheet's notes. In short:

- `blk.usb-c`: OTG0 VBUSDET rating at 9-12 V VBUS (BOM §7 item 41); VCONN termination; the D± common-mode choke footprint.
- `blk.hat-5v`, `blk.hat-signals`: the VBUS discharge value (BOM §7 item 47); DF40C contact numbering against the Hirose drawing (interface v2 §11 item 5).
- `blk.radio-*`: module land mask and stencil, supply sequencing and the AVDD33 range (module datasheet not obtained).
- `blk.fp-*`, `blk.mic-main`: the TPS22945 limit at 1.8 V and 2.8 V and the TPS22950 limit at 3.57 kΩ (**UNVERIFIED**); the TPS22950 FLT output left open; the DSI common-mode filter positions; the privacy-LED gate (no faceplate contact in pinout v1 §8.2); the LQH3NPN220 land (Murata sheet not retrieved).
- `blk.nfc-tag`: the loop antenna and its tuning (line 126); the tag's behaviour with VCC at 0 V on a live I2C2 (G6). `blk.tpm`, `blk.haptics`: kernel modules through DKMS (BOM v1.7 item 4).
- `blk.nfc-reader`: the matching values are AN13219 Rev. 1.6's first iteration for its example antenna and are retuned with a VNA on the T1's antenna (BOM line 126: shared loop or its own); the 15 pF crystal load capacitors (from CL 10 pF, DS Table 46 and AN14518's EVK parasitics) and the NDK NX2016SA pad assignment on KiCad's 2016 land are **UNVERIFIED**.
- `blk.rp2354-*`: the GPIO allocation is recorded in pinout v1 §3 (2026-10-26); the AOTA inductor's polarity against the Pico 2 layout and the RP2354A IOVDD pin list (DS Figure 152 against Table 1679, parts-lib sheet) are **UNVERIFIED**; the SoC-side 2.2 Ω USB series of pinout v1 V1/V2 sits with `blk.soc-phy` and is reconciled with the 27 Ω at the RP2354A at layout.
- `blk.buttons`: the Action part is open (BOM line 76; KMR221GLFS placeholder on KiCad's KMR2 land); the PTS815 land `T1_Main_Board:SW_CK_PTS815` is not drawn until the C&K drawing shows which terminals are common (parts-lib sheet, **UNVERIFIED**). The switches use KiCad's two-pin `Switch:SW_Push`.
- `blk.microsd`: detect switch wiring against the Hirose drawing.
- `blk.mic-main`: links #34 and #35 (one per MIC_1V8 branch, power tree §4.12) come with `blk.mic-ambient`, which sets the second branch.
- `blk.current-monitors`: the RK3566 I2C1 against the 100 ns extra hold the INA236 asks for at A0 = SDA (0x42, SBOSA81D p. 16), **UNVERIFIED** until bring-up; the stock KiCad 2512, 2010 and 1206 lands against the WSL pad table (doc 30100 p. 2).
- `blk.charger-*`: the pack NTC type behind the TS divider (**UNVERIFIED**); the Mill-Max 0965 pogo fallback land (BOM v1 line 47); the P+ TVS part (DNP, line 142).
- `blk.gauge`: CHG and DSG left open (no FETs, SLUSE07B §8.3.14); golden image and CC Gain calibration per board (ADR 0017 items 4-5).
- `blk.pwr-3v3-sys`: the Würth 744373240047 inductor land (`T1_Main_Board:L_Wuerth_WE-LHMI_4020`) is not drawn; the data sheet was not retrieved.
- `blk.vdd-cpu`: the XGL4012-221MEC land is taken as the 4020 family's (**UNVERIFIED**).
- `blk.pmic`: BATDIV and SNSP/SNSN wiring (test pads until the reference is read), the 32.768 kHz load capacitors, the RK809-5 OTP defaults (**UNVERIFIED**), PDMCLK left open against BOM line 2's "tied to ground" (it is an output).
- `blk.soc-*`: decoupling of the PHY analog supplies; unused-pin handling (pinout v1 O2); the 24 MHz crystal's load capacitance.
- `blk.lpddr4x`, `blk.emmc`: supply decoupling at the memories (data sheets silent); the DNP TPS7A2018 `vcc1v8_ddr` option (BOM line 132).
- `blk.mclk`: the oscillators' ST input driven at 3.3 V into a 3.1 V supply, and the 45.1584 MHz value on an NDK document (**UNVERIFIED**).
- `blk.dac-l`, `blk.dac-r`: the CS43198 pins' behaviour while unpowered (**UNVERIFIED**); serial-port series values other than 0 Ω are a bring-up choice.
- `blk.hpa-se`, `blk.hpa-bal-*`: the mute shunt footprints (BOM v1 line 100).
- `blk.jack-se`, `blk.jack-bal`: the RF filter footprints near the jacks (PCB-A-19); the 3.5 mm detect switch polarity and the 4.4 mm pin-to-pad assignment (**UNVERIFIED**, check against samples); the Pentaconn alternate land.
