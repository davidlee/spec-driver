---
id: IP-041.PHASE-02
slug: 041-cli_completeness_fill_obvious_command_gaps-phase-02
name: IP-041 Phase 02 — Domain additions + new commands
created: '2026-03-04'
updated: '2026-03-04'
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-041.PHASE-02
plan: IP-041
delta: DE-041
objective: >-
  Add all missing show/view/edit/find subcommands using Phase 1 shared helpers,
  add plan and backlog resolvers to the dispatch tables, create domain support
  (find_backlog_items_by_id, create_plan), and add required formatters.
entrance_criteria:
  - Phase 1 complete (shared helpers tested, revision migration done)
  - Existing test suite passing (just check)
  - DR-041 §4.2–4.10 reviewed
exit_criteria:
  - Plan resolver (_resolve_plan) and finder (_find_plans) in common.py dispatch tables
  - Backlog resolvers (_resolve_backlog) and finders (_find_backlog) in dispatch tables
  - find_backlog_items_by_id() in backlog/registry.py with tests
  - create_plan() extracted from create_delta() with tests
  - format_audit_details() and format_plan_details() formatters with tests
  - All new show subcommands wired (plan, audit, issue, problem, improvement, risk)
  - All new view subcommands wired (plan, audit, memory, issue, problem, improvement, risk)
  - All new edit subcommands wired (plan, audit, memory, issue, problem, improvement, risk)
  - All new find subcommands wired (plan, audit, requirement, issue, problem, improvement, risk)
  - create plan --delta DE-XXX CLI command wired
  - Integration tests per new subcommand (VT-commands)
  - just check green (tests + both linters)
verification:
  tests:
    - VT-backlog-find
    - VT-plan-resolve
    - VT-create-plan
    - VT-format-audit
    - VT-format-plan
    - VT-commands
  evidence:
    - VA-lint
tasks:
  - id: "2.1"
    description: "Implement find_backlog_items_by_id() in backlog/registry.py"
    status: complete
  - id: "2.2"
    description: "Add plan resolver (_resolve_plan) and finder (_find_plans) to common.py"
    status: complete
  - id: "2.3"
    description: "Add backlog resolvers and finders to common.py dispatch tables"
    status: complete
  - id: "2.4"
    description: "Unit tests for new resolvers/finders (VT-plan-resolve, VT-backlog-find)"
    status: complete
  - id: "2.5"
    description: "Add format_audit_details() and format_plan_details() formatters"
    status: complete
  - id: "2.6"
    description: "Unit tests for formatters (VT-format-audit, VT-format-plan)"
    status: complete
  - id: "2.7"
    description: "Extract create_plan() from create_delta() + tests (VT-create-plan)"
    status: complete
  - id: "2.8"
    description: "Wire all new show subcommands (plan, audit, issue, problem, improvement, risk)"
    status: complete
  - id: "2.9"
    description: "Wire all new view/edit subcommands"
    status: complete
  - id: "2.10"
    description: "Wire all new find subcommands (plan, audit, requirement, issue, problem, improvement, risk)"
    status: complete
  - id: "2.11"
    description: "Wire create plan --delta CLI command"
    status: complete
  - id: "2.12"
    description: "Integration tests for new commands (VT-commands)"
    status: complete
  - id: "2.13"
    description: "Final verification: just check green"
    status: complete
risks:
  - description: Backlog items lack a to_dict(root) method needed for show --json
    likelihood: medium
    impact: low
    mitigation: Provide json_fn using BacklogItem's existing attributes or a simple dict comprehension
  - description: Plan frontmatter parsing may differ from ChangeArtifact model
    likelihood: low
    impact: medium
    mitigation: Plan resolver loads frontmatter directly via yaml; doesn't need ChangeRegistry
  - description: create_plan extraction may break create_delta's coupling
    likelihood: low
    impact: medium
    mitigation: Extract as pure function; create_delta calls it internally
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-041.PHASE-02
```

# Phase 02 — Domain additions + new commands

## 1. Objective

Use the shared helpers proven in Phase 1 to add all missing CLI subcommands.
This requires domain support first (resolvers, finders, formatters, create_plan),
then wiring the thin CLI commands on top.

## 2. Links & References

- **Delta**: [DE-041](../DE-041.md)
- **Design Revision**: [DR-041](../DR-041.md) §4.2–4.10
- **Specs**: PROD-010 (CLI UX), PROD-013 (CLI Artifact File Access)
- **Phase 1 helpers**: `supekku/cli/common.py` (resolve_artifact, emit_artifact, find_artifacts)

## 3. Entrance Criteria

- [x] Phase 1 complete (shared helpers tested, revision migration done)
- [x] Existing test suite passing (`just check`)
- [x] DR-041 §4.2–4.10 reviewed

## 4. Exit Criteria / Done When

- [x] Plan resolver + finder in dispatch tables
- [x] Backlog resolvers + finders in dispatch tables
- [x] `find_backlog_items_by_id()` tested
- [x] `create_plan()` extracted and tested
- [x] `format_audit_details()` and `format_plan_details()` tested
- [x] All new show/view/edit/find subcommands wired
- [x] `create plan --delta` wired
- [x] Integration tests for new commands
- [x] `just check` green

## 5. Verification

```bash
# Unit tests for new domain functions
uv run pytest supekku/scripts/lib/backlog/registry_test.py -k backlog_items_by_id -v
uv run pytest supekku/cli/common_test.py -k "plan or backlog" -v
uv run pytest supekku/scripts/lib/formatters/ -k "audit_details or plan_details" -v
uv run pytest supekku/scripts/lib/changes/creation_test.py -k create_plan -v

