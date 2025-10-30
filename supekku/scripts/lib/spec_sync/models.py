"""Core data models for multi-language specification synchronization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal


@dataclass(frozen=True)
class SourceUnit:
    """Canonical identifier for a language-specific source unit.

    Examples:
        - Go package: SourceUnit("go", "internal/foo", Path("/repo"))
        - Python module: SourceUnit("python", "supekku/scripts/lib/workspace.py", Path("/repo"))

    """

    language: str
    identifier: str  # module-relative path or dotted module
    root: Path  # on-disk directory containing the source


@dataclass(frozen=True)
class DocVariant:
    """Named documentation artifact produced per source unit.

    Examples:
        - Go: DocVariant("public", Path("contracts/go/foo-public.md"), "abc123", "created")
        - Python: DocVariant("api", Path("contracts/python/workspace-api.md"), "def456", "changed")

    """

    name: str  # e.g. "public", "all", "tests"
    path: Path  # relative path under contracts/...
    hash: str  # content hash for audit/check mode
    status: Literal["created", "changed", "unchanged"]


@dataclass(frozen=True)
class SourceDescriptor:
    """Metadata describing how a source unit should be processed.
    """

    slug_parts: list[str]  # parts for generating spec slug
    default_frontmatter: dict[str, Any]  # frontmatter defaults for spec
    variants: list[DocVariant]  # documentation variants produced


@dataclass
class SyncOutcome:
    """Results from a specification synchronization operation.
    """

    processed_units: list[SourceUnit] = field(default_factory=list)
    created_specs: dict[str, str] = field(default_factory=dict)  # unit_key -> spec_id
    skipped_units: list[str] = field(default_factory=list)  # reasons for skipping
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
