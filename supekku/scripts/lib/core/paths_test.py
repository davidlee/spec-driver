"""Tests for workspace directory constants and helper functions in paths.py."""

from __future__ import annotations

import unittest
import warnings
from pathlib import Path

import supekku.scripts.lib.core.paths as paths_mod
from supekku.scripts.lib.core.paths import (
  AUDITS_SUBDIR,
  BACKLOG_DIR,
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
  SPEC_DRIVER_DIR,
  STANDARDS_SUBDIR,
  TECH_SPECS_SUBDIR,
  get_audits_dir,
  get_backlog_dir,
  get_decisions_dir,
  get_deltas_dir,
  get_memory_dir,
  get_policies_dir,
  get_product_specs_dir,
  get_revisions_dir,
  get_spec_driver_root,
  get_standards_dir,
  get_tech_specs_dir,
  init_paths,
  reset_paths,
)


class TestContentSubdirConstants(unittest.TestCase):
  """Content subdirectory constants have expected values."""

  def test_tech_specs(self) -> None:
    assert TECH_SPECS_SUBDIR == "tech"

  def test_product_specs(self) -> None:
    assert PRODUCT_SPECS_SUBDIR == "product"

  def test_decisions(self) -> None:
    assert DECISIONS_SUBDIR == "decisions"

  def test_policies(self) -> None:
    assert POLICIES_SUBDIR == "policies"

  def test_standards(self) -> None:
    assert STANDARDS_SUBDIR == "standards"

  def test_deltas(self) -> None:
    assert DELTAS_SUBDIR == "deltas"

  def test_revisions(self) -> None:
    assert REVISIONS_SUBDIR == "revisions"

  def test_audits(self) -> None:
    assert AUDITS_SUBDIR == "audits"

  def test_backlog(self) -> None:
    assert BACKLOG_DIR == "backlog"

  def test_memory(self) -> None:
    assert MEMORY_DIR == "memory"


class TestBacklogSubdirConstants(unittest.TestCase):
  """Subdirectory constants within backlog/."""

  def test_issues(self) -> None:
    assert ISSUES_SUBDIR == "issues"

  def test_problems(self) -> None:
    assert PROBLEMS_SUBDIR == "problems"

  def test_improvements(self) -> None:
    assert IMPROVEMENTS_SUBDIR == "improvements"

  def test_risks(self) -> None:
    assert RISKS_SUBDIR == "risks"


class TestContentHelpers(unittest.TestCase):
  """All content helpers resolve under .spec-driver/."""

  def setUp(self) -> None:
    self.root = Path("/fake/repo")
    self.sd = self.root / SPEC_DRIVER_DIR

  def test_get_tech_specs_dir(self) -> None:
    assert get_tech_specs_dir(self.root) == self.sd / "tech"

  def test_get_product_specs_dir(self) -> None:
    assert get_product_specs_dir(self.root) == self.sd / "product"

  def test_get_decisions_dir(self) -> None:
    assert get_decisions_dir(self.root) == self.sd / "decisions"

  def test_get_policies_dir(self) -> None:
    assert get_policies_dir(self.root) == self.sd / "policies"

  def test_get_standards_dir(self) -> None:
    assert get_standards_dir(self.root) == self.sd / "standards"

  def test_get_deltas_dir(self) -> None:
    assert get_deltas_dir(self.root) == self.sd / "deltas"

  def test_get_revisions_dir(self) -> None:
    assert get_revisions_dir(self.root) == self.sd / "revisions"

  def test_get_audits_dir(self) -> None:
    assert get_audits_dir(self.root) == self.sd / "audits"

  def test_get_backlog_dir(self) -> None:
    assert get_backlog_dir(self.root) == self.sd / "backlog"

  def test_get_memory_dir(self) -> None:
    assert get_memory_dir(self.root) == self.sd / "memory"


