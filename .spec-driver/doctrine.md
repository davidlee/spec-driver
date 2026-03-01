# Project doctrine (escape hatch)

This file is intentionally short and is loaded by skills at specific “hook points”
(boot/preflight/new-card/brainstorm/plan/notes/handover) to apply project-specific
conventions without forking vendor-managed skills.

## Conventions

- Card IDs: `T123-*` in `kanban/{backlog|next|doing|finishing|done}/`
- Design docs: `doc/artefacts/T123-*.md`
- Plans: `doc/plans/T123-*.md`

## Preferences for agents

- Prefer cards for low-ceremony operational work.
- Use deltas/IPs when we explicitly opt into higher ceremony for a piece of work.

