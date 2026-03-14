---
id: ISSUE-051
name: sync does not prune stale requirements from registry
created: "2026-03-10"
updated: "2026-03-10"
status: open
kind: issue
categories: []
severity: p2
impact: user
---

# sync does not prune stale requirements from registry

## Observed

`spec-driver sync` (including `--force`) does not remove entries from
`.spec-driver/registry/requirements.yaml` when the corresponding requirement
is deleted from spec markdown.

Orphaned requirements persist silently, polluting coverage checks and
verification gates.

## Expected

Sync should detect requirements present in the registry but absent from their
owning spec and either prune them automatically or surface them as warnings.

## Workaround

Manually delete the stale entry from `requirements.yaml`.

## Provenance

Observed in [davidlee/ligma](https://github.com/davidlee/ligma) during DE-001
(SPEC-001.NF-005 persisted after removal from spec).
