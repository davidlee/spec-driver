# Notes for DE-103

## Phase 01 — Schema definitions and registration

### What's done

All 7 workflow/bridge schemas from DR-102 implemented as `BlockMetadata`
instances and registered in the block schema registry:

- **Workflow artifacts (5):** `workflow.state`, `workflow.handoff`,
  `workflow.review-index`, `workflow.review-findings`, `workflow.sessions`
- **Bridge blocks (2):** `workflow.notes-bridge`, `workflow.phase-bridge`

Files:
- `supekku/scripts/lib/blocks/workflow_metadata.py` — schema definitions + registration
- `supekku/scripts/lib/blocks/workflow_metadata_test.py` — 68 tests
- `supekku/cli/schema.py` — side-effect import added

### Adaptations

- **Sessions schema dynamic keys:** `FieldMetadata` requires non-empty
  `properties` for object type. The sessions map uses dynamic role-name keys.
  Worked around with a sentinel `_entry_shape` property in the metadata
  definition. Per-entry validation deferred to command-level code (Phase 02+).
  This is a known gap in the metadata system, not a design flaw.

- **Renderers:** Registered placeholder renderers. Real renderers will be added
  in Phase 02+ when CLI commands need to emit YAML.

### Verification

- 68 new tests passing (valid minimal, valid full, missing required, invalid
  enums, etc. for all 7 schemas)
- 320 total tests in `supekku/scripts/lib/blocks/` — zero failures
- 33 CLI schema tests — zero failures
- ruff clean
- `spec-driver list schemas` shows all 7 workflow schemas

### Commits

- `48b3ab8f` — feat(DE-103): workflow schema definitions and registry registration
- `.spec-driver` changes committed separately before code (phase sheet, delta, IP)

### Follow-up

- Phase 02: state machine + core commands — done (see below)

## Phase 02 — State machine and core CLI commands

### What's done

State machine, state I/O, and core CLI commands implemented:

- **State machine** (`state_machine.py`): 7 states, transition table, claim
  guard, `TransitionError`/`ClaimError` exceptions. Matches DR-102 §4 exactly.
- **State I/O** (`state_io.py`): Atomic read/write with `MetadataValidator`,
  `init_state` constructor, `update_state_workflow` mutation helper.
- **CLI commands**: `phase start`, `workflow status`, `block`/`unblock` —
  all delegating to domain logic in `state_machine.py` and `state_io.py`.
- **Schema fix**: Added `previous_state` field to `WORKFLOW_STATE_METADATA`
  for block/unblock persistence.
- **Config**: `[workflow]` and `[review]` sections already present in
  `DEFAULT_CONFIG` with correct defaults per DR-102 §9.

Files:
- `supekku/scripts/lib/workflow/state_machine.py` — state machine
- `supekku/scripts/lib/workflow/state_io.py` — state I/O
- `supekku/scripts/lib/workflow/operations.py` — domain operations (unused, kept for future skinny-CLI refactor)
- `supekku/cli/workflow.py` — CLI commands
- `supekku/cli/main.py` — command registration
- `supekku/scripts/lib/blocks/workflow_metadata.py` — `previous_state` field
- `supekku/scripts/lib/core/config.py` — `[workflow]`/`[review]` defaults + section comments

### Verification

- 25 state machine tests + 22 state I/O tests + 19 CLI tests = 66 total
- ruff clean
- All existing tests still passing (101 schema, 195 CLI, etc.)
- Smoke-tested against DE-103: `phase start`, `workflow status`, `block`/`unblock`

### Commits

- `d01a51d9` — chore(DE-103): fix IP-103 phase list, update phase-02 sheet
- `e7ce8b20` — feat(DE-103): state machine, state I/O, core CLI commands
- `b2d62195` — chore(DE-103): initialise workflow state for phase-02

### Follow-up

- Phase 03: handoff commands — done (see below)

## Phase 03 — Handoff commands

### What's done

`create handoff` and `accept handoff` CLI commands implemented per DR-102 §4/§5:

- **Handoff I/O** (`handoff_io.py`): Read/write/build with schema validation,
  atomic writes. `build_handoff` constructs payloads from structured inputs.
- **Git helpers**: `get_branch`, `has_uncommitted_changes`, `has_staged_changes`
  added to `supekku/scripts/lib/core/git.py`.
- **CLI `create handoff`**: Registered under `create` group. Assembles payload
  from state.yaml (required_reading, phase, artifact), git state, and config
  (handoff_boundary). Write order: handoff first, state second (DR-102 §5).
  Clears `claimed_by` on new handoff. Infers `next_activity_kind` from `to_role`.
- **CLI `accept handoff`**: Registered under new `accept` group. Claim guard:
  rejects if claimed by different identity, idempotent for same identity.
  Defaults `--identity` to `$USER`. Transitions to `reviewing` or `implementing`
  based on `to_role` from handoff payload.

