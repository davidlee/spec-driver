---
id: IP-025.PHASE-01
slug: 025-extend-find-command-to-all-artifact-types-phase-01
name: IP-025 Phase 01 - Implement find subcommands
created: '2026-02-05'
updated: '2026-02-05'
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-025.PHASE-01
plan: IP-025
delta: DE-025
objective: >-
  Add find subcommands for all artifact types with pattern matching support.
entrance_criteria:
  - DR-025 design approved
exit_criteria:
  - find spec subcommand works
  - find delta subcommand works
  - find adr subcommand works
  - find revision subcommand works
  - find policy subcommand works
  - find standard subcommand works
  - Pattern matching works (fnmatch)
  - Tests passing
  - Lint clean
verification:
  tests:
    - supekku/cli/find_test.py
  evidence: []
tasks:
  - id: "1.1"
    description: Add find spec subcommand
    status: complete
  - id: "1.2"
    description: Add find delta subcommand
    status: complete
  - id: "1.3"
    description: Add find adr subcommand
    status: complete
  - id: "1.4"
    description: Add find revision subcommand
    status: complete
  - id: "1.5"
    description: Add find policy subcommand
    status: complete
  - id: "1.6"
    description: Add find standard subcommand
    status: complete
  - id: "1.7"
    description: Write tests
    status: complete
  - id: "1.8"
    description: Lint and verify
    status: complete
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-025.PHASE-01
```

# Phase 1 - Implement find subcommands

## 1. Objective

Add `find` subcommands for all artifact types (spec, delta, adr, revision, policy, standard) with fnmatch pattern support.

## 2. Links & References

- **Delta**: [DE-025](../DE-025.md)
- **Design Revision**: [DR-025](../DR-025.md) Section 10
- **Specs**: PROD-013.FR-005
- **Source**: `supekku/cli/find.py`

## 3. Entrance Criteria

- [x] DR-025 design approved

## 4. Exit Criteria / Done When

- [x] `spec-driver find spec SPEC-*` works
- [x] `spec-driver find delta DE-*` works
- [x] `spec-driver find adr ADR-001` works
- [x] `spec-driver find revision RE-*` works
- [x] `spec-driver find policy POL-*` works
- [x] `spec-driver find standard STD-*` works
- [x] Pattern matching (*, ?) works
- [x] Tests passing (`just test`)
- [x] Lint clean (`just lint`)

## 5. Verification

- Run: `just test supekku/cli/find_test.py`
- Run: `just lint`
- Manual: `spec-driver find adr ADR-*`

## 6. Assumptions & STOP Conditions

- Assumptions: Registries expose iteration methods
- STOP when: Registry lacks iteration support

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 1.1 | Add find spec | [P] | |
| [x] | 1.2 | Add find delta | [P] | |
| [x] | 1.3 | Add find adr | [P] | |
| [x] | 1.4 | Add find revision | [P] | |
| [x] | 1.5 | Add find policy | [P] | |
| [x] | 1.6 | Add find standard | [P] | |
| [x] | 1.7 | Write tests | | 13 tests |
| [x] | 1.8 | Lint and verify | | Passed |

### Task Details

- **1.1-1.6**: Add find subcommands following pattern:
  ```python
  @app.command("spec")
  def find_spec(
    pattern: Annotated[str, typer.Argument(help="ID pattern (e.g., SPEC-*, PROD-01*)")],
    root: RootOption = None,
  ) -> None:
    """Find specs matching ID pattern."""
    import fnmatch
    registry = SpecRegistry(root=root)
    for spec in registry.all_specs():
      if fnmatch.fnmatch(spec.id, pattern) or fnmatch.fnmatch(spec.id, pattern.upper()):
        typer.echo(spec.path)
  ```

- **1.7**: Add tests
  - Test exact match
  - Test wildcard patterns
  - Test case insensitivity

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Registry iteration varies | Check each registry's API | Open |

## 9. Decisions & Outcomes

- 2026-02-05: Design approved per DR-025
- fnmatch for pattern matching (shell-style wildcards)

## 10. Findings / Research Notes

- `find card` uses CardRegistry.find_all_cards()
- SpecRegistry has all_specs()
- DecisionRegistry has all_decisions()
- ChangeRegistry.collect() returns dict
- PolicyRegistry/StandardRegistry have find() methods, need iteration

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Plan updated with completion
