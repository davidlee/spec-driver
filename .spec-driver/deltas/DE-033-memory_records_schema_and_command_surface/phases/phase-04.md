---
id: IP-033.PHASE-04
slug: 033-memory_records_schema_and_command_surface-phase-04
name: IP-033 Phase 04 - Selection and Filtering
created: '2026-03-02'
updated: '2026-03-02'
status: complete
kind: phase
---

```yaml supekku:phase.overview@v1
schema: supekku.phase.overview
version: 1
phase: IP-033.PHASE-04
plan: IP-033
delta: DE-033
objective: >-
  Implement deterministic scope matching, filtering, and ordering for memory
  records (MEM-FR-003). Pure-function selection module with CLI integration
  via --path, --command, --match-tag options on list memories.
entrance_criteria:
  - Phase 2 complete (MemoryRecord + MemoryRegistry)
  - Phase 3 complete (CLI surface working)
  - Design document reviewed and approved (design-phase-04-selection.md)
exit_criteria:
  - selection.py module with matches_scope, scope_specificity, sort_key, is_surfaceable, select
  - Deterministic ordering verified by tests (same input → same output)
  - CLI list memories supports --path, --command, --match-tag, --include-draft, --limit
  - Thread recency exclusion working with scope + verified date check
  - Path normalization handles repo-relative, trailing /, .., ./
  - Command matching uses token-prefix (no substring false positives)
  - Unit tests passing (VT-MEM-SELECTION-001)
  - Lint checks passing (ruff + pylint)
verification:
  tests:
    - VT-MEM-SELECTION-001 - Deterministic filtering, scope matching, and ordering
  evidence:
    - Test run output showing all selection tests passing
    - Lint checks passing (ruff + pylint)
    - CLI smoke tests with --path and --command options
tasks:
  - id: "4.1"
    description: "Core selection functions — normalize_path, matches_scope, scope_specificity (TDD)"
  - id: "4.2"
    description: "Ordering and filtering — sort_key, is_surfaceable, select (TDD)"
  - id: "4.3"
    description: "CLI integration — --path, --command, --match-tag, --include-draft, --limit on list memories"
  - id: "4.4"
    description: "Integration tests and smoke tests"
risks:
  - description: "PurePosixPath.full_match() behavior edge cases with ** globs"
    mitigation: "Verified working on Python 3.13; comprehensive glob test cases"
  - description: "shlex.split may fail on malformed command strings"
    mitigation: "Graceful fallback to simple split on whitespace"
```

```yaml supekku:phase.tracking@v1
schema: supekku.phase.tracking
version: 1
phase: IP-033.PHASE-04
```

# Phase 4 - Selection and Filtering

## 1. Objective

Implement deterministic scope matching, filtering, and ordering for memory
records per MEM-FR-003. All selection logic lives in pure functions in
`memory/selection.py`. CLI integration adds context-aware filtering to
`list memories`.

## 2. Links & References

- **Delta**: DE-033
- **Design**: `design-phase-04-selection.md` (approved)
- **DR Sections**: DR-033 §12 (MEM-FR-003)
- **JAMMS Reference**: §5 Selection and Surfacing (mem.brief.md lines 161-207)
- **Requirement**: MEM-FR-003 — Deterministic Selection + Filtering

## 3. Entrance Criteria

- [x] Phase 2 complete (MemoryRecord + MemoryRegistry)
- [x] Phase 3 complete (CLI surface working)
- [x] Design document reviewed and approved

## 4. Exit Criteria / Done When

- [x] `memory/selection.py` implements all functions from design
- [x] Deterministic ordering: same input set → same output across runs
- [x] CLI `list memories` supports `--path`, `--command`, `--match-tag`, `--include-draft`, `--limit`
- [x] Tag semantics separated: `--tag` (metadata filter) vs `--match-tag` (scope match)
- [x] Thread exclusion: context-dependent with recency threshold
- [x] Tests passing, linters clean

## 5. Verification

- `uv run pytest supekku/scripts/lib/memory/selection_test.py -v`
- `uv run pytest supekku -v` (full suite)
- `just lint` + `just pylint`
- Smoke: `uv run spec-driver list memories --path <path>` with fixture data

## 6. Assumptions & STOP Conditions

- Assumptions: `PurePosixPath.full_match()` available (Python 3.12+, confirmed 3.13)
- STOP when: scope matching semantics produce surprising results in real usage

## 7. Tasks & Progress

| Status | ID  | Description                                                            | Notes                                                        |
| ------ | --- | ---------------------------------------------------------------------- | ------------------------------------------------------------ |
| [x]    | 4.1 | Core selection: normalize_path, matches_scope, scope_specificity (TDD) | 43 tests                                                     |
| [x]    | 4.2 | Ordering/filtering: sort_key, is_surfaceable, select (TDD)             | 73 tests total (incl skip_status_filter)                     |
| [x]    | 4.3 | CLI integration: new options on list memories                          | All 22 existing CLI tests pass                               |
| [x]    | 4.4 | Integration tests and smoke tests                                      | 13 CLI integration tests added, all 35 CLI memory tests pass |

### Task Details

