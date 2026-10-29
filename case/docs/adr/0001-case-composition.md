# ADR 0001: Case composition

- **Status:** Superseded by [ADR 0003](0003-case-scope.md)
- **Date:** 2026-10-21

## Context

The case holds all the rigid mechanics of the device, and the rear of the device must accept HATs.

## Decision

The case consists of:

- **Core**: the main enclosure, including the basic back cover.
- **Faceplate**: the front module. Faceplates are a category of interchangeable front modules, like HATs on the rear. The default is the [touch faceplate](https://github.com/opendap-project/faceplate-touch); others are [cassette](https://github.com/opendap-project/faceplate-cassette) and [classic](https://github.com/opendap-project/faceplate-classic).
- **HAT case**: a rear cover that carries a HAT and replaces the basic back cover.
