---
id: mem.fact.cli.typer-group-subclass
name: Typer custom Group must subclass TyperGroup
kind: memory
status: active
memory_type: fact
created: '2026-03-08'
updated: '2026-03-08'
tags: [cli, typer]
summary: Typer cls= parameter requires subclass of typer.core.TyperGroup, not click.Group. Asserted at app construction time.
verified: '2026-03-08'
review_by: '2027-03-08'
confidence: high
scope:
  globs: [supekku/cli/**]
provenance:
  sources:
  - kind: commit
    ref: e93bc5d
    note: DE-063 P02 — discovered during implementation
---

# Typer custom Group must subclass TyperGroup

When passing `cls=` to `typer.Typer()`, the class **must** inherit from
`typer.core.TyperGroup`, not `click.Group`. Typer asserts this at app
construction time with:

> `AssertionError: <class 'Foo'> should be a subclass of <class 'typer.core.TyperGroup'>`

Used in `InferringGroup` (`supekku/cli/common.py`) for ID inference in
show/view commands. See [[DE-063]].