Files:
- `supekku/scripts/lib/workflow/handoff_io.py` — handoff I/O + builder
- `supekku/scripts/lib/workflow/handoff_io_test.py` — 14 tests
- `supekku/scripts/lib/core/git.py` — new git helpers
- `supekku/cli/workflow.py` — `create_handoff_command`, `accept_handoff_command`, `accept_app`
- `supekku/cli/workflow_handoff_test.py` — 16 CLI tests
- `supekku/cli/create.py` — thin `create handoff` wrapper
- `supekku/cli/main.py` — `accept` group registration

### Verification

- 14 handoff I/O tests + 16 CLI tests = 30 new tests
- 96 total workflow tests passing
- 195 existing CLI tests still passing
- ruff clean

### Commits

- `d39362af` — chore(DE-103): phase-03 sheet
- `d92757ca` — feat(DE-103): create handoff + accept handoff CLI commands with claim guard

### Follow-up

- Phase 04: review commands (`review prime`, `review complete`, `review teardown`)
- `operations.py` still unused — future skinny-CLI refactor opportunity
- Placeholder renderers from Phase 01 still in place

---

## New Agent Instructions

### Task Card

**Delta:** `.spec-driver/deltas/DE-103-handover_and_review_orchestration/DE-103.md`
**Notes:** `.spec-driver/deltas/DE-103-handover_and_review_orchestration/notes.md` (this file)
**Status:** in-progress — Phases 01–03 complete, Phase 04 next.

### Next Activity

**Plan and execute Phase 04 — Review commands.**

Phase 04 scope (from IP-103 §4):
- `review prime` — generates `review-index.yaml` + `review-bootstrap.md` from current state
- `review complete --status <status>` — writes `review-findings.yaml`; transitions to `changes_requested` or `approved`
- `review teardown` — deletes reviewer state files
- Staleness/invalidation/reusability lifecycle for review-index (DR-102 §8)

### Required Reading

- `.spec-driver/deltas/DE-103-handover_and_review_orchestration/DE-103.md` — delta
- `.spec-driver/deltas/DE-103-handover_and_review_orchestration/IP-103.md` — plan (Phase 04 row)
- `.spec-driver/deltas/DE-102-handover_and_review_orchestration/DR-102.md` — design authority
  - §3.3 (review-index schema), §3.4 (review-findings schema)
  - §5 (CLI commands — `review prime`, `review complete`, `review teardown`, write ordering)
  - §8 (lifecycle and invalidation rules — staleness, reusability, teardown)
  - §9 (workflow.toml `[review]` config — `session_scope`, `teardown_on`, `bootstrap` settings)

### Related Documents

- `.spec-driver/backlog/improvements/IMPR-019-handover_and_review_orchestration/IMPR-019.md`
- `.spec-driver/backlog/improvements/IMPR-019-handover_and_review_orchestration/schema.md`

### Key Files

- `supekku/scripts/lib/workflow/` — state machine, state I/O, handoff I/O (Phases 02–03)
- `supekku/scripts/lib/blocks/workflow_metadata.py` — all 7 schema definitions (Phase 01); review-index and review-findings schemas already defined here
- `supekku/cli/workflow.py` — CLI commands (`workflow_app`, `phase_app`, `accept_app`, `create_handoff_command`)
- `supekku/cli/create.py` — `create handoff` thin wrapper (pattern for `create` subcommands)
- `supekku/cli/main.py` — command group registration
- `supekku/scripts/lib/core/git.py` — `get_head_sha`, `get_branch`, `short_sha`, `has_uncommitted_changes`, `has_staged_changes`
- `supekku/scripts/lib/core/config.py` — `[review]` and `[review.bootstrap]` config defaults

### Relevant Memories

- `mem.pattern.cli.skinny` — CLI files are thin orchestration; delegate to domain packages
- `mem.reference.spec-driver.workflow-config` — workflow.toml structure reference

### Unresolved Assumptions & Design Tensions

1. **`review prime` is complex.** It must: assemble domain_map from changed files,
   compute staleness from cache_key, build a markdown briefing, and handle
   incremental vs full rebuild. DR-102 §8 specifies all rules but implementation
   may surface edge cases (e.g., diff base selection for changed-file detection).
   Assess before coding.

2. **`review complete` needs review-findings I/O.** Similar pattern to handoff I/O
   but with round tracking and finding ID management. Round numbers are
   monotonically increasing — check how to read/increment from existing findings.

3. **`review teardown` policy gating.** Teardown behaviour depends on
   `[review].session_scope` and `[review].teardown_on` from workflow.toml.
   The config loader already supports these. Teardown deletes review-index,
   review-findings, and review-bootstrap.md.

