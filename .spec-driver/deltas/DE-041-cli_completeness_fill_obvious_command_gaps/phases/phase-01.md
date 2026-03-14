---
id: IP-041.PHASE-01
slug: 041-cli_completeness_fill_obvious_command_gaps-phase-01
name: 'IP-041 Phase 01 — Foundation: shared helpers + migration PoC'
created: '2026-03-04'
updated: '2026-03-04'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-041.PHASE-01
plan: IP-041
delta: DE-041
objective: >-
  Extract shared CLI helpers (resolve_artifact, emit_artifact, find_artifacts) into
  common.py, validate them by migrating revision commands as proof-of-concept, and
  fix the known show revision --json bug.
entrance_criteria:
  - DR-041 reviewed and contradictions resolved
  - Gate check passed (IP-041 §3)
  - Existing test suite passing (just check)
  - Familiarity with existing show/view/edit/find patterns in CLI files
exit_criteria:
  - ArtifactRef, ArtifactNotFoundError, AmbiguousArtifactError implemented in common.py
  - resolve_artifact() handles all existing artifact types via dispatch table
  - emit_artifact() enforces explicit json_fn (no fallback chain)
  - find_artifacts() yields matching ArtifactRef for pattern queries
  - All helpers have comprehensive parameterized unit tests
  - Pre-migration regression tests written for revision commands (all verbs x all output modes)
  - Revision commands (show/view/edit/find) migrated to shared helpers
  - show revision --json bug fixed
  - Regression tests pass both before and after migration
  - just check green (tests + both linters)
verification:
  tests:
    - VT-resolve
    - VT-emit
    - VT-find-artifacts
    - VT-migration
  evidence:
    - VA-lint
tasks:
  - id: "1.1"
    description: "Implement ArtifactRef, ArtifactNotFoundError, AmbiguousArtifactError"
    status: pending
  - id: "1.2"
    description: "Implement resolve_artifact() with dispatch table for existing types"
    status: pending
  - id: "1.3"
    description: "Implement emit_artifact() with required json_fn"
    status: pending
  - id: "1.4"
    description: "Implement find_artifacts()"
    status: pending
  - id: "1.5"
    description: "Unit tests for helpers (VT-resolve, VT-emit, VT-find-artifacts)"
    status: pending
  - id: "1.6"
    description: "Write pre-migration regression tests for revision commands"
    status: pending
  - id: "1.7"
    description: "Migrate revision show/view/edit/find to shared helpers; fix --json bug"
    status: pending
  - id: "1.8"
    description: "Final verification: just check green"
    status: pending
risks:
  - description: Dispatch table approach may not handle all artifact type quirks
    likelihood: low
    impact: medium
    mitigation: PoC migration validates against real revision commands; adjust dispatch per type
  - description: emit_artifact may need per-type variations beyond format_fn/json_fn
    likelihood: low
    impact: low
    mitigation: Start with minimal signature; revision migration reveals if more params needed
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-041.PHASE-01
```

# Phase 01 — Foundation: shared helpers + migration PoC

## 1. Objective

Extract the proven resolve→lookup→not-found-error→dispatch pattern into shared
helpers in `common.py`, then validate the design by migrating revision commands
as a proof-of-concept. This is the riskiest phase — everything in Phase 2/3
depends on these helpers working correctly.

## 2. Links & References

- **Delta**: [DE-041](../DE-041.md)
- **Design Revision**: [DR-041](../DR-041.md) §4.1 (shared helpers), §4.5 (migration)
- **Specs**: PROD-010 (CLI UX), PROD-013 (CLI Artifact File Access)
- **Existing patterns**: `supekku/cli/show.py`, `view.py`, `edit.py`, `find.py`

## 3. Entrance Criteria

- [x] DR-041 reviewed and contradictions resolved
- [x] Gate check passed (IP-041 §3)
- [ ] Existing test suite passing (`just check`)
- [ ] Familiarity with existing show/view/edit/find patterns

## 4. Exit Criteria / Done When

- [ ] `ArtifactRef`, `ArtifactNotFoundError`, `AmbiguousArtifactError` in common.py
- [ ] `resolve_artifact()` handles all existing artifact types
- [ ] `emit_artifact()` with required `json_fn` (no fallback)
- [ ] `find_artifacts()` yields matching refs
- [ ] Comprehensive unit tests for all helpers (VT-resolve, VT-emit, VT-find-artifacts)
- [ ] Pre-migration regression tests for revision commands cover all output modes
- [ ] Revision show/view/edit/find migrated to shared helpers
- [ ] `show revision --json` bug fixed
- [ ] Regression tests pass before and after migration
- [ ] `just check` green

## 5. Verification

```bash
# Unit tests for helpers
uv run pytest supekku/cli/common_test.py -v

