"""Search index builder — flattens registry records to a searchable surface.

Self-contained: instantiates its own registries via ``_REGISTRY_FACTORIES``.
No dependency on :class:`ArtifactSnapshot`.

Design reference: DR-087 DEC-087-01, DEC-087-05.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from supekku.scripts.lib.core.artifact_view import (
  _REGISTRY_FACTORIES,
  ArtifactEntry,
  ArtifactType,
  adapt_record,
)
from supekku.scripts.lib.relations.query import collect_references

logger = logging.getLogger(__name__)

# Field name constants for searchable_fields keys (POL-002).
FIELD_ID = "id"
FIELD_TITLE = "title"
FIELD_STATUS = "status"

# Frontmatter attributes extracted from raw registry records.
# Tags are handled separately (per-tag entries).
_SCALAR_ATTRS = ("kind", "slug", "category", "c4_level")
_LIST_ATTR = "tags"


@dataclass(frozen=True)
class SearchEntry:
  """A single searchable artifact with flattened fields and relation targets.

  Attributes:
    entry: The normalised view model for display and navigation.
    searchable_fields: ``field_name -> text`` mapping for the scorer.
    relation_targets: Forward-referenced artifact IDs for lower-weight matching.
  """

  entry: ArtifactEntry
  searchable_fields: dict[str, str]
  relation_targets: tuple[str, ...]


def build_search_index(*, root: Path) -> list[SearchEntry]:
  """Build a search index from fresh registry instances.

  Iterates all artifact types, instantiates each registry, calls
  ``collect()``, and flattens records into :class:`SearchEntry` values.

  Returns:
    List of search entries covering all loadable artifact types.
  """
  entries: list[SearchEntry] = []
  for art_type in ArtifactType:
    factory = _REGISTRY_FACTORIES.get(art_type)
    if factory is None:
      continue
    try:
      registry = factory(root)
      records = registry.collect()
    except Exception:  # noqa: BLE001  # pylint: disable=broad-exception-caught
      logger.debug("Skipping %s: registry load failed", art_type.value, exc_info=True)
      continue
    for _record_id, record in records.items():
      try:
        ae = adapt_record(record, art_type)
      except Exception:  # noqa: BLE001  # pylint: disable=broad-exception-caught
        logger.debug(
          "Skipping record in %s: adapt failed",
          art_type.value,
          exc_info=True,
        )
        continue
      fields = _extract_searchable_fields(ae, record)
      targets = _extract_relation_targets(record)
      entries.append(
        SearchEntry(
          entry=ae,
          searchable_fields=fields,
          relation_targets=targets,
        )
      )
  return entries


def _extract_searchable_fields(ae: ArtifactEntry, record: Any) -> dict[str, str]:
  """Flatten record attributes into a scorer-friendly dict."""
  fields: dict[str, str] = {
    FIELD_ID: ae.id,
    FIELD_TITLE: ae.title,
    FIELD_STATUS: ae.status,
  }
  # Scalar frontmatter attributes.
  for attr in _SCALAR_ATTRS:
    val = getattr(record, attr, None)
    if val is not None and val != "":
      fields[attr] = str(val)
  # Per-tag entries for correct per-tag scoring.
  tag_list = getattr(record, _LIST_ATTR, None)
  if isinstance(tag_list, list):
    for i, tag in enumerate(tag_list):
      tag_str = str(tag).strip()
      if tag_str:
        fields[f"tag.{i}"] = tag_str
  return fields


def _extract_relation_targets(record: Any) -> tuple[str, ...]:
  """Collect forward-referenced artifact IDs via the relation query layer."""
  try:
    return tuple(hit.target for hit in collect_references(record))
  except Exception:  # noqa: BLE001  # pylint: disable=broad-exception-caught
    return ()
