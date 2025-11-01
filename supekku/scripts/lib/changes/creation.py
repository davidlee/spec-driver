"""Utilities for creating change artifacts like deltas and revisions."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Template

from supekku.scripts.lib.blocks.delta import render_delta_relationships_block
from supekku.scripts.lib.blocks.plan import (
  render_phase_overview_block,
  render_plan_overview_block,
)
from supekku.scripts.lib.blocks.verification import render_verification_coverage_block
from supekku.scripts.lib.core.paths import get_templates_dir
from supekku.scripts.lib.core.spec_utils import dump_markdown_file
from supekku.scripts.lib.specs.creation import (
  extract_template_body,
  find_repository_root,
  slugify,
)
from supekku.scripts.lib.specs.registry import SpecRegistry

if TYPE_CHECKING:
  from collections.abc import Iterable


def _get_template_path(name: str, repo_root: Path | None = None) -> Path:
  """Get path to template file in user's .spec-driver/templates directory."""
  return get_templates_dir(repo_root) / name


@dataclass(frozen=True)
class ChangeArtifactCreated:
  """Result information from creating a change artifact."""

  artifact_id: str
  directory: Path
  primary_path: Path
  extras: list[Path]


def _next_identifier(base_dir: Path, prefix: str) -> str:
  highest = 0
  if base_dir.exists():
    for entry in base_dir.iterdir():
      match = re.search(rf"{prefix}-(\d{{3,}})", entry.name)
      if match:
        try:
          highest = max(highest, int(match.group(1)))
        except ValueError:
          continue
  return f"{prefix}-{highest + 1:03d}"


def _ensure_directory(path: Path) -> None:
  path.mkdir(parents=True, exist_ok=True)


# Old rendering functions and regex patterns removed.
# Block rendering now uses canonical functions from blocks package.


def create_revision(
  name: str,
  *,
  _summary: str | None = None,
  source_specs: Iterable[str] | None = None,
  destination_specs: Iterable[str] | None = None,
  requirements: Iterable[str] | None = None,
  repo_root: Path | None = None,
) -> ChangeArtifactCreated:
  """Create a new spec revision artifact.

  Args:
    name: Revision name/title.
    summary: Optional summary text.
    source_specs: Spec IDs being revised from.
    destination_specs: Spec IDs being revised to.
    requirements: Requirement IDs affected.
    repo_root: Optional repository root. Auto-detected if not provided.

  Returns:
    ChangeArtifactCreated with revision details.
  """
  repo = find_repository_root(repo_root or Path.cwd())
  base_dir = repo / "change" / "revisions"
  _ensure_directory(base_dir)
  revision_id = _next_identifier(base_dir, "RE")
  today = date.today().isoformat()
  slug = slugify(name) or "revision"
  revision_dir = base_dir / f"{revision_id}-{slug}"
  _ensure_directory(revision_dir)

  frontmatter = {
    "id": revision_id,
    "slug": slug,
    "name": f"Spec Revision - {name}",
    "created": today,
    "updated": today,
    "status": "draft",
    "kind": "revision",
    "aliases": [],
    "relations": [],
  }
  if source_specs:
    frontmatter["source_specs"] = sorted(set(source_specs))
  if destination_specs:
    frontmatter["destination_specs"] = sorted(set(destination_specs))
  if requirements:
    frontmatter["requirements"] = sorted(set(requirements))

  # Load template and render with Jinja2
  template_path = _get_template_path("revision.md", repo)
  template_body = extract_template_body(template_path)
  template = Template(template_body)
  body = template.render(
    revision_id=revision_id,
    name=name,
    created=today,
    updated=today,
  )

  revision_path = revision_dir / f"{revision_id}.md"
  dump_markdown_file(revision_path, frontmatter, body)
  return ChangeArtifactCreated(
    artifact_id=revision_id,
    directory=revision_dir,
    primary_path=revision_path,
    extras=[],
  )


