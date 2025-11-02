---
id: ISSUE-011
name: Add path field to backlog items JSON output for automation workflows
created: '2025-11-02'
updated: '2025-11-02'
status: open
kind: issue
categories: [enhancement, json-output]
severity: p3
impact: user
---

# Add path field to backlog items JSON output for automation workflows

## Problem

The `spec-driver list backlog --json` command does not include a `path` field in its JSON output, making it difficult to automate workflows that need to locate backlog item files.

Unlike specs, changes, and decisions which include path information in their JSON output, backlog items lack this field.

## Context

- Related to DE-005 (spec backfill implementation)
- Part of systematic review of JSON outputs across all entity types
- Backlog items are stored as individual markdown files in `backlog/{kind}/{id}/`
- See `JQ_VALIDATION_REPORT.md` for analysis of JSON output consistency

## Current Behavior

```bash
uv run spec-driver list backlog --json | jq '.items[0]'
{
  "id": "ISSUE-009",
  "kind": "issue",
  "title": "Status fields lack enums",
  "status": "open"
  # No path field
}
```

## Desired Behavior

```bash
uv run spec-driver list backlog --json | jq '.items[0]'
{
  "id": "ISSUE-009",
  "kind": "issue",
  "title": "Status fields lack enums",
  "status": "open",
  "path": "backlog/issues/ISSUE-009-status-fields-lack-enums/ISSUE-009.md"  # Add this
}
```

## Implementation Notes

- `BacklogItem` model needs `path` attribute added
- Path is available during discovery in `discover_backlog_items()`
- Path follows pattern: `backlog/{kind}s/{id}-{slug}/{id}.md`
- Implementation location: `supekku/scripts/lib/backlog/models.py` and `supekku/scripts/lib/backlog/registry.py`
- Formatter: `supekku/scripts/lib/formatters/backlog_formatters.py:format_backlog_list_json()`

## Acceptance Criteria

- [ ] `BacklogItem` model includes `path` attribute
- [ ] `list backlog --json` includes path field in output
- [ ] Path allows direct file access for automation
- [ ] Tests updated for new JSON structure
- [ ] Formatters maintain backward compatibility where possible

