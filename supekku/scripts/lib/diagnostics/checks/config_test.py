"""Tests for configuration checks."""

from __future__ import annotations

import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

from supekku.scripts.lib.diagnostics.checks.config import check_config

_VERSION_MODULE = "supekku.scripts.lib.core.version.get_package_version"


@dataclass
class _FakeWorkspace:
  root: Path


def _make_full_workspace(tmp: Path, *, version: str = "1.0.0") -> _FakeWorkspace:
  """Create a workspace with all config files present."""
  sd = tmp / ".spec-driver"
  sd.mkdir()
  (sd / "workflow.toml").write_text(
    f'spec_driver_installed_version = "{version}"\n'
    '[workflow]\nceremony = "town_planner"\n'
  )
  (sd / "agents").mkdir()
  (sd / "skills.allowlist").write_text("boot\ndoctrine\n")

  # Canonical skills
  for skill in ("boot", "doctrine"):
    skill_dir = sd / "skills" / skill
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(f"---\nname: {skill}\n---\n")

  # Agent target dirs with symlinks
  for target_dir in (tmp / ".claude" / "skills", tmp / ".agents" / "skills"):
    target_dir.mkdir(parents=True)
    for skill in ("boot", "doctrine"):
      link = target_dir / skill
      link.symlink_to(sd / "skills" / skill)

  (tmp / "CLAUDE.md").write_text("# Claude\n")
  return _FakeWorkspace(root=tmp)


class TestCheckConfig(unittest.TestCase):
  """Tests for check_config function."""

  @patch(_VERSION_MODULE, return_value="1.0.0")
  def test_full_config_all_pass(self, _mock_ver) -> None:
    """Complete configuration should produce no warns or fails."""
    with tempfile.TemporaryDirectory() as td:
      ws = _make_full_workspace(Path(td))
      results = check_config(ws)
      non_pass = [r for r in results if r.status != "pass"]
      assert not non_pass, [(r.name, r.status, r.message) for r in non_pass]

  def test_missing_workflow_toml_warns(self) -> None:
    """Missing workflow.toml should warn."""
    with tempfile.TemporaryDirectory() as td:
      root = Path(td)
      (root / ".spec-driver").mkdir()
      (root / ".spec-driver" / "agents").mkdir()
      ws = _FakeWorkspace(root=root)
      results = check_config(ws)
      wf = next(r for r in results if r.name == "workflow.toml")
      assert wf.status == "warn"

  def test_invalid_workflow_toml_fails(self) -> None:
    """Invalid TOML should fail."""
    with tempfile.TemporaryDirectory() as td:
      root = Path(td)
      sd = root / ".spec-driver"
      sd.mkdir()
      (sd / "workflow.toml").write_text("invalid = [toml")
      (sd / "agents").mkdir()
      ws = _FakeWorkspace(root=root)
      results = check_config(ws)
      wf = next(r for r in results if r.name == "workflow.toml")
      assert wf.status == "fail"

  def test_missing_claude_md_warns(self) -> None:
    """Missing CLAUDE.md should warn."""
    with tempfile.TemporaryDirectory() as td:
      root = Path(td)
      sd = root / ".spec-driver"
      sd.mkdir()
      (sd / "workflow.toml").write_text("")
      (sd / "agents").mkdir()
      ws = _FakeWorkspace(root=root)
      results = check_config(ws)
      cm = next(r for r in results if r.name == "CLAUDE.md")
      assert cm.status == "warn"

  def test_empty_allowlist_warns(self) -> None:
    """Empty skills allowlist should warn."""
    with tempfile.TemporaryDirectory() as td:
      root = Path(td)
      sd = root / ".spec-driver"
      sd.mkdir()
      (sd / "workflow.toml").write_text("")
      (sd / "agents").mkdir()
      (sd / "skills.allowlist").write_text("# just comments\n")
      ws = _FakeWorkspace(root=root)
      results = check_config(ws)
      al = next(r for r in results if r.name == "skills-allowlist")
      assert al.status == "warn"

  def test_skills_count_in_message(self) -> None:
    """Allowlist check should report count."""
    with tempfile.TemporaryDirectory() as td:
      ws = _make_full_workspace(Path(td))
      results = check_config(ws)
      al = next(r for r in results if r.name == "skills-allowlist")
      assert "2 skills" in al.message

  def test_missing_target_dir_warns(self) -> None:
    """Missing agent target dir should warn."""
    with tempfile.TemporaryDirectory() as td:
      root = Path(td)
      sd = root / ".spec-driver"
      sd.mkdir()
      (sd / "workflow.toml").write_text("")
      (sd / "agents").mkdir()
      (sd / "skills.allowlist").write_text("boot\n")
      skill_dir = sd / "skills" / "boot"
      skill_dir.mkdir(parents=True)
      (skill_dir / "SKILL.md").write_text("---\nname: boot\n---\n")
      (root / "CLAUDE.md").write_text("")
      # No .claude/skills or .agents/skills

      ws = _FakeWorkspace(root=root)
      results = check_config(ws)
      target_results = [
        r
        for r in results
        if r.name.startswith("skills-claude") or r.name.startswith("skills-codex")
      ]
      assert all(r.status == "warn" for r in target_results)

  @patch(_VERSION_MODULE, return_value="1.0.0")
  def test_all_results_have_config_category(self, _mock_ver) -> None:
    """Every result should be in the config category."""
    with tempfile.TemporaryDirectory() as td:
      ws = _make_full_workspace(Path(td))
      results = check_config(ws)
      assert all(r.category == "config" for r in results)


