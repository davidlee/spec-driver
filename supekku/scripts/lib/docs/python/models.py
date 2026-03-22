"""Data models for Python documentation generation API."""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, ConfigDict


class VariantType(Enum):
  """Documentation variant types."""

  PUBLIC = "public"
  ALL = "all"
  TESTS = "tests"


class VariantSpec(BaseModel):
  """Specification for a documentation variant."""

  model_config = ConfigDict(extra="ignore")

  variant_type: VariantType
  include_private: bool = False
  include_tests: bool = False

  @classmethod
  def public(cls) -> VariantSpec:
    """Create PUBLIC variant spec."""
    return cls(
      variant_type=VariantType.PUBLIC,
      include_private=False,
      include_tests=False,
    )

  @classmethod
  def all_symbols(cls) -> VariantSpec:
    """Create ALL variant spec."""
    return cls(variant_type=VariantType.ALL, include_private=True, include_tests=False)

  @classmethod
  def tests(cls) -> VariantSpec:
    """Create TESTS variant spec."""
    return cls(variant_type=VariantType.TESTS, include_private=True, include_tests=True)


class DocResult(BaseModel):
  """Result of documentation generation for a single file/variant combination."""

  model_config = ConfigDict(extra="ignore")

  variant: str
  path: Path
  hash: str
  status: str  # "created", "changed", "unchanged", "error"
  module_identifier: str  # normalized module path (e.g. "src.module")
  error_message: str | None = None

  @property
  def success(self) -> bool:
    """Whether generation was successful."""
    return self.status != "error"
