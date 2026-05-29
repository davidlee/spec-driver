---
id: ISSUE-064
name: "DE-140 spec-requirements migrator: false-positive unparseable heuristic + requirement description/acceptance backfill debt"
created: "2026-05-30"
updated: "2026-05-30"
status: open  # one of: in-progress | open | resolved | triaged
kind: issue  # one of: audit | delta | design_revision | issue | memory | phase | plan | policy | problem | prod | requirement | risk | spec | standard | task | verification
categories: []
severity: p3  # one of: p1 | p2 | p3 | p4
impact: user  # one of: user | systemic | process
---

# DE-140 spec-requirements migrator: false-positive unparseable heuristic + requirement description/acceptance backfill debt

Captured at DE-136 Phase 4 umbrella close as the durable residue of the
DL-049..074 disposition (option A: tolerated_drift + one backlog issue).
See `VA-DE136-CLOSE-001` and IP-136 §4 Phase 4.

## Origin

`spec_driver/migrations/spec_requirements/migration.py` (DE-140) produced 26
drift ledgers (DL-049..074, 1298 entries) when migrating prose requirement
bullets into `supekku:spec.requirements@v1` blocks. The entries were disposed
at DE-136 close (DL ledgers set `status: closed`, entries dismissed/deferred).
This issue tracks the two underlying defects so they are not lost.

## 1. False-positive `requirement_unparseable` heuristic (776 entries — dismissed)

`_detect_drift` flags any line matching a requirement-id shape that it cannot
parse as a full requirement definition. It fired on **coverage- and
relationships-block reference lines** — e.g. `- PROD-004.FR-001` and
`requirement: PROD-004.FR-001` — which are legitimate references, not
requirement definitions. 776 of the 1298 entries are this false positive.

**Fix**: scope the unparseable heuristic to the prose-requirements region
only (exclude `supekku:*` fenced blocks and coverage/relationship reference
lines). Add a regression test over a spec carrying coverage + relationships
blocks asserting zero `requirement_unparseable` drift.

## 2. Requirement description/acceptance backfill debt (522 entries — deferred)

261 `description_placeholder` + 261 `acceptance_placeholder` entries record
that migrated requirements carry meaningful `title`s but empty `description:
""` and `acceptance_criteria: []`. This is real but minor content debt,
re-derivable on demand, and outside DE-136's schema-consolidation scope.
Title-only requirements are the prevailing style across these PROD/SPEC
blocks. Backfill opportunistically when each owning spec is next revised; not
worth a dedicated sweep.

## 3. Drift-ledger `detail:` emitter malformed-YAML bug (FIXED)

The ledger writer emitted `detail: <raw>` unquoted, so any detail containing
`': '` produced malformed YAML that broke `list drift` parsing. **Fixed in
DE-136 Phase 4** — `write_drift_ledger` now serialises each entry via
`yaml.safe_dump`; regression test
`migration_test.py::TestDriftLedger::test_entry_blocks_are_valid_yaml`.
The 26 existing ledgers were repaired in place during disposition.

## 4. Non-canonical ledger entry shape (note)

The migrator wrote an ad-hoc entry shape (`target/drift_kind/detail/
disposition/owner/status`) that does not match the canonical drift model
(`supekku/scripts/lib/drift/models.py`: `ENTRY_TYPES`, `ENTRY_STATUSES`,
`Source/Claim/DiscoveredBy`). Any future migrator-emitted drift should use the
canonical model so `list drift` and the registry can read it. Fold into the
fix for §1.
