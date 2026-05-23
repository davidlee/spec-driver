"""Tests for spec requirements migration (DE-140 P04).

Covers VA-140-001 through VA-140-005.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from spec_driver.migrations.spec_requirements.migration import (
  DRIFT_ACCEPTANCE_PLACEHOLDER,
  DRIFT_DESCRIPTION_PLACEHOLDER,
  DRIFT_REQUIREMENT_UNPARSEABLE,
  DriftEntry,
  ParsedRequirement,
  _detect_drift,
  _insert_block,
  _parse_requirements,
  _render_block,
  _validate_written_block,
  apply_migration,
  has_requirements_block,
  migrate_spec,
  write_drift_ledger,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_SAMPLE_SPEC = """\
---
id: PROD-099
name: Test Spec
status: draft
kind: prod
---

# PROD-099 — Test Spec

## Requirements

- **FR-001**: First requirement
- **FR-002**(core)[tag1, tag2]: Second requirement
- **NF-001**: Non-functional requirement
"""

_SAMPLE_SPEC_WITH_BLOCK = """\
---
id: PROD-099
name: Test Spec
status: draft
kind: prod
---

# PROD-099 — Test Spec

```yaml supekku:spec.requirements@v1
schema: supekku.spec.requirements
version: 1
spec: PROD-099
requirements: []
```

## Requirements

