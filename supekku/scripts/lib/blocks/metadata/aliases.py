"""Field-VALUE alias normalisation for read-time tolerance (DE-137 / DEC-137-23).

Loaders call `normalize_field(kind, field_name, value)` to canonicalise a
field value via the metadata-declared alias maps. This is the
loader-default tolerant path; strictness gating is the validator's
concern (see ``validator.MetadataValidator.validate``).

Behaviour:

- Case-folds and strips the input string (preserving the legacy
  ``normalize_status`` semantics so callers see no regression on
  ``"DONE"`` / ``"  done  "`` style inputs).
- Returns the normalised value unchanged if the kind has no metadata,
  the field has no metadata, or no alias matches.
- Permanent ``FieldMetadata.aliases`` win over ``tolerated_aliases``;
  matching either returns the canonical value.
"""

from __future__ import annotations

from typing import Any

from supekku.scripts.lib.core.frontmatter_metadata import (
  FRONTMATTER_METADATA_REGISTRY,
)


def normalize_field(kind: str, field_name: str, value: Any) -> Any:
  """Return the canonical value for ``value`` on ``kind.field_name``.

  Non-string values pass through unchanged. Strings are lower-cased and
  whitespace-stripped before alias lookup.
  """
  if not isinstance(value, str):
    return value

  normalised = value.lower().strip()
  meta = FRONTMATTER_METADATA_REGISTRY.get(kind)
  if meta is None or field_name not in meta.fields:
    return normalised

  field_meta = meta.fields[field_name]
  aliases = field_meta.aliases or {}
  if normalised in aliases:
    return aliases[normalised]

  tolerated = field_meta.tolerated_aliases or {}
  if normalised in tolerated:
    return tolerated[normalised].canonical

  return normalised


__all__ = ["normalize_field"]
