---
id: ADR-010
title: "ADR-010: Default placement heuristic for structured artifact metadata"
status: accepted
created: "2026-03-22"
updated: "2026-03-22"
reviewed: "2026-03-22"
owners: []
supersedes: []
superseded_by: []
policies: []
specs: []
requirements: []
deltas: [DE-106]
revisions: []
audits: []
related_decisions: [ADR-002, ADR-009]
related_policies: []
tags: [architecture, metadata, frontmatter, placement]
summary: >-
  Frontmatter is the default home for stable, machine-consumed artifact
  metadata. Code-fenced YAML blocks are reserved for schema-versioned data
  with independent lifecycle. Markdown prose carries volatile execution detail.
---

# ADR-010: Default placement heuristic for structured artifact metadata

## Context

Spec-driver artifacts store structured metadata in three possible locations:

1. **YAML frontmatter** — parsed by `load_markdown_file()`, tooling-wide
2. **Code-fenced YAML blocks** (`supekku:schema@vN`) — parsed by block extractors
3. **Markdown prose** — parsed by humans and regex fallbacks

DE-106 exposed that phase sheets duplicated the same data across all three
locations (triple-entry bookkeeping), creating a maintenance tax and
systematic drift. The field analysis in DR-106 §3a showed that the
duplication was not deliberate — it accumulated because there was no
explicit placement rule.

Without a default heuristic, each new artifact kind risks repeating the
pattern: block schemas are added for "future machine use" and prose sections
mirror them for "human readability," producing parallel maintenance surfaces
with no clear authority boundary.

### Related decisions

- **ADR-002**: No backlinks in frontmatter (placement constraint for one field type)
- **ADR-009**: No speculative structure for future registries (argues against
  preserving structure "just in case")

## Decision

Apply the following default placement heuristic for new or refactored
artifact metadata:

### 1. Frontmatter (default for stable contract fields)

Use when the field is:
- **Consumed by tooling** (CLI, formatters, validators, artifact loading)
- **Stable after authoring** (written once or rarely updated)
- **Identity, lineage, or planning contract** (IDs, relationships, objectives, criteria)

Examples: `id`, `status`, `kind`, `plan`, `delta`, `objective`,
`entrance_criteria`, `exit_criteria`.

### 2. Code-fenced YAML blocks (schema-versioned, independent lifecycle)

Use when the field:
- **Has its own schema version** that may evolve independently
- **Is consumed by a dedicated extractor** (not general frontmatter loading)
- **Represents a self-contained data structure** (verification coverage, plan overview, relationship maps)

Examples: `supekku:verification.coverage@v1`, `supekku:plan.overview@v1`,
`supekku:spec.relationships@v1`.

### 3. Markdown prose (volatile execution detail)

Use when the field:
- **Changes frequently during execution** (task status, progress notes)
- **Is primarily human-authored and human-consumed**
- **Does not need machine-readable structure** for current tooling

Examples: task tables with checkboxes, research notes, decision logs,
implementation observations.

### Conflict resolution

When a field could live in multiple locations:

1. If tooling needs it → frontmatter (not block)
2. If it has independent versioned schema → block
3. If it's volatile execution detail → prose
4. **Never duplicate across locations.** Each field has one authoritative home.

## Consequences

### Positive

- Clear default for new artifact kinds — reduces ad-hoc placement decisions
- Eliminates triple-entry patterns before they form
- Frontmatter-first bias aligns with existing `load_markdown_file()` infrastructure
- Block schemas reserved for genuinely versioned data structures

### Negative

- Existing artifacts with block-based metadata may need migration over time
- The heuristic is a default, not a mandate — edge cases may require exceptions

### Neutral

- Does not retroactively require migration of existing block-based metadata
- Per ADR-009, does not require building validation for cases that have no
  current consumer

## Verification

- Phase sheets (DE-106) serve as the reference implementation
- New artifact kinds should cite this ADR when choosing field placement
- `spec-driver validate` enforces the phase frontmatter schema via PhaseSheet

## References

- [DR-106 §3a](../deltas/DE-106-phase_sheet_template_dry_eliminate_triple_entry_bookkeeping_across_frontmatter_blocks_and_markdown/DR-106.md) — field-by-field placement analysis
- [DR-106 §7 DEC-004](../deltas/DE-106-phase_sheet_template_dry_eliminate_triple_entry_bookkeeping_across_frontmatter_blocks_and_markdown/DR-106.md) — decision to land this ADR
- [IMPR-022](../backlog/improvements/IMPR-022-phase_sheet_template_dry_eliminate_triple_entry_bookkeeping_across_frontmatter_blocks_and_markdown/IMPR-022.md) — original duplication analysis
