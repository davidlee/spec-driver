"""Utilities for creating change artifacts like deltas and revisions."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Template

from supekku.scripts.lib.blocks.plan import render_plan_overview_block
from supekku.scripts.lib.blocks.verification import render_verification_coverage_block
from supekku.scripts.lib.changes._creation_utils import (
  _ensure_directory,
  _get_template_path,
)
from supekku.scripts.lib.core.paths import get_deltas_dir
from supekku.scripts.lib.core.spec_utils import dump_markdown_file, load_markdown_file
from supekku.scripts.lib.specs.creation import (
  extract_template_body,
  find_repository_root,
  slugify,
)
from supekku.scripts.lib.specs.registry import SpecRegistry

if TYPE_CHECKING:
  from collections.abc import Iterable


# Old rendering functions and regex patterns removed.
# Block rendering now uses canonical functions from blocks package.


def _render_plan(
  delta_id: str,
  delta_dir: Path,
  slug: str,
  name: str,
  repo: Path,
  *,
  specs: Iterable[str] | None = None,
  requirements: Iterable[str] | None = None,
) -> Path:
  """Render an implementation plan file inside a delta directory.

  This is the internal workhorse; both create_delta and create_plan call it.

  Returns:
    Path to the created plan file.
  """
  plan_id = delta_id.replace("DE", "IP")
  today = date.today().isoformat()

  plan_overview_block = render_plan_overview_block(
    plan_id,
    delta_id,
    primary_specs=list(specs or []),
    target_requirements=list(requirements or []),
  )

  first_req = list(requirements or [])[0] if requirements else "SPEC-YYY.FR-001"
  plan_verification_block = render_verification_coverage_block(
    plan_id,
    entries=[
      {
        "artefact": "VT-XXX",
        "kind": "VT",
        "requirement": first_req,
        "status": "planned",
        "notes": "Link to evidence (test run, audit, validation artefact).",
      }
    ],
  )

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
  return plan_path


def create_plan(
  delta_id: str,
  *,
  repo_root: Path | None = None,
) -> Path:
  """Create an implementation plan for an existing delta.

  Locates the delta directory, reads its frontmatter for metadata,
  and renders a plan file. Raises if the delta doesn't exist or
  a plan already exists.

  Args:
    delta_id: Delta ID (e.g. 'DE-041').
    repo_root: Optional repository root. Auto-detected if not provided.

  Returns:
    Path to the created plan file.

  Raises:
    FileNotFoundError: If delta directory not found.
    FileExistsError: If plan already exists in the delta directory.
  """
  repo = find_repository_root(repo_root or Path.cwd())
  deltas_dir = get_deltas_dir(repo)

  # Find delta directory
  delta_dir = None
  if deltas_dir.exists():
    for entry in deltas_dir.iterdir():
      if entry.is_dir() and entry.name.startswith(f"{delta_id}-"):
        delta_dir = entry
        break
  if delta_dir is None:
    msg = f"Delta directory not found for {delta_id}"
    raise FileNotFoundError(msg)

  # Check for existing plan
  plan_id = delta_id.replace("DE", "IP")
  plan_path = delta_dir / f"{plan_id}.md"
  if plan_path.exists():
    msg = f"Plan {plan_id} already exists at {plan_path}"
    raise FileExistsError(msg)

  # Read delta frontmatter for metadata
  delta_file = delta_dir / f"{delta_id}.md"
  if not delta_file.exists():
    msg = f"Delta file not found: {delta_file}"
    raise FileNotFoundError(msg)
  frontmatter, _ = load_markdown_file(delta_file)
  slug = frontmatter.get("slug", "plan")
  name = frontmatter.get("name", delta_id).removeprefix("Delta - ")
  applies_to = frontmatter.get("applies_to", {})
  specs = applies_to.get("specs")
  requirements = applies_to.get("requirements")

  return _render_plan(
    delta_id,
    delta_dir,
    slug,
    name,
    repo,
    specs=specs,
    requirements=requirements,
  )


def create_requirement_breakout(
  spec_id: str,
  requirement_id: str,
  *,
  title: str,
  kind: str | None = None,
  tags: list[str] | None = None,
  ext_id: str | None = None,
  ext_url: str | None = None,
  repo_root: Path | None = None,
) -> Path:
  """Create a breakout requirement file under a spec.

  Args:
    spec_id: Parent spec identifier.
    requirement_id: Requirement code (e.g., FR-010).
    title: Requirement title.
    kind: Optional requirement kind. Defaults based on requirement_id prefix.
    tags: Optional discovery tags for categorisation.
    ext_id: Optional external system identifier (e.g., JIRA-1234).
    ext_url: Optional URL to external resource.
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

  frontmatter: dict[str, object] = {
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
  if tags:
    frontmatter["tags"] = sorted(tags)
  if ext_id:
    frontmatter["ext_id"] = ext_id
  if ext_url:
    frontmatter["ext_url"] = ext_url
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


# Re-exports for backward compatibility (all importers unchanged)
from supekku.scripts.lib.changes._creation_utils import (  # noqa: E402, F401
  ChangeArtifactCreated,
)
from supekku.scripts.lib.changes.audit_creation import create_audit  # noqa: E402, F401
from supekku.scripts.lib.changes.delta_creation import (  # noqa: E402, F401
  create_delta,
)
from supekku.scripts.lib.changes.phase_creation import (  # noqa: E402, F401
  PhaseCreationError,
  PhaseCreationResult,
  create_phase,
)
from supekku.scripts.lib.changes.revision_creation import (  # noqa: E402, F401
  create_revision,
)

__all__ = [
  "ChangeArtifactCreated",
  "PhaseCreationError",
  "PhaseCreationResult",
  "create_audit",
  "create_delta",
  "create_plan",
  "create_phase",
  "create_requirement_breakout",
  "create_revision",
]
