---
id: IP-096-P02
name: CLI wiring
kind: phase
status: pending
delta: DE-096
plan: IP-096
created: "2026-03-14"
updated: "2026-03-14"
---

# Phase 2 – CLI Wiring

## Entrance Criteria

- [ ] Phase 1 complete (writer tests green)

## Tasks

### 1. Shared options and helper

- [ ] `TagOption` and `UntagOption` annotated types in `edit.py`
- [ ] `_apply_tags(artifact_id, path, tags, untags)` shared helper

### 2. Wire to edit commands

- [ ] Add `--tag`/`--untag` to: spec, delta, requirement, revision, audit, adr, policy, standard, issue, problem, improvement, risk, memory, card
- [ ] Each command: when tag/untag provided, apply and skip editor (same as --status)

### 3. Tests

- [ ] Edit with --tag adds tag
- [ ] Edit with --untag removes tag
- [ ] Edit with --tag + --untag (combined)
- [ ] Edit with --tag on artifact without existing tags
- [ ] Existing edit tests unaffected

### 4. Lint

- [ ] `pylint` clean

## Exit Criteria

- [ ] All edit commands support --tag/--untag
- [ ] Tests green
- [ ] Lint clean
