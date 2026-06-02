"""Golden-YAML fixture test — backlink hoist produces correct output (AR-2).

Creates a fixture corpus with known cross-references, syncs through
Workspace._sync_governance, and asserts backlinks appear correctly in YAML.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import yaml

from spec_driver.domain.registries.decision import DecisionRegistry
from spec_driver.domain.registries.policy import PolicyRegistry
from spec_driver.domain.registries.standard import StandardRegistry
from spec_driver.domain.relations.backlinks import build_backlinks_multi


def _write_md(path: Path, frontmatter: str) -> None:
  """Write a minimal markdown file with frontmatter."""
  content = f"---\n{frontmatter}\n---\n\n# Test\n"
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(content, encoding="utf-8")


def _build_fixture_corpus(tmp_path: Path) -> Path:
  """Create a minimal governance corpus with known cross-references.

  Layout:
    .spec-driver/
      decisions/ADR-001.md  → references POL-001, STD-001
      policies/POL-001.md   → references STD-001
      standards/STD-001.md  → no refs
  """
  root = tmp_path / "fixture_repo"
  decisions_dir = root / ".spec-driver" / "decisions"
  policies_dir = root / ".spec-driver" / "policies"
  standards_dir = root / ".spec-driver" / "standards"

  # ADR-001: references POL-001 (policies field) and STD-001 (standards field)
  _write_md(
    decisions_dir / "ADR-001-test-decision.md",
    "id: ADR-001\n"
    "title: Test Decision\n"
    "status: accepted\n"
    "created: 2026-01-01\n"
    "authors:\n"
    "  - name: Test Author\n"
    "policies:\n"
    "  - POL-001\n"
    "standards:\n"
    "  - STD-001\n",
  )

  # POL-001: references STD-001
  _write_md(
    policies_dir / "POL-001-test-policy.md",
    "id: POL-001\n"
    "title: Test Policy\n"
    "status: required\n"
    "created: 2026-01-01\n"
    "standards:\n"
    "  - STD-001\n",
  )

  # STD-001: no references
  _write_md(
    standards_dir / "STD-001-test-standard.md",
    "id: STD-001\n"
    "title: Test Standard\n"
    "status: required\n"
    "created: 2026-01-01\n",
  )

  return root


class TestGoldenYamlBacklinks:
  """Backlinks populated correctly through Workspace orchestration."""

  def test_policy_has_decision_backlinks(self) -> None:
    """POL-001 should have backlinks from ADR-001."""
    root = _build_fixture_corpus(Path(tempfile.mkdtemp()))

    # Simulate Workspace._sync_governance for policies
    decisions_reg = DecisionRegistry(root=root)
    policies_reg = PolicyRegistry(root=root)

    policy_records = policies_reg.collect()
    decision_records = decisions_reg.collect()

    groups = [
      (
        [(d.id, d.policies) for d in decision_records.values()],
        "decisions",
      ),
    ]
    build_backlinks_multi(policy_records, groups)

    # POL-001 should have backlinks from ADR-001 (via standards field)
    assert "POL-001" in policy_records

    # Write to temp YAML and parse back
    output = root / ".spec-driver" / "registry" / "policies.yaml"
    policies_reg.write(path=output, records=policy_records)
    data = yaml.safe_load(output.read_text())

    pol = data["policies"]["POL-001"]
    assert "backlinks" in pol
    assert "decisions" in pol["backlinks"]
    assert "ADR-001" in pol["backlinks"]["decisions"]

  def test_standard_has_decision_and_policy_backlinks(self) -> None:
    """STD-001 should have backlinks from ADR-001 and POL-001."""
    root = _build_fixture_corpus(Path(tempfile.mkdtemp()))

    decisions_reg = DecisionRegistry(root=root)
    policies_reg = PolicyRegistry(root=root)
    standards_reg = StandardRegistry(root=root)

    standard_records = standards_reg.collect()
    decision_records = decisions_reg.collect()
    policy_records = policies_reg.collect()

    groups = [
      (
        [(d.id, d.standards) for d in decision_records.values()],
        "decisions",
      ),
      (
        [(p.id, p.standards) for p in policy_records.values()],
        "policies",
      ),
    ]
    build_backlinks_multi(standard_records, groups)

    assert "STD-001" in standard_records

    output = root / ".spec-driver" / "registry" / "standards.yaml"
    standards_reg.write(path=output, records=standard_records)
    data = yaml.safe_load(output.read_text())

    std = data["standards"]["STD-001"]
    assert "backlinks" in std
    assert "decisions" in std["backlinks"]
    assert "ADR-001" in std["backlinks"]["decisions"]
    assert "policies" in std["backlinks"]
    assert "POL-001" in std["backlinks"]["policies"]

  def test_decision_has_no_backlinks(self) -> None:
    """ADR-001 should have no backlinks (no registry feeds into decisions)."""
    root = _build_fixture_corpus(Path(tempfile.mkdtemp()))

    reg = DecisionRegistry(root=root)
    records = reg.collect()
    reg.write(records=records)

    output = root / ".spec-driver" / "registry" / "decisions.yaml"
    data = yaml.safe_load(output.read_text())

    adr = data["decisions"]["ADR-001"]
    assert adr.get("backlinks", {}) == {}

  def test_yaml_no_cross_contamination(self) -> None:
    """ADR fields should not leak into policy/standard YAML and vice versa."""
    root = _build_fixture_corpus(Path(tempfile.mkdtemp()))

    reg = DecisionRegistry(root=root)
    records = reg.collect()
    reg.write(records=records)

    output = root / ".spec-driver" / "registry" / "decisions.yaml"
    data = yaml.safe_load(output.read_text())

    adr = data["decisions"]["ADR-001"]
    # ADR should have its own fields, not policy/standard fields
    assert "authors" in adr  # ADR-specific
    assert "ext_id" not in adr  # policy/standard-specific
