"""Requirements management and processing utilities."""

from __future__ import annotations

import logging
import re
import sys
from collections import defaultdict
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import yaml

from supekku.scripts.lib.blocks.delta import (
  DeltaRelationshipsValidator,
  extract_delta_relationships,
)
from supekku.scripts.lib.blocks.relationships import (
  RelationshipsBlockValidator,
  extract_relationships,
)
from supekku.scripts.lib.blocks.revision import (
  RevisionBlockValidator,
  load_revision_blocks,
)
from supekku.scripts.lib.blocks.verification import load_coverage_blocks
from supekku.scripts.lib.core.repo import find_repo_root
from supekku.scripts.lib.core.spec_utils import load_markdown_file
from supekku.scripts.lib.relations.manager import list_relations

from .lifecycle import (
  STATUS_ACTIVE,
  STATUS_IN_PROGRESS,
  STATUS_PENDING,
  VALID_STATUSES,
  RequirementStatus,
)

if TYPE_CHECKING:
  from pathlib import Path

  from supekku.scripts.lib.specs.registry import SpecRegistry

logger = logging.getLogger(__name__)

# Updated pattern to support both formats:
# - **FR-001**: Short format (legacy)
# - **PROD-010.FR-001**: Fully-qualified format (current standard)
_REQUIREMENT_LINE = re.compile(
  r"^\s*[-*]\s*\*{0,2}\s*(?:[A-Z]+-\d{3}\.)?("
  r"FR|NF)-(\d{3})\s*\*{0,2}\s*[:\-–]\s*(.+)$",
  re.IGNORECASE,
)


@dataclass
class RequirementRecord:
  """Record representing a requirement with lifecycle tracking."""

  uid: str
  label: str
  title: str
  specs: list[str] = field(default_factory=list)
  primary_spec: str = ""
  kind: str = "functional"
  status: RequirementStatus = STATUS_PENDING
  introduced: str | None = None
  implemented_by: list[str] = field(default_factory=list)
  verified_by: list[str] = field(default_factory=list)
  coverage_evidence: list[str] = field(default_factory=list)
  path: str = ""

  def merge(self, other: RequirementRecord) -> RequirementRecord:
    """Merge data from another record, preserving lifecycle fields."""
    return RequirementRecord(
      uid=self.uid,
      label=self.label,
      title=other.title,
      specs=sorted(set(self.specs) | set(other.specs)),
      primary_spec=other.primary_spec or self.primary_spec,
      kind=other.kind or self.kind,
      status=self.status,
      introduced=self.introduced,
      implemented_by=list(self.implemented_by),
      verified_by=list(self.verified_by),
      coverage_evidence=sorted(
        set(self.coverage_evidence) | set(other.coverage_evidence)
      ),
      path=other.path or self.path,
    )

  def to_dict(self) -> dict[str, object]:
    """Convert requirement record to dictionary for serialization."""
    return {
      "label": self.label,
      "title": self.title,
      "specs": self.specs,
      "primary_spec": self.primary_spec,
      "kind": self.kind,
      "status": self.status,
      "introduced": self.introduced,
      "implemented_by": self.implemented_by,
      "verified_by": self.verified_by,
      "coverage_evidence": self.coverage_evidence,
      "path": self.path,
    }

  @classmethod
  def from_dict(cls, uid: str, data: dict[str, object]) -> RequirementRecord:
    """Create requirement record from dictionary."""
    return cls(
      uid=uid,
      label=str(data.get("label", "")),
      title=str(data.get("title", "")),
      specs=list(data.get("specs", [])),
      primary_spec=str(data.get("primary_spec", "")),
      kind=str(data.get("kind", "functional")),
      status=str(data.get("status", STATUS_PENDING)),
      introduced=data.get("introduced"),
      implemented_by=list(data.get("implemented_by", [])),
      verified_by=list(data.get("verified_by", [])),
      coverage_evidence=list(data.get("coverage_evidence", [])),
      path=str(data.get("path", "")),
    )


@dataclass
class SyncStats:
  """Statistics tracking for synchronization operations."""

  created: int = 0
  updated: int = 0


