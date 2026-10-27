# ADR 0003: Case scope

- **Status:** Accepted
- **Date:** 2026-10-21

## Context

The `case` repository had collected product requirements (footprint, buttons, ports, editions, faceplate interface). The case is only the physical case; the product is the T1.

## Decision

The `case` repository covers only the physical case:

- **Core**: the main enclosure, including the basic back cover.
- **HAT case** mechanics on the device side, swapped in for the basic back cover.
- The **mount** that faceplates attach to, following the faceplate interface defined in [`t1`](https://github.com/opendap-project/t1/blob/main/docs/specs/faceplate-interface.md).

Faceplates keep their own mechanics in their repositories. Product requirements live in `t1`. This supersedes ADR 0001.
