# Notes for DE-035

## Direction captured

- Assembly specs are the only first-class authored tech spec type.
- Unit specs are deprecated as a concept for new generation.
- Contracts remain the canonical observed-code artifact.

## Compatibility posture

- Existing `SPEC-*` paths remain valid.
- Existing `category: unit` specs remain readable and non-blocking.
- Transition starts with behavior/tooling changes, not bulk migration.

## Pending implementation decisions

- Whether to keep `by-category/unit` as a compatibility view for one release window.
- Whether ADR-003 is superseded by a new ADR or amended in place.
