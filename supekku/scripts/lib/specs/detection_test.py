"""Tests for stub spec detection."""

import pytest

from supekku.scripts.lib.specs.detection import is_stub_spec


def test_is_stub_spec_status_stub(tmp_path):
  """Spec with status='stub' should be detected as stub."""
  spec_file = tmp_path / "SPEC-001.md"
  spec_file.write_text("""---
id: SPEC-001
name: Test Spec
status: stub
kind: tech
---

# SPEC-001 Test Spec

Some content here.
""")

  assert is_stub_spec(spec_file) is True


def test_is_stub_spec_line_count(tmp_path):
  """Spec with ≤30 lines should be detected as stub (fallback)."""
  spec_file = tmp_path / "SPEC-002.md"
  # Create exactly 28 lines (typical auto-generated spec)
  content_lines = (
    ["---", "id: SPEC-002", "name: Test", "status: draft", "kind: tech", "---", ""]
    + ["# Content"]
    + ["Line" for _ in range(20)]
  )
  spec_file.write_text("\n".join(content_lines))

  # Verify it's 28 lines
  actual_lines = spec_file.read_text().count("\n") + 1
  assert actual_lines == 28

  assert is_stub_spec(spec_file) is True


def test_is_stub_spec_modified(tmp_path):
  """Spec with >30 lines and status!='stub' should not be detected as stub."""
  spec_file = tmp_path / "SPEC-003.md"
  content_lines = [
    "---",
    "id: SPEC-003",
    "name: Test",
    "status: draft",
    "kind: tech",
    "---",
    "",
  ] + [f"# Section {i}" for i in range(50)]
  spec_file.write_text("\n".join(content_lines))

  # Verify it's >30 lines
  actual_lines = spec_file.read_text().count("\n") + 1
  assert actual_lines > 30

  assert is_stub_spec(spec_file) is False


def test_is_stub_spec_draft_long(tmp_path):
  """Spec with status='draft' and >30 lines should not be stub."""
  spec_file = tmp_path / "SPEC-004.md"
  content_lines = (
    ["---", "id: SPEC-004", "name: Test", "status: draft", "kind: tech", "---", ""]
    + ["# Section"]
    + [f"Line {i}" for i in range(100)]
  )
  spec_file.write_text("\n".join(content_lines))

  # Verify it's >30 lines
  actual_lines = spec_file.read_text().count("\n") + 1
  assert actual_lines > 30

  assert is_stub_spec(spec_file) is False


def test_is_stub_spec_missing_file(tmp_path):
  """Non-existent spec file should raise FileNotFoundError."""
  spec_file = tmp_path / "DOES-NOT-EXIST.md"

  with pytest.raises(FileNotFoundError):
    is_stub_spec(spec_file)


def test_is_stub_spec_accepted_long(tmp_path):
  """Spec with status='accepted' and >30 lines should not be stub."""
  spec_file = tmp_path / "SPEC-005.md"
  content_lines = (
    [
      "---",
      "id: SPEC-005",
      "name: Test",
      "status: accepted",
      "kind: tech",
      "---",
      "",
    ]
    + ["# Section"]
    + [f"Content line {i}" for i in range(200)]
  )
  spec_file.write_text("\n".join(content_lines))

  assert is_stub_spec(spec_file) is False


def test_is_stub_spec_stub_status_overrides_line_count(tmp_path):
  """Spec with status='stub' should be stub even if >30 lines (edge case)."""
  spec_file = tmp_path / "SPEC-006.md"
  content_lines = (
    ["---", "id: SPEC-006", "name: Test", "status: stub", "kind: tech", "---", ""]
    + ["# Section"]
    + [f"Extra line {i}" for i in range(50)]
  )
  spec_file.write_text("\n".join(content_lines))

  # Verify it's >30 lines
  actual_lines = spec_file.read_text().count("\n") + 1
  assert actual_lines > 30

  # Status='stub' should override line count
  assert is_stub_spec(spec_file) is True
