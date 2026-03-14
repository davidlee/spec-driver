---
id: IP-095-P01
name: Creation + Sync + Tests
kind: phase
status: pending
delta: DE-095
plan: IP-095
created: '2026-03-14'
updated: '2026-03-14'
---

# Phase 1 – Creation + Sync + Tests

## Entrance Criteria
- [x] Delta DE-095 scoped and accepted
- [x] DR-095 drafted

## Tasks

### 1. Creation pipeline – add params
- [ ] `supekku/scripts/lib/changes/creation.py`: Add `tags: list[str] | None`, `ext_id: str | None`, `ext_url: str | None` params to `create_requirement_breakout()`; emit non-empty values in frontmatter dict
- [ ] `supekku/scripts/create_requirement.py`: Add `--tags`, `--ext-id`, `--ext-url` to argparser
- [ ] `supekku/cli/create.py`: Pass new args through to `create_requirement_breakout()`
- [ ] Unit test: creation with all three params → verify frontmatter content
- [ ] Unit test: creation without params → verify fields absent from frontmatter

### 2. Sync pipeline – read from frontmatter
- [ ] `supekku/scripts/lib/requirements/registry.py`: In `_records_from_content()` or `_records_from_frontmatter()`, read `tags`/`ext_id`/`ext_url` from frontmatter and apply to yielded `RequirementRecord`
- [ ] Tag merge: frontmatter tags ∪ inline tags → sorted list
- [ ] Unit test: breakout file with frontmatter tags/ext_id/ext_url → synced record has them
- [ ] Unit test: inline tags + frontmatter tags → union
- [ ] Unit test: no frontmatter fields → defaults (empty)

### 3. Verification
- [ ] All existing tests green
- [ ] Lint clean (`just check`)
- [ ] Manual smoke: create requirement with --tags, sync, list → fields visible

## Exit Criteria
- [ ] All tasks complete
- [ ] `just check` passes
- [ ] No regressions in existing requirement tests
