"""Tests for memory staleness computation."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

from supekku.scripts.lib.memory.models import MemoryRecord
from supekku.scripts.lib.memory.staleness import (
  StalenessInfo,
  compute_batch_staleness,
  glob_to_pathspec,
)


def _make_record(
  memory_id: str = "mem.test",
  verified: date | None = None,
  verified_sha: str | None = None,
  scope_paths: list[str] | None = None,
  scope_globs: list[str] | None = None,
  updated: date | None = None,
) -> MemoryRecord:
  """Build a minimal MemoryRecord for staleness tests."""
  scope: dict = {}
  if scope_paths:
    scope["paths"] = scope_paths
  if scope_globs:
    scope["globs"] = scope_globs
  return MemoryRecord(
    id=memory_id,
    name="Test memory",
    status="active",
    memory_type="pattern",
    path="/fake/path.md",
    verified=verified,
    verified_sha=verified_sha,
    updated=updated,
    scope=scope,
  )


class TestGlobToPathspec:
  """Tests for glob-to-pathspec conversion."""

  def test_strips_trailing_double_star(self) -> None:
    assert glob_to_pathspec("supekku/cli/**") == "supekku/cli/"

  def test_strips_trailing_slash_double_star(self) -> None:
    assert glob_to_pathspec("supekku/cli/**") == "supekku/cli/"

  def test_passes_through_simple_glob(self) -> None:
    assert glob_to_pathspec("supekku/cli/*.py") == "supekku/cli/*.py"

  def test_passes_through_plain_path(self) -> None:
    assert glob_to_pathspec("supekku/cli/edit.py") == "supekku/cli/edit.py"

  def test_strips_leading_dot_slash(self) -> None:
    assert glob_to_pathspec("./supekku/cli/**") == "supekku/cli/"


class TestStalenessInfo:
  """Tests for StalenessInfo dataclass."""

  def test_scoped_attested(self) -> None:
    info = StalenessInfo(
      memory_id="mem.test",
      verified_sha="abc123" + "0" * 34,
      verified_date=date(2026, 3, 1),
      scope_paths=["supekku/cli/"],
      commits_since=5,
      days_since=8,
      has_scope=True,
    )
    assert info.has_scope is True
    assert info.verified_sha is not None
    assert info.commits_since == 5

  def test_scoped_unattested(self) -> None:
    info = StalenessInfo(
      memory_id="mem.test",
      verified_sha=None,
      verified_date=date(2026, 3, 1),
      scope_paths=["supekku/cli/"],
      commits_since=None,
      days_since=8,
      has_scope=True,
    )
    assert info.has_scope is True
    assert info.verified_sha is None
    assert info.commits_since is None

  def test_unscoped(self) -> None:
    info = StalenessInfo(
      memory_id="mem.test",
      verified_sha=None,
      verified_date=date(2026, 3, 1),
      scope_paths=[],
      commits_since=None,
      days_since=8,
      has_scope=False,
    )
    assert info.has_scope is False


class TestComputeBatchStaleness:
  """Tests for batched staleness computation."""

  def test_empty_records(self) -> None:
    result = compute_batch_staleness([], Path("/repo"))
    assert result == []

  def test_unscoped_memory_uses_days_since(self) -> None:
    """Unscoped memory falls back to days_since from verified date."""
    record = _make_record(
      verified=date(2026, 3, 1),
      updated=date(2026, 3, 1),
    )
    with patch("supekku.scripts.lib.memory.staleness.date") as mock_date:
      mock_date.today.return_value = date(2026, 3, 9)
      mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
      result = compute_batch_staleness([record], Path("/repo"))

    assert len(result) == 1
    assert result[0].has_scope is False
    assert result[0].commits_since is None
    assert result[0].days_since == 8

  def test_unscoped_uses_updated_when_no_verified(self) -> None:
    """Unscoped memory without verified date uses updated."""
    record = _make_record(updated=date(2026, 3, 5))
    with patch("supekku.scripts.lib.memory.staleness.date") as mock_date:
      mock_date.today.return_value = date(2026, 3, 9)
      mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
      result = compute_batch_staleness([record], Path("/repo"))

    assert result[0].days_since == 4

  def test_scoped_attested_counts_commits(self) -> None:
    """Scoped+attested memory counts commits from git log."""
    sha = "a" * 40
    record = _make_record(
      verified=date(2026, 3, 1),
      verified_sha=sha,
      scope_paths=["supekku/cli/edit.py"],
    )
    git_output = (
      "abc1234 fix edit command\n"
      "supekku/cli/edit.py\n"
      "\n"
      "def5678 refactor edit\n"
      "supekku/cli/edit.py\n"
      "supekku/cli/common.py\n"
      "\n"
      "ghi9012 unrelated change\n"
      "supekku/scripts/lib/core/git.py\n"
    )
    mock_result = MagicMock(returncode=0, stdout=git_output)
    with (
      patch("subprocess.run", return_value=mock_result),
      patch("supekku.scripts.lib.memory.staleness.date") as mock_date,
    ):
      mock_date.today.return_value = date(2026, 3, 9)
      mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
      result = compute_batch_staleness([record], Path("/repo"))

    assert len(result) == 1
    assert result[0].commits_since == 2
    assert result[0].has_scope is True

  def test_scoped_unattested_has_no_commits_since(self) -> None:
    """Scoped but unattested memory has commits_since=None."""
    record = _make_record(
      verified=date(2026, 3, 1),
      scope_paths=["supekku/cli/"],
    )
    with patch("supekku.scripts.lib.memory.staleness.date") as mock_date:
      mock_date.today.return_value = date(2026, 3, 9)
      mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
      result = compute_batch_staleness([record], Path("/repo"))

    assert result[0].has_scope is True
    assert result[0].commits_since is None
    assert result[0].days_since == 8

  def test_glob_scope_included(self) -> None:
    """Memories with only scope.globs are treated as scoped."""
    sha = "b" * 40
    record = _make_record(
      verified=date(2026, 3, 1),
      verified_sha=sha,
      scope_globs=["supekku/tui/**"],
    )
    git_output = "abc1234 tui change\nsupekku/tui/widget.py\n"
    mock_result = MagicMock(returncode=0, stdout=git_output)
    with (
      patch("subprocess.run", return_value=mock_result),
      patch("supekku.scripts.lib.memory.staleness.date") as mock_date,
    ):
      mock_date.today.return_value = date(2026, 3, 9)
      mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
      result = compute_batch_staleness([record], Path("/repo"))

    assert result[0].has_scope is True
    assert result[0].commits_since == 1
    # Verify pathspec was tui/ (stripped /**)
    assert "supekku/tui/" in result[0].scope_paths

  def test_git_failure_degrades_gracefully(self) -> None:
    """When git fails, scoped+attested memories degrade to days_since."""
    sha = "c" * 40
    record = _make_record(
      verified=date(2026, 3, 1),
      verified_sha=sha,
      scope_paths=["supekku/cli/"],
    )
    mock_result = MagicMock(returncode=128, stdout="")
    with (
      patch("subprocess.run", return_value=mock_result),
      patch("supekku.scripts.lib.memory.staleness.date") as mock_date,
    ):
      mock_date.today.return_value = date(2026, 3, 9)
      mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
      result = compute_batch_staleness([record], Path("/repo"))

    assert result[0].commits_since is None
    assert result[0].days_since == 8

  def test_multiple_records_single_git_call(self) -> None:
    """Multiple scoped+attested records use a single git invocation."""
    sha1 = "a" * 40
    sha2 = "b" * 40
    r1 = _make_record(
      memory_id="mem.one",
      verified=date(2026, 3, 1),
      verified_sha=sha1,
      scope_paths=["supekku/cli/edit.py"],
    )
    r2 = _make_record(
      memory_id="mem.two",
      verified=date(2026, 3, 5),
      verified_sha=sha2,
      scope_paths=["supekku/tui/app.py"],
    )
    git_output = (
      "abc1234 change edit\n"
      "supekku/cli/edit.py\n"
      "\n"
      "def5678 change tui\n"
      "supekku/tui/app.py\n"
    )
    mock_result = MagicMock(returncode=0, stdout=git_output)
    with (
      patch("subprocess.run", return_value=mock_result) as mock_run,
      patch("supekku.scripts.lib.memory.staleness.date") as mock_date,
    ):
      mock_date.today.return_value = date(2026, 3, 9)
      mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
      result = compute_batch_staleness([r1, r2], Path("/repo"))

    # Single git call
    assert mock_run.call_count == 1
    assert len(result) == 2

  def test_no_attested_records_skips_git(self) -> None:
    """When no records are attested, git is not called."""
    r1 = _make_record(
      memory_id="mem.one",
      verified=date(2026, 3, 1),
      scope_paths=["supekku/cli/"],
    )
    r2 = _make_record(
      memory_id="mem.two",
      updated=date(2026, 3, 5),
    )
    with (
      patch("subprocess.run") as mock_run,
      patch("supekku.scripts.lib.memory.staleness.date") as mock_date,
    ):
      mock_date.today.return_value = date(2026, 3, 9)
      mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
      result = compute_batch_staleness([r1, r2], Path("/repo"))

    mock_run.assert_not_called()
    assert len(result) == 2
