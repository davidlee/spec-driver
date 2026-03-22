"""MemoryRecord model for memory artifacts."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


class MemoryRecord(BaseModel):
  """A memory artifact record parsed from frontmatter.

  Required fields: id, name, status, memory_type, path.
  All other fields are optional with safe defaults.
  """

  model_config = ConfigDict(extra="ignore")

  # Required (defaulted to empty string for permissive parsing)
  id: str = ""
  name: str = ""
  status: str = ""
  memory_type: str = ""
  path: str = ""

  # Optional dates
  created: date | None = None
  updated: date | None = None
  verified: date | None = None
  review_by: date | None = None

  # Optional scalars
  verified_sha: str | None = None
  confidence: str | None = None
  summary: str = ""

  # Optional lists
  tags: list[str] = []
  owners: list[str] = []
  requires_reading: list[str] = []
  audience: list[str] = []
  visibility: list[str] = []
  relations: list[dict[str, Any]] = []

  # Optional objects
  scope: dict[str, Any] = {}
  priority: dict[str, Any] = {}
  provenance: dict[str, Any] = {}
  links: dict[str, Any] = {}

  @field_validator("created", "updated", "verified", "review_by", mode="before")
  @classmethod
  def _coerce_date(cls, v: Any) -> date | None:
    """Coerce date-like values permissively. Returns None on bad input."""
    if v is None:
      return None
    if isinstance(v, date) and not isinstance(v, datetime):
      return v
    if isinstance(v, datetime):
      return v.date()
    if isinstance(v, str):
      for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d"):
        try:
          return datetime.strptime(v, fmt).date()
        except ValueError:
          continue
      return None
    return None

  def to_dict(self, root: Path) -> dict[str, Any]:
    """Convert to dictionary for YAML serialization.

    Args:
      root: Repository root for relativizing file paths.

    Returns:
      Dictionary with non-empty fields only.
    """
    # Always-include fields
    data: dict[str, Any] = {
      "id": self.id,
      "name": self.name,
      "status": self.status,
      "memory_type": self.memory_type,
      "path": str(Path(self.path).relative_to(root)) if self.path else "",
    }

    # Dates — include only if present
    for date_field in ("created", "updated", "verified", "review_by"):
      val = getattr(self, date_field)
      if val:
        data[date_field] = val.isoformat()

    # Optional scalars — include only if truthy
    if self.verified_sha:
      data["verified_sha"] = self.verified_sha
    if self.confidence:
      data["confidence"] = self.confidence
    if self.summary:
      data["summary"] = self.summary

    # Optional lists — include only if non-empty
    for list_field in (
      "tags",
      "owners",
      "requires_reading",
      "audience",
      "visibility",
      "relations",
    ):
      val = getattr(self, list_field)
      if val:
        data[list_field] = val

    # Optional objects — include only if non-empty
    for obj_field in ("scope", "priority", "provenance", "links"):
      val = getattr(self, obj_field)
      if val:
        data[obj_field] = val

    return data
