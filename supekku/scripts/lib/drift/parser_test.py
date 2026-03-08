"""Tests for drift ledger parser (VT-065-parser).

Covers DR-065 parser contract table edge cases and normal operation.
"""

from __future__ import annotations

import textwrap

from supekku.scripts.lib.drift.parser import parse_ledger_body


class TestFreeformBodyExtraction:
  """DEC-065-08: freeform body content preserved."""

  def test_body_before_entries(self):
    body = textwrap.dedent("""\
      ## Corpus coverage

      | Doc | Surveyed |
      | --- | --- |
      | PROD-001 | yes |

      ## Entries

      ### DL-047.001: Test entry

      ```yaml
      status: open
      entry_type: contradiction
      ```
    """)
    freeform, entries = parse_ledger_body(body)
    assert "Corpus coverage" in freeform
    assert "PROD-001" in freeform
    assert len(entries) == 1

  def test_no_entries(self):
    body = "Just some text\n\nNo entries here."
    freeform, entries = parse_ledger_body(body)
    assert "Just some text" in freeform
    assert entries == []

  def test_empty_body(self):
    freeform, entries = parse_ledger_body("")
    assert freeform == ""
    assert entries == []


class TestBasicParsing:
  """Normal entry parsing with fenced YAML."""

  def test_single_entry(self):
    body = textwrap.dedent("""\
      ### DL-047.001: Contract authority

      ```yaml
      status: resolved
      entry_type: contradiction
      severity: significant
      topic: contracts
      owner: david
      ```

      FR-006 was revised but flows were not updated.
    """)
    _, entries = parse_ledger_body(body)
    assert len(entries) == 1
    e = entries[0]
    assert e.id == "DL-047.001"
    assert e.title == "Contract authority"
    assert e.status == "resolved"
    assert e.entry_type == "contradiction"
    assert e.severity == "significant"
    assert e.topic == "contracts"
    assert e.owner == "david"
    assert "FR-006" in e.analysis

  def test_multiple_entries(self):
    body = textwrap.dedent("""\
      ### DL-047.001: First entry

      ```yaml
      status: open
      entry_type: contradiction
      ```

      ### DL-047.002: Second entry

      ```yaml
      status: triaged
      entry_type: missing_decision
      ```
    """)
    _, entries = parse_ledger_body(body)
    assert len(entries) == 2
    assert entries[0].id == "DL-047.001"
    assert entries[1].id == "DL-047.002"
    assert entries[1].entry_type == "missing_decision"

  def test_sources_parsed_as_typed(self):
    body = textwrap.dedent("""\
      ### DL-047.001: Test

      ```yaml
      status: open
      entry_type: contradiction
      sources:
        - kind: prod
          ref: PROD-012
          note: "§3: contracts are canonical"
        - kind: adr
          ref: ADR-003
      ```
    """)
    _, entries = parse_ledger_body(body)
    assert len(entries[0].sources) == 2
    s = entries[0].sources[0]
    assert s.kind == "prod"
    assert s.ref == "PROD-012"
    assert s.note == "§3: contracts are canonical"
    assert entries[0].sources[1].note == ""

  def test_claims_parsed_as_typed(self):
    body = textwrap.dedent("""\
      ### DL-047.001: Test

      ```yaml
      status: open
      entry_type: contradiction
      claims:
        - kind: assertion
          label: A
          text: "Contracts are canonical"
        - kind: observation
          text: "Contracts are derived"
      ```
    """)
    _, entries = parse_ledger_body(body)
    assert len(entries[0].claims) == 2
    assert entries[0].claims[0].label == "A"
    assert entries[0].claims[1].label == ""

  def test_discovered_by_parsed(self):
    body = textwrap.dedent("""\
      ### DL-047.001: Test

      ```yaml
      status: open
      entry_type: contradiction
      discovered_by:
        kind: survey
        ref: VA-047-001
      ```
    """)
    _, entries = parse_ledger_body(body)
    assert entries[0].discovered_by is not None
    assert entries[0].discovered_by.kind == "survey"
    assert entries[0].discovered_by.ref == "VA-047-001"

  def test_evidence_list_parsed(self):
    body = textwrap.dedent("""\
      ### DL-047.001: Test

      ```yaml
      status: open
      entry_type: contradiction
      evidence:
        - 2026-03-05 discovered during survey
        - 2026-03-06 triaged as significant
      ```
    """)
    _, entries = parse_ledger_body(body)
    assert len(entries[0].evidence) == 2
    assert "2026-03-05" in entries[0].evidence[0]

  def test_affected_artifacts_parsed(self):
    body = textwrap.dedent("""\
      ### DL-047.001: Test

      ```yaml
      status: resolved
      entry_type: contradiction
      affected_artifacts:
        - PROD-012
        - ADR-003
      ```
    """)
    _, entries = parse_ledger_body(body)
    assert entries[0].affected_artifacts == ["PROD-012", "ADR-003"]

  def test_extra_yaml_keys_preserved(self):
    body = textwrap.dedent("""\
      ### DL-047.001: Test

      ```yaml
      status: open
      entry_type: contradiction
      custom_field: custom_value
      another: 42
      ```
    """)
    _, entries = parse_ledger_body(body)
    assert entries[0].extra == {"custom_field": "custom_value", "another": 42}


