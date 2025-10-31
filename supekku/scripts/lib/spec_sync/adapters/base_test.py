"""Tests for base language adapter."""

import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from supekku.scripts.lib.spec_sync.models import SourceDescriptor, SourceUnit

from .base import LanguageAdapter


class ConcreteAdapter(LanguageAdapter):
  """Concrete implementation for testing abstract base class."""

  language = "test"

  def discover_targets(self, repo_root, requested=None):
    """Stub implementation."""
    return []

  def describe(self, unit):
    """Stub implementation."""
    return SourceDescriptor(
      slug_parts=["test"],
      default_frontmatter={},
      variants=[],
    )

  def generate(self, unit, *, spec_dir, check=False):
    """Stub implementation."""
    return []

  def supports_identifier(self, identifier):
    """Stub implementation."""
    return True


class TestLanguageAdapterValidation(unittest.TestCase):
  """Test LanguageAdapter validation methods."""

  def setUp(self) -> None:
    """Set up test fixtures."""
    self.temp_dir = TemporaryDirectory()
    self.repo_root = Path(self.temp_dir.name)
    self.adapter = ConcreteAdapter(self.repo_root)

  def tearDown(self) -> None:
    """Clean up test fixtures."""
    self.temp_dir.cleanup()

  def test_validate_source_exists_file_exists_git_tracked(self) -> None:
    """Test validation when file exists and is git-tracked."""
    # Create a test file
    test_file = self.repo_root / "test_module.py"
    test_file.write_text("# test")

    unit = SourceUnit("test", "test_module.py", self.repo_root)

    # Mock git tracking
    with patch.object(
      self.adapter,
      "_get_git_tracked_files",
      return_value={test_file.resolve()},
    ):
      result = self.adapter.validate_source_exists(unit)

    assert result["exists"] is True
    assert result["git_tracked"] is True
    assert result["status"] == "valid"
    assert "valid" in result["message"].lower()

  def test_validate_source_exists_file_missing(self) -> None:
    """Test validation when source file doesn't exist."""
    unit = SourceUnit("test", "nonexistent.py", self.repo_root)

    result = self.adapter.validate_source_exists(unit)

    assert result["exists"] is False
    assert result["git_tracked"] is None
    assert result["status"] == "missing"
    assert "not found" in result["message"].lower()

  def test_validate_source_exists_file_exists_not_tracked(self) -> None:
    """Test validation when file exists but not git-tracked."""
    # Create a test file
    test_file = self.repo_root / "untracked.py"
    test_file.write_text("# untracked")

    unit = SourceUnit("test", "untracked.py", self.repo_root)

    # Mock git tracking - file not in tracked set
    other_file = Path("/other/file.py")
    with patch.object(
      self.adapter,
      "_get_git_tracked_files",
      return_value={other_file},
    ):
      result = self.adapter.validate_source_exists(unit)

    assert result["exists"] is True
    assert result["git_tracked"] is False
    assert result["status"] == "untracked"
    assert "not git-tracked" in result["message"].lower()

  def test_validate_source_exists_no_git_available(self) -> None:
    """Test validation when git is not available."""
    # Create a test file
    test_file = self.repo_root / "module.py"
    test_file.write_text("# module")

    unit = SourceUnit("test", "module.py", self.repo_root)

    # Mock git not available (empty tracked files set)
    with patch.object(self.adapter, "_get_git_tracked_files", return_value=set()):
      result = self.adapter.validate_source_exists(unit)

    # Should still pass if file exists, even without git
    assert result["exists"] is True
    assert result["git_tracked"] is None
    assert result["status"] == "valid"

  def test_validate_source_exists_nested_path(self) -> None:
    """Test validation with nested directory structure."""
    # Create nested directory and file
    nested_dir = self.repo_root / "lib" / "utils"
    nested_dir.mkdir(parents=True)
    nested_file = nested_dir / "helper.py"
    nested_file.write_text("# helper")

    unit = SourceUnit("test", "lib/utils/helper.py", self.repo_root)

    # Mock git tracking
    with patch.object(
      self.adapter,
      "_get_git_tracked_files",
      return_value={nested_file.resolve()},
    ):
      result = self.adapter.validate_source_exists(unit)

    assert result["exists"] is True
    assert result["git_tracked"] is True
    assert result["status"] == "valid"

  def test_validate_source_exists_cannot_determine_path(self) -> None:
    """Test validation when source path cannot be determined."""
    unit = SourceUnit("test", "test.py", self.repo_root)

    # Override _get_source_path to return None
    with patch.object(self.adapter, "_get_source_path", return_value=None):
      result = self.adapter.validate_source_exists(unit)

    assert result["exists"] is False
    assert result["git_tracked"] is None
    assert result["status"] == "missing"
    assert "cannot determine" in result["message"].lower()

  def test_get_source_path_default_implementation(self) -> None:
    """Test default _get_source_path implementation."""
    unit = SourceUnit("test", "module.py", self.repo_root)

    path = self.adapter._get_source_path(unit)

    assert path == self.repo_root / "module.py"

  def test_get_source_path_nested(self) -> None:
    """Test _get_source_path with nested identifier."""
    unit = SourceUnit("test", "lib/utils/helper.py", self.repo_root)

    path = self.adapter._get_source_path(unit)

    assert path == self.repo_root / "lib" / "utils" / "helper.py"


