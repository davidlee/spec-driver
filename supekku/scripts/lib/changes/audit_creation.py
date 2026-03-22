"""Audit artifact creation."""

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
from supekku.scripts.lib.core.paths import get_audits_dir
from supekku.scripts.lib.core.spec_utils import dump_markdown_file
from supekku.scripts.lib.specs.creation import (
  extract_template_body,
  find_repository_root,
  slugify,
)

if TYPE_CHECKING:
  from collections.abc import Iterable


def create_audit(
  name: str,
  *,
  mode: str = "conformance",
  delta_ref: str | None = None,
  spec_refs: Iterable[str] | None = None,
  prod_refs: Iterable[str] | None = None,
  code_scope: Iterable[str] | None = None,
  repo_root: Path | None = None,
) -> ChangeArtifactCreated:
  """Create a new audit artifact.

  Args:
    name: Audit name/title.
    mode: Audit mode — 'conformance' or 'discovery'.
    delta_ref: Owning delta ID (e.g. 'DE-079').
    spec_refs: Spec IDs referenced by the audit.
    prod_refs: Product spec IDs referenced by the audit.
    code_scope: Code path patterns inspected during audit.
    repo_root: Optional repository root. Auto-detected if not provided.

  Returns:
    ChangeArtifactCreated with audit details.
  """
  repo = find_repository_root(repo_root or Path.cwd())
  base_dir = get_audits_dir(repo)
  _ensure_directory(base_dir)
  audit_id = _next_identifier(base_dir, "AUD")
  record_artifact(audit_id)
  today = date.today().isoformat()
  slug = slugify(name) or "audit"
  audit_dir = base_dir / f"{audit_id}-{slug}"
  _ensure_directory(audit_dir)

  frontmatter: dict = {
    "id": audit_id,
    "slug": slug,
    "name": f"Audit - {name}",
    "created": today,
    "updated": today,
    "status": "draft",
    "kind": "audit",
    "mode": mode,
  }
  if delta_ref:
    frontmatter["delta_ref"] = delta_ref
  if spec_refs:
    frontmatter["spec_refs"] = sorted(set(spec_refs))
  if prod_refs:
    frontmatter["prod_refs"] = sorted(set(prod_refs))
  if code_scope:
    frontmatter["code_scope"] = sorted(set(code_scope))

  # Load template and render with Jinja2
  template_path = _get_template_path("audit.md", repo)
  template_body = extract_template_body(template_path)
  template = Template(template_body)
  body = template.render(
    audit_id=audit_id,
    name=name,
    created=today,
    updated=today,
    audit_verification_block="",
  )

  audit_path = audit_dir / f"{audit_id}.md"
  dump_markdown_file(audit_path, frontmatter, body)
  return ChangeArtifactCreated(
    artifact_id=audit_id,
    directory=audit_dir,
    primary_path=audit_path,
    extras=[],
  )
