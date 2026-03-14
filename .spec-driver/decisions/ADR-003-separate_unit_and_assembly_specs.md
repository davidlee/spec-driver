---
id: ADR-003
title: "ADR-003: Separate unit and assembly specs"
status: accepted
created: "2026-02-20"
updated: "2026-02-21"
reviewed: "2026-02-21"
owners: []
supersedes: []
superseded_by: []
policies: []
specs: []
requirements: []
deltas: []
revisions: []
audits: []
related_decisions: []
related_policies: []
tags: []
summary: "Introduce explicit separation between auto-generated unit specs (1:1 with code units) and human-authored assembly specs (cross-unit), with a clear truth/precedence model."
---

# ADR-003: Separate unit and assembly specs

## Context

Spec-driver currently places “tech specs” under `specify/tech/SPEC-###/` and uses sync tooling to auto-stub specs
for language units (packages/modules/files). This conflates two very different artefact types:

- **Auto-generated, code-bound specs** (today: “SPEC bundles created by sync”): 1:1 with a language unit
  and tightly coupled to generated contracts (derived from code).
- **Human-authored, cross-cutting specs** (desired): describe a subsystem/assembly/integration spanning multiple
  units, often created before or alongside code, and may include aspirational intent.

This ambiguity causes problems in legacy codebase adoption:

- Sync can produce a large number of stub specs that drown out “real” architecture/integration specs.
- Users/agents cannot reliably infer whether a spec is “observed from code” or “intended design”.
- When multiple specs describe interface-like truth (signatures, schemas, types), conflicts become likely and
  the system has no structural support to manage ownership or precedence.

We need a clear taxonomy, filesystem/ID approach, and a truth model for “who owns what”.

## Decision

### Terminology

Adopt two primary terms:

- **Unit spec**: a spec whose primary subject is a single code unit (language-specific: file/module/package).
- **Assembly spec**: a spec whose subject spans multiple units (subsystem, functional slice, integration boundary).

We intentionally avoid “module spec” because “module” varies across languages and can mean both file and package.

### Classification (non-breaking v1)

Keep existing spec IDs and storage (`SPEC-###` under `specify/tech/`) but require explicit classification via frontmatter:

- `c4_level`: already supported by schema (`system|container|component|code`)
- Standardize `category` to distinguish `unit` vs `assembly` (and allow future categories).

Reserved `category` values for `kind: spec` (tech specs):

- `unit`: 1:1 with a single language unit (file/module/package/folder as language-appropriate)
- `assembly`: cross-unit (subsystem, integration boundary, functional slice)

Default mapping (guidance, not a strict rule):

- `category: unit` SHOULD imply `c4_level: code`
- `category: assembly` SHOULD use `c4_level: component|container|system` depending on scope

Tooling SHOULD provide “views” (indices) that separate these categories for navigation and automation, without requiring
an immediate breaking migration.

Sync-created unit specs MUST set:

- `category: unit`
- `c4_level: code`

### Filesystem / ID strategy (potential breaking v2, optional)

If/when we decide to introduce new prefixes/roots (e.g. `UNIT-###` under `specify/unit/`, `ASM-###` or `INTG-###` under
`specify/assembly/`), we will:

- Preserve stable references via symlinks and registries (old `SPEC-###` remains resolvable).
- Provide a migration tool that rewrites registries, indices, and relationships.

This is explicitly deferred until classification + workflows prove the taxonomy value.

### Truth model (prevent conflicting “interface truth”)

Define a provenance/precedence rule:

- **Observed contracts** (generated deterministically from code, e.g. under `.contracts/**`) are the canonical
  representation of “what the code currently exposes”.
- **Unit specs** may _summarize_ and _reference_ observed contracts, but MUST NOT attempt to be the authoritative
  source of signatures/types/schemas when those are generated from code.
- **Assembly specs** may specify _requirements and constraints_ on interfaces (compatibility, invariants, expected
  shapes), but those MUST be expressed as requirements that can be validated against observed contracts/code, not as
  competing “authoritative copies” of full signatures.

For overlapping descriptions, introduce ownership metadata (incremental, non-breaking):

- A spec may declare “claims” over a set of units/symbols/paths it governs (future block schema).
- Validation warns on overlapping claims unless an explicit override relationship exists.

This reduces ambiguity and gives validation a hook to detect contradictory assertions early.

## Consequences

### Positive

- Makes legacy adoption tractable: unit-spec sprawl is separated from human-authored architecture specs.
- Clarifies intent: readers can tell whether a spec is code-bound (“unit”) or cross-cutting (“assembly”).
- Creates a path to structural conflict detection (claims/ownership), not just social convention.
- Avoids breaking changes initially by using classification + views before changing IDs/paths.

### Negative

- Adds new concepts (unit vs assembly, ownership/claims) that must be learned and enforced.
- Some specs will be ambiguous (package spec vs component spec) and need editorial judgment.
- If we later adopt new prefixes/dirs, migration will still be invasive (just deferred and better-informed).

### Neutral

- Existing `SPEC-###` IDs remain the stable referent in the near term; taxonomy is expressed via metadata and indices.
- Contract generation/corpus decisions (e.g. `.contracts/` canonical derived store) remain compatible with this ADR.
- Sync semantics should shift to avoid auto-generated unit spec sprawl in legacy repos:
  - `sync` SHOULD be contracts-first by default and SHOULD NOT auto-create unit specs on first run.
  - Users SHOULD be able to opt in to spec auto-creation explicitly, and the tool SHOULD persist that preference in-repo so future `sync` runs behave consistently.
  - Contract generation SHOULD be explicitly controllable (e.g. `--contracts/--no-contracts`) independent of spec creation.

## Verification

- Validator warns when a spec lacks `c4_level`/category once the taxonomy is adopted.
- Validator warns on overlapping ownership claims (once claims schema exists), with deterministic override rules.
- CLI/list commands can filter specs by category (unit vs assembly) and/or `c4_level`.
- Sync UX:
  - First-run `sync` does not create specs unless opted in.
  - Once opted in, subsequent `sync` runs default to that behavior (filesystem marker/config).

## References

- `specify/product/PROD-012/PROD-012.md` (contract sync + spec stubbing goals)
- `specify/product/PROD-014/PROD-014.md` (contracts corpus ergonomics)
- `specify/product/PROD-015/PROD-015.md` (taxonomy + navigation intent)
- `change/revisions/RE-015-contracts_canonical_storage_sync_less_generation/RE-015.md`
- `change/revisions/RE-016-sync_defaults_contracts_first_opt_in_spec_creation/RE-016.md`
- `change/deltas/DE-030-unit_vs_assembly_spec_classification/DE-030.md`
