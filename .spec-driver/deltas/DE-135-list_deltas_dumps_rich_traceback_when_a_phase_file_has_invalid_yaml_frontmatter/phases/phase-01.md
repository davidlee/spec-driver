---
id: IP-135-P01
slug: "135-list_deltas_dumps_rich_traceback_when_a_phase_file_has_invalid_yaml_frontmatter-phase-01"
name: IP-135 Phase 01
created: "2026-05-01"
updated: "2026-05-01"
status: completed
kind: phase
plan: IP-135
delta: DE-135
objective: Add MarkdownLoadError translation to load_markdown_file with unit + integration coverage.
---

# IP-135-P01 — Implement MarkdownLoadError + tests

## 1. Objective

Translate PyYAML parse errors at the source (`load_markdown_file` in `core/spec_utils.py`) into a single `MarkdownLoadError(ValueError)` carrying file path and YAML line/column. Land matching unit + integration coverage. No call-site edits.

## 2. Links & References

- **Delta**: DE-135
- **Design Revision**: DR-135 §3 (Architecture Intent), §4 (Code Impact Summary), §5 (Verification Alignment), §7 (Decisions)
- **Issue**: ISSUE-054 (user repro)
- **Requirement**: PROD-010.FR-010
- **Policy / Standard**: POL-001 (reuse over sprawl); STD-003 (utility placement)
- **Precedent**: `supekku/scripts/lib/core/frontmatter_schema.py:FrontmatterValidationError(ValueError)`

## 3. Entrance Criteria

- [x] DR-135 approved (open questions resolved)
- [x] DE-135 status moves to in_progress at start of execution
- [x] Repo clean enough to commit a small targeted change

## 4. Exit Criteria / Done When

- [x] `core/spec_utils.py` defines `MarkdownLoadError(ValueError)`
- [x] `load_markdown_file` wraps `frontmatter.loads(text)` in `try/except yaml.YAMLError`, raising `MarkdownLoadError` with path and (when `problem_mark` available) line/column, chaining via `from exc`
- [x] VT-DR135-001 lands and passes (`supekku/scripts/lib/spec_utils_test.py`)
- [x] VT-DR135-002 lands and passes (`supekku/cli/list_test.py::ListDeltasMalformedFrontmatterTest`, default + `--json`)
- [x] `uv run python -m pytest supekku` — 4788 passed, 4 pre-existing skips
- [x] `uv run ruff check supekku` — clean
- [x] `uv run python -m supekku.scripts.pylint_report` on touched files — no new warnings vs baseline
- [x] Manual repro of ISSUE-054 produces a one-line stderr warning (no Python traceback) and `list deltas` exits 0
- [x] DE-135 §8 follow-ups note for `requirements/sync.py` deferral — present

## 5. Verification

- Unit: `just test` covering VT-DR135-001 (helper-level).
- Integration: `just test` covering VT-DR135-002 (CLI `list deltas` path, default + machine-readable).
- Manual: edit a phase file under any DE-* to introduce malformed YAML; run `uv run spec-driver list deltas`; confirm friendly stderr warning and exit 0; revert.
- Lint: `just lint`; `just pylint-files supekku/scripts/lib/core/spec_utils.py <test files>`.

## 6. Assumptions & STOP Conditions