class TestLanguageAdapterGitTracking(unittest.TestCase):
  """Test LanguageAdapter git tracking functionality."""

  def setUp(self) -> None:
    """Set up test fixtures."""
    self.temp_dir = TemporaryDirectory()
    self.repo_root = Path(self.temp_dir.name)
    self.adapter = ConcreteAdapter(self.repo_root)

  def tearDown(self) -> None:
    """Clean up test fixtures."""
    self.temp_dir.cleanup()

  def test_get_git_tracked_files_caches_results(self) -> None:
    """Test that git tracked files are cached."""
    mock_run = Mock()
    mock_run.stdout = "file1.py\nfile2.py\n"

    with patch("subprocess.run", return_value=mock_run):
      # First call
      files1 = self.adapter._get_git_tracked_files()
      # Second call
      files2 = self.adapter._get_git_tracked_files()

      # Should only call git once
      assert subprocess.run.call_count == 1
      # Results should be identical
      assert files1 is files2

  def test_get_git_tracked_files_success(self) -> None:
    """Test getting git tracked files successfully."""
    mock_run = Mock()
    mock_run.stdout = "file1.py\nlib/file2.py\ntest/file3.py\n"

    with (
      patch("subprocess.run", return_value=mock_run),
      patch("shutil.which", return_value="/usr/bin/git"),
    ):
      files = self.adapter._get_git_tracked_files()

    assert len(files) == 3
    assert self.repo_root / "file1.py" in files
    assert self.repo_root / "lib" / "file2.py" in files
    assert self.repo_root / "test" / "file3.py" in files

  def test_get_git_tracked_files_no_git(self) -> None:
    """Test when git is not available."""
    with patch("shutil.which", return_value=None):
      files = self.adapter._get_git_tracked_files()

    assert len(files) == 0

  def test_get_git_tracked_files_git_error(self) -> None:
    """Test handling git command errors."""
    with (
      patch("shutil.which", return_value="/usr/bin/git"),
      patch(
        "subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "git"),
      ),
    ):
      files = self.adapter._get_git_tracked_files()

    assert len(files) == 0

  def test_get_git_tracked_files_timeout(self) -> None:
    """Test handling git command timeout."""
    with (
      patch("shutil.which", return_value="/usr/bin/git"),
      patch(
        "subprocess.run",
        side_effect=subprocess.TimeoutExpired("git", 30),
      ),
    ):
      files = self.adapter._get_git_tracked_files()

    assert len(files) == 0

  def test_get_git_tracked_files_empty_lines(self) -> None:
    """Test that empty lines in git output are ignored."""
    mock_run = Mock()
    mock_run.stdout = "file1.py\n\n\nfile2.py\n  \n"

    with (
      patch("subprocess.run", return_value=mock_run),
      patch("shutil.which", return_value="/usr/bin/git"),
    ):
      files = self.adapter._get_git_tracked_files()

    # Should only get the two non-empty files
    assert len(files) == 2


