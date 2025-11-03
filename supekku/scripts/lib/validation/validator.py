"""Validation utilities for workspace and artifact consistency."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

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
      requirement_ids,
      expected_type="implements",
    )
    self._validate_change_relations(
      revision_registry.values(),
      requirement_ids,
      expected_type="introduces",
    )
    self._validate_change_relations(
      audit_registry.values(),
      requirement_ids,
      expected_type="verifies",
    )

    # Decision (ADR) validation
    self._validate_decision_references(decisions, decision_ids)
    self._validate_decision_status_compatibility(decisions)

    return list(self.issues)

  # --------------------------------------------------------------
  def _validate_change_relations(
    self,
    artifacts: Iterable[ChangeArtifact],
    requirement_ids: set[str],
    *,
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
          if req not in requirement_ids:
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


def validate_workspace(
  workspace: Workspace,
  strict: bool = False,
) -> list[ValidationIssue]:
  """Validate the given workspace and return a list of validation issues."""
  validator = WorkspaceValidator(workspace, strict=strict)
  return validator.validate()


__all__ = ["ValidationIssue", "WorkspaceValidator", "validate_workspace"]
