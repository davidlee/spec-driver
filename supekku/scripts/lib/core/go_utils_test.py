"""Tests for Go toolchain utilities."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from .go_utils import (
  GoToolchainError,
  get_go_module_name,
  is_go_available,
  normalize_go_package,
  run_go_list,
)


class TestIsGoAvailable:
  """Test is_go_available function."""

  def test_go_available(self) -> None:
    """Test when Go is available in PATH."""
    with patch("supekku.scripts.lib.core.go_utils.which") as mock_which:
      mock_which.return_value = "/usr/bin/go"
      assert is_go_available() is True
      mock_which.assert_called_once_with("go")

  def test_go_not_available(self) -> None:
    """Test when Go is not in PATH."""
    with patch("supekku.scripts.lib.core.go_utils.which") as mock_which:
      mock_which.return_value = None
      assert is_go_available() is False
      mock_which.assert_called_once_with("go")


class TestGetGoModuleName:
  """Test get_go_module_name function."""

  def test_successful_module_read(self) -> None:
    """Test successful reading of Go module name."""
    repo_root = Path("/repo")
    mock_result = MagicMock()
    mock_result.stdout = "github.com/user/repo\n"

    with patch("supekku.scripts.lib.core.go_utils.subprocess.run") as mock_run:
      mock_run.return_value = mock_result

      result = get_go_module_name(repo_root)

      assert result == "github.com/user/repo"
      mock_run.assert_called_once_with(
        ["go", "list", "-m"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
      )

  def test_strips_whitespace(self) -> None:
    """Test that module name is stripped of whitespace."""
    repo_root = Path("/repo")
    mock_result = MagicMock()
    mock_result.stdout = "  github.com/user/repo  \n  "

    with patch("supekku.scripts.lib.core.go_utils.subprocess.run") as mock_run:
      mock_run.return_value = mock_result

      result = get_go_module_name(repo_root)

      assert result == "github.com/user/repo"

  def test_go_command_failure(self) -> None:
    """Test error handling when go list -m fails."""
    repo_root = Path("/repo")
    stderr = "go: no go.mod file found"

    with patch("supekku.scripts.lib.core.go_utils.subprocess.run") as mock_run:
      mock_run.side_effect = subprocess.CalledProcessError(
        1,
        ["go", "list", "-m"],
        stderr=stderr,
      )

      with pytest.raises(GoToolchainError, match="Failed to read Go module name"):
        get_go_module_name(repo_root)


class TestRunGoList:
  """Test run_go_list function."""

  def test_default_pattern(self) -> None:
    """Test go list with default pattern."""
    repo_root = Path("/repo")
    mock_result = MagicMock()
    mock_result.stdout = "github.com/user/repo\ngithub.com/user/repo/internal/foo\n"

    with patch("supekku.scripts.lib.core.go_utils.subprocess.run") as mock_run:
      mock_run.return_value = mock_result

      result = run_go_list(repo_root)

      assert result == [
        "github.com/user/repo",
        "github.com/user/repo/internal/foo",
      ]
      mock_run.assert_called_once_with(
        ["go", "list", "./..."],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
      )

  def test_custom_pattern(self) -> None:
    """Test go list with custom pattern."""
    repo_root = Path("/repo")
    mock_result = MagicMock()
    mock_result.stdout = "github.com/user/repo/internal/foo\n"

    with patch("supekku.scripts.lib.core.go_utils.subprocess.run") as mock_run:
      mock_run.return_value = mock_result

      result = run_go_list(repo_root, "./internal/...")

      assert result == ["github.com/user/repo/internal/foo"]
      mock_run.assert_called_once_with(
        ["go", "list", "./internal/..."],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
      )

  def test_empty_result(self) -> None:
    """Test go list with no matching packages."""
    repo_root = Path("/repo")
    mock_result = MagicMock()
    mock_result.stdout = ""

    with patch("supekku.scripts.lib.core.go_utils.subprocess.run") as mock_run:
      mock_run.return_value = mock_result

      result = run_go_list(repo_root)

      assert result == []

  def test_go_list_failure(self) -> None:
    """Test error handling when go list fails."""
    repo_root = Path("/repo")
    stderr = "package ./... matched no packages"

    with patch("supekku.scripts.lib.core.go_utils.subprocess.run") as mock_run:
      mock_run.side_effect = subprocess.CalledProcessError(
        1,
        ["go", "list", "./..."],
        stderr=stderr,
      )

      with pytest.raises(GoToolchainError, match="Failed to list Go packages"):
        run_go_list(repo_root)


class TestNormalizeGoPackage:
  """Test normalize_go_package function."""

  def test_absolute_package_normalization(self) -> None:
    """Test converting absolute package to relative."""
    pkg = "github.com/user/repo/internal/foo"
    module = "github.com/user/repo"

    result = normalize_go_package(pkg, module)

    assert result == "internal/foo"

  def test_already_relative_package(self) -> None:
    """Test package that is already relative."""
    pkg = "internal/foo"
    module = "github.com/user/repo"

    result = normalize_go_package(pkg, module)

    assert result == "internal/foo"

  def test_root_package(self) -> None:
    """Test root package (module itself)."""
    pkg = "github.com/user/repo"
    module = "github.com/user/repo"

    result = normalize_go_package(pkg, module)

    assert result == "github.com/user/repo"

  def test_nested_package(self) -> None:
    """Test deeply nested package."""
    pkg = "github.com/user/repo/internal/foo/bar/baz"
    module = "github.com/user/repo"

    result = normalize_go_package(pkg, module)

    assert result == "internal/foo/bar/baz"

  def test_different_module(self) -> None:
    """Test package from different module (no normalization)."""
    pkg = "github.com/other/repo/pkg"
    module = "github.com/user/repo"

    result = normalize_go_package(pkg, module)

    assert result == "github.com/other/repo/pkg"

  def test_module_prefix_substring(self) -> None:
    """Test that module must be prefix with slash, not just substring."""
    pkg = "github.com/user/repo-extra/pkg"
    module = "github.com/user/repo"

    result = normalize_go_package(pkg, module)

    # Should NOT normalize because "repo-extra" != "repo"
    assert result == "github.com/user/repo-extra/pkg"
