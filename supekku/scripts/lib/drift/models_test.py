"""Tests for drift ledger models and lifecycle vocabulary (VT-065-models)."""

from pathlib import Path

import pytest

from supekku.scripts.lib.drift.models import (
  ASSESSMENTS,
  ENTRY_STATUSES,
  ENTRY_TYPES,
  LEDGER_STATUSES,
  RESOLUTION_PATHS,
  SEVERITIES,
  Claim,
  DiscoveredBy,
  DriftEntry,
  DriftLedger,
  Source,
  is_valid_entry_status,
  is_valid_ledger_status,
)


class TestSource:
  """Source typed substructure."""

  def test_required_fields(self):
    s = Source(kind="prod", ref="PROD-012")
    assert s.kind == "prod"
    assert s.ref == "PROD-012"
    assert s.note == ""

  def test_with_note(self):
    s = Source(kind="adr", ref="ADR-008", note="§3: normative truth")
    assert s.note == "§3: normative truth"

  def test_frozen(self):
    s = Source(kind="prod", ref="PROD-012")
    with pytest.raises(AttributeError):
      s.kind = "adr"  # type: ignore[misc]


class TestClaim:
  """Claim typed substructure."""

  def test_required_fields(self):
    c = Claim(kind="assertion", text="Contracts are canonical")
    assert c.kind == "assertion"
    assert c.text == "Contracts are canonical"
    assert c.label == ""

  def test_with_label(self):
    c = Claim(kind="assertion", text="Contracts are canonical", label="A")
    assert c.label == "A"

  def test_frozen(self):
    c = Claim(kind="gap", text="missing")
    with pytest.raises(AttributeError):
      c.text = "changed"  # type: ignore[misc]


class TestDiscoveredBy:
  """DiscoveredBy typed substructure."""

  def test_required_fields(self):
    d = DiscoveredBy(kind="audit")
    assert d.kind == "audit"
    assert d.ref == ""

  def test_with_ref(self):
    d = DiscoveredBy(kind="survey", ref="VA-047-001")
    assert d.ref == "VA-047-001"

  def test_frozen(self):
    d = DiscoveredBy(kind="human")
    with pytest.raises(AttributeError):
      d.kind = "agent"  # type: ignore[misc]


class TestDriftEntry:
  """DriftEntry model construction and defaults."""

  def test_minimal_entry(self):
    e = DriftEntry(id="DL-047.001", title="Test entry")
    assert e.id == "DL-047.001"
    assert e.title == "Test entry"
    assert e.status == "open"
    assert e.entry_type == ""
    assert e.sources == []
    assert e.claims == []
    assert e.affected_artifacts == []
    assert e.discovered_by is None
    assert e.evidence == []
    assert e.extra == {}

  def test_full_entry(self):
    e = DriftEntry(
      id="DL-047.001",
      title="Contract authority",
      status="resolved",
      entry_type="contradiction",
      severity="significant",
      topic="contracts",
      owner="david",
      sources=[Source(kind="prod", ref="PROD-012")],
      claims=[
        Claim(kind="assertion", text="Contracts are canonical", label="A"),
        Claim(kind="assertion", text="Contracts are derived", label="B"),
      ],
      assessment="confirmed",
      resolution_path="RE",
      resolution_ref="RE-005",
      affected_artifacts=["PROD-012"],
      discovered_by=DiscoveredBy(kind="survey", ref="VA-047-001"),
      analysis="FR-006 was revised but flows were not updated.",
      evidence=["2026-03-05 discovered during PROD spec survey"],
    )
    assert e.status == "resolved"
    assert len(e.sources) == 1
    assert len(e.claims) == 2
    assert e.claims[0].label == "A"
    assert e.discovered_by is not None
    assert e.discovered_by.kind == "survey"

  def test_extra_field_preserved(self):
    e = DriftEntry(
      id="DL-047.001",
      title="Test",
      extra={"custom_field": "value"},
    )
    assert e.extra["custom_field"] == "value"

  def test_entries_are_mutable(self):
    """Entries are mutable — status can be updated in-place."""
    e = DriftEntry(id="DL-047.001", title="Test")
    e.status = "triaged"
    assert e.status == "triaged"


class TestDriftLedger:
  """DriftLedger model construction and defaults."""

  def test_minimal_ledger(self):
    dl = DriftLedger(id="DL-047", name="Test ledger")
    assert dl.id == "DL-047"
    assert dl.name == "Test ledger"
    assert dl.status == "open"
    assert dl.delta_ref == ""
    assert dl.body == ""
    assert dl.entries == []
    assert dl.frontmatter == {}

  def test_ledger_with_entries(self):
    entry = DriftEntry(id="DL-047.001", title="Test entry")
    dl = DriftLedger(
      id="DL-047",
      name="Spec corpus reconciliation",
      path=Path(".spec-driver/drift/DL-047-spec-corpus-reconciliation.md"),
      delta_ref="DE-047",
      entries=[entry],
    )
    assert len(dl.entries) == 1
    assert dl.entries[0].id == "DL-047.001"
    assert dl.delta_ref == "DE-047"

  def test_body_preserved(self):
    dl = DriftLedger(
      id="DL-047",
      name="Test",
      body="## Corpus coverage\n\n| Doc | Surveyed |\n",
    )
    assert "Corpus coverage" in dl.body


class TestLifecycleConstants:
  """Lifecycle vocabulary completeness."""

  def test_ledger_statuses(self):
    assert {"open", "closed"} == LEDGER_STATUSES

  def test_entry_statuses(self):
    expected = {
      "open",
      "triaged",
      "adjudicated",
      "resolved",
      "deferred",
      "dismissed",
      "superseded",
    }
    assert expected == ENTRY_STATUSES

  def test_entry_types(self):
    expected = {
      "contradiction",
      "implementation_drift",
      "stale_claim",
      "missing_decision",
      "ambiguous_intent",
    }
    assert expected == ENTRY_TYPES

  def test_severities(self):
    assert {"blocking", "significant", "cosmetic"} == SEVERITIES

  def test_assessments(self):
    assert {"confirmed", "disputed", "not_drift", "deferred"} == ASSESSMENTS

  def test_resolution_paths_includes_backlog(self):
    """backlog was added per pilot usage — see DR-065."""
    assert "backlog" in RESOLUTION_PATHS
    assert {
      "ADR",
      "RE",
      "DE",
      "editorial",
      "no_change",
      "backlog",
    } == RESOLUTION_PATHS


class TestStatusValidation:
  """Permissive validation with warnings (DEC-057-08 pattern)."""

  def test_valid_entry_status(self):
    assert is_valid_entry_status("open") is True
    assert is_valid_entry_status("resolved") is True

  def test_invalid_entry_status_warns(self, caplog):
    assert is_valid_entry_status("bogus") is False
    assert "bogus" in caplog.text

  def test_valid_ledger_status(self):
    assert is_valid_ledger_status("open") is True
    assert is_valid_ledger_status("closed") is True

  def test_invalid_ledger_status_warns(self, caplog):
    assert is_valid_ledger_status("bogus") is False
    assert "bogus" in caplog.text
