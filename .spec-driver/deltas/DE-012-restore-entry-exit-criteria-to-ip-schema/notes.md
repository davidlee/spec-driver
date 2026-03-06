# Notes for DE-012

## Historical Context - What Was Removed

### Initial Schema (commit cb4b6a8 - 2025-11-02)
When `plan_metadata.py` was first created, the `plan.overview@v1` phases array included full metadata:

```python
"phases": FieldMetadata(
  type="array",
  items=FieldMetadata(
    type="object",
    properties={
      "id": FieldMetadata(...),
      "name": FieldMetadata(...),           # Phase name
      "objective": FieldMetadata(...),       # Phase objective
      "entrance_criteria": FieldMetadata(...), # Array of criteria strings
      "exit_criteria": FieldMetadata(...),    # Array of criteria strings
    },
  ),
)
```

Example from initial schema:
```yaml
phases:
  - id: PLN-001-P01
    name: "Phase 01 - Foundation"
    objective: "Establish core authentication infrastructure"
    entrance_criteria:
      - "Requirements finalized in RE-001"
      - "Architecture review completed"
    exit_criteria:
      - "OAuth2 provider integrated"
      - "Unit tests passing"
      - "Security audit completed"
```

### Simplification (commit 71f1abe - 2025-11-03)
The schema was simplified to ID-only format to eliminate perceived duplication with `phase.overview` blocks:

```python
"phases": FieldMetadata(
  type="array",
  description="Ordered list of phase IDs (metadata in phase.overview blocks)",
  items=FieldMetadata(
    type="object",
    properties={
      "id": FieldMetadata(...),  # Only ID remains
    },
  ),
)
```

Example after simplification:
```yaml
phases:
  - id: IP-004.PHASE-01
  - id: IP-004.PHASE-02
```

**Removed fields**:
- `name` (string)
- `objective` (string)
- `entrance_criteria` (array of strings)
- `exit_criteria` (array of strings)

### Key Commits

1. **cb4b6a8** (2025-11-02): "feat: metadata validation"
   - Created `plan_metadata.py` with full phase metadata in phases array
   - Initial implementation had `name`, `objective`, `entrance_criteria`, `exit_criteria`

2. **71f1abe** (2025-11-03): "feat: update specs for contract changes and register phase.tracking schema"
   - Simplified phases array to ID-only format
   - Removed `name`, `objective`, `entrance_criteria`, `exit_criteria` from plan.overview phases
   - Rationale: Eliminate duplication with phase.overview blocks
   - Note: This was done as part of DE-004 Phase 06 work

3. **6f69db8** (2025-11-03): "feat(DE-004): Phase 06 - schema simplification & phase.tracking metadata"
   - Completed DE-004 Phase 06
   - Migrated all existing IP files to ID-only format
   - Updated documentation and tests

### Important Notes

1. **phase.overview schema was NOT changed** - it still has `entrance_criteria` and `exit_criteria` fields
2. **create_phase never copied criteria** - the functionality to copy from IP to phase was never implemented
3. **This is additive work** - restoring the fields is backward compatible (all fields will be optional)
4. **Reference diff**: `git diff c527a48..71f1abe -- supekku/scripts/lib/blocks/plan_metadata.py`

