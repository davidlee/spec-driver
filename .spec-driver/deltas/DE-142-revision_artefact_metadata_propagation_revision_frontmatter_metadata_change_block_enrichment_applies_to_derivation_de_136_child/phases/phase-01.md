---
id: IP-142-P01
slug: "142-revision_artefact_metadata_propagation_revision_frontmatter_metadata_change_block_enrichment_applies_to_derivation_de_136_child-phase-01"
name: IP-142 Phase 01 — Engine + block conditional rules
created: "2026-05-29"
updated: "2026-05-29"
status: draft  # one of: completed | deferred | draft | in-progress | pending
kind: phase  # one of: audit | delta | design_revision | issue | memory | phase | plan | policy | problem | prod | requirement | risk | spec | standard | task | verification
plan: IP-142
delta: DE-142
---

# Phase 1 — Engine + block conditional rules

## 1. Objective

Make `action × field-presence` on `supekku:revision.change@v1` enforceable
**declaratively** and **additively** (F-F: no block redefinition). Two moves:

1. Extend the metadata engine so any *object* `FieldMetadata` can carry
   `conditional_rules` (applied per array item, not just top level).
2. Declare those rules on the `requirements[]` item of `REVISION_CHANGE_METADATA`.

Foundation phase — P02–P04 build on the validated block.

## 2. Links & References

- **Delta**: DE-142
- **Design Revision Sections**: DR-142 §4 (engine extension + declared rules), §13.1 (behaviour-preservation residual), DEC-142-02/03.
- **Specs / PRODs**: PROD-004.FR-002.
- **Support Docs**:
  - `blocks/metadata/schema.py` (`FieldMetadata`, `ConditionalRule`, `BlockMetadata`)
  - `blocks/metadata/validator.py` (`_validate_conditional_rules`, `_validate_object`, `_validate_array`)
  - `blocks/revision_metadata.py` (`REVISION_CHANGE_METADATA`)
  - `blocks/metadata/test_engine.py` (only current `conditional_rules` user — must stay green)

## 3. Entrance Criteria

- [x] DR-142 approved, validated, reconciled with DE-142
- [x] DR-136 §10.2 erratum committed
- [ ] Owning delta DE-142 moved to `in-progress` (at execute time)

## 4. Exit Criteria / Done When

- [ ] `FieldMetadata.conditional_rules: list[ConditionalRule]` exists (additive, default empty)
- [ ] Object-level conditional rules applied in `_validate_object` via shared helper; top-level call preserved with no error-path regression (no leading dot)
- [ ] `REVISION_CHANGE_METADATA` `requirements[]` item declares: `move`→{origin,destination}, `introduce`→{destination}, `modify`→{destination}
- [ ] VT-142-ENGINE-001/002/003 + VT-142-BLOCK-001/002/003 pass
- [ ] Existing block-validator + `test_engine` suites green (no-change guard)
- [ ] `just lint` zero warnings; `just pylint-files` on touched files no new warnings

## 5. Verification

- `just test` (full) + targeted: `validator_test`, `revision_metadata_test`, `test_engine`.
- **VT-142-ENGINE-001**: `requirements[]` item with `action: move`, no `origin` → error `requirements[i].origin is required when action=move`.
- **VT-142-ENGINE-002**: object-level rule on a non-array nested object also fires (proves generality, not array-only).
- **VT-142-ENGINE-003**: a block whose metadata declares no `conditional_rules` validates identically before/after (regression guard for all existing blocks).
- **VT-142-BLOCK-001**: `move` missing `origin` → error; missing `destination` → error.
- **VT-142-BLOCK-002**: `introduce`/`modify` missing `destination` → error.
- **VT-142-BLOCK-003**: well-formed entries pass strict — use **RE-042** (real `modify`+`destination`, no `origin`) as regression fixture; must stay clean.
- Evidence: test run output appended to §10.

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - No production block declares top-level `conditional_rules` today (verified: only `test_engine.py`) — generalising the helper is safe.
  - Array items dispatch `_validate_field → _validate_object`, so item-scoped rules fire with `action` as a direct key (`_get_nested_value(item, "action")`).
  - `retire` adds no required fields (DEC-142-03).