- **Assumption**: `frontmatter.loads()` raises only `yaml.YAMLError` subclasses for malformed YAML. If integration testing reveals a different exception class (e.g. a `frontmatter`-specific error), STOP and revisit DR-135 §3.
- **Assumption**: existing change-artifact fixtures in tests can be reused; no new fixture infrastructure needed.
- **STOP when**: the `--format json` integration test reveals stderr mixing into stdout (would expose a separate CLI defect outside this delta's scope).

## 7. Tasks & Progress

_(Status: `[ ]` todo, `[WIP]`, `[x]` done, `[blocked]`)_

| Status | ID  | Description                                                                  | Parallel? | Notes                            |
| ------ | --- | ---------------------------------------------------------------------------- | --------- | -------------------------------- |
| [x]    | 1.1 | Add `MarkdownLoadError` class and YAML-error wrapping in `core/spec_utils.py` | [ ]       | Done; see `core/spec_utils.py`. Also added scoped warning at `changes/artifacts.py:181` (DR-135 adjustment, see §9). |
| [x]    | 1.2 | Add VT-DR135-001 (unit) for `load_markdown_file` malformed-YAML path         | [P]       | `supekku/scripts/lib/spec_utils_test.py::test_load_markdown_file_raises_friendly_error_on_malformed_yaml` |
| [x]    | 1.3 | Add VT-DR135-002 (integration) for `list deltas` (default + machine-readable) | [P]       | `supekku/cli/list_test.py::ListDeltasMalformedFrontmatterTest` (2 cases) |
| [x]    | 1.4 | Run `just test`, `just lint`, `just pylint-files` on touched paths           | [ ]       | All clean. 4788 tests pass; ruff clean; pylint baseline preserved. |
| [x]    | 1.5 | Manual repro: malformed phase YAML → friendly warning, no traceback          | [ ]       | Confirmed on `.spec-driver/deltas/DE-010-.../phases/phase-03.md`; file restored from backup. |

### Task Details

- **1.1 Add `MarkdownLoadError` and translate `yaml.YAMLError` in `load_markdown_file`**
  - **Design / Approach**: per DR-135 §4. Add class above `load_markdown_file`. Wrap only the `frontmatter.loads(text)` call. Use `getattr(exc, "problem_mark", None)` and only append " at line N, column M" when present (using `mark.line + 1` / `mark.column + 1` for 1-based reporting). Message: `f"invalid YAML frontmatter in {path}{where}: {exc.__class__.__name__}"`. Chain via `from exc`.
  - **Files / Components**: `supekku/scripts/lib/core/spec_utils.py`.
  - **Testing**: covered by 1.2 and 1.3.

- **1.2 VT-DR135-001 — unit coverage of helper**
  - **Design / Approach**: `core/spec_utils_test.py` (or sibling — check current location of `load_markdown_file` tests first to avoid sprawl). Build a tempfile with deliberately malformed YAML frontmatter (unquoted colon inside a value reproduces the ScannerError from ISSUE-054). Assert `pytest.raises(MarkdownLoadError)`; assert message substrings: file path, "invalid YAML frontmatter", `line` and `column` markers; assert `isinstance(exc.value.__cause__, yaml.YAMLError)`.
  - **Files / Components**: test file colocated with `load_markdown_file`'s existing tests.
  - **Testing**: self.

- **1.3 VT-DR135-002 — integration coverage of `list deltas`**
  - **Design / Approach**: probe existing fixtures in `changes/completion_test.py` and CLI tests for a reusable temp-workspace helper before rolling new infrastructure (POL-001). Workspace contains one well-formed delta and one delta whose phase file has malformed YAML frontmatter. Invoke the `list deltas` CLI handler (or its function-level equivalent) twice: default and `--format json` (or whichever machine-readable mode the command exposes — confirm against `cli/list/deltas.py`). For both runs assert: exit code 0; stderr contains the friendly skip warning naming the bad file path and a YAML location; stdout has no Python traceback; the JSON run yields valid JSON; the good delta still appears in stdout.
  - **Files / Components**: integration test under `changes/` or the CLI test tree, depending on what the existing pattern is. New imports of `MarkdownLoadError` not required at the test level — assertions are on observable CLI output.
  - **Testing**: self.

- **1.4 Local checks**
  - Run `just test`, `just lint`, `just pylint-files supekku/scripts/lib/core/spec_utils.py <new test files>` — all clean before opening PR / closing phase.

- **1.5 Manual repro**
  - Temporarily edit a real phase file (`.spec-driver/deltas/DE-XXX/phases/phase-0N.md`) to introduce a malformed line; run `uv run spec-driver list deltas`; capture before/after output; revert the edit. Reference in commit message.

## 8. Risks & Mitigations

| Risk                                                                  | Mitigation                                                                                                                            | Status |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| `frontmatter.loads` raises a non-`YAMLError` for some malformations.  | If 1.3 triggers an uncaught exception class, STOP and revisit DR-135 §3 before broadening the catch.                                  | resolved — repro and unit test confirm `yaml.YAMLError` (`ScannerError`) is the path |
| Integration test wording becomes brittle.                             | Assert on stable substrings (path, "invalid YAML frontmatter", "line"), not full sentence.                                            | resolved — assertions use substring matching only |
| Test for `--format json` exposes stderr leakage into stdout.          | If observed, raise a separate ISSUE; do not expand DE-135's scope mid-flight.                                                         | resolved — `--json` test passes; stderr/stdout cleanly separated |

## 9. Decisions & Outcomes

- 2026-05-01 — single phase chosen; design is settled and the change is one source file plus tests (per DR-135).
- 2026-05-01 — `requirements/sync.py:77` deferred to a follow-up issue rather than expanded into this delta (per DR-135 §3 / §8).
- 2026-05-01 — DR-135 originally claimed "no call-site edits". Implementation revealed that the existing `Console(stderr=True)` block in `changes/registry.py:87` only fires for top-level artifact files; phase-file YAML errors at `changes/artifacts.py:181` were silently swallowed. Added a single, scoped 2-line stderr warning at that site to deliver the actionable diagnostic PROD-010.FR-010 requires. DR-135 §3 / §4 updated to reflect this.

## 10. Findings / Research Notes

- Existing `load_markdown_file` tests live in `supekku/scripts/lib/spec_utils_test.py` (legacy root location, imports from `lib.core.spec_utils`); chose to colocate VT-DR135-001 with them instead of the much smaller `core/spec_utils_test.py`.
- Reused `ListFilterBackfillTest`'s temp-workspace pattern in `supekku/cli/list_test.py` for VT-DR135-002 — no new fixture infrastructure needed (POL-001).
- `CliRunner(mix_stderr=False)` is rejected by the current Click pin in this repo. Captured as `mem.fact.cli.clirunner-no-mix-stderr`.
- `MarkdownLoadError(ValueError)` invariant captured as `mem.fact.core.markdown-load-error-taxonomy`.
- Independently observed during preflight: `uv run spec-driver show memory <id>` itself dumps a Rich traceback when a memory's `provenance.sources` is a list of strings rather than dicts (`memory_formatters.py:117`). Same family bug, different module — separate ISSUE candidate, not bundled here.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored — test names in §7 and §4; commits pending
- [x] DE-135 / DR-135 / IP-135 reconciled with the call-site adjustment
- [x] Hand-off notes captured in `notes.md` for `/audit-change` → `/close-change`
