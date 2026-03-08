"""Tests for audit completeness checking (VT-079-002, VT-079-003, VT-079-004)."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from supekku.scripts.lib.changes.audit_check import (
  EFFECT_BLOCK,
  EFFECT_NONE,
  EFFECT_WARN,
  GATE_EXEMPT,
  GATE_NON_GATING,
  GATE_REQUIRED,
  AuditCheckResult,
  GatingFinding,
  check_audit_completeness,
  collect_gating_findings,
  derive_closure_effect,
  format_audit_error,
  resolve_audit_gate,
)

# -- VT-079-003: audit_gate resolution tests --


class ResolveAuditGateTest(unittest.TestCase):
  """Test resolve_audit_gate (DEC-079-003)."""

  def test_auto_with_requirements_resolves_to_required(self):
    result = resolve_audit_gate("auto", ["PROD-008.FR-001"])
    self.assertEqual(result, GATE_REQUIRED)

  def test_auto_with_empty_requirements_resolves_to_non_gating(self):
    result = resolve_audit_gate("auto", [])
    self.assertEqual(result, GATE_NON_GATING)

  def test_auto_with_multiple_requirements(self):
    result = resolve_audit_gate("auto", ["PROD-008.FR-001", "SPEC-116.FR-002"])
    self.assertEqual(result, GATE_REQUIRED)

  def test_none_defaults_to_auto_non_gating(self):
    result = resolve_audit_gate(None, [])
    self.assertEqual(result, GATE_NON_GATING)

  def test_none_defaults_to_auto_required(self):
    result = resolve_audit_gate(None, ["PROD-008.FR-001"])
    self.assertEqual(result, GATE_REQUIRED)

  def test_required_passes_through(self):
    result = resolve_audit_gate("required", [])
    self.assertEqual(result, GATE_REQUIRED)

  def test_required_ignores_requirements(self):
    result = resolve_audit_gate("required", ["PROD-008.FR-001"])
    self.assertEqual(result, GATE_REQUIRED)

  def test_exempt_passes_through(self):
    result = resolve_audit_gate("exempt", [])
    self.assertEqual(result, GATE_EXEMPT)

  def test_exempt_ignores_requirements(self):
    result = resolve_audit_gate("exempt", ["PROD-008.FR-001"])
    self.assertEqual(result, GATE_EXEMPT)


# -- VT-079-002: closure-effect derivation tests --


class DeriveClosureEffectConformanceTest(unittest.TestCase):
  """Test derive_closure_effect for conformance mode (DEC-079-005, -006)."""

  MODE = "conformance"

  def test_no_disposition_blocks(self):
    """Finding with no disposition at all → block."""
    result = derive_closure_effect(self.MODE, "drift", None, None)
    self.assertEqual(result, EFFECT_BLOCK)

  def test_pending_blocks(self):
    result = derive_closure_effect(self.MODE, "drift", "pending", "spec_patch")
    self.assertEqual(result, EFFECT_BLOCK)

  def test_reconciled_is_none(self):
    result = derive_closure_effect(self.MODE, "drift", "reconciled", "spec_patch")
    self.assertEqual(result, EFFECT_NONE)

  def test_reconciled_aligned_is_none(self):
    result = derive_closure_effect(self.MODE, "aligned", "reconciled", "aligned")
    self.assertEqual(result, EFFECT_NONE)

  def test_tolerated_drift_accepted_blocks(self):
    """DEC-079-006: conformance + tolerated_drift defaults to block."""
    result = derive_closure_effect(self.MODE, "drift", "accepted", "tolerated_drift")
    self.assertEqual(result, EFFECT_BLOCK)

  def test_follow_up_delta_accepted_with_ref_warns(self):
    refs = [{"kind": "delta", "ref": "DE-100"}]
    result = derive_closure_effect(
      self.MODE,
      "drift",
      "accepted",
      "follow_up_delta",
      refs=refs,
    )
    self.assertEqual(result, EFFECT_WARN)

  def test_follow_up_delta_accepted_without_ref_blocks(self):
    result = derive_closure_effect(
      self.MODE,
      "drift",
      "accepted",
      "follow_up_delta",
      refs=[],
    )
    self.assertEqual(result, EFFECT_BLOCK)

  def test_follow_up_backlog_accepted_with_ref_warns(self):
    refs = [{"kind": "issue", "ref": "ISSUE-042"}]
    result = derive_closure_effect(
      self.MODE,
      "drift",
      "accepted",
      "follow_up_backlog",
      refs=refs,
    )
    self.assertEqual(result, EFFECT_WARN)

  def test_follow_up_backlog_accepted_without_ref_blocks(self):
    result = derive_closure_effect(
      self.MODE,
      "drift",
      "accepted",
      "follow_up_backlog",
    )
    self.assertEqual(result, EFFECT_BLOCK)

  def test_follow_up_delta_with_empty_ref_blocks(self):
    """Ref with empty kind/ref is not a valid owned ref."""
    refs = [{"kind": "", "ref": ""}]
    result = derive_closure_effect(
      self.MODE,
      "drift",
      "accepted",
      "follow_up_delta",
      refs=refs,
    )
    self.assertEqual(result, EFFECT_BLOCK)


class DeriveClosureEffectDiscoveryTest(unittest.TestCase):
  """Test derive_closure_effect for discovery mode."""

  MODE = "discovery"

  def test_no_disposition_warns(self):
    result = derive_closure_effect(self.MODE, "drift", None, None)
    self.assertEqual(result, EFFECT_WARN)

  def test_pending_warns(self):
    result = derive_closure_effect(self.MODE, "drift", "pending", "spec_patch")
    self.assertEqual(result, EFFECT_WARN)

  def test_reconciled_is_none(self):
    result = derive_closure_effect(self.MODE, "drift", "reconciled", "spec_patch")
    self.assertEqual(result, EFFECT_NONE)

  def test_accepted_is_none(self):
    result = derive_closure_effect(self.MODE, "drift", "accepted", "follow_up_delta")
    self.assertEqual(result, EFFECT_NONE)

  def test_tolerated_drift_accepted_is_none(self):
    """Discovery + tolerated_drift does NOT block (unlike conformance)."""
    result = derive_closure_effect(self.MODE, "drift", "accepted", "tolerated_drift")
    self.assertEqual(result, EFFECT_NONE)


class ClosureOverrideTest(unittest.TestCase):
  """Test closure_override relaxation."""

  def test_override_relaxes_block_to_warn(self):
    result = derive_closure_effect(
      "conformance",
      "drift",
      "pending",
      "spec_patch",
      closure_override_effect="warn",
    )
    self.assertEqual(result, EFFECT_WARN)

  def test_override_relaxes_block_to_none(self):
    result = derive_closure_effect(
      "conformance",
      "drift",
      "pending",
      "spec_patch",
      closure_override_effect="none",
    )
    self.assertEqual(result, EFFECT_NONE)

  def test_override_cannot_escalate_none_to_block(self):
    """Override can only relax, never escalate."""
    result = derive_closure_effect(
      "conformance",
      "aligned",
      "reconciled",
      "aligned",
      closure_override_effect="block",
    )
    self.assertEqual(result, EFFECT_NONE)

  def test_override_cannot_escalate_warn_to_block(self):
    refs = [{"kind": "delta", "ref": "DE-100"}]
    result = derive_closure_effect(
      "conformance",
      "drift",
      "accepted",
      "follow_up_delta",
      closure_override_effect="block",
      refs=refs,
    )
    self.assertEqual(result, EFFECT_WARN)

  def test_override_relaxes_tolerated_drift_block_to_warn(self):
    """DEC-079-006 default block can be relaxed with closure_override."""
    result = derive_closure_effect(
      "conformance",
      "drift",
      "accepted",
      "tolerated_drift",
      closure_override_effect="warn",
    )
    self.assertEqual(result, EFFECT_WARN)


# -- VT-079-004: integration tests --


def _make_mock_audit(
  audit_id: str,
  status: str = "completed",
  path: Path | None = None,
) -> MagicMock:
  """Create a mock ChangeArtifact for an audit."""
  mock = MagicMock()
  mock.id = audit_id
  mock.status = status
  mock.path = path or Path(f"/fake/{audit_id}.md")
  return mock


def _make_mock_delta(
  delta_id: str,
  status: str = "in-progress",
  requirements: list[str] | None = None,
  path: Path | None = None,
) -> MagicMock:
  """Create a mock ChangeArtifact for a delta."""
  mock = MagicMock()
  mock.id = delta_id
  mock.status = status
  mock.applies_to = {"requirements": requirements or []}
  mock.path = path or Path(f"/fake/{delta_id}.md")
  return mock


class CollectGatingFindingsTest(unittest.TestCase):
  """Test collect_gating_findings (DEC-079-008)."""

  def _make_workspace(self, audits):
    """Create mock workspace with audit registry."""
    ws = MagicMock()
    registry = MagicMock()
    registry.collect.return_value = {a.id: a for a in audits}
    ws.audit_registry = registry
    return ws

  @patch("supekku.scripts.lib.changes.audit_check._load_audit_frontmatter")
  def test_no_audits_returns_empty(self, _mock_load):
    ws = self._make_workspace([])
    findings, count, collisions = collect_gating_findings("DE-079", ws)
    self.assertEqual(findings, [])
    self.assertEqual(count, 0)
    self.assertEqual(collisions, [])

  @patch("supekku.scripts.lib.changes.audit_check._load_audit_frontmatter")
  def test_matching_audit_collects_findings(self, mock_load):
    audit = _make_mock_audit("AUD-010")
    fm = {
      "delta_ref": "DE-079",
      "mode": "conformance",
      "findings": [
        {
          "id": "FIND-001",
          "description": "Drift found",
          "outcome": "drift",
          "disposition": {
            "status": "reconciled",
            "kind": "spec_patch",
            "refs": [{"kind": "spec", "ref": "SPEC-116"}],
          },
        },
      ],
    }
    mock_load.return_value = fm
    ws = self._make_workspace([audit])

    findings, count, collisions = collect_gating_findings("DE-079", ws)
    self.assertEqual(count, 1)
    self.assertEqual(len(findings), 1)
    self.assertEqual(findings[0].finding_id, "FIND-001")
    self.assertEqual(findings[0].closure_effect, EFFECT_NONE)
    self.assertEqual(collisions, [])

  @patch("supekku.scripts.lib.changes.audit_check._load_audit_frontmatter")
  def test_non_matching_delta_ref_excluded(self, mock_load):
    audit = _make_mock_audit("AUD-010")
    mock_load.return_value = {
      "delta_ref": "DE-999",
      "mode": "conformance",
      "findings": [{"id": "FIND-001", "description": "x", "outcome": "drift"}],
    }
    ws = self._make_workspace([audit])

    findings, count, _ = collect_gating_findings("DE-079", ws)
    self.assertEqual(count, 0)
    self.assertEqual(findings, [])

  @patch("supekku.scripts.lib.changes.audit_check._load_audit_frontmatter")
  def test_discovery_mode_excluded(self, mock_load):
    audit = _make_mock_audit("AUD-010")
    mock_load.return_value = {
      "delta_ref": "DE-079",
      "mode": "discovery",
      "findings": [{"id": "FIND-001", "description": "x", "outcome": "drift"}],
    }
    ws = self._make_workspace([audit])

    _findings, count, _ = collect_gating_findings("DE-079", ws)
    self.assertEqual(count, 0)

  @patch("supekku.scripts.lib.changes.audit_check._load_audit_frontmatter")
  def test_non_completed_audit_excluded(self, mock_load):
    audit = _make_mock_audit("AUD-010", status="draft")
    mock_load.return_value = {
      "delta_ref": "DE-079",
      "mode": "conformance",
      "findings": [{"id": "FIND-001", "description": "x", "outcome": "drift"}],
    }
    ws = self._make_workspace([audit])

    _findings, count, _ = collect_gating_findings("DE-079", ws)
    self.assertEqual(count, 0)

  @patch("supekku.scripts.lib.changes.audit_check._load_audit_frontmatter")
  def test_multi_audit_union(self, mock_load):
    """DEC-079-008: multiple audits contribute findings by union."""
    aud1 = _make_mock_audit("AUD-010", path=Path("/fake/AUD-010.md"))
    aud2 = _make_mock_audit("AUD-011", path=Path("/fake/AUD-011.md"))

    def side_effect(path):
      if "AUD-010" in str(path):
        return {
          "delta_ref": "DE-079",
          "mode": "conformance",
          "findings": [
            {
              "id": "FIND-001",
              "description": "a",
              "outcome": "aligned",
              "disposition": {"status": "reconciled", "kind": "aligned"},
            },
          ],
        }
      return {
        "delta_ref": "DE-079",
        "mode": "conformance",
        "findings": [
          {
            "id": "FIND-002",
            "description": "b",
            "outcome": "drift",
            "disposition": {"status": "reconciled", "kind": "spec_patch"},
          },
        ],
      }

    mock_load.side_effect = side_effect
    ws = self._make_workspace([aud1, aud2])

    all_findings, count, collisions = collect_gating_findings("DE-079", ws)
    self.assertEqual(count, 2)
    self.assertEqual(len(all_findings), 2)
    ids = {f.finding_id for f in all_findings}
    self.assertEqual(ids, {"FIND-001", "FIND-002"})
    self.assertEqual(collisions, [])

  @patch("supekku.scripts.lib.changes.audit_check._load_audit_frontmatter")
  def test_finding_id_collision_detected(self, mock_load):
    """DEC-079-008: colliding finding IDs produce warning."""
    aud1 = _make_mock_audit("AUD-010", path=Path("/fake/AUD-010.md"))
    aud2 = _make_mock_audit("AUD-011", path=Path("/fake/AUD-011.md"))

    def side_effect(_path):
      return {
        "delta_ref": "DE-079",
        "mode": "conformance",
        "findings": [
          {
            "id": "FIND-001",
            "description": "same id",
            "outcome": "aligned",
            "disposition": {"status": "reconciled", "kind": "aligned"},
          },
        ],
      }

    mock_load.side_effect = side_effect
    ws = self._make_workspace([aud1, aud2])

    _all_findings, count, collisions = collect_gating_findings("DE-079", ws)
    self.assertEqual(count, 2)
    self.assertEqual(len(collisions), 1)
    self.assertIn("FIND-001", collisions[0])


class CheckAuditCompletenessTest(unittest.TestCase):
  """Test check_audit_completeness end-to-end (VT-079-004)."""

  @patch("supekku.scripts.lib.changes.audit_check.collect_gating_findings")
  @patch("supekku.scripts.lib.changes.audit_check._load_audit_frontmatter")
  def test_non_gating_delta_passes(self, mock_load_fm, _mock_collect):
    """Delta with no requirements and auto gate → non-gating → passes."""
    delta = _make_mock_delta("DE-090", requirements=[])
    mock_load_fm.return_value = {}

    ws = MagicMock()
    ws.delta_registry.collect.return_value = {"DE-090": delta}

    result = check_audit_completeness("DE-090", ws)
    self.assertTrue(result.is_complete)
    self.assertEqual(result.gate_resolution, GATE_NON_GATING)
    _mock_collect.assert_not_called()

  @patch("supekku.scripts.lib.changes.audit_check.collect_gating_findings")
  @patch("supekku.scripts.lib.changes.audit_check._load_audit_frontmatter")
  def test_exempt_delta_passes(self, mock_load_fm, _mock_collect):
    delta = _make_mock_delta("DE-090", requirements=["PROD-008.FR-001"])
    mock_load_fm.return_value = {"audit_gate": "exempt"}

    ws = MagicMock()
    ws.delta_registry.collect.return_value = {"DE-090": delta}

    result = check_audit_completeness("DE-090", ws)
    self.assertTrue(result.is_complete)
    self.assertEqual(result.gate_resolution, GATE_EXEMPT)

  @patch("supekku.scripts.lib.changes.audit_check.collect_gating_findings")
  @patch("supekku.scripts.lib.changes.audit_check._load_audit_frontmatter")
  def test_required_with_no_audit_fails(self, mock_load_fm, mock_collect):
    delta = _make_mock_delta("DE-090", requirements=["PROD-008.FR-001"])
    mock_load_fm.return_value = {}
    mock_collect.return_value = ([], 0, [])

    ws = MagicMock()
    ws.delta_registry.collect.return_value = {"DE-090": delta}

    result = check_audit_completeness("DE-090", ws)
    self.assertFalse(result.is_complete)
    self.assertEqual(result.gate_resolution, GATE_REQUIRED)
    self.assertEqual(result.audits_found, 0)

  @patch("supekku.scripts.lib.changes.audit_check.collect_gating_findings")
  @patch("supekku.scripts.lib.changes.audit_check._load_audit_frontmatter")
  def test_required_with_all_reconciled_passes(self, mock_load_fm, mock_collect):
    delta = _make_mock_delta("DE-090", requirements=["PROD-008.FR-001"])
    mock_load_fm.return_value = {}
    findings = [
      GatingFinding(
        audit_id="AUD-010",
        finding_id="FIND-001",
        description="ok",
        outcome="aligned",
        disposition_status="reconciled",
        disposition_kind="aligned",
        closure_override_effect=None,
        closure_effect=EFFECT_NONE,
      ),
    ]
    mock_collect.return_value = (findings, 1, [])

    ws = MagicMock()
    ws.delta_registry.collect.return_value = {"DE-090": delta}

    result = check_audit_completeness("DE-090", ws)
    self.assertTrue(result.is_complete)
    self.assertEqual(result.audits_found, 1)
    self.assertEqual(len(result.blocking_findings), 0)

  @patch("supekku.scripts.lib.changes.audit_check.collect_gating_findings")
  @patch("supekku.scripts.lib.changes.audit_check._load_audit_frontmatter")
  def test_required_with_blocking_finding_fails(self, mock_load_fm, mock_collect):
    delta = _make_mock_delta("DE-090", requirements=["PROD-008.FR-001"])
    mock_load_fm.return_value = {}
    findings = [
      GatingFinding(
        audit_id="AUD-010",
        finding_id="FIND-001",
        description="unresolved drift",
        outcome="drift",
        disposition_status="pending",
        disposition_kind="spec_patch",
        closure_override_effect=None,
        closure_effect=EFFECT_BLOCK,
      ),
    ]
    mock_collect.return_value = (findings, 1, [])

    ws = MagicMock()
    ws.delta_registry.collect.return_value = {"DE-090": delta}

    result = check_audit_completeness("DE-090", ws)
    self.assertFalse(result.is_complete)
    self.assertEqual(len(result.blocking_findings), 1)

  @patch("supekku.scripts.lib.changes.audit_check.collect_gating_findings")
  @patch("supekku.scripts.lib.changes.audit_check._load_audit_frontmatter")
  def test_warnings_dont_block(self, mock_load_fm, mock_collect):
    delta = _make_mock_delta("DE-090", requirements=["PROD-008.FR-001"])
    mock_load_fm.return_value = {}
    findings = [
      GatingFinding(
        audit_id="AUD-010",
        finding_id="FIND-001",
        description="follow-up tracked",
        outcome="drift",
        disposition_status="accepted",
        disposition_kind="follow_up_delta",
        closure_override_effect=None,
        refs=[{"kind": "delta", "ref": "DE-100"}],
        closure_effect=EFFECT_WARN,
      ),
    ]
    mock_collect.return_value = (findings, 1, [])

    ws = MagicMock()
    ws.delta_registry.collect.return_value = {"DE-090": delta}

    result = check_audit_completeness("DE-090", ws)
    self.assertTrue(result.is_complete)
    self.assertEqual(len(result.warning_findings), 1)

  def test_unknown_delta_returns_incomplete(self):
    ws = MagicMock()
    ws.delta_registry.collect.return_value = {}
    result = check_audit_completeness("DE-999", ws)
    self.assertFalse(result.is_complete)


class FormatAuditErrorTest(unittest.TestCase):
  """Test format_audit_error output."""

  def test_no_audits_found_message(self):
    result = AuditCheckResult(
      is_complete=False,
      gate_resolution=GATE_REQUIRED,
      audits_found=0,
    )
    output = format_audit_error("DE-079", result)
    self.assertIn("No completed conformance audit", output)
    self.assertIn("--force", output)

  def test_blocking_findings_listed(self):
    result = AuditCheckResult(
      is_complete=False,
      gate_resolution=GATE_REQUIRED,
      audits_found=1,
      blocking_findings=[
        GatingFinding(
          audit_id="AUD-010",
          finding_id="FIND-001",
          description="drift here",
          outcome="drift",
          disposition_status="pending",
          disposition_kind="spec_patch",
          closure_override_effect=None,
          closure_effect=EFFECT_BLOCK,
        ),
      ],
    )
    output = format_audit_error("DE-079", result)
    self.assertIn("FIND-001", output)
    self.assertIn("AUD-010", output)
    self.assertIn("drift here", output)

  def test_collisions_shown(self):
    result = AuditCheckResult(
      is_complete=False,
      gate_resolution=GATE_REQUIRED,
      audits_found=2,
      collisions=["FIND-001 appears in both AUD-010 and AUD-011"],
      blocking_findings=[
        GatingFinding(
          audit_id="AUD-010",
          finding_id="FIND-001",
          description="x",
          outcome="drift",
          disposition_status="pending",
          disposition_kind="spec_patch",
          closure_override_effect=None,
          closure_effect=EFFECT_BLOCK,
        ),
      ],
    )
    output = format_audit_error("DE-079", result)
    self.assertIn("collision", output.lower())


if __name__ == "__main__":
  unittest.main()
