---
id: NOTE-backlog-model
slug: backlog-model
name: Backlog Model Overview
created: 2024-06-08
updated: 2024-06-08
status: draft
kind: note
aliases:
  - Backlog
  - Backlog Overview
---

# Backlog Model Overview

The backlog captures pending work against the systems of truth (PROD, SPEC, Constitution). It is composed of linked artefacts:

- **Problems (`kind: problem`)**: crisp statements of undesirable states or user pains, with evidence and success criteria. Often the anchor for product or strategic change.
- **Issues (`kind: issue`)**: actionable gaps or defects threatening existing truths. Issues carry metadata (categories, severity) and reference the problem(s) or requirements they affect.
- **Ideas (`kind: issue`, category `idea`)**: proposed improvements or opportunities, usually tied to a problem statement.
- **Deltas / Design Revisions**: execution artefacts spawned when problems/issues demand changes to PROD/SPEC.

Prioritisation lives in dedicated Markdown lists (e.g. `backlog/backlog.md`). The list order is canonical; scripts ensure new artefacts get appended, while humans/agents reorder lines to reflect priority. Impact/severity metadata helps triage but does not dictate ordering.

**Workflow:**
1. Capture a problem statement when a new pain/opportunity emerges.
2. Record issues/ideas that reference the problem and the affected requirements or decisions.
3. Use prioritised lists to decide sequencing.
4. Promote issues into Deltas and Design Revisions as scope clarifies.
5. Update backlog entries as deltas close gaps; upstream learnings into PROD/SPEC/Constitution where needed.
