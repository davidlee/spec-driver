"""Batched staleness computation for memory artifacts.

Computes staleness by counting git commits that touched scoped paths
since a memory's last verified SHA. Uses a single git invocation for
all scoped memories (DEC-086-06).
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from supekku.scripts.lib.memory.models import MemoryRecord


@dataclass
class StalenessInfo:
  """Staleness data for a single memory."""

  memory_id: str
  verified_sha: str | None
  verified_date: date | None
  scope_paths: list[str] = field(default_factory=list)
  commits_since: int | None = None
  days_since: int | None = None
  has_scope: bool = False


def glob_to_pathspec(glob: str) -> str:
  """Convert a scope glob pattern to a git pathspec.

  Strips trailing ``/**`` (directory wildcard) to produce a directory
  prefix that git understands. Other patterns pass through as-is.
  Leading ``./`` is also stripped.

  Args:
    glob: Scope glob pattern (e.g. ``supekku/cli/**``).

  Returns:
    Git-compatible pathspec string.
  """
  spec = glob.lstrip("./")
  if spec.endswith("/**"):
    spec = spec[:-2]
    if not spec.endswith("/"):
      spec += "/"
  return spec


def compute_batch_staleness(
  records: list[MemoryRecord],
  root: Path,
) -> list[StalenessInfo]:
  """Compute staleness for multiple memories using a single git invocation.

  For scoped+attested memories, runs one ``git log`` from the oldest
  verified SHA and counts commits per memory's scope paths.

  Unscoped and unattested memories fall back to ``days_since`` from
  their verified or updated date.

  Args:
    records: Memory records to evaluate.
    root: Repository root for git commands.

  Returns:
    StalenessInfo for each input record, in the same order.
  """
  if not records:
    return []

  today = date.today()
  results: list[StalenessInfo] = []

  # Classify records
  attested: list[tuple[int, MemoryRecord, list[str]]] = []
  for idx, rec in enumerate(records):
    scope_paths = _collect_scope_paths(rec)
    has_scope = len(scope_paths) > 0

    info = StalenessInfo(
      memory_id=rec.id,
      verified_sha=rec.verified_sha,
      verified_date=rec.verified,
      scope_paths=scope_paths,
      has_scope=has_scope,
      days_since=_days_since(rec, today),
    )
    results.append(info)

    if has_scope and rec.verified_sha:
      attested.append((idx, rec, scope_paths))

  # Batch git query for attested records
  if attested:
    commit_data = _query_git_log(attested, root)
    if commit_data is not None:
      _assign_commit_counts(results, attested, commit_data)

  return results


def _collect_scope_paths(record: MemoryRecord) -> list[str]:
  """Collect all scope paths and converted globs for a record."""
  paths = list(record.scope.get("paths", []))
  for glob in record.scope.get("globs", []):
    paths.append(glob_to_pathspec(glob))
  return paths


def _days_since(record: MemoryRecord, today: date) -> int | None:
  """Compute days since the most relevant date on a record."""
  ref_date = record.verified or record.updated
  if ref_date is None:
    return None
  return (today - ref_date).days


def _find_oldest_sha(
  attested: list[tuple[int, MemoryRecord, list[str]]],
) -> str:
  """Find the verified_sha from the record with the oldest verified date."""
  oldest_rec = min(attested, key=lambda t: t[1].verified or date.max)
  sha = oldest_rec[1].verified_sha
  assert sha is not None  # noqa: S101
  return sha


def _collect_all_pathspecs(
  attested: list[tuple[int, MemoryRecord, list[str]]],
) -> list[str]:
  """Collect deduplicated pathspecs from all attested records."""
  seen: set[str] = set()
  specs: list[str] = []
  for _, _, paths in attested:
    for p in paths:
      if p not in seen:
        seen.add(p)
        specs.append(p)
  return specs


@dataclass
class _CommitEntry:
  """A parsed commit from git log output."""

  paths: list[str] = field(default_factory=list)


def _query_git_log(
  attested: list[tuple[int, MemoryRecord, list[str]]],
  root: Path,
) -> list[_CommitEntry] | None:
  """Run a single git log and parse commits with affected paths.

  Returns None if git is unavailable or the command fails, so callers
  can distinguish "no commits found" from "unable to query."
  """
  oldest_sha = _find_oldest_sha(attested)
  all_pathspecs = _collect_all_pathspecs(attested)

  cmd = [
    "git",
    "log",
    "--oneline",
    "--name-only",
    f"{oldest_sha}..HEAD",
    "--",
    *all_pathspecs,
  ]

  try:
    result = subprocess.run(  # noqa: S603, S607
      cmd,
      capture_output=True,
      text=True,
      timeout=30,
      cwd=root,
      check=False,
    )
  except (FileNotFoundError, subprocess.TimeoutExpired):
    return None

  if result.returncode != 0:
    return None

  return _parse_git_log_output(result.stdout)


def _parse_git_log_output(output: str) -> list[_CommitEntry]:
  """Parse ``git log --oneline --name-only`` output into commit entries."""
  commits: list[_CommitEntry] = []
  current: _CommitEntry | None = None

  for line in output.splitlines():
    if not line.strip():
      if current is not None:
        commits.append(current)
        current = None
      continue

    if current is None:
      # First non-blank line after a blank: commit summary
      current = _CommitEntry()
    else:
      # Subsequent non-blank lines: file paths
      current.paths.append(line.strip())

  # Flush last entry
  if current is not None:
    commits.append(current)

  return commits


def _path_matches_scope(file_path: str, scope_paths: list[str]) -> bool:
  """Check whether a file path matches any scope path (prefix match)."""
  for scope in scope_paths:
    if scope.endswith("/"):
      if file_path.startswith(scope) or file_path == scope.rstrip("/"):
        return True
    elif file_path == scope or file_path.startswith(scope + "/"):
      return True
  return False


def _assign_commit_counts(
  results: list[StalenessInfo],
  attested: list[tuple[int, MemoryRecord, list[str]]],
  commit_data: list[_CommitEntry],
) -> None:
  """Count commits affecting each attested memory's scope paths."""
  for idx, _, scope_paths in attested:
    count = 0
    for commit in commit_data:
      for fpath in commit.paths:
        if _path_matches_scope(fpath, scope_paths):
          count += 1
          break
    results[idx].commits_since = count


__all__ = [
  "StalenessInfo",
  "compute_batch_staleness",
  "glob_to_pathspec",
]
