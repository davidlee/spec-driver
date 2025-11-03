"""Tests for coverage_check module."""

from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock

from supekku.scripts.lib.workspace import Workspace

from .coverage_check import (
  CoverageMissing,
  check_coverage_completeness,
  check_requirement_coverage,
  format_coverage_error,
  is_coverage_enforcement_enabled,
  parse_requirement_spec_id,
)

# Sample spec with verified coverage
SPEC_WITH_VERIFIED_COVERAGE = """---
id: SPEC-900
slug: test-spec-900
name: Test Spec
status: draft
kind: spec
created: '2025-01-01'
updated: '2025-01-01'
---

# SPEC-900 - Test Spec

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: SPEC-900
entries:
  - artefact: VT-900
    kind: VT
    requirement: SPEC-900.FR-001
    status: verified
    notes: Test passed
```
"""

# Sample spec with planned coverage
SPEC_WITH_PLANNED_COVERAGE = """---
id: SPEC-901
slug: test-spec-901
name: Test Spec
status: draft
kind: spec
created: '2025-01-01'
updated: '2025-01-01'
---

# SPEC-901 - Test Spec

```yaml supekku:verification.coverage@v1
schema: supekku.verification.coverage
version: 1
subject: SPEC-901
entries:
  - artefact: VT-901
    kind: VT
    requirement: SPEC-901.FR-001
    status: planned
    notes: Not yet verified
```
"""

# Sample spec without coverage block
SPEC_WITHOUT_COVERAGE = """---
id: SPEC-902
slug: test-spec-902
name: Test Spec
status: draft
kind: spec
created: '2025-01-01'
updated: '2025-01-01'
---

# SPEC-902 - Test Spec

No coverage block here.
"""

# Sample delta
DELTA_CONTENT = """---
id: DE-900
name: Test Delta
status: draft
kind: delta
applies_to:
  specs:
    - SPEC-900
  requirements:
    - SPEC-900.FR-001
---

# DE-900 - Test Delta
"""


def test_is_coverage_enforcement_enabled_default_true() -> None:
  """Test enforcement is enabled by default."""
  # Clear env var if set
  os.environ.pop("SPEC_DRIVER_ENFORCE_COVERAGE", None)
  assert is_coverage_enforcement_enabled() is True


def test_is_coverage_enforcement_enabled_with_true_values() -> None:
  """Test enforcement recognizes true values."""
  for value in ("true", "True", "TRUE", "1", "yes", "YES", "on", "ON"):
    os.environ["SPEC_DRIVER_ENFORCE_COVERAGE"] = value
    assert is_coverage_enforcement_enabled() is True, f"Failed for value: {value}"


def test_is_coverage_enforcement_enabled_with_false_values() -> None:
  """Test enforcement recognizes false values."""
  for value in ("false", "False", "FALSE", "0", "no", "NO", "off", "OFF"):
    os.environ["SPEC_DRIVER_ENFORCE_COVERAGE"] = value
    assert is_coverage_enforcement_enabled() is False, f"Failed for value: {value}"


def test_parse_requirement_spec_id_valid() -> None:
  """Test parsing valid requirement IDs."""
  assert parse_requirement_spec_id("SPEC-100.FR-001") == "SPEC-100"
  assert parse_requirement_spec_id("PROD-008.FR-001") == "PROD-008"
  assert parse_requirement_spec_id("SPEC-150-foo.NFR-002") == "SPEC-150-foo"


def test_parse_requirement_spec_id_invalid() -> None:
  """Test parsing invalid requirement IDs."""
  assert parse_requirement_spec_id("INVALID") is None
  assert parse_requirement_spec_id("") is None
  assert parse_requirement_spec_id("SPEC-100") is None


def test_check_requirement_coverage_verified() -> None:
  """Test checking requirement with verified coverage."""
  with TemporaryDirectory() as tmpdir:
    spec_path = Path(tmpdir) / "SPEC-900.md"
    spec_path.write_text(SPEC_WITH_VERIFIED_COVERAGE, encoding="utf-8")

    is_verified, status, reason = check_requirement_coverage(
      "SPEC-900.FR-001",
      spec_path,
    )

    assert is_verified is True
    assert status == "verified"
    assert reason == ""


def test_check_requirement_coverage_planned() -> None:
  """Test checking requirement with planned coverage."""
  with TemporaryDirectory() as tmpdir:
    spec_path = Path(tmpdir) / "SPEC-901.md"
    spec_path.write_text(SPEC_WITH_PLANNED_COVERAGE, encoding="utf-8")

    is_verified, status, reason = check_requirement_coverage(
      "SPEC-901.FR-001",
      spec_path,
    )

    assert is_verified is False
    assert status == "planned"
    assert reason == "not_verified"


