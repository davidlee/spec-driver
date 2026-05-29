"""Tests for v0_10_0_004_audit_findings migration step.

Covers VT-141-MIGRATE-001 through -005.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from .migration import (
  _MARKER,
  DRIFT_INVALID_OUTCOME,
  AuditFindingsStep,
  _transform,
)


def _write_audit(tmp_path: Path, name: str, contents: str) -> Path:
  path = tmp_path / name
  path.write_text(contents, encoding="utf-8")
  return path


def _parse_fm(text: str) -> dict:
  lines = text.split("\n")
  assert lines[0] == "---"
  end = lines.index("---", 1)
  return yaml.safe_load("\n".join(lines[1:end]))


def _drift_kinds(drift: list) -> set[str]:
  return {e.kind for e in drift}


SAMPLE_AUDIT = """\
---
id: AUD-012
slug: sample
name: AUD-012
created: "2024-06-01"
updated: "2024-06-01"
status: completed
kind: audit
mode: conformance
delta_ref: DE-097
findings:
  - id: F-001
    description: Graph builder works
    outcome: aligned
    disposition:
      status: reconciled
      kind: aligned
  - id: F-002
    description: Missing coverage
    outcome: drift
    disposition:
      status: accepted
      kind: tolerated_drift
---

# AUD-012

## Observations

Some observations.
"""


# ---------------------------------------------------------------------------
# Module export
# ---------------------------------------------------------------------------


def test_module_exports_step_instance() -> None:
  from spec_driver.migrations.v0_10_0_004_audit_findings import step  # noqa: PLC0415
  assert isinstance(step, AuditFindingsStep)
  assert step.applies_to_kind == "audit"


# ---------------------------------------------------------------------------
# VT-141-MIGRATE-001: Migration produces valid block
# ---------------------------------------------------------------------------


class TestProducesValidBlock:
  """VT-141-MIGRATE-001"""

  def test_block_emitted(self) -> None:
    result = _transform(SAMPLE_AUDIT)
    assert result.changed
    assert _MARKER in result.text
    assert "findings:" in result.text

  def test_fm_findings_removed(self) -> None:
    result = _transform(SAMPLE_AUDIT)
    fm = _parse_fm(result.text)
    assert "findings" not in fm

  def test_block_parseable(self) -> None:
    result = _transform(SAMPLE_AUDIT)
    # Extract block content
    import re  # noqa: PLC0415
    pattern = re.compile(
      r"```(?:yaml|yml)\s+" + re.escape(_MARKER) + r"\n(.*?)```",
      re.DOTALL,
    )
    match = pattern.search(result.text)
    assert match is not None
    data = yaml.safe_load(match.group(1))
    assert data["audit"] == "AUD-012"
    assert len(data["findings"]) == 2
    assert data["findings"][0]["id"] == "F-001"
    assert data["findings"][1]["outcome"] == "drift"


# ---------------------------------------------------------------------------
# VT-141-MIGRATE-002: Drift entry for invalid outcome
# ---------------------------------------------------------------------------


class TestDriftForInvalidOutcome:
  """VT-141-MIGRATE-002"""

  def test_invalid_outcome_produces_drift(self) -> None:
    audit = SAMPLE_AUDIT.replace("outcome: aligned", "outcome: pass")
    result = _transform(audit)
    assert result.changed
    assert DRIFT_INVALID_OUTCOME in _drift_kinds(result.drift)

  def test_valid_outcomes_no_drift(self) -> None:
    result = _transform(SAMPLE_AUDIT)
    assert DRIFT_INVALID_OUTCOME not in _drift_kinds(result.drift)


# ---------------------------------------------------------------------------
# VT-141-MIGRATE-003: Universal FM key cuts
# ---------------------------------------------------------------------------


class TestFmKeyCuts:
  """VT-141-MIGRATE-003"""

  def test_findings_cut_from_fm(self) -> None:
    result = _transform(SAMPLE_AUDIT)
    fm = _parse_fm(result.text)
    assert "findings" not in fm

  def test_other_keys_preserved(self) -> None:
    result = _transform(SAMPLE_AUDIT)
    fm = _parse_fm(result.text)
    assert fm["id"] == "AUD-012"
    assert fm["mode"] == "conformance"
    assert fm["delta_ref"] == "DE-097"
    assert fm["status"] == "completed"


# ---------------------------------------------------------------------------
# VT-141-MIGRATE-004: Idempotence
# ---------------------------------------------------------------------------


class TestIdempotence:
  """VT-141-MIGRATE-004"""

  def test_second_transform_is_noop(self) -> None:
    first = _transform(SAMPLE_AUDIT)
    assert first.changed
    second = _transform(first.text)
    assert not second.changed
    assert second.text == first.text


# ---------------------------------------------------------------------------
# VT-141-MIGRATE-005: FM+block coexistence
# ---------------------------------------------------------------------------


class TestFmBlockCoexistence:
  """VT-141-MIGRATE-005"""

  def test_block_preserved_fm_cut(self) -> None:
    """When both FM findings and block exist, block preserved, FM cut."""
    audit_with_block = SAMPLE_AUDIT.rstrip() + f"""

