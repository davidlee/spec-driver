---
id: IP-073.PHASE-02
slug: 073-standardize_show_output_selectors-phase-02
name: view refactor and read alias
created: '2026-03-09'
updated: '2026-03-09'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-073.PHASE-02
plan: IP-073
delta: DE-073
objective: >-
  Replace pager-by-default view with rendered stdout (glow > rich > raw),
  add --pager/-p opt-in, collapse ~16 near-identical subcommands into shared
  helper, and register read as alias for view.
entrance_criteria:
  - Phase 1 complete and committed
exit_criteria:
  - view renders to stdout by default (no pager)
  - --pager/-p invokes pager with render cascade
  - view.py duplication collapsed via shared helper
  - read alias works identically to view
  - tests pass, lint clean
verification:
  tests:
    - VT-073-02: render_file and render_file_paged cascades
    - VT-073-04: read alias dispatches identically to view
  evidence: []
tasks:
  - id: 2.1
    description: "Add render_file() and render_file_paged() to common.py"
  - id: 2.2
    description: "Add PagerOption annotated type"
  - id: 2.3
    description: "Create _view_artifact() shared helper in view.py"
  - id: 2.4
    description: "Collapse subcommands to use _view_artifact()"
  - id: 2.5
    description: "Register read alias in main.py"
  - id: 2.6
    description: "Update tests for new behavior"
risks:
  - "Typer may reject same app registered twice for read alias"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-073.PHASE-02
```

# Phase 2 - View refactor and read alias

## 1. Objective

Replace pager-by-default `view` with rendered stdout, add `--pager/-p` opt-in,
collapse duplicated subcommands, and register `read` alias.

## 2. Links & References

- **Delta**: DE-073
- **Design Revision Sections**: DR-073 §DEC-073-01 (two cascades), §DEC-073-03
  (read alias), §DEC-073-04 (view renders to stdout)
- **Key files**: `supekku/cli/view.py`, `supekku/cli/common.py`, `supekku/cli/main.py`

## 3. Entrance Criteria

- [x] Phase 1 complete and committed (c2336ab)

## 4. Exit Criteria / Done When

- [x] `view <artifact>` renders via glow → rich → raw stdout (no pager)
- [x] `view --pager <artifact>` pages via $PAGER → glow -p → ov → less → more
- [x] `view.py` subcommand duplication collapsed via shared helper
- [x] `read` works identically to `view`
- [x] All tests pass, lint clean

## 5. Verification

- Unit tests for render_file / render_file_paged cascades (mock shutil.which)
- CLI integration tests for --pager flag
- `read` alias dispatches identically to `view`
- `just lint && just test`

## 7. Tasks & Progress

| Status | ID  | Description                                            |
| ------ | --- | ------------------------------------------------------ |
| [x]    | 2.1 | Add render_file() and render_file_paged() to common.py |
| [x]    | 2.2 | Add PagerOption annotated type                         |
| [x]    | 2.3 | Create \_view_artifact() shared helper in view.py      |
| [x]    | 2.4 | Collapse subcommands to use \_view_artifact()          |
| [x]    | 2.5 | Register read alias in main.py                         |
| [x]    | 2.6 | Update tests for new behavior                          |