class TestParserContractEdgeCases:
  """DR-065 DEC-065-03 parser contract table."""

  def test_malformed_yaml_block(self):
    """Malformed YAML → warning, entry with _parse_error in extra."""
    body = textwrap.dedent("""\
      ### DL-047.001: Bad YAML

      ```yaml
      status: open
      entry_type: [invalid yaml
      missing_colon
      ```
    """)
    _, entries = parse_ledger_body(body)
    assert len(entries) == 1
    assert "_parse_error" in entries[0].extra
    assert entries[0].id == "DL-047.001"
    assert entries[0].title == "Bad YAML"

  def test_missing_required_source_keys(self):
    """Missing required nested keys → warning, malformed record skipped."""
    body = textwrap.dedent("""\
      ### DL-047.001: Bad sources

      ```yaml
      status: open
      entry_type: contradiction
      sources:
        - kind: prod
          ref: PROD-012
        - note: "missing kind and ref"
        - kind: adr
          ref: ADR-003
      ```
    """)
    _, entries = parse_ledger_body(body)
    # Second source is skipped (no kind), first and third preserved
    assert len(entries[0].sources) == 2
    assert entries[0].sources[0].ref == "PROD-012"
    assert entries[0].sources[1].ref == "ADR-003"

  def test_missing_required_claim_keys(self):
    """Missing kind or text → warning, malformed claim skipped."""
    body = textwrap.dedent("""\
      ### DL-047.001: Bad claims

      ```yaml
      status: open
      entry_type: contradiction
      claims:
        - kind: assertion
          text: "Valid claim"
        - label: A
          text: "Missing kind"
        - kind: gap
      ```
    """)
    _, entries = parse_ledger_body(body)
    # Only first claim is valid
    assert len(entries[0].claims) == 1
    assert entries[0].claims[0].text == "Valid claim"

  def test_duplicate_entry_ids(self):
    """Duplicate IDs → warning, both entries preserved."""
    body = textwrap.dedent("""\
      ### DL-047.001: First occurrence

      ```yaml
      status: open
      entry_type: contradiction
      ```

      ### DL-047.001: Second occurrence

      ```yaml
      status: triaged
      entry_type: stale_claim
      ```
    """)
    _, entries = parse_ledger_body(body)
    assert len(entries) == 2
    assert entries[0].status == "open"
    assert entries[1].status == "triaged"

  def test_entry_with_no_yaml_block(self):
    """No YAML block → warning, heading-only entry."""
    body = textwrap.dedent("""\
      ### DL-047.001: No YAML

      This entry has no fenced YAML block, just prose.
    """)
    _, entries = parse_ledger_body(body)
    assert len(entries) == 1
    assert entries[0].id == "DL-047.001"
    assert entries[0].title == "No YAML"
    assert entries[0].status == "open"  # default
    assert entries[0].entry_type == ""  # no data

  def test_multiple_yaml_blocks_first_wins(self):
    """Multiple fenced YAML blocks → first parsed, rest is analysis."""
    body = textwrap.dedent("""\
      ### DL-047.001: Multiple blocks

      ```yaml
      status: resolved
      entry_type: contradiction
      ```

      Some analysis text.

      ```yaml
      status: open
      entry_type: stale_claim
      ```
    """)
    _, entries = parse_ledger_body(body)
    assert len(entries) == 1
    assert entries[0].status == "resolved"
    assert entries[0].entry_type == "contradiction"
    # Second YAML block should be in analysis
    assert "stale_claim" in entries[0].analysis


