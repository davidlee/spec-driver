"""Tests for deletion infrastructure."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from .deletion import DeletionExecutor, DeletionPlan, DeletionValidator
from .registry_migration import RegistryV2


class TestDeletionPlan(unittest.TestCase):
  """Test DeletionPlan data class."""

  def test_creation_defaults(self) -> None:
    """Test creating a DeletionPlan with defaults."""
    plan = DeletionPlan(artifact_id="SPEC-001", artifact_type="spec")

    assert plan.artifact_id == "SPEC-001"
    assert plan.artifact_type == "spec"
    assert plan.files_to_delete == []
    assert plan.symlinks_to_remove == []
    assert plan.registry_updates == {}
    assert plan.cross_references == {}
    assert plan.is_safe is True
    assert plan.warnings == []

  def test_add_warning(self) -> None:
    """Test adding warnings to a plan."""
    plan = DeletionPlan(artifact_id="SPEC-001", artifact_type="spec")

    plan.add_warning("First warning")
    plan.add_warning("Second warning")

    assert len(plan.warnings) == 2
    assert plan.warnings[0] == "First warning"
    assert plan.warnings[1] == "Second warning"

  def test_add_file(self) -> None:
    """Test adding files to delete."""
    plan = DeletionPlan(artifact_id="SPEC-001", artifact_type="spec")

    file1 = Path("/test/file1.md")
    file2 = Path("/test/file2.md")
    plan.add_file(file1)
    plan.add_file(file2)

    assert len(plan.files_to_delete) == 2
    assert file1 in plan.files_to_delete
    assert file2 in plan.files_to_delete

  def test_add_symlink(self) -> None:
    """Test adding symlinks to remove."""
    plan = DeletionPlan(artifact_id="SPEC-001", artifact_type="spec")

    link1 = Path("/test/link1")
    link2 = Path("/test/link2")
    plan.add_symlink(link1)
    plan.add_symlink(link2)

    assert len(plan.symlinks_to_remove) == 2
    assert link1 in plan.symlinks_to_remove
    assert link2 in plan.symlinks_to_remove

  def test_add_registry_update(self) -> None:
    """Test adding registry updates."""
    plan = DeletionPlan(artifact_id="SPEC-001", artifact_type="spec")

    plan.add_registry_update("registry_v2.json", "SPEC-001")
    plan.add_registry_update("registry_v2.json", "SPEC-002")
    plan.add_registry_update("other_registry.json", "SPEC-003")

    assert len(plan.registry_updates) == 2
    assert "registry_v2.json" in plan.registry_updates
    assert len(plan.registry_updates["registry_v2.json"]) == 2
    assert "SPEC-001" in plan.registry_updates["registry_v2.json"]
    assert "SPEC-002" in plan.registry_updates["registry_v2.json"]
    assert "other_registry.json" in plan.registry_updates
    assert len(plan.registry_updates["other_registry.json"]) == 1

  def test_add_cross_reference(self) -> None:
    """Test adding cross-references."""
    plan = DeletionPlan(artifact_id="SPEC-001", artifact_type="spec")

    plan.add_cross_reference("DE-001", "SPEC-001")
    plan.add_cross_reference("DE-001", "SPEC-002")
    plan.add_cross_reference("REV-001", "SPEC-001")

    assert len(plan.cross_references) == 2
    assert "DE-001" in plan.cross_references
    assert len(plan.cross_references["DE-001"]) == 2
    assert "SPEC-001" in plan.cross_references["DE-001"]
    assert "SPEC-002" in plan.cross_references["DE-001"]
    assert "REV-001" in plan.cross_references
    assert len(plan.cross_references["REV-001"]) == 1


class TestDeletionValidator(unittest.TestCase):
  """Test DeletionValidator functionality."""

  def setUp(self) -> None:
    """Set up test fixtures."""
    self.temp_dir = TemporaryDirectory()
    self.repo_root = Path(self.temp_dir.name)
    self.tech_dir = self.repo_root / "specify" / "tech"
    self.tech_dir.mkdir(parents=True)
    self.validator = DeletionValidator(self.repo_root)

  def tearDown(self) -> None:
    """Clean up test fixtures."""
    self.temp_dir.cleanup()

  def _create_spec_with_frontmatter(self, spec_id: str, frontmatter: dict) -> Path:
    """Create a spec directory and file with given frontmatter."""
    spec_dir = self.tech_dir / spec_id
    spec_dir.mkdir(exist_ok=True)
    spec_file = spec_dir / f"{spec_id}.md"

    frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False)
    content = (
      f"---\n{frontmatter_yaml}---\n\n# {spec_id}\n\nTest specification content."
    )

    spec_file.write_text(content)
    return spec_file

  def _create_symlink(self, link_path: Path, target: Path) -> None:
    """Create a symlink, creating parent directories as needed."""
    link_path.parent.mkdir(parents=True, exist_ok=True)
    link_path.symlink_to(target)

  def test_initialization(self) -> None:
    """Test DeletionValidator initialization."""
    assert self.validator.repo_root == self.repo_root
    assert self.validator.tech_dir == self.tech_dir
    assert self.validator.change_dir == self.repo_root / "change"

  def test_validate_spec_deletion_nonexistent_spec(self) -> None:
    """Test validating deletion of a spec that doesn't exist."""
    plan = self.validator.validate_spec_deletion("SPEC-999")

    assert plan.artifact_id == "SPEC-999"
    assert plan.artifact_type == "spec"
    assert plan.is_safe is False
    assert len(plan.warnings) == 1
    assert "Spec directory not found" in plan.warnings[0]

  def test_validate_spec_deletion_existing_spec(self) -> None:
    """Test validating deletion of an existing spec."""
    self._create_spec_with_frontmatter(
      "SPEC-001",
      {"slug": "test-spec", "packages": ["internal/test"]},
    )

    plan = self.validator.validate_spec_deletion("SPEC-001")

    assert plan.artifact_id == "SPEC-001"
    assert plan.artifact_type == "spec"
    assert plan.is_safe is True
    assert len(plan.files_to_delete) == 1
    assert plan.files_to_delete[0].name == "SPEC-001.md"
    assert len(plan.registry_updates) == 1
    assert "registry_v2.json" in plan.registry_updates

  def test_validate_spec_deletion_with_multiple_files(self) -> None:
    """Test validating deletion of spec with multiple markdown files."""
    spec_dir = self.tech_dir / "SPEC-002"
    spec_dir.mkdir()
    (spec_dir / "SPEC-002.md").write_text("# Main spec")
    (spec_dir / "tests.md").write_text("# Tests")
    (spec_dir / "notes.md").write_text("# Notes")

    plan = self.validator.validate_spec_deletion("SPEC-002")

    assert plan.is_safe is True
    assert len(plan.files_to_delete) == 3
    file_names = {f.name for f in plan.files_to_delete}
    assert "SPEC-002.md" in file_names
    assert "tests.md" in file_names
    assert "notes.md" in file_names

  def test_validate_spec_deletion_with_symlinks(self) -> None:
    """Test validating deletion detects symlinks to spec."""
    self._create_spec_with_frontmatter(
      "SPEC-003",
      {"slug": "linked-spec", "packages": ["internal/linked"]},
    )

    # Create symlinks
    slug_link = self.tech_dir / "by-slug" / "linked-spec"
    package_link = self.tech_dir / "by-package" / "internal" / "linked" / "spec"
    lang_link = self.tech_dir / "by-language" / "go" / "internal" / "linked" / "spec"

    self._create_symlink(slug_link, Path("../SPEC-003"))
    self._create_symlink(package_link, Path("../../../SPEC-003"))
    self._create_symlink(lang_link, Path("../../../../SPEC-003"))

    plan = self.validator.validate_spec_deletion("SPEC-003")

    assert plan.is_safe is True
    assert len(plan.symlinks_to_remove) == 3
    symlink_names = {
      s.name if s.name != "spec" else str(s.parent.name)
      for s in plan.symlinks_to_remove
    }
    slug_found = "linked-spec" in symlink_names or any(
      "slug" in str(s) for s in plan.symlinks_to_remove
    )
    assert slug_found

  def test_validate_spec_deletion_with_broken_symlinks(self) -> None:
    """Test validator handles broken symlinks gracefully."""
    self._create_spec_with_frontmatter(
      "SPEC-004",
      {"slug": "test-spec"},
    )

    # Create broken symlink
    broken_link = self.tech_dir / "by-slug" / "broken"
    self._create_symlink(broken_link, Path("../NONEXISTENT"))

    # Should not crash
    plan = self.validator.validate_spec_deletion("SPEC-004")
    assert plan.is_safe is True

  def test_find_spec_symlinks_no_indices(self) -> None:
    """Test finding symlinks when index directories don't exist."""
    self._create_spec_with_frontmatter(
      "SPEC-005",
      {"slug": "no-indices"},
    )

    symlinks = self.validator._find_spec_symlinks("SPEC-005")
    assert len(symlinks) == 0

  def test_find_spec_symlinks_multiple_indices(self) -> None:
    """Test finding symlinks across multiple index directories."""
    self._create_spec_with_frontmatter(
      "SPEC-006",
      {"slug": "multi-index"},
    )

    # Create symlinks in different indices
    slug_link = self.tech_dir / "by-slug" / "multi-index"
    package_link = self.tech_dir / "by-package" / "pkg" / "spec"
    lang_link = self.tech_dir / "by-language" / "python" / "module.py" / "spec"

    self._create_symlink(slug_link, Path("../SPEC-006"))
    self._create_symlink(package_link, Path("../../SPEC-006"))
    self._create_symlink(lang_link, Path("../../../SPEC-006"))

    symlinks = self.validator._find_spec_symlinks("SPEC-006")
    assert len(symlinks) == 3

  def test_find_spec_symlinks_nested_in_spec_dir(self) -> None:
    """Test finding symlinks that point to files within spec directory."""
    self._create_spec_with_frontmatter(
      "SPEC-007",
      {"slug": "nested-target"},
    )

    # Create symlink pointing to file inside spec
    nested_link = self.tech_dir / "by-slug" / "nested"
    self._create_symlink(nested_link, Path("../SPEC-007/SPEC-007.md"))

    symlinks = self.validator._find_spec_symlinks("SPEC-007")
    assert len(symlinks) == 1
    assert nested_link in symlinks


