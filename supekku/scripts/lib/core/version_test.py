"""Tests for package version utilities."""

from __future__ import annotations

import unittest
from importlib.metadata import PackageNotFoundError
from unittest.mock import patch

from supekku.scripts.lib.core.version import get_package_version


class TestGetPackageVersion(unittest.TestCase):
  """Tests for get_package_version."""

  def test_returns_a_string(self) -> None:
    """Should return a non-empty version string."""
    result = get_package_version()
    assert isinstance(result, str)
    assert len(result) > 0

  @patch("importlib.metadata.version", side_effect=PackageNotFoundError)
  def test_falls_back_to_dunder_version(self, _mock) -> None:
    """Should fall back to supekku.__version__ when metadata unavailable."""
    import supekku  # noqa: PLC0415

    result = get_package_version()
    assert result == supekku.__version__


if __name__ == "__main__":
  unittest.main()
