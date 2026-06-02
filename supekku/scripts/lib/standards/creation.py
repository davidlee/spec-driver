"""Standard creation — thin wrapper around _create_governance_artifact.

Public surface preserved: StandardCreationOptions, StandardCreationResult,
StandardAlreadyExistsError, create_standard.

OQ-2 resolved (accept): record_artifact() now called unconditionally (was
previously missing — the lone omission among governance creators).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from supekku.scripts.lib.creation import (
  _AlreadyExistsError,
  _create_governance_artifact,
  _GovernanceArtifactSpec,
)
from supekku.scripts.lib.standards.registry import StandardRegistry

# ── Public surface (preserved verbatim) ────────────────────────────────────


@dataclass
class StandardCreationOptions:
  """Options for creating a new standard."""

  title: str
  status: str = "draft"
  author: str | None = None
  author_email: str | None = None


@dataclass
class StandardCreationResult:
  """Result of creating a new standard."""

  standard_id: str
  path: Path
  filename: str


class StandardAlreadyExistsError(Exception):
  """Raised when attempting to create a standard file that already exists."""


# ── Per-kind frontmatter builder (Standard-specific fields) ────────────────


def _build_standard_frontmatter(
  standard_id: str, options: StandardCreationOptions
) -> dict[str, Any]:
  """Build frontmatter dictionary for standard."""
  today = date.today().isoformat()
  frontmatter: dict[str, Any] = {
    "id": standard_id,
    "title": f"{standard_id}: {options.title}",
    "status": options.status,
    "created": today,
    "updated": today,
    "reviewed": today,
  }

  if options.author:
    frontmatter["owners"] = [options.author]
  else:
    frontmatter["owners"] = []

  frontmatter.update(
    {
      "supersedes": [],
      "superseded_by": [],
      "policies": [],
      "specs": [],
      "requirements": [],
      "deltas": [],
      "related_policies": [],
      "related_standards": [],
      "tags": [],
      "summary": "",
    },
  )
  return frontmatter


_STANDARD_SPEC = _GovernanceArtifactSpec(
  prefix="STD",
  label="Standard",
  template_name="standard-template.md",
  render_var="standard_id",
  build_frontmatter=_build_standard_frontmatter,
)


# ── Public creation function ───────────────────────────────────────────────


def create_standard(
  registry: StandardRegistry,
  options: StandardCreationOptions,
  *,
  sync_registry: bool = True,
) -> StandardCreationResult:
  """Create a new standard with the next available ID.

  record_artifact() is now called unconditionally (OQ-2: accept).
  """
  try:
    standard_id, path = _create_governance_artifact(
      _STANDARD_SPEC, registry, options, sync_registry=sync_registry
    )
  except _AlreadyExistsError as exc:
    raise StandardAlreadyExistsError(str(exc)) from exc
  return StandardCreationResult(standard_id=standard_id, path=path, filename=path.name)


# ── Legacy helpers (kept for backward compat) ──────────────────────────────


def generate_next_standard_id(registry: StandardRegistry) -> str:
  """Generate the next available standard ID."""
  from supekku.scripts.lib.core.ids import next_sequential_id  # noqa: PLC0415

  return next_sequential_id(registry.collect(), "STD")


def build_standard_frontmatter(
  standard_id: str,
  title: str,
  status: str,
  author: str | None = None,
  author_email: str | None = None,
) -> dict[str, Any]:
  """Build frontmatter dictionary for standard (legacy signature)."""
  return _build_standard_frontmatter(
    standard_id,
    StandardCreationOptions(
      title=title, status=status, author=author, author_email=author_email
    ),
  )


__all__ = [
  "StandardCreationOptions",
  "StandardCreationResult",
  "StandardAlreadyExistsError",
  "generate_next_standard_id",
  "build_standard_frontmatter",
  "create_standard",
]
