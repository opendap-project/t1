# Controls and status LED

- **Status:** Draft. The structure follows T1-043 and T1-044; timings and colours are proposals to confirm on the first prototypes.
- **Date:** 2026-10-22
- **Applies to:** every T1, whatever the faceplate. Faceplates that add controls report them through the [faceplate interface](faceplate-interface.md); this document covers the four body buttons and the status LED.

## 1. Buttons

The T1 has four body buttons (T1-014, T1-015): **Main** (right edge) and **Action**, **Volume +** and **Volume −** (left edge). The combinations follow Android's conventions, so they are familiar, and they never depend on the faceplate. Their physical form is in §1.4.

### 1.1 Press types

| Press | Duration | Reference |
|---|---|---|
| Short | released before 500 ms | Android long-press timeout (`ViewConfiguration`), proposed value |
| Long | held 500 ms or more | as above |
| Hold | held 2 s or more | proposed, to separate deliberate system actions from long presses |
| Forced power-off | held until the PMIC cuts power | RK809 long PWRON press, handled in hardware without the OS ([RK809-5 sheet](https://github.com/opendap-project/parts-lib/blob/main/Rockchip/RK809-5.md)); the time is a PMIC register setting, value to be fixed in bring-up (**UNVERIFIED**) |

### 1.2 Device off

| Combination | Result | Reference |
|---|---|---|
| **Main**, long | Power on, normal boot | Android power-on |
| **Main + Volume −**, held at power-on | **MaskROM** (USB download over the main USB-C) | Android: Power + Volume Down enters the bootloader/download mode. T1: [board ADR 0009](https://github.com/opendap-project/board/blob/main/docs/adr/0009-bom-v1-decisions.md), BRD-035, implemented in hardware. MaskROM through the buttons needs a full power-off first (a warm restart does not reopen the entry window) and an empty or unbootable microSD slot (board BOM v1.6 line 97; software can still reboot into the loader) |
| **Main + Volume +**, held at power-on | **Recovery** (Blackbird OS recovery; reflash from SD/TF, BRD-043) | Android: Power + Volume Up enters recovery on many devices. BRD-017 (recovery key) |

### 1.3 Device on

| Combination | Result | Reference |
|---|---|---|
| **Main**, short | Screen off / on (playback continues) | Android |
| **Main**, long | Power menu: power off, restart, restart to recovery | Android power menu |
| **Main + Volume −**, short | Screenshot | Android |
| **Main + Volume −**, hold | Power menu (same as Main long), also reachable when the screen is off | maintainers' choice (2026-10-22) |
| **Main**, held until forced power-off | Hardware power-off, works even if the OS is unresponsive | Android forced restart; implemented by the PMIC |
| **Volume + / −**, short | One volume step while sound is playing or the active activity asks for the volume; otherwise they move the focus: Volume − to the next element, like Tab, Volume + to the previous one, like Shift+Tab (system views such as the power menu included). It acts as the button goes down | Android (T1-062); the rule set by the maintainers (2026-10-23) |
| **Volume + / −**, held | Keeps the short press's meaning, repeating it: the volume keeps stepping, or the focus keeps moving, accelerating, and stops where it is released. Never the track | maintainers (2026-10-23 for the focus, 2026-10-26 for the volume) |
| **Volume + / −**, double | Next / previous track while they are the volume (sound playing, the activity asking, or the screen off): the first press stepped the volume at once, and the second, within 300 ms of its release, takes that step back and changes the track. A first press held into its repeat starts no double; a third quick press is a step again. In focus navigation a double press is two focus steps | maintainers (2026-10-26; T1-062, T1-063); Android's double-tap timeout |
| **Action**, short | Follows the focus, which lands on the screen's primary action whenever a screen comes to the foreground, or on its first element where it has none: so the primary action by default; the element the volume buttons moved the focus to once they did; with the focus hidden after a touch, the primary action again where there is one. With the screen off, play / pause of the active media. Action never repeats | The orange primary action on screen (T1-061); focus on entry and the focused-element rule set by the maintainers (2026-10-23) |
| **Action**, long | A direct action the user chooses; default none | T1-061; developer-accessible (BRD-036) |

**Rules:**

- System combinations (with **Main**) cannot be reassigned. The Action long press can.
- Every button works with the screen off, with the same response as with it on (T1-060).
- **Touch with the screen off** (maintainers, 2026-10-24; T1-087): the screen takes no touch, except a double tap, which turns it on (Android's and iOS's tap to wake). Nothing of either tap reaches an activity. Unlocking, where a lock is set, comes after it in the OS Shell. On a touch controller with a low-power gesture mode the double tap can be detected by the controller itself, so the screen's scanning need not stay at full rate; whether the T1's faceplate has one is **UNVERIFIED**.
- No press waits for a later one (T1-063): Action has no double or triple press, and the volume buttons' double press (the track) takes back the step their first press already made.
- Safety-related functions never depend only on software: forced power-off (PMIC) and MaskROM entry (hardware circuit) work with any OS state.
- Volume limits and the hearing-safety dose (SYS-012) apply to button volume changes like any other.

### 1.4 Physical control design

The button design in the [concept art](../concept-art/) governs (T1-059): it is the reference for the form of the controls, and this section describes it. Other details in that concept art are stale (480 × 800 screen, 1.27 mm pins, earlier dimensions) and are not a source. The shared visual language is in the [design system spec](https://github.com/opendap-project/blackbird-ui/blob/main/docs/specs/design-system.md); materials, finishes and manufacturability in the [case industrial-design spec](https://github.com/opendap-project/case/blob/main/docs/specs/industrial-design.md).

Seen from the front:

| Edge | Button | Form | Role |
|---|---|---|---|
| Left, top | **Action** | A round disc, subtly concave: circular outline, shallow comfortable concavity, a defined tactile perimeter with no sharp rim, a stable central contact area. Deeper travel and a clearer click (T1-022). The only control in the orange brand accent. | The main action button: the screen's primary action (§1.3) |
| Left, below Action | **Volume +** and **Volume −** | Two half-capsules: together they form one capsule split across the middle, each half with a rounded outer end and a flat inner edge at the split, operated as two separate buttons. Not a rocker. Short, predictable travel. | Volume steps; long press, previous / next track |
| Right | **Main (power)** | A taller capsule with horizontal ribs for touch identification. Silver-finished, visually quieter than Action. | System button (§1.2, §1.3) |

Volume + / − and Main are silver-finished plastic: a metallic silver paint under a satin clear coat on the polymer cap, with the + and − reliefs in graphite (maintainers, 2026-10-23). Action stays in the orange accent; the body stays graphite.

**Button groups.** The volume pair is the reference instance of the button-group pattern shared by physical and on-screen controls (blackbird-ui DS-013): one capsule split into segments, rounded outer ends, flat inner edges at each split, every segment its own button, with a consistent gap or divider.

**Feedback.** Each button confirms its action through travel, click, shape and position, and through the screen when it is on. A physical action never depends only on a small on-screen animation: with the screen off, volume and playback changes are audible, and the action follows the press within the [experience budgets](experience-budgets.md) (T1-057).

**Distinction by touch.** Disc, split capsule and ribbed capsule differ in shape, position and texture, so each button is found without looking.

## 2. Status LED

The status LED is on the faceplate (FPT-003), RGB where possible (FPT-025), and developer-controllable (FPT-016). The colours follow **IEC 60073** (meanings of colours for indicators), and the on-screen semantic colours use the same families for the same meanings ([design system](https://github.com/opendap-project/blackbird-ui/blob/main/docs/specs/design-system.md) §18.4): red for danger or fault, yellow/amber for an abnormal or warning condition, green for normal, blue for a condition that needs an action, white for neutral information. Patterns follow the same standard's use of flashing to draw attention.

### 2.1 Patterns

| Pattern | Definition (proposed) |
|---|---|
| Solid | On |
| Breathing | Slow fade in and out, 2 s period |
| Slow blink | 1 Hz, 50 % duty |
| Fast blink | 4 Hz, 50 % duty |
| Single pulse | One 100 ms flash |

### 2.2 Base set

Listed by priority: when several states apply, the highest one is shown.

| Priority | State | Colour | Pattern | IEC 60073 meaning |
|---|---|---|---|---|
| 1 | Hardware or thermal fault, unsafe condition | Red | Fast blink | Danger / fault |
| 2 | Battery critically low (5 % or less, discharging) | Red | Slow blink | Danger, action required |
| 3 | Update or flashing in progress: do not power off | Blue | Breathing | Action required (do not interrupt) |
| 4 | Recovery mode | Blue | Solid | Mandatory action context |
| 5 | Music volume handed to a computer: eject before unplugging (blackbird-os ADR 0013) | Blue | Slow blink | Action required (eject first) |
| 6 | Battery low (15 % or less, discharging) | Amber | Slow blink | Warning |
| 7 | Charging | Amber | Solid | Abnormal (not yet ready) |
| 8 | Charged, still on external power | Green | Solid | Normal |
| 9 | Pairing: Bluetooth, or another device through the OpenDAP Protocol | Blue | Fast blink | Action required (pair now) |
| 10 | Syncing or transferring with the screen off | White | Single pulse every 3 s | Neutral information (activity) |
| 11 | Booting | White | Breathing | Neutral information |
| 12 | Developer control (FPT-016) | Any | Any | Defined by the developer |
| — | Normal operation | Off | — | The screen carries normal feedback; the LED stays dark to save power |

**Rules:**

- Battery thresholds: 15 % and 5 %, Android's defaults, the same for the status bar's warnings (2026-10-24).
- Priorities 1–5 cannot be overridden by developer control. Below them, a developer may take the LED through the Linux LED class (`/sys/class/leds`, triggers such as `heartbeat` or `timer`).
- With a single-colour LED (if RGB is not fitted), the base set keeps its meaning through patterns only: fast blink = fault or pairing, slow blink = low battery or eject first, breathing = busy/booting, single pulse = activity, solid = charging or charged.
- Device-to-device states (5, 9, 10) follow the [OpenDAP Protocol](https://github.com/opendap-project/rfcs/blob/main/text/0004-opendap-protocol.md) and the [user-facing conventions](https://github.com/opendap-project/system/blob/main/docs/specs/user-facing-conventions.md): the screen says the same in words whenever it is on. Activity (10) is shown only with the screen off, and the listener can turn it off; calm first.
- MaskROM cannot drive the LED, because no software runs on the SoC; the host tool reports MaskROM instead (`opendap device wait --mode maskrom`).
- The microphone privacy LED is separate, hardware-tied to the microphone power (BRD-027), and never part of this code.

## 3. Open points

- Press durations and LED pattern timings: confirm on the first prototype for feel and readability.
- The PMIC forced power-off time.
- Whether Action + Volume combinations conflict with any faceplate control.
