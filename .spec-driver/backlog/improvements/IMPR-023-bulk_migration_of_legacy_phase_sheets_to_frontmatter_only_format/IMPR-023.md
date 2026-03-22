---
id: IMPR-023
name: Bulk migration of legacy phase sheets to frontmatter-only format
created: "2026-03-22"
updated: "2026-03-22"
status: idea
kind: improvement
relations:
  - type: follows_from
    target: DE-106
  - type: relates_to
    target: IMPR-022
---

# Bulk migration of legacy phase sheets to frontmatter-only format

## Problem

Legacy phase sheets (pre-DE-106) carry `phase.overview` and `phase.tracking`
embedded YAML blocks alongside markdown body content. These phases work via
the frontmatter-first fallback path in `artifacts.py`, but the blocks are
redundant maintenance surface.

## Proposed Solution

Write a migration script that:

1. Reads each legacy phase file
2. Extracts canonical fields from `phase.overview` block
3. Populates frontmatter with `plan`, `delta`, `objective`, `entrance_criteria`, `exit_criteria`
4. Removes the `phase.overview` and `phase.tracking` blocks
5. Preserves all markdown body content

## Priority

Low. The fallback path works correctly. Migration is a cleanup/hygiene
improvement, not a functional requirement. Phases migrate naturally when
agents touch them during active work.

## Context

- See DE-106 DR-106 OQ-001: "compatibility now, opportunistic migration later"
- See `mem.pattern.phase.frontmatter-block-precedence` for the compatibility strategy