def create_delta(
  name: str,
  *,
  specs: Iterable[str] | None = None,
  requirements: Iterable[str] | None = None,
  repo_root: Path | None = None,
  allow_missing_plan: bool = False,
) -> ChangeArtifactCreated:
  """Create a new delta artifact with optional implementation plan.

  Args:
    name: Delta name/title.
    specs: Spec IDs impacted.
    requirements: Requirement IDs impacted.
    repo_root: Optional repository root. Auto-detected if not provided.
    allow_missing_plan: If True, skip creating implementation plan and phases.

  Returns:
    ChangeArtifactCreated with delta details and optional plan/phase paths.
  """
  repo = find_repository_root(repo_root or Path.cwd())
  base_dir = repo / "change" / "deltas"
  _ensure_directory(base_dir)
  delta_id = _next_identifier(base_dir, "DE")
  today = date.today().isoformat()
  slug = slugify(name) or "delta"
  delta_dir = base_dir / f"{delta_id}-{slug}"
  _ensure_directory(delta_dir)

  frontmatter = {
    "id": delta_id,
    "slug": slug,
    "name": f"Delta - {name}",
    "created": today,
    "updated": today,
    "status": "draft",
    "kind": "delta",
    "aliases": [],
    "relations": [],
    "applies_to": {
      "specs": sorted(set(specs or [])),
      "requirements": sorted(set(requirements or [])),
    },
  }

  # Render YAML blocks
  relationships_block = render_delta_relationships_block(
    delta_id,
    primary_specs=list(specs or []),
    implements_requirements=list(requirements or []),
  )

  # Load template and render with Jinja2
  template_path = _get_template_path("delta.md", repo)
  template_body = extract_template_body(template_path)
  template = Template(template_body)
  body = template.render(
    delta_id=delta_id,
    name=name,
    created=today,
    updated=today,
    delta_relationships_block=relationships_block,
  )

  delta_path = delta_dir / f"{delta_id}.md"
  dump_markdown_file(delta_path, frontmatter, body)

  extras: list[Path] = []
  plan_id = delta_id.replace("DE", "IP")
  if not allow_missing_plan:
    # Render YAML blocks
    first_phase_id = f"{plan_id}.PHASE-01"
    plan_overview_block = render_plan_overview_block(
      plan_id,
      delta_id,
      primary_specs=list(specs or []),
      target_requirements=list(requirements or []),
      first_phase_id=first_phase_id,
    )

    # Render verification block for plan
    first_req = list(requirements or [])[0] if requirements else "SPEC-YYY.FR-001"
    plan_verification_block = render_verification_coverage_block(
      plan_id,
      entries=[
        {
          "artefact": "VT-XXX",
          "kind": "VT",
          "requirement": first_req,
          "phase": first_phase_id,
          "status": "planned",
          "notes": "Link to evidence (test run, audit, validation artefact).",
        }
      ],
    )

    # Load and render template
    plan_template_path = _get_template_path("plan.md", repo)
    plan_template_body = extract_template_body(plan_template_path)
    plan_template = Template(plan_template_body)
    plan_body = plan_template.render(
      plan_id=plan_id,
      delta_id=delta_id,
      plan_overview_block=plan_overview_block,
      plan_verification_block=plan_verification_block,
    )
    plan_frontmatter = {
      "id": plan_id,
      "slug": slug,
      "name": f"Implementation Plan - {name}",
      "created": today,
      "updated": today,
      "status": "draft",
      "kind": "plan",
      "aliases": [],
    }
    plan_path = delta_dir / f"{plan_id}.md"
    dump_markdown_file(plan_path, plan_frontmatter, plan_body)
    extras.append(plan_path)

    phases_dir = delta_dir / "phases"
    _ensure_directory(phases_dir)

    # Render YAML blocks for phase
    phase_id = f"{plan_id}.PHASE-01"
    phase_overview_block = render_phase_overview_block(
      phase_id,
      plan_id,
      delta_id,
    )

    # Load and render phase template
    phase_template_path = _get_template_path("phase.md", repo)
    phase_template_body = extract_template_body(phase_template_path)
    phase_template = Template(phase_template_body)
    phase_body = phase_template.render(
      phase_id=phase_id,
      plan_id=plan_id,
      delta_id=delta_id,
      phase_overview_block=phase_overview_block,
    )
    phase_path = phases_dir / "phase-01.md"
    dump_markdown_file(
      phase_path,
      {
        "id": f"{plan_id}.PHASE-01",
        "slug": f"{slug}-phase-01",
        "name": f"{plan_id} Phase 01",
        "created": today,
        "updated": today,
        "status": "draft",
        "kind": "phase",
      },
      phase_body,
    )
    extras.append(phase_path)

  notes_path = delta_dir / "notes.md"
  if not notes_path.exists():
    notes_path.write_text(f"# Notes for {delta_id}\n\n", encoding="utf-8")
    extras.append(notes_path)

  return ChangeArtifactCreated(
    artifact_id=delta_id,
    directory=delta_dir,
    primary_path=delta_path,
    extras=extras,
  )


def create_requirement_breakout(
  spec_id: str,
  requirement_id: str,
  *,
  title: str,
  kind: str | None = None,
  repo_root: Path | None = None,
) -> Path:
  """Create a breakout requirement file under a spec.

  Args:
    spec_id: Parent spec identifier.
    requirement_id: Requirement code (e.g., FR-010).
    title: Requirement title.
    kind: Optional requirement kind. Defaults based on requirement_id prefix.
    repo_root: Optional repository root. Auto-detected if not provided.

  Returns:
    Path to created requirement file.

  Raises:
    ValueError: If spec is not found.
  """
  spec_id = spec_id.upper()
  requirement_id = requirement_id.upper()
  repo = find_repository_root(repo_root or Path.cwd())
  spec_registry = SpecRegistry(repo)
  spec = spec_registry.get(spec_id)
  if spec is None:
    msg = f"Spec {spec_id} not found"
    raise ValueError(msg)

  requirement_kind = kind or (
    "functional" if requirement_id.startswith("FR-") else "non-functional"
  )
  today = date.today().isoformat()

  requirements_dir = spec.path.parent / "requirements"
  _ensure_directory(requirements_dir)
  requirement_slug = slugify(title) or requirement_id.lower()
  path = requirements_dir / f"{requirement_id}.md"

  frontmatter = {
    "id": f"{spec_id}.{requirement_id}",
    "slug": requirement_slug,
    "name": f"Requirement - {title}",
    "created": today,
    "updated": today,
    "status": "draft",
    "kind": "requirement",
    "requirement_kind": requirement_kind,
    "spec": spec_id,
  }
  body = f"""# {requirement_id} - {title}

## Statement
> TODO

## Rationale
> TODO

## Verification
> TODO

## Notes
> TODO
"""

  dump_markdown_file(path, frontmatter, body)
  return path


__all__ = [
  "ChangeArtifactCreated",
  "create_delta",
  "create_requirement_breakout",
  "create_revision",
]
