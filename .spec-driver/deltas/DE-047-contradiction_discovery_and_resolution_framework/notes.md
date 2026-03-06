# Notes for DE-047

## 2026-03-06 — Workflow/guidance cleanup folded into Phase 2

- Drafted `ADR-004` (`specify/decisions/ADR-004-canonical_workflow_loop.md`)
  to resolve DL-047.021 and establish canonical workflow doctrine.
- Drafted `ADR-005`
  (`specify/decisions/ADR-005-memories_and_skills_are_the_canonical_guidance_layer.md`)
  as a prelude/companion decision defining memories + skills as the canonical
  guidance layer.
- Intersects Phase 2 task `2.3a` directly: core loop ADR now exists in draft.

## 2026-03-06 — `.spec-driver/about/` and `docs/` cleanup

- Reworked `.spec-driver/about/README.md` into a router and added
  `.spec-driver/README.md` as the lightweight installed entrypoint.
- Ported surviving guidance from `supekku/about/glossary.md`,
  `supekku/about/processes.md`, `supekku/about/backlog.md`, and deleted those
  docs.
- Deleted the stale `docs/` working-paper set after porting the useful bits
  into memories and active guidance.
- Updated multiple spec-driver memories to:
  - remove dependence on deleted docs
  - align with ADR-004/ADR-005
  - fix stale command/status details uncovered during the cleanup
- Intersects Phase 2 task `2.10` directly. The planned "patch
  doctrine/workflow/glossary" work broadened into a guidance-layer cleanup once
  ADR-005 made the target architecture explicit.

## 2026-03-06 — INIT removal / DL-047.006

- Removed `@supekku/INIT.md` from the live bootstrap path (`AGENTS.md`;
  `CLAUDE.md` is a symlink).
- Deleted `supekku/INIT.md`.
- Updated `PROD-001` to remove obsolete INIT-based onboarding assumptions.
- Updated `drift/DL-047-spec-corpus-reconciliation.md` entry `.006` to record
  that the removal is now implemented, not merely adjudicated.
- This partly intersects planned task `2.11` ("Create backlog items"). For
  `.006`, backlog capture became unnecessary because the remediation was small
  enough to land directly inside DE-047.

## Adaptations / follow-up implications

- The original plan assumed `.006` and `.019` would likely become backlog work.
  In practice:
  - `.006` was resolved directly in DE-047.
  - `.019` was partly resolved by deleting duplicate glossary/process docs and
    rerouting guidance to memories, but broader public-doc consolidation still
    remains.
- Remaining likely follow-up areas after this pass:
  - public/top-level docs (`README`, `wub`)
  - any explicit REs needed to align affected PRODs to ADR-004/ADR-005
  - residual historical references to deleted docs in specs/deltas/backlog notes

## Verification

- `just check` has now been run successfully after the documentation/governance edits.
- Current workspace still contains uncommitted documentation/governance changes.

## Handover Context

- `CLAUDE.md` is a symlink to `AGENTS.md`; removing `@supekku/INIT.md` from
  `AGENTS.md` removed the live reference from both.
- `docs/` was not install-managed/user-facing. Cleanup strategy was to port any
  durable value into memories, then delete the stale working-paper docs.
- The deleted `docs/` set also surfaced stale memory guidance; several
  spec-driver memories were corrected as part of that cleanup. Most important:
  `mem.concept.spec-driver.relations` no longer claims the requirements
  registry is the source of truth.
- The only remaining deleted-`docs/` reference observed in generated state was
  `.spec-driver/registry/deltas.yaml`; it is derived and should disappear on
  the next registry refresh/sync.
- `DL-047.006` is now implemented, not merely adjudicated:
  `INIT.md` removed, live bootstrap updated, `PROD-001` patched, and the drift
  ledger updated accordingly.
- Historical references to deleted docs / `INIT.md` still exist in older
  deltas, audits, backlog research, and some specs. They are not part of the
  live guidance path but remain future cleanup candidates.
- `IP-047.md` still contains duplicate `IP-047.PHASE-02` entries in the plan
  overview block; not changed in this session, but worth cleaning before anyone
  relies on that plan mechanically.
