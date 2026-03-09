"""Pure formatting functions for relation references.

Receives pre-collected ``list[ReferenceHit]`` — no business logic or artifact
access.  Callers call ``collect_references()`` and pass the result.

Design reference: DR-085 §5.6, R4.
"""

from __future__ import annotations

from supekku.scripts.lib.relations.query import ReferenceHit


def format_refs_count(refs: list[ReferenceHit]) -> str:
  """Format total reference count for table column.

  Returns e.g. ``"3 refs"``, ``"1 ref"``, or ``""`` when empty.
  """
  n = len(refs)
  if n == 0:
    return ""
  return f"{n} ref{'s' if n != 1 else ''}"


def format_refs_tsv(refs: list[ReferenceHit]) -> str:
  """Format all references as ``source.detail:target`` pairs for TSV.

  Returns e.g. ``"relation.implements:PROD-010,context_input.issue:IMPR-006"``.
  Empty detail omits the dot: ``"relation:X"``.
  """
  parts: list[str] = []
  for ref in refs:
    prefix = f"{ref.source}.{ref.detail}" if ref.detail else ref.source
    parts.append(f"{prefix}:{ref.target}")
  return ",".join(parts)


__all__ = [
  "format_refs_count",
  "format_refs_tsv",
]
