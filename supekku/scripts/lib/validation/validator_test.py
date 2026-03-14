"""Tests for validator module."""

from __future__ import annotations

import os
import unittest
from typing import TYPE_CHECKING, Any

from supekku.scripts.lib.backlog.registry import sync_backlog_registry
from supekku.scripts.lib.core.paths import (
  AUDITS_SUBDIR,
  BACKLOG_DIR,
  DECISIONS_SUBDIR,
  DELTAS_SUBDIR,
  ISSUES_SUBDIR,
  PRODUCT_SPECS_SUBDIR,
  REVISIONS_SUBDIR,
  SPEC_DRIVER_DIR,
  TECH_SPECS_SUBDIR,
)
from supekku.scripts.lib.core.spec_utils import dump_markdown_file
from supekku.scripts.lib.relations.manager import add_relation
from supekku.scripts.lib.test_base import RepoTestCase
from supekku.scripts.lib.validation.validator import validate_workspace
from supekku.scripts.lib.workspace import Workspace

if TYPE_CHECKING:
  from pathlib import Path


class WorkspaceValidatorTest(RepoTestCase):
  """Test cases for workspace validation functionality."""

  def _create_repo(self) -> Path:
    root = super()._make_repo()
    os.chdir(root)
    return root

  def _write_spec(self, root: Path, spec_id: str, requirement_label: str) -> None:
    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / f"{spec_id}-sample"
    spec_dir.mkdir(parents=True)
    spec_path = spec_dir / f"{spec_id}.md"
    frontmatter = {
      "id": spec_id,
      "slug": "sample",
      "name": "Sample Spec",
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": "spec",
      "category": "assembly",
      "c4_level": "component",
    }
    dump_markdown_file(
      spec_path,
      frontmatter,
      f"# Spec\n- {requirement_label}: Example requirement\n",
    )

  def _write_delta(self, root: Path, delta_id: str, requirement_uid: str) -> Path:
    delta_dir = root / SPEC_DRIVER_DIR / DELTAS_SUBDIR / f"{delta_id}-sample"
    delta_dir.mkdir(parents=True)
    delta_path = delta_dir / f"{delta_id}.md"
    frontmatter = {
      "id": delta_id,
      "slug": delta_id.lower(),
      "name": delta_id,
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": "delta",
      "relations": [],
      "applies_to": {"requirements": [requirement_uid]},
    }
    dump_markdown_file(delta_path, frontmatter, f"# {delta_id}\n")
    return delta_path

  def _write_revision(
    self,
    root: Path,
    revision_id: str,
    requirement_uid: str,
  ) -> Path:
    revision_dir = root / SPEC_DRIVER_DIR / REVISIONS_SUBDIR / f"{revision_id}-sample"
    revision_dir.mkdir(parents=True)
    revision_path = revision_dir / f"{revision_id}.md"
    frontmatter = {
      "id": revision_id,
      "slug": revision_id.lower(),
      "name": revision_id,
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": "revision",
      "relations": [],
    }
    dump_markdown_file(revision_path, frontmatter, f"# {revision_id}\n")
    add_relation(revision_path, relation_type="introduces", target=requirement_uid)
    return revision_path

  def _write_audit(self, root: Path, audit_id: str, requirement_uid: str) -> Path:
    audit_dir = root / SPEC_DRIVER_DIR / AUDITS_SUBDIR / f"{audit_id}-sample"
    audit_dir.mkdir(parents=True)
    audit_path = audit_dir / f"{audit_id}.md"
    frontmatter = {
      "id": audit_id,
      "slug": audit_id.lower(),
      "name": audit_id,
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": "audit",
      "relations": [],
    }
    dump_markdown_file(audit_path, frontmatter, f"# {audit_id}\n")
    add_relation(audit_path, relation_type="verifies", target=requirement_uid)
    return audit_path

  def test_validator_reports_missing_relation_targets(self) -> None:
    """Test validator detects relation targets referencing missing artifacts."""
    root = self._create_repo()
    self._write_spec(root, "SPEC-300", "FR-300")
    delta_path = self._write_delta(root, "DE-300", "SPEC-300.FR-300")
    add_relation(delta_path, relation_type="implements", target="SPEC-300.FR-300")

    ws = Workspace(root)
    ws.sync_requirements()
    issues = validate_workspace(ws)
    # Only audit gate warning expected (delta has requirements but no audit)
    non_gate = [i for i in issues if "Audit gate" not in i.message]
    assert not non_gate

    # Break requirement link
    ws.requirements.records["SPEC-300.FR-300"].implemented_by = ["DE-999"]
    ws.requirements.save()
    issues = validate_workspace(ws)
    errors = [i for i in issues if i.level == "error"]
    assert len(errors) == 1
    assert "DE-999" in errors[0].message

  def test_validator_checks_change_relations(self) -> None:
    """Test validator verifies change relations point to valid requirements."""
    root = self._create_repo()
    requirement_uid = "SPEC-301.FR-301"
    self._write_spec(root, "SPEC-301", "FR-301")
    delta_path = self._write_delta(root, "DE-301", requirement_uid)
    add_relation(delta_path, relation_type="implements", target="SPEC-999.FR-999")

    ws = Workspace(root)
    ws.sync_requirements()
    issues = validate_workspace(ws)
    errors = [i for i in issues if i.level == "error"]
    assert len(errors) == 1
    assert "SPEC-999.FR-999" in errors[0].message

  def _write_adr(
    self,
    root: Path,
    adr_id: str,
    status: str = "accepted",
    related_decisions: list[str] | None = None,
  ) -> Path:
    """Helper to create ADR files for testing."""
    if related_decisions is None:
      related_decisions = []

    decisions_dir = root / SPEC_DRIVER_DIR / DECISIONS_SUBDIR
    decisions_dir.mkdir(parents=True, exist_ok=True)
    adr_path = decisions_dir / f"{adr_id}-test.md"

    frontmatter = {
      "id": adr_id,
      "title": f"Test Decision {adr_id}",
      "status": status,
      "created": "2024-01-01",
    }

    if related_decisions:
      frontmatter["related_decisions"] = related_decisions

    content = (
      f"# {adr_id}: Test Decision\n\n"
      f"## Context\nTest context.\n\n"
      f"## Decision\nTest decision.\n"
    )
    dump_markdown_file(adr_path, frontmatter, content)
    return adr_path

  def test_validator_checks_adr_reference_validation(self) -> None:
    """Test that validator detects broken ADR references."""
    root = self._create_repo()

    # Create ADRs
    self._write_adr(root, "ADR-001", "accepted")
    # ADR-999 doesn't exist
    self._write_adr(
      root,
      "ADR-002",
      "accepted",
      related_decisions=["ADR-001", "ADR-999"],
    )

    ws = Workspace(root)
    issues = validate_workspace(ws)

    # Should find one error for broken reference
    error_issues = [
      issue for issue in issues if issue.level == "error" and "ADR-999" in issue.message
    ]
    assert len(error_issues) == 1
    assert error_issues[0].artifact == "ADR-002"
    assert "does not exist" in error_issues[0].message

  def test_validator_checks_adr_status_compatibility(self) -> None:
    """Test validator warns about deprecated/superseded ADRs in strict."""
    root = self._create_repo()

    # Create ADRs with different statuses
    self._write_adr(root, "ADR-001", "deprecated")
    self._write_adr(root, "ADR-002", "superseded")
    self._write_adr(
      root,
      "ADR-003",
      "accepted",
      related_decisions=["ADR-001", "ADR-002"],
    )

    ws = Workspace(root)

    # Non-strict mode: no warnings
    issues = validate_workspace(ws, strict=False)
    warning_issues = [issue for issue in issues if issue.level == "warning"]
    assert len(warning_issues) == 0

    # Strict mode: warnings expected
    issues = validate_workspace(ws, strict=True)
    warning_issues = [issue for issue in issues if issue.level == "warning"]
    assert len(warning_issues) == 2

    # Check specific warnings
    deprecated_warning = next(
      issue for issue in warning_issues if "deprecated" in issue.message
    )
    superseded_warning = next(
      issue for issue in warning_issues if "superseded" in issue.message
    )

    assert deprecated_warning.artifact == "ADR-003"
    assert "ADR-001" in deprecated_warning.message

    assert superseded_warning.artifact == "ADR-003"
    assert "ADR-002" in superseded_warning.message

  def test_validator_adr_validation_no_issues_when_valid(self) -> None:
    """Test that validator finds no issues with valid ADR references."""
    root = self._create_repo()

    # Create valid ADRs
    self._write_adr(root, "ADR-001", "accepted")
    self._write_adr(root, "ADR-002", "accepted")
    self._write_adr(
      root,
      "ADR-003",
      "accepted",
      related_decisions=["ADR-001", "ADR-002"],
    )

    ws = Workspace(root)
    issues = validate_workspace(ws)

    # Filter to only ADR-related issues
    adr_issues = [
      issue
      for issue in issues
      if "ADR" in issue.message or issue.artifact.startswith("ADR")
    ]
    assert len(adr_issues) == 0

  def test_validator_no_warning_deprecated_referencing_deprecated(
    self,
  ) -> None:
    """Test deprecated ADRs referencing deprecated don't warn."""
    root = self._create_repo()

    # Deprecated/superseded ADRs
    self._write_adr(root, "ADR-001", "deprecated")
    self._write_adr(root, "ADR-002", "superseded")
    self._write_adr(root, "ADR-003", "deprecated")

    # Deprecated referencing deprecated - should NOT warn
    self._write_adr(root, "ADR-004", "deprecated", related_decisions=["ADR-001"])
    # Superseded referencing deprecated - should NOT warn
    self._write_adr(root, "ADR-005", "superseded", related_decisions=["ADR-002"])
    # Deprecated referencing superseded - should NOT warn
    self._write_adr(root, "ADR-006", "deprecated", related_decisions=["ADR-003"])

    # Active referencing deprecated - SHOULD warn in strict mode
    self._write_adr(root, "ADR-007", "accepted", related_decisions=["ADR-001"])

    ws = Workspace(root)

    # Non-strict: no warnings at all
    issues = validate_workspace(ws, strict=False)
    warning_issues = [issue for issue in issues if issue.level == "warning"]
    assert len(warning_issues) == 0

    # Strict mode: only 1 warning (ADR-007 -> ADR-001)
    issues = validate_workspace(ws, strict=True)
    warning_issues = [issue for issue in issues if issue.level == "warning"]
    assert len(warning_issues) == 1
    assert warning_issues[0].artifact == "ADR-007"
    assert "ADR-001" in warning_issues[0].message

  def test_validator_adr_mixed_validation_scenarios(self) -> None:
    """Test validator with mix of valid and invalid ADR scenarios in strict mode."""
    root = self._create_repo()

    # Create ADRs with various scenarios
    self._write_adr(root, "ADR-001", "accepted")
    self._write_adr(root, "ADR-002", "deprecated")
    # Valid reference
    self._write_adr(root, "ADR-003", "accepted", related_decisions=["ADR-001"])
    # Warning: deprecated (strict only)
    self._write_adr(root, "ADR-004", "accepted", related_decisions=["ADR-002"])
    # Error: missing
    self._write_adr(root, "ADR-005", "accepted", related_decisions=["ADR-999"])
    # Mixed: valid, error, warning
    mixed_refs = ["ADR-001", "ADR-888", "ADR-002"]
    self._write_adr(root, "ADR-006", "accepted", related_decisions=mixed_refs)

    ws = Workspace(root)

    # Non-strict mode: only errors, no warnings about deprecated
    issues = validate_workspace(ws, strict=False)
    adr_issues = [
      issue
      for issue in issues
      if "decision" in issue.message.lower() or issue.artifact.startswith("ADR")
    ]
    error_issues = [issue for issue in adr_issues if issue.level == "error"]
    warning_issues = [issue for issue in adr_issues if issue.level == "warning"]

    # Should have 2 errors (ADR-999 and ADR-888 missing)
    assert len(error_issues) == 2
    missing_refs = {issue.message.split()[-4] for issue in error_issues}
    assert missing_refs == {"ADR-999", "ADR-888"}
    # No warnings in non-strict mode
    assert len(warning_issues) == 0

    # Strict mode: errors + warnings
    issues = validate_workspace(ws, strict=True)
    adr_issues = [
      issue
      for issue in issues
      if "decision" in issue.message.lower() or issue.artifact.startswith("ADR")
    ]
    error_issues = [issue for issue in adr_issues if issue.level == "error"]
    warning_issues = [issue for issue in adr_issues if issue.level == "warning"]

    # Should still have 2 errors (ADR-999 and ADR-888 missing)
    assert len(error_issues) == 2
    # Should have 2 warnings (ADR-002 deprecated, referenced by ADR-004 and ADR-006)
    assert len(warning_issues) == 2
    warning_artifacts = {issue.artifact for issue in warning_issues}
    assert warning_artifacts == {"ADR-004", "ADR-006"}

  def test_validator_adr_with_empty_related_decisions(self) -> None:
    """Test that validator handles ADRs with no related_decisions correctly."""
    root = self._create_repo()

    # Create ADRs without related_decisions
    self._write_adr(root, "ADR-001", "accepted")
    self._write_adr(root, "ADR-002", "draft")

    ws = Workspace(root)
    issues = validate_workspace(ws)

    # Should have no ADR-related issues
    adr_issues = [
      issue
      for issue in issues
      if "decision" in issue.message.lower() or issue.artifact.startswith("ADR")
    ]
    assert len(adr_issues) == 0

  def test_validator_warns_coverage_without_baseline_status(self) -> None:
    """Test validator handles coverage evidence based on requirement status (VT-912)."""
    root = self._create_repo()
    self._write_spec(root, "SPEC-400", "FR-400")

    ws = Workspace(root)
    ws.sync_requirements()

    # Manually add coverage_evidence to a pending requirement
    req_uid = "SPEC-400.FR-400"
    record = ws.requirements.records[req_uid]
    assert record.status == "pending"  # Default status

    # Add coverage evidence to pending requirement
    record.coverage_evidence = ["VT-001", "VT-002"]
    ws.requirements.save()

    # Validate - should produce INFO for pending with planned artifacts
    issues = validate_workspace(ws)
    info_msgs = [issue for issue in issues if issue.level == "info"]
    warnings = [issue for issue in issues if issue.level == "warning"]

    assert len(info_msgs) == 1
    assert req_uid in info_msgs[0].artifact
    assert "planned verification" in info_msgs[0].message.lower()
    assert "VT-001" in info_msgs[0].message
    assert len(warnings) == 0  # No warnings for pending + coverage

    # Test in-progress status - should produce warning
    record.status = "in-progress"
    ws.requirements.save()
    issues = validate_workspace(ws)
    warnings = [issue for issue in issues if issue.level == "warning"]

    assert len(warnings) == 1
    assert req_uid in warnings[0].artifact
    assert "coverage evidence" in warnings[0].message.lower()
    assert "in-progress" in warnings[0].message

    # Fix by changing status to baseline - should have no info/warnings
    record.status = "baseline"
    ws.requirements.save()
    issues = validate_workspace(ws)
    info_msgs = [issue for issue in issues if issue.level == "info"]
    warnings = [issue for issue in issues if issue.level == "warning"]
    assert len(info_msgs) == 0
    assert len(warnings) == 0

  # -- Taxonomy validation tests (VT-030-005) --

  def _write_tech_spec(
    self,
    root: Path,
    spec_id: str,
    *,
    category: str = "",
    c4_level: str = "",
  ) -> None:
    """Write a tech spec with optional taxonomy fields."""
    spec_dir = root / SPEC_DRIVER_DIR / TECH_SPECS_SUBDIR / f"{spec_id}-sample"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_path = spec_dir / f"{spec_id}.md"
    frontmatter: dict[str, Any] = {
      "id": spec_id,
      "slug": "sample",
      "name": f"Sample {spec_id}",
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": "spec",
    }
    if category:
      frontmatter["category"] = category
    if c4_level:
      frontmatter["c4_level"] = c4_level
    dump_markdown_file(spec_path, frontmatter, f"# {spec_id}\n")

  def _write_prod_spec(self, root: Path, spec_id: str) -> None:
    """Write a product spec (no taxonomy expected)."""
    spec_dir = root / SPEC_DRIVER_DIR / PRODUCT_SPECS_SUBDIR / spec_id
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_path = spec_dir / f"{spec_id}.md"
    frontmatter = {
      "id": spec_id,
      "slug": "sample",
      "name": f"Sample {spec_id}",
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "draft",
      "kind": "prod",
    }
    dump_markdown_file(spec_path, frontmatter, f"# {spec_id}\n")

  def test_taxonomy_warns_missing_category(self) -> None:
    """Tech spec without category emits a warning."""
    root = self._create_repo()
    self._write_tech_spec(root, "SPEC-500", c4_level="code")
    ws = Workspace(root)
    issues = validate_workspace(ws)
    warnings = [i for i in issues if i.level == "warning" and "category" in i.message]
    assert len(warnings) == 1
    assert warnings[0].artifact == "SPEC-500"

  def test_taxonomy_warns_missing_c4_level(self) -> None:
    """Tech spec without c4_level emits a warning."""
    root = self._create_repo()
    self._write_tech_spec(root, "SPEC-501", category="assembly")
    ws = Workspace(root)
    issues = validate_workspace(ws)
    warnings = [i for i in issues if i.level == "warning" and "c4_level" in i.message]
    assert len(warnings) == 1
    assert warnings[0].artifact == "SPEC-501"

  def test_taxonomy_warns_both_missing(self) -> None:
    """Tech spec missing both category and c4_level emits two warnings."""
    root = self._create_repo()
    self._write_tech_spec(root, "SPEC-502")
    ws = Workspace(root)
    issues = validate_workspace(ws)
    warnings = [i for i in issues if i.level == "warning" and i.artifact == "SPEC-502"]
    assert len(warnings) == 2

  def test_taxonomy_warns_inconsistent_unit_non_code(self) -> None:
    """category: unit with c4_level != code emits a warning."""
    root = self._create_repo()
    self._write_tech_spec(root, "SPEC-503", category="unit", c4_level="component")
    ws = Workspace(root)
    issues = validate_workspace(ws)
    warnings = [
      i for i in issues if i.level == "warning" and "inconsistent" in i.message.lower()
    ]
    assert len(warnings) == 1
    assert warnings[0].artifact == "SPEC-503"

  def test_taxonomy_no_warn_unit_code(self) -> None:
    """category: unit with c4_level: code is consistent — no warning."""
    root = self._create_repo()
    self._write_tech_spec(root, "SPEC-504", category="unit", c4_level="code")
    ws = Workspace(root)
    issues = validate_workspace(ws)
    taxonomy_warnings = [
      i for i in issues if i.level == "warning" and i.artifact == "SPEC-504"
    ]
    assert len(taxonomy_warnings) == 0

  def test_taxonomy_no_warn_assembly_component(self) -> None:
    """category: assembly with c4_level: component is fine — no warning."""
    root = self._create_repo()
    self._write_tech_spec(root, "SPEC-505", category="assembly", c4_level="component")
    ws = Workspace(root)
    issues = validate_workspace(ws)
    taxonomy_warnings = [
      i for i in issues if i.level == "warning" and i.artifact == "SPEC-505"
    ]
    assert len(taxonomy_warnings) == 0

  def test_taxonomy_no_warn_for_prod_spec(self) -> None:
    """PROD spec missing taxonomy must not trigger warnings."""
    root = self._create_repo()
    self._write_prod_spec(root, "PROD-600")
    ws = Workspace(root)
    issues = validate_workspace(ws)
    prod_warnings = [
      i for i in issues if i.level == "warning" and i.artifact == "PROD-600"
    ]
    assert len(prod_warnings) == 0

  def test_taxonomy_never_emits_errors(self) -> None:
    """Taxonomy validation only emits warnings, never errors."""
    root = self._create_repo()
    # Worst case: missing both + inconsistent (if somehow both present)
    self._write_tech_spec(root, "SPEC-506")
    self._write_tech_spec(root, "SPEC-507", category="unit", c4_level="container")
    ws = Workspace(root)
    issues = validate_workspace(ws)
    taxonomy_errors = [
      i for i in issues if i.level == "error" and i.artifact in ("SPEC-506", "SPEC-507")
    ]
    assert len(taxonomy_errors) == 0

  # -- Backlog item acceptance (applies_to.requirements) --

  def _write_backlog_item(self, root: Path, item_id: str) -> None:
    """Create a backlog issue on disk and register it."""
    backlog = root / SPEC_DRIVER_DIR / BACKLOG_DIR
    kind_dir = backlog / ISSUES_SUBDIR / f"{item_id}-sample"
    kind_dir.mkdir(parents=True)
    md_path = kind_dir / f"{item_id}.md"
    frontmatter = {
      "id": item_id,
      "title": f"Sample {item_id}",
      "status": "open",
      "created": "2024-06-01",
    }
    dump_markdown_file(md_path, frontmatter, f"# {item_id}\n")

    sync_backlog_registry(root)

  def test_validator_accepts_backlog_item_in_applies_to(self) -> None:
    """Delta referencing a backlog item in applies_to.requirements is valid."""
    root = self._create_repo()
    self._write_backlog_item(root, "ISSUE-100")
    self._write_delta(root, "DE-100", "ISSUE-100")

    ws = Workspace(root)
    issues = validate_workspace(ws)
    errors = [i for i in issues if i.level == "error"]
    assert len(errors) == 0

  def test_validator_rejects_unknown_applies_to_requirement(self) -> None:
    """Delta referencing a nonexistent ID in applies_to.requirements is an error."""
    root = self._create_repo()
    self._write_delta(root, "DE-101", "ISSUE-999")

    ws = Workspace(root)
    issues = validate_workspace(ws)
    errors = [i for i in issues if i.level == "error"]
    assert len(errors) == 1
    assert "ISSUE-999" in errors[0].message

  # -- Audit disposition validation (DE-079 phase 3) --

  def _write_completed_audit(
    self,
    root: Path,
    audit_id: str,
    *,
    mode: str = "conformance",
    delta_ref: str = "",
    findings: list[dict] | None = None,
  ) -> Path:
    """Write a completed audit with mode, delta_ref, and findings."""
    audit_dir = root / SPEC_DRIVER_DIR / AUDITS_SUBDIR / f"{audit_id}-sample"
    audit_dir.mkdir(parents=True, exist_ok=True)
    audit_path = audit_dir / f"{audit_id}.md"
    frontmatter: dict[str, Any] = {
      "id": audit_id,
      "slug": audit_id.lower(),
      "name": audit_id,
      "created": "2024-06-01",
      "updated": "2024-06-01",
      "status": "completed",
      "kind": "audit",
      "relations": [],
      "mode": mode,
    }
    if delta_ref:
      frontmatter["delta_ref"] = delta_ref
    if findings is not None:
      frontmatter["findings"] = findings
    dump_markdown_file(audit_path, frontmatter, f"# {audit_id}\n")
    return audit_path

  def test_audit_disposition_warns_missing_disposition(self) -> None:
    """Completed audit finding without disposition emits a warning."""
    root = self._create_repo()
    self._write_completed_audit(
      root,
      "AUD-100",
      findings=[{"id": "FIND-001", "description": "Some drift", "outcome": "drift"}],
    )
    ws = Workspace(root)
    issues = validate_workspace(ws)
    warnings = [
      i for i in issues if i.level == "warning" and "no disposition" in i.message
    ]
    assert len(warnings) == 1
    assert warnings[0].artifact == "AUD-100/FIND-001"

  def test_audit_disposition_errors_invalid_status_kind(self) -> None:
    """Invalid status×kind pair emits an error."""
    root = self._create_repo()
    # aligned kind only allows reconciled, not accepted
    self._write_completed_audit(
      root,
      "AUD-101",
      findings=[
        {
          "id": "FIND-001",
          "description": "Aligned",
          "outcome": "aligned",
          "disposition": {"status": "accepted", "kind": "aligned"},
        }
      ],
    )
    ws = Workspace(root)
    issues = validate_workspace(ws)
    errors = [i for i in issues if i.level == "error" and "status×kind" in i.message]
    assert len(errors) == 1
    assert errors[0].artifact == "AUD-101/FIND-001"

  def test_audit_disposition_errors_invalid_outcome_kind(self) -> None:
    """Invalid outcome×kind pair emits an error."""
    root = self._create_repo()
    # drift outcome cannot have aligned kind
    self._write_completed_audit(
      root,
      "AUD-102",
      findings=[
        {
          "id": "FIND-001",
          "description": "Drift dispositioned as aligned",
          "outcome": "drift",
          "disposition": {"status": "reconciled", "kind": "aligned"},
        }
      ],
    )
    ws = Workspace(root)
    issues = validate_workspace(ws)
    errors = [i for i in issues if i.level == "error" and "outcome×kind" in i.message]
    assert len(errors) == 1
    assert errors[0].artifact == "AUD-102/FIND-001"

  def test_audit_disposition_errors_closure_override_no_rationale(self) -> None:
    """closure_override without rationale emits an error."""
    root = self._create_repo()
    self._write_completed_audit(
      root,
      "AUD-103",
      findings=[
        {
          "id": "FIND-001",
          "description": "Override missing rationale",
          "outcome": "drift",
          "disposition": {
            "status": "accepted",
            "kind": "tolerated_drift",
            "closure_override": {"effect": "warn"},
          },
        }
      ],
    )
    ws = Workspace(root)
    issues = validate_workspace(ws)
    errors = [
      i for i in issues if i.level == "error" and "closure_override" in i.message
    ]
    assert len(errors) == 1
    assert errors[0].artifact == "AUD-103/FIND-001"

  def test_audit_disposition_valid_finding_no_issues(self) -> None:
    """Valid disposition produces no audit-related issues."""
    root = self._create_repo()
    self._write_completed_audit(
      root,
      "AUD-104",
      findings=[
        {
          "id": "FIND-001",
          "description": "Aligned finding",
          "outcome": "aligned",
          "disposition": {"status": "reconciled", "kind": "aligned"},
        }
      ],
    )
    ws = Workspace(root)
    issues = validate_workspace(ws)
    audit_issues = [i for i in issues if i.artifact.startswith("AUD-104")]
    assert len(audit_issues) == 0

  def test_audit_disposition_skips_draft_audits(self) -> None:
    """Draft audits are not checked for disposition validity."""
    root = self._create_repo()
    # Write a draft audit with an invalid disposition — should not trigger
    audit_dir = root / SPEC_DRIVER_DIR / AUDITS_SUBDIR / "AUD-105-sample"
    audit_dir.mkdir(parents=True)
    dump_markdown_file(
      audit_dir / "AUD-105.md",
      {
        "id": "AUD-105",
        "slug": "aud-105",
        "name": "AUD-105",
        "created": "2024-06-01",
        "updated": "2024-06-01",
        "status": "draft",
        "kind": "audit",
        "relations": [],
        "findings": [
          {
            "id": "FIND-001",
            "description": "Bad pair",
            "outcome": "drift",
            "disposition": {"status": "accepted", "kind": "aligned"},
          }
        ],
      },
      "# AUD-105\n",
    )
    ws = Workspace(root)
    issues = validate_workspace(ws)
    audit_issues = [i for i in issues if i.artifact.startswith("AUD-105")]
    assert len(audit_issues) == 0

  def test_audit_gate_warns_missing_conformance_audit(self) -> None:
    """Delta with required gate but no conformance audit emits a warning."""
    root = self._create_repo()
    self._write_spec(root, "SPEC-700", "FR-700")
    # Delta with requirement → auto resolves to required
    self._write_delta(root, "DE-700", "SPEC-700.FR-700")
    ws = Workspace(root)
    ws.sync_requirements()
    issues = validate_workspace(ws)
    warnings = [i for i in issues if i.level == "warning" and "Audit gate" in i.message]
    assert len(warnings) == 1
    assert warnings[0].artifact == "DE-700"

  def test_audit_gate_no_warn_when_conformance_audit_exists(self) -> None:
    """Delta with required gate and matching conformance audit is clean."""
    root = self._create_repo()
    self._write_spec(root, "SPEC-701", "FR-701")
    self._write_delta(root, "DE-701", "SPEC-701.FR-701")
    self._write_completed_audit(
      root,
      "AUD-701",
      mode="conformance",
      delta_ref="DE-701",
      findings=[
        {
          "id": "FIND-001",
          "description": "All good",
          "outcome": "aligned",
          "disposition": {"status": "reconciled", "kind": "aligned"},
        }
      ],
    )
    ws = Workspace(root)
    ws.sync_requirements()
    issues = validate_workspace(ws)
    gate_warnings = [i for i in issues if "Audit gate" in i.message]
    assert len(gate_warnings) == 0

  def test_audit_gate_no_warn_for_non_qualifying_delta(self) -> None:
    """Delta without requirements (auto → non-gating) gets no audit warning."""
    root = self._create_repo()
    delta_dir = root / SPEC_DRIVER_DIR / DELTAS_SUBDIR / "DE-702-sample"
    delta_dir.mkdir(parents=True)
    delta_path = delta_dir / "DE-702.md"
    dump_markdown_file(
      delta_path,
      {
        "id": "DE-702",
        "slug": "de-702",
        "name": "DE-702",
        "created": "2024-06-01",
        "updated": "2024-06-01",
        "status": "draft",
        "kind": "delta",
        "relations": [],
        "applies_to": {"requirements": []},
      },
      "# DE-702\n",
    )
    ws = Workspace(root)
    issues = validate_workspace(ws)
    gate_warnings = [i for i in issues if "Audit gate" in i.message]
    assert len(gate_warnings) == 0

  def test_audit_gate_warns_finding_id_collisions(self) -> None:
    """Finding ID collision across multi-audit union emits a warning."""
    root = self._create_repo()
    self._write_spec(root, "SPEC-703", "FR-703")
    self._write_delta(root, "DE-703", "SPEC-703.FR-703")
    # Two audits with same finding ID
    self._write_completed_audit(
      root,
      "AUD-703a",
      mode="conformance",
      delta_ref="DE-703",
      findings=[
        {
          "id": "FIND-001",
          "description": "First audit finding",
          "outcome": "aligned",
          "disposition": {"status": "reconciled", "kind": "aligned"},
        }
      ],
    )
    self._write_completed_audit(
      root,
      "AUD-703b",
      mode="conformance",
      delta_ref="DE-703",
      findings=[
        {
          "id": "FIND-001",
          "description": "Colliding ID in second audit",
          "outcome": "drift",
          "disposition": {"status": "reconciled", "kind": "spec_patch"},
        }
      ],
    )
    ws = Workspace(root)
    ws.sync_requirements()
    issues = validate_workspace(ws)
    collision_warnings = [i for i in issues if "collides" in i.message]
    assert len(collision_warnings) == 1
    assert collision_warnings[0].artifact == "DE-703"
    assert "FIND-001" in collision_warnings[0].message

  # -- Non-breaking regression (VT-030-006) --

  def test_existing_specs_remain_valid_after_taxonomy_validation(self) -> None:
    """Existing specs/paths remain valid when taxonomy validation is active."""
    root = self._create_repo()
    self._write_spec(root, "SPEC-600", "FR-600")
    self._write_tech_spec(root, "SPEC-601", category="unit", c4_level="code")
    self._write_prod_spec(root, "PROD-700")

    ws = Workspace(root)
    # All specs loadable and accessible
    all_specs = ws.specs.all_specs()
    spec_ids = {s.id for s in all_specs}
    assert "SPEC-600" in spec_ids
    assert "SPEC-601" in spec_ids
    assert "PROD-700" in spec_ids

    # Validation runs without error
    issues = validate_workspace(ws)
    errors = [i for i in issues if i.level == "error"]
    # Only SPEC-600 (no taxonomy) should produce warnings, not errors
    assert not any(e.artifact in ("SPEC-600", "SPEC-601", "PROD-700") for e in errors)


