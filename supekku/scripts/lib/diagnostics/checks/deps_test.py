"""Tests for dependency checks."""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

from supekku.scripts.lib.diagnostics.checks.deps import check_deps


@dataclass
class _FakeWorkspace:
  root: Path = Path("/fake/workspace")


_ALL_DEP_NAMES = {
  "python",
  "git",
  "go",
  "gomarkdoc",
  "zig",
  "zigmarkdoc",
  "node",
  "ts-doc-extract",
}


class TestCheckDeps(unittest.TestCase):
  """Tests for check_deps function."""

  def _run_with_all_available(self) -> list:
    with (
      patch("supekku.scripts.lib.diagnostics.checks.deps.which") as mock_which,
      patch(
        "supekku.scripts.lib.diagnostics.checks.deps.is_npm_package_available",
        return_value=True,
      ),
    ):
      mock_which.side_effect = lambda cmd: f"/usr/bin/{cmd}"
      return check_deps(_FakeWorkspace())

  def test_all_available(self) -> None:
    """All deps present produces all-pass results."""
    results = self._run_with_all_available()
    assert all(r.status == "pass" for r in results), [
      (r.name, r.status) for r in results
    ]

  def test_covers_all_expected_deps(self) -> None:
    """Check that all expected dependency names are covered."""
    results = self._run_with_all_available()
    names = {r.name for r in results}
    assert names == _ALL_DEP_NAMES

  def test_python_version_pass(self) -> None:
    """Current python should always pass."""
    results = self._run_with_all_available()
    python_result = next(r for r in results if r.name == "python")
    assert python_result.status == "pass"
    vi = sys.version_info
    assert f"{vi.major}.{vi.minor}" in python_result.message

  def test_git_missing_but_jj_present(self) -> None:
    """jj as git alternative should pass."""

    def selective_which(cmd: str) -> str | None:
      return "/usr/bin/jj" if cmd == "jj" else None

    with (
      patch(
        "supekku.scripts.lib.diagnostics.checks.deps.which",
        side_effect=selective_which,
      ),
      patch(
        "supekku.scripts.lib.diagnostics.checks.deps.is_npm_package_available",
        return_value=False,
      ),
    ):
      results = check_deps(_FakeWorkspace())

    git_result = next(r for r in results if r.name == "git")
    assert git_result.status == "pass"
    assert "jj" in git_result.message

  def test_no_vcs_warns(self) -> None:
    """Missing both git and jj should warn."""
    with (
      patch(
        "supekku.scripts.lib.diagnostics.checks.deps.which",
        return_value=None,
      ),
      patch(
        "supekku.scripts.lib.diagnostics.checks.deps.is_npm_package_available",
        return_value=False,
      ),
    ):
      results = check_deps(_FakeWorkspace())

    git_result = next(r for r in results if r.name == "git")
    assert git_result.status == "warn"
    assert git_result.suggestion is not None

  def test_go_missing_warns(self) -> None:
    """Missing go should warn."""
    with (
      patch(
        "supekku.scripts.lib.diagnostics.checks.deps.which",
        return_value=None,
      ),
      patch(
        "supekku.scripts.lib.diagnostics.checks.deps.is_npm_package_available",
        return_value=False,
      ),
    ):
      results = check_deps(_FakeWorkspace())

    go_result = next(r for r in results if r.name == "go")
    assert go_result.status == "warn"
    assert "go.dev" in (go_result.suggestion or "")

  def test_gomarkdoc_missing_warns_with_install(self) -> None:
    """Missing gomarkdoc should warn with install command."""
    with (
      patch(
        "supekku.scripts.lib.diagnostics.checks.deps.which",
        return_value=None,
      ),
      patch(
        "supekku.scripts.lib.diagnostics.checks.deps.is_npm_package_available",
        return_value=False,
      ),
    ):
      results = check_deps(_FakeWorkspace())

    gmd = next(r for r in results if r.name == "gomarkdoc")
    assert gmd.status == "warn"
    assert "go install" in (gmd.suggestion or "")

  def test_zig_missing_warns(self) -> None:
    """Missing zig should warn."""
    with (
      patch(
        "supekku.scripts.lib.diagnostics.checks.deps.which",
        return_value=None,
      ),
      patch(
        "supekku.scripts.lib.diagnostics.checks.deps.is_npm_package_available",
        return_value=False,
      ),
    ):
      results = check_deps(_FakeWorkspace())

    zig = next(r for r in results if r.name == "zig")
    assert zig.status == "warn"
    assert "ziglang.org" in (zig.suggestion or "")

  def test_zigmarkdoc_missing_warns(self) -> None:
    """Missing zigmarkdoc should warn with install link."""
    with (
      patch(
        "supekku.scripts.lib.diagnostics.checks.deps.which",
        return_value=None,
      ),
      patch(
        "supekku.scripts.lib.diagnostics.checks.deps.is_npm_package_available",
        return_value=False,
      ),
    ):
      results = check_deps(_FakeWorkspace())

    zmd = next(r for r in results if r.name == "zigmarkdoc")
    assert zmd.status == "warn"
    assert "zigmarkdoc" in (zmd.suggestion or "")

  def test_ts_doc_extract_missing_warns(self) -> None:
    """Missing ts-doc-extract should warn."""
    with (
      patch(
        "supekku.scripts.lib.diagnostics.checks.deps.which",
        return_value="/usr/bin/x",
      ),
      patch(
        "supekku.scripts.lib.diagnostics.checks.deps.is_npm_package_available",
        return_value=False,
      ),
    ):
      results = check_deps(_FakeWorkspace())

    ts = next(r for r in results if r.name == "ts-doc-extract")
    assert ts.status == "warn"
    assert "npm install" in (ts.suggestion or "")

  def test_all_results_have_deps_category(self) -> None:
    """Every result should be in the deps category."""
    results = self._run_with_all_available()
    assert all(r.category == "deps" for r in results)


if __name__ == "__main__":
  unittest.main()
