"""Tests for workspace directory constants and helper functions in paths.py."""

from __future__ import annotations

import unittest
from pathlib import Path

import supekku.scripts.lib.core.paths as paths_mod
from supekku.scripts.lib.core.paths import (
  AUDITS_SUBDIR,
  BACKLOG_DIR,
  CHANGES_DIR,
  DECISIONS_SUBDIR,
  DELTAS_SUBDIR,
  IMPROVEMENTS_SUBDIR,
  ISSUES_SUBDIR,
  MEMORY_DIR,
  POLICIES_SUBDIR,
  PROBLEMS_SUBDIR,
  PRODUCT_SPECS_SUBDIR,
  REVISIONS_SUBDIR,
  RISKS_SUBDIR,
  SPECS_DIR,
  STANDARDS_SUBDIR,
  TECH_SPECS_SUBDIR,
  get_audits_dir,
  get_backlog_dir,
  get_changes_dir,
  get_decisions_dir,
  get_deltas_dir,
  get_memory_dir,
  get_policies_dir,
  get_product_specs_dir,
  get_revisions_dir,
  get_specs_dir,
  get_standards_dir,
  get_tech_specs_dir,
  init_paths,
  reset_paths,
)


class TestWorkspaceRootConstants(unittest.TestCase):
  """Workspace root directory constants have expected values."""

  def test_specs_dir(self) -> None:
    """SPECS_DIR matches the specify directory name."""
    assert SPECS_DIR == "specify"

  def test_changes_dir(self) -> None:
    """CHANGES_DIR matches the change directory name."""
    assert CHANGES_DIR == "change"

  def test_backlog_dir(self) -> None:
    """BACKLOG_DIR matches the backlog directory name."""
    assert BACKLOG_DIR == "backlog"

  def test_memory_dir(self) -> None:
    """MEMORY_DIR matches the memory directory name."""
    assert MEMORY_DIR == "memory"


class TestSpecsSubdirConstants(unittest.TestCase):
  """Subdirectory constants within SPECS_DIR."""

  def test_tech_specs(self) -> None:
    """Tech specs subdir is 'tech'."""
    assert TECH_SPECS_SUBDIR == "tech"

  def test_product_specs(self) -> None:
    """Product specs subdir is 'product'."""
    assert PRODUCT_SPECS_SUBDIR == "product"

  def test_decisions(self) -> None:
    """Decisions subdir is 'decisions'."""
    assert DECISIONS_SUBDIR == "decisions"

  def test_policies(self) -> None:
    """Policies subdir is 'policies'."""
    assert POLICIES_SUBDIR == "policies"

  def test_standards(self) -> None:
    """Standards subdir is 'standards'."""
    assert STANDARDS_SUBDIR == "standards"


class TestChangesSubdirConstants(unittest.TestCase):
  """Subdirectory constants within CHANGES_DIR."""

  def test_deltas(self) -> None:
    """Deltas subdir is 'deltas'."""
    assert DELTAS_SUBDIR == "deltas"

  def test_revisions(self) -> None:
    """Revisions subdir is 'revisions'."""
    assert REVISIONS_SUBDIR == "revisions"

  def test_audits(self) -> None:
    """Audits subdir is 'audits'."""
    assert AUDITS_SUBDIR == "audits"


class TestBacklogSubdirConstants(unittest.TestCase):
  """Subdirectory constants within BACKLOG_DIR."""

  def test_issues(self) -> None:
    """Issues subdir is 'issues'."""
    assert ISSUES_SUBDIR == "issues"

  def test_problems(self) -> None:
    """Problems subdir is 'problems'."""
    assert PROBLEMS_SUBDIR == "problems"

  def test_improvements(self) -> None:
    """Improvements subdir is 'improvements'."""
    assert IMPROVEMENTS_SUBDIR == "improvements"

  def test_risks(self) -> None:
    """Risks subdir is 'risks'."""
    assert RISKS_SUBDIR == "risks"


class TestSpecsHelpers(unittest.TestCase):
  """Helper functions for specify/ directory tree."""

  def setUp(self) -> None:
    """Set up a fake repo root for path composition tests."""
    self.root = Path("/fake/repo")

  def test_get_specs_dir(self) -> None:
    """Returns repo_root / specify."""
    assert get_specs_dir(self.root) == self.root / "specify"

  def test_get_tech_specs_dir(self) -> None:
    """Returns repo_root / specify / tech."""
    assert get_tech_specs_dir(self.root) == self.root / "specify" / "tech"

  def test_get_product_specs_dir(self) -> None:
    """Returns repo_root / specify / product."""
    assert get_product_specs_dir(self.root) == self.root / "specify" / "product"

  def test_get_decisions_dir(self) -> None:
    """Returns repo_root / specify / decisions."""
    assert get_decisions_dir(self.root) == self.root / "specify" / "decisions"

  def test_get_policies_dir(self) -> None:
    """Returns repo_root / specify / policies."""
    assert get_policies_dir(self.root) == self.root / "specify" / "policies"

  def test_get_standards_dir(self) -> None:
    """Returns repo_root / specify / standards."""
    assert get_standards_dir(self.root) == self.root / "specify" / "standards"


