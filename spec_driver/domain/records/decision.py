"""Decision (ADR) record dataclass — canonical home in spec_driver.domain.records.

Migrated verbatim from supekku/scripts/lib/decisions/registry.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any


@dataclass
class DecisionRecord:
  """Record representing an Architecture Decision Record with metadata."""

  id: str
  title: str
  status: str
  created: date | None = None
  decided: date | None = None
  updated: date | None = None
  reviewed: date | None = None
  authors: list[dict[str, str]] = field(default_factory=list)
  owners: list[str] = field(default_factory=list)
  supersedes: list[str] = field(default_factory=list)
  superseded_by: list[str] = field(default_factory=list)
  policies: list[str] = field(default_factory=list)
  standards: list[str] = field(default_factory=list)
  specs: list[str] = field(default_factory=list)
  requirements: list[str] = field(default_factory=list)
  deltas: list[str] = field(default_factory=list)
  revisions: list[str] = field(default_factory=list)
  audits: list[str] = field(default_factory=list)
  related_decisions: list[str] = field(default_factory=list)
  related_policies: list[str] = field(default_factory=list)
  tags: list[str] = field(default_factory=list)
  summary: str = ""
  path: str = ""
  backlinks: dict[str, list[str]] = field(default_factory=dict)

  def to_dict(self, root: Path) -> dict[str, Any]:
    """Convert to dictionary for YAML serialization."""
    data: dict[str, Any] = {
      "id": self.id,
      "title": self.title,
      "status": self.status,
      "path": str(Path(self.path).relative_to(root)) if self.path else "",
      "summary": self.summary,
    }
    if self.created:
      data["created"] = self.created.isoformat()
    if self.decided:
      data["decided"] = self.decided.isoformat()
    if self.updated:
      data["updated"] = self.updated.isoformat()
    if self.reviewed:
      data["reviewed"] = self.reviewed.isoformat()
    if self.authors:
      data["authors"] = self.authors
    if self.owners:
      data["owners"] = self.owners
    if self.supersedes:
      data["supersedes"] = self.supersedes
    if self.superseded_by:
      data["superseded_by"] = self.superseded_by
    if self.policies:
      data["policies"] = self.policies
    if self.standards:
      data["standards"] = self.standards
    if self.specs:
      data["specs"] = self.specs
    if self.requirements:
      data["requirements"] = self.requirements
    if self.deltas:
      data["deltas"] = self.deltas
    if self.revisions:
      data["revisions"] = self.revisions
    if self.audits:
      data["audits"] = self.audits
    if self.related_decisions:
      data["related_decisions"] = self.related_decisions
    if self.related_policies:
      data["related_policies"] = self.related_policies
    if self.tags:
      data["tags"] = self.tags
    if self.backlinks:
      data["backlinks"] = self.backlinks
    return data


__all__ = ["DecisionRecord"]
