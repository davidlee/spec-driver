---
id: IP-039.PHASE-03
slug: 039-workflow_command_surface_completion_and_strict_mode_lock_in-phase-03
name: IP-039 Phase 03
created: '2026-03-04'
updated: '2026-03-04'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-039.PHASE-03
plan: IP-039
delta: DE-039
objective: >-
  Implement strict_mode config loading and runtime enforcement at bypass
  touchpoints in complete-delta, preserving permissive default behavior.
entrance_criteria:
  - Phase 2 complete (create audit + complete revision verified)
  - Strict-mode policy decisions locked (DEC-039-01, DEC-039-04)
  - No strict_mode runtime code exists yet (greenfield)
exit_criteria:
  - strict_mode loads from workflow.toml with default false
  - strict_mode=true blocks --force, --skip-sync, --skip-update-requirements in complete delta
  - strict_mode=true blocks SPEC_DRIVER_ENFORCE_COVERAGE=false
  - Permissive default behavior preserved (all existing tests pass)
  - VT-039-001 tests pass
verification:
  tests:
    - uv run pytest -q supekku/scripts/lib/core/config_test.py -k strict
    - uv run pytest -q supekku/scripts/complete_delta_test.py -k strict
  evidence:
    - VT-039-001
tasks:
  - id: 3.1
    title: Add strict_mode to config defaults and accessor
    status: done
  - id: 3.2
    title: Add strict-mode gate in complete_delta()
    status: done
  - id: 3.3
    title: Gate SPEC_DRIVER_ENFORCE_COVERAGE=false under strict mode
    status: done
  - id: 3.4
    title: Write tests for config and enforcement paths
    status: done
  - id: 3.5
    title: Run verification, lint, update evidence
    status: done
risks:
  - risk: Strict-mode gate breaks existing permissive-mode tests
    mitigation: Gate is only active when strict_mode=true; default is false. Existing tests unaffected.
  - risk: Enforcement messages diverge from coverage_check messaging style
    mitigation: Follow existing format_coverage_error() patterns for consistency.
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-039.PHASE-03
entrance_criteria:
  - item: "Phase 2 complete (create audit + complete revision verified)"
    completed: true
  - item: "Strict-mode policy decisions locked (DEC-039-01, DEC-039-04)"
    completed: true
  - item: "No strict_mode runtime code exists yet (greenfield)"
    completed: true
exit_criteria:
  - item: "strict_mode loads from workflow.toml with default false"
    completed: true
  - item: "strict_mode=true blocks bypass flags in complete delta"
    completed: true
  - item: "Permissive default behavior preserved"
    completed: true
  - item: "VT-039-001 tests pass"
    completed: true
