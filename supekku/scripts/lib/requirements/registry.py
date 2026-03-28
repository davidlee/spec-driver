"""Requirements management and processing utilities."""

from __future__ import annotations

import fnmatch
import logging
from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING

import yaml

from supekku.scripts.lib.blocks.relationships import RelationshipsBlockValidator
from supekku.scripts.lib.core.repo import find_repo_root

from .coverage import _apply_coverage_blocks
from .lifecycle import (
  VALID_STATUSES,
  RequirementStatus,
)
from .models import RequirementRecord, SyncStats
from .parser import (
  _is_requirement_like_line,
  _load_breakout_metadata,
  _records_from_content,
  _records_from_frontmatter,
  _validate_extraction,
)
from .sync import (
  _apply_audit_relations,
  _apply_delta_relations,
  _apply_revision_blocks,
  _apply_revision_relations,
  _apply_spec_relationships,
  _iter_change_files,
  _iter_spec_files,
  _sync_backlog_requirements,
  _upsert_record,
)

if TYPE_CHECKING:
  from pathlib import Path

  from supekku.scripts.lib.backlog.registry import BacklogRegistry
  from supekku.scripts.lib.specs.registry import SpecRegistry

logger = logging.getLogger(__name__)

# Re-exports for backward compatibility
__all__ = [
  "RequirementRecord",
  "RequirementsRegistry",
  "SyncStats",
  "_REQUIREMENT_HEADING",
  "_is_requirement_like_line",
]

# Re-export regex for test imports
from .parser import _REQUIREMENT_HEADING  # noqa: E402, F401


