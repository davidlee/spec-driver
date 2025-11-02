"""Utilities for Python package detection and identification.

Provides functions to identify leaf packages, validate package paths,
and resolve files to their containing packages. Used for package-level
tech spec granularity (PROD-005).
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from collections.abc import Iterator


def is_leaf_package(path: Path) -> bool:
  """Check if path is a leaf Python package.

  A leaf package is a directory that:
  1. Contains an __init__.py file (is a Python package)
  2. Has no child directories that are also packages

  Args:
      path: Directory path to check

  Returns:
      True if path is a leaf package, False otherwise

  Examples:
      >>> is_leaf_package(Path("supekku/scripts/lib/formatters"))
      True
      >>> is_leaf_package(Path("supekku/scripts/lib"))  # Has child packages
      False

  """
  if not path.is_dir():
    return False

  # Must have __init__.py to be a package
  init_file = path / "__init__.py"
  if not init_file.exists():
    return False

  # Check for child packages
  for child_dir in path.iterdir():
    if child_dir.is_dir():
      child_init = child_dir / "__init__.py"
      if child_init.exists():
        return False  # Has a child package, not a leaf

  return True


def find_package_for_file(file_path: Path) -> Path | None:
  """Find the containing Python package for a given file.

  Traverses up from the file path to find the nearest directory
  containing an __init__.py file (a Python package).

  Args:
      file_path: Path to a Python file

  Returns:
      Path to the containing package directory, or None if not in a package

  Examples:
      >>> file_path = Path("supekku/scripts/lib/formatters/change_formatters.py")
      >>> find_package_for_file(file_path)
      Path("supekku/scripts/lib/formatters")
      >>> find_package_for_file(Path("some_script.py"))
      None

  """
  # Start from the file's directory
  current = file_path.parent if file_path.is_file() else file_path

  # Traverse up until we find a package or reach root
  while current != current.parent:
    init_file = current / "__init__.py"
    if init_file.exists():
      return current
    current = current.parent

  return None


def validate_package_path(path: Path) -> None:
  """Validate that a path is a valid Python package.

  Args:
      path: Directory path to validate

  Raises:
      FileNotFoundError: If path doesn't exist
      ValueError: If path is not a directory
      ValueError: If path doesn't contain __init__.py

  Examples:
      >>> validate_package_path(Path("supekku/cli"))  # OK
      >>> validate_package_path(Path("nonexistent"))
      FileNotFoundError: Package path does not exist: nonexistent
      >>> validate_package_path(Path("some_file.py"))
      ValueError: Package path must be a directory: some_file.py

  """
  if not path.exists():
    msg = f"Package path does not exist: {path}"
    raise FileNotFoundError(msg)

  if not path.is_dir():
    msg = f"Package path must be a directory: {path}"
    raise ValueError(msg)

  init_file = path / "__init__.py"
  if not init_file.exists():
    msg = f"Directory is not a Python package (missing __init__.py): {path}"
    raise ValueError(msg)


def find_all_leaf_packages(root: Path) -> list[Path]:
  """Find all leaf packages under a root directory.

  Recursively searches for all directories that are leaf packages
  (have __init__.py and no child packages).

  Args:
      root: Root directory to search from

  Returns:
      Sorted list of paths to leaf packages

  Examples:
      >>> packages = find_all_leaf_packages(Path("supekku"))
      >>> len(packages)
      16
      >>> Path("supekku/scripts/lib/formatters") in packages
      True

  """
  leaf_packages: list[Path] = []

  # Find all packages first
  all_packages = set(_find_all_packages(root))

  # Filter to leaf packages only
  for pkg in all_packages:
    # Check if any other package is a child of this one
    has_child = any(
      other != pkg and _is_relative_to(other, pkg)
      for other in all_packages
    )
    if not has_child:
      leaf_packages.append(pkg)

  return sorted(leaf_packages)


def _find_all_packages(root: Path) -> Iterator[Path]:
  """Find all Python packages under root (internal helper).

  Args:
      root: Root directory to search

  Yields:
      Paths to all directories containing __init__.py

  """
  if not root.exists() or not root.is_dir():
    return

  for init_file in root.rglob("__init__.py"):
    yield init_file.parent


def _is_relative_to(path: Path, base: Path) -> bool:
  """Check if path is relative to base (Python 3.9+ compatible).

  Args:
      path: Path to check
      base: Base path

  Returns:
      True if path is under base

  """
  try:
    path.relative_to(base)
    return True
  except ValueError:
    return False


__all__ = [
  "find_all_leaf_packages",
  "find_package_for_file",
  "is_leaf_package",
  "validate_package_path",
]
