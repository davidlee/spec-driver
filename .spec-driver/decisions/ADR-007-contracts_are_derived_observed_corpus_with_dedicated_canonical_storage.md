---
id: ADR-007
title: 'ADR-007: contracts are derived observed corpus with dedicated canonical storage'
status: accepted
created: '2026-03-06'
updated: '2026-03-06'
reviewed: '2026-03-06'
owners: []
supersedes: []
superseded_by: []
policies: []
specs:
  - PROD-005
  - PROD-012
  - PROD-014
requirements: []
deltas:
  - DE-047
revisions: []
audits: []
related_decisions:
  - ADR-003
  - ADR-004
  - ADR-006
related_policies: []
tags:
  - contracts
  - architecture
  - sync
summary: 'Contracts are derived observation artefacts, not competing intent; they belong in a dedicated canonical contracts corpus, while spec-bundle and index paths remain derived compatibility or navigation views.'
---

# ADR-007: contracts are derived observed corpus with dedicated canonical storage

## Context

The current corpus disagrees on three questions already recorded in `DL-047`:

- are contracts canonical observed output or spec-local supporting files?
- is the dedicated contracts corpus or `SPEC-*/contracts/` canonical storage?
- does the `PROD-014` mirror-of-source tree replace or augment the older
  by-language/by-package trees from `PROD-012`?

This ADR settles those questions and keeps the answer compatible with `ADR-006`
path consolidation and future configurable workspace roots.

## Decision

### 1. Contracts are observed truth, not competing intent

Contracts are generated observation artefacts: the deterministic record of what
the code currently exposes.

They do **not** compete with specs as a second intent layer:

- contracts answer "what does the code expose now?"
- specs answer "what behaviour, constraints, and responsibilities are accepted?"

This follows `ADR-003` and `ADR-004`: contracts provide observed interface
truth; specs become authoritative after reconciliation against observed truth.

### 2. Contracts belong in a dedicated canonical corpus

Generated contracts must live in one dedicated canonical contracts corpus,
separate from authored specs.

Under the current default layout that corpus is `.contracts/**`.

This ADR distinguishes the **canonical storage role** from the **current default
path**. If future path-centralization work moves the root under `.spec-driver/`
or elsewhere, the model remains the same: one dedicated canonical corpus for
generated contracts.

### 3. Spec-bundle contract paths are derived compatibility views

Paths such as `specify/tech/SPEC-*/contracts/` are not canonical storage.
They are compatibility and convenience views over the canonical contracts corpus.

They may remain available for backward compatibility or ergonomics, but
spec-driver must not treat them as the authoritative location of generated
contracts.

### 4. The contracts corpus is always safe to delete and regenerate

Contracts are derived and deterministic output. The canonical contracts corpus
must always be safe to delete and rebuild from unchanged source inputs.

In practice: contracts are not user-authored records, regeneration is the normal
recovery path, unchanged source should reproduce byte-identical output, and any
compatibility views must also be rebuildable.

### 5. Mirror-of-source corpus is the primary navigation model

The dedicated contracts corpus should use a mirror-of-source navigation shape as
its primary layout.

This resolves the `PROD-012` / `PROD-014` ambiguity by making the `PROD-014`
mirror tree the primary navigation and storage model for the corpus.

### 6. By-language and by-package trees augment; they do not compete

By-language and by-package symlink trees from `PROD-012` may still exist, but
they are derived navigation indexes only.

They augment the mirror-of-source corpus for alternate browsing patterns. They
do not replace it and they are not a second canonical storage structure.

### 7. Configurability must preserve the model, not hardcode the path

Future configurability may change the default root path, but it must preserve
the same model: contracts stay in a dedicated derived corpus, compatibility
paths stay derived views, and the primary navigation model remains
mirror-of-source.

## Consequences

### Positive
- Resolves the main contracts contradiction across `PROD-005`, `PROD-012`,
  and `PROD-014`.
- Makes the truth model legible: contracts are observed interface truth, specs
  are accepted intent and constraints.
- Removes authored spec bundles as a competing storage location for generated output.
- Lets mirror-of-source navigation become the clear default for discovery and search.
- Preserves alternate navigation trees without giving them doctrinal weight.
- Keeps the decision compatible with future configurable path work.

### Negative
- Older specs and examples that still point at `SPEC-*/contracts/` become
  explicit drift to revise.
- Some users may prefer spec-local browsing and see dedicated corpus storage as less immediately contextual.
- Supporting compatibility views and alternate indexes still adds implementation and maintenance cost.

### Neutral
- This ADR does not require every compatibility path to exist forever; it only
  classifies them as derived rather than canonical.
- This ADR does not force an immediate move of the corpus under `.spec-driver/`;
  it remains compatible with `ADR-006` if the default root later moves there.
- The exact set of derived navigation views remains an implementation/spec
  question so long as they do not compete with the canonical corpus.

## Verification
- Generated contracts are written to the canonical contracts corpus, not authored
  spec bundles.
- Deleting the canonical contracts corpus and regenerating it reproduces the same
  output from unchanged source.
- Any `SPEC-*/contracts/` locations, if present, are rebuilt as compatibility views.
- Mirror-of-source paths are the primary navigation/storage shape of the
  canonical contracts corpus.
- By-language and by-package trees, if present, are implemented as derived
  indexes and do not contain independent canonical files.
- Follow-up revisions reconcile `PROD-005`, `PROD-012`, and `PROD-014` to this decision.

## References
- `drift/DL-047-spec-corpus-reconciliation.md`
- `specify/decisions/ADR-003-separate_unit_and_assembly_specs.md`
- `specify/decisions/ADR-004-canonical_workflow_loop.md`
- `specify/decisions/ADR-006-consolidate_workspace_directories_under_spec_driver.md`
- `specify/product/PROD-005/PROD-005.md`
- `specify/product/PROD-012/PROD-012.md`
- `specify/product/PROD-014/PROD-014.md`