# Regression tests for revision commands
uv run pytest supekku/cli/show_test.py -k revision -v
uv run pytest supekku/cli/view_test.py -k revision -v
uv run pytest supekku/cli/edit_test.py -k revision -v
uv run pytest supekku/cli/find_test.py -k revision -v

# Full suite + linters
just check
```

## 6. Assumptions & STOP Conditions

**Assumptions**:

- The resolve→lookup→dispatch pattern is truly common across all verb groups (confirmed by codebase exploration)
- `ChangeRegistry` with `kind="revision"` provides adequate revision lookup
- All existing resolver patterns can be captured in a dispatch table

**STOP when**:

- Resolver dispatch table cannot handle an artifact type without per-type branching >5 lines
- Migration reveals that `emit_artifact` needs more than format_fn/json_fn to cover existing behavior
- Pre-migration regression tests reveal untested behavior that changes scope

## 7. Tasks & Progress

| Status | ID  | Description                                          | Parallel? | Notes                          |
| ------ | --- | ---------------------------------------------------- | --------- | ------------------------------ |
| [ ]    | 1.1 | Implement data types (ArtifactRef, errors)           | [ ]       | Foundation for everything else |
| [ ]    | 1.2 | Implement resolve_artifact() with dispatch table     | [ ]       | Depends on 1.1                 |
| [ ]    | 1.3 | Implement emit_artifact()                            | [P]       | Can parallel with 1.2          |
| [ ]    | 1.4 | Implement find_artifacts()                           | [P]       | Can parallel with 1.2          |
| [ ]    | 1.5 | Unit tests for helpers                               | [ ]       | After 1.1-1.4                  |
| [ ]    | 1.6 | Pre-migration regression tests for revision commands | [P]       | Independent of 1.1-1.4         |
| [ ]    | 1.7 | Migrate revision commands + fix --json bug           | [ ]       | After 1.5 + 1.6                |
| [ ]    | 1.8 | Final verification: just check                       | [ ]       | After 1.7                      |

### Task Details

- **1.1 Implement data types**
  - **Design / Approach**: Add to `supekku/cli/common.py`. See DR-041 §4.1 for exact signatures. `ArtifactRef` is a frozen dataclass with id, path, record. Error types carry artifact_type + artifact_id for consistent messaging.
  - **Files**: `supekku/cli/common.py`
  - **Testing**: Covered by 1.5

- **1.2 Implement resolve_artifact()**
  - **Design / Approach**: Dispatch table mapping artifact_type string to resolver function. Each resolver: normalize ID → registry lookup → return ArtifactRef or raise ArtifactNotFoundError. Start with all existing types (spec, delta, revision, audit, adr, policy, standard, requirement, card, memory). Plan/backlog resolvers added in Phase 2.
  - **Files**: `supekku/cli/common.py`
  - **Key detail**: Each `_resolve_*` function encapsulates the type-specific lookup pattern currently scattered across show/view/edit/find. Study the existing revision pattern in show.py (~L130-155) as the template.
  - **Testing**: Covered by 1.5 (VT-resolve)

- **1.3 Implement emit_artifact()**
  - **Design / Approach**: Per DR-041 §4.1. Mutual-exclusivity check for --json/--path/--raw. `json_fn` is required (not optional). Dispatches to: path_only → echo path, raw → read_text, json → json_fn(record), default → format_fn(record).
  - **Files**: `supekku/cli/common.py`
  - **Testing**: Covered by 1.5 (VT-emit)

- **1.4 Implement find_artifacts()**
  - **Design / Approach**: Similar dispatch table but returns `Iterable[ArtifactRef]`. Uses fnmatch for pattern matching against artifact IDs. Iterates via registry `.collect()` / `.all_specs()` etc.
  - **Files**: `supekku/cli/common.py`
  - **Testing**: Covered by 1.5 (VT-find-artifacts)

- **1.5 Unit tests for helpers**
  - **Design / Approach**: Create `supekku/cli/common_test.py`. Parameterized tests for resolve_artifact (each type in dispatch table, not-found error, ID normalization). Tests for emit_artifact (each output mode, mutual exclusivity). Tests for find_artifacts (pattern matching, empty results). Mock registries where needed.
  - **Files**: `supekku/cli/common_test.py` (new)
  - **Verification**: VT-resolve, VT-emit, VT-find-artifacts

- **1.6 Pre-migration regression tests for revision commands**
  - **Design / Approach**: Per DR-041 §4.5 pre-migration requirement. Write tests for all 4 commands x all output modes: `show revision` (default, --json, --path, --raw), `view revision`, `edit revision`, `find revision`. These must pass BEFORE migration starts. Note: `show revision --json` has a known bug — test should document current broken behavior, then be updated after fix.
  - **Files**: additions to `supekku/cli/show_test.py`, `view_test.py`, `edit_test.py`, `find_test.py`
  - **Verification**: VT-migration

- **1.7 Migrate revision commands + fix --json bug**
  - **Design / Approach**: Replace the body of `show_revision`, `view_revision`, `edit_revision`, `find_revision` with calls to shared helpers. Fix `show revision --json` by providing correct `json_fn=lambda r: json.dumps(r.to_dict(root), indent=2)`. Regression tests must pass after migration.
  - **Files**: `supekku/cli/show.py`, `view.py`, `edit.py`, `find.py`
  - **Testing**: Run VT-migration regression tests before and after

- **1.8 Final verification**
  - **Design / Approach**: `just check` (tests + ruff + pylint). Fix any issues.
  - **Testing**: Full suite

## 8. Risks & Mitigations

| Risk                                                   | Mitigation                                                          | Status  |
| ------------------------------------------------------ | ------------------------------------------------------------------- | ------- |
| Dispatch table doesn't handle per-type quirks          | PoC migration of revision validates design; adjust if needed        | Planned |
| emit_artifact needs more params than format_fn/json_fn | Revision migration reveals requirements; extend signature if needed | Planned |
| Pre-migration tests reveal untested edge cases         | Document and scope-limit; don't let perfect block good              | Planned |

## 9. Decisions & Outcomes

- `2026-03-04` — Phase scope: helpers + revision migration only. New commands and domain additions deferred to Phase 2.

## 10. Findings / Research Notes

**Codebase exploration findings** (pre-phase):

- show.py: 513 lines, 10 commands. Boilerplate: mutual-exclusivity check + registry lookup + output-mode dispatch (~30 lines each)
- view.py: 254 lines, 8 commands. Pattern: registry lookup + pager open (~20 lines each)
- edit.py: 254 lines, 8 commands. Identical to view but with editor
- find.py: 233 lines, 8 commands. Pattern: registry iterate + fnmatch (~15 lines each)
- common.py: 284 lines. Already has `normalize_id`, `open_in_pager`, `open_in_editor`, `matches_regexp`, `RootOption`, etc.
- Known bug: show.py:153 — `show revision --json` calls `artifact.to_dict()` without required `repo_root` arg
- Test coverage: show_test.py (525L), view_test.py (232L), edit_test.py (198L), find_test.py (199L), list_test.py (792L)

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] IP-041 updated with Phase 1 results
- [ ] Hand-off notes to Phase 2
