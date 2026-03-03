"""Frontmatter compaction using FieldMetadata persistence annotations.

Pure function that strips default/derived fields from frontmatter data
based on BlockMetadata field classifications. See DR-036 §7 (DEC-036-004)
and phase-01 §10.5 for compaction semantics.
"""

from __future__ import annotations

from typing import Any

from supekku.scripts.lib.blocks.metadata import BlockMetadata

_VALID_MODES = frozenset({"compact", "full"})


def compact_frontmatter(
  data: dict[str, Any],
  metadata: BlockMetadata,
  mode: str = "compact",
) -> dict[str, Any]:
  """Remove default/derived fields from frontmatter data.

  Applies persistence semantics per field classification:
    - canonical: always kept
    - derived: omitted in compact mode
    - optional: omitted when absent, None, or equal to default_value
    - default-omit: omitted when equal to default_value

  Fields present in data but absent from metadata pass through unchanged.

  Args:
    data: Frontmatter dict to compact.
    metadata: BlockMetadata with field persistence annotations.
    mode: "compact" (default) strips per rules; "full" preserves everything.

  Returns:
    New dict with omitted fields removed. Input is not mutated.

  Raises:
    ValueError: If mode is not "compact" or "full".
  """
  if mode not in _VALID_MODES:
    msg = f"Invalid compaction mode: {mode!r} (expected 'compact' or 'full')"
    raise ValueError(msg)

  if mode == "full":
    return dict(data)

  result: dict[str, Any] = {}
  for key, value in data.items():
    field_meta = metadata.fields.get(key)

    # Unknown field — pass through
    if field_meta is None:
      result[key] = value
      continue

    if _should_keep(field_meta.persistence, value, field_meta.default_value):
      result[key] = value

  return result


def _should_keep(
  persistence: str,
  value: Any,
  default_value: Any,
) -> bool:
  """Decide whether a field should be kept during compaction."""
  if persistence == "canonical":
    return True

  if persistence == "derived":
    return False

  if persistence == "optional":
    # Omit when absent (caller won't have it in data), None, or equal to default
    if value is None:
      return False
    return not (default_value is not None and value == default_value)

  if persistence == "default-omit":
    # Omit only when equal to default_value
    return value != default_value

  # Unknown persistence — keep (defensive)
  return True


__all__ = [
  "compact_frontmatter",
]
