"""Standard registry management.

Provides StandardRecord data model and StandardRegistry for YAML-backed
standard management. Standards support draft, required, default, and
deprecated statuses.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from supekku.scripts.lib.core.paths import get_registry_dir
from supekku.scripts.lib.core.repo import find_repo_root
from supekku.scripts.lib.core.spec_utils import load_markdown_file


@dataclass
class StandardRecord:
  """Record representing a Standard with metadata.

  Standards differ from policies in status options:
  - draft: Work in progress
  - required: Must comply (like a policy)
  - default: Recommended unless justified otherwise
  - deprecated: No longer active
  """

  id: str
  title: str
  status: str  # draft | required | default | deprecated
  created: date | None = None
  updated: date | None = None
  reviewed: date | None = None
  owners: list[str] = field(default_factory=list)
  supersedes: list[str] = field(default_factory=list)
  superseded_by: list[str] = field(default_factory=list)
  policies: list[str] = field(default_factory=list)
  specs: list[str] = field(default_factory=list)
  requirements: list[str] = field(default_factory=list)
  deltas: list[str] = field(default_factory=list)
  related_policies: list[str] = field(default_factory=list)
  related_standards: list[str] = field(default_factory=list)
  tags: list[str] = field(default_factory=list)
  summary: str = ""
  path: str = ""
  backlinks: dict[str, list[str]] = field(default_factory=dict)

  def to_dict(self, root: Path) -> dict[str, Any]:
    """Convert to dictionary for YAML serialization.

    Args:
        root: Repository root path for relativizing file paths

    Returns:
        Dictionary representation suitable for YAML serialization

    """
    data = {
      "id": self.id,
      "title": self.title,
      "status": self.status,
      "path": str(Path(self.path).relative_to(root)) if self.path else "",
      "summary": self.summary,
    }

    # Add date fields if present
    if self.created:
      data["created"] = self.created.isoformat()
    if self.updated:
      data["updated"] = self.updated.isoformat()
    if self.reviewed:
      data["reviewed"] = self.reviewed.isoformat()

    # Add list fields if non-empty
    if self.owners:
      data["owners"] = self.owners
    if self.supersedes:
      data["supersedes"] = self.supersedes
    if self.superseded_by:
      data["superseded_by"] = self.superseded_by
    if self.policies:
      data["policies"] = self.policies
    if self.specs:
      data["specs"] = self.specs
    if self.requirements:
      data["requirements"] = self.requirements
    if self.deltas:
      data["deltas"] = self.deltas
    if self.related_policies:
      data["related_policies"] = self.related_policies
    if self.related_standards:
      data["related_standards"] = self.related_standards
    if self.tags:
      data["tags"] = self.tags
    if self.backlinks:
      data["backlinks"] = self.backlinks

    return data


class StandardRegistry:
  """Registry for managing Standards."""

  def __init__(self, *, root: Path | None = None) -> None:
    self.root = root if root is not None else find_repo_root(None)
    self.directory = self.root / "specify" / "standards"
    self.output_path = get_registry_dir(self.root) / "standards.yaml"

  @classmethod
  def load(cls, root: Path | None = None) -> StandardRegistry:
    """Load existing registry from YAML file."""
    return cls(root=root)

  def collect(self) -> dict[str, StandardRecord]:
    """Collect all standard files and parse them into StandardRecords."""
    standards: dict[str, StandardRecord] = {}

    if not self.directory.exists():
      return standards

    # Find all STD-*.md files in the standards directory
    for standard_file in self.directory.glob("STD-*.md"):
      try:
        standard = self._parse_standard_file(standard_file)
        if standard:
          standards[standard.id] = standard
      except (ValueError, KeyError, FileNotFoundError):
        # Log error but continue processing other files
        continue

    return standards

  def _parse_standard_file(self, standard_path: Path) -> StandardRecord | None:
    """Parse an individual standard file into a StandardRecord."""
    frontmatter, content = load_markdown_file(standard_path)

    if not frontmatter:
      frontmatter = {}

    # Extract ID from filename if not in frontmatter
    filename_match = re.match(r"STD-(\d+)", standard_path.name)
    if not filename_match:
      return None

    file_id = f"STD-{filename_match.group(1)}"
    standard_id = frontmatter.get("id", file_id)

    # Extract title from content or frontmatter
    title = frontmatter.get("title", "")
    if not title:
      # Try to extract from first H1 in content
      for line in content.split("\n"):
        if line.strip().startswith("# STD-"):
          title = line.strip()
          break
      if not title:
        title = standard_path.stem.replace("-", " ").title()

    # Parse dates
    created = self.parse_date(frontmatter.get("created"))
    updated = self.parse_date(frontmatter.get("updated"))
    reviewed = self.parse_date(frontmatter.get("reviewed"))

    # Get status from frontmatter (draft, required, default, deprecated)
    status = frontmatter.get("status", "").lower()
    if not status:
      status = "draft"  # default

    return StandardRecord(
      id=standard_id,
      title=title,
      status=status,
      created=created,
      updated=updated,
      reviewed=reviewed,
      owners=frontmatter.get("owners", []),
      supersedes=frontmatter.get("supersedes", []),
      superseded_by=frontmatter.get("superseded_by", []),
      policies=frontmatter.get("policies", []),
      specs=frontmatter.get("specs", []),
      requirements=frontmatter.get("requirements", []),
      deltas=frontmatter.get("deltas", []),
      related_policies=frontmatter.get("related_policies", []),
      related_standards=frontmatter.get("related_standards", []),
      tags=frontmatter.get("tags", []),
      summary=frontmatter.get("summary", ""),
      path=str(standard_path),
    )

  def parse_date(self, date_value: Any) -> date | None:
    """Parse date from various formats."""
    if not date_value:
      return None

    if isinstance(date_value, date):
      return date_value

    if isinstance(date_value, datetime):
      return date_value.date()

    if isinstance(date_value, str):
      # Try common date formats
      for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d"]:
        try:
          return datetime.strptime(date_value, fmt).date()
        except ValueError:
          continue

    return None

  def write(self, path: Path | None = None) -> None:
    """Write registry to YAML file."""
    if path is None:
      path = self.output_path

    standards = self.collect()

    registry_data = {
      "standards": {
        standard_id: standard.to_dict(self.root)
        for standard_id, standard in sorted(standards.items())
      },
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(registry_data, sort_keys=False)
    path.write_text(text, encoding="utf-8")

  def sync(self) -> None:
    """Sync registry by collecting standards and writing to YAML."""
    self.write()

  def iter(self, status: str | None = None) -> Iterator[StandardRecord]:
    """Iterate over standards, optionally filtered by status."""
    standards = self.collect()
    for standard in standards.values():
      if status is None or standard.status == status:
        yield standard

  def find(self, standard_id: str) -> StandardRecord | None:
    """Find a specific standard by ID."""
    standards = self.collect()
    return standards.get(standard_id)

  def filter(
    self,
    *,
    tag: str | None = None,
    spec: str | None = None,
    delta: str | None = None,
    requirement: str | None = None,
    policy: str | None = None,
  ) -> list[StandardRecord]:
    """Filter standards by various criteria."""
    standards = list(self.iter())
    results = []

    for standard in standards:
      matches = True

      if tag and tag not in standard.tags:
        matches = False
      if spec and spec not in standard.specs:
        matches = False
      if delta and delta not in standard.deltas:
        matches = False
      if requirement and requirement not in standard.requirements:
        matches = False
      if policy and policy not in standard.policies:
        matches = False

      if matches:
        results.append(standard)

    return results


__all__ = [
  "StandardRecord",
  "StandardRegistry",
]
