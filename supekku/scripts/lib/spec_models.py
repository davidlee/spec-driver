"""Data models for specifications and related entities."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from pathlib import Path

  from .core.frontmatter_schema import FrontmatterValidationResult


@dataclass(frozen=True)
class Spec:
  """In-memory representation of a specification artefact."""

  id: str
  path: Path
  frontmatter: FrontmatterValidationResult
  body: str

  @property
  def packages(self) -> list[str]:
    """Return list of package paths associated with this spec."""
    packages = self.frontmatter.data.get("packages", [])
    if isinstance(packages, Iterable) and not isinstance(packages, (str, bytes)):
      return [str(item) for item in packages]
    return []

  @property
  def slug(self) -> str:
    """Return URL-friendly slug for this spec."""
    return str(self.frontmatter.data.get("slug", ""))

  @property
  def name(self) -> str:
    """Return human-readable name for this spec."""
    return str(self.frontmatter.data.get("name", self.id))

  @property
  def kind(self) -> str:
    """Return the kind/type of this spec (e.g., 'spec', 'prod')."""
    return str(self.frontmatter.data.get("kind", ""))


__all__ = ["Spec"]
