"""Change artifact management and processing utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from supekku.scripts.lib.core.spec_utils import load_markdown_file
from supekku.scripts.lib.relations import list_relations

from .blocks.delta import DeltaRelationshipsValidator, extract_delta_relationships
from .blocks.plan import extract_phase_overview, extract_plan_overview
from .lifecycle import VALID_STATUSES, normalize_status

if TYPE_CHECKING:
  from pathlib import Path


@dataclass(frozen=True)
class ChangeArtifact:
  """Represents a change artifact with metadata and relationships."""

  id: str
  kind: str
  status: str
  name: str
  slug: str
  path: Path
  updated: str | None
  applies_to: dict[str, Any] = field(default_factory=dict)
  relations: list[dict[str, Any]] = field(default_factory=list)
  plan: dict[str, Any] | None = None

  def to_dict(self, repo_root: Path) -> dict[str, Any]:
    """Convert artifact to dictionary for registry serialization.

    Args:
      repo_root: Repository root for computing relative paths.

    Returns:
      Dictionary representation of the artifact.
    """
    relative_path = self.path.relative_to(repo_root).as_posix()
    data: dict[str, Any] = {
      "kind": self.kind,
      "status": self.status,
      "name": self.name,
      "slug": self.slug,
      "updated": self.updated,
      "path": relative_path,
    }
    if self.applies_to:
      data["applies_to"] = self.applies_to
    if self.relations:
      data["relations"] = self.relations
    if self.plan:
      data["plan"] = self.plan
    return data


def load_change_artifact(path: Path) -> ChangeArtifact | None:
  """Load and parse a change artifact from markdown file.

  Args:
    path: Path to artifact markdown file.

  Returns:
    Parsed ChangeArtifact or None if ID is missing.

  Raises:
    ValueError: If status is invalid.
  """
  frontmatter, body = load_markdown_file(path)
  artifact_id = str(frontmatter.get("id", "")).strip()
  if not artifact_id:
    return None
  kind = str(frontmatter.get("kind", "")).strip()
  raw_status = str(frontmatter.get("status", "")).strip()
  status = normalize_status(raw_status) if raw_status else raw_status

  # Validate status against known values
  if status and status not in VALID_STATUSES:
    valid_list = ", ".join(sorted(VALID_STATUSES))
    msg = f"Invalid status '{status}' in {path}\nValid statuses: {valid_list}"
    raise ValueError(
      msg,
    )

  name = str(frontmatter.get("name", artifact_id))
  slug = str(frontmatter.get("slug", artifact_id.lower()))
  updated = frontmatter.get("updated")
  applies_to = frontmatter.get("applies_to")
  applies_to_mapping = dict(applies_to) if isinstance(applies_to, dict) else {}
  relations = [rel.__dict__ for rel in list_relations(path)]
  plan_payload: dict[str, Any] | None = None

  if kind == "delta":
    block = None
    try:
      block = extract_delta_relationships(body)
    except ValueError:
      block = None
    if block and not DeltaRelationshipsValidator().validate(
      block,
      delta_id=artifact_id,
    ):
      specs = block.data.get("specs") or {}
      primary_specs = specs.get("primary") or []
      if primary_specs:
        existing = {
          str(item)
          for item in applies_to_mapping.get("specs", [])
          if isinstance(item, str)
        }
        existing.update(str(item) for item in primary_specs if isinstance(item, str))
        if existing:
          applies_to_mapping["specs"] = sorted(existing)

      reqs = block.data.get("requirements") or {}
      requirement_ids = set()
      for key in ("implements", "updates", "verifies"):
        values = reqs.get(key) or []
        for value in values:
          if isinstance(value, str):
            requirement_ids.add(value)
      if requirement_ids:
        existing_reqs = {
          str(item)
          for item in applies_to_mapping.get("requirements", [])
          if isinstance(item, str)
        }
        existing_reqs.update(requirement_ids)
        applies_to_mapping["requirements"] = sorted(existing_reqs)

      revision_links = block.data.get("revision_links") or {}
      for rel_type in ("introduces", "supersedes"):
        for target in revision_links.get(rel_type) or []:
          relations.append({"type": rel_type, "target": str(target)})

    plan_id = artifact_id.replace("DE", "IP")
    plan_path = path.parent / f"{plan_id}.md"
    plan_block = None
    if plan_path.exists():
      try:
        plan_block = extract_plan_overview(
          plan_path.read_text(encoding="utf-8"),
          source_path=plan_path,
        )
      except ValueError:
        plan_block = None

    phases_data: list[dict[str, Any]] = []
    phase_lookup: dict[str, dict[str, Any]] = {}
    if plan_block:
      for entry in plan_block.data.get("phases", []) or []:
        if isinstance(entry, dict) and entry.get("id"):
          phase_lookup[str(entry["id"])] = entry

    phases_dir = path.parent / "phases"
    if phases_dir.exists():
      for phase_file in sorted(phases_dir.glob("*.md")):
        try:
          phase_block = extract_phase_overview(
            phase_file.read_text(encoding="utf-8"),
            source_path=phase_file,
          )
        except ValueError:
          continue
        if not phase_block:
          continue
        phase_entry = phase_block.data.copy()
        phase_entry.setdefault("phase", phase_entry.get("id"))
        phases_data.append(phase_entry)
        phase_id = str(phase_entry.get("phase", ""))
        phase_lookup.pop(phase_id, None)

    for phase_data in phase_lookup.values():
      phase_copy = phase_data.copy()
      phase_copy.setdefault("phase", phase_copy.get("id"))
      phases_data.append(phase_copy)

    if plan_block or phases_data:
      plan_payload = {
        "id": plan_id,
        "overview": plan_block.data if plan_block else {},
        "phases": phases_data,
      }

  return ChangeArtifact(
    id=artifact_id,
    kind=kind,
    status=status,
    name=name,
    slug=slug,
    path=path,
    updated=str(updated) if updated else None,
    applies_to=applies_to_mapping,
    relations=relations,
    plan=plan_payload,
  )


__all__ = ["ChangeArtifact", "load_change_artifact"]
