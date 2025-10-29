"""Utilities for parsing structured spec YAML blocks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import re

import yaml

RELATIONSHIPS_MARKER = "supekku:spec.relationships@v1"
RELATIONSHIPS_SCHEMA = "supekku.spec.relationships"
RELATIONSHIPS_VERSION = 1


@dataclass(frozen=True)
class RelationshipsBlock:
    """Parsed YAML block containing specification relationships."""

    raw_yaml: str
    data: dict[str, Any]


class RelationshipsBlockValidator:
    """Validator for specification relationships blocks."""

    def validate(
        self, block: RelationshipsBlock, *, spec_id: str | None = None
    ) -> list[str]:
        errors: list[str] = []
        data = block.data
        if data.get("schema") != RELATIONSHIPS_SCHEMA:
            errors.append(
                "relationships block must declare schema supekku.spec.relationships"
            )
        if data.get("version") != RELATIONSHIPS_VERSION:
            errors.append("relationships block must declare version 1")

        spec_value = str(data.get("spec", ""))
        if not spec_value:
            errors.append("relationships block missing spec id")
        elif spec_id and spec_value != spec_id:
            errors.append(
                f"relationships block spec {spec_value} does not match expected {spec_id}"
            )

        requirements = data.get("requirements")
        if not isinstance(requirements, dict):
            errors.append("relationships requirements must be a mapping")
        else:
            for key in ("primary", "collaborators"):
                value = requirements.get(key)
                if value is None:
                    continue
                if not isinstance(value, list):
                    errors.append(f"requirements.{key} must be a list")
                    continue
                for item in value:
                    if not isinstance(item, str):
                        errors.append(f"requirements.{key} entries must be strings")

        interactions = data.get("interactions")
        if interactions is not None:
            if not isinstance(interactions, list):
                errors.append("interactions must be a list")
            else:
                for entry in interactions:
                    if not isinstance(entry, dict):
                        errors.append("interaction entries must be objects")
                        continue
                    if "type" not in entry:
                        errors.append("interaction missing type")
                    if "spec" not in entry:
                        errors.append("interaction missing spec")
        return errors


_RELATIONSHIPS_PATTERN = re.compile(
    r"```(?:yaml|yml)\s+" + re.escape(RELATIONSHIPS_MARKER) + r"\n(.*?)```", re.DOTALL
)


def extract_relationships(block: str) -> RelationshipsBlock | None:
    match = _RELATIONSHIPS_PATTERN.search(block)
    if not match:
        return None
    raw = match.group(1)
    try:
        data = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:  # pragma: no cover
        raise ValueError(f"invalid relationships YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("relationships block must parse to mapping")
    return RelationshipsBlock(raw_yaml=raw, data=data)


def load_relationships_from_file(path: Path) -> RelationshipsBlock | None:
    text = path.read_text(encoding="utf-8")
    return extract_relationships(text)


__all__ = [
    "RelationshipsBlock",
    "RelationshipsBlockValidator",
    "extract_relationships",
    "load_relationships_from_file",
    "RELATIONSHIPS_MARKER",
]
