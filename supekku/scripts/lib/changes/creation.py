"""Utilities for creating change artifacts like deltas and revisions."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from supekku.scripts.lib.core.spec_utils import dump_markdown_file
from supekku.scripts.lib.specs.creation import (
  extract_template_body,
  find_repository_root,
  slugify,
)
from supekku.scripts.lib.specs.registry import SpecRegistry

if TYPE_CHECKING:
  from collections.abc import Iterable

REPO_ROOT = Path(__file__).resolve().parents[3]
TEMPLATE_DIR = REPO_ROOT / "supekku" / "templates"

REVISION_TEMPLATE = TEMPLATE_DIR / "spec-revision-template.md"
PLAN_TEMPLATE = TEMPLATE_DIR / "implementation-plan-template.md"
PHASE_TEMPLATE = TEMPLATE_DIR / "phase-sheet-template.md"


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


def _yaml_list(key: str, values: Iterable[str], level: int = 0) -> str:
  indent = "  " * level
  items = [str(v) for v in values if v]
  if not items:
    return f"{indent}{key}: []"
  child_indent = "  " * (level + 1)
  lines = [f"{indent}{key}:"]
  lines.extend(f"{child_indent}- {item}" for item in items)
  return "\n".join(lines)


def _render_plan_overview_block(
  plan_id: str,
  delta_id: str,
  specs: Iterable[str],
  requirements: Iterable[str],
  first_phase_id: str,
) -> str:
  specs_block = _yaml_list("primary", sorted({s for s in specs if s}), level=1)
  requirements_block = _yaml_list(
    "targets",
    sorted({r for r in requirements if r}),
    level=1,
  )
  lines = [
    "```yaml supekku:plan.overview@v1",
    "schema: supekku.plan.overview",
    "version: 1",
    f"plan: {plan_id}",
    f"delta: {delta_id}",
    "revision_links:",
    "  aligns_with: []",
    "specs:",
    specs_block,
    _yaml_list("collaborators", [], level=1),
    "requirements:",
    requirements_block,
    _yaml_list("dependencies", [], level=1),
    "phases:",
    f"  - id: {first_phase_id}",
    "    name: Phase 01 - Initial delivery",
    "    objective: >-",
    "      Deliver the foundational work for this delta.",
    "    entrance_criteria: []",
    "    exit_criteria: []",
    "```",
  ]
  return "\n".join(lines)


def _render_phase_overview_block(
  phase_id: str,
  plan_id: str,
  delta_id: str,
) -> str:
  lines = [
    "```yaml supekku:phase.overview@v1",
    "schema: supekku.phase.overview",
    "version: 1",
    f"phase: {phase_id}",
    f"plan: {plan_id}",
    f"delta: {delta_id}",
    "objective: >-",
    "  Describe the outcome for this phase.",
    "entrance_criteria: []",
    "exit_criteria: []",
    "verification:",
    "  tests: []",
    "  evidence: []",
    "tasks: []",
    "risks: []",
    "```",
  ]
  return "\n".join(lines)


def _render_delta_relationship_block(
  delta_id: str,
  specs: Iterable[str],
  requirements: Iterable[str],
) -> str:
  spec_lines = _yaml_list("primary", sorted({s for s in specs if s}), level=1)
  requirement_lines = _yaml_list(
    "implements",
    sorted({r for r in requirements if r}),
    level=1,
  )
  lines = [
    "```yaml supekku:delta.relationships@v1",
    "schema: supekku.delta.relationships",
    "version: 1",
    f"delta: {delta_id}",
    "revision_links:",
    "  introduces: []",
    "  supersedes: []",
    "specs:",
    spec_lines,
    _yaml_list("collaborators", [], level=1),
    "requirements:",
    requirement_lines,
    _yaml_list("updates", [], level=1),
    _yaml_list("verifies", [], level=1),
    "phases: []",
    "```",
  ]
  return "\n".join(lines)


_PLAN_OVERVIEW_PATTERN = re.compile(
  r"```yaml supekku:plan.overview@v1.*?```",
  re.DOTALL,
)
_PHASE_OVERVIEW_PATTERN = re.compile(
  r"```yaml supekku:phase.overview@v1.*?```",
  re.DOTALL,
)
_DELTA_RELATIONSHIPS_PATTERN = re.compile(
  r"```yaml supekku:delta.relationships@v1.*?```",
  re.DOTALL,
)


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

  body = f"""# {revision_id} - {name}

## 1. Context
- **Why**: TODO
- **Source Specs**: {", ".join(source_specs or []) or "TODO"}
- **Destination Specs**: {", ".join(destination_specs or []) or "TODO"}
- **Requirements Affected**: {", ".join(requirements or []) or "TODO"}

## 2. Related Artefacts
- **Commits**: TODO
- **Issues / Problems / Improvements**: TODO
- **Decisions / ADRs**: TODO
- **Follow-up Deltas**: TODO

## 3. Summary of Changes
- TODO

## 4. Consequences
- TODO

## 5. Actions
- [ ] Update source spec change history
- [ ] Update destination spec change history
- [ ] Notify relevant owners (if needed)
- [ ] Trigger follow-up delta (if applicable)

## 6. Notes
- TODO
"""

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

  relationships_block = _render_delta_relationship_block(
    delta_id,
    specs or [],
    requirements or [],
  )

  body = f"""{relationships_block}

# {delta_id} - {name}

## Motivation
> TODO

## Scope
> TODO

## Out of Scope
> TODO

## Verification Strategy
> TODO

## Follow-up / Tracking
> TODO

## Notes
> TODO
"""

  delta_path = delta_dir / f"{delta_id}.md"
  dump_markdown_file(delta_path, frontmatter, body)

  extras: list[Path] = []
  plan_id = delta_id.replace("DE", "IP")
  if not allow_missing_plan:
    plan_body = extract_template_body(PLAN_TEMPLATE)
    plan_body = plan_body.replace("IP-XXX", plan_id).replace("DE-XXX", delta_id)
    plan_body = _PLAN_OVERVIEW_PATTERN.sub(
      _render_plan_overview_block(
        plan_id,
        delta_id,
        specs or [],
        requirements or [],
        f"{plan_id}.PHASE-01",
      ),
      plan_body,
      count=1,
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
    phase_body = extract_template_body(PHASE_TEMPLATE)
    phase_body = phase_body.replace("PHASE-XXX", f"{plan_id}.PHASE-01")
    phase_body = _PHASE_OVERVIEW_PATTERN.sub(
      _render_phase_overview_block(f"{plan_id}.PHASE-01", plan_id, delta_id),
      phase_body,
      count=1,
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
