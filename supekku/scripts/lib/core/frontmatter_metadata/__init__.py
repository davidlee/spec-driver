"""Frontmatter metadata registry.

This module provides metadata definitions for frontmatter validation across
all artifact kinds. It follows the metadata-driven validation pattern
established in Phases 1-5 for YAML block validators.
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata

from .base import BASE_FRONTMATTER_METADATA
from .delta import DELTA_FRONTMATTER_METADATA
from .spec import SPEC_FRONTMATTER_METADATA

FRONTMATTER_METADATA_REGISTRY: dict[str, BlockMetadata] = {
  "base": BASE_FRONTMATTER_METADATA,
  "spec": SPEC_FRONTMATTER_METADATA,
  "delta": DELTA_FRONTMATTER_METADATA,
}


def get_frontmatter_metadata(kind: str | None = None) -> BlockMetadata:
  """Get metadata for frontmatter kind.

  Args:
    kind: Artifact kind (spec, delta, requirement, etc.) or None for base

  Returns:
    BlockMetadata for the specified kind, or base metadata if kind not found
  """
  if kind is None:
    return BASE_FRONTMATTER_METADATA
  return FRONTMATTER_METADATA_REGISTRY.get(kind, BASE_FRONTMATTER_METADATA)


__all__ = [
  "BASE_FRONTMATTER_METADATA",
  "SPEC_FRONTMATTER_METADATA",
  "DELTA_FRONTMATTER_METADATA",
  "FRONTMATTER_METADATA_REGISTRY",
  "get_frontmatter_metadata",
]
