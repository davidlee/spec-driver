# Notes for DE-125

## 2026-03-23

- Reconciled `DE-125`, `DR-125`, and `IP-125` with current repo reality.
- Replaced the stale "create `spec_driver/` and add import-linter" narrative with
  the narrower thesis that actually matters now: domain-internal dependency
  direction.
- Added `phases/phase-01.md` so the delta has a real active phase instead of an
  orphan plan entry.
- Identified the main architectural seam: registries should be local authorities,
  while cross-artifact traversal belongs in `relations` or orchestration.
- Chose first migration pilots from the current graph:
  `supekku/scripts/lib/relations/query.py` and
  `supekku/scripts/lib/relations/manager.py`.
- Chose the first governance seam to extract before any registry move:
  policy backlink computation currently embedded in `PolicyRegistry`.
- Explicitly deferred `requirements.registry`, `policies.registry`, and
  `validation.validator` as too coupled for first-wave migration.
- Created `phases/phase-02.md` for verification and seam extraction.
- Ran `spec-driver validate` after the doc updates. Current output is back to the
  repo's pre-existing warning baseline; no new DE-125-specific validation issues
  remain.
- Work remains uncommitted.
