"""MemoryRecord model for memory artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any


def _parse_date(value: Any) -> date | None:
  """Parse a date from string or date object.

  Args:
    value: Date string (YYYY-MM-DD), date object, or datetime object.

  Returns:
    Parsed date or None if unparseable.
  """
  if not value:
    return None
  if isinstance(value, date) and not isinstance(value, datetime):
    return value
  if isinstance(value, datetime):
    return value.date()
  if isinstance(value, str):
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d"):
      try:
        return datetime.strptime(value, fmt).date()
      except ValueError:
        continue
  return None


@dataclass
class MemoryRecord:
  """A memory artifact record parsed from frontmatter.

  Required fields: id, name, status, memory_type, path.
  All other fields are optional with safe defaults.
  """

  # Required
  id: str
  name: str
  status: str
  memory_type: str
  path: str

  # Optional dates
  created: date | None = None
  updated: date | None = None
  verified: date | None = None
  review_by: date | None = None

  # Optional scalars
  confidence: str | None = None
  summary: str = ""

  # Optional lists
  tags: list[str] = field(default_factory=list)
  owners: list[str] = field(default_factory=list)
  requires_reading: list[str] = field(default_factory=list)
  audience: list[str] = field(default_factory=list)
  visibility: list[str] = field(default_factory=list)
  relations: list[dict[str, Any]] = field(default_factory=list)

  # Optional objects
  scope: dict[str, Any] = field(default_factory=dict)
  priority: dict[str, Any] = field(default_factory=dict)
  provenance: dict[str, Any] = field(default_factory=dict)

  @classmethod
  def from_frontmatter(cls, path: Path, fm: dict[str, Any]) -> MemoryRecord:
    """Construct a MemoryRecord from parsed frontmatter.

    Args:
      path: Filesystem path to the memory file.
      fm: Parsed frontmatter dictionary.

    Returns:
      Populated MemoryRecord.
    """
    return cls(
      id=fm.get("id", ""),
      name=fm.get("name", ""),
      status=fm.get("status", ""),
      memory_type=fm.get("memory_type", ""),
      path=str(path),
      created=_parse_date(fm.get("created")),
      updated=_parse_date(fm.get("updated")),
      verified=_parse_date(fm.get("verified")),
      review_by=_parse_date(fm.get("review_by")),
      confidence=fm.get("confidence"),
      summary=fm.get("summary", ""),
      tags=fm.get("tags", []),
      owners=fm.get("owners", []),
      requires_reading=fm.get("requires_reading", []),
      audience=fm.get("audience", []),
      visibility=fm.get("visibility", []),
      relations=fm.get("relations", []),
      scope=fm.get("scope", {}),
      priority=fm.get("priority", {}),
      provenance=fm.get("provenance", {}),
    )

  def to_dict(self, root: Path) -> dict[str, Any]:
    """Convert to dictionary for YAML serialization.

    Args:
      root: Repository root for relativizing file paths.

    Returns:
      Dictionary with non-empty fields only.
    """
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

    # Optional scalars
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
    for obj_field in ("scope", "priority", "provenance"):
      val = getattr(self, obj_field)
      if val:
        data[obj_field] = val

    return data
