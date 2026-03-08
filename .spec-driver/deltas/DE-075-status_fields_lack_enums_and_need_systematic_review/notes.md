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

## Phase 2 — Theme alignment and backlog migration (next)

### Open questions

- Backlog migration: several items use legacy statuses (`captured`, `idea`, `done`, `implemented`, `in-progress` on improvements). Need manual frontmatter edits per DEC-075-05 mapping.
- Theme consolidation: per-kind backlog sections in `theme.py` (e.g. `backlog.issue.*`, `backlog.problem.*`) — collapse to unified `backlog.status.*` keys or keep per-kind keys pointing to shared colours?
