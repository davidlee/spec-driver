---
id: ISSUE-062
name: Consolidate revision.change block rendering into create_revision
created: "2026-05-30"
updated: "2026-05-30"
status: open  # one of: in-progress | open | resolved | triaged
kind: issue  # one of: audit | delta | design_revision | issue | memory | phase | plan | policy | problem | prod | requirement | risk | spec | standard | task | verification
categories: []
severity: p3  # one of: p1 | p2 | p3 | p4
impact: user  # one of: user | systemic | process
---

# Consolidate revision.change block rendering into create_revision

## Problem

Two code paths render `supekku:revision.change@v1` blocks:

1. `changes/revision_creation.py::create_revision` — emits the canonical block via
   `blocks/revision.render_revision_change_block` (DE-142, action `modify`, no lifecycle).
2. `changes/completion.py::_render_revision_change_block` — a second, richer renderer
   (delta lifecycle: `introduced_by`/`implemented_by`/`status`) used by
   `create_completion_revision` for the `complete delta` path.

Because both render a block, DE-142 gated the completion path with a
`render_change_block=False` flag (DEC-142-15) so `create_revision` skips its block and
`create_completion_revision` remains the sole author. This is a stopgap: two renderers
violate POL-001 (DRY) and ADR-008 (single source of truth for block structure).

## Desired end state

`create_revision` is the single canonical block author. `create_completion_revision`
passes rich requirement data (with lifecycle) into `create_revision` and drops its own
`_render_revision_change_block` + manual append. Remove the `render_change_block` flag
once the second renderer is gone.

## Provenance

- DE-142 P04 group C; notes.md DEC-142-14/15.
- `changes/revision_creation.py`, `changes/completion.py:46,130,209`.

