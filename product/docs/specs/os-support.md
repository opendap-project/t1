# T1 support in Blackbird OS

- **Status:** Draft.
- **Date:** 2026-10-26
- **Applies to:** the Blackbird OS image for the T1, through the T1's board support package ([Blackbird OS](https://github.com/opendap-project/blackbird-os) OS-004).
- **Sources:** the [board BOM v1.5](https://github.com/opendap-project/board/blob/main/docs/specs/bom-v1.md), [board ADR 0014](https://github.com/opendap-project/board/blob/main/docs/adr/0014-two-cell-battery.md).

What the T1's hardware needs from the image, beyond the generic Blackbird OS. Generic rules (mainline kernel, drivers through DKMS while upstream review runs) are Blackbird OS requirements; this document lists only the T1's parts.

## Kernel modules

DKMS modules ([Blackbird OS ADR 0007](https://github.com/opendap-project/blackbird-os/blob/main/docs/adr/0007-kernel-modules-through-dkms.md)):

| Module | Part | Note |
|---|---|---|
| `cs43130` | CS43198 DACs | |
| `bq27xxx_battery` with its I2C front end | BQ28Z610-R1 fuel gauge | `BATTERY_BQ27XXX_I2C` is not set in Debian's arm64 kernel |
| `bq257xx` (MFD and charger) | BQ25798 charger | `MFD_BQ257XX` and `CHARGER_BQ257XX` are not set in Debian; the BQ25798 device ID is added until upstream accepts it (board ADR 0014, Blackbird OS OS-023) |
| `nxpwifi`, `btnxpuart` | IW612 | |
| `panel-ilitek-ili9488` | touch faceplate display | Until Debian ships a kernel ≥ 7.3 |

## Driver and firmware settings

- **BQ25798 charger.** The mainline `bq257xx` charger init disables the charger watchdog (REG10 = 0), so settings persist if Linux hangs and there is no fallback to the power-on defaults; the board reviews this under BRD-049. The device tree must not describe the charger's OTG output.
- **INA236 current monitors.** They power up converting continuously; they are configured at boot.
- **RP2354A coprocessor.** Its firmware must select 1.8 V I/O (`VOLTAGE_SELECT = 1`).
