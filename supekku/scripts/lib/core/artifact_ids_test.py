"""Tests for shared artifact ID classification and normalization."""

from __future__ import annotations

import pytest

from supekku.scripts.lib.core.artifact_ids import (
  classify_artifact_id,
  is_artifact_id,
  is_kind,
  normalize_artifact_id,
)


class TestClassifyArtifactId:
  """classify_artifact_id returns the correct kind string."""

  # --- Specs ---

  def test_spec_three_digit(self) -> None:
    assert classify_artifact_id("SPEC-001") == "spec"

  def test_spec_four_digit(self) -> None:
    assert classify_artifact_id("SPEC-0123") == "spec"

  def test_spec_with_suffix(self) -> None:
    assert classify_artifact_id("SPEC-001-AUTH") == "spec"

  def test_spec_with_multi_suffix(self) -> None:
    assert classify_artifact_id("SPEC-001-AUTH-V2") == "spec"

  # --- PROD ---

  def test_prod_basic(self) -> None:
    assert classify_artifact_id("PROD-001") == "prod"

  def test_prod_with_suffix(self) -> None:
    assert classify_artifact_id("PROD-001-MVP") == "prod"

  # --- ADR ---

  def test_adr_basic(self) -> None:
    assert classify_artifact_id("ADR-001") == "adr"

  def test_adr_four_digit(self) -> None:
    assert classify_artifact_id("ADR-0012") == "adr"

  # --- Delta ---

  def test_delta_basic(self) -> None:
    assert classify_artifact_id("DE-001") == "delta"

  def test_delta_four_digit(self) -> None:
    assert classify_artifact_id("DE-0333") == "delta"

  # --- Revision ---

  def test_revision_basic(self) -> None:
    assert classify_artifact_id("RE-001") == "revision"

  # --- Audit ---

  def test_audit_basic(self) -> None:
    assert classify_artifact_id("AUD-001") == "audit"

  # --- Policy ---

  def test_policy_basic(self) -> None:
    assert classify_artifact_id("POL-001") == "policy"

  # --- Standard ---

  def test_standard_basic(self) -> None:
    assert classify_artifact_id("STD-001") == "standard"

  # --- Requirements (must match before backlog) ---

  def test_requirement_fr(self) -> None:
    assert classify_artifact_id("SPEC-001.FR-001") == "requirement"

  def test_requirement_nfr(self) -> None:
    assert classify_artifact_id("SPEC-001.NFR-PERF-01") == "requirement"

  def test_requirement_prod_fr(self) -> None:
    assert classify_artifact_id("PROD-001.FR-LOGIN") == "requirement"

  def test_requirement_spec_with_suffix(self) -> None:
    assert classify_artifact_id("SPEC-001-AUTH.FR-TOKEN") == "requirement"

  # --- Backlog ---

  def test_backlog_issue(self) -> None:
    assert classify_artifact_id("ISSUE-001") == "backlog"

  def test_backlog_improvement(self) -> None:
    assert classify_artifact_id("IMPR-001") == "backlog"

  def test_backlog_problem(self) -> None:
    assert classify_artifact_id("PROB-001") == "backlog"

  def test_backlog_risk(self) -> None:
    assert classify_artifact_id("RISK-001") == "backlog"

  # --- Plan ---

  def test_plan_basic(self) -> None:
    assert classify_artifact_id("IP-033") == "plan"

  def test_plan_four_digit(self) -> None:
    assert classify_artifact_id("IP-0123") == "plan"

  def test_plan_two_digit_rejected(self) -> None:
    assert classify_artifact_id("IP-01") is None

  # --- Phase ---

  def test_phase_basic(self) -> None:
    assert classify_artifact_id("IP-033.PHASE-08") == "phase"

  def test_phase_with_plan_suffix(self) -> None:
    assert classify_artifact_id("IP-033-AUTH.PHASE-01") == "phase"

  def test_phase_single_digit_rejected(self) -> None:
    assert classify_artifact_id("IP-033.PHASE-1") is None

  # --- Verification ---

  def test_verification_vt(self) -> None:
    assert classify_artifact_id("VT-001") == "verification"

  def test_verification_va(self) -> None:
    assert classify_artifact_id("VA-001") == "verification"

  def test_verification_vh(self) -> None:
    assert classify_artifact_id("VH-001") == "verification"

  def test_verification_four_digit(self) -> None:
    assert classify_artifact_id("VT-0012") == "verification"

  def test_verification_two_digit_rejected(self) -> None:
    assert classify_artifact_id("VT-01") is None

  # --- Unrecognized ---

  def test_unrecognized_returns_none(self) -> None:
    assert classify_artifact_id("NOPE-123") is None

  def test_memory_id_not_classified(self) -> None:
    assert classify_artifact_id("mem.fact.auth") is None

  def test_empty_string(self) -> None:
    assert classify_artifact_id("") is None

  def test_random_text(self) -> None:
    assert classify_artifact_id("hello world") is None

  def test_spec_too_few_digits(self) -> None:
    assert classify_artifact_id("SPEC-01") is None

  def test_lowercase_rejected(self) -> None:
    assert classify_artifact_id("spec-001") is None

  def test_adr_two_digit_rejected(self) -> None:
    assert classify_artifact_id("ADR-01") is None


