---
id: STD-003
title: "STD-003: utility module placement rule"
status: required
created: "2026-03-22"
updated: "2026-03-22"
reviewed: "2026-03-22"
owners: []
supersedes: []
superseded_by: []
policies: [POL-001]
specs: []
requirements: []
deltas: [DE-115]
related_policies: [POL-001]
related_standards: []
tags: [architecture, code-organization, utilities]
summary: "Extracted shared utilities go in core/ or the narrowest shared lib/ package. Never in a registry or creation module."
---

# STD-003: utility module placement rule

## Statement

When a function is extracted to satisfy POL-001 (extraction threshold), it must
be placed in the correct module:

- **Domain-agnostic utilities** (date parsing, ID generation, string
  normalisation, file I/O helpers, regex factories) go in
  `supekku/scripts/lib/core/`. Use or create a focused module:
  `core/dates.py`, `core/ids.py`, `core/io.py`, etc.

- **Domain-specific shared logic** (e.g. block extraction helpers shared by
  multiple block types) goes in the narrowest `lib/` subpackage that covers
  all callers. For example, a YAML code-fence regex factory used by
  `blocks/delta.py`, `blocks/verification.py`, and `blocks/plan.py` belongs
  in `blocks/yaml_utils.py`.

- **Prohibited locations**: Shared utilities must not live inside a registry
  module, a creation module, or a CLI module. These are consumers of utilities,
  not providers.

## Rationale

Without a placement rule, extracted utilities end up wherever the first caller
lives — typically a registry or creation module. This creates coupling: other
callers must import from a domain module to get a domain-agnostic function.
The codebase currently has `parse_date()` in three registry classes and
sequential-ID generation in eight different modules, all because there was no
rule directing extraction to `core/`.

## Scope

Applies to all shared utility extractions in `supekku/scripts/lib/`. Does not
apply to one-off helpers private to a single module (`_` prefix, not imported
elsewhere).

## Verification

- Code review must verify that new shared utilities land in the correct
  location per this standard.
- `grep -rn 'def ' supekku/scripts/lib/*/registry.py` should find only
  registry-specific methods, not general utilities.

## References

- POL-001: maximise code reuse, minimise sprawl
- DE-115: core utility extraction
