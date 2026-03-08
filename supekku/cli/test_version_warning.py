"""Tests for version-staleness CLI warning."""

from __future__ import annotations

import io
import sys
import unittest
from unittest.mock import patch

from supekku.cli.main import _warn_if_version_stale

_VERSION_FN = "supekku.scripts.lib.core.version.get_package_version"


class TestWarnIfVersionStale(unittest.TestCase):
  """Tests for _warn_if_version_stale."""

  @patch(_VERSION_FN, return_value="1.0.0")
  def test_matching_version_no_warning(self, _mock) -> None:
    """No warning when versions match."""
    stderr = io.StringIO()
    with patch.object(sys, "stderr", stderr), patch.object(sys, "argv", ["sd", "list"]):
      _warn_if_version_stale({"spec_driver_installed_version": "1.0.0"})
    assert stderr.getvalue() == ""

  @patch(_VERSION_FN, return_value="2.0.0")
  def test_stale_version_warns(self, _mock) -> None:
    """Warning when installed version differs from running version."""
    stderr = io.StringIO()
    with patch.object(sys, "stderr", stderr), patch.object(sys, "argv", ["sd", "list"]):
      _warn_if_version_stale({"spec_driver_installed_version": "1.0.0"})
    output = stderr.getvalue()
    assert "Warning" in output
    assert "1.0.0" in output
    assert "2.0.0" in output
    assert "spec-driver install" in output

  @patch(_VERSION_FN, return_value="1.0.0")
  def test_missing_version_stamp_warns(self, _mock) -> None:
    """Warning when version key is absent from config."""
    stderr = io.StringIO()
    with patch.object(sys, "stderr", stderr), patch.object(sys, "argv", ["sd", "list"]):
      _warn_if_version_stale({})
    output = stderr.getvalue()
    assert "Warning" in output
    assert "no version stamp" in output

  @patch(_VERSION_FN, return_value="2.0.0")
  def test_install_command_suppresses_warning(self, _mock) -> None:
    """No warning when running the install command itself."""
    stderr = io.StringIO()
    argv_patch = patch.object(sys, "argv", ["sd", "install"])
    with patch.object(sys, "stderr", stderr), argv_patch:
      _warn_if_version_stale({"spec_driver_installed_version": "1.0.0"})
    assert stderr.getvalue() == ""


if __name__ == "__main__":
  unittest.main()
