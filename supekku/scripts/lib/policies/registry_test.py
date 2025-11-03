"""Tests for policy registry module."""

from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

import yaml

from .registry import PolicyRecord, PolicyRegistry


class TestPolicyRecord(unittest.TestCase):
  """Tests for PolicyRecord dataclass."""

  def test_to_dict_minimal(self) -> None:
    """Test serialization with minimal fields."""
    record = PolicyRecord(id="POL-001", title="Test Policy", status="required")

    result = record.to_dict(Path("/tmp"))

    assert result["id"] == "POL-001"
    assert result["title"] == "Test Policy"
    assert result["status"] == "required"
    assert result["summary"] == ""
    assert "owners" not in result  # Empty lists are omitted

  def test_to_dict_full(self) -> None:
    """Test serialization with all fields populated."""
    record = PolicyRecord(
      id="POL-002",
      title="Full Policy",
      status="required",
      created=date(2024, 1, 1),
      updated=date(2024, 1, 3),
      reviewed=date(2024, 1, 4),
      owners=["team-alpha"],
      supersedes=["POL-001"],
      standards=["STD-001"],
      specs=["SPEC-100"],
      requirements=["SPEC-100.FR-001"],
      tags=["security", "compliance"],
      summary="A comprehensive policy",
      path="/path/to/file.md",
    )

    result = record.to_dict(Path("/"))

    assert result["created"] == "2024-01-01"
    assert result["updated"] == "2024-01-03"
    assert result["reviewed"] == "2024-01-04"
    assert result["owners"] == ["team-alpha"]
    assert result["supersedes"] == ["POL-001"]
    assert result["standards"] == ["STD-001"]
    assert result["specs"] == ["SPEC-100"]
    assert result["requirements"] == ["SPEC-100.FR-001"]
    assert result["tags"] == ["security", "compliance"]
    assert result["summary"] == "A comprehensive policy"


class TestPolicyRegistry(unittest.TestCase):
  """Tests for PolicyRegistry class."""

  def setUp(self) -> None:
    """Set up test fixtures."""
    self.test_dir = tempfile.mkdtemp()
    self.root = Path(self.test_dir)

    # Create directory structure
    self.policies_dir = self.root / "specify" / "policies"
    self.policies_dir.mkdir(parents=True)

    self.registry_dir = self.root / "specify" / ".registry"
    self.registry_dir.mkdir(parents=True)

  def test_init(self) -> None:
    """Test registry initialization."""
    registry = PolicyRegistry(root=self.root)

    assert registry.root == self.root
    assert registry.directory == self.policies_dir
    assert registry.output_path == self.registry_dir / "policies.yaml"

  def test_collect_empty(self) -> None:
    """Test collecting policies from empty directory."""
    registry = PolicyRegistry(root=self.root)
    policies = registry.collect()

    assert len(policies) == 0

  def test_collect_single_policy(self) -> None:
    """Test collecting a single policy."""
    # Create a test policy file
    policy_content = """---
id: POL-001
title: 'POL-001: Code must have tests'
status: required
created: '2024-01-01'
summary: All production code must be accompanied by automated tests
tags:
  - quality
  - testing
---

# POL-001: Code must have tests

## Statement
All production code must be accompanied by automated tests.
"""
    policy_file = self.policies_dir / "POL-001-code-must-have-tests.md"
    policy_file.write_text(policy_content, encoding="utf-8")

    registry = PolicyRegistry(root=self.root)
    policies = registry.collect()

    assert len(policies) == 1
    assert "POL-001" in policies

    policy = policies["POL-001"]
    assert policy.id == "POL-001"
    assert policy.title == "POL-001: Code must have tests"
    assert policy.status == "required"
    assert policy.created == date(2024, 1, 1)
    assert (
      policy.summary
      == "All production code must be accompanied by automated tests"
    )
    assert policy.tags == ["quality", "testing"]

  def test_write_registry(self) -> None:
    """Test writing registry to YAML."""
    # Create a test policy file
    policy_content = """---
id: POL-001
title: 'POL-001: Test Policy'
status: required
created: '2024-01-01'
---

# POL-001: Test Policy
"""
    policy_file = self.policies_dir / "POL-001-test-policy.md"
    policy_file.write_text(policy_content, encoding="utf-8")

    registry = PolicyRegistry(root=self.root)
    registry.write()

    # Check that YAML file was created
    yaml_path = self.registry_dir / "policies.yaml"
    assert yaml_path.exists()

    # Load and verify YAML content
    with yaml_path.open(encoding="utf-8") as f:
      data = yaml.safe_load(f)

    assert "policies" in data
    assert "POL-001" in data["policies"]
    assert data["policies"]["POL-001"]["title"] == "POL-001: Test Policy"
    assert data["policies"]["POL-001"]["status"] == "required"

  def test_iter_all(self) -> None:
    """Test iterating over all policies."""
    # Create multiple policy files
    for i in range(1, 4):
      policy_content = f"""---
id: POL-{i:03d}
title: 'POL-{i:03d}: Policy {i}'
status: required
---

# POL-{i:03d}: Policy {i}
"""
      policy_file = self.policies_dir / f"POL-{i:03d}-policy-{i}.md"
      policy_file.write_text(policy_content, encoding="utf-8")

    registry = PolicyRegistry(root=self.root)
    policies = list(registry.iter())

    assert len(policies) == 3

  def test_iter_filtered_by_status(self) -> None:
    """Test iterating with status filter."""
    # Create policies with different statuses
    statuses = ["draft", "required", "deprecated"]
    for i, status in enumerate(statuses, 1):
      policy_content = f"""---
id: POL-{i:03d}
title: 'POL-{i:03d}: Policy {i}'
status: {status}
---

# POL-{i:03d}: Policy {i}
"""
      policy_file = self.policies_dir / f"POL-{i:03d}-policy-{i}.md"
      policy_file.write_text(policy_content, encoding="utf-8")

    registry = PolicyRegistry(root=self.root)
    required_policies = list(registry.iter(status="required"))

    assert len(required_policies) == 1
    assert required_policies[0].status == "required"

  def test_find(self) -> None:
    """Test finding a specific policy by ID."""
    policy_content = """---
id: POL-001
title: 'POL-001: Test Policy'
status: required
---

# POL-001: Test Policy
"""
    policy_file = self.policies_dir / "POL-001-test-policy.md"
    policy_file.write_text(policy_content, encoding="utf-8")

    registry = PolicyRegistry(root=self.root)
    policy = registry.find("POL-001")

    assert policy is not None
    assert policy.id == "POL-001"

    # Test not found
    not_found = registry.find("POL-999")
    assert not_found is None

  def test_filter_by_tag(self) -> None:
    """Test filtering policies by tag."""
    # Create policies with different tags
    policy_1 = """---
id: POL-001
title: 'POL-001: Policy 1'
status: required
tags:
  - security
---

# POL-001
"""
    policy_2 = """---
id: POL-002
title: 'POL-002: Policy 2'
status: required
tags:
  - quality
---

# POL-002
"""
    (self.policies_dir / "POL-001.md").write_text(policy_1, encoding="utf-8")
    (self.policies_dir / "POL-002.md").write_text(policy_2, encoding="utf-8")

    registry = PolicyRegistry(root=self.root)
    security_policies = registry.filter(tag="security")

    assert len(security_policies) == 1
    assert security_policies[0].id == "POL-001"


if __name__ == "__main__":
  unittest.main()