class RequirementsRegistry:
  """Registry for managing requirement records and lifecycle tracking."""

  def __init__(
    self,
    registry_path: Path | None = None,
    *,
    root: Path | None = None,
  ) -> None:
    if registry_path is None and root is None:
      root = find_repo_root()
    if registry_path is None:
      from supekku.scripts.lib.core.paths import get_registry_dir  # noqa: PLC0415

      registry_path = get_registry_dir(root) / "requirements.yaml"
    self.registry_path = registry_path
    self.records: dict[str, RequirementRecord] = {}
    self._load()

  # -- ADR-009 standard surface --------------------------------------------

  def find(self, uid: str) -> RequirementRecord | None:
    """Find a requirement record by its UID."""
    return self.records.get(uid)

  def collect(self) -> dict[str, RequirementRecord]:
    """Return all requirement records as a dictionary keyed by UID."""
    return dict(self.records)

  def iter(self, *, status: str | None = None) -> Iterator[RequirementRecord]:
    """Iterate over requirement records, optionally filtered by status."""
    for record in self.records.values():
      if status is None or record.status == status:
        yield record

  def filter(
    self,
    *,
    status: str | None = None,
    spec: str | None = None,
    kind: str | None = None,
    tag: str | None = None,
  ) -> list[RequirementRecord]:
    """Filter requirement records by multiple criteria (AND logic)."""
    results = []
    for record in self.iter(status=status):
      if spec and spec not in record.specs:
        continue
      if kind and record.kind != kind:
        continue
      if tag and tag not in record.tags:
        continue
      results.append(record)
    return results

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
  def sync(
    self,
    spec_dirs: Iterable[Path] | None = None,
    *,
    spec_registry: SpecRegistry | None = None,
    delta_dirs: Iterable[Path] | None = None,
    revision_dirs: Iterable[Path] | None = None,
    audit_dirs: Iterable[Path] | None = None,
    plan_dirs: Iterable[Path] | None = None,
    backlog_registry: BacklogRegistry | None = None,
  ) -> SyncStats:
    """Sync requirements from specs, change artifacts, and backlog items."""
    repo_root = spec_registry.root if spec_registry else find_repo_root()
    stats = SyncStats()
    seen: set[str] = set()
    yielded_ids: set[str] = set()

    # Per-spec extracted UIDs for post-relation pruning (DR-129 §1.3).
    # Distinct from ``seen`` which tracks *all* UIDs (including backlog-sourced)
    # through ``_upsert_record``.  ``spec_extractions`` tracks only body-extracted
    # UIDs per spec, used to identify orphaned registry entries after all
    # relation/revision/coverage steps complete.
    spec_extractions: dict[str, set[str]] = {}

    relationships_validator = RelationshipsBlockValidator()

    # Collect (spec_id, body) pairs for deferred relationship application.
    deferred_relationships: list[tuple[str, str]] = []

    if spec_registry:
      for spec in spec_registry.all_specs():
        records = list(
          _records_from_frontmatter(
            spec.id,
            spec.frontmatter,
            spec.body,
            spec.path,
            repo_root,
            stats=stats,
          ),
        )
        extracted_uids: set[str] = set()
        for record in records:
          _upsert_record(self.records, record, seen, stats)
          extracted_uids.add(record.uid)
          yielded_ids.add(spec.id)
        spec_extractions[spec.id] = extracted_uids

        deferred_relationships.append((spec.id, spec.body))

    directories = list(spec_dirs or [])
    if directories:
      for spec_file in _iter_spec_files(directories):
        from supekku.scripts.lib.core.spec_utils import (  # noqa: PLC0415
          load_markdown_file,
        )

        frontmatter, body = load_markdown_file(spec_file)
        spec_id = str(frontmatter.get("id", "")).strip()
        if not spec_id or spec_id in yielded_ids:
          continue
        breakout_meta = _load_breakout_metadata(spec_file)
        records = list(
          _records_from_content(
            spec_id,
            frontmatter,
            body,
            spec_file,
            repo_root,
            stats=stats,
          ),
        )
        extracted_uids = set()
        for record in records:
          meta = breakout_meta.get(record.uid, {})
          if meta:
            if "tags" in meta:
              record.tags = sorted(set(record.tags) | set(meta["tags"]))
            if "ext_id" in meta:
              record.ext_id = meta["ext_id"]
            if "ext_url" in meta:
              record.ext_url = meta["ext_url"]
          _upsert_record(self.records, record, seen, stats)
          extracted_uids.add(record.uid)
        spec_extractions[spec_id] = extracted_uids

        try:
          body = spec_file.read_text(encoding="utf-8")
        except OSError:
          body = ""
        deferred_relationships.append((spec_id, body))

    # Apply all relationship blocks now that every requirement exists.
    for spec_id, body in deferred_relationships:
      _apply_spec_relationships(
        self.records,
        spec_id,
        body,
        validator=relationships_validator,
      )

    from supekku.scripts.lib.blocks.delta import (  # noqa: PLC0415
      DeltaRelationshipsValidator,
    )

    delta_validator = DeltaRelationshipsValidator()
    if delta_dirs:
      _apply_delta_relations(
        self.records,
        delta_dirs,
        repo_root,
        validator=delta_validator,
      )
    if revision_dirs:
      _apply_revision_relations(self.records, revision_dirs)
      _apply_revision_blocks(
        self.records,
        revision_dirs,
        spec_registry=spec_registry,
        stats=stats,
      )
    if audit_dirs:
      _apply_audit_relations(self.records, audit_dirs)

    # Sync requirements from backlog items
    if backlog_registry:
      _sync_backlog_requirements(
        self.records,
        backlog_registry,
        repo_root,
        seen,
        stats,
      )

    # Apply coverage blocks to update lifecycle from verification entries
    spec_files = []
    if spec_registry:
      spec_files = [spec.path for spec in spec_registry.all_specs()]
    elif spec_dirs:
      spec_files = list(_iter_spec_files(spec_dirs))

    delta_files = []
    if delta_dirs:
      delta_files = list(_iter_change_files(delta_dirs, prefix="DE-"))

    plan_files = []
    if plan_dirs:
      plan_files = list(_iter_change_files(plan_dirs, prefix="IP-"))

    audit_files = []
    if audit_dirs:
      audit_files = list(_iter_change_files(audit_dirs, prefix="AUD-"))

    if spec_files or delta_files or plan_files or audit_files:
      _apply_coverage_blocks(
        self.records,
        spec_files=spec_files,
        delta_files=delta_files,
        plan_files=plan_files,
        audit_files=audit_files,
      )

    # -- Post-relation stale requirement pruning (DR-129 §1.3) -----------
    # Runs after all extraction, relation, revision, and coverage steps so
    # that revision moves (which update primary_spec) have already landed.
    for spec_id, extracted_uids in spec_extractions.items():
      orphans = [
        uid
        for uid, rec in self.records.items()
        if rec.primary_spec == spec_id
        and uid not in extracted_uids
        and not rec.introduced  # protect revision-introduced requirements
      ]
      for uid in orphans:
        del self.records[uid]
        stats.pruned += 1
        logger.info(
          "Pruned stale requirement %s (absent from %s body)",
          uid,
          spec_id,
        )

    # Clean specs list for records not seen this run
    for uid, record in list(self.records.items()):
      if uid not in seen:
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
          source_kind=record.source_kind,
          source_type=record.source_type,
        )

    # Validation: warn about specs with no extracted requirements
    if spec_registry:
      _validate_extraction(spec_registry, seen)

    # -- Summary line (DR-129 §1.8) ----------------------------------------
    if stats.warnings or stats.pruned:
      logger.warning(
        "Sync complete: %d created, %d updated, %d pruned, %d warnings "
        "(run with -v for details)",
        stats.created,
        stats.updated,
        stats.pruned,
        stats.warnings,
      )
    else:
      logger.info(
        "Sync complete: %d created, %d updated, %d pruned",
        stats.created,
        stats.updated,
        stats.pruned,
      )

    return stats

  sync_from_specs = sync  # Deprecated alias — use sync() instead.

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
      raise ValueError(msg)
    try:
      record = self.records[uid]
    except KeyError as exc:
      msg = f"Requirement {uid} not found"
      raise KeyError(msg) from exc
    record.status = status

  def find_by_verified_by(
    self, artifact_pattern: str | None
  ) -> list[RequirementRecord]:
    """Find requirements verified by specific artifact(s) using glob patterns.

    Searches both verified_by and coverage_evidence fields.
    """
    if not artifact_pattern:
      return []

    matches: list[RequirementRecord] = []
    for record in self.records.values():
      all_artifacts = (record.verified_by or []) + (record.coverage_evidence or [])
      for artifact_id in all_artifacts:
        if fnmatch.fnmatch(artifact_id, artifact_pattern):
          matches.append(record)
          break
    return sorted(matches, key=lambda r: r.uid)

  def find_by_verification_status(self, statuses: list[str]) -> list[RequirementRecord]:
    """Find requirements with coverage entries matching given statuses."""
    if not statuses:
      return []

    status_set = set(statuses)
    return sorted(
      (
        r
        for r in self.records.values()
        if any(e.get("status") in status_set for e in r.coverage_entries)
      ),
      key=lambda r: r.uid,
    )

  def find_by_verification_kind(self, kinds: list[str]) -> list[RequirementRecord]:
    """Find requirements with coverage entries matching given kinds."""
    if not kinds:
      return []

    kind_set = set(kinds)
    return sorted(
      (
        r
        for r in self.records.values()
        if any(e.get("kind") in kind_set for e in r.coverage_entries)
      ),
      key=lambda r: r.uid,
    )
