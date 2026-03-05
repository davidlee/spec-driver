---
id: ISSUE-035
name: Memory CLI UX improvements
created: '2026-03-05'
updated: '2026-03-05'
status: open
kind: issue
---

# Memory CLI UX improvements

## Summary
Memory command ergonomics make it harder than necessary to find, verify, and
navigate memories. Add scoped link resolution, verbose reporting, and optional
content-type output to preserve context.

## Proposed Improvements
- `resolve links --verbose`: print missing targets and the files containing them.
- `resolve links --path <file>|--id <mem-id>`: scoped resolution for faster iteration.
- `list memories --links-to <id>`: backlinks / reverse edges for graph traversal.
- `show memory --links-depth N`: lightweight link graph expansion.
- Extend resolver to backlog items (ISSUE/PROB/IMPR/RISK) or add
  `--allow-unresolved` patterns to suppress known types.
- Add `--content-type/-c` to retrieval commands (e.g., `show memory`) with
  `markdown|frontmatter|yaml` to preserve context while trimming noise.

## Impact
- Faster onboarding and lower friction when exploring memory graph.
- Reduced noise in link resolution and clearer missing-target debugging.

## Notes
- `show memory --raw` already exists; `--content-type` could standardize this
  across artifact types and serve as a short-hand.
- ADR-002 prohibits storing backlinks in frontmatter — `--links-to` must use
  runtime computation from forward references. Registry caching is permitted.
- Default `show memory` already excludes body (metadata-only). The missing
  inverse is `--body-only/-b` (body without frontmatter) for agents that
  already have metadata and just want content.
- The `--truncate` flag on `list memories` renders the table nearly unreadable —
  the Status column includes the file path (`active[/memory....`). Worth
  investigating separately.
- Current corpus is ~35 memories with ~100 resolved links; `core-loop` is the
  most connected node (12 inbound links). Performance of runtime backlink
  computation is not a concern at this scale.

## Deltas
- DE-045: `--links-to`, `--links-depth N`, `--body-only` (agent discoverability)
- Remaining: `resolve links --verbose`, `--path/--id` scoped resolution,
  backlog item resolution (see also ISSUE-034)

## Related
- ISSUE-034 (resolve links does not support backlog items)
- ISSUE-036 (standardize show output selectors)
- ADR-002 (do not store backlinks in frontmatter)
