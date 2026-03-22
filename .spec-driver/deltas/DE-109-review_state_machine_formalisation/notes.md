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

- `just test` broken for all pydantic-dependent tests (system pytest lacks deps).
  Not DE-109's problem but worth a backlog item if not already tracked.
- `ConfigDict(extra="ignore")` is universal in this codebase. Not a gotcha,
  just confirmed convention — future Pydantic models should follow suit.
