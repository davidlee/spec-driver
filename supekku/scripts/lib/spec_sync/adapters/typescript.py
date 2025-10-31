"""TypeScript language adapter for specification synchronization (STUB).

This is a placeholder implementation for future TypeScript support.
Currently returns not implemented errors for all operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from supekku.scripts.lib.spec_sync.models import (
  DocVariant,
  SourceDescriptor,
  SourceUnit,
)

from .base import LanguageAdapter

if TYPE_CHECKING:
  from collections.abc import Sequence
  from pathlib import Path


class TypeScriptAdapter(LanguageAdapter):
  """Language adapter for TypeScript modules (STUB IMPLEMENTATION).

  This is a placeholder implementation that provides the interface
  for TypeScript support but does not yet implement documentation
  generation. Future implementation should integrate with TypeDoc
  or a custom AST-based documentation generator.

  TODO: Implement actual TypeScript documentation generation
  TODO: Evaluate TypeDoc vs custom AST solution
  TODO: Define variant mapping (public/internal/tests)
  TODO: Implement source discovery patterns
  """

  language: ClassVar[str] = "typescript"

  def __init__(self, repo_root: Path) -> None:
    """Initialize TypeScript adapter.

    Args:
        repo_root: Root directory of the repository

    """
    self.repo_root = repo_root

  def discover_targets(
    self,
    repo_root: Path,
    requested: Sequence[str] | None = None,
  ) -> list[SourceUnit]:
    """Discover TypeScript modules for documentation.

    Args:
        repo_root: Root directory of the repository
        requested: Optional list of specific module paths to process

    Returns:
        List of SourceUnit objects for TypeScript modules

    """
    if requested:
      # For now, just create placeholder units for requested identifiers
      # This allows testing the adapter interface
      source_units = []
      for identifier in requested:
        if self.supports_identifier(identifier):
          unit = SourceUnit("typescript", identifier, repo_root)
          source_units.append(unit)
      return source_units

    # Auto-discovery: find TypeScript files
    # Exclude common directories we don't want to document
    exclude_dirs = {
      "node_modules",
      ".git",
      "dist",
      "build",
      "coverage",
      ".next",
      ".nuxt",
      "out",
      "__pycache__",
      ".pytest_cache",
      ".venv",
      "venv",
      ".uv-cache",
      ".cache",
      "target",
      "tmp",
      "temp",
    }

    source_units = []

    # Find all .ts, .tsx files (excluding .d.ts for now)
    for ext in ["*.ts", "*.tsx"]:
      for ts_file in repo_root.rglob(ext):
        # Skip if in excluded directory
        if any(excluded in ts_file.parts for excluded in exclude_dirs):
          continue

        # Skip type definition files for now
        if ts_file.name.endswith(".d.ts"):
          continue

        # Use base class helper to skip non-git-tracked files
        if self._should_skip_path(ts_file):
          continue

        # Get relative path from repo root
        try:
          relative_path = ts_file.relative_to(repo_root)
          identifier = str(relative_path)
          unit = SourceUnit("typescript", identifier, repo_root)
          source_units.append(unit)
        except ValueError:
          # File not relative to repo_root, skip
          continue

    return source_units

  def describe(self, unit: SourceUnit) -> SourceDescriptor:
    """Describe how a TypeScript source unit should be processed.

    Args:
        unit: Source unit to describe

    Returns:
        SourceDescriptor with placeholder metadata

    Raises:
        ValueError: If unit is not a TypeScript unit

    """
    self._validate_unit_language(unit)

    # Create slug parts from identifier path
    # Remove .ts/.tsx extension and convert to slug parts
    identifier = unit.identifier
    if identifier.endswith((".ts", ".tsx")):
      identifier = identifier.rsplit(".", 1)[0]

    slug_parts = identifier.replace("/", "-").split("-")
    slug_parts = [part for part in slug_parts if part]  # Remove empty parts

    # Create placeholder variants
    # TODO: Define appropriate variants for TypeScript
    # Possible variants: public, internal, tests, types
    variants = [
      self._create_doc_variant("public", slug_parts, "typescript"),
      self._create_doc_variant("internal", slug_parts, "typescript"),
      self._create_doc_variant("types", slug_parts, "typescript"),
    ]

    # Create frontmatter with TypeScript-specific metadata
    frontmatter = {
      "sources": [
        {
          "language": "typescript",
          "identifier": unit.identifier,
          "variants": [
            {
              "name": variant.name,
              "path": str(variant.path),
            }
            for variant in variants
          ],
        },
      ],
    }

    return SourceDescriptor(
      slug_parts=slug_parts,
      default_frontmatter=frontmatter,
      variants=variants,
    )

  def generate(
    self,
    unit: SourceUnit,
    *,
    spec_dir: Path,
    check: bool = False,
  ) -> list[DocVariant]:
    """Generate documentation variants for a TypeScript source unit (NOOP).

    This is a placeholder implementation that skips actual documentation
    generation. It returns placeholder variants marked as 'skipped' until
    the AST-based doc generator is implemented.

    Args:
        unit: Source unit to generate documentation for
        spec_dir: Specification directory to write documentation to
        check: If True, only check if docs would change

    Returns:
        List of DocVariant objects with 'skipped' status

    Raises:
        ValueError: If unit is not a TypeScript unit

    """
    self._validate_unit_language(unit)

    # Get the descriptor to know what variants would be created
    descriptor = self.describe(unit)

    # Return placeholder variants with 'skipped' status
    # This allows the sync to proceed without generating docs
    return [
      DocVariant(
        name=variant.name,
        path=variant.path,
        hash="",  # Empty hash for skipped generation
        status="skipped",
      )
      for variant in descriptor.variants
    ]

  def supports_identifier(self, identifier: str) -> bool:
    """Check if this adapter can handle TypeScript identifiers.

    Args:
        identifier: Source identifier to check

    Returns:
        True if identifier looks like a TypeScript file path

    """
    # Handle empty string
    if not identifier:
      return False

    # Support TypeScript file extensions (most reliable indicator)
    if identifier.endswith((".ts", ".tsx", ".d.ts")):
      return True

    # Exclude obvious non-TypeScript patterns
    exclude_patterns = [
      # Python patterns
      ".py",
      ".pyc",
      "__pycache__",
      # Go patterns
      ".go",
      # Other non-TypeScript files
      ".txt",
      ".md",
      ".json",
      ".yaml",
      ".yml",
      ".xml",
      ".html",
      ".css",
      ".scss",
      ".less",
      ".jpg",
      ".png",
      ".gif",
      ".svg",
      "Dockerfile",
      "Makefile",
      "LICENSE",
      "README",
    ]

    if any(pattern in identifier for pattern in exclude_patterns):
      return False

    # Support TypeScript-style module paths (without extension)
    # Be more conservative - only support if it has clear TypeScript indicators
    typescript_indicators = [
      "src/",
      "lib/",
      "dist/",
      "types/",
      "components/",
      "services/",
      "utils/",
      "helpers/",
      "hooks/",
      "node_modules/",
      "@types/",
      ".component",
      ".service",
      ".module",
      ".spec",
      ".test",
    ]

    # Return True if it has TypeScript-style indicators
    # Default to False for ambiguous cases to avoid conflicts with Go adapter
    return any(indicator in identifier for indicator in typescript_indicators)


__all__ = ["TypeScriptAdapter"]
