"""Zig language adapter for specification synchronization."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from shutil import which
from typing import TYPE_CHECKING, ClassVar

from supekku.scripts.lib.sync.models import (
  DocVariant,
  SourceDescriptor,
  SourceUnit,
)

from .base import LanguageAdapter

if TYPE_CHECKING:
  from collections.abc import Sequence


class ZigToolchainNotAvailableError(RuntimeError):
  """Raised when Zig toolchain is required but not available."""


class ZigmarkdocNotAvailableError(RuntimeError):
  """Raised when zigmarkdoc is required but not available."""


def is_zig_available() -> bool:
  """Check if zig compiler is available in PATH."""
  return which("zig") is not None


def is_zigmarkdoc_available() -> bool:
  """Check if zigmarkdoc is available in PATH."""
  return which("zigmarkdoc") is not None


class ZigAdapter(LanguageAdapter):
  """Language adapter for Zig modules and packages.

  Discovers Zig source files and packages, generates documentation using
  autodoc when available.
  """

  language: ClassVar[str] = "zig"

  def _is_zig_package(self, path: Path) -> bool:
    """Check if directory is a Zig package.

    A Zig package is identified by:
    - build.zig in the directory
    - src/ subdirectory with .zig files
    - build.zig.zon (Zig package manifest)
    """
    if not path.is_dir():
      return False

    # Check for build.zig or build.zig.zon
    if (path / "build.zig").exists() or (path / "build.zig.zon").exists():
      return True

    # Check for src/ with .zig files
    src_dir = path / "src"
    if src_dir.exists() and src_dir.is_dir():
      return any(src_dir.glob("*.zig"))

    return False

  def _find_zig_files(self, root: Path) -> list[Path]:
    """Find Zig source files.

    Returns individual .zig files (Zig is per-file, not per-directory).
    """
    zig_files = []

    for zig_file in root.rglob("*.zig"):
      if self._should_skip_path(zig_file):
        continue

      # Skip test files
      if "test" in zig_file.name.lower():
        continue

      zig_files.append(zig_file)

    return sorted(zig_files)

  def discover_targets(
    self,
    repo_root: Path,
    requested: Sequence[str] | None = None,
  ) -> list[SourceUnit]:
    """Discover Zig packages and modules.

    Args:
        repo_root: Root directory of the repository
        requested: Optional list of specific paths to process

    Returns:
        List of SourceUnit objects for Zig packages/modules
    """
    source_units = []

    if requested:
      # Process specific requested paths
      for item in requested:
        path = repo_root / item
        if path.exists():
          is_zig_dir = path.is_dir() and self._is_zig_package(path)
          is_zig_file = path.is_file() and path.suffix == ".zig"
          if is_zig_dir or is_zig_file:
            identifier = str(path.relative_to(repo_root))
          else:
            identifier = item

          source_units.append(
            SourceUnit(
              language=self.language,
              identifier=identifier,
              root=repo_root,
            ),
          )
    else:
      # Auto-discover Zig packages
      # First, check if repo root is a Zig package
      if self._is_zig_package(repo_root):
        source_units.append(
          SourceUnit(
            language=self.language,
            identifier=".",
            root=repo_root,
          ),
        )

      # Find other Zig files
      for zig_file in self._find_zig_files(repo_root):
        # Skip build.zig if root package already added
        if self._is_zig_package(repo_root) and zig_file.name == "build.zig":
          continue

        rel_path = zig_file.relative_to(repo_root)

        # Skip vendor, zig-cache, zig-out directories
        rel_str = str(rel_path)
        if any(
          skip in rel_str
          for skip in ["zig-cache", "zig-out", "vendor", ".zig-cache"]
        ):
          continue

        source_units.append(
          SourceUnit(
            language=self.language,
            identifier=str(rel_path),
            root=repo_root,
          ),
        )

    return source_units

  def describe(self, unit: SourceUnit) -> SourceDescriptor:
    """Describe how a Zig package/module should be processed.

    Args:
        unit: Zig source unit

    Returns:
        SourceDescriptor with Zig-specific metadata
    """
    self._validate_unit_language(unit)

    # Generate slug parts from file path (Zig is per-file)
    # e.g., "src/utils.zig" -> ["src", "utils-zig"]
    if unit.identifier == ".":
      slug_parts = ["root"]
    else:
      path_parts = unit.identifier.replace("\\", "/").split("/")
      # Replace .zig extension with -zig in the filename
      if path_parts[-1].endswith(".zig"):
        path_parts[-1] = path_parts[-1].replace(".zig", "-zig")
      slug_parts = path_parts

    # Default frontmatter for Zig packages
    default_frontmatter = {
      "packages": [unit.identifier],
      "sources": [
        {
          "language": "zig",
          "identifier": unit.identifier,
          "variants": [
            {
              "name": "public",
              "path": "contracts/interfaces.md",
            },
            {
              "name": "internal",
              "path": "contracts/internals.md",
            },
          ],
        },
      ],
    }

    # Document variants that will be generated
    variants = [
      DocVariant(
        name="public",
        path=Path("contracts/interfaces.md"),
        hash="",
        status="unchanged",
      ),
      DocVariant(
        name="internal",
        path=Path("contracts/internals.md"),
        hash="",
        status="unchanged",
      ),
    ]

    return SourceDescriptor(
      slug_parts=slug_parts,
      default_frontmatter=default_frontmatter,
      variants=variants,
    )

  def generate(
    self,
    unit: SourceUnit,
    *,
    spec_dir: Path,
    check: bool = False,
  ) -> list[DocVariant]:
    """Generate documentation for a Zig package/module using zigmarkdoc.

    Args:
        unit: Zig source unit
        spec_dir: Specification directory to write documentation to
        check: If True, only check if docs would change

    Returns:
        List of DocVariant objects with generation results

    Raises:
        ZigmarkdocNotAvailableError: If zigmarkdoc is not available
        FileNotFoundError: If source path does not exist
    """
    self._validate_unit_language(unit)

    # Check if zigmarkdoc is available
    if not is_zigmarkdoc_available():
      raise ZigmarkdocNotAvailableError(
        "zigmarkdoc not found in PATH. Please install it from: "
        "https://github.com/davidlee/zigmarkdoc"
      )

    # Determine source path (should be a .zig file)
    source_path = self.repo_root / unit.identifier
    if not source_path.exists():
      msg = f"Source path does not exist: {source_path}"
      raise FileNotFoundError(msg)

    # Verify it's a .zig file (Zig modules are per-file, not per-directory)
    if not source_path.is_file() or source_path.suffix != ".zig":
      msg = f"Source path must be a .zig file, got: {source_path}"
      raise ValueError(msg)

    # Determine output paths within spec directory
    contracts_dir = spec_dir / "contracts"
    public_output = contracts_dir / "interfaces.md"
    internal_output = contracts_dir / "internals.md"

    variants = []

    # Generate public docs (interfaces)
    try:
      if check and not public_output.exists():
        # In check mode, if file doesn't exist, it's missing
        variants.append(
          DocVariant(
            name="public",
            path=public_output.relative_to(spec_dir),
            hash="",
            status="created",  # Would be created
          ),
        )
      else:
        # Generate or check public docs
        contracts_dir.mkdir(parents=True, exist_ok=True)

        content_hash = ""
        if check:
          # Check mode - run zigmarkdoc --check
          cmd = [
            "zigmarkdoc",
            "--check",
            "--output",
            str(public_output),
            str(source_path),
          ]
          try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            status = "unchanged"
          except subprocess.CalledProcessError:
            status = "changed"  # Would be changed
        else:
          # Check if file exists before generation
          existed_before = public_output.exists()
          old_hash = None
          if existed_before:
            old_content = public_output.read_text(encoding="utf-8")
            old_hash = hashlib.sha256(
              old_content.encode("utf-8"),
            ).hexdigest()

          # Generate mode
          cmd = [
            "zigmarkdoc",
            "--output",
            str(public_output),
            str(source_path),
          ]
          subprocess.run(cmd, check=True, capture_output=True, text=True)

          # Determine status by checking if file changed
          content_hash = ""
          if public_output.exists():
            content = public_output.read_text(encoding="utf-8")
            content_hash = hashlib.sha256(
              content.encode("utf-8"),
            ).hexdigest()

            if not existed_before:
              status = "created"
            elif content_hash != old_hash:
              status = "changed"
            else:
              status = "unchanged"
          else:
            status = "created"

        variants.append(
          DocVariant(
            name="public",
            path=public_output.relative_to(spec_dir),
            hash=content_hash if not check else "",
            status=status,
          ),
        )

    except subprocess.CalledProcessError:
      # Handle zigmarkdoc errors gracefully
      variants.append(
        DocVariant(
          name="public",
          path=public_output.relative_to(spec_dir) if public_output else Path(),
          hash="",
          status="unchanged",  # Error status would be handled at higher level
        ),
      )

    # Generate internal docs (with private symbols)
    try:
      if check and not internal_output.exists():
        variants.append(
          DocVariant(
            name="internal",
            path=internal_output.relative_to(spec_dir),
            hash="",
            status="created",
          ),
        )
      else:
        content_hash = ""
        if check:
          cmd = [
            "zigmarkdoc",
            "--check",
            "--include-private",
            "--output",
            str(internal_output),
            str(source_path),
          ]
          try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            status = "unchanged"
          except subprocess.CalledProcessError:
            status = "changed"
        else:
          # Check if file exists before generation
          existed_before = internal_output.exists()
          old_hash = None
          if existed_before:
            old_content = internal_output.read_text(encoding="utf-8")
            old_hash = hashlib.sha256(
              old_content.encode("utf-8"),
            ).hexdigest()

          cmd = [
            "zigmarkdoc",
            "--include-private",
            "--output",
            str(internal_output),
            str(source_path),
          ]
          subprocess.run(cmd, check=True, capture_output=True, text=True)

          if internal_output.exists():
            content = internal_output.read_text(encoding="utf-8")
            content_hash = hashlib.sha256(
              content.encode("utf-8"),
            ).hexdigest()

            if not existed_before:
              status = "created"
            elif content_hash != old_hash:
              status = "changed"
            else:
              status = "unchanged"
          else:
            status = "created"

        variants.append(
          DocVariant(
            name="internal",
            path=internal_output.relative_to(spec_dir),
            hash=content_hash if not check else "",
            status=status,
          ),
        )

    except subprocess.CalledProcessError:
      variants.append(
        DocVariant(
          name="internal",
          path=internal_output.relative_to(spec_dir) if internal_output else Path(),
          hash="",
          status="unchanged",
        ),
      )

    return variants


  def supports_identifier(self, identifier: str) -> bool:
    """Check if identifier looks like a Zig path.

    Args:
        identifier: Identifier to check

    Returns:
        True if identifier appears to be a Zig source path
    """
    if not identifier:
      return False

    # Explicit Zig file
    if identifier.endswith(".zig"):
      return True

    # Check if path exists and contains Zig files
    path = self.repo_root / identifier
    if path.exists():
      if path.is_file():
        return path.suffix == ".zig"
      if path.is_dir():
        return self._is_zig_package(path) or any(path.glob("*.zig"))

    # Check for Zig-specific patterns
    zig_patterns = ["src/", "lib/", "build.zig"]
    return any(pattern in identifier for pattern in zig_patterns)
