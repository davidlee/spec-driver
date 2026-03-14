---
id: IP-078.PHASE-01
slug: 078-add_list_audits_cli_subcommand-phase-01
name: Implement list audits subcommand
created: '2026-03-09'
updated: '2026-03-09'
status: completed
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-078.PHASE-01
plan: IP-078
delta: DE-078
objective: >-
  Add `list audits` and `list audit` CLI subcommands mirroring `list revisions` pattern.
entrance_criteria:
  - DR-078 drafted
  - list_revisions pattern reviewed
exit_criteria:
  - list audits command works with all standard flags
  - list audit alias registered
  - tests pass (just)
  - linters clean (just lint, just pylint-files)
verification:
  tests:
    - VT-078-001
  evidence: []
tasks:
  - id: T1
    description: Add list_audits command to supekku/cli/list.py
  - id: T2
    description: Register singular alias (list audit)
  - id: T3
    description: Write tests for list audits
  - id: T4
    description: Lint and verify
risks: []
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-078.PHASE-01
```

# Phase 1 – Implement list audits subcommand

## 1. Objective

Add `list audits` (+ `list audit` alias) to `supekku/cli/list.py`, following the `list_revisions` pattern exactly.

## 2. Links & References

- **Delta**: DE-078
- **Design Revision**: DR-078 §4 (code impact + target shape)
- **Pattern source**: `list_revisions` (list.py:1347–1446)
- **Requirements**: SPEC-110.FR-002, SPEC-110.FR-005, SPEC-110.FR-006

## 3. Entrance Criteria

- [x] DR-078 drafted
- [x] `list_revisions` pattern reviewed and understood

## 4. Exit Criteria / Done When

- [x] `spec-driver list audits --help` shows standard flags
- [x] `spec-driver list audit` alias works
- [x] Tests written and passing (3603 passed)
- [x] `just` passes clean (ruff clean, pylint — no new warnings)

## 5. Verification

- `just test` — all tests pass
- `just lint` — ruff clean
- `just pylint-files supekku/cli/list.py` — no new warnings
- Manual: `spec-driver list audits --help` shows expected flags

## 7. Tasks & Progress

| Status | ID  | Description                             | Notes                                                                                                       |
| ------ | --- | --------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| [x]    | T1  | Add `list_audits` function to `list.py` | Cloned `list_revisions`, kind="audit"                                                                       |
| [x]    | T2  | Register `list audit` singular alias    | Added to `_PLURAL_TO_SINGULAR` dict                                                                         |
| [x]    | T3  | Write tests                             | 10 tests: help, alias, json flag/parity, basic, status, filter, regexp, invalid regexp, tsv, invalid format |
| [x]    | T4  | Lint + verify                           | ruff clean, pylint no new warnings, 3603 tests pass                                                         |

### Task Details

- **T1**: Clone `list_revisions` (lines 1347–1446). Change: function name → `list_audits`, command name → `"audits"`, docstring → audits, registry kind → `"audit"`, variable names `revisions` → `audits`.
- **T2**: Add `@app.command("audit")` alias pointing to `list_audits` function, following the pattern used by other singular aliases in `list.py`.
- **T3**: Test in existing CLI test module. Cover: basic list output, --status filter, --json format, --filter substring, --regexp, empty result exit code.
- **T4**: Run `just`. Fix any issues.

## 11. Wrap-up Checklist

- [x] Exit criteria satisfied
- [x] Phase sheet updated with results
- [ ] Delta notes updated
