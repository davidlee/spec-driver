"""Policy registry management.

Provides PolicyRecord data model and PolicyRegistry for YAML-backed policy management.
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
class PolicyRecord:
  """Record representing a Policy with metadata."""

  id: str
  title: str
  status: str
  created: date | None = None
  updated: date | None = None
  reviewed: date | None = None
  owners: list[str] = field(default_factory=list)
  supersedes: list[str] = field(default_factory=list)
  superseded_by: list[str] = field(default_factory=list)
  standards: list[str] = field(default_factory=list)
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
    if self.standards:
      data["standards"] = self.standards
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


class PolicyRegistry:
  """Registry for managing Policies."""

  def __init__(self, *, root: Path | None = None) -> None:
    self.root = root if root is not None else find_repo_root(None)
    self.directory = self.root / "specify" / "policies"
    self.output_path = get_registry_dir(self.root) / "policies.yaml"

  @classmethod
  def load(cls, root: Path | None = None) -> PolicyRegistry:
    """Load existing registry from YAML file."""
    return cls(root=root)

  def collect(self) -> dict[str, PolicyRecord]:
    """Collect all policy files and parse them into PolicyRecords."""
    policies: dict[str, PolicyRecord] = {}

    if not self.directory.exists():
      return policies

    # Find all POL-*.md files in the policies directory
    for policy_file in self.directory.glob("POL-*.md"):
      try:
        policy = self._parse_policy_file(policy_file)
        if policy:
          policies[policy.id] = policy
      except (ValueError, KeyError, FileNotFoundError):
        # Log error but continue processing other files
        continue

    return policies

  def _parse_policy_file(self, policy_path: Path) -> PolicyRecord | None:
    """Parse an individual policy file into a PolicyRecord."""
    frontmatter, content = load_markdown_file(policy_path)

    if not frontmatter:
      frontmatter = {}

    # Extract ID from filename if not in frontmatter
    filename_match = re.match(r"POL-(\d+)", policy_path.name)
    if not filename_match:
      return None

    file_id = f"POL-{filename_match.group(1)}"
    policy_id = frontmatter.get("id", file_id)

    # Extract title from content or frontmatter
    title = frontmatter.get("title", "")
    if not title:
      # Try to extract from first H1 in content
      for line in content.split("\n"):
        if line.strip().startswith("# POL-"):
          title = line.strip()
          break
      if not title:
        title = policy_path.stem.replace("-", " ").title()

    # Parse dates
    created = self.parse_date(frontmatter.get("created"))
    updated = self.parse_date(frontmatter.get("updated"))
    reviewed = self.parse_date(frontmatter.get("reviewed"))

    # Get status from frontmatter (required, draft, deprecated)
    status = frontmatter.get("status", "").lower()
    if not status:
      status = "draft"  # default

    return PolicyRecord(
      id=policy_id,
      title=title,
      status=status,
      created=created,
      updated=updated,
      reviewed=reviewed,
      owners=frontmatter.get("owners", []),
      supersedes=frontmatter.get("supersedes", []),
      superseded_by=frontmatter.get("superseded_by", []),
      standards=frontmatter.get("standards", []),
      specs=frontmatter.get("specs", []),
      requirements=frontmatter.get("requirements", []),
      deltas=frontmatter.get("deltas", []),
      related_policies=frontmatter.get("related_policies", []),
      related_standards=frontmatter.get("related_standards", []),
      tags=frontmatter.get("tags", []),
      summary=frontmatter.get("summary", ""),
      path=str(policy_path),
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

    policies = self.collect()

    # Build backlinks from decisions that reference policies
    self._build_backlinks(policies)

    registry_data = {
      "policies": {
        policy_id: policy.to_dict(self.root)
        for policy_id, policy in sorted(policies.items())
      },
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(registry_data, sort_keys=False)
    path.write_text(text, encoding="utf-8")

  def _build_backlinks(self, policies: dict[str, PolicyRecord]) -> None:
    """Build backlinks from decisions that reference policies.

    Per ADR-002, backlinks are computed at runtime from forward references,
    not stored in frontmatter.

    Args:
        policies: Dictionary of PolicyRecords to populate with backlinks

    """
    # Lazy import to avoid circular dependencies at module load time
    from supekku.scripts.lib.decisions.registry import (  # noqa: PLC0415
      DecisionRegistry,
    )

    # Clear existing backlinks (fresh computation each sync per ADR-002)
    for policy in policies.values():
      policy.backlinks = {}

    # Build backlinks from decisions
    try:
      decision_registry = DecisionRegistry(root=self.root)
      decisions = decision_registry.collect()

      for decision in decisions.values():
        # For each policy this decision references, add backlink
        for policy_id in decision.policies:
          if policy_id in policies:
            policies[policy_id].backlinks.setdefault("decisions", []).append(
              decision.id
            )
    except (FileNotFoundError, ValueError):
      # Decisions directory might not exist yet
      pass

  def sync(self) -> None:
    """Sync registry by collecting policies and writing to YAML."""
    self.write()

  def iter(self, status: str | None = None) -> Iterator[PolicyRecord]:
    """Iterate over policies, optionally filtered by status."""
    policies = self.collect()
    for policy in policies.values():
      if status is None or policy.status == status:
        yield policy

  def find(self, policy_id: str) -> PolicyRecord | None:
    """Find a specific policy by ID."""
    policies = self.collect()
    return policies.get(policy_id)

  def filter(
    self,
    *,
    tag: str | None = None,
    spec: str | None = None,
    delta: str | None = None,
    requirement: str | None = None,
    standard: str | None = None,
  ) -> list[PolicyRecord]:
    """Filter policies by various criteria."""
    policies = list(self.iter())
    results = []

    for policy in policies:
      matches = True

      if tag and tag not in policy.tags:
        matches = False
      if spec and spec not in policy.specs:
        matches = False
      if delta and delta not in policy.deltas:
        matches = False
      if requirement and requirement not in policy.requirements:
        matches = False
      if standard and standard not in policy.standards:
        matches = False

      if matches:
        results.append(policy)

    return results


__all__ = [
  "PolicyRecord",
  "PolicyRegistry",
]
