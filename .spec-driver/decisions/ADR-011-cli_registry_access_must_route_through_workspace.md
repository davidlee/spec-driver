---
id: ADR-011
title: "ADR-011: CLI registry access must route through Workspace"
status: accepted
created: "2026-03-22"
updated: "2026-03-22"
reviewed: "2026-03-22"
owners: []
supersedes: []
superseded_by: []
policies: []
specs: [SPEC-110]
requirements: []
deltas: [DE-120]
revisions: []
audits: []
related_decisions: [ADR-009]
related_policies: [POL-001]
tags: [architecture, cli, registry, coupling]
summary: "CLI command implementations must acquire registries exclusively through Workspace, not by direct import of registry classes."
---

# ADR-011: CLI registry access must route through Workspace

## Context

The `Workspace` class exists as a unified facade over project registries,
providing consolidated lifecycle management, consistent root resolution, and
ordered sync. However, CLI modules systematically bypass it:

- `cli/common.py` contains duplicate registry factory functions (two separate
  blocks totalling ~150 lines) that directly instantiate registries.
- `cli/create.py` constructs `DecisionRegistry`, `PolicyRegistry`,
  `StandardRegistry` directly.
- `cli/find.py` imports 6 registry classes for direct instantiation.
- `cli/list.py` and `cli/show.py` mix facade and direct access.

This creates invisible coupling: every direct import is a second source of
root resolution and registry wiring logic, with no guarantee of consistency.
Changes to registry constructors or root resolution must be propagated to
every direct instantiation site.

## Decision

CLI command implementations must acquire registries exclusively through
`Workspace.from_cwd()` or a `Workspace` instance passed as a parameter.

Direct imports of individual registry classes (`DecisionRegistry`,
`SpecRegistry`, etc.) in CLI modules are prohibited for new code.

### Migration

The direct imports in `common.py`, `create.py`, `find.py`, `list.py`, and
`show.py` constitute technical debt tracked by DE-120. Each module must be
migrated before new registry access patterns are added to it. Adding a new
direct import to an already-non-compliant module is not acceptable.

### Exception

Utility modules in `scripts/lib/` that are not CLI entry points may import
registries directly if they require constructor control that `Workspace` does
not yet expose. The exception must be documented in the module docstring.

## Consequences

### Positive

- Single source of truth for registry wiring and root resolution.
- `Workspace` can enforce lazy-init, caching, and ordered sync.
- Reduces import sprawl in CLI modules.
- Makes the dependency between CLI and domain layer explicit and auditable.

### Negative

- `Workspace` must expose all registries that CLI commands need; missing
  properties require additions before the CLI module can be migrated.
- Typer context threading adds minor ceremony to sub-app wiring.

### Neutral

- This ADR does not change `Workspace` internals or registry APIs.
- `scripts/lib/` modules are exempt and may continue direct registry use.

## Verification

- Code review must reject new direct registry imports in `supekku/cli/`.
- `grep -rn 'Registry(root' supekku/cli/` should trend toward zero.
- DE-120 tracks the migration to completion.

## References

- ADR-009: standard registry API convention
- DE-120: Workspace facade enforcement
- POL-001: maximise code reuse, minimise sprawl
