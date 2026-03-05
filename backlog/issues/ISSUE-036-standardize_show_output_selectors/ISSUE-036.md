---
id: ISSUE-036
name: Standardize show output selectors
created: '2026-03-05'
updated: '2026-03-05'
status: open
kind: issue
---

# Standardize show output selectors

## Summary
Introduce a consistent `--content-type/-c` selector for `spec-driver show` (and
possibly `view`) so callers can request `markdown`, `frontmatter`, or `yaml`
outputs without bespoke flags like `--raw`.

## Proposed Behavior
- `spec-driver show <artifact> --content-type markdown` → body only
- `spec-driver show <artifact> --content-type frontmatter` → frontmatter only
- `spec-driver show <artifact> --content-type yaml` → raw YAML (if applicable)
- Preserve existing `--raw` as a synonym or soft-deprecate in docs

## Rationale
- Reduces cognitive load across artifact types
- Preserves context in automation and agent workflows
- Consistent selector can be reused by other commands later

## Notes
- Validate no conflict with existing `-c` flags on `show` subcommands.

## Acceptance Notes
- At least one `show` subcommand implements `--content-type/-c` with
  `markdown|frontmatter|yaml` values.
- `--raw` remains supported or explicitly documented as deprecated with a
  migration note.
- CLI help shows the new selector and example usage.

## Related
- ISSUE-035 (memory CLI UX improvements)