class TestChangesHelpers(unittest.TestCase):
  """Helper functions for change/ directory tree."""

  def setUp(self) -> None:
    """Set up a fake repo root for path composition tests."""
    self.root = Path("/fake/repo")

  def test_get_changes_dir(self) -> None:
    """Returns repo_root / change."""
    assert get_changes_dir(self.root) == self.root / "change"

  def test_get_deltas_dir(self) -> None:
    """Returns repo_root / change / deltas."""
    assert get_deltas_dir(self.root) == self.root / "change" / "deltas"

  def test_get_revisions_dir(self) -> None:
    """Returns repo_root / change / revisions."""
    assert get_revisions_dir(self.root) == self.root / "change" / "revisions"

  def test_get_audits_dir(self) -> None:
    """Returns repo_root / change / audits."""
    assert get_audits_dir(self.root) == self.root / "change" / "audits"


class TestBacklogHelpers(unittest.TestCase):
  """Helper functions for backlog/ directory."""

  def test_get_backlog_dir(self) -> None:
    """Returns repo_root / backlog."""
    root = Path("/fake/repo")
    assert get_backlog_dir(root) == root / "backlog"


class TestMemoryHelpers(unittest.TestCase):
  """Helper functions for memory/ directory."""

  def test_get_memory_dir(self) -> None:
    """Returns repo_root / memory."""
    root = Path("/fake/repo")
    assert get_memory_dir(root) == root / "memory"


class TestHelperComposition(unittest.TestCase):
  """Helpers compose correctly - subdirs build on parent helpers."""

  def setUp(self) -> None:
    """Set up a fake repo root for composition tests."""
    self.root = Path("/fake/repo")

  def test_tech_specs_is_child_of_specs(self) -> None:
    """get_tech_specs_dir result is a child of get_specs_dir."""
    specs = get_specs_dir(self.root)
    tech = get_tech_specs_dir(self.root)
    assert tech.parent == specs

  def test_deltas_is_child_of_changes(self) -> None:
    """get_deltas_dir result is a child of get_changes_dir."""
    changes = get_changes_dir(self.root)
    deltas = get_deltas_dir(self.root)
    assert deltas.parent == changes

  def test_decisions_is_child_of_specs(self) -> None:
    """get_decisions_dir result is a child of get_specs_dir."""
    specs = get_specs_dir(self.root)
    decisions = get_decisions_dir(self.root)
    assert decisions.parent == specs


class TestInitPaths(unittest.TestCase):
  """init_paths(config) overrides module-level directory constants."""

  def tearDown(self) -> None:
    """Restore defaults after each test."""
    reset_paths()

  def test_full_override(self) -> None:
    """init_paths with all keys overrides every constant."""
    config = {
      "dirs": {
        "specs": "specifications",
        "changes": "modifications",
        "backlog": "inbox",
        "memory": "knowledge",
        "tech_specs": "technical",
        "product_specs": "products",
        "decisions": "adrs",
        "policies": "rules",
        "standards": "stds",
        "deltas": "patches",
        "revisions": "revs",
        "audits": "reviews",
        "issues": "bugs",
        "problems": "pains",
        "improvements": "enhancements",
        "risks": "hazards",
      },
    }
    init_paths(config)

    assert paths_mod.SPECS_DIR == "specifications"
    assert paths_mod.CHANGES_DIR == "modifications"
    assert paths_mod.BACKLOG_DIR == "inbox"
    assert paths_mod.MEMORY_DIR == "knowledge"
    assert paths_mod.TECH_SPECS_SUBDIR == "technical"
    assert paths_mod.PRODUCT_SPECS_SUBDIR == "products"
    assert paths_mod.DECISIONS_SUBDIR == "adrs"
    assert paths_mod.POLICIES_SUBDIR == "rules"
    assert paths_mod.STANDARDS_SUBDIR == "stds"
    assert paths_mod.DELTAS_SUBDIR == "patches"
    assert paths_mod.REVISIONS_SUBDIR == "revs"
    assert paths_mod.AUDITS_SUBDIR == "reviews"
    assert paths_mod.ISSUES_SUBDIR == "bugs"
    assert paths_mod.PROBLEMS_SUBDIR == "pains"
    assert paths_mod.IMPROVEMENTS_SUBDIR == "enhancements"
    assert paths_mod.RISKS_SUBDIR == "hazards"

  def test_partial_override(self) -> None:
    """init_paths with partial dirs only overrides specified keys."""
    config = {"dirs": {"specs": "specifications", "deltas": "patches"}}
    init_paths(config)

    assert paths_mod.SPECS_DIR == "specifications"
    assert paths_mod.DELTAS_SUBDIR == "patches"
    # Non-overridden constants retain defaults
    assert paths_mod.CHANGES_DIR == "change"
    assert paths_mod.MEMORY_DIR == "memory"

  def test_missing_dirs_section(self) -> None:
    """init_paths with no dirs key leaves defaults unchanged."""
    init_paths({"ceremony": "settler"})

    assert paths_mod.SPECS_DIR == "specify"
    assert paths_mod.CHANGES_DIR == "change"

  def test_empty_dirs_section(self) -> None:
    """init_paths with empty dirs dict leaves defaults unchanged."""
    init_paths({"dirs": {}})

    assert paths_mod.SPECS_DIR == "specify"
    assert paths_mod.CHANGES_DIR == "change"


