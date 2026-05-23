"""Metadata definition for spec requirements blocks.

Defines the BlockMetadata schema for supekku:spec.requirements@v1,
plus the canonical validation wrapper validate_spec_requirements()
(DEC-140-16).
"""

from __future__ import annotations

from typing import Any

from supekku.scripts.lib.blocks.metadata import (
  BlockMetadata,
  FieldMetadata,
  MetadataValidator,
  ToleratedAlias,
)
from supekku.scripts.lib.requirements.lifecycle import REQUIREMENT_STATUSES

REQUIREMENTS_SCHEMA = "supekku.spec.requirements"
REQUIREMENTS_VERSION = 1

REQUIREMENT_ID_PATTERN = r"^(FR|NF)-\d{3}$"
SPEC_OWNER_PATTERN = r"^(SPEC|PROD)-\d{3,}$"

REQUIREMENT_KINDS = ["functional", "non-functional"]

SPEC_REQUIREMENTS_METADATA = BlockMetadata(
  version=REQUIREMENTS_VERSION,
  schema_id=REQUIREMENTS_SCHEMA,
  description="Structured requirements within spec/product artifacts",
  fields={
    "schema": FieldMetadata(
      type="const",
      const_value=REQUIREMENTS_SCHEMA,
      required=True,
      description=f"Schema identifier (must be '{REQUIREMENTS_SCHEMA}')",
    ),
    "version": FieldMetadata(
      type="const",
      const_value=REQUIREMENTS_VERSION,
      required=True,
      description=f"Schema version (must be {REQUIREMENTS_VERSION})",
    ),
    "spec": FieldMetadata(
      type="string",
      required=True,
      pattern=SPEC_OWNER_PATTERN,
      description="Owning spec/product ID (e.g. SPEC-100, PROD-004)",
    ),
    "requirements": FieldMetadata(
      type="array",
      required=True,
      min_items=0,
      description="List of requirement entries",
      items=FieldMetadata(
        type="object",
        description="A single requirement entry",
        properties={
          "id": FieldMetadata(
            type="string",
            required=True,
            pattern=REQUIREMENT_ID_PATTERN,
            description="Requirement ID (e.g. FR-001, NF-002)",
          ),
          "title": FieldMetadata(
            type="string",
            required=True,
            description="Short human-readable title",
          ),
          "lifecycle": FieldMetadata(
            type="enum",
            required=True,
            enum_values=sorted(REQUIREMENT_STATUSES),
            description="Requirement lifecycle status",
          ),
          "kind": FieldMetadata(
            type="enum",
            required=True,
            enum_values=REQUIREMENT_KINDS,
            description="Requirement kind (functional or non-functional)",
            tolerated_aliases={
              "FR": ToleratedAlias(
                canonical="functional",
                sunset_after="DE-140",
                rationale="Shorthand alias; use canonical 'functional'",
              ),
              "NF": ToleratedAlias(
                canonical="non-functional",
                sunset_after="DE-140",
                rationale="Shorthand alias; use canonical 'non-functional'",
              ),
              "NFR": ToleratedAlias(
                canonical="non-functional",
                sunset_after="DE-140",
                rationale="Shorthand alias; use canonical 'non-functional'",
              ),
            },
          ),
          "category": FieldMetadata(
            type="string",
            required=False,
            description="Classification category",
          ),
          "description": FieldMetadata(
            type="string",
            required=True,
            description="Requirement description",
          ),
          "acceptance_criteria": FieldMetadata(
            type="array",
            required=True,
            min_items=0,
            description="Testable acceptance criteria",
            items=FieldMetadata(
              type="string",
              description="A single acceptance criterion",
            ),
          ),
          "tags": FieldMetadata(
            type="array",
            required=False,
            min_items=0,
            description="Classification tags",
            items=FieldMetadata(
              type="string",
              description="A tag",
            ),
          ),
        },
      ),
    ),
  },
  examples=[
    {
      "schema": REQUIREMENTS_SCHEMA,
      "version": REQUIREMENTS_VERSION,
      "spec": "PROD-004",
      "requirements": [
        {
          "id": "FR-001",
          "title": "Metadata-driven validation",
          "lifecycle": "active",
          "kind": "functional",
          "category": "core",
          "description": (
            "The system must validate frontmatter against "
            "declarative metadata definitions."
          ),
          "acceptance_criteria": [
            "All registered kinds validate via metadata",
            "Errors are clear and actionable",
          ],
          "tags": ["validation", "metadata"],
        },
      ],
    }
  ],
)

