"""Specification domain - managing technical and product specifications.

This package handles all specification-related functionality:
- registry: SpecRegistry for discovering and accessing specs
- models: Spec dataclass and related models
- index: SpecIndexBuilder for building spec indices
- creation: Creating new specs from templates

NOTE: Block parsing (formerly specs/blocks.py) moved to:
  supekku/scripts/lib/blocks/relationships.py
  supekku/scripts/lib/blocks/verification.py

Block parsing is INFRASTRUCTURE (format extraction), not domain logic.
Domain logic that USES blocks stays here in specs/.
"""

from __future__ import annotations

# Compatibility re-export for blocks
from supekku.scripts.lib.blocks.relationships import (
  RELATIONSHIPS_MARKER as SPEC_RELATIONSHIPS_MARKER,
)
from supekku.scripts.lib.blocks.relationships import (
  RelationshipsBlock as SpecRelationshipsBlock,
)
from supekku.scripts.lib.blocks.relationships import (
  extract_relationships as extract_spec_relationships,
)
from supekku.scripts.lib.blocks.relationships import (
  load_relationships_from_file as load_spec_relationships,
)
from supekku.scripts.lib.specs.package_utils import (
  find_all_leaf_packages,
  find_package_for_file,
  is_leaf_package,
  validate_package_path,
)

__all__ = [
  "SPEC_RELATIONSHIPS_MARKER",
  "SpecRelationshipsBlock",
  "extract_spec_relationships",
  "find_all_leaf_packages",
  "find_package_for_file",
  "is_leaf_package",
  "load_spec_relationships",
  "validate_package_path",
]
