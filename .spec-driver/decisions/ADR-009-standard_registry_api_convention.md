---
id: ADR-009
title: "ADR-009: standard registry API convention"
status: accepted
created: "2026-03-06"
updated: "2026-03-06"
reviewed: "2026-03-06"
owners: []
supersedes: []
superseded_by: []
policies: []
specs: []
requirements: []
deltas:
  - DE-050
revisions: []
audits: []
related_decisions:
  - ADR-002
related_policies: []
tags:
  - architecture
  - api
  - registry
  - conventions
summary: "Codify the canonical registry API surface from the converged registries: find, collect, iter, domain-specific filter, and keyword-only root auto-discovery, while deferring Protocol/ABC standardisation."
---

# ADR-009: standard registry API convention

## Context

Spec-driver currently has nine registry implementations serving the same broad
role: discover artifact records, look them up by ID, expose them to CLI
consumers, and sometimes persist derived indices. That shared job should have
produced a predictable API. It has not.

The DE-050 audit shows five distinct patterns across nine registries for the
same baseline operations:

- constructor shape (`root` auto-discovery vs required path vs positional root)
- ID lookup (`find`, `get`, dict access, raising resolver, function returning a list)
- collection access (`collect() -> dict`, eager public `.records`, list-returning
  methods, or module-level discovery functions)
- iteration and filtering (`iter(status=None)` in some registries, specialised
  finder methods in others)

Four registries have already converged on a coherent pattern:

- `DecisionRegistry`
- `PolicyRegistry`
- `StandardRegistry`
- `MemoryRegistry`

The DE-050 research treats this as the stable pattern worth blessing rather than
inventing a new abstraction. CLI consumers in `supekku/cli/common.py` already
pay the cost of drift with per-artifact resolver workarounds because the rest of
the registries do not present the same surface.

We need one explicit convention for future and normalised registries so DE-050
is not merely a one-off cleanup and later registries do not drift again.

This ADR governs the **minimum registry read API surface**. It does not attempt
to standardise every registry concern. In particular, it does not settle:

- persistence naming (`sync`, `write`, `save`)
- model placement (`models.py` vs inline)
- model mutability (`frozen` vs mutable dataclasses)
- artifact ID normalisation rules in CLI/resolver layers
- richer domain-specific query methods
- whether functional registries must become classes immediately

ADR-002 remains in force: this API convention does not authorise storing derived
backlinks in frontmatter or any other second source of truth.

## Decision

Adopt the **standard registry API convention** as the canonical surface
for class-based registries.

### 1. Required read surface

Class-based registries MUST expose these read operations:

- `find(id: str) -> Record | None`
- `collect() -> dict[str, Record]`
- `iter(status: str | None = None) -> Iterator[Record]`
- `filter(...) -> list[Record]`

This is the required standard surface. It is intentionally small, but it includes
filtering because the converged registries already provide it and downstream
consumers, especially IMPR-009, benefit from treating filtering as part of the
normal registry contract rather than as an optional extra.

### 2. Constructor contract

The canonical constructor shape is:

```python
def __init__(self, *, root: Path | None = None, ...) -> None:
```

Rules:

- `root` is keyword-only.
- `root` is optional.
- if `root` is omitted, the registry auto-discovers the repository root using
  the normal project path resolution mechanism.
- additional domain-specific constructor parameters are allowed.

This means registries such as `ChangeRegistry` may keep required domain-specific
parameters like `kind`, and registries such as `MemoryRegistry` may keep
optional overrides like `directory`. The convention standardises the `root`
entry point, not the entire signature.

### 3. Return conventions

The standard return conventions are:

- `find()` returns the matching record or `None` when missing
- `find()` does not raise for ordinary "not found" cases
- `collect()` returns a dictionary keyed by canonical artifact ID
- `iter()` yields records and may apply only the common `status` filter

Returning `None` for missing IDs is part of the contract. Raising resolver-style
exceptions remains acceptable for separate domain APIs whose purpose is strict
resolution, but those do not replace the required `find()` method.

### 4. Loading strategy

The convention does **not** mandate lazy-only or eager-only loading.

- lazy construction is the default posture and remains a good fit for registries
  that do not always need a full scan
- eager loading in `__init__` is acceptable when the corpus is small or when the
  registry's design intrinsically depends on a full scan

What matters is the external API contract, not whether the registry warms its
cache during construction or on demand.

