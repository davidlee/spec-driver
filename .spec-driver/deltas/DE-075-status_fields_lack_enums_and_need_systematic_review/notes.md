# Notes for DE-075

## Phase 1 — Define constants and register enums

**Status**: complete
**Commit**: `344c9d7`
**Verification**: `just test` 3492 passed, `just lint` clean

### What's done

- 5 new `lifecycle.py` modules: `specs/`, `decisions/`, `policies/`, `standards/`, `memory/`
- Backlog unified: `BACKLOG_BASE_STATUSES` (4) + `RISK_EXTRA_STATUSES` (2) replaces 4 per-kind sets (20 values)
- `ENUM_REGISTRY` in `core/enums.py`: +6 entries (`spec.status`, `adr.status`, `policy.status`, `standard.status`, `memory.status`, `backlog.status`); per-kind backlog entries now point to unified base
- `decisions/registry.py`: two hardcoded status dir lists replaced with `ADR_STATUSES` reference
- `edit_test.py`: updated — spec now validates against enum (was "anything goes")
- `DEFAULT_HIDDEN_STATUSES` trimmed: removed `implemented` (no longer a valid status)

### Surprises / adaptations

- `edit_test.py` had a test explicitly asserting specs accept any status value — required update (now tests valid + invalid)
- Ruff auto-fixed yoda-style asserts in new test files and reordered imports in `enums.py`

### Rough edges / follow-ups

- `backlog/models.py` still has `is_valid_status()` with permissive (warn-only) validation — may want to tighten after migration
- Old per-kind constant names (`ISSUE_STATUSES`, `PROBLEM_STATUSES`, `IMPROVEMENT_STATUSES`) are gone — any external consumers would break (none found in grep)
- `decisions/registry.py` iterates `ADR_STATUSES` frozenset for dir inference — iteration order is arbitrary but functionally fine (first match wins, and status dirs are mutually exclusive)

## Phase 2 — Theme alignment and backlog migration

**Status**: complete
**Verification**: `just test` 3492 passed, `just lint` clean; VA-075-01 PASS, VA-075-02 PASS

### What's done

- **Theme removals**: `spec.status.live`, `policy.status.active`, `memory.status.deprecated`, `memory.status.obsolete`
- **Theme additions**: `adr.status.superseded` (#3c3836 dark grey), `policy.status.required` (#8ec07c green)
- **Backlog theme consolidation**: replaced 12 per-kind keys (`backlog.{issue,problem,improvement,risk}.*`) with 6 unified `backlog.status.*` keys
- **`get_backlog_status_style`**: simplified from `(kind, status)` to `(status)`; caller in `backlog_formatters.py` updated
- **Backlog migration**: 17 items updated on disk — `captured`→`open`, `closed`→`resolved`, `implemented`→`resolved`, `idea`→`open`
- **theme_test.py**: updated parametrized style names (`policy.status.active`→`required`, `backlog.issue.open`→`backlog.status.open`, `backlog.improvement.idea`→`backlog.status.resolved`)

### Design note

- `backlog.status.*` theme keys cover the full union of base + risk statuses (6 values), even though `backlog.status` in ENUM_REGISTRY returns only the base 4. This is correct: risk items look up via `backlog.status.{status}` and need `accepted`/`expired` themed.

## Phase 3 — Docs, guidance, and close-out

**Status**: complete

### What's done

- `mem.fact.spec-driver.status-enums` updated: added all governance + unified backlog enums, expanded scope paths, updated non-canonical terms
- ISSUE-009 acceptance criteria: 6/7 done (schema enforcement deferred as separate delta)
- ISSUE-009 current state, remaining scope, resolution history sections updated
- IP-075 verification coverage: VT-075-01, VT-075-02, VA-075-01, VA-075-02 all → `verified`
- Skills/guidance grep clean — no references to old per-kind backlog statuses
- Glossary — no updates needed
