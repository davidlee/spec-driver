"""Tests for create_change module."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from supekku.scripts.lib.changes.creation import (
  ChangeArtifactCreated,
  PhaseCreationError,
  create_delta,
  create_phase,
  create_requirement_breakout,
  create_revision,
)
from supekku.scripts.lib.core.spec_utils import load_markdown_file


class CreateChangeTest(unittest.TestCase):
  """Test cases for create_change module functionality."""

  def setUp(self) -> None:
    self._cwd = Path.cwd()

  def tearDown(self) -> None:
    os.chdir(self._cwd)

  def _make_repo(self) -> Path:
    tmpdir = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
    self.addCleanup(tmpdir.cleanup)
    root = Path(tmpdir.name)
    (root / ".git").mkdir()

    # Create .spec-driver/templates directory with template files
    templates_dir = root / ".spec-driver" / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)

    # Delta template (Jinja2, no frontmatter)
    # Uses {{ delta_relationships_block }} variable for YAML block
    (templates_dir / "delta.md").write_text(
      "# {{ delta_id }} – {{ name }}\n\n{{ delta_relationships_block }}\n",
      encoding="utf-8",
    )

    # Revision template (Jinja2, no frontmatter)
    (templates_dir / "revision.md").write_text(
      "## 1. Context\n- **Why**: Change reason\n",
      encoding="utf-8",
    )

    # Plan template (Jinja2, no frontmatter)
    # Uses {{ plan_overview_block }} variable for YAML block
    (templates_dir / "plan.md").write_text(
      "{{ plan_overview_block }}\n",
      encoding="utf-8",
    )

    # Phase template (Jinja2, no frontmatter)
    # Uses {{ phase_overview_block }} variable for YAML block
    (templates_dir / "phase.md").write_text(
      "{{ phase_overview_block }}\n",
      encoding="utf-8",
    )

    spec_dir = root / "specify" / "tech" / "spec-100-example"
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "SPEC-100.md").write_text(
      (
        "---\nid: SPEC-100\nslug: spec-100\nname: Spec 100\n"
        "created: 2024-01-01\nupdated: 2024-01-01\nstatus: draft\n"
        "kind: spec\n---\n\n- FR-100: Example\n"
      ),
      encoding="utf-8",
    )
    os.chdir(root)
    return root

  def test_create_revision(self) -> None:
    """Test creating a revision change artifact with source and destination specs."""
    root = self._make_repo()
    result = create_revision(
      "Move FR",
      source_specs=["SPEC-100"],
      destination_specs=["SPEC-101"],
      requirements=["SPEC-100.FR-100"],
      repo_root=root,
    )
    assert isinstance(result, ChangeArtifactCreated)
    assert result.primary_path.exists()
    frontmatter, _ = load_markdown_file(result.primary_path)
    assert frontmatter["kind"] == "revision"
    assert "SPEC-100" in frontmatter.get("source_specs", [])

  def test_create_delta(self) -> None:
    """Test creating a delta change artifact with associated implementation plan."""
    root = self._make_repo()
    result = create_delta(
      "Implement ignore handling",
      specs=["SPEC-100"],
      requirements=["SPEC-100.FR-100"],
      repo_root=root,
    )
    assert result.primary_path.exists()
    frontmatter, _ = load_markdown_file(result.primary_path)
    assert frontmatter["kind"] == "delta"
    plan_files = [p for p in result.extras if p.name.startswith("IP-")]
    assert plan_files

  def test_create_requirement_breakout(self) -> None:
    """Test creating a requirement breakout artifact for a spec."""
    root = self._make_repo()
    path = create_requirement_breakout(
      "SPEC-100",
      "FR-200",
      title="Handle edge cases",
      repo_root=root,
    )
    assert path.exists()
    frontmatter, _ = load_markdown_file(path)
    assert frontmatter["kind"] == "requirement"
    assert frontmatter["spec"] == "SPEC-100"

  def test_create_phase_first_in_sequence(self) -> None:
    """Test creating the first phase for a plan."""
    root = self._make_repo()
    # Create a delta with plan first
    delta_result = create_delta(
      "Test Delta",
      specs=["SPEC-100"],
      requirements=["SPEC-100.FR-100"],
      repo_root=root,
    )
    # Extract plan ID from extras (IP-001.md)
    plan_files = [p for p in delta_result.extras if p.name.startswith("IP-")]
    assert plan_files, "Plan file should be created with delta"
    plan_id = plan_files[0].stem  # Get "IP-001" from "IP-001.md"

    # Remove the default phase-01.md that delta creation made
    phases_dir = delta_result.directory / "phases"
    default_phase = phases_dir / "phase-01.md"
    if default_phase.exists():
      default_phase.unlink()

    # Now create first phase
    result = create_phase("Phase 01 - Foundation", plan_id, repo_root=root)
    assert result.phase_id == f"{plan_id}.PHASE-01"
    assert result.plan_id == plan_id
    assert result.phase_path.exists()
    assert result.phase_path.name == "phase-01.md"

    # Verify frontmatter
    frontmatter, _ = load_markdown_file(result.phase_path)
    assert frontmatter["kind"] == "phase"
    assert frontmatter["id"] == f"{plan_id}.PHASE-01"

  def test_create_phase_auto_increment(self) -> None:
    """Test phase numbering automatically increments."""
    root = self._make_repo()
    # Create delta with plan
    delta_result = create_delta(
      "Test Delta",
      specs=["SPEC-100"],
      requirements=["SPEC-100.FR-100"],
      repo_root=root,
    )
    plan_files = [p for p in delta_result.extras if p.name.startswith("IP-")]
    plan_id = plan_files[0].stem

    # Create second phase (phase-01 already exists from delta creation)
    result = create_phase("Phase 02 - Next", plan_id, repo_root=root)
    assert result.phase_id == f"{plan_id}.PHASE-02"
    assert result.phase_path.name == "phase-02.md"

    # Create third phase
    result2 = create_phase("Phase 03 - Final", plan_id, repo_root=root)
    assert result2.phase_id == f"{plan_id}.PHASE-03"
    assert result2.phase_path.name == "phase-03.md"

  def test_create_phase_invalid_plan(self) -> None:
    """Test error when plan does not exist."""
    root = self._make_repo()
    with self.assertRaises(PhaseCreationError) as ctx:
      create_phase("Phase 01", "IP-999", repo_root=root)
    assert "not found" in str(ctx.exception).lower()

  def test_create_phase_empty_name(self) -> None:
    """Test error when phase name is empty."""
    root = self._make_repo()
    with self.assertRaises(PhaseCreationError) as ctx:
      create_phase("", "IP-001", repo_root=root)
    assert "cannot be empty" in str(ctx.exception).lower()

  def test_create_phase_metadata_population(self) -> None:
    """Test phase metadata is correctly populated."""
    root = self._make_repo()
    # Create delta with plan
    delta_result = create_delta(
      "Test Delta",
      specs=["SPEC-100"],
      requirements=["SPEC-100.FR-100"],
      repo_root=root,
    )
    plan_files = [p for p in delta_result.extras if p.name.startswith("IP-")]
    plan_id = plan_files[0].stem
    delta_id = delta_result.artifact_id

    # Create phase (will be PHASE-02 since delta creates PHASE-01)
    result = create_phase("Phase 02 - Test", plan_id, repo_root=root)

    # Verify all metadata fields
    frontmatter, body = load_markdown_file(result.phase_path)
    assert frontmatter["id"] == f"{plan_id}.PHASE-02"
    assert frontmatter["kind"] == "phase"
    assert frontmatter["status"] == "draft"
    assert "created" in frontmatter
    assert "updated" in frontmatter

    # Check YAML block in body contains correct IDs
    assert f"phase: {plan_id}.PHASE-02" in body
    assert f"plan: {plan_id}" in body
    assert f"delta: {delta_id}" in body


if __name__ == "__main__":
  unittest.main()
