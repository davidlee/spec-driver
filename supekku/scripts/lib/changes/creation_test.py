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

    # Read plan before creating phase
    content_before = plan_path.read_text(encoding="utf-8")
    # Verify initial phase exists (from delta creation)
    assert f"{plan_id}.PHASE-01" in content_before

    # Create second phase
    result = create_phase("Phase 02 - Test", plan_id, repo_root=root)

    # Read plan after creating phase
    content_after = plan_path.read_text(encoding="utf-8")

    # Verify new phase added to plan.overview
    assert f"- id: {result.phase_id}" in content_after
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

    # Read original phase-01 from plan
    content_before = plan_path.read_text(encoding="utf-8")
    assert f"{plan_id}.PHASE-01" in content_before

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
    assert content_after.count("- id: ") == 3

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
    # Replace the phases section with full metadata
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
    updated_plan = plan_content.replace(f"  - id: {plan_id}.PHASE-01", replacement)
    plan_path.write_text(updated_plan, encoding="utf-8")

    # Remove default phase-01 to test creation from scratch
    phases_dir = delta_result.directory / "phases"
    default_phase = phases_dir / "phase-01.md"
    if default_phase.exists():
      default_phase.unlink()

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

    # Plan already has ID-only format by default
    plan_content = plan_path.read_text(encoding="utf-8")
    assert f"- id: {plan_id}.PHASE-01" in plan_content
    # Verify no metadata (just ID)
    assert "entrance_criteria:" not in plan_content.split("phases:")[1].split("```")[0]

    # Remove default phase-01
    phases_dir = delta_result.directory / "phases"
    default_phase = phases_dir / "phase-01.md"
    if default_phase.exists():
      default_phase.unlink()

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
    updated_plan = plan_content.replace(
      f"  - id: {plan_id}.PHASE-01",
      f"""  - id: {plan_id}.PHASE-01
    entrance_criteria:
    - Entry criterion only""",
    )
    plan_path.write_text(updated_plan, encoding="utf-8")

    # Remove default phase
    phases_dir = delta_result.directory / "phases"
    (phases_dir / "phase-01.md").unlink()

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
    updated_plan = plan_content.replace(
      f"  - id: {plan_id}.PHASE-01",
      f"""  - id: {plan_id}.PHASE-01
    objective: Test empty arrays
    entrance_criteria: []
    exit_criteria: []""",
    )
    plan_path.write_text(updated_plan, encoding="utf-8")

    # Remove default phase
    phases_dir = delta_result.directory / "phases"
    (phases_dir / "phase-01.md").unlink()

    # Create phase - should not fail
    result = create_phase("Empty Arrays Phase", plan_id, repo_root=root)

    # Verify phase created
    assert result.phase_path.exists()
    phase_content = result.phase_path.read_text(encoding="utf-8")
    assert "Test empty arrays" in phase_content


if __name__ == "__main__":
  unittest.main()