class TestVersionStaleness(unittest.TestCase):
  """Tests for version-staleness diagnostic check."""

  @patch(_VERSION_MODULE, return_value="1.0.0")
  def test_matching_version_passes(self, _mock_ver) -> None:
    """Matching version should pass."""
    with tempfile.TemporaryDirectory() as td:
      ws = _make_full_workspace(Path(td), version="1.0.0")
      results = check_config(ws)
      vs = next(r for r in results if r.name == "version-staleness")
      assert vs.status == "pass"
      assert "1.0.0" in vs.message

  @patch(_VERSION_MODULE, return_value="2.0.0")
  def test_stale_version_warns(self, _mock_ver) -> None:
    """Outdated version should warn with install suggestion."""
    with tempfile.TemporaryDirectory() as td:
      ws = _make_full_workspace(Path(td), version="1.0.0")
      results = check_config(ws)
      vs = next(r for r in results if r.name == "version-staleness")
      assert vs.status == "warn"
      assert "1.0.0" in vs.message
      assert "2.0.0" in vs.message
      assert vs.suggestion and "install" in vs.suggestion

  @patch(_VERSION_MODULE, return_value="1.0.0")
  def test_missing_version_stamp_warns(self, _mock_ver) -> None:
    """Missing version key should warn."""
    with tempfile.TemporaryDirectory() as td:
      root = Path(td)
      sd = root / ".spec-driver"
      sd.mkdir()
      (sd / "workflow.toml").write_text('[workflow]\nceremony = "settler"\n')
      (sd / "agents").mkdir()
      ws = _FakeWorkspace(root=root)
      results = check_config(ws)
      vs = next(r for r in results if r.name == "version-staleness")
      assert vs.status == "warn"
      assert vs.suggestion and "install" in vs.suggestion

  @patch(_VERSION_MODULE, return_value="1.0.0")
  def test_missing_workflow_toml_warns(self, _mock_ver) -> None:
    """Missing workflow.toml should warn for version check too."""
    with tempfile.TemporaryDirectory() as td:
      root = Path(td)
      (root / ".spec-driver").mkdir()
      (root / ".spec-driver" / "agents").mkdir()
      ws = _FakeWorkspace(root=root)
      results = check_config(ws)
      vs = next(r for r in results if r.name == "version-staleness")
      assert vs.status == "warn"


if __name__ == "__main__":
  unittest.main()
