---
id: IP-085.PHASE-01
slug: 085-surface_relation_and_backlog_metadata_in_cli_and_skills-phase-01
name: "Foundation: constants, query module, Spec model"
created: '2026-03-09'
updated: '2026-03-09'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-085.PHASE-01
plan: IP-085
delta: DE-085
objective: >-
  Create the generic relation query layer (constants, Protocol, query functions)
  and add .relations property to Spec model. Full test coverage for all new code.
entrance_criteria:
  - DR-085 reviewed and approved
exit_criteria:
  - relation_types.py created with RELATION_TYPES and REFERENCE_SOURCES constants
  - base.py imports RELATION_TYPES instead of inline list
  - relations/query.py created with RelationQueryable Protocol, ReferenceHit, and all query functions
  - Spec model exposes .relations property
  - VT-085-001 and VT-085-006 passing
  - just check green
verification:
  tests:
    - VT-085-001
    - VT-085-006
  evidence: []
tasks:
  - id: T01
    summary: Create core/relation_types.py with named constants
  - id: T02
    summary: Update base.py to import RELATION_TYPES
  - id: T03
    summary: Create relations/query.py with Protocol, ReferenceHit, and query functions
  - id: T04
    summary: Add .relations property to Spec model
  - id: T05
    summary: Verify R1 — check Spec frontmatter.data shape for relations
  - id: T06
    summary: Write comprehensive tests (VT-085-001, VT-085-006)
  - id: T07
    summary: Lint and full check
