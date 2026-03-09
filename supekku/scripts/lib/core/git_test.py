"""Tests for git integration utilities."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from .git import DEFAULT_SHORT_SHA_LENGTH, SHA_HEX_PATTERN, get_head_sha, short_sha

SAMPLE_SHA = "a" * 40


class TestGetHeadSha:
  """Tests for get_head_sha()."""

  def test_returns_sha_on_success(self) -> None:
    with patch("supekku.scripts.lib.core.git.subprocess.run") as mock_run:
      mock_run.return_value = subprocess.CompletedProcess(
        args=[], returncode=0, stdout=f"{SAMPLE_SHA}\n",
      )
      result = get_head_sha()

    assert result == SAMPLE_SHA

  def test_strips_whitespace(self) -> None:
    with patch("supekku.scripts.lib.core.git.subprocess.run") as mock_run:
      mock_run.return_value = subprocess.CompletedProcess(
        args=[], returncode=0, stdout=f"  {SAMPLE_SHA}  \n",
      )
      assert get_head_sha() == SAMPLE_SHA

  def test_returns_none_on_nonzero_exit(self) -> None:
    with patch("supekku.scripts.lib.core.git.subprocess.run") as mock_run:
      mock_run.return_value = subprocess.CompletedProcess(
        args=[], returncode=128, stdout="", stderr="not a git repo",
      )
      assert get_head_sha() is None

  def test_returns_none_when_git_not_found(self) -> None:
    with patch("supekku.scripts.lib.core.git.subprocess.run") as mock_run:
      mock_run.side_effect = FileNotFoundError("git")
      assert get_head_sha() is None

  def test_returns_none_on_timeout(self) -> None:
    with patch("supekku.scripts.lib.core.git.subprocess.run") as mock_run:
      mock_run.side_effect = subprocess.TimeoutExpired("git", 5)
      assert get_head_sha() is None

  def test_passes_root_as_cwd(self) -> None:
    root = Path("/some/repo")
    with patch("supekku.scripts.lib.core.git.subprocess.run") as mock_run:
      mock_run.return_value = subprocess.CompletedProcess(
        args=[], returncode=0, stdout=f"{SAMPLE_SHA}\n",
      )
      get_head_sha(root)

    _, kwargs = mock_run.call_args
    assert kwargs["cwd"] == root

  def test_defaults_to_none_cwd(self) -> None:
    with patch("supekku.scripts.lib.core.git.subprocess.run") as mock_run:
      mock_run.return_value = subprocess.CompletedProcess(
        args=[], returncode=0, stdout=f"{SAMPLE_SHA}\n",
      )
      get_head_sha()

    _, kwargs = mock_run.call_args
    assert kwargs["cwd"] is None

  def test_integration_returns_real_sha(self) -> None:
    """Integration test: get_head_sha returns a valid SHA in this repo."""
    sha = get_head_sha()
    # We're in a git repo, so this should succeed
    assert sha is not None
    assert re.match(SHA_HEX_PATTERN, sha)


class TestShortSha:
  """Tests for short_sha()."""

  def test_default_length(self) -> None:
    assert short_sha(SAMPLE_SHA) == "a" * DEFAULT_SHORT_SHA_LENGTH

  def test_custom_length(self) -> None:
    assert short_sha(SAMPLE_SHA, length=12) == "a" * 12

  def test_length_one(self) -> None:
    assert short_sha(SAMPLE_SHA, length=1) == "a"

  def test_full_length(self) -> None:
    assert short_sha(SAMPLE_SHA, length=40) == SAMPLE_SHA


class TestShaHexPattern:
  """Tests for SHA_HEX_PATTERN constant."""

  @pytest.mark.parametrize("sha", [
    "a" * 40,
    "0123456789abcdef" * 2 + "01234567",
    "f" * 40,
    "0" * 40,
  ])
  def test_valid_shas(self, sha: str) -> None:
    assert re.match(SHA_HEX_PATTERN, sha)

  @pytest.mark.parametrize("sha", [
    "a" * 39,       # too short
    "a" * 41,       # too long
    "a" * 7,        # way too short
    "g" * 40,       # invalid hex char
    "A" * 40,       # uppercase
    "",             # empty
    "abc123",       # short SHA (not accepted by pattern)
  ])
  def test_invalid_shas(self, sha: str) -> None:
    assert not re.match(SHA_HEX_PATTERN, sha)
