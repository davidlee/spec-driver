"""Change artifact management and processing utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from rich.console import Console

from supekku.scripts.lib.blocks.delta import (
  DeltaRelationshipsBlock,
  extract_delta_relationships,
)
from supekku.scripts.lib.blocks.metadata.aliases import normalize_field
from supekku.scripts.lib.blocks.plan import (
  extract_phase_overview,
  extract_plan_overview,
)
from supekku.scripts.lib.changes.phase_model import PhaseSheet
from supekku.scripts.lib.core.spec_utils import load_markdown_file
from supekku.scripts.lib.relations.manager import list_relations

from .lifecycle import CHANGE_STATUSES

if TYPE_CHECKING:
  from pathlib import Path


def _derive_applies_to(
  block: DeltaRelationshipsBlock | None,
  frontmatter: dict[str, Any],
) -> dict[str, Any]:
  """Synthesise ``applies_to`` from the relationships block (DR-138 §6.1).

  Block-first when present (sole source — FM silently shadowed even if
  populated). FM-fallback only when block absent (transition window for
  unmigrated artefacts). Validator layer separately reports FM
  ``applies_to`` as a strict-mode error post-flip (DEC-138-10).

  Unions ``specs.primary ∪ specs.collaborators`` so collaborator-only
  linkages remain visible to coverage gates (DEC-138-11).
  """
  if block is not None:
    spec_groups = block.data.get("specs") or {}
    specs = sorted(
      {
        str(s)
        for key in ("primary", "collaborators")
        for s in (spec_groups.get(key) or [])
        if isinstance(s, str)
      }
    )
    req_groups = block.data.get("requirements") or {}
    reqs = sorted(
      {
        str(r)
        for key in ("implements", "updates", "verifies")
        for r in (req_groups.get(key) or [])
        if isinstance(r, str)
      }
    )
    if specs or reqs:
      return {"specs": specs, "requirements": reqs}
  fm = frontmatter.get("applies_to") or {}
  return dict(fm) if isinstance(fm, dict) else {}


def _derive_revision_link_relations(
  block: DeltaRelationshipsBlock | None,
) -> list[dict[str, str]]:
  """Project ``revision_links.{introduces,supersedes}`` into relation entries.

  Preserves the legacy projection as a discrete helper so deleting the
  ``applies_to`` merge region does not collateral-drop the RE-* relation
  projection (DR-138 §6.1, F-138-16). ADR-002 backlinks rule is observed
  because the projection derives from authored block content, not from
  foreign-artefact backlinks.
  """
  if block is None:
    return []
  revision_links = block.data.get("revision_links") or {}
  relations: list[dict[str, str]] = []
  for rel_type in ("introduces", "supersedes"):
    for target in revision_links.get(rel_type) or []:
      relations.append({"type": rel_type, "target": str(target)})
  return relations


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
  tags: list[str] = field(default_factory=list)
  applies_to: dict[str, Any] = field(default_factory=dict)
  relations: list[dict[str, Any]] = field(default_factory=list)
  plan: dict[str, Any] | None = None
  ext_id: str = ""
  ext_url: str = ""
  audit_gate: str | None = None

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
    if self.ext_id:
      data["ext_id"] = self.ext_id
    if self.ext_url:
      data["ext_url"] = self.ext_url
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
  status = normalize_field(kind, "status", raw_status) if raw_status else raw_status

  # Validate status against known values (CHANGE_STATUSES is the canonical set
  # after DE-137; legacy aliases like 'complete' canonicalise via
  # ``FieldMetadata.aliases`` in `normalize_field` above).
  if status and status not in CHANGE_STATUSES:
    canonical = sorted(CHANGE_STATUSES)
    msg = (
      f"Invalid status '{raw_status}' in {path}. Valid statuses: {', '.join(canonical)}"
    )
    raise ValueError(msg)

  name = str(frontmatter.get("name", artifact_id))
  slug = str(frontmatter.get("slug", artifact_id.lower()))
  updated = frontmatter.get("updated")
  tags = frontmatter.get("tags", [])
  tags_list = [str(tag) for tag in tags] if isinstance(tags, list) else []
  applies_to = frontmatter.get("applies_to")
  applies_to_mapping = dict(applies_to) if isinstance(applies_to, dict) else {}
  relations = [rel.__dict__ for rel in list_relations(path)]
  plan_payload: dict[str, Any] | None = None

  if kind == "delta":
    block: DeltaRelationshipsBlock | None = None
    try:
      block = extract_delta_relationships(body)
    except ValueError:
      block = None
    applies_to_mapping = _derive_applies_to(block, frontmatter)
    relations.extend(_derive_revision_link_relations(block))

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
          fm_data, _ = load_markdown_file(phase_file)
        except (ValueError, OSError) as exc:
          Console(stderr=True).print(
            f"[yellow]WARNING:[/yellow] Skipping phase file: {exc}"
          )
          continue

        # Prefer frontmatter when canonical fields are present (DR-106)
        sheet = PhaseSheet(**fm_data) if fm_data else PhaseSheet()
        if sheet.has_canonical_fields():
          phase_entry = sheet.to_phase_entry()
          # Carry base frontmatter fields that downstream consumers expect
          phase_entry.setdefault("phase", fm_data.get("id"))
          phase_entry.setdefault("status", fm_data.get("status"))
        else:
          # Legacy fallback: extract from phase.overview block
          try:
            content = phase_file.read_text(encoding="utf-8")
            phase_block = extract_phase_overview(content, source_path=phase_file)
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
    tags=tags_list,
    applies_to=applies_to_mapping,
    relations=relations,
    plan=plan_payload,
    ext_id=str(frontmatter.get("ext_id", "")),
    ext_url=str(frontmatter.get("ext_url", "")),
    audit_gate=(
      str(frontmatter["audit_gate"]).strip() if frontmatter.get("audit_gate") else None
    ),
  )


__all__ = ["ChangeArtifact", "load_change_artifact"]
