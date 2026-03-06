---
id: ISSUE-024
name: Add ExtID and ExtURL support to specs, requirements, backlog, policies, standards
created: '2025-11-08'
updated: '2025-11-08'
status: open
kind: issue
categories: [enhancement, integration]
severity: p3
impact: user
---

# Add ExtID and ExtURL support to specs, requirements, backlog, policies, standards

## Problem

Spec-driver artifacts (specs, requirements, backlog items, policies, standards) currently have no way to reference external ticketing systems (JIRA, Linear, GitHub Issues, etc.). This makes it difficult to:

- Track correspondence between internal spec-driver artifacts and external project management tools
- Link to external discussions, tickets, or documentation
- Integrate spec-driver into existing workflows that rely on external systems

## Proposed Solution

Add two optional frontmatter fields to all artifact types:

- `ext_id` (string): External system identifier (e.g., "JIRA-1234", "GH-567")
- `ext_url` (string): Direct link to the external resource

## Scope

### Artifact Types Affected

- Specs (SPEC-*, PROD-*)
- Requirements (FR-*, NF-*)
- Backlog items (issues, problems, improvements, risks)
- Policies (POL-*)
- Standards (STD-*)

### Display Changes

#### List/Table Views

Add `--external` / `-e` flag to list commands to show external ID:

```bash
# Current
uv run spec-driver list specs
SPEC-001  active   Core Registry

# With --external flag
uv run spec-driver list specs --external
SPEC-001  JIRA-1234  active   Core Registry

# Requirements list
uv run spec-driver list requirements --external
FR-001  GH-42  pending  User authentication
```

Display position:
- For artifacts with ID column: immediately right of internal ID
- For requirements: immediately right of Label column

#### JSON Output

Include fields in JSON output:

```json
{
  "id": "SPEC-001",
  "ext_id": "JIRA-1234",
  "ext_url": "https://jira.example.com/browse/JIRA-1234",
  ...
}
```

#### Show/Detail Views

Display in metadata section when present:

```
SPEC-001: Core Registry
External: JIRA-1234 (https://jira.example.com/browse/JIRA-1234)
Status: active
...
```

## Implementation Notes

### Model Changes

Each domain model needs optional fields:
- `supekku/scripts/lib/specs/models.py` - Spec model
- `supekku/scripts/lib/requirements/models.py` - Requirement model
- `supekku/scripts/lib/backlog/models.py` - BacklogItem model
- Policy/Standard models (when implemented)

### Formatter Changes

- `supekku/scripts/lib/formatters/spec_formatters.py`
- `supekku/scripts/lib/formatters/requirement_formatters.py`
- `supekku/scripts/lib/formatters/backlog_formatters.py`
- Policy/standard formatters (when implemented)

Each needs:
- Add `show_external: bool = False` parameter to list formatters
- Conditionally include ext_id column in table output
- Include ext_id/ext_url in JSON output
- Format detail views to show external references

### CLI Changes

Add `--external` / `-e` flag to list commands:
- `supekku/cli/list.py` - add flag to all list subcommands
- Pass through to formatter functions

### Registry Changes

Registries should capture ext_id/ext_url in YAML:
- `.spec-driver/registry/specs.yaml`
- `.spec-driver/registry/requirements.yaml`
- `.spec-driver/registry/backlog.yaml`

## Acceptance Criteria

- [ ] Frontmatter schema supports `ext_id` and `ext_url` fields (optional)
- [ ] All affected models include ext_id/ext_url attributes
- [ ] `list` commands support `--external` / `-e` flag
- [ ] External ID displays in correct column position when flag used
- [ ] JSON output includes ext_id/ext_url fields
- [ ] Show/detail views display external references when present
- [ ] Registries capture external ID/URL metadata
- [ ] Tests cover new fields and formatting
- [ ] Documentation updated

## Related Issues

- ISSUE-007: CLI commands missing JSON output support
- ISSUE-010: Add path field to requirements JSON output
- ISSUE-011: Add path field to backlog items JSON output