class TestIsArtifactId:
  """is_artifact_id returns bool."""

  def test_recognized(self) -> None:
    assert is_artifact_id("SPEC-001") is True

  def test_unrecognized(self) -> None:
    assert is_artifact_id("nope") is False

  def test_empty(self) -> None:
    assert is_artifact_id("") is False


class TestClassificationOrder:
  """Requirements must be classified before backlog (more specific pattern)."""

  def test_requirement_not_misclassified_as_backlog(self) -> None:
    """SPEC-001.FR-001 should be requirement, not spec or backlog."""
    assert classify_artifact_id("SPEC-001.FR-001") == "requirement"

  def test_plain_spec_not_requirement(self) -> None:
    """SPEC-001 without .FR/NFR suffix is a spec, not requirement."""
    assert classify_artifact_id("SPEC-001") == "spec"


class TestIsKind:
  """is_kind checks a single pattern efficiently."""

  def test_matching_kind(self) -> None:
    assert is_kind("SPEC-001", "spec") is True

  def test_wrong_kind(self) -> None:
    assert is_kind("SPEC-001", "adr") is False

  def test_requirement(self) -> None:
    assert is_kind("SPEC-001.FR-001", "requirement") is True

  def test_verification(self) -> None:
    assert is_kind("VT-001", "verification") is True

  def test_phase(self) -> None:
    assert is_kind("IP-033.PHASE-08", "phase") is True

  def test_unknown_kind_raises(self) -> None:
    with pytest.raises(KeyError):
      is_kind("SPEC-001", "nonexistent")


class TestNormalizeArtifactId:
  """VT-097-normalize: normalize_artifact_id resolves padding variants."""

  KNOWN_IDS = frozenset(
    {
      "ADR-001",
      "ADR-011",
      "DE-097",
      "SPEC-001",
      "ISSUE-031",
      "SPEC-1234",  # 4-digit ID for future-proofing tests
    }
  )

  def test_already_canonical(self) -> None:
    result = normalize_artifact_id("ADR-011", self.KNOWN_IDS)
    assert result.canonical == "ADR-011"
    assert result.diagnostic is None

  def test_two_digit_resolves_to_three(self) -> None:
    result = normalize_artifact_id("ADR-11", self.KNOWN_IDS)
    assert result.canonical == "ADR-011"
    assert result.diagnostic is not None
    assert "ADR-11" in result.diagnostic

  def test_one_digit_resolves_to_three(self) -> None:
    result = normalize_artifact_id("ADR-1", self.KNOWN_IDS)
    assert result.canonical == "ADR-001"
    assert result.diagnostic is not None

  def test_no_match_returns_none(self) -> None:
    result = normalize_artifact_id("ADR-999", self.KNOWN_IDS)
    assert result.canonical is None
    assert result.diagnostic is None

  def test_unrecognized_prefix_returns_none(self) -> None:
    result = normalize_artifact_id("NOPE-123", self.KNOWN_IDS)
    assert result.canonical is None
    assert result.diagnostic is None

  def test_preserves_original(self) -> None:
    result = normalize_artifact_id("ADR-11", self.KNOWN_IDS)
    assert result.original == "ADR-11"

  def test_delta_two_digit(self) -> None:
    result = normalize_artifact_id("DE-97", self.KNOWN_IDS)
    assert result.canonical == "DE-097"
    assert result.diagnostic is not None

  def test_issue_two_digit(self) -> None:
    result = normalize_artifact_id("ISSUE-31", self.KNOWN_IDS)
    assert result.canonical == "ISSUE-031"
    assert result.diagnostic is not None

  def test_four_digit_future_proof(self) -> None:
    """VT-097-normalize-future: 4-digit IDs normalize correctly."""
    result = normalize_artifact_id("SPEC-1234", self.KNOWN_IDS)
    assert result.canonical == "SPEC-1234"
    assert result.diagnostic is None

  def test_short_to_four_digit(self) -> None:
    """VT-097-normalize-future: short form resolves to 4-digit."""
    known = frozenset({"SPEC-1234"})
    result = normalize_artifact_id("SPEC-1234", known)
    assert result.canonical == "SPEC-1234"
    # Already canonical, no diagnostic
    assert result.diagnostic is None

  def test_three_digit_to_four_digit(self) -> None:
    """When only a 4-digit form exists, 3-digit input doesn't match."""
    known = frozenset({"SPEC-1234"})
    result = normalize_artifact_id("SPEC-123", known)
    # 123 != 1234, padding won't help
    assert result.canonical is None

  def test_empty_string(self) -> None:
    result = normalize_artifact_id("", self.KNOWN_IDS)
    assert result.canonical is None

  def test_memory_id_skipped(self) -> None:
    """Memory IDs use a different scheme — normalizer should not touch them."""
    result = normalize_artifact_id("mem.fact.auth", self.KNOWN_IDS)
    assert result.canonical is None

  def test_empty_known_ids(self) -> None:
    result = normalize_artifact_id("ADR-001", frozenset())
    assert result.canonical is None
