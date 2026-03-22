"""Core data models for multi-language specification synchronization."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class SourceUnit(BaseModel, frozen=True):
  """Canonical identifier for a language-specific source unit.

  Examples:
      - Go package: SourceUnit("go", "internal/foo", Path("/repo"))
      - Python module: SourceUnit("python",
          "supekku/scripts/lib/workspace.py", Path("/repo"))

  """

  language: str
  identifier: str  # module-relative path or dotted module
  root: Path  # on-disk directory containing the source


class DocVariant(BaseModel, frozen=True):
  """Named documentation artifact produced per source unit.

  After generation, ``path`` MUST match the output path provided
  via ``variant_outputs`` to the adapter.  The caller validates
  this contract centrally.  Python adapters may return placeholder
  paths (the caller uses a filesystem scan of the staging dir instead).

  Examples:
      - Go: DocVariant("public",
          Path(".contracts/public/internal/foo/interfaces.md"), ...)
      - Zig: DocVariant("public",
          Path(".contracts/public/src/agent.zig.md"), ...)

  """

  name: str  # e.g. "public", "all", "tests"
  path: Path  # canonical output path (must match variant_outputs value)
  hash: str  # content hash for audit/check mode
  status: Literal["created", "changed", "unchanged"]


class SourceDescriptor(BaseModel, frozen=True):
  """Metadata describing how a source unit should be processed."""

  slug_parts: list[str]  # parts for generating spec slug
  default_frontmatter: dict[str, Any]  # frontmatter defaults for spec
  variants: list[DocVariant]  # documentation variants produced


class SyncOutcome(BaseModel):
  """Results from a specification synchronization operation."""

  model_config = ConfigDict(extra="ignore")

  processed_units: list[SourceUnit] = []
  created_specs: dict[str, str] = {}  # unit_key -> spec_id
  skipped_units: list[str] = []  # reasons for skipping
  warnings: list[str] = []
  errors: list[str] = []
