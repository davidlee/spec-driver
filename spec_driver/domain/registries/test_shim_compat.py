"""Shim compatibility suite — proves legacy imports are drop-in replacements (ER-3).

Tests import from supekku.* registry paths, not canonical paths.
"""

from __future__ import annotations

import pytest

from spec_driver.domain.registries.frontmatter import RegistryProtocol

# ── Legacy-path imports (the shims under test) ──────────────────────────────

from supekku.scripts.lib.decisions.registry import (  # noqa: E402
  DecisionRecord,
  DecisionRegistry,
)
from supekku.scripts.lib.policies.registry import (  # noqa: E402
  PolicyRecord,
  PolicyRegistry,
)
from supekku.scripts.lib.standards.registry import (  # noqa: E402
  StandardRecord,
  StandardRegistry,
)


class TestShimImports:
  """Legacy import paths resolve correctly."""

  def test_decision_imports(self) -> None:
    assert DecisionRecord is not None
    assert DecisionRegistry is not None

  def test_policy_imports(self) -> None:
    assert PolicyRecord is not None
    assert PolicyRegistry is not None

  def test_standard_imports(self) -> None:
    assert StandardRecord is not None
    assert StandardRegistry is not None


class TestShimProtocolConformance:
  """Shim-imported registries satisfy RegistryProtocol."""

  def test_decision_satisfies_protocol(self) -> None:
    assert isinstance(DecisionRegistry(), RegistryProtocol)

  def test_policy_satisfies_protocol(self) -> None:
    assert isinstance(PolicyRegistry(), RegistryProtocol)

  def test_standard_satisfies_protocol(self) -> None:
    assert isinstance(StandardRegistry(), RegistryProtocol)


class TestShimCollect:
  """Shim-imported registries can collect records."""

  def test_decision_collect(self) -> None:
    reg = DecisionRegistry()
    records = reg.collect()
    assert len(records) > 0
    for r in records.values():
      assert isinstance(r, DecisionRecord)

  def test_policy_collect(self) -> None:
    reg = PolicyRegistry()
    records = reg.collect()
    # Policies may be empty — acceptable
    for r in records.values():
      assert isinstance(r, PolicyRecord)

  def test_standard_collect(self) -> None:
    reg = StandardRegistry()
    records = reg.collect()
    # Standards may be empty — acceptable
    for r in records.values():
      assert isinstance(r, StandardRecord)


class TestShimFind:
  """Shim-imported registries support find()."""

  def test_decision_find(self) -> None:
    reg = DecisionRegistry()
    decisions = reg.collect()
    if decisions:
      first_id = next(iter(decisions))
      assert reg.find(first_id) is not None

  def test_policy_find_nonexistent(self) -> None:
    reg = PolicyRegistry()
    assert reg.find("POL-99999") is None

  def test_standard_find_nonexistent(self) -> None:
    reg = StandardRegistry()
    assert reg.find("STD-99999") is None


class TestShimIter:
  """Shim-imported registries support iter()."""

  def test_decision_iter(self) -> None:
    reg = DecisionRegistry()
    records = list(reg.iter())
    assert len(records) > 0

  def test_policy_iter(self) -> None:
    reg = PolicyRegistry()
    list(reg.iter())  # does not crash

  def test_standard_iter(self) -> None:
    reg = StandardRegistry()
    list(reg.iter())  # does not crash


class TestShimAll:
  """Shim modules expose __all__."""

  def test_decision_all(self) -> None:
    from supekku.scripts.lib.decisions import registry as mod

    assert hasattr(mod, "__all__")
    assert "DecisionRecord" in mod.__all__
    assert "DecisionRegistry" in mod.__all__

  def test_policy_all(self) -> None:
    from supekku.scripts.lib.policies import registry as mod

    assert hasattr(mod, "__all__")
    assert "PolicyRecord" in mod.__all__
    assert "PolicyRegistry" in mod.__all__

  def test_standard_all(self) -> None:
    from supekku.scripts.lib.standards import registry as mod

    assert hasattr(mod, "__all__")
    assert "StandardRecord" in mod.__all__
    assert "StandardRegistry" in mod.__all__
