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

- Phase 03: handoff commands (`create handoff`, `accept handoff` with claim guard)
- `operations.py` exists but is unused — consider refactoring CLI to delegate
  through it (skinny CLI pattern) in a future pass
- Placeholder renderers from Phase 01 still in place — real renderers needed
  when commands emit YAML for non-state schemas
