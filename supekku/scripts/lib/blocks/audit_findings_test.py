"""Tests for audit findings block extraction, rendering, and dual-path loader.

Covers VT-141-BLOCK-001 through -004, VT-141-TRANSITION-001, -002.
"""

from __future__ import annotations

import pytest

from supekku.scripts.lib.blocks.schema_registry import (
  get_block_schema,
  list_block_types,
)

from .audit_findings import (
  AUDIT_FINDINGS_MARKER,
  AuditFindingsBlock,
  extract_audit_findings,
  load_audit_findings,
  render_audit_findings_block,
  validate_audit_field,
)

SAMPLE_FINDINGS = [
  {
    "id": "F-001",
    "description": "Delta frontmatter uses deprecated key",
    "outcome": "drift",
    "linked_issue": "ISSUE-055",
    "linked_delta": "",
    "disposition": {
      "status": "reconciled",
      "kind": "spec_patch",
      "refs": [{"kind": "revision", "ref": "RE-042"}],
      "rationale": "Resolved via RE-042",
    },
  },
  {
    "id": "F-002",
    "description": "Missing coverage for NF-001",
    "outcome": "risk",
    "disposition": {
      "status": "accepted",
      "kind": "tolerated_drift",
      "rationale": "Low severity, deferred",
      "closure_override": {"effect": "warn", "rationale": "Non-blocking"},
    },
  },
]


def _wrap_block(inner: str) -> str:
  return f"# Test\n\n```yaml {AUDIT_FINDINGS_MARKER}\n{inner}```\n\n## More\n"


SAMPLE_VALID_YAML = """\
schema: supekku.audit.findings
version: 1
audit: AUD-027
findings:
  - id: F-001
    description: "Delta frontmatter uses deprecated key"
    outcome: drift
    linked_issue: ISSUE-055
    disposition:
      status: reconciled
      kind: spec_patch
      refs:
        - kind: revision
          ref: RE-042
      rationale: "Resolved via RE-042"
  - id: F-002
    description: "Missing coverage for NF-001"
    outcome: risk
"""


# ---------------------------------------------------------------------------
# VT-141-BLOCK-001: Render → extract round-trip preserves all fields
# ---------------------------------------------------------------------------


class TestRoundTrip:
  """VT-141-BLOCK-001"""

  def test_render_then_extract(self) -> None:
    rendered = render_audit_findings_block("AUD-027", SAMPLE_FINDINGS)
    block = extract_audit_findings(rendered)
    assert block is not None
    assert isinstance(block, AuditFindingsBlock)
    assert block.data["audit"] == "AUD-027"
    findings = block.data["findings"]
    assert len(findings) == 2

    f1 = findings[0]
    assert f1["id"] == "F-001"
    assert f1["outcome"] == "drift"
    assert f1["linked_issue"] == "ISSUE-055"
    assert f1["disposition"]["status"] == "reconciled"
    assert f1["disposition"]["kind"] == "spec_patch"
    assert f1["disposition"]["refs"] == [{"kind": "revision", "ref": "RE-042"}]

    f2 = findings[1]
    assert f2["id"] == "F-002"
    assert f2["outcome"] == "risk"
    assert f2["disposition"]["closure_override"]["effect"] == "warn"

  def test_schema_and_version_preserved(self) -> None:
    rendered = render_audit_findings_block("AUD-001", SAMPLE_FINDINGS)
    block = extract_audit_findings(rendered)
    assert block is not None
    assert block.data["schema"] == "supekku.audit.findings"
    assert block.data["version"] == 1


# ---------------------------------------------------------------------------
# VT-141-BLOCK-002: Empty findings block
# ---------------------------------------------------------------------------


class TestEmptyFindings:
  """VT-141-BLOCK-002"""

  def test_empty_findings_renders_and_extracts(self) -> None:
    rendered = render_audit_findings_block("AUD-010", [])
    assert "findings: []" in rendered
    block = extract_audit_findings(rendered)
    assert block is not None
    assert block.data["findings"] == []

  def test_empty_findings_round_trip(self) -> None:
    rendered = render_audit_findings_block("AUD-010", [])
    block = extract_audit_findings(rendered)
    assert block is not None
    assert block.data["audit"] == "AUD-010"


# ---------------------------------------------------------------------------
# VT-141-BLOCK-003: Duplicate/malformed block errors
# ---------------------------------------------------------------------------


class TestBlockErrors:
  """VT-141-BLOCK-003"""

  def test_duplicate_blocks_raises(self) -> None:
    block1 = _wrap_block(SAMPLE_VALID_YAML)
    block2 = _wrap_block(SAMPLE_VALID_YAML)
    content = block1 + "\n" + block2
    with pytest.raises(ValueError, match="multiple audit.findings blocks"):
      extract_audit_findings(content)

  def test_malformed_yaml_raises(self) -> None:
    bad = f"```yaml {AUDIT_FINDINGS_MARKER}\ninvalid: yaml: :\n```"
    with pytest.raises(ValueError, match="invalid audit findings YAML"):
      extract_audit_findings(bad)

  def test_non_mapping_raises(self) -> None:
    bad = f"```yaml {AUDIT_FINDINGS_MARKER}\n- list\n- items\n```"
    with pytest.raises(ValueError, match="must parse to mapping"):
      extract_audit_findings(bad)

  def test_no_block_returns_none(self) -> None:
    assert extract_audit_findings("# No blocks here\n") is None


