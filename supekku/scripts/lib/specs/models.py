"""Data models for specifications and related entities."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
  from pathlib import Path

  from supekku.scripts.lib.core.frontmatter_schema import FrontmatterValidationResult


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

  @property
  def status(self) -> str:
    """Return the status of this spec (e.g., 'draft', 'active')."""
    return str(self.frontmatter.data.get("status", "draft"))

  @property
  def informed_by(self) -> list[str]:
    """Return list of ADR IDs that inform this spec."""
    informed_by = self.frontmatter.data.get("informed_by", [])
    if isinstance(informed_by, Iterable) and not isinstance(informed_by, (str, bytes)):
      return [str(item) for item in informed_by]
    return []

  @property
  def tags(self) -> list[str]:
    """Return list of tags for this spec."""
    tags = self.frontmatter.data.get("tags", [])
    if isinstance(tags, Iterable) and not isinstance(tags, (str, bytes)):
      return [str(item) for item in tags]
    return []

  def to_dict(self, root: Path) -> dict[str, str | list[str]]:
    """Convert to dictionary for JSON serialization.

    Args:
        root: Repository root path for relativizing file paths

    Returns:
        Dictionary representation suitable for JSON serialization

    """
    data: dict[str, Any] = {
      "id": self.id,
      "slug": self.slug,
      "name": self.name,
      "kind": self.kind,
      "status": self.status,
      "path": str(self.path.relative_to(root)) if root else str(self.path),
    }

    # Add packages if present
    if self.packages:
      data["packages"] = self.packages

    return data


__all__ = ["Spec"]
