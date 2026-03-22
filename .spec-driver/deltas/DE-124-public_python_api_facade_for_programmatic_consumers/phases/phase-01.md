---
id: IP-124-P01
slug: "124-public_python_api_facade_for_programmatic_consumers-phase-01"
name: Extract operations and refactor CLI
created: "2026-03-23"
updated: "2026-03-23"
status: completed
kind: phase
plan: IP-124
delta: DE-124
---

# Phase 1 — Extract operations and refactor CLI

## 1. Objective

Extract review orchestration logic from CLI command functions into `spec_driver/orchestration/operations.py`. Refactor CLI review commands to thin wrappers. Add unit tests for all operations. This is the high-risk phase — existing CLI behaviour must be preserved exactly.

## 2. Links & References

- **Delta**: [DE-124](../DE-124.md)
- **Design Revision**: [DR-124](../DR-124.md) §4 (Extraction Design)
- **Key source**: `supekku/cli/workflow.py` lines 54–78 (resolve), 844–1058 (prime), 1241–1448 (complete), 1503–1589 (disposition), 1997–2028 (teardown)
- **Existing tests**: `supekku/cli/workflow_review_test.py`, `supekku/cli/workflow_integration_test.py`

## 3. Entrance Criteria

- [x] DR-124 complete with adversarial review (3 rounds)
- [x] IP-124 phase overview defined
- [x] No open questions

## 4. Exit Criteria / Done When

- [x] `operations.py` contains all 6 operations: `resolve_delta_dir`, `prime_review`, `complete_review`, `disposition_finding`, `teardown_review`, `summarize_review`
- [x] All result dataclasses use typed enums (DEC-124-003)
- [x] `disposition_finding` uses typed kwargs and domain validation per DR-109 matrix (DEC-124-010, DEC-124-011)
- [x] `complete_review` has `auto_teardown` parameter (DEC-124-009)
- [x] CLI review commands refactored to thin wrappers (~20-30 lines each)
- [x] All existing CLI tests pass without modification
- [x] `operations_test.py` with unit tests for all 6 operations
- [x] `just check` passes (lint, format, tests)

## 5. Verification

- Run existing tests first (baseline): `uv run pytest supekku/cli/workflow_review_test.py supekku/cli/workflow_integration_test.py -v`
- Run after extraction (regression): same command, expect identical results
- Run new tests: `uv run pytest spec_driver/orchestration/operations_test.py -v`
- Lint: `uv run ruff check spec_driver/orchestration/operations.py supekku/cli/workflow.py`
- Full suite: `just check`

## 6. Assumptions & STOP Conditions

- **Assumption**: `_load_workflow_config` can be imported by `operations.py` from the CLI module without creating circular dependencies. If not, extract to `supekku/scripts/lib/core/config.py` (it already wraps `load_workflow_config` from there).
- **Assumption**: `_build_domain_map` and `_generate_bootstrap_markdown` are purely self-contained — no hidden CLI dependencies.
- **STOP**: If extracting any helper reveals hidden state or side effects not visible in the current code reading.
- **STOP**: If any existing CLI test fails after extraction — do not proceed until resolved.

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
|---|---|---|---|---|
| [x] | 1.1 | Run existing tests (baseline) | — | 69 passed |
| [x] | 1.2 | Create `operations.py` with new types | — | Types already existed from workshopping |
| [x] | 1.3 | Extract `resolve_delta_dir` | — | ~15 lines, DeltaNotFoundError |
| [x] | 1.4 | Extract `prime_review` | — | ~120 lines, config via _load_config |
| [x] | 1.5 | Extract `complete_review` | — | ~100 lines, approval guard, auto_teardown |
| [x] | 1.6 | Extract `disposition_finding` | — | Typed kwargs, hard validation only |
| [x] | 1.7 | Extract `teardown_review` | — | ~15 lines |
| [x] | 1.8 | Implement `summarize_review` | — | New operation, reads findings+index |
| [x] | 1.9 | Refactor CLI commands to thin wrappers | — | Deleted _do_teardown, helpers migrated |
| [x] | 1.10 | Run existing tests (regression) | — | 69 passed (matches baseline) |
| [x] | 1.11 | Write `operations_test.py` | — | 33 unit tests, all passing |
| [x] | 1.12 | Lint + format | — | 4640 passed, 0 failures, clean lint |

### Task Details

- **1.1 Run existing tests (baseline)**
  - **Testing**: `uv run pytest supekku/cli/workflow_review_test.py supekku/cli/workflow_integration_test.py -v`
  - **Notes**: Record exact pass/fail count. This is the regression baseline.

- **1.2 Create `operations.py` with new types**
  - **Files**: `spec_driver/orchestration/operations.py`
  - **Design**: Define `PrimeAction` (StrEnum), `PrimeResult`, `CompleteResult`, `DispositionResult`, `TeardownResult`, `ReviewSummary` (dataclasses). Define `DeltaNotFoundError`, `ReviewApprovalGuardError`, `FindingNotFoundError`, `DispositionValidationError` exceptions. Per DR-124 §4.1, §4.3.

- **1.3 Extract `resolve_delta_dir`**
  - **Design**: Move logic from `supekku/cli/workflow.py:_resolve_delta_dir`. Change `typer.Exit` to `DeltaNotFoundError`. Accept `repo_root: Path`. ~15 lines.
  - **Files**: `operations.py` (add), `workflow.py` (replace `_resolve_delta_dir` calls)