SPEC_REQUIREMENTS_VALIDATOR = MetadataValidator(SPEC_REQUIREMENTS_METADATA)

_KIND_PREFIX_MAP = {
  "functional": "FR",
  "non-functional": "NF",
}


def _canonicalize_kind(kind_value: str) -> str:
  """Resolve tolerated aliases to canonical kind value."""
  tolerated = SPEC_REQUIREMENTS_METADATA.fields["requirements"].items
  assert tolerated is not None
  kind_field = tolerated.properties["kind"]  # type: ignore[union-attr]
  for alias, entry in (kind_field.tolerated_aliases or {}).items():
    if kind_value == alias:
      return entry.canonical
  return kind_value


def _check_duplicate_ids(
  requirements: list[Any],
) -> list[str]:
  """Return errors for duplicate requirement IDs (DEC-140-15)."""
  errors: list[str] = []
  seen: set[str] = set()
  for idx, entry in enumerate(requirements):
    if not isinstance(entry, dict):
      continue
    req_id = entry.get("id")
    if req_id is None:
      continue
    if req_id in seen:
      errors.append(
        f"requirements[{idx}].id: duplicate requirement ID '{req_id}'"
      )
    else:
      seen.add(req_id)
  return errors


def _check_kind_prefix_invariant(
  requirements: list[Any],
) -> list[str]:
  """Return errors for ID prefix / kind mismatches (DEC-140-10)."""
  errors: list[str] = []
  for idx, entry in enumerate(requirements):
    if not isinstance(entry, dict):
      continue
    req_id = entry.get("id", "")
    kind_raw = entry.get("kind", "")
    if not req_id or not kind_raw:
      continue
    kind = _canonicalize_kind(kind_raw)
    expected = _KIND_PREFIX_MAP.get(kind)
    if expected is None:
      continue
    actual = req_id.split("-")[0] if "-" in req_id else ""
    if actual != expected:
      errors.append(
        f"requirements[{idx}]: ID prefix '{actual}' "
        f"does not match kind '{kind}' (expected '{expected}-')"
      )
  return errors


def validate_spec_requirements(
  block: Any,
  *,
  spec_id: str | None = None,
  strict: bool = False,
  accept_tolerated: bool = True,
) -> list[str]:
  """Canonical validation entry point (DEC-140-16).

  Composes: schema validation + cross-field invariant + duplicate ID
  check + optional spec_id cross-validation.
  """
  data = block.data if hasattr(block, "data") else block
  errors = [
    str(err)
    for err in SPEC_REQUIREMENTS_VALIDATOR.validate(
      data, strict=strict, accept_tolerated=accept_tolerated
    )
  ]

  requirements = data.get("requirements")
  if not isinstance(requirements, list):
    return errors

  errors.extend(_check_duplicate_ids(requirements))
  errors.extend(_check_kind_prefix_invariant(requirements))

  spec_value = str(data.get("spec", ""))
  if spec_id and spec_value and spec_value != spec_id:
    errors.append(
      f"spec field '{spec_value}' does not match expected '{spec_id}'"
    )

  return errors


__all__ = [
  "REQUIREMENT_ID_PATTERN",
  "REQUIREMENT_KINDS",
  "REQUIREMENTS_SCHEMA",
  "REQUIREMENTS_VERSION",
  "SPEC_OWNER_PATTERN",
  "SPEC_REQUIREMENTS_METADATA",
  "SPEC_REQUIREMENTS_VALIDATOR",
  "validate_spec_requirements",
]
