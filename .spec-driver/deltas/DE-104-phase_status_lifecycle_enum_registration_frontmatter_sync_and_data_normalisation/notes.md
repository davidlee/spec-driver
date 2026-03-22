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

## Phase 02 — Validation + --fix, schema, skills, memory, backfill

### Done (tasks 2.1–2.7)

- `_validate_phase_statuses()` + `_validate_single_phase()` in `WorkspaceValidator`
  - Walks `deltas/*/phases/phase-[0-9][0-9].md` (DEC-104-06)
  - Checks: non-canonical status, missing status, wrong kind, missing overview block
  - `--fix` normalises via `CANONICAL_STATUS_MAP` (DEC-104-05)
  - 12 new tests in `validator_test.py`
- `--fix` flag wired through `workspace.py` → `validate_ws()` → `WorkspaceValidator`
- Schema example: `plan.py` phase status `"active"` → `"in-progress"`
- 5 skills updated: `/execute-phase` (canonical vocab + CLI guidance), `/update-delta-docs` (phase status ref), `/continuation` (frontmatter note), `/close-change` (phase status check), `/plan-phases` (do-not-hand-craft guardrail)
- 2 memory records updated: `mem.reference.workflow-commands` (dual-store, frontmatter sync), `mem.fact.spec-driver.status-enums` (phase.status + variants + scope paths)
- Backfill: 60 files normalised via `validate --fix`. Zero non-canonical frontmatter statuses remain. Idempotent — second run touches zero files.

### Commits

- `58e83d75` — feat(DE-104): phase validation with --fix, schema example fix
- `77a5d95f` — docs(DE-104): update 5 skills and 2 memory records
- `101bb1b4` — fix(DE-104): backfill all phase statuses to canonical values
- `b814c42f` — fix(DE-104): lint fixes

### Verification

- 120 DE-104-specific tests pass (enums, lifecycle, workflow, phase_complete, validator)
- 3915 full suite tests pass; 1 pre-existing failure (`package_utils_test` — leaf package count from DE-103, not DE-104)
- Lint: no new warnings from DE-104 changes
- Post-backfill grep confirms zero non-canonical frontmatter statuses

### Open

- DR-104 §4.2 deviation: state.yaml/handoff retain control-plane vocabulary — documented in Phase 01 notes
- Pre-existing test failure in `package_utils_test.py` (KNOWN_LEAF_PACKAGES missing `supekku/scripts/lib/workflow`) — not DE-104's concern
- Delta ready for audit/closure
