---
id: IP-096-P02
name: CLI wiring
kind: phase
status: complete
delta: DE-096
plan: IP-096
created: "2026-03-14"
updated: "2026-03-14"
---

# Phase 2 – CLI Wiring

## Tasks — all complete

- [x] `TagOption` and `UntagOption` annotated types
- [x] `_apply_tags(artifact_id, path, tags, untags)` shared helper (with `Path` coercion)
- [x] `--tag`/`--untag` on all 17 edit subcommands: spec, delta, requirement, revision, audit, adr, policy, standard, issue, problem, improvement, risk, memory, card, plan, backlog, drift
- [x] Each command: when tag/untag provided, apply and skip editor
- [x] Smoke tested on real artifact (POL-001)
- [x] All 4040 tests pass
- [x] pylint 10.00/10
