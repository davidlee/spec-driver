"""TypeScript language adapter for specification synchronization (STUB).

This is a placeholder implementation for future TypeScript support.
Currently returns not implemented errors for all operations.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import ClassVar

from ..models import DocVariant, SourceDescriptor, SourceUnit
from .base import LanguageAdapter


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

    def __init__(self, repo_root: Path):
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

        Raises:
            NotImplementedError: TypeScript discovery not yet implemented

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

        # Auto-discovery not yet implemented
        # TODO: Implement TypeScript file discovery (.ts, .tsx files)
        # TODO: Handle node_modules exclusion
        # TODO: Support TypeScript project structure (src/, lib/, etc.)
        raise NotImplementedError(
            "TypeScript auto-discovery not yet implemented. "
            "Use explicit targets with typescript:path/to/file.ts syntax.",
        )

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
        self, unit: SourceUnit, *, spec_dir: Path, check: bool = False,
    ) -> list[DocVariant]:
        """Generate documentation variants for a TypeScript source unit.

        Args:
            unit: Source unit to generate documentation for
            spec_dir: Specification directory to write documentation to
            check: If True, only check if docs would change

        Returns:
            List of DocVariant objects with generation results

        Raises:
            ValueError: If unit is not a TypeScript unit
            NotImplementedError: TypeScript generation not yet implemented

        """
        self._validate_unit_language(unit)

        # TODO: Implement TypeScript documentation generation
        # Options to evaluate:
        # 1. TypeDoc integration
        # 2. Custom TypeScript AST parser
        # 3. TSDoc comment extraction
        # 4. Integration with existing TypeScript tooling

        raise NotImplementedError(
            f"TypeScript documentation generation not yet implemented for {unit.identifier}. "
            "This is a placeholder adapter - see TODO items in typescript.py",
        )

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

        # If it has TypeScript-style indicators and no clear non-TS patterns
        if any(indicator in identifier for indicator in typescript_indicators):
            return True

        # Default to False for ambiguous cases to avoid conflicts with Go adapter
        return False


__all__ = ["TypeScriptAdapter"]
