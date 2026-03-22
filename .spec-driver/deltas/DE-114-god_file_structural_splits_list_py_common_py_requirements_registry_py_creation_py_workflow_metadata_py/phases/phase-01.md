---
id: IP-114-P01
slug: "114-cli_layer_split_common_and_list-phase-01"
name: "CLI layer: split common.py and list.py"
created: "2026-03-22"
updated: "2026-03-22"
status: draft
kind: phase
plan: IP-114
delta: DE-114
---

# Phase 01 — CLI layer: split common.py and list.py

## 1. Objective

Split `cli/common.py` (1,124 lines) into 4 files and `cli/list.py` (3,195 lines) into a `cli/list/` package with 10 files. All files ≤500 lines (one exception: `backlog_items.py` at ~540). Zero behaviour change.

## 2. Links & References

- **Delta**: DE-114
- **Design Revision**: DR-114 §4a (list), §4b (common)
- **Specs**: SPEC-110

## 3. Entrance Criteria

- [x] DR-114 accepted (3 adversarial passes)
- [x] IP-114 accepted

## 4. Exit Criteria / Done When

- [ ] `cli/common.py` ≤350 lines, re-exports all public symbols
- [ ] `cli/artifacts.py`, `cli/ids.py`, `cli/io.py` exist with correct content
- [ ] `cli/list/` package exists with 10 files, all ≤540 lines
- [ ] `from supekku.cli.list import app` still works (backward compat)
- [ ] `ruff check supekku` — zero new errors in changed files
- [ ] `pytest supekku` — all tests pass (excluding pre-existing DE-123 failures)
- [ ] `grep` confirms no stale imports of moved symbols

## 5. Verification

- `uv run ruff check supekku/cli/` — lint changed files
- `uv run python -m pytest supekku -q` — full suite
- `wc -l` on all new/modified files — size check
- `grep -rn 'from supekku.cli.common import' --include='*.py'` — verify re-exports cover all importers

## 6. Assumptions & STOP Conditions

- **Assumption**: Typer `@app.command()` registration works across package sub-modules (standard pattern).
- **Assumption**: Re-exports in slim `common.py` cover all 18 importers — verified during preflight.
- **STOP when**: Circular import discovered that deferred-import pattern can't resolve.

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 1.1 | Split `common.py` → `artifacts.py` | | Largest extraction (~550 lines) |
| [ ] | 1.2 | Split `common.py` → `ids.py` | [P] | ~70 lines |
| [ ] | 1.3 | Split `common.py` → `io.py` | [P] | ~150 lines |
| [ ] | 1.4 | Add re-exports to slim `common.py` | | Depends on 1.1–1.3 |
| [ ] | 1.5 | Lint + test after common.py split | | Gate before list.py |
| [ ] | 1.6 | Convert `list.py` → `list/__init__.py` | | Create package, define `app` |
| [ ] | 1.7 | Extract `list/specs.py` | [P] | ~340 lines |
| [ ] | 1.8 | Extract `list/deltas.py` | [P] | ~340 lines |
| [ ] | 1.9 | Extract `list/changes.py` | [P] | changes + plans, ~350 lines |
| [ ] | 1.10 | Extract `list/reviews.py` | [P] | revisions + audits, ~320 lines |
| [ ] | 1.11 | Extract `list/governance.py` | [P] | adrs + policies + standards, ~430 lines |
| [ ] | 1.12 | Extract `list/requirements.py` | [P] | ~310 lines |
| [ ] | 1.13 | Extract `list/backlog.py` | [P] | ~270 lines |
| [ ] | 1.14 | Extract `list/backlog_items.py` | [P] | drift + 4 item types, ~540 lines |
| [ ] | 1.15 | Extract `list/misc.py` | [P] | cards + memories + schemas, ~340 lines |
| [ ] | 1.16 | Wire `list/__init__.py` imports | | Import all sub-modules to register commands |
| [ ] | 1.17 | Lint + test after list.py split | | Final gate |

### Task Details

- **1.1 `artifacts.py`**: Move `ArtifactRef`, `ArtifactNotFoundError`, `AmbiguousArtifactError`, all `_resolve_*`, `resolve_artifact`, `resolve_by_id`, `load_all_artifacts`, `emit_artifact`, `extract_yaml_frontmatter`, `_matches_pattern`, all `_find_*`, `find_artifacts`. These form the artifact resolution subsystem — one cohesive responsibility.

- **1.2 `ids.py`**: Move `normalize_id`, `_parse_prefix`, `_normalize_plan_id`.

- **1.3 `io.py`**: Move `get_pager`, `get_editor`, `open_in_pager`, `render_file`, `render_file_paged`, `open_in_editor`.

- **1.4 Re-exports**: Slim `common.py` keeps exit codes, options, JSON helpers, `ContentType`, `InferringGroup`, `matches_regexp`, `version_callback`, `root_option_callback`. Adds `from supekku.cli.artifacts import ...` etc. for backward compat.

- **1.6 Package conversion**: Create `cli/list/__init__.py` with `app = typer.Typer(...)`, shared imports, `_parse_relation_filter`. Bottom of file imports all sub-modules to trigger `@app.command()` registration.

- **1.7–1.15 Extractions**: Each sub-module imports `app` from `supekku.cli.list` and registers commands. Each gets its own focused imports (registry, formatters, etc.).

- **1.16 Wiring**: `__init__.py` bottom section:
  ```python
  from supekku.cli.list import specs as _specs  # noqa: F401
  from supekku.cli.list import deltas as _deltas  # noqa: F401
  # ... etc
  ```

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|
| Circular import in list/ package | Standard Typer pattern; app defined before sub-module imports | mitigated |
| common.py re-exports miss a symbol | grep verification in task 1.5 | mitigated |

## 9. Decisions & Outcomes

- 2026-03-22 — Split common.py before list.py (list imports from common)
- 2026-03-22 — list/ package approach (DEC-114-01) over flat files
- 2026-03-22 — Re-exports for zero-change migration (DEC-114-02)

## 10. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Phase 02 sheet created
- [ ] Delta/plan updated