class TestFenceHeadingPrecedence:
  """DEC-065-03: fences processed before headings."""

  def test_heading_inside_fence_not_split(self):
    """### inside a fenced block is not treated as an entry boundary."""
    body = textwrap.dedent("""\
      ### DL-047.001: Real entry

      ```yaml
      status: open
      entry_type: contradiction
      ```

      Here is some analysis with a code example:

      ```markdown
      ### DL-047.999: This is not a real entry

      It's inside a fence and should be ignored.
      ```

      More analysis after the fenced example.
    """)
    _, entries = parse_ledger_body(body)
    assert len(entries) == 1
    assert entries[0].id == "DL-047.001"
    assert "DL-047.999" in entries[0].analysis

  def test_heading_after_fence_is_split(self):
    """### after a fence closes is a real entry boundary."""
    body = textwrap.dedent("""\
      ### DL-047.001: First

      ```yaml
      status: open
      entry_type: contradiction
      ```

      ```markdown
      ### Not an entry — inside fence
      ```

      ### DL-047.002: Second

      ```yaml
      status: triaged
      entry_type: stale_claim
      ```
    """)
    _, entries = parse_ledger_body(body)
    assert len(entries) == 2
    assert entries[0].id == "DL-047.001"
    assert entries[1].id == "DL-047.002"


class TestProgressiveStrictness:
  """IMPR-007 D13: minimal at creation, stricter at triage."""

  def test_minimal_entry_yaml(self):
    """Minimal valid entry: just entry_type."""
    body = textwrap.dedent("""\
      ### DL-047.001: Minimal

      ```yaml
      entry_type: contradiction
      ```
    """)
    _, entries = parse_ledger_body(body)
    assert len(entries) == 1
    assert entries[0].entry_type == "contradiction"
    assert entries[0].status == "open"
    assert entries[0].severity == ""
    assert entries[0].sources == []

  def test_discovered_by_missing_kind(self):
    """discovered_by without kind → skipped with warning."""
    body = textwrap.dedent("""\
      ### DL-047.001: Bad discovery

      ```yaml
      status: open
      entry_type: contradiction
      discovered_by:
        ref: VA-047-001
      ```
    """)
    _, entries = parse_ledger_body(body)
    assert entries[0].discovered_by is None


class TestAnalysisExtraction:
  """Freeform analysis from content outside the YAML fence."""

  def test_analysis_after_fence(self):
    body = textwrap.dedent("""\
      ### DL-047.001: Test

      ```yaml
      status: open
      entry_type: contradiction
      ```

      This is the analysis text.
      It spans multiple lines.
    """)
    _, entries = parse_ledger_body(body)
    assert "This is the analysis text." in entries[0].analysis
    assert "multiple lines" in entries[0].analysis

  def test_analysis_before_and_after_fence(self):
    body = textwrap.dedent("""\
      ### DL-047.001: Test

      Context before the YAML block.

      ```yaml
      status: open
      entry_type: contradiction
      ```

      Analysis after the YAML block.
    """)
    _, entries = parse_ledger_body(body)
    assert "Context before" in entries[0].analysis
    assert "Analysis after" in entries[0].analysis

  def test_no_analysis(self):
    body = textwrap.dedent("""\
      ### DL-047.001: Test

      ```yaml
      status: open
      entry_type: contradiction
      ```
    """)
    _, entries = parse_ledger_body(body)
    assert entries[0].analysis == ""
