---
id: ISSUE-061
slug: admin_migrate_orchestrator_does_not_materialize_stepresult_drift_entries_to_dl_files
name: admin migrate orchestrator does not materialize StepResult.drift_entries to DL files
created: "2026-05-29"
updated: "2026-05-29"
status: open  # one of: in-progress | open | resolved | triaged
kind: issue  # one of: audit | delta | design_revision | issue | memory | phase | plan | policy | problem | prod | requirement | risk | spec | standard | task | verification
categories: []
severity: p3  # one of: p1 | p2 | p3 | p4
impact: user  # one of: user | systemic | process
---

# admin migrate orchestrator does not materialize StepResult.drift_entries to DL files

## Problem

The generic `admin migrate` orchestrator (`spec_driver/presentation/cli/admin/migrate.py`)
captures `StepResult.drift_entries: list[Path]` from each migration step but never
writes the corresponding `DL-*.md` drift ledger files. It only emits a per-run log
(`_write_log`, listing touched/skipped files) and ignores `drift_entries`.

The only DL-writing path is **bespoke** to the interactive spec-migration command:
`write_drift_ledger()` / `_next_drift_id()` in
`spec_driver/migrations/spec_requirements/migration.py`, called exclusively by
`cli/admin/migrate_requirements.py`. Batch-orchestrated steps (`v0_10_0_001..005`)
have no way to emit drift ledgers through the generic orchestrator.

## Impact

Any forward-only migration step run via `admin migrate <kind>` that detects genuine
spec-vs-reality divergence can populate `StepResult.drift_entries`, but those entries
are silently dropped — no DL file is written, so the divergence is lost. The drift
mechanism is architecturally incomplete for the generic path.

## Surfaced by

DE-142 P04 consult (2026-05-29). DE-142's own migration does **not** need this
(broadened ID patterns + faithful `modify`-synthesis are lossless → zero synthesis
drift; any residual is dispositioned manually). So building the mechanism inside
DE-142 would be speculative. Filed here instead.

## Fix sketch

Hoist `write_drift_ledger` + `_next_drift_id` into a shared `migrations/_drift.py`
helper that any step can call in `apply()` (migration→migration import, respects the
DR-136 §11.1 boundary), **or** have the orchestrator materialize `StepResult.drift_entries`
after each step. Coordinate with ISSUE-059 (`write_drift_ledger` emits invalid YAML
when detail values contain colons) — fix both when this is picked up.

## Related

- ISSUE-059 — `write_drift_ledger` invalid-YAML-on-colon bug (same helper)
- DR-136 §11.1 (migration boundary), §11.4 (`migrations/` layout)
- DE-142 DR-142 §8 (synthesis), notes.md session 6 (DEC-CONSULT-05)

