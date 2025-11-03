"""Utilities for creating change artifacts like deltas and revisions."""

from __future__ import annotations

import re
import warnings
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

import yaml
from jinja2 import Template

from supekku.scripts.lib.blocks.delta import render_delta_relationships_block
from supekku.scripts.lib.blocks.plan import (
  PLAN_MARKER,
  extract_plan_overview,
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


class PhaseCreationError(Exception):
  """Raised when phase creation fails."""


@dataclass(frozen=True)
class PhaseCreationResult:
  """Result information from creating a phase."""

  phase_id: str
  phase_path: Path
  plan_id: str
  delta_id: str


def _find_plan_file(plan_id: str, repo_root: Path) -> Path | None:
  """Find plan file by ID in delta directories.

  Args:
    plan_id: Plan identifier (e.g., IP-002).
    repo_root: Repository root path.

  Returns:
    Path to plan file, or None if not found.
  """
  deltas_dir = repo_root / "change" / "deltas"
  if not deltas_dir.exists():
    return None

  # Search all delta directories for plan file
  for delta_dir in deltas_dir.iterdir():
    if not delta_dir.is_dir():
      continue
    plan_path = delta_dir / f"{plan_id}.md"
    if plan_path.exists():
      return plan_path

  return None


def _parse_phase_number(filename: str) -> int | None:
  """Extract phase number from filename like 'phase-01.md'.

  Args:
    filename: Phase filename.

  Returns:
    Phase number as int, or None if not a valid phase filename.
  """
  match = re.match(r"phase-(\d{2})\.md$", filename)
  if match:
    return int(match.group(1))
  return None


def _find_next_phase_number(phases_dir: Path) -> int:
  """Find next phase number by scanning existing phase files.

  Args:
    phases_dir: Directory containing phase files.

  Returns:
    Next phase number (1 if no phases exist).
  """
  if not phases_dir.exists():
    return 1

  max_num = 0
  for entry in phases_dir.iterdir():
    if entry.is_file():
      num = _parse_phase_number(entry.name)
      if num is not None:
        max_num = max(max_num, num)

  return max_num + 1


def _update_plan_overview_phases(
  plan_path: Path,
  phase_id: str,
) -> None:
  """Update plan.overview block to include new phase entry.

  Appends a minimal phase entry to the phases array in the plan.overview block.
  Uses id-only format to minimize user conflict.

  Args:
    plan_path: Path to the plan markdown file.
    phase_id: Phase ID to add (e.g., "IP-002.PHASE-04").

  Raises:
    ValueError: If plan.overview block missing or malformed.
    OSError: If file I/O fails.
  """
  # Read plan file
  content = plan_path.read_text(encoding="utf-8")

  # Extract plan.overview block
  block = extract_plan_overview(content, plan_path)
  if block is None:
    msg = f"No plan.overview block found in {plan_path}"
    raise ValueError(msg)

  # Parse data
  data = block.data

  # Append new phase entry (minimal - just ID)
  phases = data.get("phases", [])
  if not isinstance(phases, list):
    msg = f"plan.overview phases is not a list in {plan_path}"
    raise ValueError(msg)

  # Add phase with minimal metadata (id only)
  phases.append({"id": phase_id})
  data["phases"] = phases

  # Re-serialize YAML block
  yaml_content = yaml.safe_dump(
    data,
    sort_keys=False,
    indent=2,
    default_flow_style=False,
  )

  # Ensure trailing newline
  if not yaml_content.endswith("\n"):
    yaml_content += "\n"

  # Build new block with markers
  new_block = f"```yaml {PLAN_MARKER}\n{yaml_content}```"

  # Replace old block with new block using regex
  pattern = re.compile(
    r"```(?:yaml|yml)\s+" + re.escape(PLAN_MARKER) + r"\n.*?```",
    re.DOTALL,
  )

  new_content = pattern.sub(new_block, content, count=1)

  if new_content == content:
    msg = f"Failed to replace plan.overview block in {plan_path}"
    raise ValueError(msg)

  # Write back to file
  plan_path.write_text(new_content, encoding="utf-8")


def create_phase(
  name: str,
  plan_id: str,
  *,
  repo_root: Path | None = None,
) -> PhaseCreationResult:
  """Create a new phase for an implementation plan.

  Args:
    name: Phase name (e.g., "Phase 01 - Foundation").
    plan_id: Implementation plan ID (e.g., "IP-002").
    repo_root: Optional repository root. Auto-detected if not provided.

  Returns:
    PhaseCreationResult with phase details.

  Raises:
    PhaseCreationError: If plan not found, invalid input, or creation fails.
  """
  if not name or not name.strip():
    msg = "Phase name cannot be empty"
    raise PhaseCreationError(msg)

  if not plan_id or not plan_id.strip():
    msg = "Plan ID cannot be empty"
    raise PhaseCreationError(msg)

  plan_id = plan_id.strip().upper()
  name = name.strip()

  # Find repository root
  repo = find_repository_root(repo_root or Path.cwd())

  # Find plan file
  plan_path = _find_plan_file(plan_id, repo)
  if plan_path is None:
    msg = f"Implementation plan not found: {plan_id}"
    raise PhaseCreationError(msg)

  # Read plan frontmatter to get delta ID
  with plan_path.open(encoding="utf-8") as f:
    content = f.read()

  # Extract frontmatter between --- markers
  if not content.startswith("---\n"):
    msg = f"Plan file {plan_path} has invalid frontmatter"
    raise PhaseCreationError(msg)

  parts = content.split("---\n", 2)
  if len(parts) < 3:  # noqa: PLR2004
    msg = f"Plan file {plan_path} has invalid frontmatter"
    raise PhaseCreationError(msg)

  frontmatter = yaml.safe_load(parts[1])
  delta_id = frontmatter.get("id", "").replace("IP-", "DE-")

  if not delta_id or not delta_id.startswith("DE-"):
    # Try to find delta from plan.overview block
    overview_match = re.search(
      r"```yaml supekku:plan\.overview@v1\n(.*?)\n```", content, re.DOTALL
    )
    if overview_match:
      overview_yaml = yaml.safe_load(overview_match.group(1))
      delta_id = overview_yaml.get("delta", "")

  if not delta_id or not delta_id.startswith("DE-"):
    msg = (
      f"Plan {plan_id} does not specify delta ID in frontmatter or plan.overview block"
    )
    raise PhaseCreationError(msg)

  # Find delta directory
  delta_dir = plan_path.parent
  phases_dir = delta_dir / "phases"
  _ensure_directory(phases_dir)

  # Determine next phase number
  phase_num = _find_next_phase_number(phases_dir)

  # Generate phase ID
  phase_id = f"{plan_id}.PHASE-{phase_num:02d}"

  # Get current date
  today = date.today().isoformat()

  # Get slug from delta directory name
  slug = delta_dir.name.split("-", 1)[1] if "-" in delta_dir.name else "phase"

  # Render phase overview block (with empty defaults for user to fill in)
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

  # Create phase file
  phase_path = phases_dir / f"phase-{phase_num:02d}.md"
  phase_frontmatter = {
    "id": phase_id,
    "slug": f"{slug}-phase-{phase_num:02d}",
    "name": f"{plan_id} Phase {phase_num:02d}",
    "created": today,
    "updated": today,
    "status": "draft",
    "kind": "phase",
  }

  dump_markdown_file(phase_path, phase_frontmatter, phase_body)

  # Update plan.overview block with new phase
  try:
    _update_plan_overview_phases(plan_path, phase_id)
  except (ValueError, OSError) as exc:
    # Phase file created successfully but metadata update failed
    # Log warning but don't fail phase creation
    warnings.warn(
      f"Phase {phase_id} created but plan metadata update failed: {exc}",
      stacklevel=2,
    )

  return PhaseCreationResult(
    phase_id=phase_id,
    phase_path=phase_path,
    plan_id=plan_id,
    delta_id=delta_id,
  )


__all__ = [
  "ChangeArtifactCreated",
  "PhaseCreationError",
  "PhaseCreationResult",
  "create_delta",
  "create_phase",
  "create_requirement_breakout",
  "create_revision",
]