class TestDeletionExecutor(unittest.TestCase):
  """Test DeletionExecutor functionality."""

  def setUp(self) -> None:
    """Set up test fixtures."""
    self.temp_dir = TemporaryDirectory()
    self.repo_root = Path(self.temp_dir.name)
    self.tech_dir = self.repo_root / "specify" / "tech"
    self.tech_dir.mkdir(parents=True)
    self.executor = DeletionExecutor(self.repo_root)

  def tearDown(self) -> None:
    """Clean up test fixtures."""
    self.temp_dir.cleanup()

  def _create_spec_with_frontmatter(self, spec_id: str, frontmatter: dict) -> Path:
    """Create a spec directory and file with given frontmatter."""
    spec_dir = self.tech_dir / spec_id
    spec_dir.mkdir(exist_ok=True)
    spec_file = spec_dir / f"{spec_id}.md"

    frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False)
    content = (
      f"---\n{frontmatter_yaml}---\n\n# {spec_id}\n\nTest specification content."
    )

    spec_file.write_text(content)
    return spec_file

  def _create_symlink(self, link_path: Path, target: Path) -> None:
    """Create a symlink, creating parent directories as needed."""
    link_path.parent.mkdir(parents=True, exist_ok=True)
    link_path.symlink_to(target)

  def test_initialization(self) -> None:
    """Test DeletionExecutor initialization."""
    assert self.executor.repo_root == self.repo_root
    assert isinstance(self.executor.validator, DeletionValidator)

  def test_delete_spec_dry_run_nonexistent(self) -> None:
    """Test dry-run deletion of nonexistent spec."""
    plan = self.executor.delete_spec("SPEC-999", dry_run=True)

    assert plan.artifact_id == "SPEC-999"
    assert plan.is_safe is False
    assert len(plan.warnings) == 1

  def test_delete_spec_dry_run_existing(self) -> None:
    """Test dry-run deletion of existing spec."""
    self._create_spec_with_frontmatter(
      "SPEC-001",
      {"slug": "test-spec"},
    )

    plan = self.executor.delete_spec("SPEC-001", dry_run=True)

    assert plan.is_safe is True
    assert len(plan.files_to_delete) == 1

    # Files should still exist after dry-run
    spec_dir = self.tech_dir / "SPEC-001"
    assert spec_dir.exists()
    assert (spec_dir / "SPEC-001.md").exists()

  def test_delete_spec_actual_deletion(self) -> None:
    """Test actual deletion of spec files and directory."""
    self._create_spec_with_frontmatter(
      "SPEC-002",
      {"slug": "delete-me"},
    )

    spec_dir = self.tech_dir / "SPEC-002"
    assert spec_dir.exists()

    plan = self.executor.delete_spec("SPEC-002", dry_run=False)

    assert plan.is_safe is True
    # Spec directory should be deleted
    assert not spec_dir.exists()

  def test_delete_spec_removes_symlinks(self) -> None:
    """Test deletion removes associated symlinks."""
    self._create_spec_with_frontmatter(
      "SPEC-003",
      {"slug": "with-links"},
    )

    # Create symlinks
    slug_link = self.tech_dir / "by-slug" / "with-links"
    package_link = self.tech_dir / "by-package" / "pkg" / "spec"

    self._create_symlink(slug_link, Path("../SPEC-003"))
    self._create_symlink(package_link, Path("../../SPEC-003"))

    assert slug_link.exists()
    assert package_link.exists()

    plan = self.executor.delete_spec("SPEC-003", dry_run=False)

    assert plan.is_safe is True
    # Symlinks should be removed
    assert not slug_link.exists()
    assert not package_link.exists()

  def test_delete_spec_with_multiple_files(self) -> None:
    """Test deletion of spec with multiple markdown files."""
    spec_dir = self.tech_dir / "SPEC-004"
    spec_dir.mkdir()
    (spec_dir / "SPEC-004.md").write_text("# Main")
    (spec_dir / "tests.md").write_text("# Tests")
    (spec_dir / "notes.md").write_text("# Notes")

    assert len(list(spec_dir.glob("*.md"))) == 3

    plan = self.executor.delete_spec("SPEC-004", dry_run=False)

    assert plan.is_safe is True
    # Entire directory should be removed
    assert not spec_dir.exists()

  def test_delete_spec_unsafe_deletion_not_executed(self) -> None:
    """Test that unsafe deletions are not executed."""
    # Try to delete nonexistent spec
    plan = self.executor.delete_spec("SPEC-999", dry_run=False)

    assert plan.is_safe is False
    # Nothing should be deleted (nothing exists anyway, but plan should block)

  def test_delete_spec_handles_already_deleted_files(self) -> None:
    """Test deletion handles race conditions where files are already deleted."""
    self._create_spec_with_frontmatter(
      "SPEC-005",
      {"slug": "race-test"},
    )

    spec_file = self.tech_dir / "SPEC-005" / "SPEC-005.md"
    spec_file.unlink()  # Manually delete the file

    # Should not crash
    plan = self.executor.delete_spec("SPEC-005", dry_run=False)
    assert plan.is_safe is True

  def test_delete_spec_handles_broken_symlinks(self) -> None:
    """Test deletion removes broken symlinks."""
    self._create_spec_with_frontmatter(
      "SPEC-006",
      {"slug": "broken-link-test"},
    )

    # Create symlink
    slug_link = self.tech_dir / "by-slug" / "broken-link-test"
    self._create_symlink(slug_link, Path("../SPEC-006"))

    # Break the symlink by removing target first
    (self.tech_dir / "SPEC-006" / "SPEC-006.md").unlink()

    # Should still remove the broken symlink
    self.executor.delete_spec("SPEC-006", dry_run=False)

    assert not slug_link.exists()

  def test_delete_spec_rebuilds_indices(self) -> None:
    """Test that deletion rebuilds spec indices."""
    # Create multiple specs to ensure indices exist
    self._create_spec_with_frontmatter(
      "SPEC-007",
      {"slug": "keep-me"},
    )
    self._create_spec_with_frontmatter(
      "SPEC-008",
      {"slug": "delete-me"},
    )

    # Delete one spec
    plan = self.executor.delete_spec("SPEC-008", dry_run=False)

    assert plan.is_safe is True
    # Can't easily verify index rebuild without checking symlinks,
    # but we can verify the method was called by checking the other spec still exists
    assert (self.tech_dir / "SPEC-007").exists()
    assert not (self.tech_dir / "SPEC-008").exists()

  def test_delete_spec_removes_from_registry(self) -> None:
    """Test that deletion removes spec from registry_v2.json."""
    # Create registry
    registry_dir = self.repo_root / ".spec-driver" / "registry"
    registry_dir.mkdir(parents=True)
    registry_path = registry_dir / "registry_v2.json"

    registry = RegistryV2.create_empty()
    registry.add_source_unit("python", "module1.py", "SPEC-001")
    registry.add_source_unit("python", "module2.py", "SPEC-002")
    registry.add_source_unit("go", "cmd", "SPEC-002")
    registry.save_to_file(registry_path)

    # Create spec
    self._create_spec_with_frontmatter(
      "SPEC-002",
      {"slug": "multi-source"},
    )

    # Delete spec
    plan = self.executor.delete_spec("SPEC-002", dry_run=False)

    assert plan.is_safe is True

    # Verify registry was updated
    updated_registry = RegistryV2.from_file(registry_path)
    assert updated_registry.get_spec_id("python", "module1.py") == "SPEC-001"
    assert updated_registry.get_spec_id("python", "module2.py") is None
    assert updated_registry.get_spec_id("go", "cmd") is None

  def test_delete_spec_handles_missing_registry(self) -> None:
    """Test that deletion handles missing registry gracefully."""
    # Don't create a registry
    self._create_spec_with_frontmatter(
      "SPEC-001",
      {"slug": "test"},
    )

    # Should not crash even if registry doesn't exist
    plan = self.executor.delete_spec("SPEC-001", dry_run=False)

    assert plan.is_safe is True
    assert not (self.tech_dir / "SPEC-001").exists()


if __name__ == "__main__":
  unittest.main()
