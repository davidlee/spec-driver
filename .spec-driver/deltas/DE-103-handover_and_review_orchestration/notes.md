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

- Phase 02: state machine + core commands (`phase start`, `workflow status`,
  `block`/`unblock`) — will need real renderers for `state.yaml`
