---
id: STD-004
title: "STD-004: script lifecycle — orphan prevention"
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
deltas: [DE-113]
related_policies: [POL-001]
related_standards: []
tags: [architecture, scripts, lifecycle, hygiene]
summary: "Every standalone script must be registered as an entry point or marked deprecated. Orphaned scripts are deleted."
---

# STD-004: script lifecycle — orphan prevention

## Statement

Every file in `supekku/scripts/*.py` (not under `lib/`) must satisfy exactly
one of:

**(a)** Registered as an entry point in `pyproject.toml [project.scripts]`, or
imported by a registered entry point or the CLI layer; **or**

**(b)** Marked with `# STATUS: deprecated — superseded by: <spec-driver subcommand>`
in its module docstring, with a deletion delta opened.

Scripts without an entry-point registration and without a deprecation notice
are treated as orphaned and deleted in the next tidy delta.

Scripts carrying a deprecation notice for ≥2 deltas without progress toward
deletion are escalated to a required finding in the next workspace audit.

## Rationale

The unified CLI (`supekku/cli/`) superseded the original `supekku/scripts/*.py`
argparse wrappers, but 12+ orphaned scripts were retained indefinitely. Several
had hollow function bodies (`pass`-only display functions) that silently
swallowed output. Without a lifecycle rule, orphaned scripts accumulate, confuse
the namespace, and mislead contributors about where functionality lives.

## Scope

- Applies to `supekku/scripts/*.py` (top-level scripts, not `lib/` modules).
- Does not apply to `supekku/scripts/lib/` (library modules have their own
  lifecycle governed by their consuming code).
- Does not apply to one-time migration scripts that are explicitly date-stamped
  and carry a deletion plan in their docstring.

## Verification

- `pyproject.toml [project.scripts]` is the authoritative entry-point registry.
- Workspace audits should scan for scripts not listed as entry points and not
  carrying a deprecation marker.
- DE-113 is the initial cleanup delta.

## References

- POL-001: maximise code reuse, minimise sprawl
- DE-113: dead code purge
