"""Requirements management and processing utilities."""

from __future__ import annotations

import fnmatch
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
from supekku.scripts.lib.blocks.verification import (
  VALID_COVERAGE_STATUSES,
  load_coverage_blocks,
)
from supekku.scripts.lib.core.repo import find_repo_root
from supekku.scripts.lib.core.spec_utils import load_markdown_file
from supekku.scripts.lib.relations.manager import list_relations

from .lifecycle import (
  STATUS_ACTIVE,
  STATUS_IN_PROGRESS,
  STATUS_PENDING,
  TERMINAL_STATUSES,
  VALID_STATUSES,
  RequirementStatus,
)

if TYPE_CHECKING:
  from pathlib import Path

  from supekku.scripts.lib.backlog.registry import BacklogRegistry
  from supekku.scripts.lib.specs.registry import SpecRegistry

logger = logging.getLogger(__name__)

# Updated pattern to support both formats:
# - **FR-001**: Short format (legacy)
# - **PROD-010.FR-001**: Fully-qualified format (current standard)
# Optional tags in square brackets after category: **FR-001**(cat)[tag1, tag2]: Title
_REQUIREMENT_LINE = re.compile(
  r"^\s*[-*]\s*\*{0,2}\s*(?:[A-Z]+-\d{3}\.)?("
  r"FR|NF)-(\d{3})\s*\*{0,2}\s*(?:\(([^)]+)\))?"
  r"(?:\[([^\]]*)\])?\s*[:\-–]\s*(.+)$",
  re.IGNORECASE,
)

# Heading format for backlog items: ### FR-016.001: Title
# Matches dotted format only (NNN.MMM) — no overlap with spec bullet format.
_REQUIREMENT_HEADING = re.compile(
  r"^\s*#{1,4}\s+(FR|NF)-(\d{3})\.(\d{3})\s*[:\-–]\s*(.+)$",
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
  category: str | None = None
  status: RequirementStatus = STATUS_PENDING
  tags: list[str] = field(default_factory=list)
  introduced: str | None = None
  implemented_by: list[str] = field(default_factory=list)
  verified_by: list[str] = field(default_factory=list)
  coverage_evidence: list[str] = field(default_factory=list)
  coverage_entries: list[dict[str, Any]] = field(default_factory=list)
  path: str = ""
  ext_id: str = ""
  ext_url: str = ""
  source_kind: str = ""
  source_type: str = ""

  def merge(self, other: RequirementRecord) -> RequirementRecord:
    """Merge data from another record, preserving lifecycle fields."""
    return RequirementRecord(
      uid=self.uid,
      label=self.label,
      title=other.title,
      specs=sorted(set(self.specs) | set(other.specs)),
      primary_spec=other.primary_spec or self.primary_spec,
      kind=other.kind or self.kind,
      category=other.category or self.category,
      status=self.status,
      tags=sorted(set(self.tags) | set(other.tags)),
      introduced=self.introduced,
      implemented_by=list(self.implemented_by),
      verified_by=list(self.verified_by),
      coverage_evidence=sorted(
        set(self.coverage_evidence) | set(other.coverage_evidence)
      ),
      coverage_entries=list(self.coverage_entries),
      path=other.path or self.path,
      source_kind=other.source_kind or self.source_kind,
      source_type=other.source_type or self.source_type,
    )

  def to_dict(self) -> dict[str, object]:
    """Convert requirement record to dictionary for serialization."""
    d: dict[str, object] = {
      "label": self.label,
      "title": self.title,
      "specs": self.specs,
      "primary_spec": self.primary_spec,
      "kind": self.kind,
      "category": self.category,
      "status": self.status,
      "tags": self.tags,
      "introduced": self.introduced,
      "implemented_by": self.implemented_by,
      "verified_by": self.verified_by,
      "coverage_evidence": self.coverage_evidence,
      "coverage_entries": self.coverage_entries,
      "path": self.path,
    }
    if self.ext_id:
      d["ext_id"] = self.ext_id
    if self.ext_url:
      d["ext_url"] = self.ext_url
    if self.source_kind:
      d["source_kind"] = self.source_kind
    if self.source_type:
      d["source_type"] = self.source_type
    return d

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
      category=data.get("category"),
      status=str(data.get("status", STATUS_PENDING)),
      tags=list(data.get("tags", [])),
      introduced=data.get("introduced"),
      implemented_by=list(data.get("implemented_by", [])),
      verified_by=list(data.get("verified_by", [])),
      coverage_evidence=list(data.get("coverage_evidence", [])),
      coverage_entries=list(data.get("coverage_entries", [])),
      path=str(data.get("path", "")),
      source_kind=str(data.get("source_kind", "")),
      source_type=str(data.get("source_type", "")),
    )