# Integration tests for new CLI commands
uv run pytest supekku/cli/show_test.py -k "audit or plan or issue or problem or improvement or risk" -v
uv run pytest supekku/cli/view_test.py -k "audit or plan or issue or problem or improvement or risk" -v
uv run pytest supekku/cli/edit_test.py -k "audit or plan or issue or problem or improvement or risk" -v
uv run pytest supekku/cli/find_test.py -k "audit or plan or requirement or issue or problem or improvement or risk" -v

# Full suite + linters
just check
```

## 6. Assumptions & STOP Conditions

**Assumptions**:

- BacklogItem model has enough data for show/view/edit (id, path, frontmatter)
- Plan files (IP-\*.md) have frontmatter parseable by standard YAML loader
- create_plan logic in creation.py:251-298 can be extracted without breaking create_delta

**STOP when**:

- BacklogItem model needs significant extension to support show --json
- Plan frontmatter requires a new registry type (should be simpler than that)
- create_plan extraction breaks existing create_delta tests

## 7. Tasks & Progress

| Status | ID   | Description                                    | Parallel? | Notes                                             |
| ------ | ---- | ---------------------------------------------- | --------- | ------------------------------------------------- |
| [x]    | 2.1  | find_backlog_items_by_id()                     | [ ]       | Domain function, foundation for backlog resolvers |
| [x]    | 2.2  | Plan resolver + finder in common.py            | [P]       | Can parallel with 2.1                             |
| [x]    | 2.3  | Backlog resolvers + finders in common.py       | [ ]       | Depends on 2.1                                    |
| [x]    | 2.4  | Unit tests for new resolvers/finders           | [ ]       | After 2.1–2.3                                     |
| [x]    | 2.5  | format_audit_details() + format_plan_details() | [P]       | Independent of 2.1–2.3                            |
| [x]    | 2.6  | Unit tests for formatters                      | [ ]       | After 2.5                                         |
| [x]    | 2.7  | Extract create_plan() + tests                  | [P]       | Independent of 2.1–2.6                            |
| [x]    | 2.8  | Wire new show subcommands                      | [ ]       | After 2.4 + 2.6                                   |
| [x]    | 2.9  | Wire new view/edit subcommands                 | [P]       | Can parallel with 2.8                             |
| [x]    | 2.10 | Wire new find subcommands                      | [P]       | Can parallel with 2.8                             |
| [x]    | 2.11 | Wire create plan --delta                       | [ ]       | After 2.7                                         |
| [x]    | 2.12 | Integration tests for new commands             | [ ]       | After 2.8–2.11                                    |
| [x]    | 2.13 | Final verification                             | [ ]       | After 2.12                                        |

### Task Details

- **2.1 find_backlog_items_by_id()**
  - **Design**: DR-041 §4.9. Targeted path search: `backlog/{issues,problems,improvements,risks}/{ID}-*/{ID}.md`. Returns `list[BacklogItem]`. Optional `kind` parameter narrows to one subdir.
  - **Files**: `supekku/scripts/lib/backlog/registry.py`
  - **Testing**: VT-backlog-find in `registry_test.py`

- **2.2 Plan resolver + finder**
  - **Design**: DR-041 §4.6. `_resolve_plan(root, raw_id)`: normalize `41` → `IP-041`, scan `change/deltas/*/IP-{id}.md`, load frontmatter, return ArtifactRef. `_find_plans(root, pattern)`: iterate delta dirs for `IP-*.md`, yield matching.
  - **Files**: `supekku/cli/common.py`
  - **Testing**: VT-plan-resolve in `common_test.py`

- **2.3 Backlog resolvers + finders**
  - **Design**: DR-041 §4.9. `_resolve_backlog(root, raw_id, kind)` calls `find_backlog_items_by_id()`, raises ArtifactNotFoundError (0 matches) or AmbiguousArtifactError (>1 match). Add entries for issue/problem/improvement/risk to both dispatch tables.
  - **Files**: `supekku/cli/common.py`
  - **Testing**: VT-backlog-find extension in `common_test.py`

- **2.4 Unit tests for resolvers/finders**
  - **Design**: Parameterized tests for plan and backlog types. Mock filesystem for plan scan. Mock find_backlog_items_by_id for resolver tests.
  - **Files**: `supekku/cli/common_test.py`

- **2.5 Formatters**
  - **Design**: DR-041 §4.10. `format_audit_details(artifact, root=None)` follows `format_revision_details` pattern. `format_plan_details(plan_data, root=None)` shows plan summary with phases and delta ref.
  - **Files**: `supekku/scripts/lib/formatters/change_formatters.py`
  - **Testing**: VT-format-audit, VT-format-plan

- **2.6 Formatter tests**
  - **Files**: `supekku/scripts/lib/formatters/change_formatters_test.py`

- **2.7 Extract create_plan()**
  - **Design**: DR-041 §4.7. Extract creation.py:251-298 into `create_plan(delta_id, root, specs=None, requirements=None)`. `create_delta` calls it internally. Wire `spec-driver create plan --delta DE-XXX`.
  - **Files**: `supekku/scripts/lib/changes/creation.py`, `supekku/cli/create.py`
  - **Testing**: VT-create-plan in `creation_test.py`

- **2.8 Wire new show subcommands**
  - **Design**: DR-041 §4.2. Each ~5 lines: resolve_artifact + emit_artifact. New: plan, audit, issue, problem, improvement, risk.
  - **Files**: `supekku/cli/show.py`

- **2.9 Wire new view/edit subcommands**
  - **Design**: DR-041 §4.3. Each ~3 lines: resolve_artifact + open_in_pager/editor. New view: plan, audit, memory, issue, problem, improvement, risk. New edit: same set.
  - **Files**: `supekku/cli/view.py`, `supekku/cli/edit.py`
  - **Note**: view/edit memory already exist; skip those.

- **2.10 Wire new find subcommands**
  - **Design**: DR-041 §4.4. Each ~3 lines: find_artifacts + echo path. New: plan, audit, requirement, issue, problem, improvement, risk.
  - **Files**: `supekku/cli/find.py`

- **2.11 Wire create plan --delta**
  - **Design**: DR-041 §4.7. CLI command calls create_plan(delta_id, root).
  - **Files**: `supekku/cli/create.py`

- **2.12 Integration tests**
  - **Design**: Typer CliRunner tests per new subcommand. Verify wiring (correct resolver, correct output mode). Minimal — don't duplicate unit test coverage.
  - **Files**: `supekku/cli/show_test.py`, `view_test.py`, `edit_test.py`, `find_test.py`

- **2.13 Final verification**
  - `just check` (tests + ruff + pylint). Fix any issues.

## 8. Risks & Mitigations

| Risk                                         | Mitigation                                                                | Status  |
| -------------------------------------------- | ------------------------------------------------------------------------- | ------- |
| BacklogItem lacks to_dict for --json         | Use simple dict from frontmatter attrs                                    | Planned |
| Plan frontmatter not standard ChangeArtifact | Custom resolver loads YAML directly                                       | Planned |
| create_plan extraction breaks create_delta   | Extract as function called by create_delta; existing tests catch breakage | Planned |

## 9. Decisions & Outcomes

- `2026-03-04` — Phase scope: all new commands + domain support. List improvements deferred to Phase 3.
- `2026-03-04` — view/edit memory already exist in codebase; task 2.9 skips them.

## 10. Findings / Research Notes

**Pre-phase exploration**:

- `format_audit_details` and `format_plan_details` don't exist yet — need creation
- `find_backlog_items_by_id` doesn't exist — need creation
- `create_plan` is inline in `create_delta` at creation.py:251-298 — extraction target
- Plan/backlog resolvers and finders not in common.py dispatch tables — need addition
- BacklogItem model in `backlog/models.py`, discovery in `backlog/registry.py`
- `discover_backlog_items()` does full O(n) scan — `find_backlog_items_by_id()` uses targeted path lookup

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] IP-041 updated with Phase 2 results
- [ ] Hand-off notes to Phase 3