class TestLanguageAdapterShouldSkipPath(unittest.TestCase):
  """Test LanguageAdapter path skipping functionality."""

  def setUp(self) -> None:
    """Set up test fixtures."""
    self.temp_dir = TemporaryDirectory()
    self.repo_root = Path(self.temp_dir.name)
    self.adapter = ConcreteAdapter(self.repo_root)

  def tearDown(self) -> None:
    """Clean up test fixtures."""
    self.temp_dir.cleanup()

  def test_should_skip_symlink(self) -> None:
    """Test that symlinks are skipped."""
    # Create a file and a symlink to it
    real_file = self.repo_root / "real.py"
    real_file.write_text("# real")
    symlink = self.repo_root / "link.py"
    symlink.symlink_to(real_file)

    assert self.adapter._should_skip_path(symlink) is True
    assert self.adapter._should_skip_path(real_file) is False

  def test_should_skip_specify_directory(self) -> None:
    """Test that paths in specify/ are skipped."""
    spec_path = self.repo_root / "specify" / "tech" / "SPEC-001" / "SPEC-001.md"

    assert self.adapter._should_skip_path(spec_path) is True

  def test_should_skip_change_directory(self) -> None:
    """Test that paths in change/ are skipped."""
    change_path = self.repo_root / "change" / "deltas" / "DE-001" / "delta.yaml"

    assert self.adapter._should_skip_path(change_path) is True

  def test_should_skip_non_git_tracked(self) -> None:
    """Test that non-git-tracked files are skipped."""
    tracked_file = self.repo_root / "tracked.py"
    untracked_file = self.repo_root / "untracked.py"

    # Mock git tracking
    with patch.object(
      self.adapter,
      "_get_git_tracked_files",
      return_value={tracked_file.resolve()},
    ):
      assert self.adapter._should_skip_path(tracked_file) is False
      assert self.adapter._should_skip_path(untracked_file) is True

  def test_should_skip_no_git_does_not_skip(self) -> None:
    """Test that files are not skipped when git is unavailable."""
    test_file = self.repo_root / "test.py"

    # Mock git not available (empty set)
    with patch.object(self.adapter, "_get_git_tracked_files", return_value=set()):
      assert self.adapter._should_skip_path(test_file) is False


class TestLanguageAdapterValidateUnitLanguage(unittest.TestCase):
  """Test LanguageAdapter unit language validation."""

  def setUp(self) -> None:
    """Set up test fixtures."""
    self.repo_root = Path("/test/repo")
    self.adapter = ConcreteAdapter(self.repo_root)

  def test_validate_unit_language_matching(self) -> None:
    """Test validation passes for matching language."""
    unit = SourceUnit("test", "module.py", self.repo_root)

    # Should not raise
    self.adapter._validate_unit_language(unit)

  def test_validate_unit_language_mismatched(self) -> None:
    """Test validation fails for mismatched language."""
    unit = SourceUnit("python", "module.py", self.repo_root)

    with self.assertRaises(ValueError) as context:
      self.adapter._validate_unit_language(unit)

    assert "cannot process python units" in str(context.exception)


class TestLanguageAdapterCreateDocVariant(unittest.TestCase):
  """Test LanguageAdapter doc variant creation."""

  def setUp(self) -> None:
    """Set up test fixtures."""
    self.repo_root = Path("/test/repo")
    self.adapter = ConcreteAdapter(self.repo_root)

  def test_create_doc_variant_basic(self) -> None:
    """Test creating a basic doc variant."""
    variant = self.adapter._create_doc_variant(
      name="api",
      slug_parts=["supekku", "lib", "workspace"],
      language_subdir="python",
    )

    assert variant.name == "api"
    assert str(variant.path) == "contracts/python/supekku-lib-workspace-api.md"
    assert variant.hash == ""
    assert variant.status == "unchanged"

  def test_create_doc_variant_different_language(self) -> None:
    """Test creating doc variant for different language."""
    variant = self.adapter._create_doc_variant(
      name="public",
      slug_parts=["cmd", "vice"],
      language_subdir="go",
    )

    assert variant.name == "public"
    assert str(variant.path) == "contracts/go/cmd-vice-public.md"

  def test_create_doc_variant_single_slug_part(self) -> None:
    """Test creating doc variant with single slug part."""
    variant = self.adapter._create_doc_variant(
      name="tests",
      slug_parts=["workspace"],
      language_subdir="python",
    )

    assert str(variant.path) == "contracts/python/workspace-tests.md"


if __name__ == "__main__":
  unittest.main()
