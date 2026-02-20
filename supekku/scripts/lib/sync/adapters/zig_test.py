"""Tests for Zig language adapter."""

import subprocess
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from supekku.scripts.lib.sync.models import SourceUnit

from .zig import ZigAdapter, ZigmarkdocNotAvailableError, is_zigmarkdoc_available


class TestZigAdapter(unittest.TestCase):
  """Test ZigAdapter functionality."""

  def setUp(self) -> None:
    """Set up test fixtures."""
    self.repo_root = Path("/test/repo")
    self.adapter = ZigAdapter(self.repo_root)

  def test_language_identifier(self) -> None:
    """Test that ZigAdapter has correct language identifier."""
    assert ZigAdapter.language == "zig"
    assert self.adapter.language == "zig"

  def test_supports_identifier_valid_zig_paths(self) -> None:
    """Test supports_identifier returns True for valid Zig paths."""
    valid_identifiers = [
      "src/main.zig",
      "lib/module.zig",
      "build.zig",
      "src/",
      "lib/utils",
    ]

    for identifier in valid_identifiers:
      with (
        self.subTest(identifier=identifier),
        patch("pathlib.Path.exists") as mock_exists,
      ):
        # Mock path existence and Zig file presence
        mock_exists.return_value = True
        msg = f"Should support Zig path: {identifier}"
        # supports_identifier checks file extension or directory with .zig files
        assert self.adapter.supports_identifier(identifier), msg

  def test_supports_identifier_invalid_identifiers(self) -> None:
    """Test supports_identifier returns False for non-Zig identifiers."""
    invalid_identifiers = [
      "",  # empty
      "file.py",  # Python file
      "script.js",  # JavaScript file
    ]

    for identifier in invalid_identifiers:
      with self.subTest(identifier=identifier):
        msg = f"Should not support identifier: {identifier}"
        assert not self.adapter.supports_identifier(identifier), msg

  def test_describe_zig_package(self) -> None:
    """Test describe method generates correct metadata for Zig packages."""
    unit = SourceUnit("zig", "src/utils", self.repo_root)
    descriptor = self.adapter.describe(unit)

    # Check slug parts
    assert descriptor.slug_parts == ["src", "utils"]

    # Check frontmatter has packages
    assert "packages" in descriptor.default_frontmatter
    assert descriptor.default_frontmatter["packages"] == ["src/utils"]

    # Check new sources structure
    assert "sources" in descriptor.default_frontmatter
    sources = descriptor.default_frontmatter["sources"]
    assert len(sources) == 1
    assert sources[0]["language"] == "zig"
    assert sources[0]["identifier"] == "src/utils"

    # Check variants
    assert len(descriptor.variants) == 2
    variant_names = [v.name for v in descriptor.variants]
    assert "public" in variant_names
    assert "internal" in variant_names

    # Check variant paths
    public_variant = next(v for v in descriptor.variants if v.name == "public")
    internal_variant = next(v for v in descriptor.variants if v.name == "internal")

    assert public_variant.path == Path("contracts/interfaces.md")
    assert internal_variant.path == Path("contracts/internals.md")

  def test_describe_rejects_non_zig_unit(self) -> None:
    """Test describe method rejects non-Zig source units."""
    unit = SourceUnit("python", "some/module.py", self.repo_root)

    with pytest.raises(ValueError) as context:
      self.adapter.describe(unit)

    assert "ZigAdapter cannot process python units" in str(context.value)

  def test_generate_rejects_non_zig_unit(self) -> None:
    """Test generate method rejects non-Zig source units."""
    unit = SourceUnit("python", "some/module.py", self.repo_root)
    spec_dir = Path("/test/spec/SPEC-001")

    with pytest.raises(ValueError) as context:
      self.adapter.generate(unit, spec_dir=spec_dir)

    assert "ZigAdapter cannot process python units" in str(context.value)

  @patch("supekku.scripts.lib.sync.adapters.zig.is_zigmarkdoc_available")
  @patch("subprocess.run")
  @patch("pathlib.Path.read_text")
  @patch("pathlib.Path.exists")
  @patch("pathlib.Path.is_file")
  @patch("pathlib.Path.mkdir")
  def test_generate_creates_variants(
    self,
    _mock_mkdir,
    mock_is_file,
    mock_exists,
    mock_read_text,
    mock_subprocess,
    mock_is_zigmarkdoc,
  ) -> None:
    """Test generate method creates documentation variants."""
    # Setup mocks
    mock_is_zigmarkdoc.return_value = True
    mock_exists.return_value = True
    mock_is_file.return_value = True  # Source path is a file
    mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")

    # Mock file content for hash calculation
    mock_read_text.return_value = "# Documentation content"

    unit = SourceUnit("zig", "src/test.zig", self.repo_root)
    spec_dir = Path("/test/spec/SPEC-001")
    variants = self.adapter.generate(unit, spec_dir=spec_dir)

    # Should generate two variants
    assert len(variants) == 2

    variant_names = [v.name for v in variants]
    assert "public" in variant_names
    assert "internal" in variant_names

    # Check that zigmarkdoc was called twice (public + internal)
    assert mock_subprocess.call_count == 2

  @patch("supekku.scripts.lib.sync.adapters.zig.is_zigmarkdoc_available")
  @patch("subprocess.run")
  @patch("pathlib.Path.exists")
  @patch("pathlib.Path.is_file")
  @patch("pathlib.Path.mkdir")
  def test_generate_check_mode(
    self,
    _mock_mkdir,
    mock_is_file,
    mock_exists,
    mock_subprocess,
    mock_is_zigmarkdoc,
  ) -> None:
    """Test generate method in check mode."""
    # Setup: files exist and zigmarkdoc check passes
    mock_is_zigmarkdoc.return_value = True
    mock_exists.return_value = True
    mock_is_file.return_value = True  # Source path is a file
    mock_subprocess.return_value = Mock(returncode=0)  # Check passes

    unit = SourceUnit("zig", "src/test.zig", self.repo_root)
    spec_dir = Path("/test/spec/SPEC-001")
    variants = self.adapter.generate(unit, spec_dir=spec_dir, check=True)

    # Should check both variants
    assert len(variants) == 2

    # All variants should be unchanged (check passed)
    for variant in variants:
      assert variant.status == "unchanged"

    # Should have called zigmarkdoc with --check
    assert mock_subprocess.call_count == 2
    for call in mock_subprocess.call_args_list:
      args = call[0][0]  # First positional argument (command list)
      assert "--check" in args

  @patch("supekku.scripts.lib.sync.adapters.zig.is_zigmarkdoc_available")
  @patch("subprocess.run")
  @patch("pathlib.Path.exists")
  @patch("pathlib.Path.is_file")
  @patch("pathlib.Path.mkdir")
  def test_generate_check_mode_detects_changes(
    self,
    _mock_mkdir,
    mock_is_file,
    mock_exists,
    mock_subprocess,
    mock_is_zigmarkdoc,
  ) -> None:
    """Test generate method in check mode detects changes."""
    # Setup: files exist but zigmarkdoc check fails (content changed)
    mock_is_zigmarkdoc.return_value = True
    mock_exists.return_value = True
    mock_is_file.return_value = True  # Source path is a file

    def subprocess_side_effect(*args, **_kwargs):
      # First call succeeds, second fails
      if "--include-private" in args[0]:
        # Internal variant check fails
        raise subprocess.CalledProcessError(1, args[0])
      # Public variant check succeeds
      return Mock(returncode=0)

    mock_subprocess.side_effect = subprocess_side_effect

    unit = SourceUnit("zig", "src/test.zig", self.repo_root)
    spec_dir = Path("/test/spec/SPEC-001")
    variants = self.adapter.generate(unit, spec_dir=spec_dir, check=True)

    # Should check both variants
    assert len(variants) == 2

    # First variant unchanged, second changed
    assert variants[0].status == "unchanged"
    assert variants[1].status == "changed"

  @patch("supekku.scripts.lib.sync.adapters.zig.is_zigmarkdoc_available")
  @patch("subprocess.run")
  @patch("pathlib.Path.read_text")
  @patch("pathlib.Path.exists")
  @patch("pathlib.Path.is_file")
  @patch("pathlib.Path.mkdir")
  def test_generate_with_include_private_flag(
    self,
    _mock_mkdir,
    mock_is_file,
    mock_exists,
    mock_read_text,
    mock_subprocess,
    mock_is_zigmarkdoc,
  ) -> None:
    """Test generate calls zigmarkdoc with --include-private."""
    mock_is_zigmarkdoc.return_value = True
    mock_exists.return_value = True
    mock_is_file.return_value = True  # Source path is a file
    mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")
    mock_read_text.return_value = "# Documentation content"

    unit = SourceUnit("zig", "src/test.zig", self.repo_root)
    spec_dir = Path("/test/spec/SPEC-001")
    self.adapter.generate(unit, spec_dir=spec_dir)

    # Check that second call (internal variant) has --include-private
    assert mock_subprocess.call_count == 2
    second_call_args = mock_subprocess.call_args_list[1][0][0]
    assert "--include-private" in second_call_args

  @patch("supekku.scripts.lib.sync.adapters.zig.is_zigmarkdoc_available")
  def test_generate_raises_when_zigmarkdoc_not_available(
    self,
    mock_is_zigmarkdoc,
  ) -> None:
    """Test generate raises error when zigmarkdoc is not available."""
    mock_is_zigmarkdoc.return_value = False

    unit = SourceUnit("zig", "src/test.zig", self.repo_root)
    spec_dir = Path("/test/spec/SPEC-001")

    with pytest.raises(ZigmarkdocNotAvailableError) as context:
      self.adapter.generate(unit, spec_dir=spec_dir)

    assert "zigmarkdoc not found in PATH" in str(context.value)
    assert "https://github.com/davidlee/zigmarkdoc" in str(context.value)

  @patch("supekku.scripts.lib.sync.adapters.zig.is_zigmarkdoc_available")
  @patch("pathlib.Path.exists")
  def test_generate_raises_when_source_not_exists(
    self,
    mock_exists,
    mock_is_zigmarkdoc,
  ) -> None:
    """Test generate raises FileNotFoundError when source path doesn't exist."""
    mock_is_zigmarkdoc.return_value = True
    mock_exists.return_value = False

    unit = SourceUnit("zig", "src/nonexistent.zig", self.repo_root)
    spec_dir = Path("/test/spec/SPEC-001")

    with pytest.raises(FileNotFoundError) as context:
      self.adapter.generate(unit, spec_dir=spec_dir)

    assert "Source path does not exist" in str(context.value)

  def test_is_zigmarkdoc_available(self) -> None:
    """Test is_zigmarkdoc_available correctly detects zigmarkdoc presence."""
    with patch("supekku.scripts.lib.sync.adapters.zig.which") as mock_which:
      # Test when zigmarkdoc is available
      mock_which.return_value = "/usr/local/bin/zigmarkdoc"
      assert is_zigmarkdoc_available()

      # Test when zigmarkdoc is not available
      mock_which.return_value = None
      assert not is_zigmarkdoc_available()


if __name__ == "__main__":
  unittest.main()
