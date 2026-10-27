# ADR 0001: Faceplate interface lives in t1

- **Status:** Accepted
- **Date:** 2026-10-21

## Context

The faceplate interface (flat-cable pinout, dimensions, screw anchoring, identification and control commands; T1-018, T1-019, T1-020, T1-023, T1-024) connects the faceplates to the rest of the product. It was first placed in the `case` repository (case ADR 0002), but `case` covers only the physical case.

## Decision

The faceplate interface is a specification of the product integration repository: [`docs/specs/faceplate-interface.md`](../specs/faceplate-interface.md). It is not a separate standard repository like the HAT Case Standard, because faceplates are not meant to be swapped regularly. This supersedes case ADR 0002.
