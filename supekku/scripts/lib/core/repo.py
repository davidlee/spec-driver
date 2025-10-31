"""Repository discovery utilities."""

from __future__ import annotations

from pathlib import Path


def find_repo_root(start: Path | None = None) -> Path:
  """Find repository root from starting path.

  Args:
    start: Path to start searching from. Defaults to current directory.

  Returns:
    Repository root path.

  Raises:
    RuntimeError: If repository root cannot be found.
  """
  from .paths import SPEC_DRIVER_DIR  # noqa: PLC0415

  current = (start or Path.cwd()).resolve()
  for candidate in [current, *current.parents]:
    if (candidate / ".git").exists() or (candidate / SPEC_DRIVER_DIR).exists():
      return candidate
  msg = (
    f"Could not locate repository root (missing .git or {SPEC_DRIVER_DIR} directory)"
  )
  raise RuntimeError(msg)


__all__ = ["find_repo_root"]
