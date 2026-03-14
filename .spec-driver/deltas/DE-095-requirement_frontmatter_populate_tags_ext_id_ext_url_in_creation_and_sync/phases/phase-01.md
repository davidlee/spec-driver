---
id: IP-095-P01
name: Creation + Sync + Tests
kind: phase
status: complete
delta: DE-095
plan: IP-095
created: "2026-03-14"
updated: "2026-03-14"
---

# Phase 1 – Creation + Sync + Tests

## Entrance Criteria

- [x] Delta DE-095 scoped and accepted
- [x] DR-095 drafted

## Tasks

### 1. Creation pipeline – add params

- [x] `supekku/scripts/lib/changes/creation.py`: Added `tags`, `ext_id`, `ext_url` params to `create_requirement_breakout()`; emits non-empty values in frontmatter
- [x] `supekku/scripts/create_requirement.py`: Added `--tags`, `--ext-id`, `--ext-url` to argparser
- [x] `supekku/cli/create.py`: Added `--tag` (repeatable), `--ext-id`, `--ext-url` to typer CLI; passes through to creation function
- [x] Unit test: creation with all three params → verified frontmatter content
- [x] Unit test: creation without params → verified fields absent from frontmatter

### 2. Sync pipeline – read from frontmatter

- [x] `supekku/scripts/lib/requirements/registry.py`: Added `_load_breakout_metadata()` to scan breakout requirement files; applied in both `_records_from_frontmatter()` and the fallback `spec_dirs` path
- [x] Tag merge: frontmatter tags ∪ inline tags → sorted list
- [x] Unit test: breakout file with frontmatter tags/ext_id/ext_url → synced record has them
- [x] Unit test: inline tags + frontmatter tags → union
- [x] Unit test: no frontmatter fields → defaults (empty)
- [x] Unit test: breakout enrichment via spec_registry path
- [x] Unit test: breakout tags only (no ext fields)

### 3. Verification

- [x] All existing tests green (132 total)
- [x] Lint clean (no new errors/warnings)
- [x] 47 CLI requirement-related tests pass

## Exit Criteria

- [x] All tasks complete
- [x] No regressions
