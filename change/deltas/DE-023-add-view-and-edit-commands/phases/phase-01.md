---
id: IP-023.PHASE-01
slug: 023-add-view-and-edit-commands-phase-01
name: IP-023 Phase 01 - Implement view and edit commands
created: '2026-02-05'
updated: '2026-02-05'
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-023.PHASE-01
plan: IP-023
delta: DE-023
objective: >-
  Implement view and edit commands for opening artifacts in pager/editor.
entrance_criteria:
  - DR-023 design approved
  - PROD-013 spec reviewed
exit_criteria:
  - view command works for all artifact types
  - edit command works for all artifact types
  - Tests passing
  - Lint clean
verification:
  tests:
    - supekku/cli/view_test.py
    - supekku/cli/edit_test.py
  evidence: []
tasks:
  - id: "1.1"
    description: Add pager/editor helpers to common.py
    status: complete
  - id: "1.2"
    description: Create view.py with all subcommands
    status: complete
  - id: "1.3"
    description: Create edit.py with all subcommands
    status: complete
  - id: "1.4"
    description: Register commands in main.py
    status: complete
  - id: "1.5"
    description: Write tests
    status: complete
  - id: "1.6"
    description: Lint and verify
    status: complete
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-023.PHASE-01
```

# Phase 1 - Implement view and edit commands

## 1. Objective

Add `view` and `edit` top-level commands that open artifacts in $PAGER and $EDITOR respectively.

## 2. Links & References

- **Delta**: [DE-023](../DE-023.md)
- **Design Revision**: [DR-023](../DR-023.md) Section 10
- **Specs**: PROD-013.FR-003, PROD-013.FR-004
- **Source**: `supekku/cli/` (new files)

## 3. Entrance Criteria

- [x] DR-023 design approved
- [x] PROD-013 spec reviewed

## 4. Exit Criteria / Done When

- [x] `spec-driver view adr ADR-001` opens in pager
- [x] `spec-driver edit adr ADR-001` opens in editor
- [x] All artifact types supported (adr, spec, delta, revision, requirement, policy, standard, card)
- [x] Graceful error when pager/editor unavailable
- [x] Tests passing (`just test`)
- [x] Lint clean (`just lint`)

## 5. Verification

- Run: `just test supekku/cli/view_test.py supekku/cli/edit_test.py`
- Run: `just lint`
- Manual: `spec-driver view adr ADR-001`, `spec-driver edit adr ADR-001`

## 6. Assumptions & STOP Conditions

- Assumptions: Registries expose path via `.path` attribute or similar
- STOP when: Registry interface differs significantly from show.py usage

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 1.1 | Add helpers to common.py | | Foundation |
| [x] | 1.2 | Create view.py | | After 1.1 |
| [x] | 1.3 | Create edit.py | [P] | Parallel with 1.2 |
| [x] | 1.4 | Register in main.py | | After 1.2, 1.3 |
| [x] | 1.5 | Write tests | | After 1.4 |
| [x] | 1.6 | Lint and verify | | Final |

### Task Details

- **1.1**: Add to `common.py`
  - `get_pager()` - resolve from $PAGER or fallback
  - `get_editor()` - resolve from $EDITOR/$VISUAL or fallback
  - `open_in_pager(path)` - subprocess.run
  - `open_in_editor(path)` - subprocess.run

- **1.2**: Create `view.py`
  - Subcommands: adr, spec, delta, revision, requirement, policy, standard, card
  - Pattern: resolve path via registry, call `open_in_pager()`

- **1.3**: Create `edit.py`
  - Same structure as view.py
  - Use `open_in_editor()` instead

- **1.4**: Register in `main.py`
  ```python
  from supekku.cli import view, edit
  app.add_typer(view.app, name="view")
  app.add_typer(edit.app, name="edit")
  ```

- **1.5**: Write tests
  - Mock `subprocess.run` to verify correct command invoked
  - Test $PAGER/$EDITOR resolution
  - Test error cases

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Platform differences | Test on Linux; document | Open |

## 9. Decisions & Outcomes

- 2026-02-05: Design approved per DR-023

## 10. Findings / Research Notes

- Registries in show.py use `.path` attribute or `to_dict()['path']`
- show_card uses `registry.resolve_path()`
- Pattern is consistent; can mirror show.py structure

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Plan updated with completion

## 12. Verification Evidence

- **Tests**: 1542 passed (2026-02-05), including 18 new tests in view_test.py and edit_test.py
- **Lint**: `just lint` passes clean
- **Manual**: `PAGER=cat uv run spec-driver view adr ADR-001` outputs ADR content
- **Manual**: `EDITOR=cat uv run spec-driver edit adr ADR-001` outputs ADR content
