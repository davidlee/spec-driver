# Notes for DE-135

## Status

- 2026-05-01 — Phase IP-135-P01 implementation complete; all exit criteria met locally. Awaiting `/audit-change` and `/close-change` handoff.

## What's done

- `supekku/scripts/lib/core/spec_utils.py` — added `MarkdownLoadError(ValueError)`; `load_markdown_file` now wraps `frontmatter.loads(text)` in `try/except yaml.YAMLError`, raising `MarkdownLoadError` with file path and (when `problem_mark` is present) 1-based line/column. Original PyYAML exception preserved as `__cause__`.
- `supekku/scripts/lib/changes/artifacts.py` — added a one-line `Console(stderr=True)` warning before the existing `continue` in the per-phase-file `except (ValueError, OSError)` clause. Necessary because the existing skip-and-warn block in `changes/registry.py` only fires for top-level artifact files; phase files inside a delta bundle's `phases/` dir went through this silent path.
- VT-DR135-001 (unit) — `supekku/scripts/lib/spec_utils_test.py::test_load_markdown_file_raises_friendly_error_on_malformed_yaml`.
- VT-DR135-002 (integration) — `supekku/cli/list_test.py::ListDeltasMalformedFrontmatterTest`, two cases (default and `--json`).
- Manual repro against a real phase file in `.spec-driver/deltas/DE-010-.../phases/phase-03.md` — confirmed friendly stderr WARNING with path + line/column, no Python traceback, exit 0, full delta list rendered. File restored from backup.

## Surprises / adaptations

- DR-135 originally claimed "no call-site edits" because the existing `Console(stderr=True)` block in `changes/registry.py:87` would catch everything. Wrong: that block only fires for top-level delta/revision/audit files. The actual ISSUE-054 path is a *phase* file, hit at `artifacts.py:181`, which silently `continue`s with no diagnostic. Adjusted DR-135 §3 / §4 and added a single, scoped call-site edit to deliver the actionable warning the user requested. User explicitly approved option 2 over silent skip.
- `CliRunner(mix_stderr=False)` — initial test used this kwarg; current Click version in the repo no longer accepts it. Plain `CliRunner()` already separates `result.stdout` / `result.stderr`. Worth knowing for future CLI integration tests.
- `pylint-report` flagged a `redefined-outer-name` for my local `msg`; renamed to `detail` to keep the file's pre-existing baseline of 4 (rather than adding a 5th). The pre-existing `msg` and `frontmatter` shadowings on lines 11/17 are out of scope for this delta.

## Rough edges / follow-ups

- `requirements/sync.py:77` still catches only `OSError`. A malformed backlog item file would still leak a YAML traceback there. Off the ISSUE-054 path; deferred per DR-135 §3 ("sites that still leak"). Worth a small follow-up issue.
- Sites already catching `Exception` (`backlog/registry.py`, `validation/validator.py`, `changes/registry.py:discover_plans`) could be migrated to catch `MarkdownLoadError` for tighter intent. Not urgent.
- Independently noticed during preflight: `uv run spec-driver show memory <id>` itself dumps a Rich traceback when a memory's `provenance.sources` is a list of strings rather than dicts (`memory_formatters.py:117` does `src.get("kind", "")` on a `str`). Same family of "loader/formatter throws to user", different module. Not in this delta — separate ISSUE candidate.
- Pre-existing `Warning: spec-driver may need re-install (workflow.toml has 0.9.2, running 0.9.3)` is unrelated noise from the dev environment; ignored.

## Durable facts / memory candidates

- **`MarkdownLoadError` taxonomy decision** (DEC-DR135-002 in DR-135): make markdown-load errors a `ValueError` subclass so existing `except (ValueError, OSError)` clauses stay correct. Pairs with the existing `FrontmatterValidationError(ValueError)` precedent in `core/frontmatter_schema.py`. Worth a memory record so future agents touching `core/spec_utils.py` don't break the contract.
- **`CliRunner` no longer accepts `mix_stderr`** in the current Click pinned by this repo — stderr is split by default; passing the kwarg is a `TypeError`. Not previously captured in memory; would save a future agent ~10 minutes of test-debugging.
- **PyYAML `problem_mark`** — not always present on `yaml.YAMLError` subclasses; use `getattr(exc, "problem_mark", None)` and guard. Mark line/column are 0-based; surface as 1-based for UX consistency.

## Verification

- `uv run python -m pytest supekku` — 4788 passed, 4 pre-existing skips. ✓
- `uv run ruff check supekku` — clean. ✓
- `uv run python -m supekku.scripts.pylint_report` (touched files) — no new warnings vs baseline. ✓
- Manual ISSUE-054 repro — friendly diagnostic, no traceback. ✓

## Commits

- All work currently uncommitted. Touched files:
  - `supekku/scripts/lib/core/spec_utils.py`
  - `supekku/scripts/lib/changes/artifacts.py`
  - `supekku/scripts/lib/spec_utils_test.py`
  - `supekku/cli/list_test.py`
  - `.spec-driver/backlog/issues/ISSUE-054-.../ISSUE-054.md` (new)
  - `.spec-driver/deltas/DE-135-.../{DE-135.md, DR-135.md, IP-135.md, notes.md, phases/phase-01.md}` (new)
- Per repo doctrine: small frequent commits preferred. Code + workflow artefacts are tightly coupled in this delta; a single commit covering everything is appropriate (or two — workflow first, code second — either is fine).
