---
id: mem.thread.de-041
name: DE-041 CLI completeness
kind: memory
status: active
memory_type: thread
updated: '2026-03-04'
tags:
- cli
- DE-041
- delta
summary: 'Working context for DE-041: shared CLI helpers, new commands, list flag
  backfill'
scope:
  globs:
  - supekku/cli/**
  - supekku/scripts/lib/changes/creation.py
  - supekku/scripts/lib/formatters/change_formatters.py
  - supekku/scripts/lib/backlog/registry.py
  commands:
  - show
  - view
  - edit
  - find
  - list
  - create plan
priority:
  severity: high
  weight: 8
confidence: high
review_by: '2026-03-18'
provenance:
  sources:
  - kind: delta
    ref: DE-041
    note: Delta, DR, and IP for CLI completeness
  - kind: doc
    ref: CLAUDE.md
    note: "Architecture guide \u2014 skinny CLI, formatter SoC"
---

# DE-041 CLI completeness — working context

## Quick orientation

**Goal**: Every artifact with `create` gets `show/view/edit/find`. All `list`
commands get baseline flags. Plans get full CLI presence.

**Delta bundle** (read these first):
- `change/deltas/DE-041-cli_completeness_fill_obvious_command_gaps/DE-041.md` — scope & motivation
- `change/deltas/DE-041-cli_completeness_fill_obvious_command_gaps/DR-041.md` — design: shared helpers, code impacts, decisions
- `change/deltas/DE-041-cli_completeness_fill_obvious_command_gaps/IP-041.md` — 3-phase plan, verification coverage
- `change/deltas/DE-041-cli_completeness_fill_obvious_command_gaps/phases/phase-01.md` — active phase (8 tasks)
- `change/deltas/DE-041-cli_completeness_fill_obvious_command_gaps/notes.md` — implementation notes

## Key design decisions (DR-041 §7)

- **DEC-041-01**: Shared helpers (`resolve_artifact`, `emit_artifact`, `find_artifacts`) over command factories. Explicit `@app.command` functions, shared internals.
- **DEC-041-02**: `find_backlog_items_by_id()` with duplicate-aware semantics. Single-target → error on ambiguity. Multi-target → return all.
- **DEC-041-03**: `ArtifactNotFoundError` normalizes error handling.
- **DEC-041-04**: Migrate revision commands as proof-of-concept before bulk-adding new commands.
- **DEC-041-05**: Canonical requirement ID is dot-separated (`SPEC-009.FR-001`); colon is alias.

## Codebase map (key files)

| File | Lines | Role | DE-041 changes |
|------|-------|------|----------------|
| `supekku/cli/common.py` | 284 | Shared CLI utils | Add ArtifactRef, errors, resolve/emit/find helpers |
| `supekku/cli/show.py` | 513 | 10 show commands | +6 new, migrate revision |
| `supekku/cli/view.py` | 254 | 8 view commands | +7 new, migrate revision |
| `supekku/cli/edit.py` | 254 | 8 edit commands | +7 new, migrate revision |
| `supekku/cli/find.py` | 233 | 8 find commands | +7 new, migrate revision |
| `supekku/cli/list.py` | 2158 | 15 list commands | +list plans, --filter backfill |
| `supekku/cli/create.py` | 737 | create commands | +create plan |
| `supekku/scripts/lib/changes/creation.py` | ~800 | Delta/phase creation | Extract create_plan() |
| `supekku/scripts/lib/formatters/change_formatters.py` | — | Change formatters | +audit/plan formatters |
| `supekku/scripts/lib/backlog/registry.py` | — | Backlog discovery | +find_backlog_items_by_id() |

## Existing boilerplate pattern (what we're DRYing)

All show commands repeat this ~30-line pattern:
1. Mutual-exclusivity check (`--json`/`--path`/`--raw`)
2. Registry lookup (normalize ID → load → not-found error)
3. Output-mode dispatch (path → raw → json → formatted)

View/edit: registry lookup → `open_in_pager`/`open_in_editor`
Find: registry iterate → fnmatch → echo paths

## Known bugs & sharp edges

- **show revision --json** (show.py:153): calls `artifact.to_dict()` without required `repo_root` arg → crashes. Fix in Phase 1 migration.
- **_update_plan_overview_phases** regex escape: FIXED in this session. `re.sub` replacement string contained `\u` from YAML content. Fix: `lambda _: new_block`.
- **Duplicate backlog IDs** exist in repo (IMPR-003 x2, ISSUE-019 x2). `find_backlog_items_by_id` returns all matches; single-target commands error on ambiguity.
- **list cards --status** is semantically wrong — cards use `--lane`. DR-041 explicitly excludes `--status` from cards.
- **6 pre-existing test failures** (unrelated to DE-041): 1 in resolve_test.py, 5 in TestVerificationStatusFilters.

## Phase status

| Phase | Status | Focus |
|-------|--------|-------|
| **Phase 1** | **ready to execute** | Shared helpers + revision migration PoC |
| Phase 2 | blocked on P1 | Domain additions + all new commands |
| Phase 3 | blocked on P2 | List plans + flag backfill |

## Related memories

- [[mem.pattern.cli.skinny]] — skinny CLI pattern (delegate to domain + formatters)
- [[mem.pattern.formatters.soc]] — formatter separation of concerns
- [[mem.concept.spec-driver.plan]] — implementation plans concept