class RequirementsRegistry:
  """Registry for managing requirement records and lifecycle tracking."""

  def __init__(self, registry_path: Path) -> None:
    self.registry_path = registry_path
    self.records: dict[str, RequirementRecord] = {}
    self._load()

  # ------------------------------------------------------------------
  def _load(self) -> None:
    if not self.registry_path.exists():
      return
    data = yaml.safe_load(self.registry_path.read_text(encoding="utf-8")) or {}
    requirements = data.get("requirements", {})
    for uid, payload in sorted(requirements.items()):
      record = RequirementRecord.from_dict(uid, payload)
      self.records[uid] = record

  def save(self) -> None:
    """Save requirements registry to YAML file."""
    payload = {
      "requirements": {
        uid: record.to_dict() for uid, record in sorted(self.records.items())
      },
    }
    self.registry_path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(payload, sort_keys=False, allow_unicode=False)
    self.registry_path.write_text(text, encoding="utf-8")

  # ------------------------------------------------------------------
  def sync_from_specs(
    self,
    spec_dirs: Iterable[Path] | None = None,
    *,
    spec_registry: SpecRegistry | None = None,
    delta_dirs: Iterable[Path] | None = None,
    revision_dirs: Iterable[Path] | None = None,
    audit_dirs: Iterable[Path] | None = None,
    plan_dirs: Iterable[Path] | None = None,
  ) -> SyncStats:
    """Sync requirements from specs and change artifacts, updating registry."""
    repo_root = spec_registry.root if spec_registry else find_repo_root()
    stats = SyncStats()
    seen: set[str] = set()

    yielded_ids: set[str] = set()

    relationships_validator = RelationshipsBlockValidator()

    if spec_registry:
      for spec in spec_registry.all_specs():
        records = list(
          self._records_from_frontmatter(
            spec.id,
            spec.frontmatter,
            spec.body,
            spec.path,
            repo_root,
          ),
        )
        for record in records:
          seen.add(record.uid)
          yielded_ids.add(spec.id)
          existing = self.records.get(record.uid)
          if existing is not None:
            merged = existing.merge(record)
            if merged != existing:
              self.records[record.uid] = merged
              stats.updated += 1
          else:
            self.records[record.uid] = record
            stats.created += 1

        self._apply_spec_relationships(
          spec.id,
          spec.body,
          validator=relationships_validator,
        )

    directories = list(spec_dirs or [])
    if directories:
      for spec_file in self._iter_spec_files(directories):
        frontmatter, body = load_markdown_file(spec_file)
        spec_id = str(frontmatter.get("id", "")).strip()
        if not spec_id or spec_id in yielded_ids:
          continue
        records = list(
          self._records_from_content(
            spec_id,
            frontmatter,
            body,
            spec_file,
            repo_root,
          ),
        )
        for record in records:
          seen.add(record.uid)
          existing = self.records.get(record.uid)
          if existing is not None:
            merged = existing.merge(record)
            if merged != existing:
              self.records[record.uid] = merged
              stats.updated += 1
          else:
            self.records[record.uid] = record
            stats.created += 1

        try:
          body = spec_file.read_text(encoding="utf-8")
        except OSError:
          body = ""
        self._apply_spec_relationships(
          spec_id,
          body,
          validator=relationships_validator,
        )

    delta_validator = DeltaRelationshipsValidator()
    if delta_dirs:
      self._apply_delta_relations(
        delta_dirs,
        repo_root,
        validator=delta_validator,
      )
    if revision_dirs:
      self._apply_revision_relations(revision_dirs)
      self._apply_revision_blocks(
        revision_dirs,
        spec_registry=spec_registry,
        stats=stats,
      )
    if audit_dirs:
      self._apply_audit_relations(audit_dirs)

    # Apply coverage blocks to update lifecycle from verification entries
    spec_files = []
    if spec_registry:
      spec_files = [spec.path for spec in spec_registry.all_specs()]
    elif spec_dirs:
      spec_files = list(self._iter_spec_files(spec_dirs))

    delta_files = []
    if delta_dirs:
      delta_files = list(self._iter_change_files(delta_dirs, prefix="DE-"))

    plan_files = []
    if plan_dirs:
      plan_files = list(self._iter_plan_files(plan_dirs))

    audit_files = []
    if audit_dirs:
      audit_files = list(self._iter_change_files(audit_dirs, prefix="AUD-"))

    if spec_files or delta_files or plan_files or audit_files:
      self._apply_coverage_blocks(
        spec_files=spec_files,
        delta_files=delta_files,
        plan_files=plan_files,
        audit_files=audit_files,
      )

    # Clean specs list for records not seen this run
    for uid, record in list(self.records.items()):
      if uid not in seen:
        # Retain record but ensure specs list is unique
        self.records[uid] = RequirementRecord(
          uid=record.uid,
          label=record.label,
          title=record.title,
          specs=sorted(set(record.specs)),
          primary_spec=record.primary_spec,
          kind=record.kind,
          status=record.status,
          introduced=record.introduced,
          implemented_by=sorted(set(record.implemented_by)),
          verified_by=sorted(set(record.verified_by)),
          path=record.path,
        )

    # Validation: warn about specs with no extracted requirements
    if spec_registry:
      self._validate_extraction(spec_registry, seen)

    return stats

  def _iter_spec_files(self, spec_dirs: Iterable[Path]) -> Iterator[Path]:
    for directory in spec_dirs:
      if not directory.exists():
        continue
      for subdir in directory.iterdir():
        if not subdir.is_dir():
          continue
        for file in subdir.glob("*.md"):
          if file.name.startswith("SPEC-") or file.name.startswith("PROD-"):
            yield file

  def _validate_extraction(
    self,
    spec_registry: SpecRegistry,
    seen: set[str],
  ) -> None:
    """Validate extraction results and warn about potential issues.

    Checks for specs with zero extracted requirements, which may indicate
    format issues or extraction failures.
    """
    for spec in spec_registry.all_specs():
      # Skip non-product/tech specs (like policies, standards)
      if spec.kind not in ("prod", "tech"):
        continue

      # Count requirements extracted from this spec
      extracted = [uid for uid in seen if uid.startswith(f"{spec.id}.")]

      if len(extracted) == 0:
        print(
          f"WARNING: Spec {spec.id} ({spec.kind}) has 0 extracted requirements. "
          f"Check requirement format in {spec.path.name}",
          file=sys.stderr,
        )
        logger.warning(
          "Spec %s has no extracted requirements - possible format mismatch",
          spec.id,
        )

  def _apply_delta_relations(
    self,
    delta_dirs: Iterable[Path],
    _repo_root: Path,
    *,
    validator: DeltaRelationshipsValidator,
  ) -> None:
    for file in self._iter_change_files(delta_dirs, prefix="DE-"):
      frontmatter, _ = load_markdown_file(file)
      delta_id = str(frontmatter.get("id", "")).strip() or file.stem
      if not delta_id:
        continue

      applies_to = frontmatter.get("applies_to") or {}
      req_list = (
        applies_to.get("requirements") if isinstance(applies_to, Mapping) else None
      )
      if isinstance(req_list, Iterable):
        for req in req_list:
          target = str(req).strip()
          record = self.records.get(target)
          if not record:
            continue
          if delta_id not in record.implemented_by:
            record.implemented_by.append(delta_id)
            record.implemented_by.sort()

      for relation in list_relations(file):
        if relation.type.lower() != "implements":
          continue
        target = relation.target.strip()
        record = self.records.get(target)
        if not record:
          continue
        if delta_id not in record.implemented_by:
          record.implemented_by.append(delta_id)
          record.implemented_by.sort()

      # Structured relationships block
      try:
        block = extract_delta_relationships(file.read_text(encoding="utf-8"))
      except ValueError:
        block = None
      if block and not validator.validate(block, delta_id=delta_id):
        requirements = block.data.get("requirements") or {}
        implements = requirements.get("implements") or []
        for req in implements:
          record = self.records.get(req)
          if not record:
            continue
          if delta_id not in record.implemented_by:
            record.implemented_by.append(delta_id)
            record.implemented_by.sort()

  def _apply_revision_relations(self, revision_dirs: Iterable[Path]) -> None:
    for file in self._iter_change_files(revision_dirs, prefix="RE-"):
      frontmatter, _ = load_markdown_file(file)
      revision_id = str(frontmatter.get("id", "")).strip() or file.stem
      if not revision_id:
        continue
      for relation in list_relations(file):
        target = relation.target.strip()
        record = self.records.get(target)
        if not record:
          continue
        rel_type = relation.type.lower()
        if rel_type in {"introduces", "moves", "reparented"} and not record.introduced:
          record.introduced = revision_id

  def _apply_revision_blocks(
    self,
    revision_dirs: Iterable[Path],
    *,
    spec_registry: SpecRegistry | None,
    stats: SyncStats,
  ) -> None:
    validator = RevisionBlockValidator()
    for file in self._iter_change_files(revision_dirs, prefix="RE-"):
      blocks = load_revision_blocks(file)
      for block in blocks:
        try:
          data = block.parse()
        except ValueError:
          continue
        if validator.validate(data):
          continue
        for requirement in data.get("requirements", []) or []:
          created, updated = self._apply_revision_requirement(
            requirement,
            spec_registry=spec_registry,
          )
          stats.created += created
          stats.updated += updated

  def _apply_audit_relations(self, audit_dirs: Iterable[Path]) -> None:
    for file in self._iter_change_files(audit_dirs, prefix="AUD-"):
      frontmatter, _ = load_markdown_file(file)
      audit_id = str(frontmatter.get("id", "")).strip() or file.stem
      if not audit_id:
        continue
      for relation in list_relations(file):
        if relation.type.lower() != "verifies":
          continue
        target = relation.target.strip()
        record = self.records.get(target)
        if not record:
          continue
        if audit_id not in record.verified_by:
          record.verified_by.append(audit_id)
          record.verified_by.sort()

  def _check_coverage_drift(
    self,
    req_id: str,
    entries: list[dict[str, Any]],
  ) -> None:
    """Check for coverage drift and emit warnings.

    Detects when the same requirement has conflicting coverage statuses
    across different artifacts (spec vs IP vs audit).
    """
    # Group by source file
    by_source: dict[Path, list[str]] = defaultdict(list)
    for entry in entries:
      source = entry.get("source")
      status = entry.get("status")
      artefact = entry.get("artefact")
      if source and status and artefact:
        by_source[source].append(f"{status} ({artefact})")

    # Check if all sources agree
    if len(by_source) <= 1:
      return

    statuses_by_source = {
      source: set(statuses) for source, statuses in by_source.items()
    }

    # Get unique status sets
    unique_status_sets = list({frozenset(s) for s in statuses_by_source.values()})

    # If all sources have the same set of statuses, no drift
    if len(unique_status_sets) <= 1:
      return

    # Drift detected - emit warning
    print(
      f"WARNING: Coverage drift detected for {req_id}",
      file=sys.stderr,
    )
    for source, status_list in sorted(by_source.items(), key=lambda x: x[0].name):
      print(
        f"  {source.name}: {', '.join(status_list)}",
        file=sys.stderr,
      )
    print(
      "  Action: Update specs or change artifacts to resolve inconsistency",
      file=sys.stderr,
    )

  def _compute_status_from_coverage(
    self,
    entries: list[dict[str, Any]],
  ) -> RequirementStatus | None:
    """Compute requirement status from aggregated coverage entries.

    Applies precedence rules:
    - ANY 'failed' or 'blocked' → in-progress (needs attention)
    - ALL 'verified' → active
    - ANY 'in-progress' → in-progress
    - ALL 'planned' → pending
    - MIXED → in-progress

    Returns None if no entries or unable to determine.
    """
    if not entries:
      return None

    statuses = {e.get("status") for e in entries if e.get("status")}
    if not statuses:
      return None

    # Failed or blocked coverage means requirement needs work
    if "failed" in statuses or "blocked" in statuses:
      return STATUS_IN_PROGRESS

    # All verified means requirement is live
    if statuses == {"verified"}:
      return STATUS_ACTIVE

    # In-progress or mixed statuses
    if "in-progress" in statuses or len(statuses) > 1:
      return STATUS_IN_PROGRESS

    # All planned
    if statuses == {"planned"}:
      return STATUS_PENDING

    return None

  def _apply_coverage_blocks(
    self,
    spec_files: Iterable[Path],
    delta_files: Iterable[Path],
    plan_files: Iterable[Path],
    audit_files: Iterable[Path],
  ) -> None:
    """Apply verification coverage blocks to update requirement lifecycle.

    Extracts coverage blocks from all artifact types, aggregates coverage
    entries by requirement, and updates verified_by lists.
    """
    coverage_map: dict[str, list[dict[str, Any]]] = defaultdict(list)

    # Extract from specs
    for spec_file in spec_files:
      try:
        blocks = load_coverage_blocks(spec_file)
      except (ValueError, OSError):
        continue
      for block in blocks:
        for entry in block.data.get("entries", []):
          req_id = entry.get("requirement")
          if not req_id:
            continue
          coverage_map[req_id].append(
            {
              "source": spec_file,
              "artefact": entry.get("artefact"),
              "status": entry.get("status"),
              "kind": entry.get("kind"),
            }
          )

    # Extract from deltas
    for delta_file in delta_files:
      try:
        blocks = load_coverage_blocks(delta_file)
      except (ValueError, OSError):
        continue
      for block in blocks:
        for entry in block.data.get("entries", []):
          req_id = entry.get("requirement")
          if not req_id:
            continue
          coverage_map[req_id].append(
            {
              "source": delta_file,
              "artefact": entry.get("artefact"),
              "status": entry.get("status"),
              "kind": entry.get("kind"),
            }
          )

    # Extract from implementation plans
    for plan_file in plan_files:
      try:
        blocks = load_coverage_blocks(plan_file)
      except (ValueError, OSError):
        continue
      for block in blocks:
        for entry in block.data.get("entries", []):
          req_id = entry.get("requirement")
          if not req_id:
            continue
          coverage_map[req_id].append(
            {
              "source": plan_file,
              "artefact": entry.get("artefact"),
              "status": entry.get("status"),
              "kind": entry.get("kind"),
            }
          )

    # Extract from audits
    for audit_file in audit_files:
      try:
        blocks = load_coverage_blocks(audit_file)
      except (ValueError, OSError):
        continue
      for block in blocks:
        for entry in block.data.get("entries", []):
          req_id = entry.get("requirement")
          if not req_id:
            continue
          coverage_map[req_id].append(
            {
              "source": audit_file,
              "artefact": entry.get("artefact"),
              "status": entry.get("status"),
              "kind": entry.get("kind"),
            }
          )

    # Update records
    for req_id, entries in coverage_map.items():
      record = self.records.get(req_id)
      if not record:
        continue

      # Check for drift before updating
      self._check_coverage_drift(req_id, entries)

      # Update coverage_evidence with unique artefact IDs
      artefacts = {e["artefact"] for e in entries if e.get("artefact")}
      record.coverage_evidence = sorted(set(record.coverage_evidence) | artefacts)

      # Compute and update status from coverage
      computed_status = self._compute_status_from_coverage(entries)
      if computed_status is not None:
        record.status = computed_status

  def _apply_spec_relationships(
    self,
    spec_id: str,
    body: str,
    *,
    validator: RelationshipsBlockValidator,
  ) -> None:
    if not body:
      return
    try:
      block = extract_relationships(body)
    except ValueError:
      return
    if not block:
      return
    if validator.validate(block, spec_id=spec_id):
      return

    data = block.data
    requirements = data.get("requirements") or {}
    primary = requirements.get("primary") or []
    collaborators = requirements.get("collaborators") or []

    for req_id in list(primary):
      record = self.records.get(req_id)
      if not record:
        continue
      if spec_id not in record.specs:
        record.specs.append(spec_id)
        record.specs.sort()

    for req_id in list(collaborators):
      record = self.records.get(req_id)
      if not record:
        continue
      if spec_id not in record.specs:
        record.specs.append(spec_id)
        record.specs.sort()

  def _apply_revision_requirement(
    self,
    payload: Mapping[str, Any],
    *,
    spec_registry: SpecRegistry | None,
  ) -> tuple[int, int]:
    created = 0
    updated = 0

    action = str(payload.get("action", "") or "").strip().lower()

    destination = payload.get("destination")
    if not isinstance(destination, Mapping):
      return created, updated

    target_spec = str(destination.get("spec", "")).strip()
    if not target_spec:
      return created, updated

    target_uid = str(
      destination.get("requirement_id") or payload.get("requirement_id") or "",
    ).strip()
    if not target_uid:
      return created, updated

    lifecycle = payload.get("lifecycle") if isinstance(payload, Mapping) else None
    lifecycle_map = lifecycle if isinstance(lifecycle, Mapping) else {}

    record = self.records.get(target_uid)
    if record is None:
      record = self._find_record_from_origin(payload)
      if record is not None and record.uid != target_uid:
        self.records.pop(record.uid, None)
        record.uid = target_uid
        record.label = target_uid.split(".", 1)[-1]
        self.records[target_uid] = record
      elif record is None:
        record = self._create_placeholder_record(
          target_uid,
          target_spec,
          payload,
          spec_registry=spec_registry,
          lifecycle=lifecycle_map,
        )
        created += 1

    changed = False

    if record.primary_spec != target_spec:
      record.primary_spec = target_spec
      changed = True

    current_specs = set(record.specs)
    if target_spec not in current_specs:
      current_specs.add(target_spec)
      changed = True

    additional_specs = destination.get("additional_specs")
    additional_set: set[str] = set()
    if isinstance(additional_specs, Iterable) and not isinstance(
      additional_specs,
      (str, bytes),
    ):
      for spec_id in additional_specs:
        spec_value = str(spec_id).strip()
        if spec_value and spec_value not in current_specs:
          current_specs.add(spec_value)
          changed = True
        if spec_value:
          additional_set.add(spec_value)

    if action == "move":
      allowed = {target_spec}.union(additional_set)
      filtered = {spec for spec in current_specs if spec in allowed}
      if filtered != current_specs:
        current_specs = filtered
        changed = True

    updated_specs = sorted(current_specs)
    if updated_specs != record.specs:
      record.specs = updated_specs
      changed = True

    status = lifecycle_map.get("status")
    if isinstance(status, str) and status and status != record.status:
      record.status = status
      changed = True

    introduced_by = lifecycle_map.get("introduced_by")
    if (
      isinstance(introduced_by, str)
      and introduced_by
      and record.introduced != introduced_by
    ):
      record.introduced = introduced_by
      changed = True

    implemented_by = lifecycle_map.get("implemented_by")
    if isinstance(implemented_by, Iterable) and not isinstance(
      implemented_by,
      (str, bytes),
    ):
      merged = {value for value in record.implemented_by if value}
      merged.update(str(item).strip() for item in implemented_by if str(item).strip())
      normalised = sorted(merged)
      if normalised != record.implemented_by:
        record.implemented_by = normalised
        changed = True

    verified_by = lifecycle_map.get("verified_by")
    if isinstance(verified_by, Iterable) and not isinstance(
      verified_by,
      (str, bytes),
    ):
      merged = {value for value in record.verified_by if value}
      merged.update(str(item).strip() for item in verified_by if str(item).strip())
      normalised = sorted(merged)
      if normalised != record.verified_by:
        record.verified_by = normalised
        changed = True

    kind = payload.get("kind")
    if isinstance(kind, str) and kind and kind != record.kind:
      record.kind = kind
      changed = True

    path = self._resolve_spec_path(target_spec, spec_registry)
    if path and path != record.path:
      record.path = path
      changed = True

    if changed and created == 0:
      updated += 1

    return created, updated

  def _find_record_from_origin(
    self,
    payload: Mapping[str, Any],
  ) -> RequirementRecord | None:
    origins = payload.get("origin")
    if not isinstance(origins, Iterable) or isinstance(origins, (str, bytes)):
      return None
    for origin in origins:
      if not isinstance(origin, Mapping):
        continue
      if origin.get("kind") != "requirement":
        continue
      ref = str(origin.get("ref", "")).strip()
      if ref and ref in self.records:
        return self.records[ref]
    return None

  def _create_placeholder_record(
    self,
    uid: str,
    spec_id: str,
    payload: Mapping[str, Any],
    *,
    spec_registry: SpecRegistry | None,
    lifecycle: Mapping[str, Any],
  ) -> RequirementRecord:
    label = uid.split(".", 1)[-1] if "." in uid else uid
    path = self._resolve_spec_path(spec_id, spec_registry)
    kind = str(payload.get("kind", "functional") or "functional")
    status = str(lifecycle.get("status", STATUS_PENDING) or STATUS_PENDING)
    introduced = lifecycle.get("introduced_by")
    implemented_by = []
    raw_impl = lifecycle.get("implemented_by")
    if isinstance(raw_impl, Iterable) and not isinstance(raw_impl, (str, bytes)):
      implemented_by = [str(item).strip() for item in raw_impl if str(item).strip()]
    verified_by = []
    raw_ver = lifecycle.get("verified_by")
    if isinstance(raw_ver, Iterable) and not isinstance(raw_ver, (str, bytes)):
      verified_by = [str(item).strip() for item in raw_ver if str(item).strip()]
    record = RequirementRecord(
      uid=uid,
      label=label,
      title=str(payload.get("summary", "") or label),
      specs=[spec_id],
      primary_spec=spec_id,
      kind=kind,
      status=status,
      introduced=str(introduced)
      if isinstance(introduced, str) and introduced
      else None,
      implemented_by=implemented_by,
      verified_by=verified_by,
      path=path,
    )
    self.records[uid] = record
    return record

  def _resolve_spec_path(
    self,
    spec_id: str,
    spec_registry: SpecRegistry | None,
  ) -> str:
    if not spec_registry:
      return ""
    spec = spec_registry.get(spec_id)
    if not spec:
      return ""
    try:
      return spec.path.relative_to(spec_registry.root).as_posix()
    except ValueError:
      return spec.path.as_posix()

  def _iter_change_files(self, dirs: Iterable[Path], prefix: str) -> Iterator[Path]:
    for directory in dirs:
      if not directory.exists():
        continue
      for bundle in directory.iterdir():
        if not bundle.is_dir():
          continue
        for file in bundle.glob("*.md"):
          if file.name.startswith(prefix):
            yield file

  def _iter_plan_files(self, dirs: Iterable[Path]) -> Iterator[Path]:
    """Iterate over implementation plan files in directories."""
    for directory in dirs:
      if not directory.exists():
        continue
      for bundle in directory.iterdir():
        if not bundle.is_dir():
          continue
        for file in bundle.glob("*.md"):
          if file.name.startswith("IP-"):
            yield file

  def _records_from_frontmatter(
    self,
    spec_id: str,
    frontmatter: Any,
    body: str,
    spec_path: Path,
    repo_root: Path,
  ) -> Iterator[RequirementRecord]:
    data = getattr(frontmatter, "data", frontmatter)
    mapping = dict(data) if isinstance(data, Mapping) else {}
    mapping.setdefault("id", spec_id)
    yield from self._records_from_content(
      spec_id,
      mapping,
      body,
      spec_path,
      repo_root,
    )

  def _records_from_content(
    self,
    spec_id: str,
    _frontmatter: Mapping[str, Any],
    body: str,
    spec_path: Path,
    repo_root: Path,
  ) -> Iterator[RequirementRecord]:
    """Extract requirement records from spec body content.

    Logs warnings if requirement-like lines are found but not extracted.
    """
    try:
      path = spec_path.relative_to(repo_root).as_posix()
    except ValueError:
      path = spec_path.as_posix()

    requirement_like_lines = []
    extracted_count = 0

    for line in body.splitlines():
      # Track lines that look like requirements for diagnostics
      if re.search(r"\b(FR|NF)-\d{3}\b", line, re.IGNORECASE):
        requirement_like_lines.append(line.strip())

      match = _REQUIREMENT_LINE.match(line)
      if not match:
        continue

      extracted_count += 1
      prefix, number, title = match.groups()
      label = f"{prefix.upper()}-{number}"
      uid = f"{spec_id}.{label}"
      kind = "functional" if label.startswith("FR-") else "non-functional"
      yield RequirementRecord(
        uid=uid,
        label=label,
        title=title.strip(),
        specs=[spec_id],
        primary_spec=spec_id,
        kind=kind,
        status=STATUS_PENDING,
        path=path,
      )

    # Warn if we found requirement-like lines but extracted none
    if requirement_like_lines and extracted_count == 0:
      logger.warning(
        "Spec %s at %s: Found %d requirement-like lines but extracted 0. "
        "First line: %s",
        spec_id,
        spec_path.name,
        len(requirement_like_lines),
        requirement_like_lines[0][:80],
      )

  def _requirements_from_spec(
    self,
    spec_path: Path,
    spec_id: str,
    repo_root: Path,
  ) -> Iterator[RequirementRecord]:
    frontmatter, body = load_markdown_file(spec_path)
    yield from self._records_from_content(
      spec_id,
      frontmatter,
      body,
      spec_path,
      repo_root,
    )

  # ------------------------------------------------------------------
  def move_requirement(
    self,
    uid: str,
    new_spec_id: str,
    *,
    spec_registry: SpecRegistry | None = None,
    introduced_by: str | None = None,
  ) -> str:
    """Move requirement to different spec, returning new UID."""
    if uid not in self.records:
      msg = f"Requirement {uid} not found"
      raise KeyError(msg)
    record = self.records.pop(uid)
    label = record.label
    new_uid = f"{new_spec_id}.{label}"
    if new_uid in self.records:
      msg = f"Requirement {new_uid} already exists"
      raise ValueError(msg)

    old_primary = record.primary_spec

    if spec_registry:
      spec = spec_registry.get(new_spec_id)
      if spec is None:
        msg = f"Spec {new_spec_id} not found"
        raise ValueError(msg)
      try:
        record.path = spec.path.relative_to(spec_registry.root).as_posix()
      except ValueError:
        record.path = spec.path.as_posix()
    else:
      record.path = record.path

    specs = set(record.specs)
    if old_primary:
      specs.discard(old_primary)
    specs.add(new_spec_id)
    record.specs = sorted(specs)
    record.primary_spec = new_spec_id
    record.uid = new_uid
    if introduced_by:
      record.introduced = introduced_by

    self.records[new_uid] = record
    return new_uid

  # ------------------------------------------------------------------
  def search(
    self,
    *,
    query: str | None = None,
    status: RequirementStatus | None = None,
    spec: str | None = None,
    implemented_by: str | None = None,
    introduced_by: str | None = None,
    verified_by: str | None = None,
  ) -> list[RequirementRecord]:
    """Search requirements by query text and various filters."""
    query_norm = query.lower() if query else None
    results: list[RequirementRecord] = []
    for record in self.records.values():
      if status and record.status != status:
        continue
      if spec and spec not in record.specs:
        continue
      if implemented_by and implemented_by not in record.implemented_by:
        continue
      if introduced_by and record.introduced != introduced_by:
        continue
      if verified_by and verified_by not in record.verified_by:
        continue
      if query_norm:
        haystack = f"{record.uid} {record.label} {record.title}".lower()
        if query_norm not in haystack:
          continue
      results.append(record)
    return sorted(results, key=lambda r: r.uid)

  def set_status(self, uid: str, status: RequirementStatus) -> None:
    """Set the status of a requirement."""
    if status not in VALID_STATUSES:
      msg = f"Invalid status {status!r}; must be one of {sorted(VALID_STATUSES)}"
      raise ValueError(
        msg,
      )
    try:
      record = self.records[uid]
    except KeyError as exc:
      msg = f"Requirement {uid} not found"
      raise KeyError(msg) from exc
    record.status = status


__all__ = [
  "RequirementRecord",
  "RequirementsRegistry",
  "SyncStats",
]