- **STOP when**:
  - The shared-helper refactor changes any existing validator test output (beyond intended) → re-check error-path prefix; do not paper over with test edits.
  - Per-item rules cannot resolve `action` without deeper engine surgery → `/consult` before expanding scope into `_validate_array`.

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description | Parallel? | Notes |
| ------ | --- | ----------- | --------- | ----- |
| [ ] | 1.1 | Add `conditional_rules: list[ConditionalRule] = field(default_factory=list)` to `FieldMetadata` | [ ] | schema.py; additive |
| [ ] | 1.2 | Extract `_apply_conditional_rules(obj, rules, path_prefix)` from `_validate_conditional_rules`; call from `validate()` (prefix="") and `_validate_object` (prefix=field_path) | [ ] | preserve error path (no leading dot) — R-142-03 |
| [ ] | 1.3 | Declare `conditional_rules` on `requirements[]` item in `REVISION_CHANGE_METADATA` | [ ] | move→{origin,destination}, introduce/modify→{destination} |
| [ ] | 1.4 | Tests VT-142-ENGINE-001/002/003 | [P] | validator_test / test_engine |
| [ ] | 1.5 | Tests VT-142-BLOCK-001/002/003 (RE-042 regression fixture) | [P] | revision_metadata_test |
| [ ] | 1.6 | Lint + full suite green (no-change guard) | [ ] | `just lint`, `just test` |

### Task Details

- **1.1 FieldMetadata.conditional_rules**
  - **Design / Approach**: mirror `BlockMetadata.conditional_rules`; additive dataclass field, default empty. Confirm `__post_init__`/JSON-schema generation (`json_schema.py`) tolerate the new field (likely no-op for empty).
  - **Files / Components**: `blocks/metadata/schema.py`; check `blocks/metadata/json_schema.py`.
  - **Testing**: covered by 1.4.

- **1.2 Shared conditional-rule helper**
  - **Design / Approach**: rename body of `_validate_conditional_rules(data)` into `_apply_conditional_rules(obj, rules, path_prefix)`; existing top-level entry calls it with `self.metadata.conditional_rules, ""`. Add a call at end of `_validate_object` with `field_meta.conditional_rules, field_path`. Join paths so prefix `""` yields `origin` (not `.origin`) and prefix `requirements[2]` yields `requirements[2].origin`.
  - **Files / Components**: `blocks/metadata/validator.py`.
  - **Testing**: VT-142-ENGINE-001/002/003.

- **1.3 Declare requirements[] rules**
  - **Design / Approach**: add `conditional_rules=[...]` to the `requirements[]` item object `FieldMetadata` in `REVISION_CHANGE_METADATA`. Reuse existing `ConditionalRule` import. Keep field descriptions (now enforced, not just prose).
  - **Files / Components**: `blocks/revision_metadata.py`.
  - **Testing**: VT-142-BLOCK-001/002/003.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| ---- | ---------- | ------ |
| Helper refactor regresses existing validation (R-142-03) | VT-142-ENGINE-003 no-change guard; run `test_engine` + full validator suite | design |
| Error-path prefix introduces leading dot | explicit join logic + assertion in 1.2 tests | design |

## 9. Decisions & Outcomes

- `2026-05-29` — Conditional rules are object-scoped on `FieldMetadata`, applied in `_validate_object`, so they cover both top-level blocks and array items without touching `_validate_array` (DEC-142-02).

## 10. Findings / Research Notes

- `_validate_conditional_rules` (validator.py:529) uses dot-path traversal on the passed dict; generalising the object it receives is sufficient for per-item rules — no array-indexing logic needed.
- Only `test_engine.py` exercises top-level `conditional_rules` today — low refactor blast radius.

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored (§10)
- [ ] DR-142/IP-142 updated if approach shifted
- [ ] Hand-off note to P02 (FM completion + applies_to derivation)
