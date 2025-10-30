"""Schema definitions and validation for markdown file frontmatter."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from types import MappingProxyType
from typing import Any


class FrontmatterValidationError(ValueError):
    """Raised when frontmatter metadata fails schema validation."""


@dataclass(frozen=True)
class Relation:
    """Represents a relationship between specifications or changes."""

    type: str
    target: str
    attributes: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FrontmatterValidationResult:
    """Result of validating frontmatter against schema requirements."""

    id: str
    name: str
    slug: str
    kind: str
    status: str
    created: date
    updated: date
    owners: tuple[str, ...]
    auditers: tuple[str, ...]
    relations: tuple[Relation, ...]
    data: Mapping[str, Any]

    def dict(self) -> Mapping[str, Any]:
        """Return the validated frontmatter as an immutable mapping."""
        return self.data


def validate_frontmatter(
    frontmatter: Mapping[str, Any], *, kind: str | None = None,
) -> FrontmatterValidationResult:
    if not isinstance(frontmatter, Mapping):
        msg = "frontmatter must be a mapping of keys to values"
        raise FrontmatterValidationError(
            msg,
        )

    payload = dict(frontmatter)
    fm_kind = kind or payload.get("kind")
    if not isinstance(fm_kind, str) or not fm_kind.strip():
        msg = "frontmatter.kind is required for validation"
        raise FrontmatterValidationError(msg)

    required_fields = ("id", "name", "slug", "status", "created", "updated")
    missing = [field for field in required_fields if field not in payload]
    if missing:
        msg = f"frontmatter missing required field(s): {', '.join(sorted(missing))}"
        raise FrontmatterValidationError(
            msg,
        )

    id_value = _require_str(payload, "id")
    name_value = _require_str(payload, "name")
    slug_value = _require_str(payload, "slug")
    status_value = _require_str(payload, "status")

    created_value = _parse_iso_date(payload["created"], field_name="created")
    updated_value = _parse_iso_date(payload["updated"], field_name="updated")
    payload["created"] = created_value.isoformat()
    payload["updated"] = updated_value.isoformat()

    owners = _ensure_str_list(payload, "owners")
    auditers = _ensure_str_list(payload, "auditers")

    relations_list, relation_objs = _normalize_relations(payload)
    payload["relations"] = relations_list

    immutable_payload = MappingProxyType(payload)

    return FrontmatterValidationResult(
        id=id_value,
        name=name_value,
        slug=slug_value,
        kind=fm_kind,
        status=status_value,
        created=created_value,
        updated=updated_value,
        owners=tuple(owners),
        auditers=tuple(auditers),
        relations=relation_objs,
        data=immutable_payload,
    )


def _require_str(payload: MutableMapping[str, Any], field: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        msg = f"frontmatter.{field} must be a non-empty string"
        raise FrontmatterValidationError(
            msg,
        )
    return value


def _parse_iso_date(value: Any, *, field_name: str) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            msg = f"frontmatter.{field_name} must be an ISO-8601 date string"
            raise FrontmatterValidationError(
                msg,
            ) from exc
    msg = f"frontmatter.{field_name} must be an ISO-8601 date string"
    raise FrontmatterValidationError(
        msg,
    )


def _ensure_str_list(payload: MutableMapping[str, Any], field: str) -> list[str]:
    value = payload.get(field)
    if value is None:
        payload[field] = []
        return []
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        msg = f"frontmatter.{field} must be a list of strings"
        raise FrontmatterValidationError(
            msg,
        )
    result: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            msg = f"frontmatter.{field}[{index}] must be a non-empty string"
            raise FrontmatterValidationError(
                msg,
            )
        result.append(item)
    payload[field] = list(result)
    return result


def _normalize_relations(
    payload: MutableMapping[str, Any],
) -> tuple[list[dict[str, Any]], tuple[Relation, ...]]:
    raw_relations = payload.get("relations")
    if raw_relations is None:
        return [], ()
    if not isinstance(raw_relations, Sequence) or isinstance(
        raw_relations, (str, bytes),
    ):
        msg = "frontmatter.relations must be a list of mapping objects"
        raise FrontmatterValidationError(
            msg,
        )

    normalized: list[dict[str, Any]] = []
    relation_objs: list[Relation] = []
    for index, relation in enumerate(raw_relations):
        if not isinstance(relation, Mapping):
            msg = f"frontmatter.relations[{index}] must be a mapping"
            raise FrontmatterValidationError(
                msg,
            )
        try:
            relation_type = relation["type"]
            relation_target = relation["target"]
        except KeyError as missing_key:
            msg = f"frontmatter.relations[{index}] missing required key: {missing_key.args[0]}"
            raise FrontmatterValidationError(
                msg,
            ) from None
        if not isinstance(relation_type, str) or not relation_type.strip():
            msg = f"frontmatter.relations[{index}].type must be a non-empty string"
            raise FrontmatterValidationError(
                msg,
            )
        if not isinstance(relation_target, str) or not relation_target.strip():
            msg = f"frontmatter.relations[{index}].target must be a non-empty string"
            raise FrontmatterValidationError(
                msg,
            )
        extras = {
            key: value
            for key, value in relation.items()
            if key not in {"type", "target"}
        }
        normalized_relation = {
            "type": relation_type,
            "target": relation_target,
            **extras,
        }
        normalized.append(normalized_relation)
        relation_objs.append(
            Relation(
                type=relation_type,
                target=relation_target,
                attributes=MappingProxyType(dict(extras))
                if extras
                else MappingProxyType({}),
            ),
        )
    return normalized, tuple(relation_objs)


__all__ = [
    "FrontmatterValidationError",
    "FrontmatterValidationResult",
    "Relation",
    "validate_frontmatter",
]
