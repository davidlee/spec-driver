# DE-095 Implementation Notes

## 2026-03-14 – Phase 1 Complete

### Changes Made

**Creation pipeline** (`supekku/scripts/lib/changes/creation.py`):

- Added `tags: list[str] | None`, `ext_id: str | None`, `ext_url: str | None` keyword params to `create_requirement_breakout()`
- Frontmatter dict emits `tags` (sorted), `ext_id`, `ext_url` only when non-empty
- Two CLI surfaces updated:
  - `supekku/cli/create.py` (typer): `--tag` (repeatable via `list[str]`), `--ext-id`, `--ext-url`
  - `supekku/scripts/create_requirement.py` (argparse): `--tags` (comma-separated), `--ext-id`, `--ext-url`

**Sync pipeline** (`supekku/scripts/lib/requirements/registry.py`):

- New static method `_load_breakout_metadata(spec_path)` scans `spec_path.parent/requirements/*.md` for frontmatter `tags`/`ext_id`/`ext_url`
- Called in both sync paths:
  - `_records_from_frontmatter()` (spec_registry path) — enriches yielded records
  - Fallback `spec_dirs` iteration — enriches records before upsert
- Tag merge: frontmatter tags ∪ inline `[tag]` tags → `sorted(set(...))`

### Design Decisions

- Tags use sorted set union matching `RequirementRecord.merge()` semantics
- Breakout files that don't exist or lack these fields have no effect (all optional)
- `_load_breakout_metadata` is `@staticmethod` — pure function, no registry state dependency

### Test Coverage

- 2 new creation tests (with/without params)
- 5 new sync tests (merge, ext_id+url, no-op, tags-only, spec_registry path)
- All 132 existing tests pass, 47 CLI requirement tests pass
