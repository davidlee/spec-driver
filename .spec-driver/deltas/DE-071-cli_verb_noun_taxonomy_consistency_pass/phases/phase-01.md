---
id: IP-071.PHASE-01
slug: 071-cli-restructure
name: 'P01: CLI restructure'
created: '2026-03-09'
updated: '2026-03-09'
status: draft
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-071.PHASE-01
plan: IP-071
delta: DE-071
objective: >-
  Move schema commands into show/list, create admin group for compact/resolve/backfill,
  remove skills group. All tests pass, linters clean.
entrance_criteria:
  - DR-071 accepted
exit_criteria:
  - All new command paths work (admin, show schema, list schemas)
  - Old top-level schema/skills/compact/resolve/backfill removed from main.py
  - All tests pass (just test)
  - Linters clean (just lint, just pylint-report)
verification:
  tests:
    - VT-071-01
    - VT-071-02
    - VT-071-03
    - VT-071-04
  evidence: []
tasks:
  - id: "1.1"
    description: Move schema into show/list
  - id: "1.2"
    description: Create admin group
  - id: "1.3"
    description: Remove skills group
  - id: "1.4"
    description: Update main.py registrations
  - id: "1.5"
    description: Adapt/create tests
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-071.PHASE-01
```

# Phase 1 — CLI Restructure

## 1. Objective

Move/remove/group CLI commands to enforce VERB NOUN grammar per DR-071.
Three independent sub-tasks (can be done in any order):
schema move, admin group creation, skills removal.

## 2. Links & References

- **Delta**: [DE-071](../DE-071.md)
- **Design Revision**: [DR-071](../DR-071.md) §4.1–4.3
- **Specs**: SPEC-110, PROD-010

## 3. Entrance Criteria

- [x] DR-071 accepted

## 4. Exit Criteria / Done When

- [x] `spec-driver show schema <name>` and `list schemas` work
- [x] `spec-driver admin compact delta`, `admin resolve links`, `admin backfill spec` work
- [x] `spec-driver skills` no longer exists
- [x] Top-level `schema`, `compact`, `resolve`, `backfill` removed
- [x] All tests pass (566 passed, 5 skipped, 1 pre-existing deselected)
- [x] Linters clean (ruff zero warnings, pylint: admin.py 10/10)

## 5. Verification

- `just test` — all pass
- `just lint` — zero warnings
- `just pylint-report` — no regression
- Manual: `spec-driver --help` shows clean top-level commands

## 6. Assumptions & STOP Conditions

- Assumptions: No internal code imports `skills.app`, `schema.app`, `compact.app`,
  `resolve.app`, or `backfill.app` outside of `main.py` and tests.
  Verify with grep before deleting.
- STOP when: unexpected importers found for any removed module.

## 7. Tasks & Progress

| Status | ID  | Description                | Parallel? | Notes                                                                  |
| ------ | --- | -------------------------- | --------- | ---------------------------------------------------------------------- |
| [x]    | 1.1 | Move schema into show/list | [P]       | schema.py → library, thin wrappers in show.py/list.py                  |
| [x]    | 1.2 | Create admin group         | [P]       | New admin.py, mount compact/resolve/backfill sub-Typers                |
| [x]    | 1.3 | Remove skills group        | [P]       | Deleted skills.py, skills_test.py                                      |
| [x]    | 1.4 | Update main.py             |           | Removed old registrations, added admin                                 |
| [x]    | 1.5 | Adapt/create tests         |           | schema_test.py adapted, admin_test.py created, compact_test.py updated |

### Task Details

- **1.1 Move schema into show/list**
  - Remove `app` from `schema.py`; keep all rendering functions
  - Add `@app.command("schema")` in `show.py` delegating to `schema.show_schema()`
  - Add `@app.command("schemas")` in `list.py` delegating to `schema.list_schemas()`
  - Files: `schema.py`, `show.py`, `list.py`

- **1.2 Create admin group**
  - New `admin.py`: create Typer app, mount `compact.app`, `resolve.app`, `backfill.app`
  - Files: `admin.py` (new)

- **1.3 Remove skills group**
  - Verify no importers besides `main.py` and tests
  - Delete `skills.py`, `skills_test.py`
  - Files: `skills.py`, `skills_test.py`

- **1.4 Update main.py**
  - Remove: `schema`, `skills`, `compact`, `resolve`, `backfill` registrations
  - Add: `admin` group registration
  - Update imports

- **1.5 Adapt/create tests**
  - `schema_test.py`: invoke via `show schema` / `list schemas` paths
  - New `admin_test.py`: basic routing tests for admin subcommands
  - Remove `skills_test.py`
