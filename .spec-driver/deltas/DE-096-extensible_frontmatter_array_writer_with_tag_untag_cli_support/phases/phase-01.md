---
id: IP-096-P01
name: Writer infrastructure
kind: phase
status: pending
delta: DE-096
plan: IP-096
created: "2026-03-14"
updated: "2026-03-14"
---

# Phase 1 – Writer Infrastructure

## Entrance Criteria

- [x] Delta DE-096 scoped
- [x] DR-096 drafted

## Tasks

### 1. Core writer functions

- [ ] `ListUpdateResult` dataclass
- [ ] `add_frontmatter_list_items(path, field, items, *, sort=True)` — add items, create field if absent, dedup, bump updated
- [ ] `remove_frontmatter_list_items(path, field, items)` — remove items, bump updated
- [ ] Internal helpers: parse flow-style `[a, b]`, parse block-style `- a`, detect format, emit in matching format

### 2. Tests

- [ ] Flow-style: add to existing, add duplicates (dedup), remove, remove last item → `[]`
- [ ] Block-style: add to existing, remove
- [ ] Absent field: add creates flow-style
- [ ] Sort behaviour (default on, explicit off)
- [ ] Body content preservation
- [ ] Idempotent add (already present)
- [ ] Remove non-existent item (no-op)
- [ ] `updated:` date bumped
- [ ] Error cases: missing file

### 3. Lint

- [ ] `pylint` clean on touched files

## Exit Criteria

- [ ] All writer tests green
- [ ] Existing `frontmatter_writer_test.py` tests unaffected
- [ ] Lint clean
