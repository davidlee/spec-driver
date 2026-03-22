---
id: IP-113-P01
slug: "113-dead_code_purge_orphaned_scripts_hollow_functions_stale_migrations-phase-01"
name: "Purge orphaned scripts, relocate complete_delta, rename registry_migration"
created: "2026-03-22"
updated: "2026-03-22"
status: in-progress
kind: phase
plan: IP-113
delta: DE-113
---

# Phase 01 — Purge orphaned scripts, relocate complete_delta, rename registry_migration

## 1. Objective

Delete 19 orphaned files (15 scripts + 2 tests + 1 duplicate doc generator + 1 stale migration), relocate `complete_delta` business logic to `scripts/lib/changes/completion.py`, rename `registry_migration.py` → `registry_v2.py`, clean stale TODO. Zero behaviour change.

## 2. Links & References

- **Delta**: DE-113
- **Design Revision**: DR-113 (sections 4a–4d)
- **Specs**: SPEC-110, SPEC-112
- **Standards**: STD-004 (orphan prevention), POL-001 (minimise sprawl)

## 3. Entrance Criteria

- [x] DR-113 accepted
- [x] IP-113 accepted
- [x] Orphaned scripts verified via import grep (preflight)

## 4. Exit Criteria / Done When

- [ ] All 19 orphaned files deleted
- [ ] `complete_delta` business logic in `scripts/lib/changes/completion.py`
- [ ] `scripts/complete_delta.py` deleted or reduced to thin shim
- [ ] `registry_migration.py` renamed to `registry_v2.py`, all 5 importers updated
- [ ] Stale TODO in `blocks/__init__.py` removed
- [ ] `just check` passes
- [ ] `grep -rn` confirms no imports of deleted modules (excluding `.uv-cache`)

## 5. Verification

- `just check` — full test suite + lint
- `grep -rn 'from supekku.scripts.list_specs\|from supekku.scripts.list_changes\|from supekku.scripts.decision_registry\|registry_migration' --include='*.py' | grep -v __pycache__ | grep -v .uv-cache` — zero hits
- No new tests needed; deleted tests covered deleted code

## 6. Assumptions & STOP Conditions

- **Assumption**: `complete_delta.py` argparse `main()` has no external callers (verified: not in pyproject.toml entry points, not in Justfile).
- **STOP when**: Any import of a "deleted" script is found in CI config, Justfile, or external tooling.

## 7. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [x] | 1.1 | Delete 15 orphaned scripts + backlog dir | [P] | 19 files removed |
| [x] | 1.2 | Delete orphaned tests (`list_specs_test`, `list_changes_test`) | [P] | |
| [x] | 1.3 | Delete `scripts/cli/ast_doc_generator.py` | [P] | |
| [x] | 1.4 | Delete `migrate_stub_status.py` | [P] | |
| [x] | 1.5 | Relocate `complete_delta` business logic to `completion.py` | | Hollow display fns deleted |
| [x] | 1.6 | Update `cli/complete.py` import | | |
| [x] | 1.7 | Move `complete_delta_test.py` to `lib/changes/` | | Patches updated |
| [x] | 1.8 | Rename `registry_migration.py` → `registry_v2.py` | | |
| [x] | 1.9 | Update 5 importers of `registry_migration` | | |
| [x] | 1.10 | Clean stale TODO in `blocks/__init__.py` | [P] | |
| [x] | 1.11 | Run tests + lint + grep verification | | See notes |

### Task Details

- **1.1–1.4 Deletions**
  - Pure `git rm`. Files listed in DR-113 §4a.
  - Include `scripts/backlog/__init__.py` (delete entire directory).

- **1.5 Relocate complete_delta**
  - Move functions from `scripts/complete_delta.py` into `scripts/lib/changes/completion.py`:
    - `complete_delta()` (main orchestrator, ~180 lines)
    - `validate_delta_status()`
    - `collect_requirements_to_update()`
    - `update_delta_frontmatter()`
    - `update_requirements_status()`
    - `update_requirements_in_revision_sources()`
    - `handle_already_completed_delta()`
    - `run_spec_sync()`, `_is_interactive_input_available()`, `prompt_yes_no()`, `prompt_spec_sync()`
  - **Delete** hollow display functions: `display_preview`, `display_actions`, `display_dry_run_requirements` — they do nothing (all `pass` bodies). Callers in `complete_delta()` that invoke them become no-ops or are removed.
  - Delete `scripts/complete_delta.py` entirely (argparse `main()`/`build_parser()` are unused — CLI uses Typer).

- **1.8–1.9 Registry rename**
  - `git mv scripts/lib/registry_migration.py scripts/lib/registry_v2.py`
  - `git mv scripts/lib/registry_migration_test.py scripts/lib/registry_v2_test.py`
  - Update imports in: `cli/sync.py`, `scripts/sync_specs.py`, `scripts/lib/deletion/executor.py`, `scripts/lib/deletion/executor_test.py`, `scripts/lib/registry_v2_test.py`

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|------------|--------|
| External caller of orphaned script | Verified pyproject.toml, Justfile, CI — none found | mitigated |
| complete_delta relocation breaks CLI | Mechanical import update, test coverage | mitigated |

## 9. Decisions & Outcomes

- 2026-03-22 — Delete hollow display functions rather than implement (DEC-113-02)
- 2026-03-22 — Add `validate_revision_blocks.py` to kill list (DEC-113-03)
- 2026-03-22 — Relocation target is `scripts/lib/changes/completion.py` (DEC-113-01)

## 10. Findings / Research Notes

- `cli/complete.py` already imports from `scripts/lib/changes/completion` for `complete_revision` — confirms relocation target is natural.
- `pyproject.toml [project.scripts]` has only `spec-driver = supekku.cli.main:main` — no orphaned script entry points.
- `pylint_report.py` is invoked via Justfile (`python -m`) — NOT orphaned, excluded from kill list.
- `package_utils_test.py` had `supekku/scripts/backlog` in its known leaf packages list — updated.
- 4 test failures remain but all are caused by DE-123 uncommitted changes to `cli/list.py`, not by DE-113 changes. Confirmed by stashing DE-123 changes — all 4 pass.
- Net result: +508 / −2890 lines (−2382 net).

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence: lint clean on changed files, 4580 tests pass, grep clean
- [x] Delta/plan updated
- [ ] Delta closed via `spec-driver complete delta DE-113`
