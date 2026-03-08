# Notes for DE-070

## Phase 1 — Registry sync and schema completeness (in progress)

### Done

- **RequirementRecord.to_dict()**: Added conditional ext_id/ext_url serialization.
  Changed from direct `return {...}` to building dict `d` then conditionally
  appending ext_id/ext_url before return.
- **PolicyRecord.to_dict()**: Added conditional ext_id/ext_url after backlinks block.
- **StandardRecord.to_dict()**: Same pattern as PolicyRecord.
- **BASE_FRONTMATTER_METADATA**: Added ext_id (string, optional) and ext_url
  (string, optional) to base schema. Placed before `relations` field.
  Confirmed `schema show frontmatter.base` renders them correctly.
- Ruff clean on all 4 edited files.
- Full test suite was running at interruption (3365+ tests expected).

- **Tests (task 1.6)**: Added to_dict() ext_id/ext_url tests to all three
  registry test files:
  - `requirements/registry_test.py`: TestRequirementRecordToDict (3 tests)
  - `policies/registry_test.py`: 3 new tests in TestPolicyRecord
  - `standards/registry_test.py`: 3 new tests in TestStandardRecord
  - All tests verify: absent when empty, present when set, partial (one field only)

- **Model ↔ schema parity audit (task 1.5, VA)**:
  Audited all 15 frontmatter metadata schemas against corresponding model
  dataclasses. BASE schema correctly includes ext_id/ext_url (optional).
  All artifact-specific schemas inherit from BASE.

  **Full parity (ext_id/ext_url in both model and schema)**:
  - Spec, ChangeArtifact (delta/plan/phase/task), BacklogItem (issue/problem/risk),
    PolicyRecord, StandardRecord, RequirementRecord

  **Gaps found (ext_id/ext_url in schema via BASE, absent from model)**:
  - MemoryRecord (`memory/models.py`) — missing ext_id, ext_url
  - DecisionRecord (`decisions/registry.py`) — missing ext_id, ext_url

  These gaps are out of DE-070 scope (which targeted registry sync for
  requirements/policies/standards). Tracked as follow-up.

### Observations

- RequirementRecord.to_dict() previously used a bare `return {...}` pattern
  (all fields unconditionally). Changed to `d = {...}; if ext_id: ...; return d`
  to keep ext_id/ext_url conditional. Other fields remain unconditional —
  that's the existing convention for RequirementRecord.
- Policy/Standard to_dict() already used conditional pattern for optional fields,
  so ext_id/ext_url additions were trivial appends.
- Backlog registry (`backlog.yaml`) is ordering-only — no field serialization
  needed. Not a gap.
