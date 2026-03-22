"""Revision artifact creation."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Template

from supekku.scripts.lib.changes._creation_utils import (
  ChangeArtifactCreated,
  _ensure_directory,
  _get_template_path,
  _next_identifier,
)
from supekku.scripts.lib.core.events import record_artifact
from supekku.scripts.lib.core.paths import get_revisions_dir
from supekku.scripts.lib.core.spec_utils import dump_markdown_file
from supekku.scripts.lib.specs.creation import (
  extract_template_body,
  find_repository_root,
  slugify,
)

if TYPE_CHECKING:
  from collections.abc import Iterable


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
  base_dir = get_revisions_dir(repo)
  _ensure_directory(base_dir)
  revision_id = _next_identifier(base_dir, "RE")
  record_artifact(revision_id)
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
