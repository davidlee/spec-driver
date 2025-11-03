"""Cross-reference integrity tests for policies, standards, and decisions.

Tests cross-reference parsing and filtering across artifact types.

Note: Backlink generation is tested separately in registry tests. These tests
focus on forward reference parsing and filtering capabilities which are the
primary cross-reference features used by CLI commands.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from supekku.scripts.lib.decisions.registry import DecisionRegistry
from supekku.scripts.lib.policies.registry import PolicyRegistry


class TestCrossReferenceIntegrity(unittest.TestCase):
  """Test cross-reference integrity across artifact types."""

  def _setup_test_repo(self, tmpdir: str) -> Path:
    """Set up a minimal test repository."""
    root = Path(tmpdir)
    (root / "specify" / "decisions").mkdir(parents=True)
    (root / "specify" / "policies").mkdir(parents=True)
    (root / "specify" / "standards").mkdir(parents=True)
    (root / ".spec-driver" / "registry").mkdir(parents=True)
    return root

  def test_policy_references_standard(self) -> None:
    """Test that policies can reference standards."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = self._setup_test_repo(tmpdir)

      # Create policy referencing standards
      pol_file = root / "specify" / "policies" / "POL-001-test.md"
      pol_file.write_text(
        """---
id: POL-001
title: Test Policy
status: active
standards: [STD-001, STD-002]
---
# Test Policy
""",
        encoding="utf-8",
      )

      # Load and verify forward reference
      policy_registry = PolicyRegistry(root=root)
      policies = policy_registry.collect()
      assert "POL-001" in policies
      assert "STD-001" in policies["POL-001"].standards
      assert "STD-002" in policies["POL-001"].standards

      # Verify filtering works
      std_policies = policy_registry.filter(standard="STD-001")
      assert len(std_policies) == 1
      assert std_policies[0].id == "POL-001"

  def test_decision_references_policy(self) -> None:
    """Test that decisions can reference policies."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = self._setup_test_repo(tmpdir)

      # Create ADR referencing policies
      adr_file = root / "specify" / "decisions" / "ADR-001-test.md"
      adr_file.write_text(
        """---
id: ADR-001
title: Security Decision
status: accepted
policies: [POL-001, POL-002]
---
# Security Decision
""",
        encoding="utf-8",
      )

      # Load and verify forward reference
      decision_registry = DecisionRegistry(root=root)
      decisions = decision_registry.collect()
      assert "ADR-001" in decisions
      assert "POL-001" in decisions["ADR-001"].policies
      assert "POL-002" in decisions["ADR-001"].policies

      # Verify filtering works
      policy_decisions = decision_registry.filter(policy="POL-001")
      assert len(policy_decisions) == 1
      assert policy_decisions[0].id == "ADR-001"

  def test_decision_references_standard(self) -> None:
    """Test that decisions can reference standards."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = self._setup_test_repo(tmpdir)

      # Create ADR referencing standards
      adr_file = root / "specify" / "decisions" / "ADR-002-test.md"
      adr_file.write_text(
        """---
id: ADR-002
title: Code Decision
status: accepted
standards: [STD-001, STD-002]
---
# Code Decision
""",
        encoding="utf-8",
      )

      # Load and verify forward reference
      decision_registry = DecisionRegistry(root=root)
      decisions = decision_registry.collect()
      assert "ADR-002" in decisions
      assert "STD-001" in decisions["ADR-002"].standards
      assert "STD-002" in decisions["ADR-002"].standards

      # Verify filtering works (from task 4.8)
      std_decisions = decision_registry.filter(standard="STD-001")
      assert len(std_decisions) == 1
      assert std_decisions[0].id == "ADR-002"

  def test_combined_cross_references(self) -> None:
    """Test filtering with multiple cross-reference types."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = self._setup_test_repo(tmpdir)

      # Create ADR with both policy and standard references
      adr_file = root / "specify" / "decisions" / "ADR-003-test.md"
      adr_file.write_text(
        """---
id: ADR-003
title: Comprehensive Decision
status: accepted
policies: [POL-001]
standards: [STD-001]
---
# Comprehensive Decision
""",
        encoding="utf-8",
      )

      # Load and verify both references
      decision_registry = DecisionRegistry(root=root)
      decisions = decision_registry.collect()
      assert "ADR-003" in decisions
      assert "POL-001" in decisions["ADR-003"].policies
      assert "STD-001" in decisions["ADR-003"].standards

      # Verify filtering by policy works
      policy_decisions = decision_registry.filter(policy="POL-001")
      assert len(policy_decisions) == 1
      assert policy_decisions[0].id == "ADR-003"

      # Verify filtering by standard works
      std_decisions = decision_registry.filter(standard="STD-001")
      assert len(std_decisions) == 1
      assert std_decisions[0].id == "ADR-003"


if __name__ == "__main__":
  unittest.main()