class TestUnresolvedReferenceValidation(RepoTestCase):
  """VT-097-unresolved: unresolved frontmatter references detected."""

  def _create_workspace_with_delta(
    self,
    *,
    target: str,
  ) -> Workspace:
    """Create a minimal workspace with a delta referencing a target."""
    root = self._make_repo()

    # Create spec-driver dirs
    spec_dir = root / SPEC_DRIVER_DIR
    (spec_dir / TECH_SPECS_SUBDIR).mkdir(parents=True)
    (spec_dir / PRODUCT_SPECS_SUBDIR).mkdir(parents=True)
    (spec_dir / DECISIONS_SUBDIR).mkdir(parents=True)
    (spec_dir / DELTAS_SUBDIR).mkdir(parents=True)
    (spec_dir / REVISIONS_SUBDIR).mkdir(parents=True)
    (spec_dir / AUDITS_SUBDIR).mkdir(parents=True)

    # Create a delta with a relation to the target
    delta_dir = spec_dir / DELTAS_SUBDIR / "DE-001-test"
    delta_dir.mkdir(parents=True)
    dump_markdown_file(
      delta_dir / "DE-001.md",
      {
        "id": "DE-001",
        "name": "Test delta",
        "status": "draft",
        "kind": "delta",
        "relations": [{"type": "implements", "target": target}],
        "applies_to": {"specs": [], "requirements": []},
      },
      "# DE-001\n",
    )

    os.chdir(root)
    return Workspace(root=root)

  def test_unresolved_ref_produces_warning(self) -> None:
    """Unresolved target in relation emits a warning."""
    ws = self._create_workspace_with_delta(target="NONEXISTENT-999")
    issues = validate_workspace(ws)
    unresolved = [
      i for i in issues if "NONEXISTENT-999" in i.message and i.level == "warning"
    ]
    assert len(unresolved) >= 1, f"Expected warning for unresolved ref, got: {issues}"

  def test_unresolved_ref_strict_produces_error(self) -> None:
    """In strict mode, unresolved target emits an error."""
    ws = self._create_workspace_with_delta(target="NONEXISTENT-999")
    issues = validate_workspace(ws, strict=True)
    unresolved = [
      i for i in issues if "NONEXISTENT-999" in i.message and i.level == "error"
    ]
    assert len(unresolved) >= 1, f"Expected error for unresolved ref, got: {issues}"

  def test_resolved_ref_no_warning(self) -> None:
    """Known target does not produce an unresolved warning."""
    ws = self._create_workspace_with_delta(target="DE-001")
    issues = validate_workspace(ws)
    unresolved = [i for i in issues if "unresolved" in i.message.lower()]
    assert len(unresolved) == 0, f"Unexpected unresolved warnings: {unresolved}"


if __name__ == "__main__":
  unittest.main()
