# Notes for DE-142

## Session 2026-05-29 — reconciliation + DR + planning

### Done
- **DR-136 §10.2/§10.5 erratum** (commit `45b756a1`): the canonical placement
  table sketched a *flat* `changes:` block that contradicted DE-118's shipped
  rich `metadata`/`specs`/`requirements` schema AND its own F-F scope-note
  ("additive enrichment, not redefinition"). Corrected in place to the shipped
  shape + field-mapping. Recorded in DE-136 phase-03 §9. Routed via /consult,
  user-approved erratum path (not a formal umbrella RE — DR-136 still draft,
  binding intent unchanged).
- **DR-142 authored + validated + internally adversarially reviewed** (commit
  `760d4984`). 7 work items, all grounded in current code reality. DE-142
  reconciled (scope/touchpoints/verification/OQs/risk register).
- **IP-142 + phase-01 sheet** (commit `b5363f73`). 4-phase plan; P01 ready.

### Key design facts (load-bearing — verified in code, not assumed)
- `supekku:revision.change@v1` is **DE-118's rich schema** (`blocks/revision_metadata.py`):
  top-level `metadata`/`specs`/`requirements`; `requirements[].action` enum
  (`introduce|modify|move|retire`) **already exists**. DE-142 is **additive only**
  (F-F) — NO `@v2`, NO block reshape.
- `REVISION_FRONTMATTER_METADATA` already exists as a **DE-137 stub** (Base +
  status only). DE-142 *completes* it (Base 7 + relations + tags + ext_id/ext_url).
- `ConditionalRule` (`blocks/metadata/schema.py`) is **top-level only** —
  `_validate_conditional_rules` does dot-path dict traversal, cannot reach
  `requirements[].action`. DE-142 P01 extends `FieldMetadata` with object-scoped
  `conditional_rules` applied in `_validate_object` (DEC-142-02). Only
  `test_engine.py` uses top-level rules today → low refactor blast radius.
- `applies_to` is **derived, never stored** (DEC-138-10 no-competing-truths);
  precedent `_derive_applies_to` in `changes/artifacts.py:29`. Revisions load via
  `ChangeRegistry(kind="revision")`.
- Migration folder is **`v0_10_0_005_revision_metadata`** (follows
  `v0_10_0_004_audit_findings`), NOT DR-136's ordinal "v06" (DEC-142-07,
  precedent DEC-141-05).
- `list revisions` lives in **`cli/list/reviews.py`** (same file as audits).

### What's next
- **`/execute-phase` for IP-142-P01** (engine + block conditional rules). Move
  DE-142 to `in-progress` at start. TDD per phase-01 §7 tasks 1.1–1.6.
- Then P02 (FM + applies_to), P03 (list), P04 (migration + sweep + strict flip).
- **Audit deferred to DE-136 umbrella close** (VA-DE136-CLOSE-001), per
  DE-139/DE-141 sibling precedent.
- After DE-142 closes + `[validation.strict].revision = true`: DE-136 P03 tasks
  3.9–3.11 (flip confirm, baseline check, phase wrap), then P04 umbrella close.

### Memory to capture once P01 lands (not yet — design only)
- "Object-level `FieldMetadata.conditional_rules` enable per-array-item
  validation" — capture as a metadata-engine capability memory after it's real.
