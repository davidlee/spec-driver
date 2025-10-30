"""Backlog management utilities for creating and managing backlog entries."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from .spec_utils import dump_markdown_file, load_markdown_file

if TYPE_CHECKING:
  from collections.abc import Iterable, Mapping

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


def find_repo_root(start: Path | None = None) -> Path:
  # Import here to avoid circular dependency with paths.py
  from .paths import SPEC_DRIVER_DIR  # noqa: PLC0415

  current = (start or Path.cwd()).resolve()
  for candidate in [current, *current.parents]:
    if (candidate / ".git").exists() or (candidate / SPEC_DRIVER_DIR).exists():
      return candidate
  msg = (
    f"Could not locate repository root (missing .git or {SPEC_DRIVER_DIR} directory)"
  )
  raise RuntimeError(
    msg,
  )


def backlog_root(repo_root: Path) -> Path:
  return repo_root / "backlog"


def slugify(value: str) -> str:
  slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
  return slug or "item"


def next_identifier(entries: Iterable[Path], prefix: str) -> str:
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
  frontmatter, body = load_markdown_file(path)
  title = frontmatter.get("name")
  if isinstance(title, str) and title.strip():
    return title.strip()
  for line in body.splitlines():
    if line.strip().startswith("# "):
      return line.strip().lstrip("# ").strip()
  return "Untitled"


def append_backlog_summary(*, repo_root: Path | None = None) -> list[str]:
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


__all__ = [
  "append_backlog_summary",
  "create_backlog_entry",
  "find_repo_root",
]
