---
id: ISSUE-010
name: Add path field to requirements JSON output for automation workflows
created: '2025-11-02'
updated: '2025-11-02'
status: resolved
kind: issue
categories: [enhancement, json-output]
severity: p3
impact: user
---

# Add path field to requirements JSON output for automation workflows

## Problem

The `spec-driver list requirements --json` command does not include a `path` field in its JSON output, making it difficult to automate workflows that need to locate requirement source files.

Unlike specs, changes, and decisions which include path information in their JSON output, requirements lack this field.

## Context

- Related to DE-005 (spec backfill implementation)
- Part of systematic review of JSON outputs across all entity types
- Requirements are defined in spec files, so path information exists but requires traversal
- See `JQ_VALIDATION_REPORT.md` for analysis of JSON output consistency

## Current Behavior

```bash
uv run spec-driver list requirements --json | jq '.items[0]'
{
  "uid": "SPEC-009.FR-001",
  "label": "FR-001",
  "title": "Requirement title",
  "status": "draft"
  # No path field
}
```

## Desired Behavior

```bash
uv run spec-driver list requirements --json | jq '.items[0]'
{
  "uid": "SPEC-009.FR-001",
  "label": "FR-001",
  "title": "Requirement title",
  "status": "draft",
  "spec_path": "specify/tech/SPEC-009/SPEC-009.md"  # Add this
}
```

## Implementation Notes

- Requirements are stored in spec files, not separate files
- `RequirementRecord` model would need to track source spec path
- Path can be derived from spec ID (first part of UID before dot)
- Consider field name: `spec_path` (clear) vs `path` (consistent with other entities)

## Acceptance Criteria

- [ ] `list requirements --json` includes path information
- [ ] Path field allows locating the spec file containing the requirement
- [ ] Tests updated for new JSON structure
- [ ] Formatters maintain backward compatibility where possible
