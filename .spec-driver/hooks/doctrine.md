# Project doctrine

This file is intentionally short and is loaded by skills at specific “hook points”
(boot/preflight/new-card/brainstorm/plan/notes/handover) to apply project-specific
conventions without forking vendor-managed skills.

## Conventions

- Kanban IDs: `T123-*` in `kanban/{backlog|next|doing|finishing|done}/`
- Design docs: `doc/artefacts/T123-*.md`
- Plans: `doc/plans/T123-*.md`

## Preferences for agents

- "Card" means whatever artifact tracks active work in this project — kanban card, delta, or revision, depending on ceremony mode.
- For low-ceremony operational work, prefer kanban cards.
- Use deltas/IPs when we explicitly opt into higher ceremony for a piece of work.
- These are not competing defaults — ceremony mode determines which is primary.

