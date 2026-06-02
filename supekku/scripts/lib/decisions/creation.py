"""ADR creation — thin wrapper around _create_governance_artifact.

Public surface preserved: ADRCreationOptions, ADRCreationResult,
ADRAlreadyExistsError, create_adr.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from supekku.scripts.lib.creation import (
  _AlreadyExists,
  _GovernanceArtifactSpec,
  _create_governance_artifact,
)
from supekku.scripts.lib.decisions.registry import DecisionRegistry


# ── Public surface (preserved verbatim) ────────────────────────────────────


@dataclass
class ADRCreationOptions:
  """Options for creating a new ADR."""

  title: str
  status: str = "draft"
  author: str | None = None
  author_email: str | None = None


@dataclass
class ADRCreationResult:
  """Result of creating a new ADR."""

  adr_id: str
  path: Path
  filename: str


class ADRAlreadyExistsError(Exception):
  """Raised when attempting to create an ADR file that already exists."""


# ── Per-kind frontmatter builder (ADR-specific fields) ─────────────────────


def _build_adr_frontmatter(adr_id: str, options: ADRCreationOptions) -> dict[str, Any]:
  """Build frontmatter dictionary for ADR."""
  today = date.today().isoformat()
  frontmatter: dict[str, Any] = {
    "id": adr_id,
    "title": f"{adr_id}: {options.title}",
    "status": options.status,
    "created": today,
    "updated": today,
    "reviewed": today,
  }

  if options.author or options.author_email:
    author_info: dict[str, str] = {}
    if options.author:
      author_info["name"] = options.author
    if options.author_email:
      author_info["contact"] = f"mailto:{options.author_email}"
    frontmatter["authors"] = [author_info]

  frontmatter.update(
    {
      "owners": [],
      "supersedes": [],
      "superseded_by": [],
      "policies": [],
      "specs": [],
      "requirements": [],
      "deltas": [],
      "revisions": [],
      "audits": [],
      "related_decisions": [],
      "related_policies": [],
      "tags": [],
      "summary": "",
    },
  )
  return frontmatter


_ADR_SPEC = _GovernanceArtifactSpec(
  prefix="ADR",
  label="ADR",
  template_name="ADR.md",
  render_var="adr_id",
  build_frontmatter=_build_adr_frontmatter,
)


# ── Public creation function ───────────────────────────────────────────────


def create_adr(
  registry: DecisionRegistry,
  options: ADRCreationOptions,
  *,
  sync_registry: bool = True,
) -> ADRCreationResult:
  """Create a new ADR with the next available ID."""
  try:
    adr_id, path = _create_governance_artifact(
      _ADR_SPEC, registry, options, sync_registry=sync_registry
    )
  except _AlreadyExists as exc:
    raise ADRAlreadyExistsError(str(exc)) from exc
  return ADRCreationResult(adr_id=adr_id, path=path, filename=path.name)


# ── Legacy helpers (kept for backward compat — thin wrappers) ──────────────


def generate_next_adr_id(registry: DecisionRegistry) -> str:
  """Generate the next available ADR ID."""
  from supekku.scripts.lib.core.ids import next_sequential_id

  return next_sequential_id(registry.collect(), "ADR")


def build_adr_frontmatter(
  adr_id: str,
  title: str,
  status: str,
  author: str | None = None,
  author_email: str | None = None,
) -> dict[str, Any]:
  """Build frontmatter dictionary for ADR (legacy signature)."""
  return _build_adr_frontmatter(
    adr_id,
    ADRCreationOptions(title=title, status=status, author=author, author_email=author_email),
  )


__all__ = [
  "ADRCreationOptions",
  "ADRCreationResult",
  "ADRAlreadyExistsError",
  "generate_next_adr_id",
  "build_adr_frontmatter",
  "create_adr",
]
