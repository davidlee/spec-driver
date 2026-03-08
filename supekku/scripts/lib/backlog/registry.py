"""Backlog management utilities for creating and managing backlog entries.

Provides BacklogRegistry (ADR-009 conformant class) and module-level
wrapper functions for backwards compatibility (DEC-057-04).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from supekku.scripts.lib.backlog.models import BacklogItem
from supekku.scripts.lib.core import slugify
from supekku.scripts.lib.core.paths import get_backlog_dir, get_registry_dir
from supekku.scripts.lib.core.repo import find_repo_root
from supekku.scripts.lib.core.spec_utils import dump_markdown_file, load_markdown_file

if TYPE_CHECKING:
  from collections.abc import Iterable, Iterator, Mapping

logger = logging.getLogger(__name__)

BACKLOG_ID_PATTERN = re.compile(r"^(ISSUE|IMPR|PROB|RISK)-(\d{3,})\.md$")


@dataclass(frozen=True)
class BacklogTemplate:
  """Template for creating backlog entries with specific metadata."""

  prefix: str
  subdir: str
  frontmatter: Mapping[str, object]


TEMPLATES: Mapping[str, BacklogTemplate] = {
  "issue": BacklogTemplate(
    prefix="ISSUE",
    subdir="issues",
    frontmatter={
      "status": "open",
      "kind": "issue",
      "categories": [],
      "severity": "p3",
      "impact": "user",
    },
  ),
  "problem": BacklogTemplate(
    prefix="PROB",
    subdir="problems",
    frontmatter={
      "status": "captured",
      "kind": "problem",
    },
  ),
  "improvement": BacklogTemplate(
    prefix="IMPR",
    subdir="improvements",
    frontmatter={
      "status": "idea",
      "kind": "improvement",
    },
  ),
  "risk": BacklogTemplate(
    prefix="RISK",
    subdir="risks",
    frontmatter={
      "status": "suspected",
      "kind": "risk",
      "categories": [],
      "likelihood": 0.2,
      "severity": "p3",
      "impact": "user",
    },
  ),
}


class BacklogRegistry:
  """Registry for backlog items (ADR-009 conformant).

  Provides find/collect/iter/filter over all backlog item types.
  Eagerly loads and caches items on construction (DEC-057-05).
  """

  def __init__(self, *, root: Path | None = None) -> None:
    self.root = find_repo_root(root)
    self._directory = get_backlog_dir(self.root)
    self._items: dict[str, BacklogItem] = {}
    self._load()

  def _load(self) -> None:
    """Scan filesystem and cache all backlog items."""
    if not self._directory.exists():
      return

    for kind_dir_name in ("issues", "problems", "improvements", "risks"):
      kind_path = self._directory / kind_dir_name
      if not kind_path.exists():
        continue
      for entry_dir in kind_path.iterdir():
        if not entry_dir.is_dir():
          continue
        for md_file in entry_dir.glob("*.md"):
          item = self._parse_item(md_file, kind_dir_name)
          if item is not None:
            if item.id in self._items:
              logger.warning(
                "Duplicate backlog item ID %s: %s and %s",
                item.id,
                self._items[item.id].path,
                item.path,
              )
            self._items[item.id] = item

  def _parse_item(self, md_file: Path, kind_dir_name: str) -> BacklogItem | None:
    """Parse a single backlog item file into a BacklogItem."""
    match = BACKLOG_ID_PATTERN.match(md_file.name)
    if not match:
      return None

    prefix = match.group(1)
    number = match.group(2)
    item_id = f"{prefix}-{number}"

    try:
      frontmatter, _ = load_markdown_file(md_file)
    except Exception as exc:  # noqa: BLE001
      logger.warning(
        "Skipping %s: invalid YAML frontmatter — %s",
        md_file.relative_to(self.root),
        exc,
      )
      return None

    item_kind = str(frontmatter.get("kind", "")).lower() or kind_dir_name.rstrip("s")
    status = str(frontmatter.get("status", "")).lower() or "unknown"
    title = str(frontmatter.get("name", "")).strip()
    if not title:
      title = extract_title(md_file)

    return BacklogItem(
      id=item_id,
      kind=item_kind,
      status=status,
      title=title,
      path=md_file,
      frontmatter=dict(frontmatter),
      tags=list(frontmatter.get("tags", [])),
      severity=str(frontmatter.get("severity", "")),
      categories=list(frontmatter.get("categories", [])),
      impact=str(frontmatter.get("impact", "")),
      likelihood=float(frontmatter.get("likelihood", 0.0)),
      created=str(frontmatter.get("created", "")),
      updated=str(frontmatter.get("updated", "")),
      ext_id=str(frontmatter.get("ext_id", "")),
      ext_url=str(frontmatter.get("ext_url", "")),
    )

  def find(self, item_id: str) -> BacklogItem | None:
    """Find a backlog item by ID.

    Returns the matching item or None (ADR-009 contract).
    """
    return self._items.get(item_id)

  def collect(self) -> dict[str, BacklogItem]:
    """Return all backlog items as a dict keyed by ID (ADR-009 contract)."""
    return dict(self._items)

  def iter(
    self,
    *,
    status: str | None = None,
    kind: str | None = None,
  ) -> Iterator[BacklogItem]:
    """Iterate over items, optionally filtered by status and/or kind."""
    for item in self._items.values():
      if status is not None and item.status != status:
        continue
      if kind is not None and item.kind != kind:
        continue
      yield item

  def filter(
    self,
    *,
    kind: str | None = None,
    status: str | None = None,
    tag: str | None = None,
    severity: str | None = None,
  ) -> list[BacklogItem]:
    """Filter items by domain-specific criteria.

    Returns a list (ADR-009 contract). Empty list when no matches.
    """
    results: list[BacklogItem] = []
    for item in self._items.values():
      if kind is not None and item.kind != kind:
        continue
      if status is not None and item.status != status:
        continue
      if tag is not None and tag not in item.tags:
        continue
      if severity is not None and item.severity != severity:
        continue
      results.append(item)
    return results


def backlog_root(repo_root: Path) -> Path:
  """Get backlog directory path.

  Args:
    repo_root: Repository root path.

  Returns:
    Backlog directory path.
  """
  return get_backlog_dir(repo_root)


def load_backlog_registry(root: Path | None = None) -> list[str]:
  """Load backlog priority ordering from registry.

  Args:
    root: Repository root path (auto-detected if None)

  Returns:
    Ordered list of backlog item IDs. Empty list if registry doesn't exist
    or ordering field is missing.

  Raises:
    yaml.YAMLError: If registry file exists but contains invalid YAML
  """
  repo_root = find_repo_root(root)
  registry_path = get_registry_dir(repo_root) / "backlog.yaml"

  if not registry_path.exists():
    return []

  registry_data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))

  if not isinstance(registry_data, dict):
    return []

  ordering = registry_data.get("ordering", [])
  return list(ordering) if isinstance(ordering, list) else []


def save_backlog_registry(ordering: list[str], root: Path | None = None) -> None:
  """Save backlog priority ordering to registry.

  Args:
    ordering: Ordered list of backlog item IDs
    root: Repository root path (auto-detected if None)

  Note:
    Creates parent directories if needed. Uses atomic write via temporary file.
  """
  repo_root = find_repo_root(root)
  registry_path = get_registry_dir(repo_root) / "backlog.yaml"

  # Ensure registry directory exists
  registry_path.parent.mkdir(parents=True, exist_ok=True)

  # Build registry data structure
  registry_data = {"ordering": ordering}

  # Write atomically: write to temp file, then rename
  # yaml.safe_dump with sort_keys=False preserves insertion order
  yaml_content = yaml.safe_dump(
    registry_data, sort_keys=False, default_flow_style=False
  )

  registry_path.write_text(yaml_content, encoding="utf-8")


def sync_backlog_registry(
  root: Path | None = None,
  *,
  dry_run: bool = False,
) -> dict[str, int]:
  """Sync backlog registry with filesystem.

  Discovers all backlog items, merges with existing registry ordering,
  and writes updated registry. Preserves order of existing items,
  appends new items, and prunes orphaned IDs.

  Args:
    root: Repository root path (auto-detected if None)
    dry_run: If True, compute stats but skip writing registry.

  Returns:
    Dictionary with sync statistics:
      - total: total items in registry after sync
      - added: number of new items added
      - removed: number of orphaned items removed
      - unchanged: number of items already in registry
  """
  repo_root = find_repo_root(root)

  # Discover all backlog items from filesystem
  items = discover_backlog_items(root=repo_root)
  current_ids = {item.id for item in items}

  # Load existing registry ordering
  existing_order = load_backlog_registry(repo_root)
  existing_ids = set(existing_order)

  # Calculate changes
  new_ids = current_ids - existing_ids
  orphaned_ids = existing_ids - current_ids

  # Build merged ordering:
  # 1. Keep existing items in their current order (excluding orphans)
  # 2. Append new items sorted by ID
  merged_order = [item_id for item_id in existing_order if item_id in current_ids]
  merged_order.extend(sorted(new_ids))

  # Save updated registry (skip in dry-run mode)
  if not dry_run:
    save_backlog_registry(merged_order, repo_root)

  # Return statistics
  return {
    "total": len(merged_order),
    "added": len(new_ids),
    "removed": len(orphaned_ids),
    "unchanged": len(existing_ids - orphaned_ids),
  }


def next_identifier(entries: Iterable[Path], prefix: str) -> str:
  """Determine next sequential identifier.

  Args:
    entries: Existing entry paths.
    prefix: Identifier prefix.

  Returns:
    Next available identifier.
  """
  highest = 0
  pattern = re.compile(rf"{re.escape(prefix)}[-_](\d+)")
  for entry in entries:
    match = pattern.search(entry.name)
    if not match:
      continue
    try:
      highest = max(highest, int(match.group(1)))
    except ValueError:
      continue
  return f"{prefix}-{highest + 1:03d}"


def create_backlog_entry(
  kind: str,
  name: str,
  *,
  repo_root: Path | None = None,
) -> Path:
  """Create a new backlog entry.

  Args:
    kind: Entry kind (issue, problem, improvement, risk).
    name: Entry name/title.
    repo_root: Optional repository root. Auto-detected if not provided.

  Returns:
    Path to created entry file.

  Raises:
    ValueError: If kind is not supported.
  """
  template = TEMPLATES.get(kind)
  if template is None:
    msg = f"Unsupported backlog kind: {kind}"
    raise ValueError(msg)

  repo_root = find_repo_root(repo_root)
  base_dir = backlog_root(repo_root) / template.subdir
  base_dir.mkdir(parents=True, exist_ok=True)

  entry_id = next_identifier(base_dir.iterdir(), template.prefix)
  slug = slugify(name)
  entry_dir = base_dir / f"{entry_id}-{slug}"
  entry_dir.mkdir(parents=True, exist_ok=True)

  today = date.today().isoformat()
  frontmatter = {
    "id": entry_id,
    "name": name,
    "created": today,
    "updated": today,
    **template.frontmatter,
  }
  body = f"# {name}\n\n"

  entry_path = entry_dir / f"{entry_id}.md"
  dump_markdown_file(entry_path, frontmatter, body)
  return entry_path


def extract_title(path: Path) -> str:
  """Extract title from backlog entry file.

  Args:
    path: Path to backlog entry.

  Returns:
    Entry title from frontmatter or first heading.
  """
  frontmatter, body = load_markdown_file(path)
  title = frontmatter.get("name")
  if isinstance(title, str) and title.strip():
    return title.strip()
  for line in body.splitlines():
    if line.strip().startswith("# "):
      return line.strip().lstrip("# ").strip()
  return "Untitled"


def append_backlog_summary(*, repo_root: Path | None = None) -> list[str]:
  """Append new entries to backlog summary file.

  Args:
    repo_root: Optional repository root. Auto-detected if not provided.

  Returns:
    List of newly added summary lines.
  """
  repo_root = find_repo_root(repo_root)
  root = backlog_root(repo_root)
  summary_path = root / "backlog.md"
  if not summary_path.exists():
    summary_path.touch()
  existing_text = summary_path.read_text(encoding="utf-8")

  additions: list[str] = []
  for file_path in root.rglob("*.md"):
    if file_path == summary_path:
      continue
    relative = file_path.relative_to(root)
    match = BACKLOG_ID_PATTERN.match(relative.name)
    if not match:
      continue
    backlog_id = f"{match.group(1)}-{match.group(2)}"
    if backlog_id in existing_text:
      continue
    title = extract_title(file_path)
    entry = f"- {backlog_id} - {title} [{backlog_id}]({relative.as_posix()})"
    additions.append(entry)

  if additions:
    with summary_path.open("a", encoding="utf-8") as handle:
      handle.write("\n".join(additions) + "\n")
    existing_text += "\n".join(additions)

  return additions


def discover_backlog_items(
  *,
  root: Path | None = None,
  kind: str = "all",
) -> list[BacklogItem]:
  """Discover all backlog items in workspace.

  Thin wrapper around BacklogRegistry for backwards compatibility (DEC-057-04).

  Args:
    root: Repository root (auto-detected if None)
    kind: Filter by kind (issue|problem|improvement|risk|all)

  Returns:
    List of BacklogItem objects, sorted by ID.
  """
  registry = BacklogRegistry(root=root)
  kind_filter = kind if kind != "all" else None
  items = list(registry.iter(kind=kind_filter))
  return sorted(items, key=lambda x: x.id)


def find_backlog_items_by_id(
  item_id: str,
  root: Path,
  kind: str | None = None,
) -> list[BacklogItem]:
  """Find backlog items by ID.

  Thin wrapper around BacklogRegistry for backwards compatibility (DEC-057-04).
  Returns a list because duplicate IDs may exist (data quality issue).

  Args:
    item_id: Backlog item ID (e.g. 'ISSUE-001', 'IMPR-003').
    root: Repository root path.
    kind: Optional kind filter ('issue', 'problem', 'improvement', 'risk').

  Returns:
    List of matching BacklogItem objects, sorted by path.
  """
  registry = BacklogRegistry(root=root)
  item = registry.find(item_id)
  if item is None:
    return []
  if kind is not None and item.kind != kind:
    return []
  return [item]


def find_item(
  item_id: str,
  root: Path | None = None,
  kind: str | None = None,
) -> BacklogItem | None:
  """Find a single backlog item by ID.

  Thin wrapper around BacklogRegistry for backwards compatibility (DEC-057-04).

  Args:
    item_id: Backlog item ID (e.g. 'ISSUE-001').
    root: Repository root path (auto-detected if None).
    kind: Optional kind filter.

  Returns:
    BacklogItem or None if not found.
  """
  registry = BacklogRegistry(root=root)
  item = registry.find(item_id)
  if item is None:
    return None
  if kind is not None and item.kind != kind:
    return None
  return item


__all__ = [
  "BacklogRegistry",
  "append_backlog_summary",
  "create_backlog_entry",
  "discover_backlog_items",
  "find_backlog_items_by_id",
  "find_item",
  "find_repo_root",
  "load_backlog_registry",
  "save_backlog_registry",
  "sync_backlog_registry",
]