```yaml {_MARKER}
schema: supekku.audit.findings
version: 1
audit: AUD-012
findings:
  - id: F-001
    description: From block
    outcome: aligned
```
"""
    result = _transform(audit_with_block)
    assert result.changed
    fm = _parse_fm(result.text)
    assert "findings" not in fm
    # Block preserved (not duplicated)
    assert result.text.count(_MARKER) == 1


# ---------------------------------------------------------------------------
# Step apply/preview
# ---------------------------------------------------------------------------


class TestStepApplyPreview:
  """Step interface tests."""

  def test_apply_writes(self, tmp_path: Path) -> None:
    path = _write_audit(tmp_path, "AUD-012.md", SAMPLE_AUDIT)
    step = AuditFindingsStep()
    result = step.apply(path)
    assert result.touched == [path]
    text = path.read_text(encoding="utf-8")
    assert _MARKER in text
    fm = _parse_fm(text)
    assert "findings" not in fm

  def test_preview_no_write(self, tmp_path: Path) -> None:
    path = _write_audit(tmp_path, "AUD-012.md", SAMPLE_AUDIT)
    step = AuditFindingsStep()
    preview = step.preview(path)
    assert preview.touched == [path]
    # File unchanged
    assert path.read_text(encoding="utf-8") == SAMPLE_AUDIT

  def test_apply_idempotent(self, tmp_path: Path) -> None:
    path = _write_audit(tmp_path, "AUD-012.md", SAMPLE_AUDIT)
    step = AuditFindingsStep()
    step.apply(path)
    text_after_first = path.read_text(encoding="utf-8")
    result = step.apply(path)
    assert result.skipped == [path]
    assert path.read_text(encoding="utf-8") == text_after_first

  def test_applies_to_no_findings(self, tmp_path: Path) -> None:
    no_findings = """\
---
id: AUD-099
status: completed
kind: audit
---

# No findings
"""
    path = _write_audit(tmp_path, "AUD-099.md", no_findings)
    step = AuditFindingsStep()
    assert not step.applies_to(path)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
  """Edge case coverage."""

  def test_no_frontmatter(self) -> None:
    result = _transform("# Just a heading\n\nSome text.\n")
    assert not result.changed

  def test_empty_findings_list(self) -> None:
    audit = SAMPLE_AUDIT.replace(
      "findings:\n  - id: F-001\n    description: Graph builder works\n"
      "    outcome: aligned\n    disposition:\n      status: reconciled\n"
      "      kind: aligned\n  - id: F-002\n    description: Missing coverage\n"
      "    outcome: drift\n    disposition:\n      status: accepted\n"
      "      kind: tolerated_drift",
      "findings: []",
    )
    result = _transform(audit)
    assert result.changed
    assert "findings: []" in result.text
    fm = _parse_fm(result.text)
    assert "findings" not in fm
