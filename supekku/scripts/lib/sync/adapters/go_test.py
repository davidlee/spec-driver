"""Tests for Go language adapter."""

import subprocess
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from supekku.scripts.lib.sync.models import SourceUnit

from .go import GoAdapter, GomarkdocNotAvailableError, GoToolchainNotAvailableError


class TestGoAdapter(unittest.TestCase):
  """Test GoAdapter functionality."""

  def setUp(self) -> None:
    """Set up test fixtures."""
    self.repo_root = Path("/test/repo")
    self.adapter = GoAdapter(self.repo_root)

  def test_language_identifier(self) -> None:
    """Test that GoAdapter has correct language identifier."""
    assert GoAdapter.language == "go"
    assert self.adapter.language == "go"

  def test_supports_identifier_valid_go_packages(self) -> None:
    """Test supports_identifier returns True for valid Go package paths."""
    valid_identifiers = [
      "cmd/vice",
      "internal/application/pipeline",
      "pkg/utils",
      "test/helpers",
      "tools/generator",
      "simple",
      "github.com/user/repo/pkg",
      "module/sub-package",
      "module/sub_package",
    ]

    for identifier in valid_identifiers:
      with self.subTest(identifier=identifier):
        msg = f"Should support Go package: {identifier}"
        assert self.adapter.supports_identifier(identifier), msg

  def test_supports_identifier_invalid_identifiers(self) -> None:
    """Test supports_identifier returns False for non-Go identifiers."""
    invalid_identifiers = [
      "",  # empty
      "file.go",  # file extension
      "module.py",  # Python file
      "script.js",  # JavaScript file
      "package with spaces",  # spaces
      "package\twith\ttabs",  # tabs
      "package\nwith\nnewlines",  # newlines
    ]

    for identifier in invalid_identifiers:
      with self.subTest(identifier=identifier):
        msg = f"Should not support identifier: {identifier}"
        assert not self.adapter.supports_identifier(identifier), msg

  def test_describe_go_package(self) -> None:
    """Test describe method generates correct metadata for Go packages."""
    unit = SourceUnit(
      language="go", identifier="internal/application/pipeline", root=self.repo_root
    )
    descriptor = self.adapter.describe(unit)

    # Check slug parts
    assert descriptor.slug_parts == ["internal", "application", "pipeline"]

    # Check frontmatter has packages for compatibility
    assert "packages" in descriptor.default_frontmatter
    assert descriptor.default_frontmatter["packages"] == [
      "internal/application/pipeline",
    ]

    # Check new sources structure
    assert "sources" in descriptor.default_frontmatter
    sources = descriptor.default_frontmatter["sources"]
    assert len(sources) == 1
    assert sources[0]["language"] == "go"
    assert sources[0]["identifier"] == "internal/application/pipeline"

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

  def test_describe_rejects_non_go_unit(self) -> None:
    """Test describe method rejects non-Go source units."""
    unit = SourceUnit(
      language="python", identifier="some/module.py", root=self.repo_root
    )

    with pytest.raises(ValueError) as context:
      self.adapter.describe(unit)

    assert "GoAdapter cannot process python units" in str(context.value)

  def test_generate_rejects_non_go_unit(self) -> None:
    """Test generate method rejects non-Go source units."""
    unit = SourceUnit(
      language="python", identifier="some/module.py", root=self.repo_root
    )
    variant_outputs = {
      "public": Path("/test/output/public/interfaces.md"),
      "internal": Path("/test/output/internal/internals.md"),
    }

    with pytest.raises(ValueError) as context:
      self.adapter.generate(unit, variant_outputs=variant_outputs)

    assert "GoAdapter cannot process python units" in str(context.value)

  @patch("supekku.scripts.lib.sync.adapters.go.is_go_available")
  @patch("supekku.scripts.lib.sync.adapters.go.which")
  @patch("subprocess.run")
  @patch("pathlib.Path.read_text")
  @patch("pathlib.Path.exists")
  @patch("pathlib.Path.mkdir")
  def test_generate_creates_variants(
    self,
    _mock_mkdir,
    mock_exists,
    mock_read_text,
    mock_subprocess,
    mock_which,
    mock_is_go,
  ) -> None:
    """Test generate method creates documentation variants."""
    mock_is_go.return_value = True
    mock_which.return_value = "/usr/bin/go"
    mock_exists.return_value = True
    mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")
    mock_read_text.return_value = "# Documentation content"

    unit = SourceUnit(language="go", identifier="internal/test", root=self.repo_root)
    variant_outputs = {
      "public": Path("/test/output/public/internal/test/interfaces.md"),
      "internal": Path("/test/output/internal/internal/test/internals.md"),
    }
    variants = self.adapter.generate(unit, variant_outputs=variant_outputs)

    assert len(variants) == 2
    variant_names = [v.name for v in variants]
    assert "public" in variant_names
    assert "internal" in variant_names

    # gomarkdoc called twice (public + internal)
    assert mock_subprocess.call_count == 2

    # Verify ./-prefixed relative path and cwd=repo_root
    for call in mock_subprocess.call_args_list:
      cmd = call[0][0]
      assert cmd[-1] == "./internal/test", f"Expected ./prefix path, got {cmd[-1]}"
      assert call[1].get("cwd") == self.repo_root

  @patch("supekku.scripts.lib.sync.adapters.go.is_go_available")
  @patch("supekku.scripts.lib.sync.adapters.go.which")
  @patch("subprocess.run")
  @patch("pathlib.Path.exists")
  @patch("pathlib.Path.mkdir")
  def test_generate_check_mode(
    self,
    _mock_mkdir,
    mock_exists,
    mock_subprocess,
    mock_which,
    mock_is_go,
  ) -> None:
    """Test generate method in check mode."""
    mock_is_go.return_value = True
    mock_which.return_value = "/usr/bin/go"
    mock_exists.return_value = True
    mock_subprocess.return_value = Mock(returncode=0)

    unit = SourceUnit(language="go", identifier="internal/test", root=self.repo_root)
    variant_outputs = {
      "public": Path("/test/output/public/internal/test/interfaces.md"),
      "internal": Path("/test/output/internal/internal/test/internals.md"),
    }
    variants = self.adapter.generate(
      unit,
      variant_outputs=variant_outputs,
      check=True,
    )

    assert len(variants) == 2
    for variant in variants:
      assert variant.status == "unchanged"

    assert mock_subprocess.call_count == 2
    for call in mock_subprocess.call_args_list:
      cmd = call[0][0]
      assert "--check" in cmd
      assert cmd[-1] == "./internal/test"
      assert call[1].get("cwd") == self.repo_root

  @patch("supekku.scripts.lib.sync.adapters.go.is_go_available")
  def test_discover_targets_raises_when_go_not_available(
    self,
    mock_is_go,
  ) -> None:
    """Test discover_targets raises error when Go toolchain is not available."""
    # Mock Go not being available
    mock_is_go.return_value = False

    with pytest.raises(GoToolchainNotAvailableError) as context:
      self.adapter.discover_targets(self.repo_root)

    assert "Go toolchain not found in PATH" in str(context.value)
    assert "https://go.dev/dl/" in str(context.value)

  @patch("supekku.scripts.lib.sync.adapters.go.is_go_available")
  def test_generate_raises_when_go_not_available(
    self,
    mock_is_go,
  ) -> None:
    """Test generate raises error when Go toolchain is not available."""
    # Mock Go not being available
    mock_is_go.return_value = False

    unit = SourceUnit(language="go", identifier="internal/test", root=self.repo_root)
    variant_outputs = {
      "public": Path("/test/output/public/interfaces.md"),
      "internal": Path("/test/output/internal/internals.md"),
    }

    with pytest.raises(GoToolchainNotAvailableError) as context:
      self.adapter.generate(unit, variant_outputs=variant_outputs)

    assert "Go toolchain not found in PATH" in str(context.value)
    assert "https://go.dev/dl/" in str(context.value)

  def test_is_go_available(self) -> None:
    """Test is_go_available correctly detects Go presence."""
    with patch("supekku.scripts.lib.sync.adapters.go.is_go_available") as mock_is_go:
      # Test when Go is available
      mock_is_go.return_value = True
      assert mock_is_go()

      # Test when Go is not available
      mock_is_go.return_value = False
      assert not mock_is_go()

  def test_is_gomarkdoc_available(self) -> None:
    """Test is_gomarkdoc_available correctly detects gomarkdoc presence."""
    with patch("supekku.scripts.lib.sync.adapters.go.which") as mock_which:
      # Test when gomarkdoc is available
      mock_which.return_value = "/go/bin/gomarkdoc"
      assert GoAdapter.is_gomarkdoc_available()

      # Test when gomarkdoc is not available
      mock_which.return_value = None
      assert not GoAdapter.is_gomarkdoc_available()

  @patch("supekku.scripts.lib.sync.adapters.go.is_go_available")
  @patch("supekku.scripts.lib.sync.adapters.go.which")
  def test_generate_raises_when_gomarkdoc_not_available(
    self,
    mock_which,
    mock_is_go,
  ) -> None:
    """Test generate raises error when gomarkdoc is not available."""
    mock_is_go.return_value = True

    def which_side_effect(cmd: str) -> str | None:
      if cmd == "go":
        return "/usr/bin/go"
      if cmd == "gomarkdoc":
        return None
      return None

    mock_which.side_effect = which_side_effect

    unit = SourceUnit(language="go", identifier="internal/test", root=self.repo_root)
    variant_outputs = {
      "public": Path("/test/output/public/interfaces.md"),
      "internal": Path("/test/output/internal/internals.md"),
    }

    with pytest.raises(GomarkdocNotAvailableError) as context:
      self.adapter.generate(unit, variant_outputs=variant_outputs)

    assert "gomarkdoc not found in PATH" in str(context.value)
    assert "go install github.com/princjef/gomarkdoc" in str(context.value)

  @patch("supekku.scripts.lib.sync.adapters.go.is_go_available")
  @patch("supekku.scripts.lib.sync.adapters.go.which")
  @patch("subprocess.run")
  @patch("pathlib.Path.exists")
  @patch("pathlib.Path.mkdir")
  def test_generate_propagates_gomarkdoc_error(
    self,
    _mock_mkdir,
    mock_exists,
    mock_subprocess,
    mock_which,
    mock_is_go,
  ) -> None:
    """Test generate propagates CalledProcessError instead of swallowing it."""
    mock_is_go.return_value = True
    mock_which.return_value = "/usr/bin/gomarkdoc"
    mock_exists.return_value = False
    mock_subprocess.side_effect = subprocess.CalledProcessError(
      1,
      ["gomarkdoc"],
      stderr="invalid package",
    )

    unit = SourceUnit(language="go", identifier="bad/pkg", root=self.repo_root)
    variant_outputs = {
      "public": Path("/test/output/public.md"),
      "internal": Path("/test/output/internal.md"),
    }

    with pytest.raises(RuntimeError, match="gomarkdoc failed"):
      self.adapter.generate(unit, variant_outputs=variant_outputs)


if __name__ == "__main__":
  unittest.main()
