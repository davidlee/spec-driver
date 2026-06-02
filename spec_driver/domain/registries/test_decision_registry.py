"""Tests for DecisionRegistry on the FrontmatterFileRegistry base."""

from __future__ import annotations

from pathlib import Path

import pytest

from spec_driver.domain.records.decision import DecisionRecord
from spec_driver.domain.registries.decision import DecisionRegistry
from spec_driver.domain.registries.frontmatter import RegistryProtocol


@pytest.fixture
def registry() -> DecisionRegistry:
  return DecisionRegistry()


class TestDecisionRegistryProtocol:
  """ADR-009 read-surface conformance."""

  def test_isinstance_satisfies_protocol(self, registry: DecisionRegistry) -> None:
    assert isinstance(registry, RegistryProtocol)

  def test_protocol_has_expected_methods(self) -> None:
    assert hasattr(RegistryProtocol, "find")
    assert hasattr(RegistryProtocol, "collect")
    assert hasattr(RegistryProtocol, "iter")
    # filter is deliberately excluded (ER-1)
    assert not hasattr(RegistryProtocol, "filter")


class TestDecisionRegistryCollect:
  """collect() discovers ADR-*.md files."""

  def test_collect_returns_dict_keyed_by_id(self, registry: DecisionRegistry) -> None:
    decisions = registry.collect()
    assert isinstance(decisions, dict)
    assert len(decisions) > 0
    for key, value in decisions.items():
      assert key.startswith("ADR-")
      assert isinstance(value, DecisionRecord)
      assert value.id == key

  def test_collect_populates_basic_fields(self, registry: DecisionRegistry) -> None:
    decisions = registry.collect()
    for record in decisions.values():
      assert record.id
      assert record.title
      assert record.status
      assert record.path


class TestDecisionRegistryFind:
  """find() looks up by ID."""

  def test_find_existing(self, registry: DecisionRegistry) -> None:
    decisions = registry.collect()
    first_id = next(iter(decisions))
    record = registry.find(first_id)
    assert record is not None
    assert record.id == first_id

  def test_find_nonexistent(self, registry: DecisionRegistry) -> None:
    assert registry.find("ADR-99999") is None


class TestDecisionRegistryIter:
  """iter() yields records, optionally filtered by status."""

  def test_iter_unfiltered(self, registry: DecisionRegistry) -> None:
    records = list(registry.iter())
    assert len(records) > 0
    assert all(isinstance(r, DecisionRecord) for r in records)

  def test_iter_filtered_by_status(self, registry: DecisionRegistry) -> None:
    accepted = list(registry.iter(status="accepted"))
    for r in accepted:
      assert r.status == "accepted"


class TestDecisionRegistryFilter:
  """filter() with kw-only criteria."""

  def test_filter_no_criteria_returns_all(self, registry: DecisionRegistry) -> None:
    all_records = registry.filter()
    assert len(all_records) > 0

  def test_filter_by_tag(self, registry: DecisionRegistry) -> None:
    # Find a tag that exists
    all_records = registry.collect()
    for record in all_records.values():
      if record.tags:
        tag = record.tags[0]
        filtered = registry.filter(tag=tag)
        assert len(filtered) > 0
        for r in filtered:
          assert tag in r.tags
        return
    pytest.skip("No ADRs with tags found")

  def test_filter_nonexistent_tag_returns_empty(
    self, registry: DecisionRegistry,
  ) -> None:
    result = registry.filter(tag="__nonexistent_tag_xyz__")
    assert result == []


class TestDecisionRegistryWrite:
  """write() produces valid YAML."""

  def test_write_creates_file(self, registry: DecisionRegistry, tmp_path: Path) -> None:
    output = tmp_path / "decisions.yaml"
    registry.write(path=output)
    assert output.exists()
    content = output.read_text()
    assert "decisions:" in content

  def test_write_is_idempotent(
    self, registry: DecisionRegistry, tmp_path: Path,
  ) -> None:
    output = tmp_path / "decisions.yaml"
    records = registry.collect()
    registry.write(path=output, records=records)
    first = output.read_text()
    registry.write(path=output, records=records)
    second = output.read_text()
    assert first == second


class TestDecisionRegistrySync:
  """sync() collects + writes."""

  def test_sync(self, registry: DecisionRegistry) -> None:
    registry.sync()
    assert registry.output_path.exists()
