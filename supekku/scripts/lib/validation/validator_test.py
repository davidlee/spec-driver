"""Tests for validator module."""

from __future__ import annotations

import os
import unittest
from typing import TYPE_CHECKING

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
    spec_dir = root / "specify" / "tech" / f"{spec_id}-sample"
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
    }
    dump_markdown_file(
      spec_path,
      frontmatter,
      f"# Spec\n- {requirement_label}: Example requirement\n",
    )

  def _write_delta(self, root: Path, delta_id: str, requirement_uid: str) -> Path:
    delta_dir = root / "change" / "deltas" / f"{delta_id}-sample"
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
    revision_dir = root / "change" / "revisions" / f"{revision_id}-sample"
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
    audit_dir = root / "change" / "audits" / f"{audit_id}-sample"
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
    assert not issues

    # Break requirement link
    ws.requirements.records["SPEC-300.FR-300"].implemented_by = ["DE-999"]
    ws.requirements.save()
    issues = validate_workspace(ws)
    assert len(issues) == 1
    assert "DE-999" in issues[0].message

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
    assert len(issues) == 1
    assert "SPEC-999.FR-999" in issues[0].message

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

    decisions_dir = root / "specify" / "decisions"
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


if __name__ == "__main__":
  unittest.main()
