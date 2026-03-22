"""Requirement coverage tracking and drift detection."""

from __future__ import annotations

import sys
from collections import defaultdict
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from supekku.scripts.lib.blocks.verification import (
  VALID_COVERAGE_STATUSES,
  load_coverage_blocks,
)

from .lifecycle import (
  STATUS_ACTIVE,
  STATUS_IN_PROGRESS,
  STATUS_PENDING,
  TERMINAL_STATUSES,
  RequirementStatus,
)
from .models import RequirementRecord

if TYPE_CHECKING:
  from pathlib import Path


def _check_coverage_drift(
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

  statuses_by_source = {source: set(statuses) for source, statuses in by_source.items()}

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
  records: dict[str, RequirementRecord],
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
  for record in records.values():
    record.coverage_evidence = []
    record.coverage_entries = []

  coverage_map: dict[str, list[dict[str, Any]]] = defaultdict(list)

  for files in (spec_files, delta_files, plan_files, audit_files):
    _extract_coverage_entries(files, coverage_map)

  # Rebuild from current sources
  for req_id, entries in coverage_map.items():
    record = records.get(req_id)
    if not record:
      continue

    # Check for drift before updating
    _check_coverage_drift(req_id, entries)

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
    computed_status = _compute_status_from_coverage(entries)
    if computed_status is not None:
      record.status = computed_status
