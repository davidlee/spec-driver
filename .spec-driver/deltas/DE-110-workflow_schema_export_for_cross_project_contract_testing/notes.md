# Notes for DE-110

## Phase 01 — Complete

### Implementation summary

4 commits implementing DR-110:

1. `f6354c1c` — Attach `BlockMetadata` to all 15 `BlockSchema` registrations:
   - Added `metadata: BlockMetadata | None = None` field to `BlockSchema` (TYPE_CHECKING guard)
   - Wired `metadata=` at all 11 registration sites (delta.py, plan.py×3, verification.py, revision.py, relationships.py×2, workflow_metadata.py loop)
   - Created `spec_metadata.py` with `SPEC_RELATIONSHIPS_METADATA` and `SPEC_CAPABILITIES_METADATA`
   - Authored examples for all 7 workflow `BlockMetadata` objects

2. `b02411b0` — Replaced hardcoded `metadata_registry` dict in `schema.py`:
   - Removed duplicated 6-entry dict from `_render_json_schema()` and `_render_yaml_example()`
   - Eliminated `importlib` + `getattr` name-munging convention
   - Both functions now read `schema.metadata` directly
   - Net -57 lines

3. `3cb34452` — Tests: parameterised json-schema and yaml-example over all 15 block types

### Verification

- `schema_test.py`: 35/35 passed
- `blocks/` tests: 320/320 passed
- ruff: clean on all changed files
- pylint: 9.92/10 (2 pre-existing `import-outside-toplevel` for lazy yaml import — intentional)
- Manual: `spec-driver show schema workflow.state --format=json-schema` produces valid JSON Schema Draft 2020-12

### Key design choices

- Used `TYPE_CHECKING` guard for `BlockMetadata` import in `schema_registry.py` to keep the module lightweight at runtime
- Workflow examples based on real YAML from `DE-112/workflow/` where available; authored from schema fields for review-index, review-findings, sessions
- `spec_metadata.py` follows existing `*_metadata.py` convention — separate file from `relationships.py`
- Registration pattern asymmetry documented: domain modules import from sibling `*_metadata.py`, workflow_metadata.py self-registers

### No gotchas encountered

Clean implementation — all design assumptions from DR-110 held.
