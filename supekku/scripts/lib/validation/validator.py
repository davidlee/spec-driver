"""Validation utilities for workspace and artifact consistency."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

# Compiled patterns for requirement/spec ID shape detection (POL-002).
_BARE_REQUIREMENT_PATTERN = re.compile(r"^(?:FR|NF)-\d{3}$")
_SPEC_ID_PATTERN = re.compile(r"^(?:SPEC|PROD)-\d{3}$")

from supekku.scripts.lib.backlog.models import BacklogItem
from supekku.scripts.lib.backlog.registry import discover_backlog_items
from supekku.scripts.lib.blocks.audit_findings import load_audit_findings
from supekku.scripts.lib.blocks.delta import (
  extract_delta_context_inputs,
  extract_delta_risk_register,
)
from supekku.scripts.lib.blocks.delta_metadata import (
  DELTA_CONTEXT_INPUTS_VALIDATOR,
  DELTA_RISK_REGISTER_VALIDATOR,
)
from supekku.scripts.lib.blocks.metadata.aliases import normalize_field
from supekku.scripts.lib.blocks.relationships import (
  extract_spec_concerns,
  extract_spec_decisions,
  extract_spec_hypotheses,
)
from supekku.scripts.lib.blocks.spec_metadata import (
  SPEC_CONCERNS_VALIDATOR,
  SPEC_DECISIONS_VALIDATOR,
  SPEC_HYPOTHESES_VALIDATOR,
)
from supekku.scripts.lib.blocks.spec_requirements import extract_spec_requirements
from supekku.scripts.lib.blocks.spec_requirements_metadata import (
  SPEC_REQUIREMENTS_VALIDATOR,
)
from supekku.scripts.lib.changes.audit_check import resolve_audit_gate
from supekku.scripts.lib.changes.phase_model import PhaseSheet
from supekku.scripts.lib.core.enums import get_enum_values
from supekku.scripts.lib.core.frontmatter_metadata.audit import (
  AUDIT_MODE_CONFORMANCE,
  FINDING_OUTCOMES,
  VALID_OUTCOME_KINDS,
  VALID_STATUS_KIND_PAIRS,
)
from supekku.scripts.lib.core.frontmatter_writer import update_frontmatter_status
from supekku.scripts.lib.core.paths import (
  get_backlog_dir,
  get_deltas_dir,
  get_drift_dir,
  get_memory_dir,
)
from supekku.scripts.lib.core.spec_utils import load_markdown_file
from supekku.scripts.lib.drift.models import DriftLedger
from supekku.scripts.lib.memory.models import MemoryRecord

if TYPE_CHECKING:
  from collections.abc import Iterable
  from pathlib import Path
  from typing import Any

  from pydantic import BaseModel

  from supekku.scripts.lib.changes.artifacts import ChangeArtifact
  from supekku.scripts.lib.workspace import Workspace


@dataclass(frozen=True)
class ValidationIssue:
  """Represents a validation issue with severity level and context."""

  level: str  # "error", "warning", or "info"
  message: str
  artifact: str


class WorkspaceValidator:
  """Validates workspace consistency and artifact relationships."""

  def __init__(
    self,
    workspace: Workspace,
    strict: bool = False,
    *,
    fix: bool = False,
    accept_tolerated: bool = True,
  ) -> None:
    self.workspace = workspace
    self.issues: list[ValidationIssue] = []
    self.strict = strict
    self.fix = fix
    self.accept_tolerated = accept_tolerated

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
      # §1.6: Revision-created requirements must have introduced_by
      if record.source_type == "revision" and not record.introduced:
        self._warning(
          req_id,
          "Requirement appears to be revision-created (source_type=revision) "
          "but has no introduced_by field. This may cause incorrect pruning. "
          "Check revision blocks.",
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

    # Phase status validation (DE-104)
    self._validate_phase_statuses()

    # Delta block schema validation (DE-138 P04 — DEC-138-14)
    self._validate_delta_blocks(delta_registry)

    # Spec block schema validation (DE-139 P04)
    self._validate_spec_blocks()

    # Spec requirements block validation (DE-140 P03)
    self._validate_spec_requirements_blocks()

    # Kind-aware frontmatter validation (DE-112)
    memory_dir = get_memory_dir(self.workspace.root)
    backlog_dir = get_backlog_dir(self.workspace.root)
    drift_dir = get_drift_dir(self.workspace.root)
    self._validate_kind_frontmatter(
      MemoryRecord,
      "Memory",
      [memory_dir],
      glob="mem.*.md",
    )
    self._validate_kind_frontmatter(
      BacklogItem,
      "Backlog",
      [backlog_dir / d for d in ("issues", "problems", "improvements", "risks")],
    )
    self._validate_kind_frontmatter(
      DriftLedger,
      "Drift",
      [drift_dir],
      glob="DL-*.md",
    )

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
        # §1.5: Specific guidance when implements targets a spec, not a requirement
        if _SPEC_ID_PATTERN.match(target):
          self._warning(
            artifact.id,
            f"Relation '{rel_type} -> {target}' targets a spec, not a requirement. "
            f"'implements' is for requirements (e.g., {target}.FR-001). "
            f"Use 'relates_to' for spec-level relations.",
          )
          continue
        if target not in requirement_ids:
          self._error(
            artifact.id,
            f"Relation {rel_type} -> {target} does not match any known requirement",
          )
      applies = artifact.applies_to.get("requirements", [])
      if applies:
        for req in applies:
          # §1.4: Warn on bare requirement IDs (no spec prefix)
          if _BARE_REQUIREMENT_PATTERN.match(req):
            self._warning(
              artifact.id,
              f"applies_to requirement '{req}' is not fully qualified. "
              f"Use 'SPEC-XXX.{req}' to avoid ambiguity.",
            )
          if req not in applies_to_ids:
            self._error(
              artifact.id,
              f"applies_to requirement {req} not found",
            )

  def _validate_delta_blocks(
    self,
    delta_registry: dict[str, ChangeArtifact],
  ) -> None:
    """Validate per-delta context_inputs and risk_register block schemas.

    Tolerated alias entries become errors when ``self.accept_tolerated`` is
    False (DEC-138-14, F-138-23). Diagnostics are dispatched at the severity
    reported by the underlying ``MetadataValidator`` so warnings stay warnings
    unless ``--strict`` promotes them at the exit-code layer.
    """
    for delta_id, artifact in delta_registry.items():
      try:
        _, body = load_markdown_file(artifact.path)
      except (OSError, ValueError):
        continue

      try:
        ctx_block = extract_delta_context_inputs(body)
      except ValueError as exc:
        self._error(delta_id, f"context_inputs block extraction failed: {exc}")
        ctx_block = None
      if ctx_block is not None:
        for err in DELTA_CONTEXT_INPUTS_VALIDATOR.validate(
          ctx_block.data,
          strict=self.strict,
          accept_tolerated=self.accept_tolerated,
        ):
          self._block_issue(delta_id, "context_inputs", err)

      try:
        risk_block = extract_delta_risk_register(body)
      except ValueError as exc:
        self._error(delta_id, f"risk_register block extraction failed: {exc}")
        risk_block = None
      if risk_block is not None:
        for err in DELTA_RISK_REGISTER_VALIDATOR.validate(
          risk_block.data,
          strict=self.strict,
          accept_tolerated=self.accept_tolerated,
        ):
          self._block_issue(delta_id, "risk_register", err)

  def _validate_spec_blocks(self) -> None:
    """Validate per-spec concerns, hypotheses, and decisions block schemas.

    Mirrors ``_validate_delta_blocks`` for spec-kind artefacts.
    """
    block_defs = (
      ("concerns", extract_spec_concerns, SPEC_CONCERNS_VALIDATOR),
      ("hypotheses", extract_spec_hypotheses, SPEC_HYPOTHESES_VALIDATOR),
      ("decisions", extract_spec_decisions, SPEC_DECISIONS_VALIDATOR),
    )
    for spec in self.workspace.specs.all_specs():
      body = spec.body
      for label, extractor, validator in block_defs:
        try:
          block = extractor(body)
        except ValueError as exc:
          self._error(spec.id, f"{label} block extraction failed: {exc}")
          continue
        if block is not None:
          for err in validator.validate(
            block.data,
            strict=self.strict,
            accept_tolerated=self.accept_tolerated,
          ):
            self._block_issue(spec.id, label, err)

  def _validate_spec_requirements_blocks(self) -> None:
    """Validate per-spec requirements block schemas (DE-140 P03).

    Follows ``_validate_spec_blocks`` pattern: extract → schema validate →
    semantic checks. Adds spec field cross-validation and strict-mode
    trimmed-empty/blank-item rejection per DR-140 §7.
    """
    for spec in self.workspace.specs.all_specs():
      body = spec.body
      try:
        block = extract_spec_requirements(body)
      except ValueError as exc:
        self._error(spec.id, f"spec.requirements block extraction failed: {exc}")
        continue
      if block is None:
        if self.strict:
          self._error(
            spec.id,
            "spec.requirements block missing (strict mode)",
          )
        continue
      for err in SPEC_REQUIREMENTS_VALIDATOR.validate(
        block.data,
        strict=self.strict,
        accept_tolerated=self.accept_tolerated,
      ):
        self._block_issue(spec.id, "spec.requirements", err)
      spec_value = block.data.get("spec", "")
      if spec_value and spec_value != spec.id:
        self._error(
          spec.id,
          f"spec.requirements: spec field '{spec_value}' "
          f"does not match artifact ID '{spec.id}'",
        )
      if self.strict:
        self._check_strict_content_requirements(spec.id, block.data)

  def _check_strict_content_requirements(
    self,
    artifact: str,
    data: dict[str, Any],
  ) -> None:
    """Reject trimmed-empty description and blank acceptance_criteria (VT-140-022)."""
    requirements = data.get("requirements")
    if not isinstance(requirements, list):
      return
    for idx, entry in enumerate(requirements):
      if not isinstance(entry, dict):
        continue
      desc = entry.get("description", "")
      if isinstance(desc, str) and not desc.strip():
        self._error(
          artifact,
          f"spec.requirements: requirements[{idx}].description "
          f"is trimmed-empty (strict mode)",
        )
      criteria = entry.get("acceptance_criteria")
      if isinstance(criteria, list):
        if not criteria:
          self._error(
            artifact,
            f"spec.requirements: requirements[{idx}].acceptance_criteria "
            f"is empty (strict mode)",
          )
        else:
          for ci, item in enumerate(criteria):
            if isinstance(item, str) and not item.strip():
              self._error(
                artifact,
                f"spec.requirements: requirements[{idx}]."
                f"acceptance_criteria[{ci}] is blank (strict mode)",
              )

  def _block_issue(self, artifact: str, block_label: str, err: Any) -> None:
    """Dispatch a block ValidationError into a ValidationIssue at its severity."""
    message = f"{block_label}: {err}"
    if err.severity == "warning":
      self._warning(artifact, message)
    else:
      self._error(artifact, message)

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

    Checks per finding (DR-141 §4):
    - Invalid outcome enum → error (strict) / warn (non-strict)
    - Missing disposition on completed audit → error (strict) / warn
    - Invalid status×kind pair → error
    - Invalid outcome×kind pair → error
    - closure_override without rationale → error (strict) / warn
    - closure_override.effect escalation → error (strict)
    - Undisposed finding on completed audit → error (strict)
    """
    emit_strict = self._error if self.strict else self._warning

    for audit_id, audit in audit_registry.items():
      if audit.status != "completed":
        continue

      fm, body = load_markdown_file(audit.path)
      findings = load_audit_findings(body, fm=fm)
      seen_ids: set[str] = set()

      for finding in findings:
        finding_id = finding.get("id", "?")
        label = f"{audit_id}/{finding_id}"

        # Duplicate finding ID within this audit
        if finding_id in seen_ids:
          emit_strict(label, f"Duplicate finding ID '{finding_id}'")
        seen_ids.add(finding_id)

        # Invalid outcome enum
        outcome = finding.get("outcome", "")
        if outcome and outcome not in FINDING_OUTCOMES:
          emit_strict(
            label,
            f"Invalid outcome '{outcome}'"
            f" (valid: {', '.join(sorted(FINDING_OUTCOMES))})",
          )

        disposition = finding.get("disposition")
        if not disposition:
          emit_strict(label, "Finding has no disposition")
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

        # Undisposed: pending status on completed audit
        if status == "pending":
          emit_strict(label, "Undisposed finding (status: pending)")

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

        # Validate closure_override
        override = disposition.get("closure_override")
        if override:
          if not override.get("rationale"):
            emit_strict(label, "closure_override is missing rationale")
          # Escalation check: effect must not exceed derived gate
          effect = override.get("effect")
          if effect and effect not in ("warn", "none"):
            emit_strict(
              label,
              f"closure_override.effect '{effect}' is not a valid"
              " de-escalation (must be 'warn' or 'none')",
            )

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
  ) -> dict[str, list[tuple[str, dict, str]]]:
    """Index completed conformance audits by delta_ref."""
    result: dict[str, list[tuple[str, dict, str]]] = {}
    for audit_id, audit in self.workspace.audit_registry.collect().items():
      if audit.status != "completed":
        continue
      fm, body = load_markdown_file(audit.path)
      if fm.get("mode") != AUDIT_MODE_CONFORMANCE:
        continue
      delta_ref = fm.get("delta_ref")
      if delta_ref:
        result.setdefault(delta_ref, []).append((audit_id, fm, body))
    return result

  def _check_finding_id_collisions(
    self,
    delta_id: str,
    audits: list[tuple[str, dict, str]],
  ) -> None:
    """Check finding ID collisions across multi-audit union.

    Severity gated on strict (DR-141 §4).
    """
    emit = self._error if self.strict else self._warning
    seen: dict[str, str] = {}
    for audit_id, fm, body in audits:
      findings = load_audit_findings(body, fm=fm)
      for finding in findings:
        fid = finding.get("id", "")
        if fid in seen:
          emit(
            delta_id,
            f"Finding ID '{fid}' collides across audits"
            f" {seen[fid]} and {audit_id}",
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

    # Surface unresolved references.
    # Skip domain_field and backlog_field slots — those have dedicated
    # validators (_validate_decision_references, _validate_change_relations,
    # etc.) that already emit targeted errors.
    emit = self._error if self.strict else self._warning
    covered_slots = frozenset({"domain_field", "backlog_field"})
    for edge in find_unresolved_references(graph):
      if edge.source_slot in covered_slots:
        continue
      # Skip cross-project references (namespace:ID pattern)
      if ":" in edge.target:
        continue
      emit(
        edge.source,
        f"References unresolved artifact '{edge.target}' "
        f"(via {edge.source_slot}.{edge.detail})",
      )

  # -----------------------------------------------------------
  # Phase status validation (DE-104)
  # -----------------------------------------------------------

  def _validate_phase_statuses(self) -> None:
    """Validate phase frontmatter statuses across all delta bundles."""
    deltas_dir = get_deltas_dir(self.workspace.root)
    if not deltas_dir.exists():
      return
    valid = get_enum_values("phase.status")
    if valid is None:
      return  # pragma: no cover — defensive; enum should always exist
    for delta_dir in sorted(deltas_dir.iterdir()):
      if not delta_dir.is_dir():
        continue
      phases_dir = delta_dir / "phases"
      if not phases_dir.is_dir():
        continue
      for phase_file in sorted(phases_dir.glob("phase-[0-9][0-9].md")):
        self._validate_single_phase(phase_file, valid)

  def _validate_single_phase(
    self,
    phase_file: Path,
    valid_statuses: list[str],
  ) -> None:
    """Validate a single phase file's frontmatter and structure."""
    try:
      fm, _ = load_markdown_file(phase_file)
    except Exception:  # noqa: BLE001  # pylint: disable=broad-exception-caught
      self._warning(str(phase_file.name), "Could not parse frontmatter")
      return

    artifact = fm.get("id", phase_file.name)

    # Status check
    status = fm.get("status")
    if status is None:
      self._warning(artifact, "Missing status field in frontmatter")
    elif status not in valid_statuses:
      canonical = normalize_field("phase", "status", status)
      if self.fix and canonical in valid_statuses:
        update_frontmatter_status(phase_file, canonical)
        self._info(artifact, f"Fixed phase status: '{status}' → '{canonical}'")
      else:
        valid = sorted(valid_statuses)
        self._warning(
          artifact,
          f"Non-canonical phase status: '{status}'; valid: {valid}",
        )

    # Kind check
    if fm.get("kind") != "phase":
      self._warning(artifact, "Missing or incorrect kind (expected 'phase')")

    # New-format phases (DR-106): validate canonical frontmatter via Pydantic
    has_canonical_frontmatter = fm.get("plan") and fm.get("delta")
    if has_canonical_frontmatter:
      self._validate_phase_frontmatter(fm, artifact)
    else:
      # Legacy: require overview block
      content = phase_file.read_text(encoding="utf-8")
      if "supekku:phase.overview" not in content:
        self._warning(artifact, "Missing phase.overview block")

  def _validate_phase_frontmatter(
    self,
    fm: dict[str, Any],
    artifact: str,
  ) -> None:
    """Validate canonical phase frontmatter fields via PhaseSheet model."""
    try:
      sheet = PhaseSheet(**fm)
    except Exception:  # noqa: BLE001
      self._warning(artifact, "Phase frontmatter failed Pydantic validation")
      return

    if not sheet.plan:
      self._warning(artifact, "Phase frontmatter missing 'plan' field")
    if not sheet.delta:
      self._warning(artifact, "Phase frontmatter missing 'delta' field")

  # -- Kind-aware frontmatter validation (DE-112) -------------------------

  def _validate_kind_frontmatter(
    self,
    model_cls: type[BaseModel],
    label: str,
    directories: Iterable[Path],
    glob: str = "*.md",
  ) -> None:
    """Validate frontmatter files against a Pydantic model.

    Walks *directories*, globs for *glob*, parses frontmatter, and
    attempts ``model_cls(**fm)``.  Failures emit a warning using *label*
    (e.g. "Memory", "Backlog", "Drift").
    """
    for directory in directories:
      if not directory.is_dir():
        continue
      for md_file in sorted(directory.glob(glob)):
        try:
          fm, _ = load_markdown_file(md_file)
        except Exception:  # noqa: BLE001  # pylint: disable=broad-exception-caught
          self._warning(md_file.name, "Could not parse frontmatter")
          continue
        if fm:
          artifact = fm.get("id", md_file.name)
          try:
            model_cls(**fm)
          except Exception:  # noqa: BLE001
            self._warning(
              artifact,
              f"{label} frontmatter failed Pydantic validation",
            )


def validate_workspace(
  workspace: Workspace,
  strict: bool = False,
  *,
  fix: bool = False,
  accept_tolerated: bool = True,
) -> list[ValidationIssue]:
  """Validate the given workspace and return a list of validation issues."""
  validator = WorkspaceValidator(
    workspace, strict=strict, fix=fix, accept_tolerated=accept_tolerated
  )
  return validator.validate()


def check_requirements_migration_complete(
  workspace: Workspace,
) -> list[str]:
  """Return IDs of specs/prods missing a ``spec.requirements`` block.

  Used as an operational guard (DEC-140-13): the strict flip must not
  proceed while any spec/prod artifact lacks a requirements block.
  """
  unmigrated: list[str] = []
  for spec in workspace.specs.all_specs():
    if spec.id.endswith(".TESTS"):
      continue
    try:
      block = extract_spec_requirements(spec.body)
    except ValueError:
      block = None
    if block is None:
      unmigrated.append(spec.id)
  return unmigrated


__all__ = [
  "ValidationIssue",
  "WorkspaceValidator",
  "check_requirements_migration_complete",
  "validate_workspace",
]
