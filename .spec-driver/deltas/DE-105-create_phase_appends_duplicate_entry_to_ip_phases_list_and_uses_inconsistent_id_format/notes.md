# Notes for DE-105

- Reconciled the generated DE/DR/IP scaffolding with ISSUE-052 and added
  `phases/phase-01.md` as the active execution sheet.
- Updated `supekku/scripts/lib/changes/creation.py` so `create_phase()` now:
  - parses both `IP-###-P##` and `IP-###.PHASE-##`
  - prefers the first planned-but-not-yet-materialized phase from the owning
    plan
  - preserves the plan's established ID spelling
  - treats equivalent phase IDs as the same logical phase during metadata lookup
    and plan-overview updates
- Updated `supekku/scripts/lib/changes/creation_test.py` to align default
  expectations with the plan scaffold's hyphenated IDs and added a regression
  for hand-authored hyphenated phase lists.
- Verification since last code change:
  - `uv run pytest supekku/scripts/lib/changes/creation_test.py` ✓
  - `uv run ruff check supekku/scripts/lib/changes/creation.py supekku/scripts/lib/changes/creation_test.py` ✓
- Outstanding:
  - the broader codebase still contains dotted-ID assumptions in unrelated
    workflow/display paths; this delta deliberately did not normalize those
  - worktree changes remain uncommitted