### 5. What remains domain-specific

The following remain domain-specific and are not mandated by this ADR:

- the exact `filter()` keyword parameters beyond the existence of the method
- richer query methods beyond `iter(status=None)` and `filter(...)`
- persistence semantics and method names
- internal caching strategy and reload/sync mechanics
- model location and mutability
- additional constructor parameters beyond the standard `root` entry point
- functional vs class-based handling for legacy registries that are not yet in scope

`filter()` is part of the canonical surface, but its parameter set remains
domain-specific. This ADR standardises the presence of the method and its broad
role, not one universal signature. The current converged registries already
demonstrate that pattern:

- decision/policy/standard registries filter on relationship-oriented fields
- memory filters on `memory_type`, `status`, and `tag`

The shared contract is therefore:

- a registry exposes `filter(...)`
- the method applies domain-relevant filtering
- the method returns `list[Record]`
- no-match cases return an empty list

This allows IMPR-009 and future generic consumers to rely on filtering support
existing everywhere without pretending every registry filters on identical fields.

### 6. Protocol/ABC is deferred

We explicitly defer introducing a `typing.Protocol`, abstract base class, or
shared registry superclass.

The converged registries demonstrate a workable convention, but the corpus is
not yet consistent enough to justify freezing a formal abstraction. The ADR is
the contract for now. A Protocol or ABC can be introduced later if, after
normalisation, it clearly reduces duplication without forcing misleading commonality.

## Consequences

### Positive

- Gives DE-050 a concrete target pattern derived from existing successful code
  rather than a fresh abstraction.
- Reduces future drift by making the minimum registry contract explicit.
- Simplifies generic consumers such as CLI artifact resolution and TUI work that
  need predictable registry access.
- Gives IMPR-009 a better baseline for typed/status/domain filtering without
  forcing the TUI to invent one-off filter adapters for every registry.
- Preserves domain flexibility by standardising only the small read surface that
  has already proven reusable.
- Avoids premature commitment to a base class or Protocol before the shape has
  stabilised across the whole corpus.

### Negative

- Some registries will temporarily carry both legacy and canonical methods while
  DE-050 normalises them additively.
- The convention still does not fully unify filter semantics, so some caller-side
  adaptation will remain for richer or cross-registry operations.
- Allowing both lazy and eager loading means construction behaviour is not fully
  predictable from the signature alone.

### Neutral

- This ADR governs the minimum API surface, not registry internals.
- Functional registries such as backlog are not required by this ADR to become
  class-based immediately, though future work may wrap them to align.
- Existing specialised resolver APIs may remain for compatibility or stricter
  domain workflows as long as the canonical read surface also exists.
- Artifact ID normalisation concerns in resolver layers, such as requirement
  colon-to-dot translation or implicit memory ID prefixes, remain a separate
  concern from the registry API contract.
- This ADR does not change ADR-002's prohibition on storing derived backlinks in
  frontmatter.

## Verification

- DE-050 normalisation work adds or adapts registry tests so affected registries
  expose `find()`, `collect()`, `iter(status=None)`, and `filter(...)` with the
  documented return semantics.
- Constructor updates preserve `root` as an optional keyword-only entry point
  for registries brought into conformance.
- Generic consumers such as `supekku/cli/common.py` can reduce per-registry
  workarounds for baseline lookup and collection access.
- Follow-on registry work cites this ADR when introducing a new registry or
  normalising an existing one.
- Any future proposal for a Protocol/ABC demonstrates that the post-DE-050
  corpus has actually converged enough to justify formalisation.

## References

- `change/deltas/DE-050-normalise_registry_api_surface_for_consistent_artifact_access/DE-050.md`
- `change/deltas/DE-050-normalise_registry_api_surface_for_consistent_artifact_access/DR-050.md`
- `change/deltas/DE-050-normalise_registry_api_surface_for_consistent_artifact_access/research.md`
- `backlog/improvements/IMPR-009-tui_dashboard_for_human_navigation_of_spec_driver_workspace/IMPR-009.md`
- `backlog/improvements/IMPR-009-tui_dashboard_for_human_navigation_of_spec_driver_workspace/research.md`
- `specify/decisions/ADR-002-do-not-store-backlinks-in-frontmatter.md`
- `specify/decisions/ADR-006-consolidate_workspace_directories_under_spec_driver.md`
- `supekku/cli/common.py`