```

# Phase 03 — Strict-Mode Runtime Wiring

## 1. Objective
Implement `strict_mode` as a runtime config boolean loaded from `.spec-driver/workflow.toml`.
When enabled, gate all force-style bypass paths in `complete delta` with hard-fail errors.
Default: `false` (permissive — no behavioral change unless opt-in).

## 2. Links & References
- **Delta**: DE-039
- **Design Revision**: DR-039 §4 (code impact: `config.py`, `complete_delta.py`), §7 (DEC-039-01, DEC-039-04)
- **Specs / PRODs**:
  - PROD-016.FR-002 — strict-mode runtime branching contract
- **Existing Infrastructure**:
  - Config loader: `supekku/scripts/lib/core/config.py` (`load_workflow_config()`, `DEFAULT_CONFIG`)
  - Config tests: `supekku/scripts/lib/core/config_test.py`
  - Enforcement touchpoint: `supekku/scripts/complete_delta.py:complete_delta()`
  - Coverage enforcement: `supekku/scripts/lib/changes/coverage_check.py` (`is_coverage_enforcement_enabled()`)

## 3. Entrance Criteria
- [x] Phase 2 complete — commit `1d6fc0e`
- [x] Strict-mode policy locked (DEC-039-01: single boolean; DEC-039-04: universal bypass block)
- [x] No existing strict_mode runtime code (confirmed: zero `.py` references)

## 4. Exit Criteria / Done When
- [x] `strict_mode` key in `DEFAULT_CONFIG` with default `false`
- [x] `is_strict_mode(config)` accessor function exported from `config.py`
- [x] `complete delta --force` fails with error when `strict_mode=true`
- [x] `complete delta --skip-sync` fails with error when `strict_mode=true`
- [x] `complete delta --skip-update-requirements` fails with error when `strict_mode=true`
- [x] `SPEC_DRIVER_ENFORCE_COVERAGE=false` fails with error when `strict_mode=true`
- [x] All existing tests still pass (permissive default preserved)
- [x] `just lint` and `just pylint` clean on changed files

## 5. Verification
- `uv run pytest -q supekku/scripts/lib/core/config_test.py -k strict`
- `uv run pytest -q supekku/scripts/complete_delta_test.py -k strict`
- `uv run pytest -q` (full suite regression)
- `uv run ruff check` on all changed files
- `uv run pylint --indent-string "  "` on changed production files
- Evidence: VT-039-001 test output

## 6. Assumptions & STOP Conditions
- Assumptions:
  - Single boolean `strict_mode` is sufficient (per DEC-039-01).
  - `--dry-run` is NOT gated (it's non-destructive, safe in strict mode).
  - Only `complete delta` bypass paths are gated in this phase. Other commands can be extended later.
- STOP when:
  - If `strict_mode` needs per-flag granularity (contradicts DEC-039-01) — escalate.
  - If coverage_check.py refactor needed to support strict mode cleanly — escalate.

## 7. Tasks & Progress
*(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)*

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 3.1 | Add `strict_mode` to config defaults and accessor | [x] | `strict_mode: False` in DEFAULT_CONFIG, `is_strict_mode()` pure fn |
| [x] | 3.2 | Add strict-mode gate in `complete_delta()` | [ ] | Early-return gate after workspace load; blocks --force/--skip-sync/--skip-update-requirements |
| [x] | 3.3 | Gate `SPEC_DRIVER_ENFORCE_COVERAGE=false` under strict mode | [ ] | Gated at call site in complete_delta.py, not in coverage_check.py |
| [x] | 3.4 | Write tests for config and enforcement paths | [x] | 7 config tests + 4 strict enforcement + 3 permissive regression |
| [x] | 3.5 | Run verification, lint, update evidence | [ ] | ruff clean, pylint 9.93, 2233 passed |

### Task Details

- **3.1 — Add `strict_mode` to config defaults and accessor**
  - **Location**: `supekku/scripts/lib/core/config.py`
  - **Changes**:
    - Add `"strict_mode": False` as top-level key in `DEFAULT_CONFIG` (same level as `ceremony`)
    - Add `is_strict_mode(config: dict) -> bool` pure function
    - Export in `__all__`
  - **Pattern**: follows existing `DEFAULT_CONFIG` structure; scalar at root level like `ceremony`

- **3.2 — Add strict-mode gate in `complete_delta()`**
  - **Location**: `supekku/scripts/complete_delta.py`, early in `complete_delta()` (after workspace load, before flag-dependent branching)
  - **Logic**:
    ```python
    config = load_workflow_config(workspace.root)
    if is_strict_mode(config):
        if force:
            print("Error: --force is not permitted in strict mode", file=sys.stderr)
            return 1
        if not update_requirements:
            print("Error: --skip-update-requirements is not permitted in strict mode", file=sys.stderr)
            return 1
        if skip_sync:
            print("Error: --skip-sync is not permitted in strict mode", file=sys.stderr)
            return 1
    ```
  - **Note**: `--dry-run` is NOT gated (non-destructive).

- **3.3 — Gate `SPEC_DRIVER_ENFORCE_COVERAGE=false` under strict mode**
  - **Location**: `supekku/scripts/complete_delta.py` (in the coverage check block, lines ~477–485)
  - **Logic**: When `strict_mode=true` and `is_coverage_enforcement_enabled()` returns `False`, print error and return 1.
  - **Alternative**: Could gate in `coverage_check.py:is_coverage_enforcement_enabled()` itself, but that changes a widely-used function. Prefer gating at the call site in `complete_delta.py` for clarity.

- **3.4 — Write tests**
  - **Config tests** (`supekku/scripts/lib/core/config_test.py`):
    - `strict_mode` defaults to `False`
    - `strict_mode=true` in workflow.toml loads correctly
    - `is_strict_mode()` returns correct value
  - **Enforcement tests** (`supekku/scripts/complete_delta_test.py`):
    - `--force` with `strict_mode=true` → exit code 1 with error message
    - `--skip-sync` with `strict_mode=true` → exit code 1
    - `--skip-update-requirements` with `strict_mode=true` → exit code 1
    - `SPEC_DRIVER_ENFORCE_COVERAGE=false` with `strict_mode=true` → exit code 1
    - Permissive mode (default) → all flags work as before (regression)
  - **Fixture approach**: Use `tmp_path` with workflow.toml containing `strict_mode = true`, mock or set workspace root.

- **3.5 — Verification**
  - Run `just lint` + `just pylint` on all changed files.
  - Run `just test` for full suite.
  - Update VT-039-001 status to `verified` in IP-039.
  - Update this phase sheet with evidence and task notes.

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| Strict-mode gate breaks existing permissive tests | Gate only active when strict_mode=true; default false | Closed — 2233 tests pass |
| Error messaging inconsistent with coverage_check | Follow existing format_coverage_error() patterns | Closed — consistent "Error: X is not permitted in strict mode" |
| Config deep-merge drops strict_mode key | Test explicitly; key is top-level scalar, not nested | Closed — 7 config tests verify |

## 9. Decisions & Outcomes
- Placed strict-mode flag gate immediately after `Workspace.from_cwd()` — earliest viable point, before any flag-dependent branching.
- Coverage env var gate placed at call site in `complete_delta.py` (not in `coverage_check.py`) to avoid changing a widely-used utility.
- Error messages use consistent "Error: X is not permitted in strict mode" pattern, printed to stderr.

## 10. Findings / Research Notes
- `DEFAULT_CONFIG` in `config.py` has ~11 top-level keys. `ceremony` is the only non-dict scalar — `strict_mode` will be the second.
- `load_workflow_config()` deep-merges one level; top-level scalars are simple overrides (no merge complexity).
- `complete_delta()` takes `force`, `skip_sync`, `update_requirements` as kwargs — gate is a simple early-return block.
- `is_coverage_enforcement_enabled()` reads `SPEC_DRIVER_ENFORCE_COVERAGE` env var. Strict-mode gate should happen at call site, not inside this function.
- Existing `complete_delta_test.py` tests exist and cover the main flow.

## 11. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Verification evidence stored (ruff clean, pylint 9.93/10, 2233 passed)
- [x] Phase sheet updated with task notes and outcomes
- [x] Hand-off notes to next phase: no additional implementation phase; proceed to DE-039 closure.
