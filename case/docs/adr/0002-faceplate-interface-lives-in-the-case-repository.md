# ADR 0002: Faceplate interface lives in the case repository

- **Status:** Superseded by [t1 ADR 0001](https://github.com/opendap-project/t1/blob/main/docs/adr/0001-faceplate-interface-lives-in-t1.md)
- **Date:** 2026-10-21

## Context

Faceplates are interchangeable front modules (CASE-008), but they are not meant to be swapped regularly (CASE-010). Their interface only covers flat-cable connector pinout, dimensions and screw anchoring (CASE-009).

## Decision

The faceplate interface is a specification inside the `case` repository ([`docs/specs/faceplate-interface.md`](https://github.com/opendap-project/t1/blob/main/docs/specs/faceplate-interface.md)), not a separate standard repository like the HAT Case Standard. Each faceplate keeps its own mechanics in its repository and meets this interface.
