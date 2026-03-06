---
id: ADR-006
title: 'ADR-006: consolidate workspace directories under .spec-driver'
status: draft
created: '2026-03-06'
updated: '2026-03-06'
reviewed: '2026-03-06'
owners: []
supersedes: []
superseded_by: []
policies: []
specs: []
requirements: []
deltas: []
revisions: []
audits: []
related_decisions:
  - ADR-001
  - ADR-003
related_policies: []
tags:
  - architecture
  - workspace
  - install
summary: 'Canonical spec-driver workspace directories move under .spec-driver/ with backward-compat root symlinks; migration tooling and content reference cleanup are deferred.'
---

# ADR-006: consolidate workspace directories under .spec-driver

## Context

Spec-driver currently spreads its workspace across several top-level repository
directories, notably `specify/`, `change/`, `backlog/`, `memory/`, and
`.spec-driver/`. This has a few practical costs:

- the repo root feels more invasive than necessary for a tool intended for wider adoption
- the workspace is split across multiple load-bearing locations
- common git operations require remembering several roots instead of one
- user-serviceable configuration and spec-driver-managed internals are mixed together under `.spec-driver/`

`IMPR-008` and its spike concluded that the default layout should be simplified.
The main alternatives were:

- **Option A: flatten under `.spec-driver/`**
- **Option B: move current groupings under `.spec-driver/` but keep `specify/` and `change/`**

The spike found that:

- production code already centralizes directory values in `core.paths`, so the
  implementation surface is contained
- most stored registry paths are derived and safely regenerated
- repo-internal symlinks are already a normal and reliable compatibility mechanism here
- content cross-references do not need immediate rewriting if compatibility
  symlinks preserve the old paths
- migration tooling would add noticeable scope without solving an immediate
  adoption problem

This ADR decides the canonical layout for spec-driver workspace directories.
It does not define a migration command, and it does not require immediate
cleanup of existing prose references.

## Decision

Adopt **Option A (flatten)** as the canonical default layout.

Canonical spec-driver workspace directories will consolidate under
`.spec-driver/`, with root-level backward-compatibility symlinks from the old
top-level paths such as `specify/`, `change/`, and `backlog/`.

### 1. Canonical footprint

For the workspace governed by spec-driver, `.spec-driver/` is the single
canonical top-level home. The intended outcome is effectively zero repo-root
pollution beyond `.spec-driver/` for these directories.

This improves discoverability of ownership and makes the workspace easier to
reason about as one managed tree instead of several unrelated roots.

### 2. Flatten rather than preserve `specify/` and `change/`

We will not retain `specify/` and `change/` as canonical grouping directories
inside `.spec-driver/`.

Directories such as `decisions/`, `tech/`, `product/`, `deltas/`, `revisions/`,
and `audits/` are already self-explanatory enough without another level of
grouping. Flattening removes indirection rather than moving it.

### 3. Backward-compatibility via symlinks

Legacy top-level paths such as `specify/`, `change/`, and `backlog/` will be
provided as backward-compatibility symlinks to the canonical locations under
`.spec-driver/`.

These symlinks are convenience and compatibility views, not canonical storage.
They are cosmetic rather than load-bearing. Users may rename, remove, or ignore
them without changing where spec-driver considers the authoritative workspace to
live.

### 4. Separate config from managed internals

Introduce a `.spec-driver/config/` grouping for user-serviceable configuration
and templates, including files such as:

- `workflow.toml`
- `doctrine.md`
- templates and related editable config assets

This keeps user-edited lifecycle/config material separate from spec-driver-managed
internals such as:

- `agents/`
- `hooks/`
- `registry/`

### 5. Dotdir discoverability is not a blocking concern

We reject “hidden directories are too hard to find” as a meaningful objection to
this layout.

In practice, `.spec-driver/` is already a daily-use dotdir in this repository,
and `.contracts/` already demonstrates that dotdir-based canonical storage is
workable. The project already expects agents and users to work comfortably with
dot-prefixed directories.

### 6. Defer migration tooling

We explicitly defer dedicated migration tooling.

At current adoption, a purpose-built migration command is unnecessary scope.
Compatibility symlinks reduce the immediate cost of changing defaults for new or
actively managed workspaces. If migration pain becomes real later, we can add a
targeted migration flow then.

### 7. Defer content cross-reference cleanup

We explicitly defer bulk rewriting of markdown cross-references and similar
content that still names old paths.

Those references may continue to work through backward-compatibility symlinks.
We will not pay the cost of mass editorial cleanup until it produces practical
value.

### 8. Atomic git operations are a design goal

This layout should make spec-driver changes easier to stage and review as one
tree. In the steady state, `git add .spec-driver` should capture the canonical
spec-driver workspace rather than requiring several unrelated root paths.

## Consequences

### Positive
- Consolidates the canonical workspace under one top-level directory.
- Makes staging and reviewing spec-driver changes more atomic.
- Removes unnecessary nesting such as `specify/decisions/`.
- Clarifies which files are user-serviceable config versus managed internals.
- Preserves existing path expectations through backward-compatibility symlinks.
- Avoids premature investment in migration tooling and mass reference rewriting.

### Negative
- The `.spec-driver/` root will have more direct child directories.
- Some users may prefer explicit root-level directories for casual shell browsing.
- Existing documentation and content will continue to contain old path spellings for a while.
- A later migration command, if needed, will still require design and implementation work.

### Neutral
- Existing root-level paths become compatibility views rather than canonical locations.
- Cross-reference cleanup is deferred, not rejected permanently.
- This ADR sets the default layout direction; implementation details still belong in follow-up change work.
- The separate contracts corpus decision remains governed by existing specs and ADRs unless changed explicitly.

## Verification
- Default workspace initialization creates the canonical directories under `.spec-driver/`.
- User-serviceable files move under `.spec-driver/config/`, while managed internals remain outside that subdirectory.
- Backward-compatibility symlinks from `specify/`, `change/`, and `backlog/` resolve to the canonical targets.
- Internal path resolution treats `.spec-driver/` locations as canonical rather than depending on the symlinked views.
- Existing content that references old top-level paths continues to resolve correctly through compatibility symlinks.
- No migration command is required to satisfy this ADR initially.

## References
- `backlog/improvements/IMPR-008-configurable_workspace_directory_layout_with_migration_support/IMPR-008.md`
- `backlog/improvements/IMPR-008-configurable_workspace_directory_layout_with_migration_support/spike.md`
- `specify/decisions/ADR-001-use-spec-driver-to-build-spec-driver.md`
- `specify/decisions/ADR-003-separate_unit_and_assembly_specs.md`