4. **`operations.py` exists but is unused.** A previous agent created it as a
   domain layer for skinny CLI. It covers `phase_start`, `workflow_status`,
   `block_workflow`, `unblock_workflow` but not handoff or review operations.
   Decision: use it or continue the current pattern. Not blocking.

5. **Placeholder renderers** from Phase 01 are still registered for all 7
   schemas. Phase 04 review commands may need real renderers for review-index
   and review-findings if they need to be rendered for display.

### Commit State

- Worktree is clean for DE-103 code. Only `flake.lock`/`flake.nix` are modified
  (unrelated nix changes from another session — not DE-103 scope).
- No pending `.spec-driver` changes to commit.

### Advice

- Follow the same TDD pattern used in Phases 02–03: write I/O module + tests
  first, then CLI commands + tests.
- `review prime` is the most complex command in this phase — consider splitting
  it into smaller functions (domain map assembly, staleness evaluation,
  bootstrap markdown generation) and testing each independently.
- The `handoff_io.py` module is a good pattern to follow for review I/O.
- Phase 04 entrance criteria: Phase 03 complete ✓ (all handoff commands working).

---

## Phase 04 — Review commands

### What's done

All three review CLI commands implemented per DR-102 §3.3, §3.4, §5, §8:

- **Review I/O** (`review_io.py`): Read/write/build with schema validation for
  both `review-index.yaml` and `review-findings.yaml`. Atomic writes.
  `build_review_index` and `build_findings` construct payloads from structured
  inputs. `next_round_number` reads/increments round counter.
- **Staleness evaluator** (`staleness.py`): Evaluates bootstrap_status
  transitions per DR-102 §8 — commit drift, phase boundary crossing, major
  scope change, dependency surface expansion. Determines warm/stale/reusable/
  invalid status. `check_domain_map_files_exist` for filesystem-level
  invalidation.
- **Git helper**: `get_changed_files(from_ref, to_ref)` added to `git.py`.
- **CLI `review prime`**: Generates `review-index.yaml` + `review-bootstrap.md`.
  Evaluates existing cache staleness, rebuilds or incrementally updates.
  Builds domain_map from delta bundle files. Carries forward invariants/
  risk_areas/review_focus/known_decisions on incremental update. Records
  source_handoff when present.
- **CLI `review complete --status <status>`**: Writes `review-findings.yaml`
  with monotonically increasing round numbers. Transitions reviewing →
  changes_requested or reviewing → approved. Auto-teardown on approved per
  `[review].teardown_on` policy.
- **CLI `review teardown`**: Deletes review-index, review-findings, and
  review-bootstrap.md.

Files:
- `supekku/scripts/lib/workflow/review_io.py` — review I/O
- `supekku/scripts/lib/workflow/review_io_test.py` — 24 tests
- `supekku/scripts/lib/workflow/staleness.py` — staleness evaluator
- `supekku/scripts/lib/workflow/staleness_test.py` — 16 tests
- `supekku/scripts/lib/core/git.py` — `get_changed_files` helper
- `supekku/cli/workflow.py` — `review_app` with `prime`, `complete`, `teardown`
- `supekku/cli/workflow_review_test.py` — 21 CLI tests
- `supekku/cli/main.py` — `review` group registration

### Design Decisions

- **Domain map assembly**: Built from delta bundle files (delta docs, phase
  sheets, workflow artifacts). Git-diff-based changed-file discovery used for
  staleness evaluation of existing caches, not for initial domain map population.
  This keeps `review prime` usable without complex git history analysis.

- **Auto-teardown on approved**: When `[review].teardown_on` includes "approved"
  (the default), `review complete --status approved` automatically deletes
  reviewer state files after writing findings and transitioning state. This
  matches DR-102 §8.

- **Incremental update on reusable cache**: When staleness evaluator returns
  `reusable`, existing invariants/risk_areas/review_focus/known_decisions are
  preserved. Cache key is refreshed. Full rebuild otherwise.

- **Diff-base for staleness**: Compare `staleness.cache_key.head` to current
  HEAD. No merge-base complexity. `get_changed_files` wrapper uses
  `git diff --name-only`.

### Verification

- 24 review I/O tests + 16 staleness tests + 21 CLI tests = 61 new tests
- 138 total workflow tests passing
- 4378 total tests passing (2 pre-existing failures in package_utils_test)
- ruff clean

### Commits

- `13a3575f` — chore(DE-103): phase-04 sheet — review commands
- `3d203203` — feat(DE-103): review prime, review complete, review teardown CLI commands

### Follow-up

- Phase 05: phase complete, bridges, continuation refit — done (see below)
- `operations.py` still unused — future skinny-CLI refactor opportunity
- Placeholder renderers from Phase 01 still in place
- Git-diff-based domain_map construction (assembling code areas from changed
  files) deferred — current approach uses delta bundle structure

---

## Phase 05 — Phase complete, bridges, continuation refit

