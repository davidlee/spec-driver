"""Abstract base class for language adapters."""

from __future__ import annotations

import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from shutil import which
from typing import TYPE_CHECKING, ClassVar

from supekku.scripts.lib.spec_sync.models import (
  DocVariant,
  SourceDescriptor,
  SourceUnit,
)

if TYPE_CHECKING:
  from collections.abc import Sequence


class LanguageAdapter(ABC):
  """Abstract interface for language-specific source discovery and documentation.

  Each language adapter is responsible for:
  1. Discovering source units (packages, modules, files) for its language
  2. Describing how source units should be processed (slug, frontmatter, variants)
  3. Generating documentation variants with check mode support
  4. Determining whether it supports a given identifier format
  """

  language: ClassVar[str]  # Language identifier (e.g., "go", "python", "typescript")

  def __init__(self, repo_root: Path) -> None:
    """Initialize adapter with repository root."""
    self.repo_root = repo_root
    self._git_tracked_files: set[Path] | None = None

  def _get_git_tracked_files(self) -> set[Path]:
    """Get set of git-tracked files (cached).

    Returns:
        Set of absolute paths to git-tracked files

    """
    if self._git_tracked_files is not None:
      return self._git_tracked_files

    tracked_files = set()

    # Check if git is available and this is a git repo
    if not which("git"):
      self._git_tracked_files = tracked_files
      return tracked_files

    try:
      result = subprocess.run(
        ["git", "-C", str(self.repo_root), "ls-files"],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
      )
      for line in result.stdout.splitlines():
        if line.strip():
          tracked_files.add(self.repo_root / line.strip())
    except (
      subprocess.CalledProcessError,
      subprocess.TimeoutExpired,
      FileNotFoundError,
    ):
      pass

    self._git_tracked_files = tracked_files
    return tracked_files

  def _should_skip_path(self, path: Path) -> bool:
    """Check if a path should be skipped (shared across all adapters).

    Args:
        path: Path to check

    Returns:
        True if the path should be skipped

    """
    # Skip symlinks (documentation indices, etc.)
    if path.is_symlink():
      return True

    # Skip documentation directories
    path_str = str(path)
    if "/specify/" in path_str or "/change/" in path_str:
      return True

    # Skip files not tracked by git (includes gitignored files)
    # Only apply git filtering if we successfully got tracked files
    tracked_files = self._get_git_tracked_files()
    # Non-empty set means git worked; return True if not in tracked files
    return bool(tracked_files and path.resolve() not in tracked_files)

  def _validate_unit_language(self, unit: SourceUnit) -> None:
    """Validate that the unit language matches this adapter.

    Args:
        unit: Source unit to validate

    Raises:
        ValueError: If unit language doesn't match adapter language

    """
    if unit.language != self.language:
      msg = f"{self.__class__.__name__} cannot process {unit.language} units"
      raise ValueError(
        msg,
      )

  def _create_doc_variant(
    self,
    name: str,
    slug_parts: list[str],
    language_subdir: str,
  ) -> DocVariant:
    """Create a DocVariant with standard placeholder values.

    Args:
        name: Variant name (e.g., "public", "api", "tests")
        slug_parts: Parts to join for the filename
        language_subdir: Language subdirectory (e.g., "go", "python")

    Returns:
        DocVariant with placeholder hash and status

    """
    filename = f"{'-'.join(slug_parts)}-{name}.md"
    return DocVariant(
      name=name,
      path=Path(f"contracts/{language_subdir}/{filename}"),
      hash="",  # Will be filled during generation
      status="unchanged",  # Will be determined during generation
    )

  @abstractmethod
  def discover_targets(
    self,
    repo_root: Path,
    requested: Sequence[str] | None = None,
  ) -> list[SourceUnit]:
    """Discover source units for this language.

    Args:
        repo_root: Root directory of the repository
        requested: Optional list of specific identifiers to process

    Returns:
        List of SourceUnit objects representing discoverable targets

    """

  @abstractmethod
  def describe(self, unit: SourceUnit) -> SourceDescriptor:
    """Describe how a source unit should be processed.

    Args:
        unit: Source unit to describe

    Returns:
        SourceDescriptor with slug parts, frontmatter defaults, and variants

    """

  @abstractmethod
  def generate(
    self,
    unit: SourceUnit,
    *,
    spec_dir: Path,
    check: bool = False,
  ) -> list[DocVariant]:
    """Generate documentation variants for a source unit.

    Args:
        unit: Source unit to generate documentation for
        spec_dir: Specification directory to write documentation to
        check: If True, only check if docs would change (don't write files)

    Returns:
        List of DocVariant objects with generation results

    """

  @abstractmethod
  def supports_identifier(self, identifier: str) -> bool:
    """Check if this adapter can handle the given identifier format.

    Args:
        identifier: Source identifier to check

    Returns:
        True if this adapter can process the identifier

    """
