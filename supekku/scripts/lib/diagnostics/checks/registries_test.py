"""Tests for registry integrity checks."""

from __future__ import annotations

import unittest
from dataclasses import dataclass, field
from pathlib import Path

from supekku.scripts.lib.diagnostics.checks.registries import (
  CATEGORY,
  check_registries,
)


@dataclass
class _FakeRegistry:
  """Minimal registry stub with collect()."""

  items: dict = field(default_factory=dict)
  error: Exception | None = None

  def collect(self) -> dict:
    if self.error:
      raise self.error
    return self.items


@dataclass
class _FakeWorkspace:
  root: Path
  _specs: _FakeRegistry = field(default_factory=_FakeRegistry)
  _delta_registry: _FakeRegistry = field(default_factory=_FakeRegistry)
  _revision_registry: _FakeRegistry = field(default_factory=_FakeRegistry)
  _audit_registry: _FakeRegistry = field(default_factory=_FakeRegistry)
  _decisions: _FakeRegistry = field(default_factory=_FakeRegistry)

  @property
  def specs(self) -> _FakeRegistry:
    return self._specs

  @property
  def delta_registry(self) -> _FakeRegistry:
    return self._delta_registry

  @property
  def revision_registry(self) -> _FakeRegistry:
    return self._revision_registry

  @property
  def audit_registry(self) -> _FakeRegistry:
    return self._audit_registry

  @property
  def decisions(self) -> _FakeRegistry:
    return self._decisions


class TestCheckRegistries(unittest.TestCase):
  """Tests for check_registries function."""

  def test_all_registries_load_pass(self) -> None:
    """All registries loading successfully should produce pass results."""
    ws = _FakeWorkspace(
      root=Path("/fake"),
      _specs=_FakeRegistry(items={"SPEC-001": "a", "SPEC-002": "b"}),
      _delta_registry=_FakeRegistry(items={"DE-001": "x"}),
      _revision_registry=_FakeRegistry(items={}),
      _audit_registry=_FakeRegistry(items={}),
      _decisions=_FakeRegistry(items={"ADR-001": "d"}),
    )
    results = check_registries(ws)
    assert len(results) == 5
    assert all(r.status == "pass" for r in results)

  def test_item_count_in_message(self) -> None:
    """Pass results should report item counts."""
    ws = _FakeWorkspace(
      root=Path("/fake"),
      _specs=_FakeRegistry(items={"S1": 1, "S2": 2, "S3": 3}),
    )
    results = check_registries(ws)
    specs_result = next(r for r in results if r.name == "specs")
    assert "3 items" in specs_result.message

  def test_registry_error_produces_fail(self) -> None:
    """A registry that raises on collect() should produce a fail result."""
    ws = _FakeWorkspace(
      root=Path("/fake"),
      _specs=_FakeRegistry(error=ValueError("bad frontmatter in SPEC-099")),
    )
    results = check_registries(ws)
    specs_result = next(r for r in results if r.name == "specs")
    assert specs_result.status == "fail"
    assert "bad frontmatter" in specs_result.message
    assert specs_result.suggestion is not None

  def test_one_broken_others_still_checked(self) -> None:
    """A failure in one registry should not prevent checking others."""
    ws = _FakeWorkspace(
      root=Path("/fake"),
      _delta_registry=_FakeRegistry(error=OSError("disk error")),
    )
    results = check_registries(ws)
    assert len(results) == 5
    delta_result = next(r for r in results if r.name == "deltas")
    assert delta_result.status == "fail"
    non_delta = [r for r in results if r.name != "deltas"]
    assert all(r.status == "pass" for r in non_delta)

  def test_empty_registry_passes(self) -> None:
    """An empty registry should still pass (0 items)."""
    ws = _FakeWorkspace(root=Path("/fake"))
    results = check_registries(ws)
    assert all(r.status == "pass" for r in results)
    assert all("0 items" in r.message for r in results)

  def test_all_results_have_registries_category(self) -> None:
    """Every result should use the registries category."""
    ws = _FakeWorkspace(root=Path("/fake"))
    results = check_registries(ws)
    assert all(r.category == CATEGORY for r in results)


if __name__ == "__main__":
  unittest.main()
