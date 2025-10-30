"""Utilities for managing relationships between specifications and changes."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from .frontmatter_schema import Relation
from .spec_utils import dump_markdown_file, load_markdown_file

RelationDict = dict[str, Any]


def _ensure_relations(frontmatter: dict[str, Any]) -> list[RelationDict]:
    value = frontmatter.setdefault("relations", [])
    if not isinstance(value, list):
        raise TypeError("frontmatter['relations'] must be a list of mapping objects")
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise TypeError(f"frontmatter['relations'][{index}] must be a mapping")
        if "type" not in item or "target" not in item:
            raise ValueError(
                f"frontmatter['relations'][{index}] missing required keys 'type'/'target'",
            )
    return value  # type: ignore[return-value]


def list_relations(path: Path | str) -> list[Relation]:
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
    frontmatter, body = load_markdown_file(path)
    relations = _ensure_relations(frontmatter)

    relation_type = relation_type.strip()
    target = target.strip()
    if not relation_type or not target:
        raise ValueError("relation_type and target must be non-empty strings")

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
    frontmatter, body = load_markdown_file(path)
    relations = _ensure_relations(frontmatter)

    relation_type = relation_type.strip()
    target = target.strip()
    if not relation_type or not target:
        raise ValueError("relation_type and target must be non-empty strings")

    initial_len = len(relations)
    relations[:] = [
        rel
        for rel in relations
        if not (
            str(rel.get("type")) == relation_type and str(rel.get("target")) == target
        )
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
