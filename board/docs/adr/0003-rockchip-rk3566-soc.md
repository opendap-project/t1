# ADR 0003: Rockchip RK3566 SoC

- **Status:** Accepted
- **Date:** 2026-10-21

## Context

The SoC must meet the requirements without raising the price significantly (BRD-002) and work with mainline Linux (BRD-001).

- The display is only a few inches (credit-card footprint), and the T1 is not meant to be a video player. HD video is enough.
- The most demanding workloads are monitoring spectrograms or radiograms, and recording SDR samples or video at high data rates.
- The requirements do not call for the most advanced on-board AI.

## Decision

Use the **Rockchip RK3566**, chosen for its mature mainline support.

Upgrade alternatives, if a later revision needs more: **Rockchip RK3576** and **NXP i.MX 8M Plus**.
