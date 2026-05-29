---
id: mem.signpost.spec-driver.upgrade.metadata-blocks-0-10
slug: upgrade-metadata-blocks-0-10
name: 'Upgrade Runbook: Metadata Blocks (0.10)'
kind: memory
status: active
memory_type: signpost
created: '2026-05-30'
updated: '2026-05-30'
verified: '2026-05-30'
confidence: medium
tags:
- spec-driver
- upgrade
- migration
summary: 'Client upgrade runbook for the 0.10 metadata-blocks consolidation: admin
  migrate sequence, per-kind strict-mode flip, and drift-ledger residual model.'
---

# Upgrade Runbook: Metadata Blocks (0.10)

## Summary

The 0.10 line consolidated artefact metadata into validated structured blocks
(ADR-010) across **delta, spec/prod, requirements-in-spec, audit, and
revision**. Upgrading an existing `.spec-driver/` is a **migrate-then-flip**
process, kind by kind, with residual drift captured in ledgers you disposition.
Nothing is bulk-rewritten; migrations are idempotent and opt-in.

## Context

A fresh `install` enables per-kind strict-on-validate by default. An **upgrade**
leaves strict **off** (tolerant read) so you can migrate at your own pace and
flip each kind only once its sweep is clean (install fresh-vs-upgrade default,
DEC-137-18). Truth model unchanged — see [[mem.concept.spec-driver.truth-model]]
and [[mem.signpost.spec-driver.overview]].

## Runbook

### 1. Preview

```
uv run spec-driver admin migrate --list      # pending + applied steps
uv run spec-driver admin migrate --check     # what each kind would touch
```

Registered steps (kind in brackets): `v0_10_0_001_delta_blocks` [delta],
`002_spec_blocks` [spec], `003_prod_blocks` [prod], `004_audit_findings`
[audit], `005_revision_metadata` [revision].

### 2. Migrate + flip, one kind at a time

```
uv run spec-driver admin migrate <kind> --dry-run   # inspect diff
uv run spec-driver admin migrate <kind>             # apply (idempotent)
uv run spec-driver validate workspace --kind <kind> # confirm conformance
uv run spec-driver admin migrate <kind> --strict    # flip [validation.strict].<kind>=true after sweep passes
```

`admin migrate all` sweeps every kind. The `--strict` flag is the **only**
thing that flips strict; do it per kind after that kind's sweep is acceptable.
Order is free, but `delta` first establishes the pattern.

### 3. Requirements-in-spec (separate, feature-level — DEC-140-13)

Requirements migration is **not** part of `admin migrate`; it is per-spec and
has its own strict toggle (`[validation.strict_requirements]`, not
`[validation.strict].requirement`):

```
uv run spec-driver admin migrate-requirements <SPEC_ID> --dry-run
uv run spec-driver admin migrate-requirements <SPEC_ID>
uv run spec-driver admin strict-flip-requirements   # enable strict_requirements
```

### 4. Discoverability surfaces (verify the upgrade)

```
uv run spec-driver schema enums                # controlled-vocab fields by kind
uv run spec-driver schema enums <kind>.<field> # canonical + aliases + tolerated
uv run spec-driver validate file <path>        # single-file diagnostics
```

## Drift-ledger residual model

Requirements migration emits **drift ledgers** (`DL-*`, `kind: drift_ledger`)
under `.spec-driver/drift/` for lines it could not cleanly migrate. Two classes,
two dispositions:

- **`requirement_unparseable`** — frequently **false positives**: the heuristic
  flags coverage/relationship-block reference lines (`- SPEC.FR-001`,
  `requirement: SPEC.FR-001`), not requirement definitions. Disposition:
  **dismiss** (entry `status: dismissed`). Do not treat as real drift.
- **`description_placeholder` / `acceptance_placeholder`** — **real but minor**:
  migrated requirements keep their titles but have empty `description` /
  `acceptance_criteria`. Re-derivable on demand. Disposition: **defer** (entry
  `status: deferred`); backfill opportunistically when the spec is next revised.

Close a ledger by setting frontmatter `status: closed` once its entries are
dispositioned. Ledger statuses are `{open, closed}`; entry statuses include
`{dismissed, deferred, ...}` — see `supekku/scripts/lib/drift/models.py`.

`verified` requirement coverage reflects **implementation/evidence**, not
description completeness — flipping FRs to `verified` while placeholder debt
remains is expected.

## Gotchas

- **Strict is opt-in on upgrade.** Flipping a kind before its sweep is clean
  surfaces every legacy non-conformance at once. Migrate → validate → flip.
- **Two strict toggles.** `[validation.strict].<kind>` (delta/spec/audit/revision)
  vs `[validation.strict_requirements].enabled` (requirements). Different
  sections, different commands.
- Migrations live in an isolated package (`spec_driver/migrations/**`, POL-003);
  they import only stdlib + helpers + pyyaml and never import `validation/`.

## Provenance

Authored at DE-136 umbrella close (metadata-schema-consolidation program;
PROD-004). Drift-disposition model and the known migrator defects (false-positive
heuristic, requirement backfill debt) are tracked in **ISSUE-064**. Related:
[[mem.pattern.architecture.migration-principles]],
[[mem.signpost.spec-driver.file-map]].

