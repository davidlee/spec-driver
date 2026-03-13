---
id: mem.fact.backlog.relations-in-frontmatter
name: BacklogItem relations live in frontmatter dict
kind: memory
status: active
memory_type: fact
updated: '2026-03-14'
verified: '2026-03-14'
confidence: high
tags:
- backlog
- relations
- gotcha
summary: BacklogItem.relations is not a dataclass field. Relations are stored in frontmatter
  dict, so getattr returns None. Use frontmatter.get('relations', []).
scope:
  paths:
  - supekku/scripts/lib/backlog/models.py
  - supekku/scripts/lib/relations/query.py
  globs:
  - supekku/scripts/lib/backlog/**
provenance:
  sources:
  - kind: code
    ref: supekku/scripts/lib/backlog/models.py
  - kind: delta
    ref: DE-090
---

# BacklogItem relations live in frontmatter dict

`BacklogItem` (in `backlog/models.py`) is a dataclass with `frontmatter: dict[str, Any]`.
Unlike `ChangeArtifact` or `Spec`, it does **not** have a `.relations` attribute as a
dataclass field.

## Sharp edge

- `getattr(backlog_item, "relations", None)` → `None`
- `_collect_from_relations()` in `relations/query.py` uses getattr → misses BacklogItem relations

## Correct access

- `backlog_item.frontmatter.get("relations", [])` → list of relation dicts
- `_collect_from_backlog_fields()` in `relations/query.py` handles this correctly,
  including frontmatter relations with `source="relation"` provenance.

## Also in frontmatter (not dataclass fields)

- `linked_deltas` → `frontmatter.get("linked_deltas", [])`
- `related_requirements` → `frontmatter.get("related_requirements", [])`