@dataclass
class SyncStats:
  """Statistics tracking for synchronization operations."""

  created: int = 0
  updated: int = 0


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
    """Find a requirement record by its UID.

    Returns:
      RequirementRecord or None if not found.
    """
    return self.records.get(uid)

  def collect(self) -> dict[str, RequirementRecord]:
    """Return all requirement records as a dictionary keyed by UID.

    Returns:
      Copy of the internal records dictionary.
    """
    return dict(self.records)

  def iter(self, *, status: str | None = None) -> Iterator[RequirementRecord]:
    """Iterate over requirement records, optionally filtered by status.

    Args:
      status: If provided, yield only records with this status.

    Yields:
      RequirementRecord instances.
    """
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
    """Filter requirement records by multiple criteria (AND logic).

    Args:
      status: Filter by status field.
      spec: Filter by spec membership (primary or secondary).
      kind: Filter by kind (functional/non-functional).
      tag: Filter by tag membership.

    Returns:
      List of matching RequirementRecords.
    """
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

    relationships_validator = RelationshipsBlockValidator()

    # Collect (spec_id, body) pairs for deferred relationship application.
    # Relationships reference requirements from other specs, so all
    # requirements must be created before any relationship block is applied.
    deferred_relationships: list[tuple[str, str]] = []

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
          self._upsert_record(record, seen, stats)
          yielded_ids.add(spec.id)

        deferred_relationships.append((spec.id, spec.body))

    directories = list(spec_dirs or [])
    if directories:
      for spec_file in self._iter_spec_files(directories):
        frontmatter, body = load_markdown_file(spec_file)
        spec_id = str(frontmatter.get("id", "")).strip()
        if not spec_id or spec_id in yielded_ids:
          continue
        breakout_meta = self._load_breakout_metadata(spec_file)
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
          meta = breakout_meta.get(record.uid, {})
          if meta:
            if "tags" in meta:
              record.tags = sorted(set(record.tags) | set(meta["tags"]))
            if "ext_id" in meta:
              record.ext_id = meta["ext_id"]
            if "ext_url" in meta:
              record.ext_url = meta["ext_url"]
          self._upsert_record(record, seen, stats)

        try:
          body = spec_file.read_text(encoding="utf-8")
        except OSError:
          body = ""
        deferred_relationships.append((spec_id, body))

    # Apply all relationship blocks now that every requirement exists.
    for spec_id, body in deferred_relationships:
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

    # Sync requirements from backlog items
    if backlog_registry:
      self._sync_backlog_requirements(
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
      spec_files = list(self._iter_spec_files(spec_dirs))

    delta_files = []
    if delta_dirs:
      delta_files = list(self._iter_change_files(delta_dirs, prefix="DE-"))

    plan_files = []
    if plan_dirs:
      plan_files = list(self._iter_change_files(plan_dirs, prefix="IP-"))

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
          source_kind=record.source_kind,
          source_type=record.source_type,
        )

    # Validation: warn about specs with no extracted requirements
    if spec_registry:
      self._validate_extraction(spec_registry, seen)

    return stats

  sync_from_specs = sync  # Deprecated alias — use sync() instead.

  def _upsert_record(
    self,
    record: RequirementRecord,
    seen: set[str],
    stats: SyncStats,
    source_kind: str = "",
    source_type: str = "",
  ) -> None:
    """Merge-or-create a requirement record, tracking it in *seen*.

    If *source_kind* or *source_type* are provided they are stamped on the
    record **after** merge so the freshly-extracted provenance wins.
    """
    seen.add(record.uid)
    existing = self.records.get(record.uid)
    if existing is not None:
      merged = existing.merge(record)
      if source_kind:
        merged = RequirementRecord(**{**merged.__dict__, "source_kind": source_kind})
      if source_type:
        merged = RequirementRecord(**{**merged.__dict__, "source_type": source_type})
      if merged != existing:
        self.records[record.uid] = merged
        stats.updated += 1
    else:
      if source_kind:
        record = RequirementRecord(**{**record.__dict__, "source_kind": source_kind})
      if source_type:
        record = RequirementRecord(**{**record.__dict__, "source_type": source_type})
      self.records[record.uid] = record
      stats.created += 1

  def _sync_backlog_requirements(
    self,
    backlog_registry: BacklogRegistry,
    repo_root: Path,
    seen: set[str],
    stats: SyncStats,
  ) -> None:
    """Extract and upsert requirements from backlog items."""
    for item in backlog_registry.iter():
      try:
        frontmatter, body = load_markdown_file(item.path)
      except OSError:
        logger.warning("Cannot read backlog item %s at %s", item.id, item.path)
        continue

      records = list(
        self._records_from_content(
          item.id,
          frontmatter,
          body,
          item.path,
          repo_root,
        ),
      )
      for record in records:
        self._upsert_record(
          record,
          seen,
          stats,
          source_kind=item.kind,
          source_type="backlog",
        )

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
          f"Expected format: '- **FR-001**: Title' or '- **SPEC-100.FR-001**: Title' "
          f"(label inside **bold** must be bare — no description). "
          f"Check {spec.path.name}",
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

    Only entries with statuses in VALID_COVERAGE_STATUSES are considered.
    Unknown statuses are silently ignored (warnings are emitted at the
    ingestion boundary in _apply_coverage_blocks).

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

    statuses = {
      e.get("status") for e in entries if e.get("status") in VALID_COVERAGE_STATUSES
    }
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

  @staticmethod
  def _extract_coverage_entries(
    files: Iterable[Path],
    coverage_map: dict[str, list[dict[str, Any]]],
  ) -> None:
    """Extract coverage entries from a set of artifact files into coverage_map.

    Entries with unknown statuses are still recorded (for transparency in
    coverage_entries) but a warning is emitted.  The downstream
    _compute_status_from_coverage() independently filters unknown statuses
    so they never influence derived requirement state.
    """
    for source_file in files:
      try:
        blocks = load_coverage_blocks(source_file)
      except (ValueError, OSError):
        continue
      for block in blocks:
        for entry in block.data.get("entries", []):
          req_id = entry.get("requirement")
          if not req_id:
            continue
          status = entry.get("status")
          if status and status not in VALID_COVERAGE_STATUSES:
            print(
              f"WARNING: Coverage entry for {req_id} has unknown status "
              f"{status!r} in {source_file.name}; "
              f"entry will not influence derived requirement status",
              file=sys.stderr,
            )
          coverage_map[req_id].append(
            {
              "source": source_file,
              "artefact": entry.get("artefact"),
              "status": status,
              "kind": entry.get("kind"),
            }
          )

  def _apply_coverage_blocks(
    self,
    spec_files: Iterable[Path],
    delta_files: Iterable[Path],
    plan_files: Iterable[Path],
    audit_files: Iterable[Path],
  ) -> None:
    """Apply verification coverage blocks to update requirement lifecycle.

    Extracts coverage blocks from all artifact types, rebuilds coverage
    fields from current sources (not accumulated), and derives status.

    Coverage fields are cleared first so that removed coverage blocks
    correctly result in empty evidence — the registry is a derived
    projection (ADR-008 §5), not a persistent accumulator.

    Terminal-status requirements (deprecated, superseded, retired) are
    not overwritten by coverage-derived status.
    """
    # Clear all coverage fields — will be rebuilt from current sources
    for record in self.records.values():
      record.coverage_evidence = []
      record.coverage_entries = []

    coverage_map: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for files in (spec_files, delta_files, plan_files, audit_files):
      self._extract_coverage_entries(files, coverage_map)

    # Rebuild from current sources
    for req_id, entries in coverage_map.items():
      record = self.records.get(req_id)
      if not record:
        continue

      # Check for drift before updating
      self._check_coverage_drift(req_id, entries)

      # Store structured coverage entries on the record
      record.coverage_entries = [
        {k: v for k, v in e.items() if k != "source"} for e in entries
      ]

      # Derive coverage_evidence from current sources
      artefacts = {e["artefact"] for e in entries if e.get("artefact")}
      record.coverage_evidence = sorted(artefacts)

      # Derive status — skip terminal statuses (normative, not derived)
      if record.status in TERMINAL_STATUSES:
        continue
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

  @staticmethod
  def _load_breakout_metadata(
    spec_path: Path,
  ) -> dict[str, dict[str, Any]]:
    """Load metadata from breakout requirement files under a spec.

    Scans ``spec_path.parent / "requirements"`` for ``*.md`` files and
    extracts ``tags``, ``ext_id``, and ``ext_url`` from their frontmatter.

    Returns:
      Mapping from qualified requirement ID (e.g. ``SPEC-100.FR-010``)
      to a dict of metadata fields.
    """
    requirements_dir = spec_path.parent / "requirements"
    if not requirements_dir.is_dir():
      return {}
    result: dict[str, dict[str, Any]] = {}
    for file in requirements_dir.glob("*.md"):
      try:
        fm, _ = load_markdown_file(file)
      except (OSError, ValueError):
        continue
      req_id = str(fm.get("id", "")).strip()
      if not req_id:
        continue
      meta: dict[str, Any] = {}
      fm_tags = fm.get("tags")
      if isinstance(fm_tags, list):
        meta["tags"] = [str(t) for t in fm_tags if str(t).strip()]
      fm_ext_id = fm.get("ext_id")
      if fm_ext_id:
        meta["ext_id"] = str(fm_ext_id)
      fm_ext_url = fm.get("ext_url")
      if fm_ext_url:
        meta["ext_url"] = str(fm_ext_url)
      if meta:
        result[req_id] = meta
    return result

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
    breakout_meta = self._load_breakout_metadata(spec_path)
    for record in self._records_from_content(
      spec_id,
      mapping,
      body,
      spec_path,
      repo_root,
    ):
      meta = breakout_meta.get(record.uid, {})
      if meta:
        if "tags" in meta:
          record.tags = sorted(set(record.tags) | set(meta["tags"]))
        if "ext_id" in meta:
          record.ext_id = meta["ext_id"]
        if "ext_url" in meta:
          record.ext_url = meta["ext_url"]
      yield record

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

      # Try bullet format first (spec requirements)
      match = _REQUIREMENT_LINE.match(line)
      if match:
        extracted_count += 1
        prefix, number, category, tags_raw, title = match.groups()
        label = f"{prefix.upper()}-{number}"
        uid = f"{spec_id}.{label}"
        kind = "functional" if label.startswith("FR-") else "non-functional"
        inline_category = category.strip() if category else None
        frontmatter_category = _frontmatter.get("category")
        final_category = inline_category or frontmatter_category
        tags = (
          sorted(t.strip() for t in tags_raw.split(",") if t.strip())
          if tags_raw
          else []
        )

        yield RequirementRecord(
          uid=uid,
          label=label,
          title=title.strip(),
          specs=[spec_id],
          primary_spec=spec_id,
          kind=kind,
          category=final_category,
          status=STATUS_PENDING,
          tags=tags,
          path=path,
        )
        continue

      # Try heading format (backlog dotted requirements)
      heading_match = _REQUIREMENT_HEADING.match(line)
      if heading_match:
        extracted_count += 1
        prefix, artifact_num, seq_num, title = heading_match.groups()
        label = f"{prefix.upper()}-{artifact_num}.{seq_num}"
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
        "Expected format: '- **FR-001**: Title' or '- **SPEC-100.FR-001**: Title'. "
        "The label inside **bold** must be bare (no description). "
        "First unmatched line: %s",
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

  def find_by_verified_by(
    self, artifact_pattern: str | None
  ) -> list[RequirementRecord]:
    """Find requirements verified by specific artifact(s) using glob patterns.

    Searches both verified_by and coverage_evidence fields.

    Args:
      artifact_pattern: Artifact ID or glob pattern (e.g., "VT-CLI-001" or "VT-*").
                        Returns empty list if None or empty string.

    Returns:
      List of RequirementRecord objects verified by matching artifacts.
      Returns empty list if artifact_pattern is None, empty, or no matches found.
    """

    if not artifact_pattern:
      return []

    matches: list[RequirementRecord] = []

    for record in self.records.values():
      # Combine both verified_by and coverage_evidence fields
      all_artifacts = (record.verified_by or []) + (record.coverage_evidence or [])

      # Check if any artifact matches the pattern
      for artifact_id in all_artifacts:
        if fnmatch.fnmatch(artifact_id, artifact_pattern):
          matches.append(record)
          break  # Only add each requirement once

    return sorted(matches, key=lambda r: r.uid)

  def find_by_verification_status(self, statuses: list[str]) -> list[RequirementRecord]:
    """Find requirements with coverage entries matching given statuses.

    A requirement matches if ANY of its coverage_entries has a status
    in the provided list (OR logic).

    Args:
      statuses: List of verification statuses to match.
                Returns empty list if empty.

    Returns:
      Sorted list of matching RequirementRecord objects.
    """
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
    """Find requirements with coverage entries matching given kinds.

    A requirement matches if ANY of its coverage_entries has a kind
    in the provided list (OR logic).

    Args:
      kinds: List of verification kinds (VT, VA, VH) to match.
             Returns empty list if empty.

    Returns:
      Sorted list of matching RequirementRecord objects.
    """
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


__all__ = [
  "RequirementRecord",
  "RequirementsRegistry",
  "SyncStats",
]
