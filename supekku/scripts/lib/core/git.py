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


def short_sha(sha: str, length: int = DEFAULT_SHORT_SHA_LENGTH) -> str:
  """Truncate a full SHA for display purposes.

  Args:
    sha: Full hex SHA string.
    length: Number of characters to keep. Defaults to 8.

  Returns:
    Truncated SHA string.
  """
  return sha[:length]


__all__ = [
  "DEFAULT_SHORT_SHA_LENGTH",
  "SHA_HEX_PATTERN",
  "get_head_sha",
  "short_sha",
]
