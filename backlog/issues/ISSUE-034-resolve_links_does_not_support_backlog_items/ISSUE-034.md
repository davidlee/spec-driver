---
id: ISSUE-034
name: Resolve links does not support backlog items
created: '2026-03-05'
updated: '2026-03-05'
status: open
kind: issue
---

# Resolve links does not support backlog items

## Summary
`uv run spec-driver resolve links` does not resolve wikilinks to backlog items
(e.g., `[[PROB-002]]`). These show up as missing targets even when the files
exist under `backlog/`.

## Impact
- Memory link resolution reports missing targets for problems/issues/improvements.
- Creates noise in link resolution output and risks discouraging backlog cross-links.

## Proposed Fix
Extend resolver to include backlog items (issues, problems, improvements, risks),
or add a clear allowlist/flag to suppress missing warnings for these types.

## Evidence
- `[[PROB-002]]` exists at
  `backlog/problems/PROB-002-requirement_lifecycle_guidance_drift/PROB-002.md` but
  remains unresolved after `resolve links`.

## Related
- PROB-002 (requirement lifecycle guidance drift)
