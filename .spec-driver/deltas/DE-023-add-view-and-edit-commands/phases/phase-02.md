---
id: IP-023.PHASE-02
slug: 023-add-view-and-edit-commands-phase-02
name: IP-023 Phase 02 - Support numeric ID shorthand
created: '2026-02-05'
updated: '2026-02-05'
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-023.PHASE-02
plan: IP-023
delta: DE-023
objective: >-
  Allow numeric-only IDs (e.g., '001') for artifact types with unambiguous prefixes.
entrance_criteria:
  - Phase 1 complete
exit_criteria:
  - numeric shorthand works for unambiguous types
  - full IDs still work
  - tests passing
  - lint clean
verification:
  tests:
    - supekku/cli/view_test.py
    - supekku/cli/edit_test.py
  evidence: []
tasks:
  - id: "2.1"
    description: Add normalize_id() helper to common.py
    status: complete
  - id: "2.2"
    description: Update view.py to use normalize_id()
    status: complete
  - id: "2.3"
    description: Update edit.py to use normalize_id()
    status: complete
  - id: "2.4"
    description: Add tests for shorthand IDs
    status: complete
  - id: "2.5"
    description: Lint and verify
    status: complete
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-023.PHASE-02
```

# Phase 2 - Support numeric ID shorthand

## 1. Objective

Allow users to omit the prefix for artifact types with unambiguous prefixes:
- `spec-driver view adr 001` → resolves to `ADR-001`
- `spec-driver edit delta 5` → resolves to `DE-005`

## 2. Links & References

- **Delta**: [DE-023](../DE-023.md)
- **Plan**: [IP-023](../IP-023.md)
- **Depends on**: Phase 1 (complete)

## 3. Entrance Criteria

- [x] Phase 1 complete

## 4. Exit Criteria / Done When

- [x] `spec-driver view adr 001` opens ADR-001
- [x] `spec-driver view adr ADR-001` still works (backwards compatible)
- [x] Shorthand works for: ADR, Delta, Revision, Policy, Standard
- [x] Shorthand NOT attempted for: Spec, Requirement, Card (ambiguous)
- [x] Tests passing (`just test`)
- [x] Lint clean (`just lint`)

## 5. Verification

- Run: `just test`
- Run: `just lint`
- Manual: `spec-driver view adr 001`, `spec-driver edit delta 23`

## 6. Assumptions & STOP Conditions

- Assumptions: Numeric-only input can be reliably detected
- STOP when: Edge cases emerge (e.g., IDs that look numeric but aren't)

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 2.1 | Add normalize_id() to common.py | | Foundation |
| [x] | 2.2 | Update view.py | | After 2.1 |
| [x] | 2.3 | Update edit.py | [P] | Parallel with 2.2 |
| [x] | 2.4 | Add tests | | After 2.2, 2.3 |
| [x] | 2.5 | Lint and verify | | Final |

### Task Details

- **2.1**: Add to `common.py`
  ```python
  # Unambiguous prefix mapping
  ARTIFACT_PREFIXES = {
    "adr": "ADR-",
    "delta": "DE-",
    "revision": "RE-",
    "policy": "POL-",
    "standard": "STD-",
  }

  def normalize_id(artifact_type: str, raw_id: str) -> str:
    """Normalize ID by prepending prefix if raw_id is numeric-only."""
    if artifact_type not in ARTIFACT_PREFIXES:
      return raw_id  # No normalization for ambiguous types
    prefix = ARTIFACT_PREFIXES[artifact_type]
    if raw_id.upper().startswith(prefix):
      return raw_id.upper()  # Already has prefix
    if raw_id.isdigit():
      return f"{prefix}{raw_id.zfill(3)}"  # Pad to 3 digits
    return raw_id  # Not numeric, return as-is
  ```

- **2.2**: Update `view.py` - call `normalize_id("adr", decision_id)` etc.

- **2.3**: Update `edit.py` - same pattern

- **2.4**: Add tests
  - `normalize_id("adr", "1")` → `"ADR-001"`
  - `normalize_id("adr", "001")` → `"ADR-001"`
  - `normalize_id("adr", "ADR-001")` → `"ADR-001"`
  - `normalize_id("spec", "001")` → `"001"` (no change)

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Zero-padding mismatch | Use 3-digit padding consistently | Open |

## 9. Decisions & Outcomes

- 2026-02-05: Scope limited to unambiguous artifact types only

## 10. Findings / Research Notes

- Unambiguous types: ADR, Delta, Revision, Policy, Standard
- Ambiguous types: Spec (SPEC/PROD), Requirement (complex), Card (various)

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Plan updated with completion

## 12. Verification Evidence

- **Tests**: 1551 passed (2026-02-05), including 9 new shorthand tests
- **Lint**: `just lint` passes clean
- **Manual**: `PAGER=cat uv run spec-driver view adr 001` → ADR-001 content
- **Manual**: `PAGER=cat uv run spec-driver view adr 1` → ADR-001 content
- **Manual**: `PAGER=cat uv run spec-driver view delta 23` → DE-023 content
