---
id: IP-116-P04
slug: "116-registry_protocol_enforcement_and_governance_triplet_consolidation_adr_009-phase-04"
name: IP-116 Phase 3 — Creation impl-only unification
created: "2026-06-02"
updated: "2026-06-02"
status: in-progress
kind: phase
plan: IP-116
delta: DE-116
---

# Phase 3 — Creation impl-only unification

## 1. Objective

Extract the ~80% duplicated creation bodies into one shared private
`_create_governance_artifact` engine. Keep the public `create_X` /
`*Options` / `*Result` / `*AlreadyExistsError` symbols as thin typed
wrappers with exact error messages preserved. `cli/create.py` unchanged.
Isolated phase — a creation regression cannot block the already-landed R work
(ER-5/ER-7).

## 2. Links & References

- **Delta**: DE-116 §3 (P3), §5 (creation unification).
- **Design Revision**: DR-116 §4 (creation unification sketch, DEC-116-6), §4 code-impact table.
- **Governance**: ER-5 (impl-only), OQ-2 (record_artifact on STD — resolved: accept).
- **Predecessor**: P2 (`phase-03.md`) — R landed.

## 3. Entrance Criteria

- [x] P2 committed green — R landed (registries + base + backlinks).
- [x] OQ-2 resolved: add `record_artifact()` to Standard creation (telemetry-only, corrects inconsistency).
- [x] Current creation modules read and diffed — differences catalogued.

## 4. Exit Criteria / Done When

- [ ] One shared private `_create_governance_artifact(spec, registry, options, *, sync_registry)`
      engine lives in `supekku/scripts/lib/creation.py` (private module). Handles: next-id,
      slug+filename, exists-check, frontmatter, template render, file write, sync.
- [ ] `create_adr` / `create_policy` / `create_standard` are thin wrappers (~15 lines each)
      that delegate to the shared engine. Per-type `*Options` / `*Result` / `*AlreadyExistsError`
      kept verbatim in current modules.
- [ ] `record_artifact()` called unconditionally for all three (Standard was missing it — OQ-2).
- [ ] CLI error messages byte-identical: `"ADR file already exists: ..."`, `"Policy file already exists: ..."`, `"Standard file already exists: ..."`.
- [ ] `cli/create.py` unchanged (public surface preserved).
- [ ] Existing creation tests (if any) pass; no regression.

## 5. Verification

- **Smoke test**: import `create_adr` / `create_policy` / `create_standard` and call with options → file created, result returned.
- **Error message test**: creating duplicate ADR/Policy/Standard raises correct exception with exact message.
- **result field test**: `.adr_id` / `.policy_id` / `.standard_id` accessible on results.
- **`record_artifact` test**: Standard creation now calls `record_artifact` (previously missing).

## 6. Assumptions & STOP Conditions

- **Assumptions**:
  - `build_X_frontmatter` functions are part of the per-type surface (different field sets) —
    kept as-is, called from the shared engine via a callable in the spec.
  - `generate_next_X_id` helpers are thin wrappers around `next_sequential_id` — folded into
    the shared engine.
- **STOP when**:
  - Error message text changes even by one character → the public surface contract is broken.
  - Existing creation tests fail.

## 7. Tasks & Progress

| Status | ID  | Description | Notes |
| --- | --- | --- | --- |
| [ ]    | 3.1 | Create `_GovernanceArtifactSpec` dataclass + `_AlreadyExists` exception | private, in new `supekku/scripts/lib/creation.py` |
| [ ]    | 3.2 | Create `_create_governance_artifact` private engine | handles full creation flow |
| [ ]    | 3.3 | Refactor `create_adr` to thin wrapper | delegate to engine; preserve ADRCreationOptions/Result/Error |
| [ ]    | 3.4 | Refactor `create_policy` to thin wrapper | same pattern |
| [ ]    | 3.5 | Refactor `create_standard` to thin wrapper | add record_artifact (OQ-2) |
| [ ]    | 3.6 | Verify error messages byte-identical + import surface + tests | smoke |

## 8. Wrap-up Checklist

- [ ] Exit criteria satisfied
- [ ] IP-116 progress updated (P3 ticked)
