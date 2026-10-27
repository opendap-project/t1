# Experience budgets

- **Status:** Draft. The structure is confirmed (T1-048); the values are proposals to confirm and to calibrate on the first prototype. Where the hardware allows better, the target moves up (T1-045).
- **Date:** 2026-10-22
- **Rule:** each metric has an **ideal** value (the target), a **warning** value (investigate before release) and a **hard limit** (the release does not ship). Every metric is measured by an automated test on the virtual T1 and, where it depends on hardware, on the device (TK-016, TK-017).
- **Sources:** the T1 requirements, the board power tree and the user-experience work behind them. Values without a source are engineering proposals and say so.

## Start-up and responsiveness

| Metric | Ideal | Warning | Hard limit | Basis |
|---|---|---|---|---|
| Cold boot to first sound (resume last track) | ≤ 10 s | > 15 s | > 25 s | Proposal; time to first track is a moment of truth |
| Screen on (from off) to interactive | ≤ 150 ms | > 300 ms | > 600 ms | Proposal |
| Button press to action (play, pause, volume) | ≤ 50 ms | > 100 ms | > 200 ms | Proposal; about 100 ms is where delay becomes noticeable |
| Touch to visual response | ≤ 50 ms | > 100 ms | > 150 ms | Proposal |
| UI frame rate (scrolling, transitions, animations), under any background load | 60 fps (display refresh) | < 55 fps, or any dropped-frame burst | < 50 fps | T1-056, SYS-036 |
| Track change gap (same format) | 0 samples | — | > 0 samples | Gapless is exact or it fails |
| Volume input to audible change | ≤ 20 ms | > 50 ms | > 100 ms | T1-057, SYS-037: volume set in the DAC register (proposal) |
| Play or resume input to first sound | ≤ 100 ms | > 200 ms | > 400 ms | T1-057 (proposal) |
| Pause input to silence | ≤ 50 ms | > 100 ms | > 200 ms | T1-057, SYS-037 (proposal) |
| Seek or track skip to new audio | ≤ 150 ms | > 300 ms | > 600 ms | T1-057, SYS-037 (proposal) |
| Interface state vs device state | always equal | any visible mismatch | any mismatch that persists | T1-057 |

## Library scale

| Metric | Ideal | Warning | Hard limit | Basis |
|---|---|---|---|---|
| Library size handled without degradation | no fixed limit, tested at 1,000,000 tracks | tested below 500,000 | any fixed cap, or tested below 200,000 | T1-046 |
| Open a list or view (any library size) | ≤ 200 ms | > 400 ms | > 1 s | Proposal; SYS-033 |
| Search results (500,000 tracks) | ≤ 100 ms | > 300 ms | > 1 s | Proposal |
| Incremental rescan after adding 1,000 files | ≤ 10 s, in the background | > 30 s | blocks playback or the UI | Proposal; LB requirements |
| Start-up cost of the library (any size) | none (no rebuild at boot) | > 1 s | > 5 s | T1-047: no database rebuild at power-on |

## Audio output

| Metric | Ideal | Warning | Hard limit | Basis |
|---|---|---|---|---|
| Output impedance | ≤ 0.5 Ω | > 1 Ω | > 2 Ω | Proposal; one-eighth of a 16 Ω IEM is 2 Ω |
| Volume step | ≤ 0.5 dB | > 1 dB | > 2 dB | DAC volume resolution |
| Channel balance at low volume | ≤ 0.1 dB | > 0.3 dB | > 1 dB | Proposal; volume in the DAC |
| Audible pops and clicks at any transition | none | — | any | Proposal |
| Bit-perfect on every declared path | 100 % | — | any failure | OS-020 |

Noise floor into sensitive IEMs, distortion and output power are set from the first prototype's measurements against ADR 0012's design figures.

## Power

