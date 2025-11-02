"""Frontmatter metadata registry.

This module provides metadata definitions for frontmatter validation across
all artifact kinds. It follows the metadata-driven validation pattern
established in Phases 1-5 for YAML block validators.
"""

from __future__ import annotations

from supekku.scripts.lib.blocks.metadata import BlockMetadata

from .audit import AUDIT_FRONTMATTER_METADATA
from .base import BASE_FRONTMATTER_METADATA
from .delta import DELTA_FRONTMATTER_METADATA
from .design_revision import DESIGN_REVISION_FRONTMATTER_METADATA
from .issue import ISSUE_FRONTMATTER_METADATA
from .plan import PLAN_FRONTMATTER_METADATA
from .policy import POLICY_FRONTMATTER_METADATA
from .problem import PROBLEM_FRONTMATTER_METADATA
from .prod import PROD_FRONTMATTER_METADATA
from .requirement import REQUIREMENT_FRONTMATTER_METADATA
from .risk import RISK_FRONTMATTER_METADATA
from .spec import SPEC_FRONTMATTER_METADATA
from .standard import STANDARD_FRONTMATTER_METADATA
from .verification import VERIFICATION_FRONTMATTER_METADATA

FRONTMATTER_METADATA_REGISTRY: dict[str, BlockMetadata] = {
  "base": BASE_FRONTMATTER_METADATA,
  "spec": SPEC_FRONTMATTER_METADATA,
  "prod": PROD_FRONTMATTER_METADATA,
  "delta": DELTA_FRONTMATTER_METADATA,
  "design_revision": DESIGN_REVISION_FRONTMATTER_METADATA,
  "policy": POLICY_FRONTMATTER_METADATA,
  "standard": STANDARD_FRONTMATTER_METADATA,
  "verification": VERIFICATION_FRONTMATTER_METADATA,
  "problem": PROBLEM_FRONTMATTER_METADATA,
  "risk": RISK_FRONTMATTER_METADATA,
  "requirement": REQUIREMENT_FRONTMATTER_METADATA,
  "issue": ISSUE_FRONTMATTER_METADATA,
  "audit": AUDIT_FRONTMATTER_METADATA,
  "plan": PLAN_FRONTMATTER_METADATA,
  "phase": PLAN_FRONTMATTER_METADATA,  # Shared schema
  "task": PLAN_FRONTMATTER_METADATA,  # Shared schema
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
  "AUDIT_FRONTMATTER_METADATA",
  "BASE_FRONTMATTER_METADATA",
  "DELTA_FRONTMATTER_METADATA",
  "DESIGN_REVISION_FRONTMATTER_METADATA",
  "ISSUE_FRONTMATTER_METADATA",
  "PLAN_FRONTMATTER_METADATA",
  "POLICY_FRONTMATTER_METADATA",
  "PROBLEM_FRONTMATTER_METADATA",
  "PROD_FRONTMATTER_METADATA",
  "REQUIREMENT_FRONTMATTER_METADATA",
  "RISK_FRONTMATTER_METADATA",
  "SPEC_FRONTMATTER_METADATA",
  "STANDARD_FRONTMATTER_METADATA",
  "VERIFICATION_FRONTMATTER_METADATA",
  "FRONTMATTER_METADATA_REGISTRY",
  "get_frontmatter_metadata",
]
