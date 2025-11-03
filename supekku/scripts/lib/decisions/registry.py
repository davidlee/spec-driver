"""Decision (ADR) registry management and processing utilities."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from supekku.scripts.lib.core.paths import get_registry_dir
from supekku.scripts.lib.core.repo import find_repo_root
from supekku.scripts.lib.core.spec_utils import load_markdown_file

if TYPE_CHECKING:
  from collections.abc import Iterator


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
    if self.decided:
      data["decided"] = self.decided.isoformat()
    if self.updated:
      data["updated"] = self.updated.isoformat()
    if self.reviewed:
      data["reviewed"] = self.reviewed.isoformat()

    # Add list fields if non-empty
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


class DecisionRegistry:
  """Registry for managing Architecture Decision Records."""

  def __init__(self, *, root: Path | None = None) -> None:
    self.root = find_repo_root(root)
    self.directory = self.root / "specify" / "decisions"
    self.output_path = get_registry_dir(self.root) / "decisions.yaml"

  @classmethod
  def load(cls, root: Path | None = None) -> DecisionRegistry:
    """Load existing registry from YAML file."""
    return cls(root=root)

  def collect(self) -> dict[str, DecisionRecord]:
    """Collect all ADR files and parse them into DecisionRecords."""
    decisions: dict[str, DecisionRecord] = {}

    if not self.directory.exists():
      return decisions

    # Find all ADR-*.md files in the decisions directory
    for adr_file in self.directory.glob("ADR-*.md"):
      try:
        decision = self._parse_adr_file(adr_file)
        if decision:
          decisions[decision.id] = decision
      except (ValueError, KeyError, FileNotFoundError):
        # Log error but continue processing other files
        continue

    return decisions

  def _parse_adr_file(self, adr_path: Path) -> DecisionRecord | None:
    """Parse an individual ADR file into a DecisionRecord."""
    frontmatter, content = load_markdown_file(adr_path)

    if not frontmatter:
      frontmatter = {}

    # Extract ID from filename if not in frontmatter
    filename_match = re.match(r"ADR-(\d+)", adr_path.name)
    if not filename_match:
      return None

    file_id = f"ADR-{filename_match.group(1)}"
    adr_id = frontmatter.get("id", file_id)

    # Extract title from content or frontmatter
    title = frontmatter.get("title", "")
    if not title:
      # Try to extract from first H1 in content
      for line in content.split("\n"):
        if line.strip().startswith("# ADR-"):
          title = line.strip()
          break
      if not title:
        title = adr_path.stem.replace("-", " ").title()

    # Parse dates
    created = self.parse_date(frontmatter.get("created"))
    decided = self.parse_date(frontmatter.get("decided"))
    updated = self.parse_date(frontmatter.get("updated"))
    reviewed = self.parse_date(frontmatter.get("reviewed"))

    # Determine status from frontmatter or directory location
    status = frontmatter.get("status", "").lower()
    if not status:
      # Infer from directory structure
      status_dirs = [
        "accepted",
        "deprecated",
        "superseded",
        "rejected",
        "proposed",
        "draft",
      ]
      for status_dir in status_dirs:
        if (self.directory / status_dir / adr_path.name).exists():
          status = status_dir
          break
      if not status:
        status = "draft"  # default

    return DecisionRecord(
      id=adr_id,
      title=title,
      status=status,
      created=created,
      decided=decided,
      updated=updated,
      reviewed=reviewed,
      authors=frontmatter.get("authors", []),
      owners=frontmatter.get("owners", []),
      supersedes=frontmatter.get("supersedes", []),
      superseded_by=frontmatter.get("superseded_by", []),
      policies=frontmatter.get("policies", []),
      standards=frontmatter.get("standards", []),
      specs=frontmatter.get("specs", []),
      requirements=frontmatter.get("requirements", []),
      deltas=frontmatter.get("deltas", []),
      revisions=frontmatter.get("revisions", []),
      audits=frontmatter.get("audits", []),
      related_decisions=frontmatter.get("related_decisions", []),
      related_policies=frontmatter.get("related_policies", []),
      tags=frontmatter.get("tags", []),
      summary=frontmatter.get("summary", ""),
      path=str(adr_path),
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

    decisions = self.collect()

    # Build backlinks from policies and standards
    self._build_backlinks(decisions)

    registry_data = {
      "decisions": {
        decision_id: decision.to_dict(self.root)
        for decision_id, decision in sorted(decisions.items())
      },
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(registry_data, sort_keys=False)
    path.write_text(text, encoding="utf-8")

  def _build_backlinks(self, decisions: dict[str, DecisionRecord]) -> None:
    """Build backlinks for decisions.

    Currently decisions don't receive backlinks from policies/standards,
    but this method is provided for future extensibility (e.g., specs or
    requirements referencing decisions).

    Args:
        decisions: Dictionary of DecisionRecords to populate with backlinks

    """
    # Clear existing backlinks (fresh computation each sync per ADR-002)
    for decision in decisions.values():
      decision.backlinks = {}

    # Note: Decisions contain forward references to policies and standards.
    # Policies and Standards build their own backlinks to decisions.
    # If in future we need to show "referenced by" on decisions, add logic here.

  def sync(self) -> None:
    """Sync registry by collecting decisions and writing to YAML."""
    self.write()

  def iter(self, status: str | None = None) -> Iterator[DecisionRecord]:
    """Iterate over decisions, optionally filtered by status."""
    decisions = self.collect()
    for decision in decisions.values():
      if status is None or decision.status == status:
        yield decision

  def find(self, decision_id: str) -> DecisionRecord | None:
    """Find a specific decision by ID."""
    decisions = self.collect()
    return decisions.get(decision_id)

  def filter(
    self,
    *,
    tag: str | None = None,
    spec: str | None = None,
    delta: str | None = None,
    requirement: str | None = None,
    policy: str | None = None,
  ) -> list[DecisionRecord]:
    """Filter decisions by various criteria."""
    decisions = list(self.iter())
    results = []

    for decision in decisions:
      matches = True

      if tag and tag not in decision.tags:
        matches = False
      if spec and spec not in decision.specs:
        matches = False
      if delta and delta not in decision.deltas:
        matches = False
      if requirement and requirement not in decision.requirements:
        matches = False
      if policy and policy not in decision.policies:
        matches = False

      if matches:
        results.append(decision)

    return results

  def rebuild_status_symlinks(self) -> None:
    """Rebuild all status-based symlink directories."""
    decisions = self.collect()
    decisions_dir = self.root / "specify" / "decisions"

    # First, clean up all existing status directories
    self._cleanup_all_status_directories(decisions_dir)

    # Group decisions by status
    status_groups = {}
    for decision in decisions.values():
      status = decision.status
      if status not in status_groups:
        status_groups[status] = []
      status_groups[status].append(decision)

    # Create/update symlink directories for each status
    for status, status_decisions in status_groups.items():
      status_dir = decisions_dir / status
      self._rebuild_status_directory(status_dir, status_decisions)

  def _cleanup_all_status_directories(self, decisions_dir: Path) -> None:
    """Remove all symlinks from existing status directories."""
    # Known status directories that might contain symlinks
    status_dirs = [
      "accepted",
      "draft",
      "proposed",
      "deprecated",
      "superseded",
      "rejected",
      "revision-required",
    ]

    for status in status_dirs:
      status_dir = decisions_dir / status
      if status_dir.exists() and status_dir.is_dir():
        for item in status_dir.iterdir():
          if item.is_symlink():
            item.unlink()

  def _rebuild_status_directory(
    self,
    status_dir: Path,
    decisions: list[DecisionRecord],
  ) -> None:
    """Rebuild a single status directory with symlinks."""
    # Create directory if it doesn't exist
    status_dir.mkdir(exist_ok=True)

    # Create new symlinks
    for decision in decisions:
      source_file = Path(decision.path)
      if source_file.exists():
        link_name = status_dir / source_file.name
        # Create relative symlink back to canonical file
        relative_target = Path("..") / source_file.name
        link_name.symlink_to(relative_target)

  def sync_with_symlinks(self) -> None:
    """Sync registry and rebuild symlinks in one operation."""
    self.collect()  # Ensure data is loaded
    self.write(self.output_path)
    self.rebuild_status_symlinks()


__all__ = ["DecisionRecord", "DecisionRegistry"]
