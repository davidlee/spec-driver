"""Tests for spec_driver.domain.relations.backlinks."""

from __future__ import annotations

from dataclasses import dataclass, field

from spec_driver.domain.relations.backlinks import (
  build_backlinks,
  build_backlinks_multi,
)


@dataclass
class FakeRecord:
  """Minimal record implementing BacklinkTarget protocol."""

  id: str
  backlinks: dict[str, list[str]] = field(default_factory=dict)


class TestBuildBacklinks:
  """Tests for build_backlinks()."""

  def test_basic_backlink(self) -> None:
    targets = {"POL-001": FakeRecord(id="POL-001")}
    sources = [("ADR-001", ["POL-001"])]
    build_backlinks(targets, sources, "decisions")
    assert targets["POL-001"].backlinks == {"decisions": ["ADR-001"]}

  def test_multiple_sources_same_target(self) -> None:
    targets = {"POL-001": FakeRecord(id="POL-001")}
    sources = [("ADR-001", ["POL-001"]), ("ADR-002", ["POL-001"])]
    build_backlinks(targets, sources, "decisions")
    assert targets["POL-001"].backlinks == {"decisions": ["ADR-001", "ADR-002"]}

  def test_source_referencing_unknown_target_ignored(self) -> None:
    targets = {"POL-001": FakeRecord(id="POL-001")}
    sources = [("ADR-001", ["POL-999"])]
    build_backlinks(targets, sources, "decisions")
    assert targets["POL-001"].backlinks == {}

  def test_empty_sources(self) -> None:
    targets = {"POL-001": FakeRecord(id="POL-001", backlinks={"old": ["X"]})}
    build_backlinks(targets, [], "decisions")
    assert targets["POL-001"].backlinks == {}

  def test_clear_false_preserves_existing(self) -> None:
    targets = {"POL-001": FakeRecord(id="POL-001", backlinks={"old": ["X"]})}
    sources = [("ADR-001", ["POL-001"])]
    build_backlinks(targets, sources, "decisions", clear=False)
    assert targets["POL-001"].backlinks == {"old": ["X"], "decisions": ["ADR-001"]}

  def test_clear_true_removes_existing(self) -> None:
    targets = {"POL-001": FakeRecord(id="POL-001", backlinks={"old": ["X"]})}
    sources = [("ADR-001", ["POL-001"])]
    build_backlinks(targets, sources, "decisions", clear=True)
    assert targets["POL-001"].backlinks == {"decisions": ["ADR-001"]}

  def test_multiple_targets(self) -> None:
    targets = {
      "POL-001": FakeRecord(id="POL-001"),
      "POL-002": FakeRecord(id="POL-002"),
    }
    sources = [("ADR-001", ["POL-001", "POL-002"])]
    build_backlinks(targets, sources, "decisions")
    assert targets["POL-001"].backlinks == {"decisions": ["ADR-001"]}
    assert targets["POL-002"].backlinks == {"decisions": ["ADR-001"]}

  def test_generator_sources(self) -> None:
    """Sources can be any iterable, not just a list."""
    targets = {"POL-001": FakeRecord(id="POL-001")}
    sources = (("ADR-001", ["POL-001"]) for _ in range(1))
    build_backlinks(targets, sources, "decisions")
    assert targets["POL-001"].backlinks == {"decisions": ["ADR-001"]}


class TestBuildBacklinksMulti:
  """Tests for build_backlinks_multi()."""

  def test_two_categories(self) -> None:
    targets = {"STD-001": FakeRecord(id="STD-001")}
    build_backlinks_multi(
      targets,
      [
        ([("ADR-001", ["STD-001"])], "decisions"),
        ([("POL-001", ["STD-001"])], "policies"),
      ],
    )
    assert targets["STD-001"].backlinks == {
      "decisions": ["ADR-001"],
      "policies": ["POL-001"],
    }

  def test_clears_once_before_accumulating(self) -> None:
    targets = {"STD-001": FakeRecord(id="STD-001", backlinks={"old": ["X"]})}
    build_backlinks_multi(
      targets,
      [
        ([("ADR-001", ["STD-001"])], "decisions"),
      ],
    )
    assert "old" not in targets["STD-001"].backlinks
    assert targets["STD-001"].backlinks == {"decisions": ["ADR-001"]}

  def test_empty_groups(self) -> None:
    targets = {"STD-001": FakeRecord(id="STD-001", backlinks={"old": ["X"]})}
    build_backlinks_multi(targets, [])
    assert targets["STD-001"].backlinks == {}
