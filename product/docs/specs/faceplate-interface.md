# Faceplate interface

- **Status:** draft, interface **v1.0** (2026-10-24). Completes the v0 interface: the contacts and their positions are unchanged from pinout v1; the electrical classes, protocol, identification, capabilities, versioning, mechanical parameters and conformance are new. Every decision is in the [decision log](#11-decision-log), the significant ones in [ADR 0004](../adr/0004-faceplate-identity-and-hid-transport.md) and [ADR 0005](../adr/0005-faceplate-supply-classes-and-protection.md). Nothing here is built or measured yet.
- **Requirements:** T1-003, T1-018 to T1-024, T1-036, T1-043, T1-044, T1-059 to T1-063, T1-087; BRD-027, BRD-048, BRD-049; FPT-, FPK- and FPC- requirements of the three faceplates.
- **Decisions:** [ADR 0001](../adr/0001-faceplate-interface-lives-in-t1.md) (this spec lives in t1), [ADR 0002](../adr/0002-faceplate-controls-use-hid-over-i2c.md) (HID over I2C), [ADR 0004](../adr/0004-faceplate-identity-and-hid-transport.md), [ADR 0005](../adr/0005-faceplate-supply-classes-and-protection.md); [RFC 0001](https://github.com/opendap-project/rfcs/blob/main/text/0001-faceplate-interface-v0-pinout.md) (pinout by function).

How a faceplate attaches to the T1. Every faceplate (touch, cassette, classic, …) meets this interface; its own mechanics live in its repository, and the case provides the mount. Faceplates are not meant to be swapped regularly (T1-019), so the interface is kept to one connector, one pinout and screws.

## Summary

- **One connector, one pinout.** Hirose FH35C-51S, 51 contacts: 46 used, 5 reserved. A faceplate connects the groups it needs; the rest stay unconnected on its side.
- **Every faceplate identifies itself** through an HID-over-I2C controller at I2C address 0x2C (vendor ID 0x1209, one pid.codes product ID per model), and describes what it carries in its device description (`opendap.device-description/v1`, layer H3). Blackbird OS enables what the description declares, nothing more and nothing less.
- **Controls are HID usages** from the USB-IF tables; OpenDAP-specific commands live on vendor page 0xFF00.
- **Power is the body's.** The faceplate is powered only through its rails, each with a budget and a fault ceiling; it never back-powers the body. Faceplate rails are off in suspend by default; the body buttons wake the T1.
- **Versioning:** the contacts needed to identify a faceplate never change; minor revisions only add, so any v1 faceplate works on any v1 body for the functions both have.

Terms: the **body** is the T1 without its faceplate (board, case, battery); **core set** means the core HID commands (§4.3).

## 1. Connector and contacts

Defined by function ([RFC 0001](https://github.com/opendap-project/rfcs/blob/main/text/0001-faceplate-interface-v0-pinout.md)). The board maps its SoC pins onto these groups; no SoC pin is part of the interface (hardware-support connector rule). Connector: Hirose FH35C-51S, 0.3 mm pitch, 51 contacts: 46 used, 5 reserved. Contact positions: [board pinout v1 §8](https://github.com/opendap-project/board/blob/main/docs/specs/pinout-v1.md).

| Group | Lines | Contacts | Notes |
|---|---|---|---|
| Display, high speed | MIPI DSI clock ±, data lanes 0–3 ± (or LVDS on the same lines) | 10 | A faceplate uses the lanes its panel needs; a single-lane panel uses contacts 10–16 only |
| I2C | SCL, SDA | 2 | Identity and HID controls (address 0x2C), touch, ambient light sensor, panel |
| SPI/DBI | SCLK, MOSI, MISO, CS#, D/C | 5 | Panels driven over SPI or MIPI DBI |
| Touch | INT, RST# | 2 | |
| Panel | RST#, TE | 2 | |
| Interrupts | HID_INT#, ALS_INT# | 2 | Open drain on the faceplate, pulled up on the board to FP_3V3; HID_INT# is a wake source, ALS_INT# is not |
| Status LED | LED_R, LED_G, LED_B | 3 | Anodes, from constant-current sources on the board; cathodes to faceplate ground (FPT-016, FPT-025) |
| Microphone | PDM_CLK, PDM_DATA | 2 | |
| Detect and spare GPIO | FP_DET#, GPIO0, GPIO1 | 3 | Slow lines |
| Power | FP_3V3 ×2, FP_1V8, FP_VCI, MIC_1V8, BL_LEDA, BL_LEDK | 7 | Backlight driver on the board; the LED string returns through BL_LEDK |
| Ground | Between DSI pairs, group edges, returns | 8 | A faceplate connects every ground contact |
| Reserved | — | 5 | §7.3 |

### 1.1 Contact positions, pinout v1

RFC 0001's group order, each DSI pair between two grounds and lane 0 next to the clock. Numbering follows the Hirose drawing (contact 1's side and the top/bottom row assignment are on the drawing for approval, **UNVERIFIED**).

| Contact | Line | Group |
|---|---|---|
| 1 | GND | Ground |
| 2 | DSI_D3+ | Display |
| 3 | DSI_D3− | Display |
| 4 | GND | Ground |
| 5 | DSI_D2+ | Display |
| 6 | DSI_D2− | Display |
| 7 | GND | Ground |
| 8 | DSI_D1+ | Display |
| 9 | DSI_D1− | Display |
| 10 | GND | Ground |
| 11 | DSI_D0+ | Display |
| 12 | DSI_D0− | Display |
| 13 | GND | Ground |
| 14 | DSI_CLK+ | Display |
| 15 | DSI_CLK− | Display |
| 16 | GND | Ground |
| 17 | I2C_SCL | I2C |
| 18 | I2C_SDA | I2C |
| 19 | SPI_SCLK | SPI/DBI |
| 20 | SPI_MOSI | SPI/DBI |
| 21 | SPI_MISO | SPI/DBI |
| 22 | SPI_CS# | SPI/DBI |
| 23 | DBI_D/C | SPI/DBI |
| 24 | TP_INT | Touch |
| 25 | TP_RST# | Touch |
| 26 | LCD_RST# | Panel |
| 27 | LCD_TE | Panel |
| 28 | HID_INT# | Interrupts |
| 29 | ALS_INT# | Interrupts |
| 30 | LED_R | Status LED |
| 31 | LED_G | Status LED |
| 32 | LED_B | Status LED |
| 33 | GND | Ground |
| 34 | PDM_CLK | Microphone |
| 35 | PDM_DATA | Microphone |
| 36 | FP_DET# | Detect |
| 37 | GPIO0 | Spare GPIO |
| 38 | GPIO1 | Spare GPIO |
| 39 | GND | Ground |
| 40 | MIC_1V8 | Power |
| 41 | FP_1V8 | Power |
| 42 | FP_3V3 | Power |
| 43 | FP_3V3 | Power |
| 44 | FP_VCI | Power |
| 45 | BL_LEDK | Power |
| 46 | BL_LEDA | Power |
| 47 | Reserved | Reserved |
| 48–51 | Reserved | Reserved |

Contact 47, next to BL_LEDA, stays reserved or becomes a ground; it never carries a logic line.

**Identity core.** Contacts 17, 18 (I2C), 28 (HID_INT#), 36 (FP_DET#), 42, 43 (FP_3V3) and every ground: what the body needs to detect and identify any faceplate. They never change in any revision (§7.1).

## 2. Electrical

### 2.1 Signal classes

Levels are the body's: 3.3 V for the low-speed groups, 1.8 V for PDM. A faceplate whose parts need other levels translates on its side, powered from the faceplate rails.

| Group | Direction (body view) | Class | Limits and rules |
|---|---|---|---|
| DSI (or LVDS) | Out | MIPI D-PHY (or LVDS) differential | Faceplate flex **100 Ω ± 10 % differential**, each pair length-matched within itself and referenced to the adjacent grounds. Lane rate is set by the panel (the touch faceplate: one lane at about 337 Mb/s, board BOM line 81); the highest rate the connector and flex carry is measured on the M-UI module (**UNVERIFIED**). Unused lanes unconnected on the faceplate |
| I2C | Bidirectional | 3.3 V open drain, standard and fast mode (≤ 400 kHz) | Pull-ups on the board, on FP_3V3. The faceplate adds no pull-ups and at most **100 pF** of bus capacitance (flex included). Address 0x2C is the identity device's; the faceplate's other addresses are declared in its overlay. No second controller (master) on the bus |
| SPI/DBI | SCLK, MOSI, CS#, D/C out; MISO in | 3.3 V CMOS, single-ended | Clock rate declared in the faceplate's overlay; the interface target is 50 MHz (**UNVERIFIED** until the M-UI module) |
| TP_INT | Bidirectional | 3.3 V CMOS | Bidirectional because some touch controllers sample it as an address strap at reset (GT911) |
| TP_RST#, LCD_RST# | Out | 3.3 V CMOS, active low | Board holds them low while the faceplate rails are off |
| LCD_TE | In | 3.3 V CMOS | Pulled down on the board |
| HID_INT#, ALS_INT# | In | Open drain, active low, 4.7 kΩ pull-up to FP_3V3 on the board | Faceplate sinks ≥ 1 mA at ≤ 0.4 V. HID_INT# is level-triggered (§4.1) |
| LED_R, LED_G, LED_B | Out (current) | Constant-current sources, ≤ 20 mA per channel (device-tree cap), compliance up to 4.55 V | A passive LED with its cathode to faceplate ground; forward voltage ≤ 3.8 V at the declared current. The body may light it with every faceplate rail off (charging in suspend) |
| PDM_CLK | Out | 1.8 V CMOS, about 3 MHz (pinout v1 §8.1) | The microphone declares the clock range it accepts in the description |
| PDM_DATA | In | 1.8 V CMOS | |
| FP_DET# | In | Ground on the faceplate (≤ 100 Ω to GND); pull-up on the board | High = no faceplate |
| GPIO0, GPIO1 | Bidirectional | 3.3 V, slow (I2C GPIO expander on the board), no wake | ≤ 2 mA load; function declared per faceplate in its description |

### 2.2 Supply rails

Budgets are continuous maxima for the whole faceplate, at about 70 % of the derated contact capacity (0.14 A per contact when all contacts carry current, FH35C catalog p. 2); fault ceilings are at or below 100 % of the contact rating (0.2 A per contact). The body enforces the ceilings ([ADR 0005](../adr/0005-faceplate-supply-classes-and-protection.md)).

| Rail | Contacts | Voltage | Faceplate budget | Fault ceiling (body) | Body source today | Capacitance on the faceplate | Notes |
|---|---|---|---|---|---|---|---|
| FP_3V3 | 42, 43 | 3.3 V | 200 mA | ≤ 0.4 A | TPS22919 from vcc3v3_sys, `FP_IO_EN` | ≤ 10 µF | Identity and HID controller, touch, ALS, logic, the microphone privacy indicator. One contact open still keeps 200 mA at the 0.2 A rating |
| FP_1V8 | 41 | 1.8 V | 100 mA | ≤ 0.2 A | TPS22919 from vcc_1v8, `FP_IO_EN` | ≤ 4.7 µF | Panel IOVCC, translators. Follows vcc_1v8, which is off in suspend |
| MIC_1V8 | 40 | 1.8 V | 20 mA | ≤ 0.2 A | TPS22919 from vcc_1v8, `MIC_EN` | ≤ 4.7 µF | Microphones only. A faceplate with a microphone ties its privacy indicator to this rail, so it cannot light without microphone power (BRD-027, Draft) |
| FP_VCI | 44 | 2.8 V default; the faceplate's overlay may set 0.6–3.4 V (RK809 LDO4 range) | 100 mA | ≤ 0.2 A | RK809 LDO4 | ≤ 4.7 µF | Panel analog supply |
| BL_LEDA | 46 | String voltage, ≤ 30 V in every state (§2.3) | 60 mA full scale | ≤ 0.2 A | TPS61169 boost | — | String anode |
| BL_LEDK | 45 | ≈ 0.2 V (feedback) | as BL_LEDA | as BL_LEDA | TPS61169 feedback | — | String cathode only |

Capacitance limits keep the switches' inrush within their soft start; they are provisional until measured on the M-UI module.

The body sets the backlight current (60 mA full scale, dimmed by scaling the reference); Blackbird OS never drives it above the maximum the faceplate's description declares. The same holds for each status LED channel.

### 2.3 Backlight voltage against the connector rating

The FH35C is rated **30 V AC rms** (Hirose FH35C catalog, edition 2013.11, p. 2; [parts-lib sheet](https://github.com/opendap-project/parts-lib/blob/main/Hirose/FH35C-51S-0.3SHW.md)). The touch faceplate's string runs at 14–16.5 V, inside it. The fault case is not: with the TPS61169, an open string drives BL_LEDA to the over-voltage threshold, 36–39 V (SNVSA40B p. 5), and the output capacitor holds it on contact 46 after the driver shuts down. The catalog does not say whether its AC rms figure applies to DC (**UNVERIFIED**).

Interface v1 therefore caps **BL_LEDA at 30 V in every state, fault included**, and a faceplate's string forward voltage at **22 V** at its maximum current (provisional: the chosen driver's minimum threshold less 3 V). Two ways to close it, for the board owner: a backlight driver whose maximum over-voltage threshold is at most 30 V (recommended; the BOM's alternate TPS61160 is listed with a 26 V threshold, limits and land **UNVERIFIED**), or a written DC rating of at least 40 V from Hirose, after which a later ADR may relax the cap.

### 2.4 ESD

| Side | Protects | How |
|---|---|---|
| Body | Every signal contact (10 DSI, 21 low-speed), against discharges that reach the connector through the faceplate and during service with the flex unmated | TVS arrays at the FH35C: TPD4E05U06 ×3 on DSI, ×6 on the low-speed lines (board BOM lines 72, 75), IEC 61000-4-2 level 4 parts |
| Faceplate | Everything a user can touch on it: buttons, dials, switches, metal trim, the cover's edges | Discharge paths to faceplate ground (and to the frame through the anchoring, input from the case) before any interface line; protection on its own control inputs; no user-touchable conductor connected to an interface signal contact |
| Neither | The DSI lines on the faceplate side | No second TVS on DSI: it would double the line capacitance (the HAT standard's rule for its high-speed pairs) |

Mating is a service operation (10 rated cycles, T1-019) done with ESD-safe handling; the faceplate's parts with low ratings (the RGB LED's green and blue dies are rated 150 V HBM, board BOM line 79) are protected in use by the body's arrays.

### 2.5 Power sequencing

**Power-up**, driven by the body:

1. Read FP_DET# (no faceplate rail needed). High: no faceplate; the body stops here (§5.3).
2. `FP_IO_EN` on: FP_3V3 and FP_1V8 rise together.
3. Identity read (§5.2), at most 20 ms after FP_3V3 is in regulation.
4. The panel's own order, from its overlay: FP_VCI, panel reset release, the first frame.
5. Backlight last, after the first frame, so nothing flashes.

MIC_1V8 rises only while a microphone is in use.

**Power-down:** the reverse. The backlight goes off first, then the panel sleeps, then FP_VCI and `FP_IO_EN` go off; the switches discharge their outputs.

**Faceplate tolerance:** a faceplate works with its rails rising in any order and with any subset present, without latch-up, back-powering or drawing above its budget. In particular, FP_VCI may be present before FP_3V3 and FP_1V8 while the RK809's start-up sequence runs, because the RK809-5 OTP defaults are **UNVERIFIED**.

### 2.6 Suspend and wake

As decided on 2026-10-24 (board BOM v1.9 item 3):

- **By default, every faceplate rail is off in suspend.** The body buttons wake the T1 (Main on the PMIC, Action on an always-on ball). HID_INT# reads low with FP_3V3 off and is masked.
- **The hardware can keep FP_3V3 on.** Blackbird OS does so only for a faceplate whose description declares wake-capable controls, and only while the listener enables faceplate wake. In Linux terms: the identity node's `power/wakeup` is disabled by default, so `i2c-hid` releases FP_3V3 in suspend; enabling it keeps the rail on.
- **With FP_3V3 kept on**, FP_1V8 still follows vcc_1v8 and is off. The controller runs from FP_3V3 alone, draws at most **100 µA** from FP_3V3 in the HID SLEEP state with wake armed (about 8 % of the ideal standby drain of 1 % per day on a pack of about 10 Wh, est.; experience budgets), and never feeds the 1.8 V domain.
- **Wake:** a wake-capable control asserts HID_INT#; the body resumes; the controller keeps the report that woke it queued until it is read, so the press also acts (T1-060 applies to faceplate controls the same way).

### 2.7 What a faceplate never does

- **Back-power.** No faceplate part drives any interface contact while its supply is off, and no faceplate output exceeds its rail. No faceplate has another power source (battery, harvester, a regulator fed from a signal line). It never feeds current into a body rail, and never connects two rails together.
- **Draw above its class** on any rail, in any state, inrush included (§2.2).
- **Connect BL_LEDK to ground**, or anything but the string's cathode: BL_LEDK is the driver's feedback, and grounding it drives the string to the over-voltage threshold.
- **Use a reserved contact.** Reserved contacts stay unconnected: not grounded, not tied, not routed.
- **Pull up, terminate or master the faceplate I2C**, or use address 0x2C for anything but the identity device.
- **Mate or unmate with the T1 powered.** The faceplate is attached with the T1 off.

## 3. Identity core rules

Every faceplate, whatever it carries:

1. ties FP_DET# to ground;
2. connects every ground contact;
3. carries the identity device (§4) on FP_3V3, I2C and HID_INT#;
4. has a device description (§6) keyed by its identity.

Everything else is optional and declared.

## 4. Control protocol

Physical controls on a faceplate (buttons, switches, dials) reach Blackbird OS as standardized binary commands, not raw signals (T1-023, T1-024), through **HID over I2C** ([ADR 0002](../adr/0002-faceplate-controls-use-hid-over-i2c.md)): Microsoft's *HID over I2C Protocol Specification* v1.0, read by Linux's mainline `i2c-hid` driver ([binding `hid-over-i2c.yaml`](https://github.com/torvalds/linux/blob/master/Documentation/devicetree/bindings/input/hid-over-i2c.yaml)). The faceplate's controller presents one HID device; `hid-input` turns its core-set reports into standard input events.

### 4.1 Transport parameters

| Parameter | Value | Note |
|---|---|---|
| Bus | Faceplate I2C, contacts 17 and 18, ≤ 400 kHz | §2.1 |
| I2C address (7-bit) | **0x2C** | Fixed, so the body reads the identity without probing. The `hid-over-i2c` binding's example address; clear of the touch (GT911 0x5D, 0x14), the ALS (VEML6030 0x10, 0x48), common OLED controllers (0x3C, 0x3D) and the I2C reserved ranges (0x00–0x07, 0x78–0x7F) |
| HID descriptor register | **0x0001** | `hid-descr-addr = <0x0001>` |
| HID descriptor | 30 bytes, `bcdVersion` 0x0100 | Field order as Linux's `struct i2c_hid_desc`; `i2c-hid` rejects any other `bcdVersion` |
| Interrupt | HID_INT#, contact 28: open drain, **active low, level-triggered** | Asserted while an input report is pending, released once it is read; the `i2c-hid` default trigger is low level |
| Reset | HID-over-I2C RESET command (opcode 0x01); no reset contact | Acknowledged within **50 ms** by asserting HID_INT# with a zero-length input report (`i2c-hid` waits at most 1000 ms). Hard reset: power-cycle FP_3V3 |
| Power states | SET_POWER (opcode 0x08) ON and SLEEP | In SLEEP the controller still answers reads and can assert HID_INT# for wake |
| Ready after power-up | ≤ **20 ms** from FP_3V3 in regulation | Body devicetree `post-power-on-delay-ms = <20>`. After a power cycle the controller works whether or not the host sends RESET: on resume, `i2c-hid` sends only SET_POWER ON |
| Event latency | ≤ **10 ms** from the physical event to HID_INT# assertion, debounce included | Leaves room within the experience budgets (volume input to audible change ≤ 20 ms ideal) |
| Report queue | ≥ 8 input reports; a release is never dropped | No stuck keys after a burst |
| Supply | FP_3V3 only | The `vdd-supply` of the node |

The `hid-over-i2c` node for the identity device belongs to the body's devicetree (layer H1), enabled when FP_DET# reads present ([ADR 0004](../adr/0004-faceplate-identity-and-hid-transport.md)). The faceplate's overlay adds its other parts.

### 4.2 Report descriptor layout

The report descriptor is self-describing, so the interface fixes the collections and report IDs, not the bit order. A faceplate declares only the usages its controls produce.

| Report ID | Type | Application collection | Content | Required |
|---|---|---|---|---|
| 0x01 | Input | Consumer Control (page 0x0C, usage 0x01) | Buttons and switches of the core set, one bit each (logical 0–1), and the absolute Volume (0x0C:0xE0) | Faceplates with controls |
| 0x02 | Input | the same Consumer Control collection | Relative axes of the core set: Wheel (0x01:0x38), Dial (0x01:0x37), AC Pan (0x0C:0x238), signed 8 bit per detent | Faceplates with rotary controls |
| 0x03–0x0F | — | — | Reserved for core-set growth | — |
| 0x10 | Feature (read only) | OpenDAP faceplate (page 0xFF00, usage 0x01) | Identity (§4.5) | Every faceplate |
| 0x11–0x1F | any | OpenDAP faceplate | Extension commands, assigned only through an RFC | — |
| 0x20–0xFF | — | — | Reserved | — |

The controller reports raw states only: press, release, position, detents. Long press, hold, repeat and chords are the composer's (system input events spec §3.3); the controller never synthesizes them, and never emits double or triple presses (T1-063).

Example (informative), a faceplate with play/pause, next, previous, volume up and down and a dial:

```text
05 0C        Usage Page (Consumer)
09 01        Usage (Consumer Control)
A1 01        Collection (Application)
85 01          Report ID (1)
15 00 25 01    Logical Minimum (0), Logical Maximum (1)
75 01 95 05    Report Size (1), Report Count (5)
09 CD 09 B5    Usage (Play/Pause), Usage (Scan Next Track)
09 B6 09 E9    Usage (Scan Previous Track), Usage (Volume Increment)
09 EA          Usage (Volume Decrement)
81 02          Input (Data, Variable, Absolute)
75 03 95 01    Report Size (3), Report Count (1)
81 03          Input (Constant)
85 02          Report ID (2)
05 01 09 37    Usage Page (Generic Desktop), Usage (Dial)
15 81 25 7F    Logical Minimum (−127), Logical Maximum (127)
75 08 95 01    Report Size (8), Report Count (1)
81 06          Input (Data, Variable, Relative)
C0           End Collection
06 00 FF     Usage Page (0xFF00, vendor-defined)
09 01        Usage (OpenDAP faceplate)
A1 01        Collection (Application)
85 10          Report ID (0x10)
09 10          Usage (Identity)
15 00 26 FF 00 Logical Minimum (0), Logical Maximum (255)
75 08 95 08    Report Size (8), Report Count (8)
B1 03          Feature (Constant, Variable, Absolute)
C0           End Collection
```

A faceplate without controls (the touch faceplate) presents the vendor collection alone. Linux then creates no input device for it, only a `hidraw` node.

### 4.3 Core set

USB-IF HID Usage Tables. The Linux event is what mainline `drivers/hid/hid-input.c` produces for each usage (checked 2026-10-21). A faceplate implements the subset that matches its controls.

| Function | Usage page | Usage ID | Usage name | Linux event |
|---|---|---|---|---|
| Play / pause | Consumer (0x0C) | 0xCD | Play/Pause | `KEY_PLAYPAUSE` |
| Play | Consumer | 0xB0 | Play | `KEY_PLAY` |
| Pause | Consumer | 0xB1 | Pause | `KEY_PAUSE` |
| Stop | Consumer | 0xB7 | Stop | `KEY_STOPCD` |
| Next track | Consumer | 0xB5 | Scan Next Track | `KEY_NEXTSONG` |
| Previous track | Consumer | 0xB6 | Scan Previous Track | `KEY_PREVIOUSSONG` |
| Fast forward | Consumer | 0xB3 | Fast Forward | `KEY_FASTFORWARD` |
| Rewind | Consumer | 0xB4 | Rewind | `KEY_REWIND` |
| Record | Consumer | 0xB2 | Record | `KEY_RECORD` |
| Shuffle | Consumer | 0xB9 | Random Play | `KEY_SHUFFLE` |
| Repeat | Consumer | 0xBC | Repeat | `KEY_MEDIA_REPEAT` |
| Volume up | Consumer | 0xE9 | Volume Increment | `KEY_VOLUMEUP` |
| Volume down | Consumer | 0xEA | Volume Decrement | `KEY_VOLUMEDOWN` |
| Mute | Consumer | 0xE2 | Mute | `KEY_MUTE` |
| Volume (absolute knob) | Consumer | 0xE0 | Volume | `ABS_VOLUME` |
| Menu | Consumer | 0x40 | Menu | `KEY_MENU` |
| Select | Consumer | 0x41 | Menu Pick | `KEY_SELECT` |
| Up / down / left / right | Consumer | 0x42–0x45 | Menu Up / Down / Left / Right | `KEY_UP` / `KEY_DOWN` / `KEY_LEFT` / `KEY_RIGHT` |
| Escape | Consumer | 0x46 | Menu Escape | `KEY_ESC` |
| Home | Consumer | 0x223 | AC Home | `KEY_HOMEPAGE` |
| Back | Consumer | 0x224 | AC Back | `KEY_BACK` |
| Forward | Consumer | 0x225 | AC Forward | `KEY_FORWARD` |
| Search | Consumer | 0x221 | AC Search | `KEY_SEARCH` |
| Favorites | Consumer | 0x22A | AC Bookmarks | `KEY_BOOKMARKS` |
| Brightness up / down | Consumer | 0x6F / 0x70 | Display Brightness Increment / Decrement | `KEY_BRIGHTNESSUP` / `KEY_BRIGHTNESSDOWN` |
| Scroll wheel (relative) | Generic Desktop (0x01) | 0x38 | Wheel | `REL_WHEEL` |
| Rotary dial (relative) | Generic Desktop | 0x37 | Dial | `REL_DIAL` |
| Horizontal scroll | Consumer | 0x238 | AC Pan | `REL_HWHEEL` |

A faceplate uses no usage outside this table on the Consumer and Generic Desktop pages, and no other page except 0xFF00. What each control means to the T1 (its role: `action`, `volume-up`, `main`, `back`…) is in the description, not in the usage (§6); Blackbird OS maps codes to roles (system hardware support §4, input events §3.3).

### 4.4 Extensions: vendor page 0xFF00

New commands go on the **OpenDAP vendor-defined usage page, 0xFF00**, in the OpenDAP faceplate collection (usage 0x01), read by Blackbird OS through `hidraw`. Why 0xFF00: mainline `hid-input` ignores that page (`HID_UP_MSVENDOR`, `goto ignore`), while it maps input and output usages on any other unknown page in 0xFF01–0xFFFF to `BTN_MISC`, `ABS_MISC`, `REL_MISC` or `LED_MISC` (torvalds/linux `drivers/hid/hid-input.c` and `include/linux/hid.h`, checked 2026-10-24); OpenDAP commands thus never leak into the input stack as stray events. Other vendors use the same page for their own purposes; its meaning here holds only for a device with an OpenDAP faceplate identity (§5).

| Usage (page 0xFF00) | Name | Status |
|---|---|---|
| 0x01 | OpenDAP faceplate (application collection) | v1.0 |
| 0x10 | Identity (feature report 0x10) | v1.0 |
| 0x11–0x1F | Extension commands | Assigned by RFC |

A command moves to the core set only through an RFC. Candidates, not decided: hold / lock switch, output select, gain, DAC filter, A–B repeat, like.

### 4.5 Identity report

Feature report 0x10, read with GET_REPORT (opcode 0x02) or `HIDIOCGFEATURE` on `hidraw`; 8 bytes after the report ID, little-endian:

| Bytes | Field | Value |
|---|---|---|
| 0 | Interface major | 1 |
| 1 | Interface minor | 0 for this revision |
| 2–3 | Hardware revision | Same as `wVersionID` |
| 4–5 | Firmware version | major × 256 + minor |
| 6–7 | Reserved | 0 |

It exists because `i2c-hid` passes `bcdVersion`, not `wVersionID`, to userspace as the device version (`drivers/hid/i2c-hid/i2c-hid-core.c`, checked 2026-10-24).

## 5. Identification

T1-020: identification relies on the interface pinout; an EEPROM only if the pinout cannot do it. The identity device on the interface's I2C does it, so no EEPROM.

### 5.1 Identity keys

| Field | Content |
|---|---|
| `wVendorID` | **0x1209**, the open-hardware vendor ID allocated by [pid.codes](https://pid.codes/1209/) |
| `wProductID` | One pid.codes PID per faceplate model (touch, cassette, classic, and each later model). Not assigned yet |
| `wVersionID` | Hardware revision of the faceplate: major × 256 + minor |

Routes evaluated (OpenDAP has no USB vendor ID):

| Route | For | Against |
|---|---|---|
| **pid.codes, VID 0x1209** (chosen) | Free, for projects with published, openly licensed hardware and firmware, which OpenDAP is; IDs are the standard 16-bit HID fields that Linux, hwdb and `hidraw` already use | Not endorsed by the USB-IF; its prerequisites mention a device with a USB interface, which the faceplate is not, so the request must explain the HID-over-I2C use |
| USB-IF vendor ID | Universally recognised; would also serve the T1's own USB functions | Paid, and a project-level commitment: a maintainers' call |
| A microcontroller maker's PID programme | Low or no cost | Ties the identity to one silicon maker's controller, against the interface's part freedom |
| Unregistered numbers | None | Collide silently with other devices |

pid.codes reserves 0x0001–0x0010 as test PIDs: usable in private testing only, never on a device that is redistributed, sold or manufactured. Faceplates use them up to quality level Q1 (RFC 0010); from Q2 on, a faceplate carries its granted PID.

### 5.2 How Blackbird OS maps the identity to the description

1. **Presence.** FP_DET# low.
2. **Power.** `FP_IO_EN` on; wait for the ready time (≤ 20 ms).
3. **Read the HID descriptor** at 0x2C, register 0x0001, 30 bytes: check `wHIDDescLength` = 30 and `bcdVersion` = 0x0100; take `wVendorID`, `wProductID`, `wVersionID`. This read needs no driver, so it can happen before the display is brought up; where Blackbird OS does it (bootloader or early boot) is its choice.
4. **Resolve the description** `opendap.device-description/v1`, kind `faceplate`, keyed by `1209:<pid>` and a hardware-revision range: an L2 package for known faceplates, a signed L6 registry artifact for new ones (system hardware support §5). The description names the devicetree overlay against the faceplate connector.
5. **Apply the overlay** and bind the faceplate's drivers. `i2c-hid` binds the identity node; its uevent carries `HID_ID=0018:00001209:0000<pid>` (bus I2C), which hwdb and the component services match.
6. **Check** the identity report (interface major 1, hardware revision equal to `wVersionID`) and the compatibility of the description's `provides` with the running release (system hardware support §7).
7. **Publish** the capabilities (§6) in `org.opendap.device.Capabilities`.

### 5.3 When identification fails

| Case | Body behaviour |
|---|---|
| FP_DET# high | No faceplate. Faceplate rails stay off; capabilities report display, touch, faceplate controls, status LED, ALS and faceplate microphone as `absent` |
| FP_DET# low, nothing answers at 0x2C | Non-conformant faceplate. Only FP_3V3 and FP_1V8 were powered; they are switched off again and the reason is reported (`opendap` CLI, logs). The status LED, on the body's driver, can still show states |
| Identity read, no description found | Unknown faceplate. The core set still works through generic `i2c-hid` (events without roles until a description gives them); no panel is driven; the identity is reported so a description can be added |
| Interface major other than 1 | The body powers nothing beyond the identity core and reports the mismatch (§7.2) |

An owner override (L7) may name a description for a faceplate under development; it is documented and visible, never silent.

## 6. Capabilities

What a faceplate carries is declared once, in its device description (system [hardware support](https://github.com/opendap-project/system/blob/main/docs/specs/hardware-support.md) §3), so Blackbird OS adapts to it (SYS-040, T1-045) and nothing about a faceplate is hard-coded (§9 of the same spec). The device never reports capabilities over HID beyond its identity.

| Capability | Description section | What the faceplate declares | When absent |
|---|---|---|---|
| Identity | `identity` | Kind `faceplate`, `1209:<pid>`, hardware-revision range, interface revision, maker | Not allowed: every faceplate has one |
| Outline and front | `layout` | Outline in mm in the T1 coordinate system (T1-021), the display's visible area, shape, corner radii and cutouts, and its position on the front | — |
| Display | `display` | Technology, physical size, refresh, distance class; the overlay names the panel, its bus (DSI lanes, LVDS or SPI/DBI), FP_VCI voltage and power sequence | `display` omitted: Blackbird OS uses the no-display layout class (hardware support §6). All three official faceplates have a display (FPT-014, FPK-004, FPC-004) |
| Backlight | `display` | String: present or none, maximum current (≤ 60 mA), forward voltage at that current (≤ 22 V) | None (an emissive display): the body keeps the backlight driver off |
| Touch | `touch` | `resolution_x`, `resolution_y`, `contacts`; the overlay names the controller and its address | Touch input profile not offered |
| Controls | `controls` | Per control: kind, HID usage and the Linux code it produces, semantic role, wake-capable or not, position, size, shape and tactile marks | Only the body buttons |
| Status LED | `indicators` | Role `status`, RGB or one colour, which LED contacts are connected, maximum current per channel (≤ 20 mA), forward voltage | The body's LED driver stays off (FPT-003 requires one on the touch faceplate) |
| Ambient light | `sensors` | Kind `ambient-light`, the IIO device name, whether ALS_INT# is connected | Fixed brightness curve, user-set |
| Microphone | `audio` | Per microphone: PDM, the clock range it accepts, its position; the privacy indicator tied to MIC_1V8 | Recording sources from the body only |
| Spare GPIO | `controls` or `indicators`, by function | What GPIO0 and GPIO1 do, if anything | Inputs with pulls on the body |
| Power | `power` | Per rail: typical and maximum current, maximum in suspend with wake armed (FP_3V3 ≤ 100 µA) | — |
| Interfaces provided | `provides` | `org.opendap.hw.*` interfaces and versions (Display, Controls, Led…) | — |

The description schema has no section named for microphones or for a faceplate's per-rail power yet; the rows above use `audio` and `power`, to be confirmed by the system spec's owner (§10).

## 7. Versioning and compatibility

### 7.1 Revisions

- **Interface revision:** major.minor, reported in the identity report. This spec is **1.0**.
- **Identity invariant:** the identity core (§1.1), the identity device's address, descriptor register and identity report never change, in any major revision. Any body can always tell what a faceplate is.
- **Minor revision (1.x):** only adds: new core-set usages, new vendor commands (report IDs 0x11–0x1F), new description fields, tighter limits. It never changes a contact's position or class, and never assigns a reserved contact (§7.3). Anything a minor revision adds must be safe when the other side does not know it.
- **Major revision (2.0):** anything else; only through an RFC.
- **Faceplate hardware revision** (`wVersionID`) is the faceplate's own; descriptions cover ranges of it.
- **v0 to v1:** v0 defined the same contacts by function and pinout v1 their positions; no faceplate was built to v0, so v1.0 replaces it with no contact change.

### 7.2 Body and faceplate of different revisions

| Case | What happens |
|---|---|
| Same major, faceplate older (1.x on a 1.y body, x < y) | Works. Functions added after 1.x are absent from the capabilities |
| Same major, faceplate newer (1.y on a 1.x body) | Works for the functions of 1.x. The faceplate's later additions stay unused; Blackbird OS reports them as unsupported by this body |
| Different major | The body powers nothing beyond the identity core and reports the mismatch, with the faceplate's and the body's revisions |
| Description newer than the running Blackbird OS | Checked like any hardware attach (hardware support §7): reported with its reason, never silently half-enabled |

### 7.3 Reserved contacts

- 5 of 51 contacts are reserved: **9.8 %**. The floor is **8 %**, this interface's own rule (taken on 2026-10-24 from the HAT standard's interface v1 rule per level, hat-standard ADR 0002 and ADR 0003; HAT interface v2 is USB only and has no reserved contacts or levels, hat-standard ADR 0006, so the rule now stands on its own here), which also meets board ADR 0006's "at least about 10 %" as BOM line 71 records it. 8 % of 51 is 4.1 contacts, so the floor is **5 contacts**: today's count.
- Consequence: **no 1.x revision assigns a reserved contact.** Interface v1 evolves through what needs no contact: the spare GPIO (whose function each faceplate declares), devices on the faceplate I2C, and vendor commands. Assigning a reserved contact is a major revision, or comes with a connector that restores the floor.
- Contact 47 may only become a ground; it never carries a logic line (it sits next to BL_LEDA).
- Reserved contacts are unconnected on both sides (§2.7).

### 7.4 No compatibility levels

HAT interface v1 had levels because a HAT could carry only a zone of its contacts; HAT interface v2 is one USB port with no levels (hat-standard ADR 0006). A faceplate always mates the whole connector, so interface v1 has one pinout, one mandatory part (the identity core rules of §3) and everything else optional and declared. A faceplate with only controls and an LED and one with a 4-lane display are equally conformant; what differs is their description. Whether a faceplate has a display is a product rule of each faceplate (FPT-014, FPK-004, FPC-004), not an interface level.

### 7.5 Can the pinout be reduced?

No, with these numbers:

- **Use today.** 46 used: 10 DSI, 8 ground, 21 low-speed, 7 power. The touch faceplate uses 32 contacts (DSI lane 0 and clock, every ground, I2C, touch, LCD_RST#, both interrupts, LED, PDM, FP_DET#, every supply). Not used by any defined faceplate yet: DSI lanes 1–3 (6), SPI/DBI (5), LCD_TE (1), GPIO0–1 (2): 14 contacts.
- **Those 14 are required.** T1-036 and BRD-048 (both must) ask for almost any display and touch connection standard: multi-lane DSI for larger or faster panels, SPI/DBI for small panels, many small OLEDs among them (the classic and cassette faceplates will most likely use OLED or AMOLED, FPK-007, FPC-007), TE for command-mode panels. The HAT reduction removed groups with no must behind them; here every group has one.
- **Grounds are at the minimum.** Five DSI pairs between six grounds is already the shared-guard minimum (one ground per pair, plus one); the other two separate PDM from the LED lines and the supplies from the low-speed group.
- **A smaller connector does not fit.** The next size in the BOM history is 45 contacts (BOM line 71, "45 → 51"): 46 used contacts do not fit, and dropping six would take the reserve below the floor or remove a required group.

Positions stay as pinout v1: no change is clearly better.

## 8. Mechanical interface

Values are given in the T1 coordinate system (T1-021: origin at the device centre, x across the width, y along the length, +z towards the faceplate; general tolerances ISO 2768-m). What the case decides is marked as such; nothing here invents mechanics.

| Parameter | Value | Status | Source |
|---|---|---|---|
| Body outline | 59.5 × 94.3 × 25.0 mm (tentative) | Defined (tentative) | t1 ADR 0003, board ADR 0016 |
| Faceplate outline and front-face z | — | Input from the case | case scope (case ADR 0003) |
| Connector | FH35C-51S-0.3SHW on the board's front side | Defined | Board BOM line 71 |
| Connector location | In the faceplate connection area, about 10 × 54 mm at the display's bottom edge (front zone PCB-Z-03); x, y and orientation of contact 1 | Area defined, size to confirm; position input from board placement and the case | Board ADR 0016 item 1 |
| Connector body | 16.9 mm wide (51 contacts), 3.0 mm deep (3.2 mm with actuator), 0.9 ± 0.1 mm high; back-flip actuator opens to 90°, 1.8 mm high open (reference) | Defined | FH35C catalog p. 3 |
| Actuator access during assembly | Room to open and close the actuator with the tail inserted | Input from the case (assembly sequence) | — |
| Contact 1 side and row assignment | — | **UNVERIFIED** (Hirose drawing for approval) | Parts-lib FH35C sheet |
| FPC tail at the mating area | 0.2 ± 0.03 mm thick, gold-plated contacts; width 15.6 ± 0.05 mm with stiffener film; dimension N ≥ 0.5 mm; on a double-sided flex, no back-side copper in the mating area | Defined | FH35C catalog pp. 2, 5, 6 |
| DSI pairs on the connector | Each pair on contacts of the same row | Defined | FH35C catalog p. 1, feature 3 |
| Flex impedance | DSI 100 Ω ± 10 % differential | Defined | §2.1 |
| Flex length, fold and routing | — | Input from the faceplate's mechanics and the case | — |
| Display-to-board gap | 1.3 mm. Nothing of the faceplate enters it except the tail and its stiffener at the connector | Defined | Board ADR 0016 |
| Board parts under the display (front zone PCB-Z-03) | ≤ 1.0 mm, FH35C included; no shield cans | Defined | Board ADR 0016 |
| Faceplate stack above the gap | Touch faceplate reference: lens and OCA 0.9 mm, display 5.5 mm. Any faceplate: up to the front face set by the case | Reference defined; limit input from the case | Board ADR 0016 consequences |
| Front zone outside the display footprint (PCB-Z-04) | Gap + module = 6.8 mm where the faceplate frame leaves room | **UNVERIFIED** until the faceplate mechanics | Board ADR 0016 |
| Anchoring | Screws (CASE-024, must): count, size and positions | Input from the case (CASE-018's four M1.6 screws was withdrawn) | Case requirements |
| Alignment features | — | Input from the case | — |
| Ground bond to the frame (ESD path) | — | Input from the case | §2.4 |
| Sealing at the faceplate (IP65 target of the Commercial edition, T1-017, should, Draft) | — | Input from the case | — |
| Mating cycles | 10 rated; a service operation | Defined | FH35C catalog p. 2; T1-019 |

## 9. Conformance

The rows a faceplate passes, for `toolkit-verify`. Each carries the RFC 0010 quality level at which it becomes mandatory; a faceplate's build declares its target level and passes every row at or below it. Fixtures: `faceplate-emu` (UHID) at L1; a reference body or a faceplate test fixture with per-rail current measurement at L3 and above.

| ID | Level | Area | Test | Pass |
|---|---|---|---|---|
| FI-E01 | Q0 | Electrical | Current on each rail in every operating state, start-up included | Within §2.2 budgets |
| FI-E02 | Q0 | Electrical | Back-power: each rail off in turn and all off; every signal contact driven to its class high level through 1 kΩ | No rail above 0.3 V; ≤ 10 µA into any contact |
| FI-E03 | Q0 | Electrical | BL_LEDK continuity to ground; string forward voltage at the declared maximum current | No path from BL_LEDK to ground except through the string; VF ≤ 22 V |
| FI-E04 | Q0 | Electrical | Reserved contacts | > 10 MΩ to every other contact |
| FI-E05 | Q1 | Electrical | Capacitance on each rail | Within §2.2 |
| FI-E06 | Q1 | Electrical | FP_DET# to ground | ≤ 100 Ω |
| FI-E07 | Q1 | Electrical | Open-drain lines | VOL ≤ 0.4 V at 1 mA; no pull-up on the faceplate |
| FI-E08 | Q1 | Electrical | Faceplate I2C | No pull-ups (> 100 kΩ to any rail); ≤ 100 pF; correct operation at 400 kHz |
| FI-E09 | Q1 | Electrical | Rails in any order and any subset, FP_VCI first included | No latch-up; budgets held |
| FI-E10 | Q1 | Electrical | Status LED forward voltage per channel at the declared current | ≤ 3.8 V |
| FI-E11 | Q2 | Electrical | DSI flex impedance (TDR) | 100 Ω ± 10 % differential |
| FI-E12 | Q2 | Electrical | Suspend draw with FP_3V3 kept on, FP_1V8 off, wake armed (faceplates declaring wake) | ≤ 100 µA |
| FI-P01 | Q1 | Protocol | HID descriptor at 0x2C, register 0x0001 | 30 bytes, `wHIDDescLength` 30, `bcdVersion` 0x0100 |
| FI-P02 | Q1 | Protocol | Report descriptor | Parses (kernel and `hid-tools`); collections and report IDs per §4.2; identity collection present |
| FI-P03 | Q1 | Protocol | Usages | Only core-set usages on pages 0x0C and 0x01, and page 0xFF00; nothing else |
| FI-P04 | Q1 | Protocol | Each declared control | The declared Linux event, once per action (L1 through UHID, L3 on real `i2c-hid`) |
| FI-P05 | Q1 | Protocol | RESET | Acknowledged within 50 ms with a zero-length input report |
| FI-P06 | Q1 | Protocol | Ready after power-up; resume with SET_POWER ON only, no RESET | Descriptor readable ≤ 20 ms; reports flow after resume |
| FI-P07 | Q1 | Protocol | Interrupt behaviour | Level low while a report is pending, released after it is read; no assertion without a report |
| FI-P08 | Q1 | Protocol | Bursts | 8 queued reports delivered in order; no release dropped |
| FI-P09 | Q2 | Protocol | Event latency | ≤ 10 ms from the physical event to HID_INT#; ≤ 5 ms at Q4 |
| FI-P10 | Q2 | Protocol | Wake (faceplates declaring wake) | A wake-capable control wakes the T1 and its press acts once |
| FI-I01 | Q1 | Identification | `wVendorID`, `wProductID` | 0x1209 with a pid.codes test PID (Q0–Q1) or the model's granted PID |
| FI-I02 | Q2 | Identification | Product ID | Granted pid.codes PID; no test PID |
| FI-I03 | Q1 | Identification | Identity report | Interface major 1; hardware revision equal to `wVersionID` |
| FI-I04 | Q1 | Identification | Identity with only the identity core powered | Readable with FP_1V8, FP_VCI, MIC_1V8 and the backlight off |
| FI-I05 | Q1 | Identification | Description | Validates against the schema; resolved from the identity; every declared capability present on the hardware and nothing undeclared |
| FI-S01 | Q1 | ESD | User-touchable conductors | None connected to an interface signal contact; each bonded to ground |
| FI-S02 | Q2 | ESD | IEC 61000-4-2 at every user-touchable point, faceplate on a reference body | ±4 kV contact, ±8 kV air, criterion B (as t1 V5-02) |
| FI-S03 | Q4 | ESD | As FI-S02 | ±8 kV contact, ±15 kV air, criterion B |
| FI-M01 | Q1 | Mechanical | FPC tail | §8 tail dimensions, stiffener, no back copper in the mating area |
| FI-M02 | Q1 | Mechanical | z envelope | Nothing in the 1.3 mm gap except the tail; stack within the case's envelope |
| FI-M03 | Q2 | Mechanical | Anchoring and alignment | Per the case's values (once defined) |

## 10. Changes other repositories need

Not made here.

**Board** (BOM, power tree, pinout, feature blocks):

| # | Change | Why |
|---|---|---|
| BC1 | FP_3V3: replace the TPS22919 with a current-limited switch, maximum trip ≤ 0.4 A, minimum trip above the 200 mA budget (BOM line 50, power tree §3, §5) | §2.2, ADR 0005: the TPS22919 limits at 30–900 mA on a hard short and about 3 A on a soft one |
| BC2 | FP_1V8 and MIC_1V8: current-limited switches, maximum trip ≤ 0.2 A | As BC1 |
| BC3 | FP_VCI: confirm RK809 LDO4's current limit is ≤ 0.2 A, or add a limit; confirm the RK809-5 OTP state of LDO4 at power-up | §2.2, §2.5 |
| BC4 | Backlight: keep BL_LEDA ≤ 30 V in every state: a driver with a maximum over-voltage threshold ≤ 30 V (BOM line 51; alternate TPS61160 listed at 26 V, limits and land **UNVERIFIED**; its rectifier and output capacitor re-rated), unless Hirose confirms a DC rating ≥ 40 V. Power tree §4.5 and `blk.fp-backlight`: string forward voltage ≤ 22 V instead of "up to about 10 series LEDs" | §2.3, ADR 0005 |
| BC5 | Board devicetree: the identity node, `hid-over-i2c` at 0x2C on the faceplate I2C, `hid-descr-addr = <0x0001>`, interrupt `FP_HID_INT_N` level-low, `vdd-supply` FP_3V3, `post-power-on-delay-ms = <20>`, wakeup disabled by default; `blk.fp-controls` software field | §4.1, ADR 0004 |
| BC6 | I2C3 pull-ups on FP_3V3 sized for 400 kHz with up to 100 pF from the faceplate | §2.1 |
| BC7 | BOM faceplate lines: the touch faceplate's identity controller (HID over I2C, from FP_3V3); part chosen with faceplate-touch | §3, ADR 0004 |
| BC8 | Pinout v1 §8 and `blk.fp-connector`: "interface v0" becomes "interface v1"; no contact moves | §7.1 |

**Others:** faceplate-touch: identity controller and firmware, tail per §8, ESD of its touchable surfaces, description; faceplate-classic and faceplate-cassette: the same rules when designed. System: name the description sections for microphones and per-rail faceplate power, and the identity flow of §5.2 in the hardware support spec. Parts-lib: the FH35C sheet still says 44 used and 7 spare (now 46 and 5), and the GT911 sheet's unassigned HID address is now 0x2C. toolkit-verify: the rows of §9. Maintainers: the pid.codes request (§5.1).

## 11. Decision log

All decided on 2026-10-24, D6's default earlier the same day.

| # | Decision | Why | Record |
|---|---|---|---|
| D1 | Interface v1.0 (Draft); contacts and positions unchanged from pinout v1 | Nothing built to v0; positions already reviewed | §7.1 |
| D2 | Signal classes per group, including I2C ≤ 400 kHz with ≤ 100 pF and no faceplate pull-ups, DSI flex 100 Ω ± 10 % | One electrical contract every faceplate can be checked against | §2.1 |
| D3 | Rail budgets at about 70 % of the derated contact capacity, fault ceilings ≤ 100 % of the rating, enforced by the body | BRD-049; the TPS22919 does not limit to the contact rating | ADR 0005 |
| D4 | BL_LEDA ≤ 30 V in every state; string ≤ 22 V | Open-string voltage 36–39 V against a 30 V AC rms rating with no stated DC figure | ADR 0005 |
| D5 | ESD: the body protects every signal contact; the faceplate protects its touchable surfaces; no second TVS on DSI | Each side protects what it exposes; capacitance on the pairs | §2.4 |
| D6 | Faceplate rails off in suspend by default, body buttons wake, FP_3V3 kept on only for declared wake with the listener's consent; ≤ 100 µA kept-on draw; the controller runs from FP_3V3 alone | Maintainers' decision of 2026-10-24 (board BOM v1.9 item 3); standby budget | §2.6 |
| D7 | Rails tolerate any order; FP_VCI may come first | RK809-5 OTP defaults unknown | §2.5 |
| D8 | Identity device on every faceplate, I2C 0x2C, descriptor register 0x0001, no reset contact, ready ≤ 20 ms, reset ack ≤ 50 ms | Identification without probing; T1-020 without an EEPROM; `i2c-hid` behaviour | ADR 0004 |
| D9 | Vendor page 0xFF00 | Ignored by mainline `hid-input`; any other vendor page leaks `*_MISC` events | ADR 0004 |
| D10 | VID 0x1209 through pid.codes, one PID per model; test PIDs up to Q1; `wVersionID` = hardware revision; identity feature report 0x10 | No OpenDAP VID; Linux hides `wVersionID` | ADR 0004 |
| D11 | Report IDs: 0x01 buttons, 0x02 relative axes, 0x10 identity, 0x11–0x1F extensions; raw states only | Stable layout; long press and repeat belong to the composer (T1-063) | §4.2 |
| D12 | Event latency ≤ 10 ms (5 ms at Q4) | Volume input to audible change ≤ 20 ms ideal | §4.1 |
| D13 | Capabilities only in the description | Hardware support §3; one source of truth | §6 |
| D14 | Identity invariant; minor revisions only add; reserved floor 5 contacts (8 %), so v1.x never assigns one | The 8 % rule of §7.3 (from HAT interface v1); any body can always identify any faceplate | §7 |
| D15 | No compatibility levels | The whole connector is always mated | §7.4 |
| D16 | Pinout not reduced; positions unchanged | Every group is required by T1-036 and BRD-048 | §7.5 |
| D17 | Mechanical values: defined only where a source fixes them; the rest is input from the case | No invented mechanics | §8 |

## 12. Open items

- The pid.codes PIDs: the request, under the project's name, is the maintainers' (and, if declined, the choice of fallback).
- FH35C DC voltage rating, and the backlight driver change (BC4).
- The RK809 LDO4 current limit and the RK809-5 OTP defaults (BC3).
- The highest DSI lane rate and SPI clock the connector and flex carry: measured on the M-UI module.
- Rail capacitance limits: confirmed against the chosen current-limited switches.
- Contact 1 side and row assignment from the Hirose drawing.
- Every "input from the case" row of §8.
- Description sections for microphones and per-rail power (system).