class TestResetPaths(unittest.TestCase):
  """reset_paths() restores original default constants."""

  def tearDown(self) -> None:
    """Safety net: always restore."""
    reset_paths()

  def test_restores_after_override(self) -> None:
    """reset_paths undoes init_paths overrides."""
    init_paths({"dirs": {"specs": "custom_specs", "changes": "custom_changes"}})
    reset_paths()

    assert paths_mod.SPECS_DIR == "specify"
    assert paths_mod.CHANGES_DIR == "change"

  def test_idempotent(self) -> None:
    """Calling reset_paths without init_paths is safe."""
    reset_paths()
    assert paths_mod.SPECS_DIR == "specify"


class TestCustomDirsHelpers(unittest.TestCase):
  """get_*_dir() helpers return paths using overridden constants."""

  def setUp(self) -> None:
    """Set up custom dirs."""
    self.root = Path("/fake/repo")
    init_paths(
      {
        "dirs": {
          "specs": "specifications",
          "changes": "modifications",
          "backlog": "inbox",
          "memory": "knowledge",
          "tech_specs": "technical",
          "decisions": "adrs",
          "deltas": "patches",
          "revisions": "revs",
          "audits": "reviews",
        },
      }
    )

  def tearDown(self) -> None:
    """Restore defaults."""
    reset_paths()

  def test_get_specs_dir_custom(self) -> None:
    """get_specs_dir uses overridden SPECS_DIR."""
    assert get_specs_dir(self.root) == self.root / "specifications"

  def test_get_changes_dir_custom(self) -> None:
    """get_changes_dir uses overridden CHANGES_DIR."""
    assert get_changes_dir(self.root) == self.root / "modifications"

  def test_get_backlog_dir_custom(self) -> None:
    """get_backlog_dir uses overridden BACKLOG_DIR."""
    assert get_backlog_dir(self.root) == self.root / "inbox"

  def test_get_memory_dir_custom(self) -> None:
    """get_memory_dir uses overridden MEMORY_DIR."""
    assert get_memory_dir(self.root) == self.root / "knowledge"

  def test_get_tech_specs_dir_custom(self) -> None:
    """get_tech_specs_dir uses overridden parent and subdir."""
    assert get_tech_specs_dir(self.root) == self.root / "specifications" / "technical"

  def test_get_decisions_dir_custom(self) -> None:
    """get_decisions_dir uses overridden parent and subdir."""
    assert get_decisions_dir(self.root) == self.root / "specifications" / "adrs"

  def test_get_deltas_dir_custom(self) -> None:
    """get_deltas_dir uses overridden parent and subdir."""
    assert get_deltas_dir(self.root) == self.root / "modifications" / "patches"

  def test_get_revisions_dir_custom(self) -> None:
    """get_revisions_dir uses overridden parent and subdir."""
    assert get_revisions_dir(self.root) == self.root / "modifications" / "revs"

  def test_get_audits_dir_custom(self) -> None:
    """get_audits_dir uses overridden parent and subdir."""
    assert get_audits_dir(self.root) == self.root / "modifications" / "reviews"


if __name__ == "__main__":
  unittest.main()
