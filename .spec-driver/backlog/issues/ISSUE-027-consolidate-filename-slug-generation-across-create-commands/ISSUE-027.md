---
id: ISSUE-027
name: 'Consolidate filename slug generation across create commands'
created: '2026-02-06'
updated: '2026-02-06'
status: done
kind: issue
categories:
  - cli
  - core
severity: p4
impact: developer
---

# Consolidate filename slug generation across create commands

## Problem

Multiple `create` commands generate file paths from titles (ADR, issue, improvement, problem, etc.) but may use inconsistent slug logic.

## Expected

- Single code path for title → filename slug conversion
- Normalize special characters: `:-+_` etc. should collapse to single `_`
- Deduplicate consecutive separators
- Consistent behavior across all create commands

## Examples

| Input | Expected slug |
|-------|---------------|
| `ADR-001: use spec-driver` | `adr_001_use_spec_driver` |
| `Fix bug -- urgent` | `fix_bug_urgent` |
| `foo___bar` | `foo_bar` |
| `title: with: colons` | `title_with_colons` |

## Acceptance Criteria

- [x] Single `slugify()` in `core/strings.py`
- [x] All create commands use shared function
- [x] Special chars `:-+_` normalized to `_` (underscores)
- [x] Consecutive separators deduplicated
- [x] Existing paths not broken (new behavior only)

## References

- `supekku/scripts/lib/decisions/creation.py`
- `supekku/scripts/backlog/`
