"""Revision artifact creation."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Template

from supekku.scripts.lib.blocks.revision import render_revision_change_block
from supekku.scripts.lib.changes._creation_utils import (
  ChangeArtifactCreated,
  _ensure_directory,
  _get_template_path,
  _next_identifier,
)
from supekku.scripts.lib.core.events import record_artifact
from supekku.scripts.lib.core.paths import get_revisions_dir
from supekku.scripts.lib.core.spec_utils import dump_markdown_file_create
from supekku.scripts.lib.specs.creation import (
  extract_template_body,
  find_repository_root,
  slugify,
)

if TYPE_CHECKING:
  from collections.abc import Iterable


def _requirement_kind(requirement_id: str) -> str:
  """Derive requirement kind from its ID token (FR -> functional, NF/NFR -> not)."""
  _, _, tail = requirement_id.partition(".")
  token = tail.split("-", 1)[0]
  return "non-functional" if token in ("NF", "NFR") else "functional"


def _requirement_container(requirement_id: str) -> str:
  """The spec/container prefix of a requirement_id (text before the first dot)."""
  container, _, _ = requirement_id.partition(".")
  return container


def _render_scope_block(
  revision_id: str,
  destination_specs: Iterable[str] | None,
  requirements: Iterable[str] | None,
) -> str:
  """Render the canonical revision.change block from supplied scope.

  specs[] from destination_specs, requirements[] as modify (DEC-142-09/12).
  """
  return render_revision_change_block(
    revision_id,
    specs=[
      {"spec_id": s, "action": "updated"} for s in sorted(set(destination_specs or []))
    ],
    requirements=[
      {
        "requirement_id": r,
        "kind": _requirement_kind(r),
        "action": "modify",
        "destination": {"spec": _requirement_container(r)},
      }
      for r in sorted(set(requirements or []))
    ],
    prepared_by="create-revision",
  )


def create_revision(
  name: str,
  *,
  destination_specs: Iterable[str] | None = None,
  requirements: Iterable[str] | None = None,
  render_change_block: bool = True,
  repo_root: Path | None = None,
) -> ChangeArtifactCreated:
  """Create a new spec revision artifact.

  Args:
    name: Revision name/title.
    destination_specs: Spec IDs being revised to.
    requirements: Requirement IDs affected.
    render_change_block: Emit the canonical revision.change block from the
      supplied scope. ``complete delta`` sets this False because it appends
      its own richer (lifecycle-bearing) block (see ISSUE-062 for the
      planned consolidation).
    repo_root: Optional repository root. Auto-detected if not provided.

  Returns:
    ChangeArtifactCreated with revision details.
  """
  repo = find_repository_root(repo_root or Path.cwd())
  base_dir = get_revisions_dir(repo)
  _ensure_directory(base_dir)
  revision_id = _next_identifier(base_dir, "RE")
  record_artifact(revision_id)
  today = date.today().isoformat()
  slug = slugify(name) or "revision"
  revision_dir = base_dir / f"{revision_id}-{slug}"
  _ensure_directory(revision_dir)

  # Narrow frontmatter (ADR-010 / DE-142): scope lives in the block, not FM.
  frontmatter = {
    "id": revision_id,
    "slug": slug,
    "name": f"Spec Revision - {name}",
    "created": today,
    "updated": today,
    "status": "draft",
    "kind": "revision",
    "relations": [],
  }

  change_block = (
    _render_scope_block(revision_id, destination_specs, requirements)
    if render_change_block
    else ""
  )

  # Load template and render with Jinja2
  body = Template(
    extract_template_body(_get_template_path("revision.md", repo))
  ).render(
    revision_id=revision_id,
    name=name,
    created=today,
    updated=today,
    revision_change_block=change_block,
  )

  revision_path = revision_dir / f"{revision_id}.md"
  dump_markdown_file_create(revision_path, frontmatter, body, kind="revision")
  return ChangeArtifactCreated(
    artifact_id=revision_id,
    directory=revision_dir,
    primary_path=revision_path,
    extras=[],
  )
