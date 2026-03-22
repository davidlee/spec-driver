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

## Phase 3 — Implementation log

### Deliverables

- 4 disposition subcommands: `review finding resolve|defer|waive|supersede`
- `review prime` sets `judgment_status: in_progress` via `apply_review_transition()`
- `review complete --status approved` enforces `can_approve()` guard
- `review complete` writes `judgment_status` to review-index
- `--summary` wired into round metadata (`build_round_entry`/`append_round`/`build_findings`)
- `summary` field added to round entry schema in `workflow_metadata.py`

### Design choices

- **Default authority**: All CLI disposition commands default to `authority: agent`.
  `--authority user` overrides explicitly (waive command). This follows the model
  where agents are the typical CLI invokers; human authority requires opt-in.
- **Shared orchestration**: `_disposition_finding()` helper handles all 4 commands
  (read → validate → update → write). Each command builds a disposition dict and
  delegates. Keeps CLI thin (~160 lines for all disposition code).
- **Finding not found**: Lists available IDs from all rounds for discoverability.
- **Guard placement**: Guard runs before round append, so failed approval doesn't
  create a spurious round entry.
- **Judgment write**: Non-fatal if review-index doesn't exist (e.g. teardown already
  ran). Findings and state are higher priority writes.

### Gotcha: FindingDisposition.authority is required

`FindingDisposition(BaseModel)` has `authority: DispositionAuthority` as a required
field (not optional). Every disposition dict passed to `update_finding_disposition()`
must include authority. Initial implementation missed this — Pydantic validation
caught it at write time.

### Commits

- `1fa074fc` — feat(DE-109): Phase 3 implementation + 22 new tests

### Verification

`uv run python -m pytest supekku` — 4562 passed, 0 failures.
`uv run ruff check` — clean on all changed files.
`just pylint-files` — no new warnings (pre-existing only).

### Phase 4 readiness

Phase 3 is functionally complete. Phase 4 (integration/cleanup) remains:
- Derive `workflow_metadata.py` validation lists from StrEnums (POL-002)
- Refactor `staleness.py` to import BootstrapStatus from review_state_machine
- End-to-end test: multi-round review with disposition and approval
- `just check` green

---

## New Agent Instructions

### Task card

**Delta**: `.spec-driver/deltas/DE-109-review_state_machine_formalisation/DE-109.md`
**Notes**: this file (`notes.md`)

### Status

- Phase 1 (domain model) — **complete**. 59 tests.
- Phase 2 (I/O layer) — **complete**. 44 tests + CLI/schema tests updated.
- Phase 3 (CLI commands) — **complete**. 22 new tests (43 review tests total).
- Phase 4 (integration/cleanup) — **next**. Phase sheet needs creation.

### Required reading

1. `DE-109/DR-109.md` — full design (§4 for CLI, §3 for domain model)
2. `DE-109/IP-109.md` — phase overview and VT coverage
3. `DE-109/phases/phase-01.md` through `phase-03.md` — completed work

### Key files

- `supekku/scripts/lib/workflow/review_state_machine.py` — domain enums, models, guards (Phase 1)
- `supekku/scripts/lib/workflow/review_io.py` — I/O layer with v2 accumulative model (Phase 2)
- `supekku/scripts/lib/blocks/workflow_metadata.py` — schema definitions (v2)
- `supekku/cli/workflow.py` — CLI commands (Phase 3 target)
- `supekku/cli/workflow_review_test.py` — CLI review tests

### What Phase 4 must deliver (from IP-109)

1. Derive `workflow_metadata.py` validation lists from StrEnums (POL-002)
2. Refactor `staleness.py`: import `BootstrapStatus` from `review_state_machine`, call `derive_bootstrap_status()`
3. End-to-end test: multi-round review with disposition and approval (VT-109-009)
4. `just check` green (lint + test)

### Loose ends

- OQ-109-001 (WorkflowState duplication in workflow_metadata.py) — Phase 4 if natural.

### Commit state

All `.spec-driver/` and code changes committed. Full suite green (4562 passed).

### Relevant ADRs/policies

- POL-002: no magic strings — disposition commands use StrEnums
- ADR-009: standard registry API convention

### Verification

```
uv run python -m pytest supekku  # 4562 passed
uv run ruff check                # clean
just pylint-files                # no new warnings
```
