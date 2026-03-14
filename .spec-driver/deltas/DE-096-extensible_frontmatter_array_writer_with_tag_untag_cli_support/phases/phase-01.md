---
id: IP-096-P01
name: CompactDumper + writer + dump_markdown_file
kind: phase
status: complete
delta: DE-096
plan: IP-096
created: '2026-03-14'
updated: '2026-03-14'
---

# Phase 1 – CompactDumper + Writer + dump_markdown_file

## Entrance Criteria
- [x] DR-096 approved

## Tasks

### 1. CompactDumper
- [ ] `CompactDumper` class in `frontmatter_writer.py`
- [ ] Flow-style for short scalar lists (< 80 chars total), block otherwise
- [ ] `dump_frontmatter(data) -> str` function using CompactDumper with canonical settings
- [ ] Tests: idempotency, flow/block heuristic, unicode, empty lists, date quoting

### 2. update_frontmatter core primitive
- [ ] `update_frontmatter(path, mutator)` — load, mutate, bump updated, write
- [ ] Body content preserved exactly
- [ ] Tests: mutation, updated-date bump, body preservation, error cases

### 3. List operation convenience functions
- [ ] `ListUpdateResult` dataclass
- [ ] `add_frontmatter_list_items(path, field, items, *, sort=True)`
- [ ] `remove_frontmatter_list_items(path, field, items)`
- [ ] Tests: add, remove, dedup, sort, create-when-absent, empty-after-remove, idempotent

### 4. Reimplement existing functions
- [ ] `update_frontmatter_status` as thin wrapper around `update_frontmatter`
- [ ] `update_frontmatter_fields` as thin wrapper around `update_frontmatter`
- [ ] Existing tests still pass

### 5. dump_markdown_file alignment
- [ ] Switch `spec_utils.py:dump_markdown_file` to use `dump_frontmatter`
- [ ] Existing creation tests still pass

### 6. Lint
- [ ] pylint clean on touched files

## Exit Criteria
- [ ] All new + existing writer tests green
- [ ] Full test suite green
- [ ] Lint clean
