---
id: IMPR-022
name: "Phase sheet template DRY: eliminate triple-entry bookkeeping across frontmatter, blocks, and markdown"
created: "2026-03-21"
updated: "2026-03-21"
status: idea
kind: improvement
relations:
  - type: relates_to
    target: DE-104
    description: DE-104 investigation surfaced this as a root cause of agent drift
  - type: relates_to
    target: IMPR-021
    description: PhaseRegistry would change what tooling reads from phase sheets, affecting which representations carry value
  - type: relates_to
    target: DE-004
    description: DE-004 designed the original phase management system including blocks and template
---

# Phase sheet template DRY: eliminate triple-entry bookkeeping

## Problem

A canonical phase sheet contains four representation layers for the same
information. Agents must keep all four in sync manually. They don't — and that's
a root cause of the status drift DE-104 addresses.

## Duplication map

Concrete example from a real phase sheet (IP-104.PHASE-01):

### Phase ID — 3 locations

| Layer                | Field    | Example           |
| -------------------- | -------- | ----------------- |
| Frontmatter          | `id:`    | `IP-104.PHASE-01` |
| phase.overview block | `phase:` | `IP-104.PHASE-01` |
| phase.tracking block | `phase:` | `IP-104.PHASE-01` |

### Entrance/exit criteria — 3 locations

| Layer                | Format                                 | Example                                                                        |
| -------------------- | -------------------------------------- | ------------------------------------------------------------------------------ |
| phase.overview block | YAML list of strings                   | `- DR-104 approved with review findings integrated`                            |
| phase.tracking block | YAML list of `{item, completed}` dicts | `- item: "DR-104 approved with review findings integrated"\n  completed: true` |
| Markdown body §3/§4  | Checkbox lists                         | `- [x] DR-104 approved with review findings R1-R3, C1-C2 integrated`           |

The tracking block adds `completed:` booleans. The markdown checkboxes convey
the same with `[x]` vs `[ ]`. The overview block has the criteria text without
progress state. Three copies of the same text, three formats, three places to
update when a criterion changes.

### Objective — 2 locations

| Layer                | Format                        |
| -------------------- | ----------------------------- |
| phase.overview block | `objective: >-` (YAML scalar) |
| Markdown body §1     | Prose paragraph               |

### Tasks — 2 locations

| Layer                | Format                                                     |
| -------------------- | ---------------------------------------------------------- |
| phase.overview block | YAML list of title strings                                 |
| Markdown body §7     | Table + detail blocks with approach, files, testing, notes |

The overview carries titles only. The markdown body has the actual useful detail.
The title list in the overview is pure redundancy — it conveys nothing the
markdown table heading doesn't.

### Verification — 2 locations

| Layer                | Format                                   |
| -------------------- | ---------------------------------------- |
| phase.overview block | `verification.tests:` (list of commands) |
| Markdown body §5     | Prose list of commands and evidence      |

### Risks — 2 locations

| Layer                | Format                                    |
| -------------------- | ----------------------------------------- |
| phase.overview block | YAML list of strings                      |
| Markdown body §8     | Table with risk/mitigation/status columns |

The markdown table has more structure (mitigation, status). The YAML list is a
subset.

## What each layer uniquely contributes

### Frontmatter — identity + lifecycle (valuable, keep)

`id`, `slug`, `name`, `created`, `updated`, `status`, `kind`. This is the
standard artifact identity block. Every artifact type has it. Tooling reads it
for listing, filtering, status transitions. No redundancy issue.

### phase.overview block — machine-readable summary (questionable value)

Designed for tooling to read structured phase data. In practice:

- `show delta` reads `objective` from it to display phase summaries
- Nothing else reads it programmatically
- Everything it contains is also in the markdown body with more detail
- Agents must keep it in sync with the body — and frequently don't

The overview block is a promise of machine-readability that hasn't been
fulfilled. If `show delta` needs objectives, it could read frontmatter or the
first heading.

### phase.tracking block — progress overlay (valuable concept, wrong execution)

The `completed: true/false` on criteria is the only machine-readable progress
tracking. This is genuinely useful — it enables programmatic progress queries
("how many exit criteria are met?"). But:

- It duplicates the criteria text from the overview
- It competes with markdown checkboxes for the same information
- Agents update checkboxes in the body but forget the tracking block (or vice
  versa)