- **4.1 Core selection functions**
  - **Files**: `supekku/scripts/lib/memory/selection.py`, `supekku/scripts/lib/memory/selection_test.py`
  - **Testing**: TDD — tests first for normalize_path, matches_scope, scope_specificity
  - **Key decisions**: trailing `/` = prefix match; `full_match()` for globs; token-prefix for commands

- **4.2 Ordering and filtering**
  - **Files**: same as 4.1
  - **Testing**: TDD — sort_key determinism, is_surfaceable status matrix, select pipeline
  - **Key decisions**: severity ranking, weight negation, verified recency, thread recency

- **4.3 CLI integration**
  - **Files**: `supekku/cli/list.py`
  - **Testing**: CLI integration tests
  - **Key decisions**: `--match-tag` separate from `--tag`; pipeline ordering

- **4.4 Integration tests**
  - **Files**: CLI test file(s)
  - **Testing**: End-to-end with fixture memory files

## 8. Risks & Mitigations

| Risk                             | Mitigation                                          | Status    |
| -------------------------------- | --------------------------------------------------- | --------- |
| `full_match()` edge cases        | Custom `_glob_match` with comprehensive test matrix | mitigated |
| `shlex.split` on malformed input | Fallback to whitespace split, tested                | mitigated |
| Tag semantics confusion          | Clear `--tag` vs `--match-tag` naming + help text   | mitigated |

## 9. Decisions & Outcomes

- `2026-03-02` - Design approved: pure functions, separated tag semantics, token-prefix commands, trailing-/ prefix paths
- `2026-03-02` - `PurePosixPath.full_match()` not available in venv Python 3.12; implemented custom `_glob_match`/`_match_segments` using segment-by-segment matching with fnmatch.fnmatchcase per segment. `*` matches single segment, `**` matches zero or more.
- `2026-03-02` - Added `skip_status_filter` param to `is_surfaceable`/`select` — when user passes explicit `--status`, the status-based exclusion is bypassed (user is in control). Thread recency still applies.

## 10. Findings / Research Notes

- `PurePosixPath.full_match()` is Python 3.13+ only. Venv runs 3.12.10. Custom glob matcher implemented.
- `fnmatch.fnmatch()` treats `*` and `**` identically (both cross `/`), so it's unsuitable for proper globstar semantics.
- Existing `backlog/priority.py` `sort_by_priority()` served as reference pattern for multi-level sort keys.
- Pylint only complaint: `select()` has 7 args (limit 5) → R0913 at 9.93/10, acceptable for a pipeline function.

## Implementation State (handover)

### Completed

- **`supekku/scripts/lib/memory/selection.py`** — full module with all functions from design:
  - `MatchContext` dataclass
  - `normalize_path()` — repo-relative POSIX normalization
  - `matches_scope()` — OR logic across path/glob/command/tag dimensions
  - `scope_specificity()` — scoring 0-3 per match dimension
  - `sort_key()` — 5-level deterministic tuple (severity/weight/specificity/verified/id)
  - `is_surfaceable()` — status exclusion + thread recency + skip_status_filter
  - `select()` — composed pipeline: filter → scope match → sort → limit
  - Helper: `_glob_match`/`_match_segments` — proper `**` globstar support
  - Helper: `_tokenize_command` — shlex.split with fallback
  - Helper: `_matches_paths`, `_matches_globs`, `_matches_commands`

- **`supekku/scripts/lib/memory/selection_test.py`** — 73 unit tests covering:
  - normalize_path edge cases (8 tests)
  - matches_scope: path exact (6), globs (5), commands (8), tags (4), composition (4)
  - scope_specificity (8 tests)
  - sort_key: severity ordering, weight, specificity, verified recency, id, defaults, determinism (9 tests)
  - is_surfaceable: status matrix, draft, thread recency, skip_status_filter (14 tests)
  - select: end-to-end pipeline (7 tests)

- **`supekku/scripts/lib/memory/__init__.py`** — exports updated

- **`supekku/cli/list.py`** — `list_memories` updated with:
  - `--path` / `-p` (repeatable)
  - `--command` / `-c`
  - `--match-tag` (repeatable)
  - `--include-draft`
  - `--limit` / `-n`
  - Pipeline: metadata pre-filter → regexp → MatchContext → select()
  - `skip_status_filter=True` when `--status` is explicitly provided

- **`supekku/cli/memory_test.py`** — 13 new CLI integration tests in `ListMemoriesSelectionTest`:
  - `_write_memory_file` extended with `scope`, `priority`, `verified` kwargs
  - `--path` scope filtering (exact, no-match, repeatable)
  - `--command` token-prefix scope filtering
  - `--match-tag` tag intersection filtering (single, repeatable)
  - `--include-draft` flag (excluded by default, included when set)
  - `--limit` caps output
  - Deprecated excluded by default; `--status deprecated` bypasses exclusion
  - Deterministic ordering by severity
  - Combined `--path` + `--type` metadata/scope AND logic

### Verification

- Full test suite: 1935 passed, 3 skipped (pre-existing skips)
- Ruff: clean
- Pylint: 9.65/10 (R0913 on test helper only; threshold 0.75)

### Closeout

- Design doc updated: `full_match` → custom `_glob_match` note, status → implemented
- IP-033 updated: Phase 4 → completed, VT-MEM-SELECTION-001 → verified
- All exit criteria satisfied