| Metric | Ideal | Warning | Hard limit | Basis |
|---|---|---|---|---|
| Playback autonomy (core session) | > 12 h | < 8 h | < 6 h | T1-039 |
| Standby drain | ≤ 1 % per day | > 3 % per day | > 5 % per day | Proposal |

## Radio

Draft until calibrated on the first prototype and on the benchmark set. Each row names its course: LOS (line of sight), W1 and W2 (through one and two interior walls), BODY (on the body) and COEX (with Wi-Fi active); dropouts and latency are measured on the same course for every device. Every row also holds against the median of the dated benchmark set (commercial Digital Audio Players, phones as a reference) measured on the same course: ideal ≥ 2× (latency ≤ 0.5×), warning below 1.5× (latency above 0.67×), hard limit at or below 1.0× (latency at or above 1.0×). Results state the variant and the certified transmit power it ran with (T1-075).

| Metric | Ideal | Warning | Hard limit | Basis |
|---|---|---|---|---|
| Bluetooth audio on the body: T1 in a front, then back, trouser pocket, reference headphones worn, 30 min each, LDAC 990 kb/s held (BODY) | 0 dropouts | any dropout | > 3 dropouts in 30 min | Proposal; a phone in a pocket swings 15–20 dB with body orientation |
| Bluetooth range, line of sight, LDAC 990 kb/s held, no dropout (LOS) | ≥ 15 m | < 10 m | < 5 m | Proposal; LDAC 990 and 660 kb/s need about −60 dBm at the headphones |
| Bluetooth range, line of sight, LDAC adaptive, no dropout (LOS) | ≥ 40 m | < 25 m | < 15 m | Proposal; 330 kb/s holds to about −80 dBm |
| Bluetooth range through one interior wall, LDAC adaptive, no dropout (W1) | ≥ 20 m | < 12 m | < 8 m | Proposal; wall loss measured and recorded |
| Bluetooth range through two interior walls, LDAC adaptive, no dropout (W2) | ≥ 12 m | < 8 m | < 5 m | Proposal; wall losses measured and recorded |
| Bluetooth audio with Wi-Fi streaming 20 Mb/s on the same T1, LDAC 990 kb/s, 3 m, 60 min, Wi-Fi on 2.4 then 5 GHz (COEX) | 0 dropouts | — | any dropout | Board ADR 0018 coexistence gate |
| Wi-Fi TCP downlink, 5 GHz 80 MHz, 1 m line of sight | ≥ 350 Mb/s | < 250 Mb/s | < 150 Mb/s | Murata: 384 Mb/s TCP at about 0.9 m (E2B-09-1413 Table 25); SDIO 3.0 bound |
| Wi-Fi TCP downlink, 10 m through one wall (W1) | ≥ 200 Mb/s | < 120 Mb/s | < 60 Mb/s | Proposal |
| Wi-Fi TCP downlink, 15 m through two walls (W2) | ≥ 100 Mb/s | < 50 Mb/s | < 25 Mb/s | Proposal; 2×2 phones carry 150–160 Mb/s at 15 m through walls (reference, not target) |
| Range with sustained TCP ≥ 20 Mb/s, two-wall course extended (W2) | ≥ 25 m | < 18 m | < 12 m | Proposal; lossless hi-res streaming with margin |
| Bluetooth audio latency, A2DP (SBC, AAC, LDAC), reference headphones | ≤ 150 ms | > 200 ms | > 300 ms | Android phones average 308–369 ms by codec (SoundGuys) |
| Bluetooth audio latency, LE Audio (LC3), when supported | ≤ 60 ms | > 100 ms | > 150 ms | Proposal |
| Wi-Fi round trip to the access point under load, 99th percentile | ≤ 20 ms | > 50 ms | > 150 ms | Proposal |

## Endurance

| Metric | Ideal | Warning | Hard limit | Basis |
|---|---|---|---|---|
| Memory, file descriptors and response times over 72 h of use | flat | any upward trend | growth that would exhaust a resource in 30 days | T1-047, SYS-034, TK-017 |
