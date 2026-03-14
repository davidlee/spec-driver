---
id: ISSUE-048
name: Factor list.py into domain-specific submodules
created: "2026-03-10"
updated: "2026-03-10"
status: open
kind: issue
categories: []
severity: p3
impact: user
---

# Factor list.py into domain-specific submodules

## Context

`supekku/cli/list.py` is 2750+ lines with 95 pre-existing pylint warnings. It handles listing for every artifact type in a single file.

## Suggested approach

Factor into domain-specific list modules (e.g. `list_memories.py`, `list_specs.py`, `list_deltas.py`, etc.) while keeping the main `list.py` as a thin router that registers subcommands.

## Origin

Noted during DE-086 Phase 02 implementation. Deferred to avoid scope creep.
