---
id: DL-048
name: DE-138 sweep FM/block reconciliation
created: '2026-05-20'
updated: '2026-05-20'
status: open
kind: drift_ledger
delta_ref: DE-138
---

# DL-048 — DE-138 sweep FM/block reconciliation

Tracks FM ↔ `supekku:delta.relationships@v1` block mismatches surfaced by the
DE-138 P03 sweep (`v0_10_0_001_delta_blocks`). Each entry is a deferred
reconciliation: the migration step preserved the block as canonical and cut
the FM key per DEC-138-11; this ledger records the unmatched FM entries so
they can be reviewed against the block-shape source of truth, repaired into
the block, or accepted as legitimate FM-only references that the block
shape never represented.

Sweep commit anchor: `2afc0833` (post `de-138-pre-sweep` tag at `46976634`).

## Entries

### DL-048.001: DE-016 FM spec PROD-011 absent from relationships block

```yaml
target: DE-016
drift_kind: fm_specs_unmatched
observed:
  fm_applies_to_specs: [PROD-011]
  block_specs_primary: []  # block enumerates SPEC-* targets only
  block_specs_collaborators: []
analysis: |
  DE-016 predates DR-138; its FM applies_to.specs named the parent PROD
  but the supekku:delta.relationships@v1 block (added later by another
  delta) only carried SPEC-* targets. After the sweep, derived
  applies_to.specs no longer surfaces PROD-011 for DE-016, which
  understates the delta's PROD-level scope to readers of `list deltas`.
disposition: needs_block_amend
recommendation: |
  Add PROD-011 to specs.collaborators in DE-016's relationships block
  (preserves block as canonical; restores PROD-level visibility).
  Out of scope for DE-138 (would require auditing DE-016's actual PROD
  alignment); track here for follow-up.
owner: unassigned
status: open
```

### DL-048.002: DE-020 FM specs PROD-010 SPEC-110 SPEC-113 + requirement ISSUE-025 absent from block

```yaml
target: DE-020
drift_kinds: [fm_specs_unmatched, fm_requirements_unmatched]
observed:
  fm_applies_to_specs: [PROD-010, SPEC-110, SPEC-113]
  fm_applies_to_requirements: [ISSUE-025]
  block_specs_primary: []
  block_specs_collaborators: []
  block_requirements_implements: []
analysis: |
  DE-020's FM carried both an old PROD/SPEC reference set and an
  ISSUE-* in applies_to.requirements (ISSUE-025 is a backlog issue, not
  a spec requirement — its placement in FM applies_to.requirements is
  a legacy authoring convention pre-dating ADR-002). The relationships
  block was sparse. Post-sweep applies_to is empty.
disposition: needs_block_amend
recommendation: |
  - Add PROD-010, SPEC-110, SPEC-113 to specs.collaborators if alignment
    survives review; otherwise mark as historical and accept loss of
    derived linkage.
  - ISSUE-025 belongs in `relations[]` (relates_to/satisfies) per
    ADR-002, not in applies_to.requirements; rehome accordingly.
owner: unassigned
status: open
```

### DL-048.004: Body section 7 risk narrative recovery anchor (137 deltas)

```yaml
target: '*'  # 137 swept deltas, full list in p03-risk-recon-log.md §2.1
drift_kind: body_risk_narrative
disposition: file_dl
recovery_anchor: de-138-pre-sweep  # commit 46976634
analysis: |
  VA-DE138-RISK-RECON-001 disposed all 137 body_risk_narrative drift
  entries as `file_dl` against the pre-sweep tag. Each delta's
  pre-sweep §7 prose is recoverable verbatim via
  `git show de-138-pre-sweep:<delta-path>`. Selective promotion into
  `risk_register@v1` blocks is deferred to the cleanup delta
  (DR-138 §15.1) for the 22 active deltas where in-flight signal is
  load-bearing.
recommendation: |
  Retain pre-sweep tag until the cleanup delta closes. Cleanup-delta
  scope = survey the 22 active deltas (in-progress + draft) and
  promote body-prose risks where the signal is load-bearing.
owner: unassigned
status: open
```

### DL-048.003: DE-106 FM specs PROD-006 PROD-011 + 5 PROD-006 requirements absent from block

```yaml
target: DE-106
drift_kinds: [fm_specs_unmatched, fm_requirements_unmatched]
observed:
  fm_applies_to_specs: [PROD-006, PROD-011]
  fm_applies_to_requirements:
    [PROD-006.FR-001, PROD-006.FR-003, PROD-006.FR-004, PROD-006.FR-005, PROD-006.NF-002]
  block_specs_primary: []
  block_specs_collaborators: []
  block_requirements_implements: []
analysis: |
  DE-106's FM carried a full PROD-006 alignment surface (2 specs, 5
  requirements) but the relationships block was empty. Post-sweep
  applies_to is empty, which orphans DE-106 from coverage queries
  against PROD-006.
disposition: needs_block_amend
recommendation: |
  Populate DE-106's supekku:delta.relationships@v1 block:
    specs.primary: [PROD-006]
    specs.collaborators: [PROD-011]
    requirements.implements: [PROD-006.FR-001, PROD-006.FR-003,
      PROD-006.FR-004, PROD-006.FR-005]
    requirements.verifies: [PROD-006.NF-002]
  Verify against PROD-006 coverage block before committing.
owner: unassigned
status: open
```

## Followups

- Cleanup delta (post-strict-flip) per DR-138 §6.4 may sweep DL-048
  resolutions back into block shape.
- DR-138 §15.1 "Cleanup delta" deferred until consumer-migration window
  closes; DL-048 entries should be resolved before that delta runs to
  avoid losing the FM signal entirely.
