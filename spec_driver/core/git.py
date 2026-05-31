"""Git integration utilities for spec-driver.

Provides lightweight wrappers for git operations needed by
artifact verification and staleness tracking.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

SHA_HEX_PATTERN = r"^[0-9a-f]{40}$"
"""Regex pattern matching a full 40-character hex SHA."""

DEFAULT_SHORT_SHA_LENGTH = 8


def get_head_sha(root: Path | None = None) -> str | None:
  """Return full 40-char SHA of HEAD, or None if not in a git repo.

  Args:
    root: Working directory for the git command. Defaults to cwd.

  Returns:
    Full hex SHA string, or None if git is unavailable or not in a repo.
  """
  try:
    result = subprocess.run(  # noqa: S603, S607
      ["git", "rev-parse", "HEAD"],
      capture_output=True,
      text=True,
      timeout=5,
      cwd=root,
      check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None
  except (FileNotFoundError, subprocess.TimeoutExpired):
    return None


def get_branch(root: Path | None = None) -> str | None:
  """Return current branch name, or None if detached/not in a repo."""
  try:
    result = subprocess.run(  # noqa: S603, S607
      ["git", "rev-parse", "--abbrev-ref", "HEAD"],
      capture_output=True,
      text=True,
      timeout=5,
      cwd=root,
      check=False,
    )
    if result.returncode != 0:
      return None
    branch = result.stdout.strip()
    return None if branch == "HEAD" else branch  # detached
  except (FileNotFoundError, subprocess.TimeoutExpired):
    return None


def has_uncommitted_changes(root: Path | None = None) -> bool:
  """Check if working tree has uncommitted changes (unstaged)."""
  try:
    result = subprocess.run(  # noqa: S603, S607
      ["git", "diff", "--quiet"],
      capture_output=True,
      timeout=5,
      cwd=root,
      check=False,
    )
    return result.returncode != 0
  except (FileNotFoundError, subprocess.TimeoutExpired):
    return False


def has_staged_changes(root: Path | None = None) -> bool:
  """Check if index has staged changes."""
  try:
    result = subprocess.run(  # noqa: S603, S607
      ["git", "diff", "--cached", "--quiet"],
      capture_output=True,
      timeout=5,
      cwd=root,
      check=False,
    )
    return result.returncode != 0
  except (FileNotFoundError, subprocess.TimeoutExpired):
    return False


def short_sha(sha: str, length: int = DEFAULT_SHORT_SHA_LENGTH) -> str:
  """Truncate a full SHA for display purposes.

  Args:
    sha: Full hex SHA string.
    length: Number of characters to keep. Defaults to 8.

  Returns:
    Truncated SHA string.
  """
  return sha[:length]


def get_changed_files(
  from_ref: str,
  to_ref: str = "HEAD",
  root: Path | None = None,
) -> list[str]:
  """Return list of files changed between two refs.

  Uses ``git diff --name-only``.  Returns empty list on failure.

  Args:
    from_ref: Base commit ref.
    to_ref: Target commit ref (default HEAD).
    root: Working directory for the git command.

  Returns:
    List of changed file paths (relative to repo root).
  """
  try:
    result = subprocess.run(  # noqa: S603, S607
      ["git", "diff", "--name-only", from_ref, to_ref],
      capture_output=True,
      text=True,
      timeout=10,
      cwd=root,
      check=False,
    )
    if result.returncode != 0:
      return []
    return [f for f in result.stdout.strip().split("\n") if f]
  except (FileNotFoundError, subprocess.TimeoutExpired):
    return []


__all__ = [
  "DEFAULT_SHORT_SHA_LENGTH",
  "SHA_HEX_PATTERN",
  "get_branch",
  "get_changed_files",
  "get_head_sha",
  "has_staged_changes",
  "has_uncommitted_changes",
  "short_sha",
]
