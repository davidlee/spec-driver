---
id: IP-024.PHASE-01
slug: 024-add-raw-flag-to-show-commands-phase-01
name: IP-024 Phase 01 - Implement --raw flag
created: '2026-02-05'
updated: '2026-02-05'
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-024.PHASE-01
plan: IP-024
delta: DE-024
objective: >-
  Add --raw flag to all show subcommands for raw file content output.
entrance_criteria:
  - DR-024 design approved
exit_criteria:
  - All show commands support --raw flag
  - Mutual exclusivity with --json and --path
  - Tests passing
  - Lint clean
verification:
  tests:
    - supekku/cli/show_test.py
  evidence: []
tasks:
  - id: "1.1"
    description: Update show.py mutual exclusivity check
    status: complete
  - id: "1.2"
    description: Add --raw to show_spec
    status: complete
  - id: "1.3"
    description: Add --raw to show_delta
    status: complete
  - id: "1.4"
    description: Add --raw to show_revision
    status: complete
  - id: "1.5"
    description: Add --raw to show_requirement
    status: complete
  - id: "1.6"
    description: Add --raw to show_adr
    status: complete
  - id: "1.7"
    description: Add --raw to show_policy
    status: complete
  - id: "1.8"
    description: Add --raw to show_standard
    status: complete
  - id: "1.9"
    description: Add --raw to show_card
    status: complete
  - id: "1.10"
    description: Write tests
    status: complete
  - id: "1.11"
    description: Lint and verify
    status: complete
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-024.PHASE-01
```

# Phase 1 - Implement --raw flag

## 1. Objective

Add `--raw` flag to all `show` subcommands that outputs the raw file content without any formatting.

## 2. Links & References

- **Delta**: [DE-024](../DE-024.md)
- **Design Revision**: [DR-024](../DR-024.md) Section 10
- **Specs**: PROD-013.FR-002
- **Source**: `supekku/cli/show.py`

## 3. Entrance Criteria

- [x] DR-024 design approved

## 4. Exit Criteria / Done When

- [x] All show commands accept `--raw` flag
- [x] `--raw` outputs file content unchanged
- [x] `--raw`, `--json`, `--path` are mutually exclusive
- [x] Tests passing (`just test`)
- [x] Lint clean (`just lint`)

## 5. Verification

- Run: `just test supekku/cli/show_test.py`
- Run: `just lint`
- Manual: `spec-driver show adr ADR-001 --raw`

## 6. Assumptions & STOP Conditions

- Assumptions: All artifacts have readable file paths
- STOP when: Artifact lacks path attribute

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 1.1 | Update mutual exclusivity check | | 3-way check |
| [x] | 1.2-1.9 | Add --raw to each subcommand | [P] | Parallel |
| [x] | 1.10 | Write tests | | 7 tests added |
| [x] | 1.11 | Lint and verify | | Passed |

### Task Details

- **1.1**: Update mutual exclusivity from 2-way to 3-way check
  ```python
  if sum([json_output, path_only, raw_output]) > 1:
    typer.echo("Error: --json, --path, and --raw are mutually exclusive", err=True)
    raise typer.Exit(EXIT_FAILURE)
  ```

- **1.2-1.9**: Add `--raw` flag and handler to each show subcommand
  ```python
  raw_output: Annotated[bool, typer.Option("--raw", help="Output raw file content")] = False
  # ...
  if raw_output:
    typer.echo(artifact.path.read_text())
  ```

- **1.10**: Add tests for --raw flag
  - Test raw output matches file content
  - Test mutual exclusivity error

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
| --- | --- | --- |
| Large file output | None needed - user's choice | Accepted |

## 9. Decisions & Outcomes

- 2026-02-05: Design approved per DR-024

## 10. Findings / Research Notes

- Pattern follows DE-022 (--path flag addition)
- All artifact types have `.path` attribute

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Verification evidence stored
- [x] Plan updated with completion