- No tooling currently reads the tracking block for progress reporting

### Markdown body — implementation detail (valuable, keep)

Task detail blocks (§7), decisions (§9), findings (§10), assumptions (§6) — this
is where implementation-depth content lives. The body is what agents actually
work from. It's not redundant with the blocks; the blocks are redundant with it.

## Quantifying the overhead

A typical phase sheet is ~150–200 lines. Of those:

- ~8 lines: frontmatter (useful)
- ~30 lines: phase.overview block (mostly redundant with body)
- ~20 lines: phase.tracking block (criteria text redundant with overview + body)
- ~140 lines: markdown body (the actual content)

Roughly **25% of a phase sheet is ceremonial duplication** that exists for
tooling that doesn't use it.

## The agent behaviour consequence

Agents face three options when updating phase state:

1. Update all three representations (correct but tedious — nobody does this
   consistently)
2. Update the markdown body only (what usually happens — blocks drift)
3. Update blocks only (rare — body drifts)

The `/update-delta-docs` skill tells agents to reconcile blocks and body. In
practice, this is where status drift, criteria drift, and task drift enter.
DE-104 addresses status specifically, but the structural incentive to drift
remains.

## Possible directions (not prescriptive)

### A. Eliminate the overview block entirely

The markdown body contains everything the overview has, with more detail.
`show delta` could read the objective from frontmatter (add an `objective:`
field) or from the first markdown heading/paragraph.

- Pro: Removes the primary duplication source
- Con: Loses machine-readable entrance/exit criteria, verification, tasks
- Con: Breaking change for `show delta` formatter and `create_phase()` renderer

### B. Eliminate the tracking block; use overview + markdown checkboxes

Keep the overview block as the machine-readable source. Remove the tracking
block. Progress is tracked via markdown checkboxes in the body only. If
programmatic progress is needed, parse the checkboxes.

- Pro: Removes one duplication layer; checkboxes are what agents actually update
- Con: Parsing checkboxes is fragile; mixed structured/unstructured
- Con: Overview still duplicates body criteria text

### C. Make blocks the single source; generate markdown sections

The overview and tracking blocks become the single source of truth for criteria,
tasks, risks. The markdown body sections (§3, §4, §7, §8) are either removed or
auto-generated from the blocks by tooling.

- Pro: Single source of truth for structured data
- Con: Agents can't easily add prose detail to criteria/tasks in YAML
- Con: Requires rendering tooling that doesn't exist
- Con: YAML is a poor format for rich task detail

### D. Reduce template to frontmatter + body only

Strip both blocks. Frontmatter carries identity/status/lifecycle. Markdown body
carries everything else in human-readable form. Accept that phase data is not
machine-readable beyond identity and status.

- Pro: Simplest; eliminates all duplication; matches how agents actually work
- Con: Loses all machine-readable phase data beyond frontmatter
- Con: `show delta` phase summaries would need to parse markdown or lose detail
- Con: Programmatic progress tracking becomes impossible without parsing

### E. Hybrid: frontmatter-enriched + body only

Extend frontmatter with `objective:`, `plan:`, `delta:` (already in the schema
as optional fields). Drop both blocks. Body carries criteria, tasks, detail.

- Pro: Machine-readable identity + objective + lineage in frontmatter; detail in body
- Con: Criteria/progress not machine-readable
- Observation: This is essentially what agents produce when they hand-craft
  phases (DE-096 pattern) — which is the format agents naturally gravitate toward

## When to revisit

- When IMPR-021 (PhaseRegistry) is implemented — the registry's data needs
  determine which representations matter
- When agents consistently fail to maintain block/body sync despite DE-104's
  improved skill guidance
- When programmatic phase progress reporting becomes a requested feature
- When the template is next revised for any reason

## Recommendation

Direction D or E is likely correct for this project's current maturity. The
blocks were designed for a tooling future that hasn't arrived. Agents work from
the markdown body. The blocks create maintenance burden that directly causes the
drift DE-104 is fixing.

However, this is a structural change with broad impact — every existing phase
sheet, the `create_phase()` renderer, `show delta` formatters, and the
`artifacts.py` phase discovery code all depend on the current structure. It
should be a deliberate delta with proper design, not a drive-by simplification.
