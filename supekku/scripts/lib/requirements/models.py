"""Requirement data models and statistics tracking."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .lifecycle import STATUS_PENDING, RequirementStatus


@dataclass
class RequirementRecord:
  """Record representing a requirement with lifecycle tracking."""

  uid: str
  label: str
  title: str
  specs: list[str] = field(default_factory=list)
  primary_spec: str = ""
  kind: str = "functional"
  category: str | None = None
  status: RequirementStatus = STATUS_PENDING
  tags: list[str] = field(default_factory=list)
  introduced: str | None = None
  implemented_by: list[str] = field(default_factory=list)
  verified_by: list[str] = field(default_factory=list)
  coverage_evidence: list[str] = field(default_factory=list)
  coverage_entries: list[dict[str, Any]] = field(default_factory=list)
  path: str = ""
  ext_id: str = ""
  ext_url: str = ""
  source_kind: str = ""
  source_type: str = ""

  def merge(self, other: RequirementRecord) -> RequirementRecord:
    """Merge data from another record, preserving lifecycle fields."""
    return RequirementRecord(
      uid=self.uid,
      label=self.label,
      title=other.title,
      specs=sorted(set(self.specs) | set(other.specs)),
      primary_spec=other.primary_spec or self.primary_spec,
      kind=other.kind or self.kind,
      category=other.category or self.category,
      status=self.status,
      tags=sorted(set(self.tags) | set(other.tags)),
      introduced=self.introduced,
      implemented_by=list(self.implemented_by),
      verified_by=list(self.verified_by),
      coverage_evidence=sorted(
        set(self.coverage_evidence) | set(other.coverage_evidence)
      ),
      coverage_entries=list(self.coverage_entries),
      path=other.path or self.path,
      source_kind=other.source_kind or self.source_kind,
      source_type=other.source_type or self.source_type,
    )

  def to_dict(self) -> dict[str, object]:
    """Convert requirement record to dictionary for serialization."""
    d: dict[str, object] = {
      "label": self.label,
      "title": self.title,
      "specs": self.specs,
      "primary_spec": self.primary_spec,
      "kind": self.kind,
      "category": self.category,
      "status": self.status,
      "tags": self.tags,
      "introduced": self.introduced,
      "implemented_by": self.implemented_by,
      "verified_by": self.verified_by,
      "coverage_evidence": self.coverage_evidence,
      "coverage_entries": self.coverage_entries,
      "path": self.path,
    }
    if self.ext_id:
      d["ext_id"] = self.ext_id
    if self.ext_url:
      d["ext_url"] = self.ext_url
    if self.source_kind:
      d["source_kind"] = self.source_kind
    if self.source_type:
      d["source_type"] = self.source_type
    return d

  @classmethod
  def from_dict(cls, uid: str, data: dict[str, Any]) -> RequirementRecord:
    """Create requirement record from dictionary."""
    cat = data.get("category")
    intro = data.get("introduced")
    return cls(
      uid=uid,
      label=str(data.get("label", "")),
      title=str(data.get("title", "")),
      specs=list(data.get("specs", [])),
      primary_spec=str(data.get("primary_spec", "")),
      kind=str(data.get("kind", "functional")),
      category=str(cat) if cat is not None else None,
      status=str(data.get("status", STATUS_PENDING)),
      tags=list(data.get("tags", [])),
      introduced=str(intro) if intro is not None else None,
      implemented_by=list(data.get("implemented_by", [])),
      verified_by=list(data.get("verified_by", [])),
      coverage_evidence=list(data.get("coverage_evidence", [])),
      coverage_entries=list(data.get("coverage_entries", [])),
      path=str(data.get("path", "")),
      source_kind=str(data.get("source_kind", "")),
      source_type=str(data.get("source_type", "")),
    )


@dataclass
class SyncStats:
  """Statistics tracking for synchronization operations."""

  created: int = 0
  updated: int = 0
  pruned: int = 0
  warnings: int = 0
