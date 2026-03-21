# Notes for DE-104

## Phase 01 — Enum registration, lifecycle map, CLI frontmatter sync

### Done (tasks 1.1–1.6)

- Registered `phase.status` in `ENUM_REGISTRY` using `_change_statuses` (1 line)
- Extended `CANONICAL_STATUS_MAP` with `done`, `active`, `in_progress` variants (3 entries)
- `phase start` updates frontmatter to `in-progress` before `state.yaml` (DEC-104-08)
- `phase complete` updates frontmatter to `completed` before `state.yaml` (DEC-104-08)
- `create_phase` uses `STATUS_DRAFT` constant (import added)
- New: `lifecycle_test.py` — normalize_status variants + canonical map coverage
- Extended: `enums_test.py` — phase.status presence, values, path listing
- Extended: `workflow_test.py` — phase start frontmatter update, tolerance for missing status
- Extended: `workflow_phase_complete_test.py` — frontmatter updated to completed, tolerance for no-frontmatter files, state.yaml still uses `"complete"`

### Deviation from DR-104

**state.yaml and handoff retain control-plane vocabulary** (`"complete"`, not `"completed"`). DR-104 §4.2 proposed normalising `state.yaml` and handoff payload to `STATUS_COMPLETED`, but the `PHASE_STATUS_VALUES` schema in `workflow_metadata.py` enforces `["not_started", "in_progress", "blocked", "complete", "skipped"]`. Writing `"completed"` breaks schema validation. The handoff schema uses the same vocabulary.

This means:
- Frontmatter (normative): `completed` ✓ (lifecycle vocabulary)
- state.yaml (transient): `complete` (control-plane vocabulary, unchanged)
- Handoff payload: `complete` (control-plane vocabulary, unchanged)
- Idempotency guard: `== "complete"` (reads from state.yaml)

This is correct — two vocabularies for two domains. DR should be updated to note this.

### Commits

- `201c24f4` — chore(DE-104): move delta to in-progress
- `6b47f1e4` — feat(DE-104): phase status enum, lifecycle map, CLI frontmatter sync

### Verification

- 77 tests pass (enums, lifecycle, workflow, phase_complete)
- Lint: no new warnings; all pre-existing

### Open

- Phase 02 (validation + `--fix`) and Phase 03 (skills/memory/backfill) still pending
- DR-104 §4.2 needs a deviation note re state.yaml/handoff vocabulary
