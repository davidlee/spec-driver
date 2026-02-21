# DE-030 Implementation Notes (Handoff)

This delta operationalizes ADR-003 via **non-breaking taxonomy metadata** and **navigation tooling**.

## Locked decisions
- Reserved tech spec taxonomy values:
  - `category: unit` (1:1 with a language unit)
  - `category: assembly` (cross-unit / subsystem / integration)
- Mapping guidance: `unit` → `c4_level: code` (warn if inconsistent; do not block).
- **Warn-only** validation in v1.
- No filesystem/prefix migration in this delta (no `UNIT-*` / `ASM-*` roots).

## Expected user-visible outcomes
- Humans/agents can browse/list assembly specs without unit-stub noise.
- Sync-created unit specs (when enabled) are clearly labeled and show up in unit-only views.
- Unclassified specs are easy to find and clean up via an `unknown` bucket.

## Implementation sketch (non-prescriptive)
- Add by-category + by-c4-level symlink views under `specify/tech/`:
  - `specify/tech/by-category/unit/...`
  - `specify/tech/by-category/assembly/...`
  - `specify/tech/by-category/unknown/...`
  - `specify/tech/by-c4-level/code/...` (and others as present)
- Add `specify/tech/by-c4-level/unknown/...` for missing `c4_level`.
- Extend `spec-driver list specs` with:
  - `--category <value>` (repeatable or comma-separated; pick one pattern)
  - `--c4-level <value>`
- Ensure sync-created specs set defaults (`category: unit`, `c4_level: code`).
- Add validator warnings:
  - missing `category` or `c4_level` on tech specs
  - inconsistent combos (e.g. `unit` + non-`code`)
  - scope: tech specs only (`SPEC-*` / `kind: spec`)

## Suggested tests (keep minimal)
- Unit test: spec list filtering returns strict subsets.
- Unit test: index builder creates expected view roots and links only matching specs.
- Validation test: warnings emitted but do not fail validation.

## Don'ts (scope control)
- Don’t tighten the schema to an enum for `category` in v1 (too breaking; existing freeform use may exist).
- Don’t introduce a new top-level folder split yet (defer migration until taxonomy proves value).
