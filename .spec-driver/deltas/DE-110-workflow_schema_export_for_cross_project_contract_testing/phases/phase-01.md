---
id: IP-110-P01
slug: "110-workflow_schema_export_for_cross_project_contract_testing-phase-01"
name: "Wire metadata to BlockSchema and complete schema show coverage"
created: "2026-03-22"
updated: "2026-03-22"
status: draft
kind: phase
plan: IP-110
delta: DE-110
---

# Phase 01 — Wire metadata to BlockSchema and complete schema show coverage

## 1. Objective

Make `show schema <type> --format=json-schema` and `--format=yaml-example` work for all 15 registered block types by attaching `BlockMetadata` directly to `BlockSchema` and eliminating the hardcoded lookup dict in `schema.py`.

## 2. Links & References

- **Delta**: DE-110
- **Design Revision**: DR-110 (approved) — §4.1–§4.5
- **Specs**: PROD-012

## 3. Entrance Criteria

- [x] DR-110 approved
- [x] No blocking dependencies

## 4. Exit Criteria / Done When

- [ ] All 15 `show schema <type> --format=json-schema` produce valid JSON Schema
- [ ] All 15 `show schema <type> --format=yaml-example` produce valid YAML
- [ ] Hardcoded `metadata_registry` dict removed from `schema.py`
- [ ] Tests pass, lint clean (ruff + pylint)
- [ ] Worktree committed

## 5. Verification

- `uv run python -m pytest supekku/cli/schema_test.py -v`
- `uv run ruff check` on all changed files
- `just pylint-files` on all changed files
- Manual: `uv run spec-driver show schema workflow.state --format=json-schema` produces output

## 6. Assumptions & STOP Conditions

- Assumptions: No circular import issues (verified during DR)
- STOP when: Any block type produces invalid JSON Schema or breaks existing output

## 7. Tasks & Progress

| Status | ID  | Description | Parallel? | Notes |
|--------|-----|-------------|-----------|-------|
| [ ] | 1.1 | Add `metadata` field to `BlockSchema` | | DR §4.1 |
| [ ] | 1.2 | Wire `metadata=` at 6 existing registration sites | [P] | DR §4.3 — delta.py, plan.py (×3), verification.py, revision.py |
| [ ] | 1.3 | Wire `metadata=` in workflow registration loop | [P] | DR §4.3 — workflow_metadata.py |
| [ ] | 1.4 | Create `spec_metadata.py` | [P] | DR §4.4 — BlockMetadata for spec.relationships + spec.capabilities |
| [ ] | 1.5 | Wire `metadata=` at spec registration in relationships.py | | After 1.4 |
| [ ] | 1.6 | Author 7 workflow examples | | DR §4.5 — roughly half the effort |
| [ ] | 1.7 | Replace hardcoded dict in `schema.py` | | DR §4.2 — depends on 1.1–1.6 |
| [ ] | 1.8 | Tests | | Parameterised over all 15 types |
| [ ] | 1.9 | Lint + verify | | ruff, pylint, manual check |

### Task Details

- **1.1 Add `metadata` field to `BlockSchema`**
  - **Files**: `supekku/scripts/lib/blocks/schema_registry.py`
  - **Approach**: Add `metadata: BlockMetadata | None = None` using `TYPE_CHECKING` guard for the import. Single-field addition, backward-compatible.

- **1.2 Wire existing registrations**
  - **Files**: `delta.py`, `plan.py`, `verification.py`, `revision.py`
  - **Approach**: Each file imports its `*_METADATA` constant from sibling `*_metadata.py` and passes `metadata=` to `BlockSchema(...)`.

- **1.3 Wire workflow registration loop**
  - **Files**: `workflow_metadata.py`
  - **Approach**: The `_WORKFLOW_SCHEMAS` tuple already contains the metadata object as element [4]. Pass it through as `metadata=_meta` in the `register_block_schema` call.

- **1.4 Create `spec_metadata.py`**
  - **Files**: NEW `supekku/scripts/lib/blocks/spec_metadata.py`
  - **Approach**: ~120 lines. Two `BlockMetadata` objects: `SPEC_RELATIONSHIPS_METADATA` and `SPEC_CAPABILITIES_METADATA`. Fields derived from `RelationshipsBlockValidator` and `render_spec_capabilities_block`. One example each.

- **1.5 Wire spec registration**
  - **Files**: `relationships.py`
  - **Approach**: Import from `spec_metadata.py` at registration site (bottom of file). Pass `metadata=` to both `register_block_schema` calls.

- **1.6 Author workflow examples**
  - **Files**: `workflow_metadata.py`
  - **Approach**: Add `examples=[{...}]` to each of the 7 `BlockMetadata` objects. Base `workflow.state` and `workflow.handoff` on real files from `DE-112/workflow/`. Author remaining 5 from schema field definitions. Keep minimal but structurally complete.

- **1.7 Replace hardcoded dict in `schema.py`**
  - **Files**: `supekku/cli/schema.py`
  - **Approach**: In `_render_json_schema()` and `_render_yaml_example()`, replace `metadata_registry` dict + `importlib` + `getattr` with `if not schema.metadata: ... return` / `schema.metadata`. Delete ~20 lines of lookup code per function.

- **1.8 Tests**
  - **Files**: `supekku/cli/schema_test.py`
  - **Approach**: Parameterised test: for each of 15 block types, call `show_schema(type, format_type="json-schema")` and `show_schema(type, format_type="yaml-example")`, assert no exception and valid output. Regression check: existing 6 types produce structurally identical JSON Schema.

## 8. Risks & Mitigations

| Risk | Mitigation | Status |
|------|-----------|--------|
| Workflow examples invalid | Validate each against its own BlockMetadata field definitions | Open |

## 9. Decisions & Outcomes

- DR-110 DEC-110-001/002/003 govern all design choices.

## 11. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] Verification evidence stored
- [ ] Notes updated
- [ ] Delta/IP updated
