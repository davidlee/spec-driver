"""Policy creation — thin wrapper around _create_governance_artifact.

Public surface preserved: PolicyCreationOptions, PolicyCreationResult,
PolicyAlreadyExistsError, create_policy.
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
from supekku.scripts.lib.policies.registry import PolicyRegistry


# ── Public surface (preserved verbatim) ────────────────────────────────────


@dataclass
class PolicyCreationOptions:
  """Options for creating a new policy."""

  title: str
  status: str = "draft"
  author: str | None = None
  author_email: str | None = None


@dataclass
class PolicyCreationResult:
  """Result of creating a new policy."""

  policy_id: str
  path: Path
  filename: str


class PolicyAlreadyExistsError(Exception):
  """Raised when attempting to create a policy file that already exists."""


# ── Per-kind frontmatter builder (Policy-specific fields) ──────────────────


def _build_policy_frontmatter(policy_id: str, options: PolicyCreationOptions) -> dict[str, Any]:
  """Build frontmatter dictionary for policy."""
  today = date.today().isoformat()
  frontmatter: dict[str, Any] = {
    "id": policy_id,
    "title": f"{policy_id}: {options.title}",
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
      "standards": [],
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


_POLICY_SPEC = _GovernanceArtifactSpec(
  prefix="POL",
  label="Policy",
  template_name="policy-template.md",
  render_var="policy_id",
  build_frontmatter=_build_policy_frontmatter,
)


# ── Public creation function ───────────────────────────────────────────────


def create_policy(
  registry: PolicyRegistry,
  options: PolicyCreationOptions,
  *,
  sync_registry: bool = True,
) -> PolicyCreationResult:
  """Create a new policy with the next available ID."""
  try:
    policy_id, path = _create_governance_artifact(
      _POLICY_SPEC, registry, options, sync_registry=sync_registry
    )
  except _AlreadyExists as exc:
    raise PolicyAlreadyExistsError(str(exc)) from exc
  return PolicyCreationResult(policy_id=policy_id, path=path, filename=path.name)


# ── Legacy helpers (kept for backward compat) ──────────────────────────────


def generate_next_policy_id(registry: PolicyRegistry) -> str:
  """Generate the next available policy ID."""
  from supekku.scripts.lib.core.ids import next_sequential_id

  return next_sequential_id(registry.collect(), "POL")


def build_policy_frontmatter(
  policy_id: str,
  title: str,
  status: str,
  author: str | None = None,
  author_email: str | None = None,
) -> dict[str, Any]:
  """Build frontmatter dictionary for policy (legacy signature)."""
  return _build_policy_frontmatter(
    policy_id,
    PolicyCreationOptions(title=title, status=status, author=author, author_email=author_email),
  )


__all__ = [
  "PolicyCreationOptions",
  "PolicyCreationResult",
  "PolicyAlreadyExistsError",
  "generate_next_policy_id",
  "build_policy_frontmatter",
  "create_policy",
]