- **FR-001**: First requirement
"""


# ---------------------------------------------------------------------------
# Parsing tests
# ---------------------------------------------------------------------------


class TestParseRequirements:
  def test_parses_basic_bullets(self):
    body = (
      "## Requirements\n\n"
      "- **FR-001**: First req\n"
      "- **NF-001**: Non-func req\n"
    )
    result = _parse_requirements(body)
    assert len(result) == 2
    assert result[0] == ParsedRequirement(
      id="FR-001", title="First req", kind="functional",
    )
    assert result[1] == ParsedRequirement(
      id="NF-001",
      title="Non-func req",
      kind="non-functional",
    )

  def test_parses_category_and_tags(self):
    body = "- **FR-001**(core)[tag1, tag2]: Req with extras\n"
    result = _parse_requirements(body)
    assert len(result) == 1
    assert result[0].category == "core"
    assert result[0].tags == ["tag1", "tag2"]

  def test_empty_body_returns_empty(self):
    assert _parse_requirements("") == []

  def test_ignores_non_requirement_lines(self):
    body = "## Section\n\nSome text about FR-001.\n"
    assert _parse_requirements(body) == []


# ---------------------------------------------------------------------------
# Rendering tests
# ---------------------------------------------------------------------------


class TestRenderBlock:
  def test_empty_requirements(self):
    block = _render_block("PROD-099", [])
    assert "requirements: []" in block
    assert "supekku:spec.requirements@v1" in block
    assert "spec: PROD-099" in block

  def test_renders_requirements(self):
    reqs = [
      ParsedRequirement(
        id="FR-001", title="First", kind="functional",
      ),
      ParsedRequirement(
        id="NF-001", title="Non-func", kind="non-functional",
        category="perf", tags=["fast"],
      ),
    ]
    block = _render_block("PROD-099", reqs)
    assert "- id: FR-001" in block
    assert "  title: First" in block
    assert '  description: ""' in block
    assert "  acceptance_criteria: []" in block
    assert "  category: perf" in block
    assert "  tags: [fast]" in block


# ---------------------------------------------------------------------------
# Block insertion tests
# ---------------------------------------------------------------------------


class TestInsertBlock:
  def test_inserts_before_first_heading(self):
    text = "---\nid: X\n---\n\n# Heading\n\nBody\n"
    block = "```yaml marker\ncontent\n```"
    result = _insert_block(text, block)
    assert result.index("```yaml marker") < result.index(
      "# Heading"
    )

  def test_inserts_after_existing_blocks(self):
    text = (
      "---\nid: X\n---\n\n"
      "```yaml other\nstuff\n```\n\n"
      "# Heading\n"
    )
    block = "```yaml marker\ncontent\n```"
    result = _insert_block(text, block)
    assert result.index("```yaml marker") > result.index(
      "```yaml other"
    )
    assert result.index("```yaml marker") < result.index(
      "# Heading"
    )


# ---------------------------------------------------------------------------
# Guard tests (VA-140-004)
# ---------------------------------------------------------------------------


class TestGuard:
  def test_detects_existing_block(self):
    assert has_requirements_block(_SAMPLE_SPEC_WITH_BLOCK)

  def test_no_block(self):
    assert not has_requirements_block(_SAMPLE_SPEC)


# ---------------------------------------------------------------------------
# migrate_spec (pure transform) tests
# ---------------------------------------------------------------------------


class TestMigrateSpec:
  def test_transforms_prose_to_block(self):
    result = migrate_spec("PROD-099", _SAMPLE_SPEC)
    assert result.changed
    assert result.requirements_count == 3
    assert "supekku:spec.requirements@v1" in result.text
    assert "- id: FR-001" in result.text
    assert "- id: NF-001" in result.text

  def test_refuses_if_block_exists(self):
    """VA-140-004: refuses if block already present."""
    result = migrate_spec(
      "PROD-099", _SAMPLE_SPEC_WITH_BLOCK,
    )
    assert not result.changed
    assert result.requirements_count == 0

  def test_no_requirements_no_change(self):
    text = (
      "---\nid: X\n---\n\n"
      "# Heading\n\nNo requirements here.\n"
    )
    result = migrate_spec("X", text)
    assert not result.changed


# ---------------------------------------------------------------------------
# Dry-run (VA-140-001)
# ---------------------------------------------------------------------------


class TestDryRun:
  def test_dry_run_produces_valid_block(self, tmp_path: Path):
    """VA-140-001: dry-run produces valid proposed block."""
    spec_file = tmp_path / "PROD-099.md"
    spec_file.write_text(_SAMPLE_SPEC, encoding="utf-8")

    result = apply_migration(
      spec_file, "PROD-099", dry_run=True,
    )
    assert result.changed
    assert result.requirements_count == 3
    assert "supekku:spec.requirements@v1" in result.text

    original = spec_file.read_text(encoding="utf-8")
    assert original == _SAMPLE_SPEC, (
      "dry-run must not modify file"
    )


# ---------------------------------------------------------------------------
# Post-write validation (VA-140-002)
# ---------------------------------------------------------------------------


class TestPostWriteValidation:
  def test_valid_write_succeeds(self, tmp_path: Path):
    spec_file = tmp_path / "PROD-099.md"
    spec_file.write_text(_SAMPLE_SPEC, encoding="utf-8")

    result = apply_migration(spec_file, "PROD-099")
    assert result.changed

    written = spec_file.read_text(encoding="utf-8")
    assert "supekku:spec.requirements@v1" in written

  def test_catches_missing_block(self):
    """VA-140-002: catches malformed output."""
    errors = _validate_written_block(
      "no block here", "PROD-099",
    )
    assert any(
      "no spec.requirements block" in e for e in errors
    )

  def test_catches_spec_mismatch(self):
    text = (
      "```yaml supekku:spec.requirements@v1\n"
      "schema: supekku.spec.requirements\n"
      "version: 1\n"
      "spec: PROD-WRONG\n"
      "requirements: []\n"
      "```\n"
    )
    errors = _validate_written_block(text, "PROD-099")
    assert any("spec field mismatch" in e for e in errors)


# ---------------------------------------------------------------------------
# Atomicity (VA-140-003)
# ---------------------------------------------------------------------------


class TestAtomicity:
  def test_refuses_when_block_exists(self, tmp_path: Path):
    """VA-140-003: block-present guard prevents double migration."""
    spec_file = tmp_path / "PROD-099.md"
    spec_file.write_text(
      _SAMPLE_SPEC_WITH_BLOCK, encoding="utf-8",
    )

    result = apply_migration(spec_file, "PROD-099")
    assert not result.changed

    content = spec_file.read_text(encoding="utf-8")
    assert content == _SAMPLE_SPEC_WITH_BLOCK

  def test_reverts_on_validation_failure(
    self, tmp_path: Path, monkeypatch,
  ):
    """VA-140-002/003: reverts on post-write validation failure."""
    spec_file = tmp_path / "PROD-099.md"
    spec_file.write_text(_SAMPLE_SPEC, encoding="utf-8")

    from spec_driver.migrations.spec_requirements import (  # noqa: PLC0415
      migration,
    )

    def failing_validate(text, spec_id):  # noqa: ARG001
      return ["forced validation failure"]

    monkeypatch.setattr(
      migration, "_validate_written_block", failing_validate,
    )

    with pytest.raises(
      ValueError, match="post-write validation failed",
    ):
      apply_migration(spec_file, "PROD-099")

    content = spec_file.read_text(encoding="utf-8")
    assert content == _SAMPLE_SPEC, (
      "must revert to original on validation failure"
    )


# ---------------------------------------------------------------------------
# Drift ledger (VA-140-005)
# ---------------------------------------------------------------------------


class TestDriftLedger:
  def test_writes_drift_entries(self, tmp_path: Path):
    """VA-140-005: drift entries persist as DL-* ledger files."""
    drift_dir = tmp_path / "drift"
    entries = [
      DriftEntry(
        "PROD-099", DRIFT_DESCRIPTION_PLACEHOLDER,
        "FR-001: empty desc",
      ),
      DriftEntry(
        "PROD-099", DRIFT_ACCEPTANCE_PLACEHOLDER,
        "FR-001: empty ac",
      ),
    ]
    path = write_drift_ledger(drift_dir, "PROD-099", entries)
    assert path is not None
    assert path.exists()
    assert path.name.startswith("DL-")

    content = path.read_text(encoding="utf-8")
    assert "kind: drift_ledger" in content
    assert "delta_ref: DE-140" in content
    assert DRIFT_DESCRIPTION_PLACEHOLDER in content
    assert DRIFT_ACCEPTANCE_PLACEHOLDER in content

  def test_no_entries_returns_none(self, tmp_path: Path):
    drift_dir = tmp_path / "drift"
    result = write_drift_ledger(drift_dir, "PROD-099", [])
    assert result is None

  def test_sequential_ids(self, tmp_path: Path):
    drift_dir = tmp_path / "drift"
    drift_dir.mkdir()
    (drift_dir / "DL-048-existing.md").write_text(
      "", encoding="utf-8",
    )

    entries = [DriftEntry("PROD-099", "test", "detail")]
    path = write_drift_ledger(drift_dir, "PROD-099", entries)
    assert path is not None
    assert "DL-049" in path.name


class TestDetectDrift:
  def test_detects_placeholder_drift(self):
    body = "- **FR-001**: Title\n"
    parsed = [
      ParsedRequirement(
        id="FR-001", title="Title", kind="functional",
      ),
    ]
    drift = _detect_drift("PROD-099", body, parsed)
    desc = [
      d for d in drift
      if d.kind == DRIFT_DESCRIPTION_PLACEHOLDER
    ]
    acc = [
      d for d in drift
      if d.kind == DRIFT_ACCEPTANCE_PLACEHOLDER
    ]
    assert len(desc) == 1
    assert len(acc) == 1

  def test_detects_unparseable_lines(self):
    body = "- **FR-001**: Title\n- FR-002 malformed line\n"
    parsed = [
      ParsedRequirement(
        id="FR-001", title="Title", kind="functional",
      ),
    ]
    drift = _detect_drift("PROD-099", body, parsed)
    unparseable = [
      d for d in drift
      if d.kind == DRIFT_REQUIREMENT_UNPARSEABLE
    ]
    assert len(unparseable) == 1

