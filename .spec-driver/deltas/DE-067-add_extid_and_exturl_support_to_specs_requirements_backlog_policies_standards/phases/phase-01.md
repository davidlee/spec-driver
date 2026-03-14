---
id: IP-067.PHASE-01
slug: "067-add_extid_and_exturl_support_to_specs_requirements_backlog_policies_standards-phase-01"
name: IP-067 Phase 01
created: "2026-03-08"
updated: "2026-03-08"
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-067.PHASE-01
plan: IP-067
delta: DE-067
objective: >-
  Add ext_id and ext_url optional fields to all domain models. Verify
  frontmatter passthrough. Add column definitions.
entrance_criteria:
  - Delta DE-067 scoped and accepted
exit_criteria:
  - All domain models accept ext_id/ext_url
  - Frontmatter roundtrip preserves the fields
  - Column defs updated
  - Unit tests pass, just check green
verification:
  tests:
    - VT-067-001
  evidence: []
tasks:
  - id: "1.1"
    description: Add ext_id/ext_url to domain models
  - id: "1.2"
    description: Verify frontmatter passthrough
  - id: "1.3"
    description: Add column definitions
  - id: "1.4"
    description: Write unit tests
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-067.PHASE-01
```

# Phase 1 – Models and Schema

## 1. Objective

Add `ext_id` and `ext_url` optional string fields to all domain models that
represent artifacts. Verify that frontmatter parsing passes these fields through.
Add column definitions for the external ID column.

## 2. Links & References

- **Delta**: DE-067
- **Specs**: PROD-004, SPEC-116
- **Issue**: ISSUE-024

## 3. Entrance Criteria

- [x] Delta DE-067 scoped

## 4. Exit Criteria / Done When

- [x] All domain models accept ext_id/ext_url as optional fields
- [x] Frontmatter roundtrip preserves ext_id/ext_url without validation errors
- [x] Column defs include external ID column definition
- [x] Unit tests cover model construction with/without fields
- [x] `just check` passes

## 5. Verification

- `just test` — all unit tests pass
- `just lint` — zero warnings
- `just pylint-files` on changed files

## 6. Assumptions & STOP Conditions

- Assumption: `FrontmatterValidationResult` passes through unknown fields via
  `data` dict — ext_id/ext_url will be available in `data` without schema changes
- STOP if: frontmatter validation rejects unknown fields (would need schema change first)

## 7. Tasks & Progress

| Status | ID  | Description                         | Parallel? | Notes                                          |
| ------ | --- | ----------------------------------- | --------- | ---------------------------------------------- |
| [x]    | 1.1 | Add ext_id/ext_url to domain models | [P]       | All 6 models updated                           |
| [x]    | 1.2 | Verify frontmatter passthrough      |           | Confirmed: unknown fields survive in data dict |
| [x]    | 1.3 | Add column defs for external ID     | [P]       | EXT_ID_COLUMN added                            |
| [x]    | 1.4 | Write unit tests                    |           | Spec, BacklogItem, ChangeArtifact tests added  |

### Task Details

- **1.1 Add ext_id/ext_url to domain models**
  - **Files**:
    - `supekku/scripts/lib/backlog/models.py` — `BacklogItem`
    - `supekku/scripts/lib/specs/models.py` — `Spec`
    - `supekku/scripts/lib/changes/artifacts.py` — `ChangeArtifact`
    - `supekku/scripts/lib/requirements/registry.py` — `RequirementRecord`
    - `supekku/scripts/lib/policies/registry.py` — `PolicyRecord`
    - `supekku/scripts/lib/standards/registry.py` — `StandardRecord`
  - **Approach**: Add `ext_id: str = ""` and `ext_url: str = ""` to each dataclass.
    Source the values from frontmatter `data` dict during construction.

- **1.2 Verify frontmatter passthrough**
  - **Files**: `supekku/scripts/lib/core/frontmatter_schema.py`
  - **Approach**: Confirm that `validate_frontmatter()` preserves unknown fields
    in the `data` mapping. Write a test if not already covered.

- **1.3 Add column definitions**
  - **Files**: `supekku/scripts/lib/formatters/column_defs.py`
  - **Approach**: Add a shared `EXT_ID_COLUMN` def. Don't add to default column
    lists yet — that's phase 2 (behind `--external` flag).

- **1.4 Write unit tests**
  - Model construction with ext_id/ext_url populated and empty
  - Frontmatter roundtrip test

## 8. Risks & Mitigations

| Risk                  | Mitigation                                      | Status |
| --------------------- | ----------------------------------------------- | ------ |
| Missing a model class | Enumerated all 6 above; VA-067-001 will confirm | open   |

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Hand-off notes to phase 2
