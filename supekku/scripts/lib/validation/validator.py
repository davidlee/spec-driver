"""Validation utilities for workspace and artifact consistency."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from supekku.scripts.lib.backlog.registry import discover_backlog_items
from supekku.scripts.lib.changes.audit_check import resolve_audit_gate
from supekku.scripts.lib.core.frontmatter_metadata.audit import (
  AUDIT_MODE_CONFORMANCE,
  VALID_OUTCOME_KINDS,
  VALID_STATUS_KIND_PAIRS,
)
from supekku.scripts.lib.core.spec_utils import load_markdown_file

if TYPE_CHECKING:
  from collections.abc import Iterable

  from .changes.artifacts import ChangeArtifact
  from .workspace import Workspace


@dataclass(frozen=True)
class ValidationIssue:
  """Represents a validation issue with severity level and context."""

  level: str  # "error", "warning", or "info"
  message: str
  artifact: str


class WorkspaceValidator:
  """Validates workspace consistency and artifact relationships."""

  def __init__(self, workspace: Workspace, strict: bool = False) -> None:
    self.workspace = workspace
    self.issues: list[ValidationIssue] = []
    self.strict = strict

  def validate(self) -> list[ValidationIssue]:
    """Validate workspace for missing references and inconsistencies."""
    self.issues.clear()
    _ = self.workspace.specs  # Access but don't assign
    requirements = self.workspace.requirements
    decisions = self.workspace.decisions.collect()
    delta_registry = self.workspace.delta_registry.collect()
    revision_registry = self.workspace.revision_registry.collect()
    audit_registry = self.workspace.audit_registry.collect()

    requirement_ids = set(requirements.records.keys())
    decision_ids = set(decisions.keys())
    delta_ids = set(delta_registry.keys())
    revision_ids = set(revision_registry.keys())
    audit_ids = set(audit_registry.keys())

    # Backlog items (ISSUE-*, IMPR-*, etc.) are valid relation targets
    backlog_ids = {item.id for item in discover_backlog_items(root=self.workspace.root)}
    applies_to_ids = requirement_ids | backlog_ids

    # Requirement lifecycle links
    for req_id, record in requirements.records.items():
      for delta_id in record.implemented_by:
        if delta_id not in delta_ids:
          self._error(
            req_id,
            f"Requirement references missing delta {delta_id}",
          )
      if record.introduced and record.introduced not in revision_ids:
        self._error(
          req_id,
          f"Requirement introduced_by references missing revision {record.introduced}",
        )
      for audit_id in record.verified_by:
        if audit_id not in audit_ids:
          self._error(
            req_id,
            f"Requirement references missing audit {audit_id}",
          )

      # Validation check: coverage evidence without proper status
      valid_statuses = ("baseline", "active", "verified")
      if record.coverage_evidence and record.status not in valid_statuses:
        artifacts = ", ".join(record.coverage_evidence)
        # Pending + coverage means all artifacts are "planned" - this is expected
        if record.status == "pending":
          self._info(
            req_id,
            f"Has planned verification artifacts ({artifacts}). "
            f"Requirement will move to active when artifacts are verified.",
          )
        else:
          # Other statuses (e.g., in-progress) with coverage may indicate issues
          self._warning(
            req_id,
            f"Has coverage evidence ({artifacts}) but status is '{record.status}'. "
            f"Expected: baseline/active/verified. "
            f"Update requirement status to reflect coverage or remove stale artifacts.",
          )

      # Validation warning: missing audit verification
      # (placeholder for grace period logic)
      # TODO: Implement grace period check based on introduced date
      # if not record.verified_by and record.introduced:
      #   # Check if >30 days since introduced
      #   pass

    # Change artifact relation checks
    self._validate_change_relations(
      delta_registry.values(),
      requirement_ids | backlog_ids,
      applies_to_ids=applies_to_ids,
      expected_type="implements",
    )
    self._validate_change_relations(
      revision_registry.values(),
      requirement_ids,
      applies_to_ids=applies_to_ids,
      expected_type="introduces",
    )
    self._validate_change_relations(
      audit_registry.values(),
      requirement_ids,
      applies_to_ids=applies_to_ids,
      expected_type="verifies",
    )

    # Decision (ADR) validation
    self._validate_decision_references(decisions, decision_ids)
    self._validate_decision_status_compatibility(decisions)

    # Spec taxonomy validation (warn-only)
    self._validate_spec_taxonomy()

    # Audit disposition and gate coverage (DE-079 phase 3)
    self._validate_audit_disposition(audit_registry)
    self._validate_audit_gate_coverage(delta_registry)

    # Cross-artifact unresolved reference check (DE-097)
    self._validate_unresolved_references()

    return list(self.issues)

  # --------------------------------------------------------------
  def _validate_change_relations(
    self,
    artifacts: Iterable[ChangeArtifact],
    requirement_ids: set[str],
    *,
    applies_to_ids: set[str],
    expected_type: str,
  ) -> None:
    exp = expected_type.lower()
    for artifact in artifacts:
      for relation in artifact.relations:
        rel_type = str(relation.get("type", "")).lower()
        target = str(relation.get("target", ""))
        if rel_type != exp:
          continue
        if target not in requirement_ids:
          self._error(
            artifact.id,
            f"Relation {rel_type} -> {target} does not match any known requirement",
          )
      applies = artifact.applies_to.get("requirements", [])
      if applies:
        for req in applies:
          if req not in applies_to_ids:
            self._error(
              artifact.id,
              f"applies_to requirement {req} not found",
            )

  def _error(self, artifact: str, message: str) -> None:
    self.issues.append(
      ValidationIssue(level="error", artifact=artifact, message=message),
    )

  def _warning(self, artifact: str, message: str) -> None:
    self.issues.append(
      ValidationIssue(level="warning", artifact=artifact, message=message),
    )

  def _info(self, artifact: str, message: str) -> None:
    self.issues.append(
      ValidationIssue(level="info", artifact=artifact, message=message),
    )

  def _validate_decision_references(
    self,
    decisions: dict,
    decision_ids: set[str],
  ) -> None:
    """Validate that all related_decisions references point to existing ADRs."""
    for decision_id, decision in decisions.items():
      # Check related_decisions references
      for related_id in decision.related_decisions:
        if related_id not in decision_ids:
          self._error(
            decision_id,
            f"Related decision {related_id} does not exist",
          )

  def _validate_decision_status_compatibility(self, decisions: dict) -> None:
    """Warn if active ADR references deprecated or superseded ADRs.

    Only applies in strict mode.
    """
    if not self.strict:
      return

    for decision_id, decision in decisions.items():
      # Skip if the referencing decision itself is deprecated/superseded
      if decision.status in ["deprecated", "superseded"]:
        continue

      for related_id in decision.related_decisions:
        related_decision = decisions.get(related_id)
        if related_decision and related_decision.status in [
          "deprecated",
          "superseded",
        ]:
          self._warning(
            decision_id,
            f"References {related_decision.status} decision {related_id}",
          )

  def _validate_audit_disposition(
    self,
    audit_registry: dict[str, ChangeArtifact],
  ) -> None:
    """Validate finding dispositions in completed audits.

    For each completed audit, checks every finding for:
    - Missing disposition → warning
    - Invalid status×kind pair → error
    - Invalid outcome×kind pair → error
    - closure_override without rationale → error
    """
    for audit_id, audit in audit_registry.items():
      if audit.status != "completed":
        continue

      fm, _ = load_markdown_file(audit.path)
      for finding in fm.get("findings", []):
        finding_id = finding.get("id", "?")
        label = f"{audit_id}/{finding_id}"

        disposition = finding.get("disposition")
        if not disposition:
          self._warning(label, "Finding has no disposition")
          continue

        if not isinstance(disposition, dict):
          self._error(
            label,
            f"Disposition must be a mapping with 'status' and 'kind' keys,"
            f" got {type(disposition).__name__}: {disposition!r}",
          )
          continue

        status = disposition.get("status")
        kind = disposition.get("kind")
        outcome = finding.get("outcome")

        # Validate status×kind
        if kind and status:
          valid_statuses = VALID_STATUS_KIND_PAIRS.get(kind)
          if valid_statuses is not None and status not in valid_statuses:
            self._error(
              label,
              f"Invalid status×kind: status '{status}' is not valid"
              f" for kind '{kind}'"
              f" (valid: {', '.join(sorted(valid_statuses))})",
            )

        # Validate outcome×kind
        if outcome and kind:
          valid_kinds = VALID_OUTCOME_KINDS.get(outcome)
          if valid_kinds is not None and kind not in valid_kinds:
            self._error(
              label,
              f"Invalid outcome×kind: kind '{kind}' is not valid"
              f" for outcome '{outcome}'"
              f" (valid: {', '.join(sorted(valid_kinds))})",
            )

        # Validate closure_override has rationale
        override = disposition.get("closure_override")
        if override and not override.get("rationale"):
          self._error(label, "closure_override is missing rationale")

  def _validate_audit_gate_coverage(
    self,
    delta_registry: dict[str, ChangeArtifact],
  ) -> None:
    """Validate audit gate coverage for qualifying deltas.

    For each delta, resolves audit_gate. If required and no completed
    conformance audit exists → warning. If multiple audits have
    colliding finding IDs → warning.
    """
    audit_by_delta = self._build_conformance_audit_index()

    for delta_id, delta in delta_registry.items():
      fm, _ = load_markdown_file(delta.path)
      gate = resolve_audit_gate(
        fm.get("audit_gate"),
        delta.applies_to.get("requirements", []),
      )
      if gate != "required":
        continue

      matching = audit_by_delta.get(delta_id, [])
      if not matching:
        self._warning(
          delta_id,
          "Audit gate is required but no completed conformance audit found",
        )
      elif len(matching) > 1:
        self._check_finding_id_collisions(delta_id, matching)

  def _build_conformance_audit_index(
    self,
  ) -> dict[str, list[tuple[str, dict]]]:
    """Index completed conformance audits by delta_ref."""
    result: dict[str, list[tuple[str, dict]]] = {}
    for audit_id, audit in self.workspace.audit_registry.collect().items():
      if audit.status != "completed":
        continue
      fm, _ = load_markdown_file(audit.path)
      if fm.get("mode") != AUDIT_MODE_CONFORMANCE:
        continue
      delta_ref = fm.get("delta_ref")
      if delta_ref:
        result.setdefault(delta_ref, []).append((audit_id, fm))
    return result

  def _check_finding_id_collisions(
    self,
    delta_id: str,
    audits: list[tuple[str, dict]],
  ) -> None:
    """Warn if finding IDs collide across multi-audit union."""
    seen: dict[str, str] = {}
    for audit_id, fm in audits:
      for finding in fm.get("findings", []):
        fid = finding.get("id", "")
        if fid in seen:
          self._warning(
            delta_id,
            f"Finding ID '{fid}' collides across audits {seen[fid]} and {audit_id}",
          )
        else:
          seen[fid] = audit_id

  def _validate_spec_taxonomy(self) -> None:
    """Warn when tech specs are missing taxonomy or have inconsistent values.

    Scoped to tech specs (SPEC-*) only. PROD specs are excluded.
    Emits warnings only — never errors.
    """
    for spec in self.workspace.specs.all_specs():
      if spec.kind != "spec":
        continue

      if not spec.category:
        self._warning(
          spec.id,
          "Tech spec is missing 'category' (expected: unit or assembly).",
        )
      if not spec.c4_level:
        self._warning(
          spec.id,
          "Tech spec is missing 'c4_level' (expected: code, component, etc.).",
        )

      if spec.category == "unit" and spec.c4_level and spec.c4_level != "code":
        self._warning(
          spec.id,
          f"Inconsistent taxonomy: category 'unit' typically implies "
          f"c4_level 'code', but found '{spec.c4_level}'.",
        )

  def _validate_unresolved_references(self) -> None:
    """Validate that frontmatter references resolve to known artifacts.

    Uses ``build_reference_graph`` to get the full edge set, then checks
    each edge target against the node index. Non-canonical forms that
    resolve via normalization produce warnings. Targets that don't
    resolve at all produce warnings (or errors in strict mode).

    Design reference: DR-097 §4.4.
    """
    from supekku.scripts.lib.relations.graph import (  # noqa: PLC0415  # pylint: disable=import-outside-toplevel
      build_reference_graph,
      find_unresolved_references,
    )

    try:
      graph = build_reference_graph(self.workspace)
    except Exception:  # noqa: BLE001  # pylint: disable=broad-exception-caught
      self._warning(
        "graph",
        "Could not build reference graph for unresolved reference check",
      )
      return

    # Surface normalization diagnostics
    for diag in graph.diagnostics:
      self._warning("normalization", diag)

    # Surface unresolved references
    emit = self._error if self.strict else self._warning
    for edge in find_unresolved_references(graph):
      emit(
        edge.source,
        f"References unresolved artifact '{edge.target}' "
        f"(via {edge.source_slot}.{edge.detail})",
      )


def validate_workspace(
  workspace: Workspace,
  strict: bool = False,
) -> list[ValidationIssue]:
  """Validate the given workspace and return a list of validation issues."""
  validator = WorkspaceValidator(workspace, strict=strict)
  return validator.validate()


__all__ = ["ValidationIssue", "WorkspaceValidator", "validate_workspace"]
