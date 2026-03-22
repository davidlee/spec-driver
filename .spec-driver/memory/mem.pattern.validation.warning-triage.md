---
id: mem.pattern.validation.warning-triage
name: validate warning triage pattern
kind: memory
status: active
memory_type: pattern
updated: '2026-03-23'
verified: '2026-03-23'
confidence: high
tags:
- validation
- workflow
summary: Repeatable procedure for investigating and burning down spec-driver validate warnings by category
scope:
  commands: [validate]
  globs: [supekku/scripts/lib/validation/**]
  paths:
    - supekku/scripts/lib/validation/validator.py
---

# validate warning triage pattern

Run `uv run spec-driver validate` and categorise warnings. Common categories and fixes:

## Finding dispositions missing (AUD-xxx/FIND-xxx)

- Completed audits require every finding to have a `disposition` dict.
- For aligned discovery findings: `disposition: {status: reconciled, kind: aligned}`.
- Valid status×kind pairs are in `VALID_STATUS_KIND_PAIRS` (`frontmatter_metadata/audit.py`).
- Validity matrix: `aligned` outcome → `kind: aligned`; `drift`/`risk` outcomes → `spec_patch`, `revision`, `follow_up_delta`, `follow_up_backlog`, or `tolerated_drift`.

## Audit gate required but no conformance audit

- Cause: delta has `applies_to.requirements` populated and `audit_gate` is absent (defaults to `auto` → `required`).
- Fix for pre-enforcement deltas: set `audit_gate: exempt` in frontmatter.
- Fix for current deltas: create a conformance audit or explicitly set `audit_gate: exempt` with justification.
- See [[mem.fact.validation.audit-gate-test-impact]] for test implications.

## Unresolved artifact references

- Placeholder refs (`PROD-TBD`, `SPEC-TBD`): remove from `applies_to.specs` and any relationships blocks.
- Dangling refs to deleted/renumbered specs: clear from `applies_to.specs`.
- Cross-project refs (`namespace:ID`, e.g. `autobahn:DE-001`): validator skips these automatically.

## Missing phase.overview block

- Legacy phase files without `plan`/`delta` frontmatter trigger this.
- Fix: add `plan: IP-xxx` and `delta: DE-xxx` to frontmatter → promotes to new-format, bypasses overview check.

## General approach

1. Run `uv run spec-driver validate 2>&1` and group by message pattern.
2. Read `_validate_*` methods in `validator.py` to understand each check's logic.
3. Prefer data fixes (frontmatter edits) over validator suppression.
4. Run `uv run pytest supekku/scripts/lib/validation/ -x -q` after code changes.