def test_check_requirement_coverage_missing_block() -> None:
  """Test checking requirement when spec has no coverage block."""
  with TemporaryDirectory() as tmpdir:
    spec_path = Path(tmpdir) / "SPEC-902.md"
    spec_path.write_text(SPEC_WITHOUT_COVERAGE, encoding="utf-8")

    is_verified, status, reason = check_requirement_coverage(
      "SPEC-902.FR-001",
      spec_path,
    )

    assert is_verified is False
    assert status is None
    assert reason == "missing_block"


def test_check_requirement_coverage_missing_entry() -> None:
  """Test checking requirement not listed in coverage block."""
  with TemporaryDirectory() as tmpdir:
    spec_path = Path(tmpdir) / "SPEC-900.md"
    spec_path.write_text(SPEC_WITH_VERIFIED_COVERAGE, encoding="utf-8")

    # Check different requirement
    is_verified, status, reason = check_requirement_coverage(
      "SPEC-900.FR-999",
      spec_path,
    )

    assert is_verified is False
    assert status is None
    assert reason == "missing_entry"


def test_check_requirement_coverage_spec_not_found() -> None:
  """Test checking requirement when spec file doesn't exist."""
  spec_path = Path("/nonexistent/SPEC-900.md")

  is_verified, status, reason = check_requirement_coverage(
    "SPEC-900.FR-001",
    spec_path,
  )

  assert is_verified is False
  assert status is None
  assert reason == "spec_not_found"


def test_check_coverage_completeness_all_verified() -> None:
  """Test completion check when all requirements have verified coverage."""
  with TemporaryDirectory() as tmpdir:
    tmp_path = Path(tmpdir)

    # Create workspace structure
    spec_dir = tmp_path / "specify" / "tech" / "SPEC-900"
    spec_dir.mkdir(parents=True)
    spec_file = spec_dir / "SPEC-900.md"
    spec_file.write_text(SPEC_WITH_VERIFIED_COVERAGE, encoding="utf-8")

    delta_dir = tmp_path / "change" / "deltas" / "DE-900"
    delta_dir.mkdir(parents=True)
    delta_file = delta_dir / "DE-900.md"
    delta_file.write_text(DELTA_CONTENT, encoding="utf-8")

    # Create .git marker so repo root is found
    (tmp_path / ".git").mkdir()

    # Create workspace
    workspace = Workspace(root=tmp_path)
    workspace.specs.reload()
    workspace.delta_registry.sync()

    # Check coverage
    is_complete, missing = check_coverage_completeness("DE-900", workspace)

    assert is_complete is True
    assert len(missing) == 0


def test_check_coverage_completeness_planned_coverage() -> None:
  """Test completion check fails when coverage is planned."""
  with TemporaryDirectory() as tmpdir:
    tmp_path = Path(tmpdir)

    # Create spec with planned coverage
    spec_dir = tmp_path / "specify" / "tech" / "SPEC-901"
    spec_dir.mkdir(parents=True)
    spec_file = spec_dir / "SPEC-901.md"
    spec_file.write_text(SPEC_WITH_PLANNED_COVERAGE, encoding="utf-8")

    # Create delta referencing the spec
    delta_content = DELTA_CONTENT.replace("SPEC-900", "SPEC-901").replace(
      "DE-900",
      "DE-901",
    )
    delta_dir = tmp_path / "change" / "deltas" / "DE-901"
    delta_dir.mkdir(parents=True)
    delta_file = delta_dir / "DE-901.md"
    delta_file.write_text(delta_content, encoding="utf-8")

    # Create .git marker
    (tmp_path / ".git").mkdir()

    # Create workspace
    workspace = Workspace(root=tmp_path)
    workspace.specs.reload()
    workspace.delta_registry.sync()

    # Check coverage
    is_complete, missing = check_coverage_completeness("DE-901", workspace)

    assert is_complete is False
    assert len(missing) == 1
    assert missing[0].requirement_id == "SPEC-901.FR-001"
    assert missing[0].current_status == "planned"
    assert missing[0].reason == "not_verified"


