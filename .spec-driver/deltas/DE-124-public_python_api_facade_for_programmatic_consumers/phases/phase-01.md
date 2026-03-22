---
id: IP-124-P01
slug: "124-public_python_api_facade_for_programmatic_consumers-phase-01"
name: "Extract operations and refactor CLI"
created: "2026-03-23"
updated: "2026-03-23"
status: draft
kind: phase
plan: IP-124
delta: DE-124
---

# Phase 1 — Extract operations and refactor CLI

## 1. Objective

Extract review orchestration logic from CLI command functions into `supekku/scripts/lib/workflow/operations.py`. Refactor CLI review commands to thin wrappers. Add unit tests for all operations. This is the high-risk phase — existing CLI behaviour must be preserved exactly.

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

- [ ] `operations.py` contains all 6 operations: `resolve_delta_dir`, `prime_review`, `complete_review`, `disposition_finding`, `teardown_review`, `summarize_review`
- [ ] All result dataclasses use typed enums (DEC-124-003)
- [ ] `disposition_finding` uses typed kwargs and domain validation per DR-109 matrix (DEC-124-010, DEC-124-011)
- [ ] `complete_review` has `auto_teardown` parameter (DEC-124-009)
- [ ] CLI review commands refactored to thin wrappers (~20-30 lines each)
- [ ] All existing CLI tests pass without modification
- [ ] `operations_test.py` with unit tests for all 6 operations
- [ ] `just check` passes (lint, format, tests)

## 5. Verification

- Run existing tests first (baseline): `uv run pytest supekku/cli/workflow_review_test.py supekku/cli/workflow_integration_test.py -v`
- Run after extraction (regression): same command, expect identical results
- Run new tests: `uv run pytest supekku/scripts/lib/workflow/operations_test.py -v`
- Lint: `uv run ruff check supekku/scripts/lib/workflow/operations.py supekku/cli/workflow.py`
- Full suite: `just check`

## 6. Assumptions & STOP Conditions

- **Assumption**: `_load_workflow_config` can be imported by `operations.py` from the CLI module without creating circular dependencies. If not, extract to `supekku/scripts/lib/core/config.py` (it already wraps `load_workflow_config` from there).
- **Assumption**: `_build_domain_map` and `_generate_bootstrap_markdown` are purely self-contained — no hidden CLI dependencies.
- **STOP**: If extracting any helper reveals hidden state or side effects not visible in the current code reading.
- **STOP**: If any existing CLI test fails after extraction — do not proceed until resolved.

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
|---|---|---|---|---|
| [ ] | 1.1 | Run existing tests (baseline) | — | Capture pass count |
| [ ] | 1.2 | Create `operations.py` with new types | — | Enums, dataclasses, exceptions |
| [ ] | 1.3 | Extract `resolve_delta_dir` | — | From CLI `_resolve_delta_dir` |
| [ ] | 1.4 | Extract `prime_review` | — | Largest extraction (~120 lines) |
| [ ] | 1.5 | Extract `complete_review` | — | ~150 lines, approval guard, teardown |
| [ ] | 1.6 | Extract `disposition_finding` | — | Typed kwargs, domain validation |
| [ ] | 1.7 | Extract `teardown_review` | — | Trivial (~20 lines) |
| [ ] | 1.8 | Implement `summarize_review` | — | New operation, no CLI equivalent |
| [ ] | 1.9 | Refactor CLI commands to thin wrappers | — | After all operations extracted |
| [ ] | 1.10 | Run existing tests (regression) | — | Must match baseline |
| [ ] | 1.11 | Write `operations_test.py` | — | Unit tests for all 6 operations |
| [ ] | 1.12 | Lint + format | — | `just check` |

### Task Details

- **1.1 Run existing tests (baseline)**
  - **Testing**: `uv run pytest supekku/cli/workflow_review_test.py supekku/cli/workflow_integration_test.py -v`
  - **Notes**: Record exact pass/fail count. This is the regression baseline.

- **1.2 Create `operations.py` with new types**
  - **Files**: `supekku/scripts/lib/workflow/operations.py`
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
  - **Files**: `supekku/scripts/lib/workflow/operations_test.py`
  - **Testing**: Per IP-124 §6 key scenarios. Use temp dirs with fixture YAML data. Test each operation's happy path and error paths.

- **1.12 Lint + format**
  - **Testing**: `just check`. Zero warnings.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|---|---|---|
| `_load_workflow_config` import creates circular dependency | It wraps `supekku.scripts.lib.core.config.load_workflow_config` — import that directly if needed | open |
| `_generate_bootstrap_markdown` has hidden CLI dependency | Code review during extraction; it only uses data params | open |
| Disposition validation needs finding category (blocking/non-blocking) | Look up finding in rounds data before applying validation rules | open |

## 9. Decisions & Outcomes

- 2026-03-23 — Phase plan created per DR-124 post-adversarial review

## 10. Findings / Research Notes

_Populated during execution._

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Regression tests match baseline
- [ ] New operations tests pass
- [ ] `just check` clean
- [ ] Notes updated with implementation observations
