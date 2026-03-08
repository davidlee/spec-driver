"""Schema hint output for create commands.

After creating an artifact, suggest relevant `schema show` commands
so users can inspect the YAML block and frontmatter schemas embedded
in the generated template.
"""

from __future__ import annotations

import typer

# Artifact kind -> relevant schema types to suggest inspection of.
# Only includes kinds whose templates contain non-trivial schemas.
# POL-002: named constant, not inline strings.
ARTIFACT_SCHEMA_MAP: dict[str, list[str]] = {
  "delta": ["delta.relationships", "frontmatter.delta"],
  "plan": ["plan.overview", "frontmatter.plan"],
  "phase": ["phase.overview", "phase.tracking"],
  "revision": ["revision.change", "frontmatter.revision"],
  "audit": ["verification.coverage", "frontmatter.audit"],
  "spec": ["spec.relationships", "spec.capabilities", "frontmatter.spec"],
  "prod": ["frontmatter.prod"],
  "policy": ["frontmatter.policy"],
  "standard": ["frontmatter.standard"],
  "memory": ["frontmatter.memory"],
}


def format_schema_hints(artifact_kind: str) -> list[str]:
  """Return schema inspection commands relevant to an artifact kind.

  Pure function: artifact_kind -> list of hint strings.
  Returns empty list for kinds with no registered schemas.
  """
  schemas = ARTIFACT_SCHEMA_MAP.get(artifact_kind, [])
  return [f"  spec-driver schema show {s} -f yaml-example" for s in schemas]


def print_schema_hints(artifact_kind: str) -> None:
  """Print schema inspection hints to stderr for a created artifact.

  No-op for kinds with no registered schemas.
  """
  hints = format_schema_hints(artifact_kind)
  if hints:
    typer.echo("\nInspect embedded schemas:")
    for hint in hints:
      typer.echo(hint)
