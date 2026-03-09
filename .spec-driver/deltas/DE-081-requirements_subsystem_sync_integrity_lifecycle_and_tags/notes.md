# Notes for DE-081

## Session 2026-03-09

### What's done

- **O1 (ISSUE-032)**: Coverage replacement semantics. `_apply_coverage_blocks()` clears all `coverage_evidence` and `coverage_entries` before rebuilding from current sources. Sync idempotency (NF-002) restored.
- **O2 (ISSUE-029)**: `deprecated`/`superseded` lifecycle statuses added to `lifecycle.py`. `TERMINAL_STATUSES` set guards these from coverage-derived overwrite.
- **O3 (ISSUE-018)**: `_REQUIREMENT_LINE` regex extended with optional `[tag1, tag2]` group. Tags populate registry, survive round-trip, and work with existing `filter(tag=...)`.
- **ISSUE-033**: Confirmed already fixed by DE-043. Closed.
- **ISSUE-030/IMPR-007**: Closed as resolved by prior deltas (DE-071, DE-065).
- SPEC-122 coverage block and FR-002 updated. AUD-003 completed. Delta closed via RE-037.

### Surprises / adaptations

- ISSUE-033 was filed as p2 but had already been fixed by DE-043 (commit `62cfcd5`). The current code filters unknown coverage statuses at both ingestion and derivation boundaries.
- `filter(tag=...)` already existed on `RequirementsRegistry` — task 1.6 was a no-op.
- `RequirementRecord.merge()` already unioned tags — no change needed.
- The lifecycle.py and registry.py implementation changes were already present in the working tree (committed by user in `2e17e7d` before this session's test-writing phase).

### Verification

- 3573 tests pass, 0 failures. `ruff check` clean. `pylint` — no new warnings on changed files.

### Commits

- `2e17e7d` — user commit with implementation + artefacts
- `11868e8` — tests (10 new)
- `4557cc4` — spec coverage, backlog closure
- `450b7ed` — AUD-003
- `7736c8d` — delta closure

All `.spec-driver` changes committed promptly.

### Potential follow-ups

- `superseded_by` cross-linking field not added (noted as out-of-scope in DR-081; needs relationship model work).
- Coverage clear-and-rebuild means manual registry edits to coverage fields are overwritten — correct per ADR-008 §5 but worth noting in agent guidance if it causes confusion.
