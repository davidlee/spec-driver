# Notes for DE-109

## Cross-project coherence: autobahn DE-001/DR-001

Coherence review identified 8 updates needed in autobahn's DR-001 when DE-109 lands:

1. BootstrapStatus enum: drop WARMING (5 values, not 6)
2. ReviewStatus enum: drop BLOCKED (4 values, not 5)
3. review-findings write surface: autobahn may write to `session` block within round records (DEC-109-009)
4. Consumed fields: expand beyond "round, status, finding counts" to include disposition structure
5. SUPPORTED_SCHEMAS: add review-findings v2
6. OQ-001: partially answered — CLI shapes in DR-109 §4; structured output remains DE-108
7. OQ-003: substantially answered by DR-109
8. Bootstrap status: stored value is snapshot, not authority; true status requires derivation

These are autobahn-side updates, not spec-driver action items.

## Phase 1 — Implementation log

### Validity matrix extension

DR-109 §3.2 defined 8 valid bootstrap transitions. During implementation,
idempotent self-transitions were needed for re-derivation scenarios:
`cold→cold`, `stale→stale`, `invalid→invalid`. These are not *state changes*
but repeated derivation producing the same result — the matrix assertion
would otherwise false-positive on legitimate re-checks. Extended to 11 pairs.

### can_approve() McCabe reduction

Extracted `_check_disposition()` helper to bring McCabe from 11 to acceptable.
`can_approve()` iterates findings and delegates per-action validation.

### Test runner note

`just test` uses system pytest which lacks pydantic in its path.
`uv run python -m pytest` uses the venv and works correctly.

### Pylint residual

`too-many-arguments` on `derive_bootstrap_status` (6/5). All params are
keyword-only and represent independent context inputs. A context dataclass
would add a type with no reuse value — accepted.

### Commits

- `43964de8` — feat: review_state_machine.py + tests (59 passing)
- `906ca886` — docs: phase 1 exit criteria + notes

Artefact updates (DR-109 accepted, DE-109 in_progress, stale dedup text)
were committed in prior session's `45485a35`.

### Verification

`uv run python -m pytest supekku/scripts/lib/workflow/review_state_machine_test.py` — 59 passed, last run after final commit.
`uv run ruff check` — clean on both files.
`just pylint-files` — 9.97/10 (1 residual, accepted).

### Phase 2 readiness

- Phase 1 module is a leaf — no imports from other supekku modules.
- Phase 2 (I/O layer) will import enums/models from review_state_machine.py.
- `collect_blocking_findings()` already parses v2-shaped round dicts — Phase 2
  must produce dicts in that shape from review_io.py.
- `derive_finding_status()` is ready for Phase 2 to call on read/write paths.

### Rough edges / follow-ups

- `just test` fixed — now uses `uv run python -m pytest` (commit `ad04ab4c`).
- `ConfigDict(extra="ignore")` is universal in this codebase. Not a gotcha,
  just confirmed convention — future Pydantic models should follow suit.

## Phase 2 — Implementation log

### Schema v2 changes

- `REVIEW_FINDINGS_METADATA` → v2: `rounds` array replaces flat structure.
  Per-round entries have `round`, `status`, `reviewer_role`, `completed_at`,
  `session` (opaque), `blocking`, `non_blocking`.
- `REVIEW_INDEX_METADATA` gains `judgment_status` (optional enum).
- Added `_finding_disposition()` sub-schema and `_round_entry()` helper
  to `workflow_metadata.py`.

### Session metadata (OQ-109-002 resolved)

`FieldMetadata` requires non-empty properties for object type. Session is
opaque/freeform (DR-109 §3.6), so it's omitted from the schema — the validator
doesn't reject unknown keys, so session data passes through unvalidated.
This is the intended behavior.

### CLI compatibility fix (pulled ahead from Phase 3)

`review complete` updated to use v2 `build_findings()`/`append_round()` API.
Without this, the CLI would crash on any review complete. Minimal fix:
first round creates v2, subsequent rounds append. Summary/history feature
deferred to Phase 3 proper.

### Pre-existing test fixes

10 failures fixed across 3 files:
- `card_formatters_test.py` — positional args → keyword args (Pydantic migration)
- `package_utils_test.py` — `workflow` added to `KNOWN_LEAF_PACKAGES`
- `DL-047` drift ledger — YAML evidence strings with colons needed quoting

### Commits

- `91af7aae` — feat: phase 2 implementation
- `1cae793a` — fix: 10 pre-existing test failures

### Verification

`uv run python -m pytest supekku` — 4533 passed, 0 failures.
`uv run ruff check` — clean on all changed files.

---

## New Agent Instructions

### Task card

**Delta**: `.spec-driver/deltas/DE-109-review_state_machine_formalisation/DE-109.md`
**Notes**: this file (`notes.md`)

### Status

- Phase 1 (domain model) — **complete**. 59 tests.
- Phase 2 (I/O layer) — **complete**. 44 tests + CLI/schema tests updated.
- Phase 3 (CLI commands) — **next**. Phase sheet needs creation.
- Phase 4 (integration/cleanup) — planned.

### Required reading

1. `DE-109/DR-109.md` §4 — CLI UX for disposition and query commands
2. `DE-109/IP-109.md` §5 Phase 3 — CLI commands scope
3. `DE-109/phases/phase-01.md` and `phase-02.md` — completed work

### Key files

- `supekku/scripts/lib/workflow/review_state_machine.py` — domain enums, models, guards (Phase 1)
- `supekku/scripts/lib/workflow/review_io.py` — I/O layer with v2 accumulative model (Phase 2)
- `supekku/scripts/lib/blocks/workflow_metadata.py` — schema definitions (v2)
- `supekku/cli/workflow.py` — CLI commands (Phase 3 target)
- `supekku/cli/workflow_review_test.py` — CLI review tests

### What Phase 3 must deliver (from IP-109)

1. **Disposition commands**: `review finding resolve|defer|waive|supersede`
   - DR-109 §4.1 defines CLI shapes and constraints
   - `update_finding_disposition()` and `find_finding()` in review_io.py are ready
   - Each command: read findings → validate constraints → update in-place → write
2. **Update `review prime`**: set judgment to `in_progress` via `apply_review_transition()`
3. **Update `review complete`**: enforce `can_approve()` guard on `--status approved`
4. **Write judgment transition to review-index** on complete

### What was pulled ahead from Phase 3

`review complete` already uses v2 `build_findings()`/`append_round()` (Phase 2
compatibility fix). It does NOT yet:
- Use `apply_review_transition()` for judgment
- Enforce `can_approve()` guard
- Write `judgment_status` to review-index
- Handle `--summary` (currently ignored)

### Loose ends

- `summary` parameter in `review complete` is accepted but ignored in v2. Phase 3
  should wire it into round metadata or remove it.
- OQ-109-001 (WorkflowState duplication in workflow_metadata.py) — deferred to
  Phase 4 if natural.

### Commit state

All `.spec-driver/` and code changes are committed. Worktree is clean except
`.claude/settings.local.json`. Full suite green (4533 passed, 0 failures).

### Relevant ADRs/policies

- POL-002: no magic strings — disposition commands must use StrEnums
- ADR-009: standard registry API convention

### Verification

```
just test          # 4533 passed
just lint          # clean
just pylint-report # check score
```