risks:
  - id: R1
    description: Spec frontmatter.data may store Relation objects not raw dicts
    mitigation: Verify and adjust property implementation accordingly
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-085.PHASE-01
```

# Phase 1 — Foundation: constants, query module, Spec model

## 1. Objective

Create the generic relation query layer and Spec model update that all subsequent phases depend on. This phase produces no CLI-visible changes — it builds the reusable internals.

## 2. Links & References
- **Delta**: [DE-085](../DE-085.md)
- **Design Revision**: [DR-085](../DR-085.md) §5.1 (constants), §5.2 (query functions), §5.3 (Spec model)
- **Specs**: PROD-004 (frontmatter metadata), PROD-010 (CLI UX)

## 3. Entrance Criteria
- [x] DR-085 reviewed and approved

## 4. Exit Criteria / Done When
- [x] `core/relation_types.py` created with `RELATION_TYPES` and `REFERENCE_SOURCES` frozensets
- [x] `base.py` imports `RELATION_TYPES` — no inline string list for relation enum
- [x] `relations/query.py` created with `RelationQueryable`, `ReferenceHit`, `collect_references()`, `matches_related_to()`, `matches_relation()`, `find_related_to()`, `find_by_relation()`
- [x] `Spec.relations` property added and working
- [x] VT-085-001 passing (query module tests)
- [x] VT-085-006 passing (Spec.relations tests)
- [x] `just check` green

## 5. Verification
- `just test` — VT-085-001, VT-085-006
- `just lint` — zero warnings on new and modified files
- `just pylint-files` on all touched files
- `just check` — full suite

## 6. Assumptions & STOP Conditions
- **Assumption**: `frontmatter.data["relations"]` contains raw YAML dicts (not parsed `Relation` objects). Verify in T05.
- **STOP if**: `frontmatter.data` shape is unexpected — `/consult` before adapting.

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [x] | T01 | Create `core/relation_types.py` | [P] | Done — `RELATION_TYPES` + `REFERENCE_SOURCES` frozensets |
| [x] | T02 | Update `base.py` to import `RELATION_TYPES` | | Done — inline list replaced with `sorted(RELATION_TYPES)` |
| [x] | T03 | Create `relations/query.py` | [P] | Done — extracted to 4 private helpers, pylint 10/10 |
| [x] | T04 | Add `Spec.relations` property | [P] | Done — reads from `frontmatter.data`, validates shape |
| [x] | T05 | Verify R1: Spec frontmatter.data shape | | Resolved — `frontmatter.data["relations"]` contains raw dicts (line 86 of frontmatter_schema.py) |
| [x] | T06 | Write tests (VT-085-001, VT-085-006) | | Done — 42 query tests + 3 Spec.relations tests, all passing |
| [x] | T07 | Lint + full check | | `just check` green (3674 pass), pylint 10/10 on query.py |

### Task Details

- **T01 — `core/relation_types.py`**
  - **Files**: `supekku/scripts/lib/core/relation_types.py` (new)
  - **Design**: DR-085 §5.1. Two frozenset constants.
  - **Testing**: Import test; verify values match current inline list in `base.py`.

- **T02 — Update `base.py`**
  - **Files**: `supekku/scripts/lib/core/frontmatter_metadata/base.py`
  - **Design**: Replace inline `enum_values=[...]` with import from `relation_types.py`.
  - **Testing**: Existing `base_test.py` tests for relation type validation must pass unchanged.

- **T03 — `relations/query.py`**
  - **Files**: `supekku/scripts/lib/relations/query.py` (new), `supekku/scripts/lib/relations/__init__.py` (update exports)
  - **Design**: DR-085 §5.2. Five functions + Protocol + dataclass.
  - **Key detail**: `collect_references()` searches `.relations`, `.applies_to`, `.context_inputs`, `.informed_by` via `getattr`. Duck-typed for all but `.relations` (Protocol-required).
  - **R4**: Functions return `list[ReferenceHit]` — callers (formatters in P02) receive hits, not raw artifacts.
  - **Testing**: VT-085-001. Test with mock objects having various combinations of slots. Edge cases: empty relations, missing keys, None vs [], case sensitivity, artifact with no slots.

- **T04 — `Spec.relations` property**
  - **Files**: `supekku/scripts/lib/specs/models.py`
  - **Design**: DR-085 §5.3. Read from `frontmatter.data`, validate shape, return `list[dict[str, Any]]`.
  - **R1**: Shape depends on T05 verification.
  - **Testing**: VT-085-006. Test with specs that have relations, don't have relations, have malformed relations.

- **T05 — Verify R1**
  - Check what `FrontmatterValidationResult.data["relations"]` actually contains at runtime for a spec with relations.
  - If raw dicts → T04 sketch works as-is.
  - If parsed `Relation` objects → convert via `{"type": r.type, "target": r.target, **r.attributes}`.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|
| R1: Spec frontmatter.data shape | Verify in T05 before implementing T04 | Open |

## 9. Decisions & Outcomes
- 2026-03-09: R1 resolved — `frontmatter.data["relations"]` holds raw `list[dict]`, not `Relation` objects. `Spec.relations` property reads from `.data` directly.
- 2026-03-09: ruff formatter auto-reformatted 6 files on `just check` — all formatting now canonical.
- 2026-03-09: T07 resolved — extracted `collect_references` into 4 private `_collect_from_*` helpers. Protocol gets `pylint: disable=too-few-public-methods` + `unnecessary-ellipsis` (both correct by design). Pylint 10/10.

## 10. Findings / Research Notes

### T07 pylint issues on `query.py` (5 messages, must fix before phase exit)

```
supekku/scripts/lib/relations/query.py:19  too-few-public-methods  (RelationQueryable Protocol — 1/2)
supekku/scripts/lib/relations/query.py:56  too-complex  collect_references McCabe=16
supekku/scripts/lib/relations/query.py:56  too-many-branches  (15/12)
supekku/scripts/lib/relations/query.py:56  too-many-locals  (17/15)
supekku/scripts/lib/relations/query.py:28  missing-function-docstring  (Protocol property)
```

**Fix approach**: Extract `collect_references` into 4 private slot-collection helpers:
- `_collect_from_relations(artifact) -> list[ReferenceHit]`
- `_collect_from_applies_to(artifact) -> list[ReferenceHit]`
- `_collect_from_context_inputs(artifact) -> list[ReferenceHit]`
- `_collect_from_informed_by(artifact) -> list[ReferenceHit]`

Then `collect_references` just concatenates. This resolves complexity, branches, and locals.

For `too-few-public-methods` on Protocol: add a pylint disable comment (Protocol with one property is correct by design — ADR-009 defers richer abstractions).

For `missing-function-docstring` on the Protocol property: add a one-line docstring.

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Notes updated with findings
- [ ] Hand-off notes to Phase 2
