"""Tests for create_change module."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from textwrap import dedent

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
    # Uses {{ phase_overview_block }} and {{ phase_tracking_block }} variables
    (templates_dir / "phase.md").write_text(
      "{{ phase_overview_block }}\n\n{{ phase_tracking_block }}\n",
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
    """VT-016-001: Test delta creation produces 4 files without phase-01."""
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

    # Verify design revision created
    design_revision_files = [p for p in result.extras if p.name.startswith("DR-")]
    assert design_revision_files, "Design revision file should be created with delta"
    design_revision_path = design_revision_files[0]
    dr_frontmatter, _ = load_markdown_file(design_revision_path)
    assert dr_frontmatter["kind"] == "design_revision"
    assert dr_frontmatter["delta_ref"] == result.artifact_id
    assert dr_frontmatter.get("relations") == [
      {"type": "implements", "target": result.artifact_id},
    ]

    # Verify implementation plan created
    plan_files = [p for p in result.extras if p.name.startswith("IP-")]
    assert plan_files, "Implementation plan should be created"

    # VT-016-001: Verify NO phase-01 auto-created (PROD-011.FR-001)
    phase_files = [p for p in result.extras if "phase" in p.name.lower()]
    assert not phase_files, "Phase-01 should NOT be auto-created with delta"

    # Verify no phases directory created
    phases_dir = result.directory / "phases"
    assert not phases_dir.exists(), "Phases directory should not exist yet"

    # Verify exactly 4 files: delta, DR, IP, notes
    assert len(result.extras) == 3  # DR, IP, notes (not counting primary delta file)

  def test_create_delta_without_plan_still_adds_design_revision(self) -> None:
    """Delta creation without plan still scaffolds a design revision."""
    root = self._make_repo()
    result = create_delta(
      "Documentation-only delta",
      specs=["SPEC-100"],
      requirements=None,
      repo_root=root,
      allow_missing_plan=True,
    )
    design_revision_files = [p for p in result.extras if p.name.startswith("DR-")]
    assert design_revision_files, "Design revision created even when plan is skipped"
    design_revision_path = design_revision_files[0]
    assert design_revision_path.exists()
    frontmatter, _ = load_markdown_file(design_revision_path)
    assert frontmatter["delta_ref"] == result.artifact_id
    assert frontmatter.get("relations") == [
      {"type": "implements", "target": result.artifact_id},
    ]
    plan_files = [p for p in result.extras if p.name.startswith("IP-")]
    assert plan_files == []

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
    """VT-016-002: Test creating phase-01 when no phases exist (PROD-011.FR-002)."""
    root = self._make_repo()
    # Create a delta with plan
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

    # Verify no phases directory exists yet (FR-001)
    phases_dir = delta_result.directory / "phases"
    assert not phases_dir.exists(), "No phases directory should exist initially"

    # VT-016-002: Create first phase when none exist (PROD-011.FR-002)
    result = create_phase("Phase 01 - Foundation", plan_id, repo_root=root)
    assert result.phase_id == f"{plan_id}.PHASE-01"
    assert result.plan_id == plan_id
    assert result.phase_path.exists()
    assert result.phase_path.name == "phase-01.md"

    # Verify phases directory created
    assert phases_dir.exists(), "Phases directory should be created by create_phase"

    # Verify frontmatter
    frontmatter, _ = load_markdown_file(result.phase_path)
    assert frontmatter["kind"] == "phase"
    assert frontmatter["id"] == f"{plan_id}.PHASE-01"

  def test_create_phase_auto_increment(self) -> None:
    """VT-016-004: Test phase numbering automatically increments from 01 onwards."""
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

    # Create first phase (none exist yet per FR-001)
    result1 = create_phase("Phase 01 - Foundation", plan_id, repo_root=root)
    assert result1.phase_id == f"{plan_id}.PHASE-01"
    assert result1.phase_path.name == "phase-01.md"

    # Create second phase
    result2 = create_phase("Phase 02 - Next", plan_id, repo_root=root)
    assert result2.phase_id == f"{plan_id}.PHASE-02"
    assert result2.phase_path.name == "phase-02.md"

    # Create third phase
    result3 = create_phase("Phase 03 - Final", plan_id, repo_root=root)
    assert result3.phase_id == f"{plan_id}.PHASE-03"
    assert result3.phase_path.name == "phase-03.md"

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

    # Create phase (will be PHASE-01 since delta no longer auto-creates phase-01)
    result = create_phase("Phase 01 - Test", plan_id, repo_root=root)

    # Verify all metadata fields
    frontmatter, body = load_markdown_file(result.phase_path)
    assert frontmatter["id"] == f"{plan_id}.PHASE-01"
    assert frontmatter["kind"] == "phase"
    assert frontmatter["status"] == "draft"
    assert "created" in frontmatter
    assert "updated" in frontmatter

    # Check YAML block in body contains correct IDs
    assert f"phase: {plan_id}.PHASE-01" in body
    assert f"plan: {plan_id}" in body
    assert f"delta: {delta_id}" in body

  def test_create_phase_updates_plan_metadata(self) -> None:
    """VT-PHASE-006: Test plan.overview phases array is updated."""
    root = self._make_repo()
    # Create delta with plan
    delta_result = create_delta(
      "Test Delta",
      specs=["SPEC-100"],
      requirements=["SPEC-100.FR-100"],
      repo_root=root,
    )
    plan_files = [p for p in delta_result.extras if p.name.startswith("IP-")]
    plan_path = plan_files[0]
    plan_id = plan_path.stem

    # Read plan before creating phases (should have no phases initially per FR-001)
    content_before = plan_path.read_text(encoding="utf-8")
    assert "phases:" in content_before
    # Should have empty phases array initially
    assert f"{plan_id}.PHASE-01" not in content_before

    # Create first phase
    result1 = create_phase("Phase 01 - Test", plan_id, repo_root=root)

    # Create second phase
    result2 = create_phase("Phase 02 - Test", plan_id, repo_root=root)

    # Read plan after creating phases
    content_after = plan_path.read_text(encoding="utf-8")

    # Verify both phases added to plan.overview
    assert f"- id: {result1.phase_id}" in content_after
    assert f"- id: {result2.phase_id}" in content_after
    assert f"- id: {plan_id}.PHASE-01" in content_after
    assert f"- id: {plan_id}.PHASE-02" in content_after

    # Verify both phases present
    assert content_after.count("- id: ") >= 2

  def test_create_phase_metadata_preserves_existing(self) -> None:
    """VT-PHASE-006: Test existing phases not corrupted by new phase."""
    root = self._make_repo()
    delta_result = create_delta(
      "Test Delta",
      specs=["SPEC-100"],
      requirements=["SPEC-100.FR-100"],
      repo_root=root,
    )
    plan_files = [p for p in delta_result.extras if p.name.startswith("IP-")]
    plan_path = plan_files[0]
    plan_id = plan_path.stem

    # Create phase-01
    create_phase("Phase 01", plan_id, repo_root=root)

    # Read after phase-01 created
    content_after_01 = plan_path.read_text(encoding="utf-8")
    assert f"{plan_id}.PHASE-01" in content_after_01

    # Create phase-02
    create_phase("Phase 02", plan_id, repo_root=root)

    # Create phase-03
    create_phase("Phase 03", plan_id, repo_root=root)

    # Verify all three phases present and phase-01 not corrupted
    content_after = plan_path.read_text(encoding="utf-8")
    assert f"{plan_id}.PHASE-01" in content_after
    assert f"{plan_id}.PHASE-02" in content_after
    assert f"{plan_id}.PHASE-03" in content_after

    # Verify structure still valid (phases as list)
    assert "phases:" in content_after
    # Count should be 4: 1 placeholder (IP-001-P01) + 3 created phases
    assert content_after.count("- id: ") == 4

  def test_create_phase_copies_criteria_from_plan(self) -> None:
    """VT-CREATE-013-002: Test phase criteria copied from IP metadata."""
    root = self._make_repo()
    # Create delta with plan
    delta_result = create_delta(
      "Test Delta",
      specs=["SPEC-100"],
      requirements=["SPEC-100.FR-100"],
      repo_root=root,
    )
    plan_files = [p for p in delta_result.extras if p.name.startswith("IP-")]
    plan_path = plan_files[0]
    plan_id = plan_path.stem

    # Manually edit plan to add full phase metadata
    plan_content = plan_path.read_text(encoding="utf-8")
    # Replace the placeholder with full phase metadata
    replacement = dedent(f"""\
      - id: {plan_id}.PHASE-01
        name: Foundation Phase
        objective: Build the foundation
        entrance_criteria:
        - Requirement 1 satisfied
        - Design approved
        exit_criteria:
        - Tests passing
        - Code reviewed""")
    # Replace placeholder (IP-001-P01) with actual phase ID
    updated_plan = plan_content.replace(f"  - id: {plan_id}-P01", replacement)
    plan_path.write_text(updated_plan, encoding="utf-8")

    # No phase-01 exists yet (FR-001: delta no longer auto-creates phase-01)
    # Create phase from plan with metadata
    result = create_phase("Foundation Phase", plan_id, repo_root=root)

    # Verify phase file content
    phase_content = result.phase_path.read_text(encoding="utf-8")

    # Check phase.overview block has criteria (may use YAML block scalars)
    assert "Build the foundation" in phase_content
    assert "entrance_criteria:" in phase_content
    assert "Requirement 1 satisfied" in phase_content
    assert "Design approved" in phase_content
    assert "exit_criteria:" in phase_content
    assert "Tests passing" in phase_content
    assert "Code reviewed" in phase_content

    # Check phase.tracking block has criteria
    assert "phase.tracking" in phase_content
    has_entrance = (
      'item: "Requirement 1 satisfied"' in phase_content
      or 'item: "Design approved"' in phase_content
    )
    has_exit = (
      'item: "Tests passing"' in phase_content
      or 'item: "Code reviewed"' in phase_content
    )
    assert has_entrance
    assert has_exit

  def test_create_phase_id_only_format_graceful_fallback(self) -> None:
    """VT-CREATE-013-002: Test create_phase works with ID-only format."""
    root = self._make_repo()
    # Create delta with plan
    delta_result = create_delta(
      "Test Delta",
      specs=["SPEC-100"],
      requirements=["SPEC-100.FR-100"],
      repo_root=root,
    )
    plan_files = [p for p in delta_result.extras if p.name.startswith("IP-")]
    plan_path = plan_files[0]
    plan_id = plan_path.stem

    # Plan has placeholder format by default (IP-001-P01)
    plan_content = plan_path.read_text(encoding="utf-8")
    assert f"- id: {plan_id}-P01" in plan_content
    # Replace placeholder with PHASE-01 for testing
    updated_plan = plan_content.replace(f"{plan_id}-P01", f"{plan_id}.PHASE-01")
    plan_path.write_text(updated_plan, encoding="utf-8")

    # Verify no metadata (just ID)
    plan_content = plan_path.read_text(encoding="utf-8")
    assert f"- id: {plan_id}.PHASE-01" in plan_content
    assert "entrance_criteria:" not in plan_content.split("phases:")[1].split("```")[0]

    # No phase-01 exists yet (FR-001: delta no longer auto-creates phase-01)
    # Create phase - should work without errors
    result = create_phase("Phase 01 - Minimal", plan_id, repo_root=root)

    # Verify phase created successfully
    assert result.phase_path.exists()
    phase_content = result.phase_path.read_text(encoding="utf-8")
    assert f"phase: {plan_id}.PHASE-01" in phase_content

  def test_create_phase_partial_metadata_handles_correctly(self) -> None:
    """VT-CREATE-013-002: Test partial metadata (some fields present)."""
    root = self._make_repo()
    delta_result = create_delta(
      "Test Delta",
      specs=["SPEC-100"],
      requirements=["SPEC-100.FR-100"],
      repo_root=root,
    )
    plan_files = [p for p in delta_result.extras if p.name.startswith("IP-")]
    plan_path = plan_files[0]
    plan_id = plan_path.stem

    # Add partial metadata (only entrance_criteria, no exit_criteria or objective)
    plan_content = plan_path.read_text(encoding="utf-8")
    # Replace placeholder with PHASE-01 with partial metadata
    updated_plan = plan_content.replace(
      f"  - id: {plan_id}-P01",
      f"""  - id: {plan_id}.PHASE-01
    entrance_criteria:
    - Entry criterion only""",
    )
    plan_path.write_text(updated_plan, encoding="utf-8")

    # No phase-01 exists yet (FR-001: delta no longer auto-creates phase-01)
    # Create phase
    result = create_phase("Partial Metadata Phase", plan_id, repo_root=root)

    # Verify entrance criteria copied but no exit criteria
    phase_content = result.phase_path.read_text(encoding="utf-8")
    assert 'item: "Entry criterion only"' in phase_content
    # phase.tracking should have entrance but empty exit
    assert "entrance_criteria:" in phase_content

  def test_create_phase_empty_criteria_arrays_handled(self) -> None:
    """VT-CREATE-013-002: Test empty criteria arrays handled correctly."""
    root = self._make_repo()
    delta_result = create_delta(
      "Test Delta",
      specs=["SPEC-100"],
      requirements=["SPEC-100.FR-100"],
      repo_root=root,
    )
    plan_files = [p for p in delta_result.extras if p.name.startswith("IP-")]
    plan_path = plan_files[0]
    plan_id = plan_path.stem

    # Add empty criteria arrays
    plan_content = plan_path.read_text(encoding="utf-8")
    # Replace placeholder with PHASE-01 with empty criteria
    updated_plan = plan_content.replace(
      f"  - id: {plan_id}-P01",
      f"""  - id: {plan_id}.PHASE-01
    objective: Test empty arrays
    entrance_criteria: []
    exit_criteria: []""",
    )
    plan_path.write_text(updated_plan, encoding="utf-8")

    # No phase-01 exists yet (FR-001: delta no longer auto-creates phase-01)
    # Create phase - should not fail
    result = create_phase("Empty Arrays Phase", plan_id, repo_root=root)

    # Verify phase created
    assert result.phase_path.exists()
    phase_content = result.phase_path.read_text(encoding="utf-8")
    assert "Test empty arrays" in phase_content


if __name__ == "__main__":
  unittest.main()
