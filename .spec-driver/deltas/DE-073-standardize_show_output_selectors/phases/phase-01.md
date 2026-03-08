---
id: IP-073.PHASE-01
slug: 073-content_type_on_show-phase-01
name: "Phase 1 - --content-type on show"
created: '2026-03-09'
updated: '2026-03-09'
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-073.PHASE-01
plan: IP-073
delta: DE-073
objective: >-
  Add unified --content-type/-c option to show subcommands, starting with
  show memory, then extending to other artifact types.
entrance_criteria:
  - DR-073 accepted
  - No -c flag conflicts on show subcommands (confirmed by exploration)
exit_criteria:
  - show memory -c markdown|frontmatter|yaml produces correct output
  - --content-type coexists with --raw/--json/--body-only
  - Tests pass, lint clean
verification:
  tests:
    - VT-073-01
  evidence: []
tasks:
  - "1.1: Define ContentType enum and shared option"
  - "1.2: Implement -c on show memory"
  - "1.3: Extend -c to remaining show subcommands"
  - "1.4: Tests"
risks:
  - "-c flag may conflict with existing options"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-073.PHASE-01
```

# Phase 1 — `--content-type` on `show`

## 1. Objective
Add `--content-type/-c` (`markdown|frontmatter|yaml`) to `show` subcommands
as a unified output selector per DEC-073-02.

## 2. Links & References
- **Delta**: DE-073
- **Design Revision**: DR-073 §DEC-073-02
- **Issues**: ISSUE-036

## 3. Entrance Criteria
- [x] DR-073 accepted with DEC-073-02 resolved
- [x] Confirm no `-c` flag conflicts on `show` subcommands

## 4. Exit Criteria / Done When
- [x] `show memory -c markdown` outputs full file content
- [x] `show memory -c frontmatter` outputs structured metadata
- [x] `show memory -c yaml` outputs raw YAML frontmatter block
- [x] `--content-type` overrides `--raw`/`--json` with warning when both specified
- [x] At least 3 other `show` subcommands support `-c` (all 15 subcommands)
- [x] Tests pass (`just test`), lint clean (`just lint`)

## 5. Verification
- Unit tests for each `-c` value on `show memory`
- Test conflict resolution when both `-c` and `--raw` specified
- Regression tests for existing `--raw`/`--json`/`--path` unchanged

## 6. Assumptions & STOP Conditions
- Assumptions: `-c` is not used on any `show` subcommand (confirmed by exploration)
- STOP when: unexpected `-c` conflict found on a subcommand

## 7. Tasks & Progress

| Status | ID | Description | Parallel? | Notes |
| --- | --- | --- | --- | --- |
| [x] | 1.1 | Define `ContentType` enum + shared Typer option in `common.py` | | Done |
| [x] | 1.2 | Implement `-c` on `show memory` | | Done |
| [x] | 1.3 | Extend `-c` to other `show` subcommands | [P] | All 15 subcommands |
| [x] | 1.4 | Tests for all `-c` values and conflict resolution | | Done |

### Task Details

- **1.1 Define ContentType enum + shared option**
  - **Files**: `supekku/cli/common.py`
  - **Approach**: `ContentType` string enum (`markdown`, `frontmatter`, `yaml`).
    Typer `Option` factory or annotated type for reuse across subcommands.

- **1.2 Implement on `show memory`**
  - **Files**: `supekku/cli/show.py` (show_memory function)
  - **Approach**: Add `-c` parameter. When provided: `markdown` → read_text(),
    `frontmatter` → existing metadata display, `yaml` → extract YAML block only.
    If both `-c` and `--raw` specified, `-c` wins with stderr warning.

- **1.3 Extend to other subcommands**
  - **Files**: `supekku/cli/show.py`
  - **Approach**: Add `-c` to `show spec`, `show delta`, `show adr`, etc.
    Behaviour is consistent: `markdown` = raw file, `frontmatter` = metadata,
    `yaml` = raw YAML block.

- **1.4 Tests**
  - **Files**: `supekku/cli/show_test.py` (or equivalent)
  - **Testing**: Typer CLI runner tests for each `-c` value. Conflict warning test.

## 8. Risks & Mitigations
| Risk | Mitigation | Status |
| --- | --- | --- |
| `-c` conflicts on a subcommand | Audit done during exploration — none found | mitigated |

## 9. Decisions & Outcomes
- Per DEC-073-02: `-c` coexists with existing flags, wins on conflict with warning.

## 10. Wrap-up Checklist
- [x] Exit criteria satisfied
- [x] Verification evidence: 171 tests pass (common_test + show_test), lint clean
- [x] IP-073 progress tracking updated
