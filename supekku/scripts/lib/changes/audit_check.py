"""Audit completeness checking for delta completion enforcement.

Follows the coverage_check.py pattern: a self-contained module that resolves
audit gates, collects gating findings from conformance audits, derives
closure effects, and reports audit completeness for qualifying deltas.

Design authority: DR-079 (DEC-079-003, -005, -006, -008, -011).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from supekku.scripts.lib.core.frontmatter_metadata.audit import (
  AUDIT_MODE_CONFORMANCE,
  DISPOSITION_KIND_FOLLOW_UP_BACKLOG,
  DISPOSITION_KIND_FOLLOW_UP_DELTA,
  DISPOSITION_KIND_TOLERATED_DRIFT,
  DISPOSITION_STATUS_PENDING,
  DISPOSITION_STATUS_RECONCILED,
)
from supekku.scripts.lib.core.frontmatter_metadata.delta import (
  AUDIT_GATE_AUTO,
  AUDIT_GATE_EXEMPT,
  AUDIT_GATE_REQUIRED,
)
from supekku.scripts.lib.core.spec_utils import load_markdown_file

if TYPE_CHECKING:
  from pathlib import Path

  from supekku.scripts.lib.workspace import Workspace


# -- Gate resolution constants --

GATE_REQUIRED = "required"
GATE_NON_GATING = "non-gating"
GATE_EXEMPT = "exempt"

# -- Closure effect constants --

EFFECT_BLOCK = "block"
EFFECT_WARN = "warn"
EFFECT_NONE = "none"

_EFFECT_SEVERITY = {EFFECT_BLOCK: 2, EFFECT_WARN: 1, EFFECT_NONE: 0}


# -- Data classes --


@dataclass(frozen=True)
class GatingFinding:
  """A finding extracted from an audit for gate evaluation."""

  audit_id: str
  finding_id: str
  description: str
  outcome: str
  disposition_status: str | None
  disposition_kind: str | None
  closure_override_effect: str | None
  refs: list[dict[str, str]] = field(default_factory=list)
  closure_effect: str = EFFECT_NONE


@dataclass(frozen=True)
class AuditCheckResult:
  """Result of audit completeness check for a delta."""

  is_complete: bool
  gate_resolution: str
  audits_found: int
  blocking_findings: list[GatingFinding] = field(default_factory=list)
  warning_findings: list[GatingFinding] = field(default_factory=list)
  collisions: list[str] = field(default_factory=list)


# -- Pure functions --


def resolve_audit_gate(
  audit_gate: str | None,
  requirement_ids: list[str],
) -> str:
  """Resolve audit_gate field to an effective gate value.

  DEC-079-003: auto resolves from applies_to.requirements; required and
  exempt pass through.

  Args:
    audit_gate: Raw audit_gate value from delta frontmatter (default: auto).
    requirement_ids: The delta's applies_to.requirements list.

  Returns:
    One of GATE_REQUIRED, GATE_NON_GATING, or GATE_EXEMPT.
  """
  gate = audit_gate or AUDIT_GATE_AUTO

  if gate == AUDIT_GATE_REQUIRED:
    return GATE_REQUIRED
  if gate == AUDIT_GATE_EXEMPT:
    return GATE_EXEMPT
  # auto: resolve based on requirements
  if requirement_ids:
    return GATE_REQUIRED
  return GATE_NON_GATING


def derive_closure_effect(  # noqa: PLR0913
  mode: str,
  outcome: str,  # pylint: disable=unused-argument
  disposition_status: str | None,
  disposition_kind: str | None,
  closure_override_effect: str | None = None,
  refs: list[dict[str, str]] | None = None,
) -> str:
  """Derive the closure effect for a single finding.

  DEC-079-005: closure_effect is derived, never stored.
  DEC-079-006: conformance + tolerated_drift defaults to block.

  Args:
    mode: Audit mode (conformance or discovery).
    outcome: Finding outcome — present in API for caller context
      but not used in derivation (outcome×kind validity is a
      separate schema concern).
    disposition_status: Disposition status (reconciled, accepted, pending), or None.
    disposition_kind: Disposition kind, or None.
    closure_override_effect: Optional relaxation from closure_override.effect.
    refs: Disposition refs for validating owned artefacts.

  Returns:
    One of EFFECT_BLOCK, EFFECT_WARN, or EFFECT_NONE.
  """
  # No disposition at all → treat as pending
  if disposition_status is None:
    return EFFECT_BLOCK if mode == AUDIT_MODE_CONFORMANCE else EFFECT_WARN

  derived = _derive_raw_effect(mode, disposition_status, disposition_kind, refs)
  return _apply_override(derived, closure_override_effect)


def _derive_raw_effect(
  mode: str,
  status: str,
  kind: str | None,
  refs: list[dict[str, str]] | None,
) -> str:
  """Derive raw closure effect before override application."""
  if mode == AUDIT_MODE_CONFORMANCE:
    if status == DISPOSITION_STATUS_PENDING:
      return EFFECT_BLOCK
    if status == DISPOSITION_STATUS_RECONCILED:
      return EFFECT_NONE
    # status == accepted
    if kind == DISPOSITION_KIND_TOLERATED_DRIFT:
      return EFFECT_BLOCK  # DEC-079-006
    if kind in (DISPOSITION_KIND_FOLLOW_UP_DELTA, DISPOSITION_KIND_FOLLOW_UP_BACKLOG):
      if refs and _has_owned_ref(refs):
        return EFFECT_WARN
      return EFFECT_BLOCK
    # Fallback for accepted with other kinds
    return EFFECT_WARN

  # discovery mode
  if status == DISPOSITION_STATUS_PENDING:
    return EFFECT_WARN
  return EFFECT_NONE


def _has_owned_ref(refs: list[dict[str, str]]) -> bool:
  """Check whether refs contain at least one valid owned artefact reference."""
  return any(ref.get("kind") and ref.get("ref") for ref in refs)


def _apply_override(derived: str, override_effect: str | None) -> str:
  """Apply closure_override relaxation (can only relax, never escalate)."""
  if not override_effect:
    return derived
  # Override can only relax: block→warn, block→none, warn→none
  if _EFFECT_SEVERITY.get(override_effect, 0) < _EFFECT_SEVERITY.get(derived, 0):
    return override_effect
  return derived


# -- Finding collection --


def _load_audit_frontmatter(audit_path: Path) -> dict[str, Any]:
  """Load raw frontmatter from an audit file."""
  frontmatter, _ = load_markdown_file(audit_path)
  return frontmatter


# pylint: disable=too-many-locals
# Rationale: finding extraction loop has inherent structural breadth
def collect_gating_findings(
  delta_id: str,
  workspace: Workspace,
) -> tuple[list[GatingFinding], int, list[str]]:
  """Collect findings from qualifying conformance audits for a delta.

  DEC-079-008: multiple audits contribute findings by union.

  Args:
    delta_id: Delta identifier (e.g., "DE-079").
    workspace: Workspace instance for registry access.

  Returns:
    Tuple of (findings, audits_found, collisions).
    - findings: All gating findings with derived closure effects.
    - audits_found: Number of qualifying audits found.
    - collisions: Finding IDs that appear in multiple audits.
  """
  audit_registry = workspace.audit_registry
  all_audits = audit_registry.collect()

  qualifying: list[tuple[str, dict[str, Any]]] = []
  for audit_id, audit in all_audits.items():
    fm = _load_audit_frontmatter(audit.path)
    if (
      fm.get("delta_ref") == delta_id
      and fm.get("mode") == AUDIT_MODE_CONFORMANCE
      and audit.status == "completed"
    ):
      qualifying.append((audit_id, fm))

  if not qualifying:
    return [], 0, []

  findings: list[GatingFinding] = []
  seen_ids: dict[str, str] = {}  # finding_id -> first audit_id
  collisions: list[str] = []

  for audit_id, fm in qualifying:
    mode = fm.get("mode", AUDIT_MODE_CONFORMANCE)
    for raw_finding in fm.get("findings", []):
      finding_id = raw_finding.get("id", "")

      # Track collisions (DEC-079-008)
      if finding_id in seen_ids:
        collisions.append(
          f"{finding_id} appears in both {seen_ids[finding_id]} and {audit_id}"
        )
      else:
        seen_ids[finding_id] = audit_id

      disposition = raw_finding.get("disposition") or {}
      d_status = disposition.get("status")
      d_kind = disposition.get("kind")
      override = disposition.get("closure_override") or {}
      override_effect = override.get("effect")
      refs = disposition.get("refs") or []

      effect = derive_closure_effect(
        mode=mode,
        outcome=raw_finding.get("outcome", ""),
        disposition_status=d_status,
        disposition_kind=d_kind,
        closure_override_effect=override_effect,
        refs=refs,
      )

      findings.append(
        GatingFinding(
          audit_id=audit_id,
          finding_id=finding_id,
          description=raw_finding.get("description", ""),
          outcome=raw_finding.get("outcome", ""),
          disposition_status=d_status,
          disposition_kind=d_kind,
          closure_override_effect=override_effect,
          refs=refs,
          closure_effect=effect,
        )
      )

  return findings, len(qualifying), collisions


# -- Top-level orchestrator --


def check_audit_completeness(
  delta_id: str,
  workspace: Workspace,
) -> AuditCheckResult:
  """Check if a delta's audit obligations are satisfied.

  Args:
    delta_id: Delta identifier (e.g., "DE-079").
    workspace: Workspace instance for registry access.

  Returns:
    AuditCheckResult with gate resolution, findings, and completeness status.
  """
  delta_registry = workspace.delta_registry
  delta_artifacts = delta_registry.collect()

  if delta_id not in delta_artifacts:
    return AuditCheckResult(
      is_complete=False,
      gate_resolution=GATE_NON_GATING,
      audits_found=0,
    )

  delta = delta_artifacts[delta_id]
  delta_fm = _load_audit_frontmatter(delta.path)

  audit_gate = delta_fm.get("audit_gate")
  requirement_ids = delta.applies_to.get("requirements", [])
  gate = resolve_audit_gate(audit_gate, requirement_ids)

  # Non-gating or exempt → pass
  if gate in (GATE_NON_GATING, GATE_EXEMPT):
    return AuditCheckResult(
      is_complete=True,
      gate_resolution=gate,
      audits_found=0,
    )

  # Gate is required — collect and evaluate findings
  findings, audits_found, collisions = collect_gating_findings(delta_id, workspace)

  if audits_found == 0:
    return AuditCheckResult(
      is_complete=False,
      gate_resolution=gate,
      audits_found=0,
      collisions=collisions,
    )

  blocking = [f for f in findings if f.closure_effect == EFFECT_BLOCK]
  warnings = [f for f in findings if f.closure_effect == EFFECT_WARN]

  return AuditCheckResult(
    is_complete=len(blocking) == 0,
    gate_resolution=gate,
    audits_found=audits_found,
    blocking_findings=blocking,
    warning_findings=warnings,
    collisions=collisions,
  )


# -- Formatting --


def format_audit_error(
  delta_id: str,
  result: AuditCheckResult,
) -> str:
  """Format error message for audit completeness failure.

  Args:
    delta_id: Delta identifier.
    result: AuditCheckResult with blocking findings.

  Returns:
    Formatted error message.
  """
  lines = [
    f"ERROR: Cannot complete {delta_id} — audit reconciliation required",
    "",
  ]

  if result.audits_found == 0:
    lines.append("No completed conformance audit found for this delta.")
    lines.append(
      "Create one with: uv run spec-driver create audit"
      f" '<title>' --delta {delta_id} --mode conformance"
    )
    lines.append("")
  else:
    n_block = len(result.blocking_findings)
    lines.append(
      f"Found {result.audits_found} conformance audit(s),"
      f" but {n_block} finding(s) block closure:"
    )
    lines.append("")
    for finding in result.blocking_findings:
      s = finding.disposition_status or "no disposition"
      k = finding.disposition_kind or "—"
      lines.append(f"  {finding.finding_id} ({finding.audit_id})")
      lines.append(f"    outcome: {finding.outcome}, status: {s}, kind: {k}")
      if finding.description:
        lines.append(f"    {finding.description}")
      lines.append("")

  if result.collisions:
    lines.append("Finding ID collisions across audits:")
    for collision in result.collisions:
      lines.append(f"  ⚠ {collision}")
    lines.append("")

  n_warn = len(result.warning_findings)
  if result.warning_findings:
    lines.append(f"{n_warn} finding(s) produce warnings (non-blocking):")
    for finding in result.warning_findings:
      lines.append(f"  {finding.finding_id}: {finding.description}")
    lines.append("")

  lines.extend(
    [
      "To bypass this check (emergency only):",
      f"  uv run spec-driver complete delta {delta_id} --force",
      "",
    ]
  )

  return "\n".join(lines)


def display_audit_error(
  delta_id: str,
  result: AuditCheckResult,
) -> None:
  """Display audit error message to stderr."""
  print(format_audit_error(delta_id, result), file=sys.stderr)


def display_audit_warnings(
  result: AuditCheckResult,
) -> None:
  """Display audit warning findings to stderr (non-blocking)."""
  if not result.warning_findings:
    return
  lines = [f"Audit warnings ({len(result.warning_findings)} finding(s)):"]
  for finding in result.warning_findings:
    lines.append(f"  {finding.finding_id}: {finding.description}")
  if result.collisions:
    lines.append("Finding ID collisions:")
    for collision in result.collisions:
      lines.append(f"  ⚠ {collision}")
  print("\n".join(lines), file=sys.stderr)


__all__ = [
  "AuditCheckResult",
  "GatingFinding",
  "check_audit_completeness",
  "collect_gating_findings",
  "derive_closure_effect",
  "display_audit_error",
  "display_audit_warnings",
  "format_audit_error",
  "resolve_audit_gate",
]
