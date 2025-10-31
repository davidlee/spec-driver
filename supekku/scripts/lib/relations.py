"""Utilities for managing relationships between specifications and changes."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Any

from .core.frontmatter_schema import Relation
from .core.spec_utils import dump_markdown_file, load_markdown_file

if TYPE_CHECKING:
  from pathlib import Path

RelationDict = dict[str, Any]


def _ensure_relations(frontmatter: dict[str, Any]) -> list[RelationDict]:
  value = frontmatter.setdefault("relations", [])
  if not isinstance(value, list):
    msg = "frontmatter['relations'] must be a list of mapping objects"
    raise TypeError(msg)
  for index, item in enumerate(value):
    if not isinstance(item, Mapping):
      msg = f"frontmatter['relations'][{index}] must be a mapping"
      raise TypeError(msg)
    if "type" not in item or "target" not in item:
      msg = f"frontmatter['relations'][{index}] missing required keys 'type'/'target'"
      raise ValueError(
        msg,
      )
  return value  # type: ignore[return-value]


def list_relations(path: Path | str) -> list[Relation]:
  """List relations from markdown file frontmatter.

  Args:
    path: Path to markdown file.

  Returns:
    List of parsed Relation objects.
  """
  frontmatter, _ = load_markdown_file(path)
  relations_raw = frontmatter.get("relations")
  if not isinstance(relations_raw, Iterable):
    return []
  result: list[Relation] = []
  for item in relations_raw:
    if not isinstance(item, Mapping):
      continue
    rel_type = str(item.get("type", "")).strip()
    target = str(item.get("target", "")).strip()
    if not rel_type or not target:
      continue
    extras = {
      key: value for key, value in item.items() if key not in {"type", "target"}
    }
    result.append(Relation(type=rel_type, target=target, attributes=dict(extras)))
  return result


def add_relation(
  path: Path | str,
  *,
  relation_type: str,
  target: str,
  **attributes: Any,
) -> bool:
  """Add a relation to markdown file frontmatter.

  Args:
    path: Path to markdown file.
    relation_type: Type of relation (e.g., "implements", "supersedes").
    target: Target identifier.
    **attributes: Additional relation attributes.

  Returns:
    True if relation was added, False if it already existed.

  Raises:
    ValueError: If relation_type or target are empty.
    TypeError: If frontmatter relations are malformed.
  """
  frontmatter, body = load_markdown_file(path)
  relations = _ensure_relations(frontmatter)

  relation_type = relation_type.strip()
  target = target.strip()
  if not relation_type or not target:
    msg = "relation_type and target must be non-empty strings"
    raise ValueError(msg)

  for existing in relations:
    if (
      str(existing.get("type")) == relation_type
      and str(existing.get("target")) == target
    ):
      return False

  new_relation: RelationDict = {"type": relation_type, "target": target}
  for key, value in attributes.items():
    if value is not None:
      new_relation[key] = value
  relations.append(new_relation)
  dump_markdown_file(path, frontmatter, body)
  return True


def remove_relation(path: Path | str, *, relation_type: str, target: str) -> bool:
  """Remove a relation from markdown file frontmatter.

  Args:
    path: Path to markdown file.
    relation_type: Type of relation to remove.
    target: Target identifier.

  Returns:
    True if relation was removed, False if it wasn't found.

  Raises:
    ValueError: If relation_type or target are empty.
    TypeError: If frontmatter relations are malformed.
  """
  frontmatter, body = load_markdown_file(path)
  relations = _ensure_relations(frontmatter)

  relation_type = relation_type.strip()
  target = target.strip()
  if not relation_type or not target:
    msg = "relation_type and target must be non-empty strings"
    raise ValueError(msg)

  initial_len = len(relations)
  relations[:] = [
    rel
    for rel in relations
    if not (str(rel.get("type")) == relation_type and str(rel.get("target")) == target)
  ]
  if len(relations) == initial_len:
    return False

  dump_markdown_file(path, frontmatter, body)
  return True


__all__ = [
  "add_relation",
  "list_relations",
  "remove_relation",
]