### What's done

- **`phase complete` command**: Marks phase complete in state.yaml. Emits
  auto-handoff per policy (`auto_handoff_on_phase_complete`) or bridge block
  (`handoff_ready: true`). Bridge block takes precedence over policy. `--to`
  flag overrides target role. `--no-handoff` suppresses emission. Idempotent
  re-run supported.
- **Bridge block I/O** (`bridge.py`): Extract phase-bridge and notes-bridge
  from markdown using fenced YAML block patterns. Render both bridge types.
  Full roundtrip extraction tested.
- **Continuation skill refit**: Updated SKILL.md to instruct agents to invoke
  `spec-driver create handoff` or `spec-driver phase complete` when
  `workflow/state.yaml` exists. No silent fallback to prose-only mode. Prose
  handoff preserved when no orchestration is active.

Files:
- `supekku/scripts/lib/workflow/bridge.py` — bridge extraction and rendering
- `supekku/scripts/lib/workflow/bridge_test.py` — 13 tests
- `supekku/cli/workflow.py` — `phase complete` command
- `supekku/cli/workflow_phase_complete_test.py` — 8 CLI tests
- `supekku/skills/continuation/SKILL.md` — refit
- `.spec-driver/skills/continuation/SKILL.md` — synced copy

### Verification

- 13 bridge tests + 8 phase complete CLI tests = 21 new tests
- 159 total workflow tests passing
- ruff clean

### Commits

- `c2ace647` — feat(DE-103): phase complete, bridge blocks, continuation skill refit

### Follow-up

- Phase 06: configuration, docs, integration testing, end-to-end verification

---

## Phase 06 — Configuration, docs, integration testing

### What's done

- **End-to-end integration test**: Full workflow cycle
  (start → implement → handoff → review → changes_requested → handoff →
  implement → handoff → review → approved) with auto-teardown. Verifies all
  DR-102 §12 evaluation criteria.
- **Phase complete cycle test**: Auto-handoff emission verified.
- **Block/unblock cycle test**: Round-trip state preservation verified.
- **Claim guard integration test**: Cross-identity rejection verified.
- **Regression test (VA-103-002)**: Existing deltas without `workflow/`
  continue to work. `workflow status` returns cleanly. Delta files untouched
  by workflow commands.
- **Memory record**: `mem.reference.workflow-commands` — quick reference for
  all workflow CLI commands, state transitions, file layout, domain modules.
- **Cleanup**: Removed unused `operations.py`.

Files:
- `supekku/cli/workflow_integration_test.py` — 6 integration tests
- `.spec-driver/memory/mem.reference.workflow-commands.md` — workflow reference

### Verification

- 6 new integration tests
- 165 total workflow tests passing
- ruff clean

### Commits

- `2ed7bfad` — feat(DE-103): phase 06 — integration tests, memory, cleanup

---

## New Agent Instructions

### Task Card

**Delta:** `.spec-driver/deltas/DE-103-handover_and_review_orchestration/DE-103.md`
**Notes:** `.spec-driver/deltas/DE-103-handover_and_review_orchestration/notes.md` (this file)
**Status:** in-progress — Phases 01–06 complete. Ready for audit and closure.

### Next Activity

**Audit and close DE-103.**

All 6 phases are complete. 165 workflow tests passing. DR-102 §12 criteria
verified end-to-end. Next step is `/audit-change` then `/close-change`.

### Required Reading

- `.spec-driver/deltas/DE-103-handover_and_review_orchestration/DE-103.md`
- `.spec-driver/deltas/DE-103-handover_and_review_orchestration/IP-103.md`
- `.spec-driver/deltas/DE-102-handover_and_review_orchestration/DR-102.md` §12

### Key Files

- `supekku/scripts/lib/workflow/` — state_machine, state_io, handoff_io, review_io, staleness, bridge
- `supekku/cli/workflow.py` — all CLI commands (phase start/complete, create/accept handoff, review prime/complete/teardown, workflow status, block/unblock)
- `supekku/cli/workflow_*.py` — 4 test files (handoff, review, phase_complete, integration)
- `supekku/scripts/lib/blocks/workflow_metadata.py` — 7 schema definitions
- `supekku/scripts/lib/core/config.py` — `[workflow]`/`[review]` config defaults
- `supekku/skills/continuation/SKILL.md` — refit skill

### Test Summary

- 165 total workflow tests passing
- 68 schema (Phase 01) + 47 state/IO (Phase 02) + 30 handoff (Phase 03)
- 61 review (Phase 04) + 21 bridge/phase-complete (Phase 05) + 6 integration (Phase 06)

### Remaining Work

- IP-103 progress tracking checkboxes need updating
- Placeholder renderers from Phase 01 still registered (not blocking — real rendering not needed)
- `operations.py` removed — skinny-CLI refactor deferred