def test_check_coverage_completeness_missing_coverage() -> None:
  """Test completion check fails when spec has no coverage block."""
  with TemporaryDirectory() as tmpdir:
    tmp_path = Path(tmpdir)

    # Create spec without coverage
    spec_dir = tmp_path / "specify" / "tech" / "SPEC-902"
    spec_dir.mkdir(parents=True)
    spec_file = spec_dir / "SPEC-902.md"
    spec_file.write_text(SPEC_WITHOUT_COVERAGE, encoding="utf-8")

    # Create delta referencing the spec
    delta_content = DELTA_CONTENT.replace("SPEC-900", "SPEC-902").replace(
      "DE-900",
      "DE-902",
    )
    delta_dir = tmp_path / "change" / "deltas" / "DE-902"
    delta_dir.mkdir(parents=True)
    delta_file = delta_dir / "DE-902.md"
    delta_file.write_text(delta_content, encoding="utf-8")

    # Create .git marker
    (tmp_path / ".git").mkdir()

    # Create workspace
    workspace = Workspace(root=tmp_path)
    workspace.specs.reload()
    workspace.delta_registry.sync()

    # Check coverage
    is_complete, missing = check_coverage_completeness("DE-902", workspace)

    assert is_complete is False
    assert len(missing) == 1
    assert missing[0].requirement_id == "SPEC-902.FR-001"
    assert missing[0].current_status is None
    assert missing[0].reason == "missing_block"


def test_check_coverage_completeness_no_requirements() -> None:
  """Test completion check succeeds when delta has no requirements."""
  with TemporaryDirectory() as tmpdir:
    tmp_path = Path(tmpdir)

    # Create delta without requirements
    delta_content = """---
id: DE-903
name: Test Delta
status: draft
kind: delta
applies_to:
  specs:
    - SPEC-900
---

# DE-903 - Test Delta
"""
    delta_dir = tmp_path / "change" / "deltas" / "DE-903"
    delta_dir.mkdir(parents=True)
    delta_file = delta_dir / "DE-903.md"
    delta_file.write_text(delta_content, encoding="utf-8")

    # Create .git marker
    (tmp_path / ".git").mkdir()

    # Create workspace
    workspace = Workspace(root=tmp_path)
    workspace.delta_registry.sync()

    # Check coverage
    is_complete, missing = check_coverage_completeness("DE-903", workspace)

    assert is_complete is True
    assert len(missing) == 0


def test_check_coverage_completeness_delta_not_found() -> None:
  """Test completion check when delta doesn't exist."""
  workspace = Mock(spec=Workspace)
  workspace.delta_registry.collect.return_value = {}

  is_complete, missing = check_coverage_completeness("DE-999", workspace)

  assert is_complete is False
  assert len(missing) == 0


def test_format_coverage_error_contains_key_information() -> None:
  """Test error message formatting includes all necessary information."""
  missing = [
    CoverageMissing(
      requirement_id="SPEC-900.FR-001",
      spec_id="SPEC-900",
      spec_path=Path("/repo/specify/tech/SPEC-900/SPEC-900.md"),
      current_status="planned",
      reason="not_verified",
    ),
  ]

  error = format_coverage_error("DE-900", missing, Path("/repo"))

  # Check key elements are present
  assert "DE-900" in error
  assert "SPEC-900.FR-001" in error
  assert "specify/tech/SPEC-900/SPEC-900.md" in error
  assert "Current status: planned" in error
  assert "status: verified" in error
  assert "complete delta DE-900 --force" in error
  assert "RUN.md" in error


def test_format_coverage_error_handles_missing_spec() -> None:
  """Test error message handles missing spec file."""
  missing = [
    CoverageMissing(
      requirement_id="SPEC-999.FR-001",
      spec_id="SPEC-999",
      spec_path=None,
      current_status=None,
      reason="spec_not_found",
    ),
  ]

  error = format_coverage_error("DE-900", missing, Path("/repo"))

  assert "SPEC-999" in error
  assert "not found" in error


def test_format_coverage_error_handles_missing_block() -> None:
  """Test error message handles spec without coverage block."""
  missing = [
    CoverageMissing(
      requirement_id="SPEC-902.FR-001",
      spec_id="SPEC-902",
      spec_path=Path("/repo/specify/tech/SPEC-902/SPEC-902.md"),
      current_status=None,
      reason="missing_block",
    ),
  ]

  error = format_coverage_error("DE-900", missing, Path("/repo"))

  assert "no coverage block" in error
  assert "Add coverage block" in error


def test_format_coverage_error_handles_multiple_requirements() -> None:
  """Test error message handles multiple missing requirements."""
  missing = [
    CoverageMissing(
      requirement_id="SPEC-900.FR-001",
      spec_id="SPEC-900",
      spec_path=Path("/repo/specify/tech/SPEC-900/SPEC-900.md"),
      current_status="planned",
      reason="not_verified",
    ),
    CoverageMissing(
      requirement_id="SPEC-900.FR-002",
      spec_id="SPEC-900",
      spec_path=Path("/repo/specify/tech/SPEC-900/SPEC-900.md"),
      current_status=None,
      reason="missing_entry",
    ),
  ]

  error = format_coverage_error("DE-900", missing, Path("/repo"))

  assert "SPEC-900.FR-001" in error
  assert "SPEC-900.FR-002" in error
  assert error.count("  - artefact: VT-902") >= 1  # Example block shown once
