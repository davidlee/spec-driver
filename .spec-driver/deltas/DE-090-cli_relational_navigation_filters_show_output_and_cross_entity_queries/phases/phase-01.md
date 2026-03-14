---
id: IP-090.PHASE-01
slug: 090-p0-bug-fixes
name: "P0 bug fixes: relation display, show spec, plan resilience"
created: "2026-03-13"
updated: "2026-03-13"
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-090.PHASE-01
plan: IP-090
delta: DE-090
objective: >-
  Fix three P0 bugs: relation type display in show delta, missing relations/requirements
  in show spec, and list plans crash on malformed YAML.
entrance_criteria:
  - DR-090 P0 design approved
exit_criteria:
  - All three bugs fixed with tests
  - VT-090-P0-1, VT-090-P0-2, VT-090-P0-3 passing
  - Lint clean (ruff + pylint)
  - Existing tests unbroken
verification:
  tests:
    - VT-090-P0-1
    - VT-090-P0-2
    - VT-090-P0-3
  evidence: []
tasks:
  - id: "1.1"
    description: "Fix _format_relations() key bug"
  - id: "1.2"
    description: "Add _format_spec_relations() and _format_requirements_summary()"
  - id: "1.3"
    description: "Add plan parse error resilience with stderr warning"
  - id: "1.4"
    description: "Update show spec JSON to include relations"
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-090.PHASE-01
```

# Phase 01 — P0 Bug Fixes

## 1. Objective

Fix three P0 bugs identified in DE-090 and designed in DR-090 §P0:

1. `show delta` relation type display (reads wrong key)
2. `show spec` missing relations and requirements summary
3. `list plans` crash on malformed YAML blocks

## 2. Links & References

- **Delta**: DE-090
- **Design Revision**: DR-090 §4 P0-1, P0-2, P0-3
- **Specs**: PROD-010.FR-005
- **Files**: `change_formatters.py`, `spec_formatters.py`, `show.py`, `registry.py`

## 3. Entrance Criteria

- [x] DR-090 P0 design approved

## 4. Exit Criteria / Done When

- [x] `show delta` displays relation types (e.g., `- relates_to: PROD-010`)
- [x] `show spec` includes Relations section and Requirements count
- [x] `show spec --json` includes relations in output
- [x] `list plans` skips malformed plans with stderr warning
- [x] VT-090-P0-1, VT-090-P0-2, VT-090-P0-3 passing
- [x] `just` passes (tests + both linters)

## 5. Verification

- Unit tests in `change_formatters_test.py`, `spec_formatters_test.py`
- Integration test for `discover_plans()` with malformed YAML fixture
- Run `just` for full check

## 6. Assumptions & STOP Conditions

- Assumptions: `Spec.frontmatter.relations` is populated by registry load for specs with relations in frontmatter
- STOP when: Spec model doesn't expose relations as expected (verify before implementing)

## 7. Tasks & Progress

| Status | ID  | Description                                                       | Parallel? | Notes                                               |
| ------ | --- | ----------------------------------------------------------------- | --------- | --------------------------------------------------- |
| [x]    | 1.1 | Fix `_format_relations()` key bug                                 | [P]       | Done: `"kind"` → `"type"`                           |
| [x]    | 1.2 | Add `_format_spec_relations()` + `_format_requirements_summary()` | [P]       | Done: formatter helpers + show.py integration       |
| [x]    | 1.3 | Plan parse resilience in `discover_plans()`                       | [P]       | Done: ValueError catch + stderr warning             |
| [x]    | 1.4 | Update `Spec.to_dict()` and show_spec JSON                        | [x]       | Done: relations serialised from .relations property |

### Task Details

- **1.1 Fix relation type key**
  - **Files**: `supekku/scripts/lib/formatters/change_formatters.py:460`
  - **Change**: `relation.get("kind", "")` → `relation.get("type", "")`; rename var from `kind` to `rel_type`
  - **Testing**: VT-090-P0-1 — test `_format_relations()` with relation dicts containing `type` key

- **1.2 Spec relations + requirements summary**
  - **Files**: `supekku/scripts/lib/formatters/spec_formatters.py`, `supekku/cli/show.py`
  - **Change**: Add `_format_spec_relations(spec)` using `spec.frontmatter.relations`. Add `_format_requirements_summary(fr_count, nf_count, other_count)`. Integrate both into `format_spec_details()`. Caller (`show_spec`) loads `RequirementsRegistry`, counts by spec ID, passes counts.
  - **Testing**: VT-090-P0-2 — formatter unit tests + show integration

- **1.3 Plan parse resilience**
  - **Files**: `supekku/scripts/lib/changes/registry.py:207-213`
  - **Change**: Wrap `extract_plan_overview()` call in `try/except ValueError`, print warning to stderr, continue. Also add warning to existing `except Exception` block.
  - **Testing**: VT-090-P0-3 — test with malformed plan YAML, verify warning emitted and valid plans returned

- **1.4 Spec JSON relations**
  - **Files**: `supekku/scripts/lib/specs/models.py:108-133`
  - **Change**: Add relations to `Spec.to_dict()` — serialise `self.frontmatter.relations` as list of `{"type": r.type, "target": r.target}` dicts
  - **Testing**: Covered by VT-090-P0-2

## 8. Risks & Mitigations

| Risk                                                 | Mitigation                                                                  | Status |
| ---------------------------------------------------- | --------------------------------------------------------------------------- | ------ |
| Spec model relations access differs from expectation | Verified: `.relations` property returns list of dicts with type/target keys | Closed |

## 9. Decisions & Outcomes

- 2026-03-13 — DEC-090-01: Display relation types raw, not humanized
- 2026-03-13 — DEC-090-02: Requirements count-only in rendered; full in JSON
- 2026-03-13 — DEC-090-03: Plan parse errors warn to stderr and skip

## 10. Findings / Research Notes

- `Spec.relations` property (line 53 of models.py) does `dict(r)` on raw frontmatter, preserving extra keys like `annotation`. `to_dict()` passes these through — consistent with other dict-based serialisation in the model.
- `FrontmatterValidationResult` stores relations as list of dicts (Mapping), not typed Relation objects. The `.relations` property filters to only entries with both `type` and `target` keys.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored (3869 tests pass, linters clean)
- [x] Phase tracking block updated
- [x] Hand-off notes to Phase 02

### Hand-off to Phase 02

- All P0 bugs fixed. Tasks 1.1–1.4 complete with tests.
- `just` passes: 3869 tests, ruff clean, pylint 9.72/10 (no new warnings).
- Phase 02 scope: 5 relational filter flags on list commands (DR-090 §P1).
- Phase 02 sheet needs creation via `spec-driver create phase`.
- Unresolved assumptions verified: `BacklogItem.frontmatter` is a raw dict (confirmed by `item.frontmatter.get()` usage in existing backlog code). `ChangeArtifact.relations` stores dicts with `type`/`target` keys (confirmed).
