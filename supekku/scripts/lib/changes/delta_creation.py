"""Delta artifact creation."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Template

from supekku.scripts.lib.blocks.delta import render_delta_relationships_block
from supekku.scripts.lib.changes._creation_utils import (
  ChangeArtifactCreated,
  _ensure_directory,
  _get_template_path,
  _next_identifier,
)
from supekku.scripts.lib.core.events import record_artifact
from supekku.scripts.lib.core.paths import get_deltas_dir
from supekku.scripts.lib.core.spec_utils import dump_markdown_file
from supekku.scripts.lib.specs.creation import (
  extract_template_body,
  find_repository_root,
  slugify,
)

if TYPE_CHECKING:
  from collections.abc import Iterable


def create_delta(
  name: str,
  *,
  specs: Iterable[str] | None = None,
  requirements: Iterable[str] | None = None,
  context_inputs: list[dict[str, str]] | None = None,
  relations: list[dict[str, str]] | None = None,
  repo_root: Path | None = None,
  allow_missing_plan: bool = False,
) -> ChangeArtifactCreated:
  """Create a new delta artifact with optional implementation plan.

  Args:
    name: Delta name/title.
    specs: Spec IDs impacted.
    requirements: Requirement IDs impacted.
    context_inputs: Context input dicts (``{"type": ..., "id": ...}``).
    relations: Relation dicts (``{"type": ..., "target": ...}``).
    repo_root: Optional repository root. Auto-detected if not provided.
    allow_missing_plan: If True, skip creating implementation plan and phases.

  Returns:
    ChangeArtifactCreated with delta details and optional plan/phase paths.
  """
  # Import here to avoid circular dependency — _render_plan is in creation.py
  from supekku.scripts.lib.changes.creation import _render_plan  # noqa: PLC0415

  repo = find_repository_root(repo_root or Path.cwd())
  base_dir = get_deltas_dir(repo)
  _ensure_directory(base_dir)
  delta_id = _next_identifier(base_dir, "DE")
  record_artifact(delta_id)
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
    "relations": list(relations or []),
    "context_inputs": list(context_inputs or []),
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

  design_revision_id = delta_id.replace("DE", "DR", 1)
  design_revision_frontmatter = {
    "id": design_revision_id,
    "slug": slug,
    "name": f"Design Revision - {name}",
    "created": today,
    "updated": today,
    "status": "draft",
    "kind": "design_revision",
    "aliases": [],
    "owners": [],
    "relations": [
      {"type": "implements", "target": delta_id},
    ],
    "delta_ref": delta_id,
    "source_context": [],
    "code_impacts": [],
    "verification_alignment": [],
    "design_decisions": [],
    "open_questions": [],
  }
  design_revision_template_path = _get_template_path("design_revision.md", repo)
  design_revision_template_body = extract_template_body(design_revision_template_path)
  design_revision_template = Template(design_revision_template_body)
  design_revision_body = design_revision_template.render(
    design_revision_id=design_revision_id,
    delta_id=delta_id,
    name=name,
    created=today,
    updated=today,
  )
  design_revision_path = delta_dir / f"{design_revision_id}.md"
  dump_markdown_file(
    design_revision_path,
    design_revision_frontmatter,
    design_revision_body,
  )
  extras.append(design_revision_path)

  if not allow_missing_plan:
    plan_path = _render_plan(
      delta_id,
      delta_dir,
      slug,
      name,
      repo,
      specs=specs,
      requirements=requirements,
    )
    extras.append(plan_path)

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