class TestHelperComposition(unittest.TestCase):
  """All content helpers are direct children of spec-driver root."""

  def setUp(self) -> None:
    self.root = Path("/fake/repo")
    self.sd = get_spec_driver_root(self.root)

  def test_all_content_dirs_are_children_of_spec_driver_root(self) -> None:
    """Every content helper resolves as a direct child of .spec-driver/."""
    helpers = [
      get_tech_specs_dir,
      get_product_specs_dir,
      get_decisions_dir,
      get_policies_dir,
      get_standards_dir,
      get_deltas_dir,
      get_revisions_dir,
      get_audits_dir,
      get_backlog_dir,
      get_memory_dir,
    ]
    for helper in helpers:
      result = helper(self.root)
      assert result.parent == self.sd, (
        f"{helper.__name__} resolves to {result}, expected parent {self.sd}"
      )


class TestInitPaths(unittest.TestCase):
  """init_paths(config) overrides module-level directory constants."""

  def tearDown(self) -> None:
    reset_paths()

  def test_full_override(self) -> None:
    config = {
      "dirs": {
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
    config = {"dirs": {"deltas": "patches", "memory": "knowledge"}}
    init_paths(config)

    assert paths_mod.DELTAS_SUBDIR == "patches"
    assert paths_mod.MEMORY_DIR == "knowledge"
    # Non-overridden constants retain defaults
    assert paths_mod.BACKLOG_DIR == "backlog"
    assert paths_mod.TECH_SPECS_SUBDIR == "tech"

  def test_missing_dirs_section(self) -> None:
    init_paths({"ceremony": "settler"})
    assert paths_mod.BACKLOG_DIR == "backlog"
    assert paths_mod.MEMORY_DIR == "memory"

  def test_empty_dirs_section(self) -> None:
    init_paths({"dirs": {}})
    assert paths_mod.BACKLOG_DIR == "backlog"
    assert paths_mod.MEMORY_DIR == "memory"

  def test_unknown_key_warns(self) -> None:
    """Unrecognized [dirs] keys emit a warning."""
    with warnings.catch_warnings(record=True) as w:
      warnings.simplefilter("always")
      init_paths({"dirs": {"specs": "specify", "bogus": "value"}})

    warning_messages = [str(x.message) for x in w]
    assert any("specs" in m for m in warning_messages)
    assert any("bogus" in m for m in warning_messages)

  def test_removed_grouping_keys_warn(self) -> None:
    """Former grouping keys (specs, changes) trigger warning."""
    with warnings.catch_warnings(record=True) as w:
      warnings.simplefilter("always")
      init_paths({"dirs": {"specs": "specify", "changes": "change"}})

    assert len(w) == 2
    messages = [str(x.message) for x in w]
    assert any("specs" in m for m in messages)
    assert any("changes" in m for m in messages)


class TestResetPaths(unittest.TestCase):
  """reset_paths() restores original default constants."""

  def tearDown(self) -> None:
    reset_paths()

  def test_restores_after_override(self) -> None:
    init_paths({"dirs": {"deltas": "custom_deltas", "memory": "custom_mem"}})
    reset_paths()

    assert paths_mod.DELTAS_SUBDIR == "deltas"
    assert paths_mod.MEMORY_DIR == "memory"

  def test_idempotent(self) -> None:
    reset_paths()
    assert paths_mod.BACKLOG_DIR == "backlog"


class TestCustomDirsHelpers(unittest.TestCase):
  """get_*_dir() helpers return paths using overridden constants."""

  def setUp(self) -> None:
    self.root = Path("/fake/repo")
    self.sd = self.root / SPEC_DRIVER_DIR
    init_paths(
      {
        "dirs": {
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
    reset_paths()

  def test_get_backlog_dir_custom(self) -> None:
    assert get_backlog_dir(self.root) == self.sd / "inbox"

  def test_get_memory_dir_custom(self) -> None:
    assert get_memory_dir(self.root) == self.sd / "knowledge"

  def test_get_tech_specs_dir_custom(self) -> None:
    assert get_tech_specs_dir(self.root) == self.sd / "technical"

  def test_get_decisions_dir_custom(self) -> None:
    assert get_decisions_dir(self.root) == self.sd / "adrs"

  def test_get_deltas_dir_custom(self) -> None:
    assert get_deltas_dir(self.root) == self.sd / "patches"

  def test_get_revisions_dir_custom(self) -> None:
    assert get_revisions_dir(self.root) == self.sd / "revs"

  def test_get_audits_dir_custom(self) -> None:
    assert get_audits_dir(self.root) == self.sd / "reviews"


if __name__ == "__main__":
  unittest.main()