# ---------------------------------------------------------------------------
# VT-141-BLOCK-004: Block audit field mismatch
# ---------------------------------------------------------------------------


class TestAuditFieldMismatch:
  """VT-141-BLOCK-004"""

  def test_matching_audit_field_passes(self) -> None:
    block = AuditFindingsBlock(raw_yaml="", data={"audit": "AUD-027", "findings": []})
    validate_audit_field(block, "AUD-027")

  def test_mismatched_audit_field_raises(self) -> None:
    block = AuditFindingsBlock(raw_yaml="", data={"audit": "AUD-027", "findings": []})
    with pytest.raises(ValueError, match="does not match"):
      validate_audit_field(block, "AUD-099")

  def test_missing_audit_field_raises(self) -> None:
    block = AuditFindingsBlock(raw_yaml="", data={"findings": []})
    with pytest.raises(ValueError, match="does not match"):
      validate_audit_field(block, "AUD-001")


# ---------------------------------------------------------------------------
# VT-141-TRANSITION-001: Block-first when both exist
# ---------------------------------------------------------------------------


class TestDualPathBlockFirst:
  """VT-141-TRANSITION-001"""

  def test_block_wins_over_fm(self) -> None:
    block_body = render_audit_findings_block("AUD-001", [
      {"id": "F-001", "description": "From block", "outcome": "aligned"},
    ])
    fm = {"findings": [{"id": "F-099", "description": "From FM", "outcome": "risk"}]}
    result = load_audit_findings(block_body, fm=fm)
    assert len(result) == 1
    assert result[0]["id"] == "F-001"
    assert result[0]["description"] == "From block"


# ---------------------------------------------------------------------------
# VT-141-TRANSITION-002: FM fallback when no block
# ---------------------------------------------------------------------------


class TestDualPathFmFallback:
  """VT-141-TRANSITION-002"""

  def test_fm_fallback_when_no_block(self) -> None:
    body = "# No block here\n\nJust prose.\n"
    fm = {"findings": [{"id": "F-001", "description": "From FM", "outcome": "drift"}]}
    result = load_audit_findings(body, fm=fm)
    assert len(result) == 1
    assert result[0]["id"] == "F-001"

  def test_no_block_no_fm_returns_empty(self) -> None:
    result = load_audit_findings("# Nothing\n")
    assert result == []

  def test_fm_without_findings_returns_empty(self) -> None:
    result = load_audit_findings("# Nothing\n", fm={"status": "completed"})
    assert result == []


# ---------------------------------------------------------------------------
# Schema registry
# ---------------------------------------------------------------------------


class TestSchemaRegistry:
  """Block is registered in schema registry."""

  def test_registered(self) -> None:
    schema = get_block_schema("audit.findings")
    assert schema is not None
    assert schema.marker == AUDIT_FINDINGS_MARKER
    assert schema.version == 1
    assert schema.renderer is render_audit_findings_block

  def test_appears_in_list(self) -> None:
    assert "audit.findings" in list_block_types()


# ---------------------------------------------------------------------------
# Renderer edge cases
# ---------------------------------------------------------------------------


class TestRendererEdgeCases:
  """Renderer handles special characters and optional fields."""

  def test_description_with_colons(self) -> None:
    findings = [
      {
        "id": "F-001",
        "description": "Key: value pair in description",
        "outcome": "aligned",
      },
    ]
    rendered = render_audit_findings_block("AUD-001", findings)
    block = extract_audit_findings(rendered)
    assert block is not None
    assert "value pair" in block.data["findings"][0]["description"]

  def test_finding_without_optional_fields(self) -> None:
    findings = [
      {"id": "F-001", "description": "Minimal finding", "outcome": "aligned"},
    ]
    rendered = render_audit_findings_block("AUD-001", findings)
    block = extract_audit_findings(rendered)
    assert block is not None
    f = block.data["findings"][0]
    assert f["id"] == "F-001"
    assert "linked_issue" not in f
    assert "disposition" not in f

  def test_disposition_with_drift_refs(self) -> None:
    findings = [
      {
        "id": "F-001",
        "description": "With drift refs",
        "outcome": "drift",
        "disposition": {
          "status": "reconciled",
          "kind": "follow_up_delta",
          "drift_refs": [{"kind": "drift", "ref": "DL-001"}],
        },
      },
    ]
    rendered = render_audit_findings_block("AUD-001", findings)
    block = extract_audit_findings(rendered)
    assert block is not None
    disp = block.data["findings"][0]["disposition"]
    assert disp["drift_refs"] == [{"kind": "drift", "ref": "DL-001"}]
