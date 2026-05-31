"""Legacy re-export shim — see spec_driver.core.frontmatter_schema."""

from spec_driver.core.frontmatter_schema import (
  FrontmatterValidationError,
  FrontmatterValidationResult,
  Relation,
  validate_frontmatter,
)

__all__ = [
  "FrontmatterValidationError",
  "FrontmatterValidationResult",
  "Relation",
  "validate_frontmatter",
]
