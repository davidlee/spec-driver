"""Requirement synchronization — change artifact relations and record upsert."""

from __future__ import annotations

import logging
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import replace
from typing import TYPE_CHECKING, Any

from supekku.scripts.lib.blocks.delta import (
  DeltaRelationshipsValidator,
  extract_delta_relationships,
)
from supekku.scripts.lib.blocks.revision import (
  RevisionBlockValidator,
  load_revision_blocks,
)
from supekku.scripts.lib.core.spec_utils import load_markdown_file
from supekku.scripts.lib.relations.manager import list_relations

from .models import RequirementRecord, SyncStats
from .parser import _records_from_content

if TYPE_CHECKING:
  from pathlib import Path

  from supekku.scripts.lib.backlog.registry import BacklogRegistry
  from supekku.scripts.lib.specs.registry import SpecRegistry

logger = logging.getLogger(__name__)


def _upsert_record(
  records: dict[str, RequirementRecord],
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
  existing = records.get(record.uid)
  if existing is not None:
    merged = existing.merge(record)
    if source_kind:
      merged = replace(merged, source_kind=source_kind)
    if source_type:
      merged = replace(merged, source_type=source_type)
    if merged != existing:
      records[record.uid] = merged
      stats.updated += 1
  else:
    if source_kind:
      record = replace(record, source_kind=source_kind)
    if source_type:
      record = replace(record, source_type=source_type)
    records[record.uid] = record
    stats.created += 1


def _sync_backlog_requirements(
  records: dict[str, RequirementRecord],
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

    extracted = list(
      _records_from_content(
        item.id,
        frontmatter,
        body,
        item.path,
        repo_root,
      ),
    )
    for record in extracted:
      _upsert_record(
        records,
        record,
        seen,
        stats,
        source_kind=item.kind,
        source_type="backlog",
      )


def _iter_spec_files(spec_dirs: Iterable[Path]) -> Iterator[Path]:
  """Yield spec markdown files from spec directories."""
  for directory in spec_dirs:
    if not directory.exists():
      continue
    for subdir in directory.iterdir():
      if not subdir.is_dir():
        continue
      for file in subdir.glob("*.md"):
        if file.name.startswith("SPEC-") or file.name.startswith("PROD-"):
          yield file


def _iter_change_files(dirs: Iterable[Path], prefix: str) -> Iterator[Path]:
  """Yield change artifact markdown files matching a prefix."""
  for directory in dirs:
    if not directory.exists():
      continue
    for bundle in directory.iterdir():
      if not bundle.is_dir():
        continue
      for file in bundle.glob("*.md"):
        if file.name.startswith(prefix):
          yield file


def _apply_delta_relations(
  records: dict[str, RequirementRecord],
  delta_dirs: Iterable[Path],
  _repo_root: Path,
  *,
  validator: DeltaRelationshipsValidator,
) -> None:
  """Apply delta relationship blocks to requirement records."""
  for file in _iter_change_files(delta_dirs, prefix="DE-"):
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
        record = records.get(target)
        if not record:
          continue
        if delta_id not in record.implemented_by:
          record.implemented_by.append(delta_id)
          record.implemented_by.sort()

    for relation in list_relations(file):
      if relation.type.lower() != "implements":
        continue
      target = relation.target.strip()
      record = records.get(target)
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
        record = records.get(req)
        if not record:
          continue
        if delta_id not in record.implemented_by:
          record.implemented_by.append(delta_id)
          record.implemented_by.sort()


def _apply_revision_relations(
  records: dict[str, RequirementRecord],
  revision_dirs: Iterable[Path],
) -> None:
  """Apply revision relation entries to requirement records."""
  for file in _iter_change_files(revision_dirs, prefix="RE-"):
    frontmatter, _ = load_markdown_file(file)
    revision_id = str(frontmatter.get("id", "")).strip() or file.stem
    if not revision_id:
      continue
    for relation in list_relations(file):
      target = relation.target.strip()
      record = records.get(target)
      if not record:
        continue
      rel_type = relation.type.lower()
      if rel_type in {"introduces", "moves", "reparented"} and not record.introduced:
        record.introduced = revision_id


def _apply_revision_blocks(
  records: dict[str, RequirementRecord],
  revision_dirs: Iterable[Path],
  *,
  spec_registry: SpecRegistry | None,
  stats: SyncStats,
) -> None:
  """Apply structured revision blocks to requirement records."""
  validator = RevisionBlockValidator()
  for file in _iter_change_files(revision_dirs, prefix="RE-"):
    blocks = load_revision_blocks(file)
    for block in blocks:
      try:
        data = block.parse()
      except ValueError:
        continue
      if validator.validate(data):
        continue
      for requirement in data.get("requirements", []) or []:
        created, updated = _apply_revision_requirement(
          records,
          requirement,
          spec_registry=spec_registry,
        )
        stats.created += created
        stats.updated += updated


def _apply_audit_relations(
  records: dict[str, RequirementRecord],
  audit_dirs: Iterable[Path],
) -> None:
  """Apply audit relation entries to requirement records."""
  for file in _iter_change_files(audit_dirs, prefix="AUD-"):
    frontmatter, _ = load_markdown_file(file)
    audit_id = str(frontmatter.get("id", "")).strip() or file.stem
    if not audit_id:
      continue
    for relation in list_relations(file):
      if relation.type.lower() != "verifies":
        continue
      target = relation.target.strip()
      record = records.get(target)
      if not record:
        continue
      if audit_id not in record.verified_by:
        record.verified_by.append(audit_id)
        record.verified_by.sort()


def _apply_spec_relationships(
  records: dict[str, RequirementRecord],
  spec_id: str,
  body: str,
  *,
  validator: Any,
) -> None:
  """Apply spec relationship blocks to requirement records."""
  from supekku.scripts.lib.blocks.relationships import (  # noqa: PLC0415
    extract_relationships,
  )

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
    record = records.get(req_id)
    if not record:
      continue
    if spec_id not in record.specs:
      record.specs.append(spec_id)
      record.specs.sort()

  for req_id in list(collaborators):
    record = records.get(req_id)
    if not record:
      continue
    if spec_id not in record.specs:
      record.specs.append(spec_id)
      record.specs.sort()


def _apply_revision_requirement(
  records: dict[str, RequirementRecord],
  payload: Mapping[str, Any],
  *,
  spec_registry: SpecRegistry | None,
) -> tuple[int, int]:
  """Apply a single revision requirement entry to records."""
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

  record = records.get(target_uid)
  if record is None:
    record = _find_record_from_origin(records, payload)
    if record is not None and record.uid != target_uid:
      records.pop(record.uid, None)
      record.uid = target_uid
      record.label = target_uid.split(".", 1)[-1]
      records[target_uid] = record
    elif record is None:
      record = _create_placeholder_record(
        records,
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

  path = _resolve_spec_path(target_spec, spec_registry)
  if path and path != record.path:
    record.path = path
    changed = True

  if changed and created == 0:
    updated += 1

  return created, updated


def _find_record_from_origin(
  records: dict[str, RequirementRecord],
  payload: Mapping[str, Any],
) -> RequirementRecord | None:
  """Find a record from revision origin references."""
  origins = payload.get("origin")
  if not isinstance(origins, Iterable) or isinstance(origins, (str, bytes)):
    return None
  for origin in origins:
    if not isinstance(origin, Mapping):
      continue
    if origin.get("kind") != "requirement":
      continue
    ref = str(origin.get("ref", "")).strip()
    if ref and ref in records:
      return records[ref]
  return None


def _create_placeholder_record(
  records: dict[str, RequirementRecord],
  uid: str,
  spec_id: str,
  payload: Mapping[str, Any],
  *,
  spec_registry: SpecRegistry | None,
  lifecycle: Mapping[str, Any],
) -> RequirementRecord:
  """Create a placeholder requirement record from revision data."""
  from .lifecycle import STATUS_PENDING as _STATUS_PENDING  # noqa: PLC0415

  label = uid.split(".", 1)[-1] if "." in uid else uid
  path = _resolve_spec_path(spec_id, spec_registry)
  kind = str(payload.get("kind", "functional") or "functional")
  status = str(lifecycle.get("status", _STATUS_PENDING) or _STATUS_PENDING)
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
    introduced=str(introduced) if isinstance(introduced, str) and introduced else None,
    implemented_by=implemented_by,
    verified_by=verified_by,
    path=path,
  )
  records[uid] = record
  return record


def _resolve_spec_path(
  spec_id: str,
  spec_registry: SpecRegistry | None,
) -> str:
  """Resolve a spec ID to its relative file path."""
  if not spec_registry:
    return ""
  spec = spec_registry.get(spec_id)
  if not spec:
    return ""
  try:
    return spec.path.relative_to(spec_registry.root).as_posix()
  except ValueError:
    return spec.path.as_posix()
