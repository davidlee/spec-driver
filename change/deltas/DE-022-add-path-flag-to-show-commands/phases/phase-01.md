---
id: IP-022.PHASE-01
slug: 022-add-path-flag-to-show-commands-phase-01
name: IP-022 Phase 01 - Implement --path and --json flags
created: '2026-02-04'
updated: '2026-02-04'
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-022.PHASE-01
plan: IP-022
delta: DE-022
objective: >-
  Add --path flag to all show subcommands and --json to show card for consistent CLI flag support.
entrance_criteria:
  - DR-022 design approved
  - PROD-013 spec reviewed
exit_criteria:
  - All show commands support --path flag
  - show card supports --json flag
  - Tests passing
  - Lint clean
verification:
  tests:
    - supekku/cli/show_test.py
  evidence: []
tasks:
  - id: "1.1"
    description: Add --path flag to show_spec
    status: complete
  - id: "1.2"
    description: Add --path flag to show_delta
    status: complete
  - id: "1.3"
    description: Add --path flag to show_revision
    status: complete
  - id: "1.4"
    description: Add --path flag to show_requirement
    status: complete
  - id: "1.5"
    description: Add --path flag to show_adr
    status: complete
  - id: "1.6"
    description: Add --path flag to show_policy
    status: complete
  - id: "1.7"
    description: Add --path flag to show_standard
    status: complete
  - id: "1.8"
    description: Update show_card with --json and --path
    status: complete
  - id: "1.9"
    description: Write tests
    status: complete
  - id: "1.10"
    description: Lint and verify
    status: complete
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-022.PHASE-01
```

# Phase 1 - Implement --path and --json flags

## 1. Objective

Add `--path` flag to all `show` subcommands and `--json` flag to `show card` for consistent CLI flag support per PROD-013.FR-001, FR-006, FR-007.

## 2. Links & References

- **Delta**: [DE-022](../DE-022.md)
- **Design Revision**: [DR-022](../DR-022.md) Section 4, 10
- **Specs**: PROD-013.FR-001, PROD-013.FR-006, PROD-013.FR-007
- **Source**: `supekku/cli/show.py`

## 3. Entrance Criteria

- [x] DR-022 design approved
- [x] PROD-013 spec reviewed

## 4. Exit Criteria / Done When

- [x] All show commands accept `--path` flag
- [x] `show card` accepts `--json` flag
- [x] `-q` alias still works on `show card`
- [x] Mutual exclusivity error for `--path --json`
- [x] Tests passing (`just test`)
- [x] Lint clean (`just lint`)

## 5. Verification

- Run: `just test supekku/cli/show_test.py`
- Run: `just lint`
- Manual: `spec-driver show adr ADR-001 --path`

## 6. Assumptions & STOP Conditions

- Assumptions: All registries already expose path via `to_dict()` or similar
- STOP when: Registry lacks path information (would need additional work)

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 1.1 | Add --path to show_spec | [P] | |
| [x] | 1.2 | Add --path to show_delta | [P] | |
| [x] | 1.3 | Add --path to show_revision | [P] | |
| [x] | 1.4 | Add --path to show_requirement | [P] | |
| [x] | 1.5 | Add --path to show_adr | [P] | |
| [x] | 1.6 | Add --path to show_policy | [P] | |
| [x] | 1.7 | Add --path to show_standard | [P] | |
| [x] | 1.8 | Update show_card (--json, --path) | | -q alias kept |
| [x] | 1.9 | Write tests | | 6 new tests |
| [x] | 1.10 | Lint and verify | | Final |

### Task Details

- **1.1-1.7**: Add `--path` flag following pattern in DR-022 Section 10
  - Add parameter to function signature
  - Add mutual exclusivity check
  - Add early return with path output

- **1.8**: Update show_card
  - Add `--json` flag
  - Rename `--quiet` to `--path`, keep `-q` as alias
  - Add card.to_dict() for JSON output

- **1.9**: Write tests in `show_test.py`
  - Test `--path` returns single line path
  - Test `--json` on show card
  - Test `--path --json` returns error

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Registry lacks path | Verify JSON output first | Verified OK |

## 9. Decisions & Outcomes

- 2026-02-04: Design approved per DR-022

## 10. Findings / Research Notes

- JSON output already includes `path` for all artifact types (verified)
- `show_card` uses `registry.resolve_path()` for `-q` output
- Pattern is consistent across show commands

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Plan updated with completion

## 12. Verification Evidence

- **Tests**: 1555 passed (2026-02-05), including 6 new --path flag tests
- **Lint**: `just lint` passes clean
- **Manual**: `uv run spec-driver show adr ADR-001 --path` → path only
- **Manual**: `uv run spec-driver show delta DE-023 --path --json` → mutual exclusivity error