- **1.4 Extract `prime_review`**
  - **Design**: Move logic from `review_prime_command`. Strip CLI concerns (typer.echo, json formatting, exit codes). Load config internally. Return `PrimeResult` with typed enum fields. Per DR-124 §4.1.
  - **Files**: `operations.py` (add), `workflow.py` (refactor `review_prime_command`)
  - **Helpers to move**: `_prime_action` (becomes `PrimeAction` mapping), `_build_domain_map`, `_generate_bootstrap_markdown`

- **1.5 Extract `complete_review`**
  - **Design**: Move logic from `review_complete_command`. Add `auto_teardown: bool = True` parameter. Return `CompleteResult` with `removed_files`. Raise `ReviewApprovalGuardError` instead of `typer.Exit`. Per DR-124 §4.1, DEC-124-009.
  - **Files**: `operations.py` (add), `workflow.py` (refactor `review_complete_command`)

- **1.6 Extract `disposition_finding`**
  - **Design**: Typed kwargs per DEC-124-010. Domain validation per DR-109 §3.4 validity matrix (DEC-124-011). Finding needs blocking/non-blocking context for validation — look up finding in rounds data to determine category. Raise `DispositionValidationError` for constraint violations. Raise `FindingNotFoundError` (with available IDs) instead of returning bool.
  - **Files**: `operations.py` (add), `workflow.py` (refactor `_disposition_finding` and per-action commands)

- **1.7 Extract `teardown_review`**
  - **Design**: Move logic from `_do_teardown`. Return `TeardownResult`. ~15 lines.
  - **Files**: `operations.py` (add), `workflow.py` (refactor `review_teardown_command`)

- **1.8 Implement `summarize_review`**
  - **Design**: New operation per DEC-124-012. Read findings + review-index. Count blocking/non-blocking. Call `collect_blocking_findings` + `can_approve`. Derive `outcome_ready` from judgment status. Return `ReviewSummary`.
  - **Files**: `operations.py` (add)
  - **Testing**: Fixture-based — create temp workflow dirs with known findings data

- **1.9 Refactor CLI commands**
  - **Design**: Each CLI command becomes: parse args → call operation → format output → exit. Remove all orchestration logic from CLI. Per DR-124 §4.4. Delete moved helpers (`_prime_action`, `_build_domain_map`, `_generate_bootstrap_markdown`, `_do_teardown`). Keep `_load_workflow_config` (shared with non-review commands).
  - **Files**: `supekku/cli/workflow.py`

- **1.10 Run existing tests (regression)**
  - **Testing**: Same command as 1.1. Must produce identical pass/fail count.

- **1.11 Write `operations_test.py`**
  - **Files**: `spec_driver/orchestration/operations_test.py`
  - **Testing**: Per IP-124 §6 key scenarios. Use temp dirs with fixture YAML data. Test each operation's happy path and error paths.

- **1.12 Lint + format**
  - **Testing**: `just check`. Zero warnings.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|---|---|---|
| `_load_workflow_config` import creates circular dependency | It wraps `supekku.scripts.lib.core.config.load_workflow_config` — import that directly if needed | resolved — no circular dep |
| `_generate_bootstrap_markdown` has hidden CLI dependency | Code review during extraction; it only uses data params | resolved — pure function |
| Disposition validation needs finding category (blocking/non-blocking) | Look up finding in rounds data before applying validation rules | resolved — `_find_finding_with_category` helper; hard constraints only at disposition time |

## 9. Decisions & Outcomes

- 2026-03-23 — Phase plan created per DR-124 post-adversarial review
- 2026-03-23 — Phase 1 implemented. Key design decisions during execution:
  - Disposition validation (DEC-124-011): hard constraints only at disposition time (rationale for waive/defer, superseded_by for supersede). Blocking-specific constraints (authority=user, backlog_ref, resolved_at) remain approval-time guards via `can_approve`. This preserves existing CLI behavior where dispositions are always written and the guard catches invalid ones at approval.
  - `_load_workflow_config` → imported directly as `load_workflow_config` from `supekku.scripts.lib.core.config`. No circular dependency — confirmed.
  - `_generate_bootstrap_markdown` — pure function, no hidden CLI deps. Moved cleanly.
  - `_extract_delta_id` — shared utility for all operations to derive `DE-NNN` from dir name.
  - `PrimeAction` mapping: `BootstrapStatus.WARM` (no staleness triggers) maps to `CREATED`, same as `COLD`. Only `REUSABLE` maps to `REFRESHED`.

## 10. Findings / Research Notes

- `evaluate_staleness` returns `WARM` (not `REUSABLE`) when no staleness triggers are detected. Both `WARM` and `COLD` map to `PrimeAction.CREATED`. `REUSABLE` only occurs when there ARE staleness triggers but the cache is deemed reusable for incremental update.
- `init_state` requires `timestamps` field and `phase.status` uses underscore convention (`in_progress`), not hyphen (`in-progress`). Test fixtures must use `init_state()` + `update_state_workflow()` — hand-crafted YAML won't pass validation.
- The `finding_list_command` was NOT refactored (no corresponding operation — it's a direct read, not an orchestration path). This is correct per DR-124 scope.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Regression tests match baseline (69/69)
- [x] New operations tests pass (33/33)
- [x] Full test suite clean (4640 passed)
- [x] Lint clean on changed files
- [x] Notes updated with implementation observations
