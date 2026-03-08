---
id: IMPR-012
name: 'Registries check: detect silent ID deduplication from filesystem-level collisions'
created: '2026-03-08'
updated: '2026-03-08'
status: idea
kind: improvement
---

# Registries check: detect silent ID deduplication from filesystem-level collisions

## Context

Registry `.collect()` returns `dict[str, T]`, keyed by artifact ID. If two
filesystem entries parse to the same ID (e.g. two directories both yielding
`DE-042`), the dict silently overwrites one — no error, no warning.

## Proposed Behaviour

The `registries` doctor check (DE-064) should scan the filesystem independently
of `.collect()` to detect when multiple source paths would produce the same
artifact ID. Report as `fail` with both paths so the user can resolve.

## Origin

Discovered during DE-064 Phase 2 preflight. Explicitly deferred from Phase 2
scope to keep the registries check focused on load-without-error and basic
integrity.

