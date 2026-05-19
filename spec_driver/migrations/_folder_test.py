"""Tests for spec_driver.migrations._folder (VT-CC-028)."""

from __future__ import annotations

import pytest
from packaging.version import Version

from spec_driver.migrations._folder import ParsedFolder, parse_migration_folder


class TestParseCanonical:
  def test_canonical_name(self) -> None:
    parsed = parse_migration_folder("v0_10_0_001_delta_blocks")
    assert parsed is not None
    assert parsed.version == Version("0.10.0")
    assert parsed.ordinal == 1
    assert parsed.slug == "delta_blocks"
    assert parsed.name == "v0_10_0_001_delta_blocks"

  def test_multi_part_slug(self) -> None:
    parsed = parse_migration_folder("v1_2_3_042_spec_relationships_block")
    assert parsed is not None
    assert parsed.version == Version("1.2.3")
    assert parsed.ordinal == 42
    assert parsed.slug == "spec_relationships_block"


class TestParseNonMatching:
  """Non-matching names return None so the orchestrator skips silently."""

  @pytest.mark.parametrize(
    "name",
    [
      "_protocol.py",
      "__pycache__",
      "0.10.0_001_x",
      "v0.10.0_001_x",
      "v0_10_0_x_slug",
      "v0_10_0_001",
      "",
      "migrations",
    ],
  )
  def test_returns_none(self, name: str) -> None:
    assert parse_migration_folder(name) is None


class TestSortKey:
  def test_version_then_ordinal_total_order(self) -> None:
    raw = [
      "v0_10_0_002_b",
      "v0_10_0_001_a",
      "v0_11_0_001_c",
      "v0_9_0_005_x",
    ]
    parsed: list[ParsedFolder] = [
      p for p in (parse_migration_folder(n) for n in raw) if p is not None
    ]
    parsed.sort(key=lambda p: (p.version, p.ordinal))
    assert [p.name for p in parsed] == [
      "v0_9_0_005_x",
      "v0_10_0_001_a",
      "v0_10_0_002_b",
      "v0_11_0_001_c",
    ]
