"""POL-002 sanity coverage for CLI vocabulary constants.

Regression guard against silent magic-string reintroduction in CLI
modules that import from this constants surface.
"""

from __future__ import annotations

import re

from spec_driver.presentation.cli import constants


class TestSubcommandNames:
  def test_validate_group_names(self) -> None:
    assert constants.VALIDATE == "validate"
    assert constants.VALIDATE_WORKSPACE == "workspace"
    assert constants.VALIDATE_FILE == "file"
    assert constants.VALIDATE_TEMPLATES == "templates"

  def test_schema_group_names(self) -> None:
    assert constants.SCHEMA == "schema"
    assert constants.SCHEMA_ENUMS == "enums"

  def test_admin_group_names(self) -> None:
    assert constants.ADMIN == "admin"
    assert constants.ADMIN_MIGRATE == "migrate"
    assert constants.ADMIN_REGENERATE_TEMPLATES == "regenerate-templates"


class TestFlagLiterals:
  def test_flag_literals_carry_double_dash(self) -> None:
    flag_attrs = [
      constants.FLAG_STRICT,
      constants.FLAG_NO_TOLERATED,
      constants.FLAG_FIX,
      constants.FLAG_SYNC,
      constants.FLAG_KIND,
      constants.FLAG_DRY_RUN,
      constants.FLAG_CHECK,
      constants.FLAG_LIST,
    ]
    for flag in flag_attrs:
      assert flag.startswith("--"), flag

  def test_flag_no_tolerated_uses_aliases_suffix(self) -> None:
    # DR-137 §5.4 verbatim spelling
    assert constants.FLAG_NO_TOLERATED == "--no-tolerated-aliases"


class TestMigrationVocabulary:
  def test_migration_folder_pattern_matches_canonical(self) -> None:
    pattern = constants.MIGRATION_FOLDER_PATTERN
    assert isinstance(pattern, re.Pattern)
    match = pattern.match("v0_10_0_001_delta_blocks")
    assert match is not None
    assert match.group("major") == "0"
    assert match.group("minor") == "10"
    assert match.group("patch") == "0"
    assert match.group("ordinal") == "001"
    assert match.group("slug") == "delta_blocks"

  def test_migration_folder_pattern_rejects_invalid(self) -> None:
    pattern = constants.MIGRATION_FOLDER_PATTERN
    assert pattern.match("0.10.0_001_delta") is None  # dotted form
    assert pattern.match("v0_10_0_delta_blocks") is None  # no ordinal
    assert pattern.match("v0_10_001_delta") is None  # missing patch

  def test_migration_paths_under_run(self) -> None:
    assert constants.MIGRATION_LOG_PATH.startswith(".spec-driver/run/migrations/")
    assert constants.MIGRATION_LOCK_PATH.startswith(".spec-driver/run/migrations/")
    assert "{timestamp}" in constants.MIGRATION_LOG_PATH
    assert "{step}" in constants.MIGRATION_LOG_PATH


class TestPublicSurface:
  def test_all_names_exported(self) -> None:
    expected = {
      "ADMIN",
      "ADMIN_MIGRATE",
      "ADMIN_REGENERATE_TEMPLATES",
      "FLAG_CHECK",
      "FLAG_DRY_RUN",
      "FLAG_FIX",
      "FLAG_KIND",
      "FLAG_LIST",
      "FLAG_NO_TOLERATED",
      "FLAG_STRICT",
      "FLAG_SYNC",
      "MIGRATION_FOLDER_PATTERN",
      "MIGRATION_LOCK_PATH",
      "MIGRATION_LOG_PATH",
      "SCHEMA",
      "SCHEMA_ENUMS",
      "VALIDATE",
      "VALIDATE_FILE",
      "VALIDATE_TEMPLATES",
      "VALIDATE_WORKSPACE",
    }
    assert set(constants.__all__) == expected
    for name in expected:
      assert hasattr(constants, name), name
