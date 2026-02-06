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


def is_zig_available() -> bool:
  """Check if zig compiler is available in PATH."""
  return which("zig") is not None


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

  def _find_zig_modules(self, root: Path) -> list[Path]:
    """Find Zig modules (directories with .zig files).

    Returns directories containing .zig files that are likely modules.
    """
    modules = []
    seen_dirs: set[Path] = set()

    for zig_file in root.rglob("*.zig"):
      if self._should_skip_path(zig_file):
        continue

      parent = zig_file.parent
      if parent in seen_dirs:
        continue
      seen_dirs.add(parent)

      # Skip test directories
      if "test" in parent.name.lower() and parent.name != "test":
        continue

      modules.append(parent)

    return sorted(modules)

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

      # Find other Zig modules
      for module_dir in self._find_zig_modules(repo_root):
        # Skip root if already added
        if module_dir == repo_root:
          continue

        rel_path = module_dir.relative_to(repo_root)

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

    # Generate slug parts from path
    if unit.identifier == ".":
      slug_parts = ["root"]
    else:
      slug_parts = unit.identifier.replace("\\", "/").split("/")

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
              "path": "contracts/zig/public.md",
            },
          ],
        },
      ],
    }

    # Document variants
    variants = [
      self._create_doc_variant("public", slug_parts, "zig"),
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
    """Generate documentation for a Zig package/module.

    Uses `zig build-exe --emit=docs` or autodoc when available.

    Args:
        unit: Zig source unit
        spec_dir: Specification directory to write documentation to
        check: If True, only check if docs would change

    Returns:
        List of DocVariant objects with generation results
    """
    self._validate_unit_language(unit)

    # Determine output path
    slug_parts = (
      ["root"]
      if unit.identifier == "."
      else unit.identifier.replace("\\", "/").split("/")
    )
    contracts_dir = spec_dir / "contracts" / "zig"
    output_file = contracts_dir / f"{'-'.join(slug_parts)}-public.md"

    variants = []

    # Check if Zig is available
    if not is_zig_available():
      # Return placeholder variant when Zig isn't available
      if spec_dir in output_file.parents:
        out_path = output_file.relative_to(spec_dir)
      else:
        out_path = output_file
      variants.append(
        DocVariant(
          name="public",
          path=out_path,
          hash="",
          status="unchanged",  # No change possible without toolchain
        ),
      )
      return variants

    # Determine source path
    source_path = self.repo_root / unit.identifier
    if not source_path.exists():
      variants.append(
        DocVariant(
          name="public",
          path=Path(f"contracts/zig/{'-'.join(slug_parts)}-public.md"),
          hash="",
          status="unchanged",  # Source missing, no docs to generate
        ),
      )
      return variants

    # Generate documentation
    try:
      contracts_dir.mkdir(parents=True, exist_ok=True)

      # Check if file exists before generation
      existed_before = output_file.exists()
      old_hash = None
      if existed_before:
        old_content = output_file.read_text(encoding="utf-8")
        old_hash = hashlib.sha256(old_content.encode("utf-8")).hexdigest()

      # Generate basic documentation by parsing Zig files
      doc_content = self._generate_zig_docs(source_path)

      if check:
        # In check mode, compare content
        if not existed_before:
          status = "created"
        else:
          new_hash = hashlib.sha256(doc_content.encode("utf-8")).hexdigest()
          status = "unchanged" if new_hash == old_hash else "changed"
      else:
        # Write documentation
        output_file.write_text(doc_content, encoding="utf-8")

        content_hash = hashlib.sha256(doc_content.encode("utf-8")).hexdigest()
        if not existed_before:
          status = "created"
        elif content_hash != old_hash:
          status = "changed"
        else:
          status = "unchanged"

      doc_hash = "" if check else hashlib.sha256(
        doc_content.encode("utf-8")
      ).hexdigest()
      variants.append(
        DocVariant(
          name="public",
          path=output_file.relative_to(spec_dir),
          hash=doc_hash,
          status=status,
        ),
      )

    except (subprocess.CalledProcessError, OSError):
      variants.append(
        DocVariant(
          name="public",
          path=Path(f"contracts/zig/{'-'.join(slug_parts)}-public.md"),
          hash="",
          status="unchanged",  # Error during generation
        ),
      )

    return variants

  def _generate_zig_docs(self, source_path: Path) -> str:
    """Generate markdown documentation for Zig source.

    Parses Zig files and extracts doc comments and public declarations.

    Args:
        source_path: Path to Zig source file or directory

    Returns:
        Markdown documentation string
    """
    lines = [f"# Zig Module: {source_path.name}", ""]

    if source_path.is_file():
      zig_files = [source_path]
    else:
      zig_files = sorted(source_path.glob("*.zig"))

    for zig_file in zig_files:
      if zig_file.name.startswith("_"):
        continue

      file_docs = self._parse_zig_file(zig_file)
      if file_docs:
        lines.append(f"## {zig_file.name}")
        lines.append("")
        lines.extend(file_docs)
        lines.append("")

    return "\n".join(lines)

  def _parse_zig_file(self, zig_file: Path) -> list[str]:
    """Parse a Zig file and extract documentation.

    Args:
        zig_file: Path to .zig file

    Returns:
        List of documentation lines
    """
    lines = []
    try:
      content = zig_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
      return lines

    current_doc: list[str] = []
    in_doc_comment = False

    for line in content.splitlines():
      stripped = line.strip()

      # Collect doc comments (/// or //!)
      if stripped.startswith("///") or stripped.startswith("//!"):
        doc_text = stripped[3:].strip()
        current_doc.append(doc_text)
        in_doc_comment = True
      elif in_doc_comment:
        # Check if this is a public declaration
        if stripped.startswith("pub "):
          # Extract declaration
          decl = self._extract_declaration(stripped)
          if decl:
            lines.append(f"### `{decl}`")
            lines.append("")
            if current_doc:
              lines.extend(current_doc)
              lines.append("")
        current_doc = []
        in_doc_comment = False

    return lines

  def _extract_declaration(self, line: str) -> str | None:
    """Extract declaration name from a pub line.

    Args:
        line: Line starting with 'pub '

    Returns:
        Declaration signature or None
    """
    # Remove 'pub ' prefix
    rest = line[4:].strip()

    # Handle common declaration types
    for keyword in ["fn ", "const ", "var ", "struct ", "enum ", "union "]:
      if rest.startswith(keyword):
        # Extract up to opening brace or equals
        end_chars = ["{", "=", ";"]
        end_idx = len(rest)
        for char in end_chars:
          idx = rest.find(char)
          if idx != -1 and idx < end_idx:
            end_idx = idx

        return rest[:end_idx].strip()

    return None

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
