"""Tests for memory display formatters."""

from __future__ import annotations

import json
from datetime import date

from supekku.scripts.lib.formatters.memory_formatters import (
  format_link_graph_json,
  format_link_graph_table,
  format_link_graph_tree,
  format_memory_details,
  format_memory_list_json,
  format_memory_list_table,
)
from supekku.scripts.lib.memory.links import LinkGraphNode
from supekku.scripts.lib.memory.models import MemoryRecord


def _make_record(**overrides) -> MemoryRecord:
  """Create a MemoryRecord with sensible defaults, overridable."""
  defaults = {
    "id": "mem.fact.test",
    "name": "Test Memory",
    "status": "active",
    "memory_type": "fact",
    "path": "/repo/memory/mem.fact.test.md",
    "created": date(2026, 1, 15),
    "updated": date(2026, 2, 1),
  }
  defaults.update(overrides)
  return MemoryRecord(**defaults)


# --- format_memory_details ---


class TestFormatMemoryDetails:
  """Tests for format_memory_details."""

  def test_minimal_record(self) -> None:
    record = _make_record()
    output = format_memory_details(record)
    assert "mem.fact.test" in output
    assert "Test Memory" in output
    assert "active" in output
    assert "fact" in output

  def test_includes_dates(self) -> None:
    record = _make_record()
    output = format_memory_details(record)
    assert "2026-01-15" in output
    assert "2026-02-01" in output

  def test_includes_tags(self) -> None:
    record = _make_record(tags=["arch", "python"])
    output = format_memory_details(record)
    assert "arch" in output
    assert "python" in output

  def test_includes_confidence(self) -> None:
    record = _make_record(confidence="high")
    output = format_memory_details(record)
    assert "high" in output

  def test_includes_summary(self) -> None:
    record = _make_record(summary="A brief summary")
    output = format_memory_details(record)
    assert "A brief summary" in output

  def test_includes_path(self) -> None:
    record = _make_record()
    output = format_memory_details(record)
    assert "mem.fact.test.md" in output

  def test_omits_empty_optional_fields(self) -> None:
    record = _make_record(confidence=None, tags=[], summary="")
    output = format_memory_details(record)
    assert "Confidence:" not in output
    assert "Tags:" not in output
    assert "Summary:" not in output

  def test_no_dates(self) -> None:
    record = _make_record(created=None, updated=None)
    output = format_memory_details(record)
    # Should still format without error
    assert "mem.fact.test" in output

  def test_full_record(self) -> None:
    """All non-empty fields render in detail view."""
    record = _make_record(
      confidence="high",
      summary="Full test",
      tags=["arch", "py"],
      verified=date(2026, 2, 15),
      review_by=date(2026, 6, 1),
      owners=["alice", "bob"],
      audience=["human", "agent"],
      visibility=["pre", "on_demand"],
      requires_reading=["ADR-011.md", "SPEC-042.md"],
      scope={
        "paths": ["src/auth/cache.ts"],
        "globs": ["src/auth/**"],
        "commands": ["test auth"],
        "languages": ["ts"],
      },
      priority={"severity": "high", "weight": 10},
      provenance={
        "sources": [
          {"kind": "adr", "ref": "ADR-011.md", "note": "Primary"},
        ]
      },
      relations=[
        {"type": "implements", "target": "FR-102", "annotation": "Auth cache"},
      ],
    )
    output = format_memory_details(record)

    # Dates
    assert "Verified: 2026-02-15" in output
    assert "Review by: 2026-06-01" in output

    # Lists
    assert "Owners: alice, bob" in output
    assert "Audience: human, agent" in output
    assert "Visibility: pre, on_demand" in output
    assert "Requires reading: ADR-011.md, SPEC-042.md" in output

    # Scope
    assert "Scope:" in output
    assert "paths: src/auth/cache.ts" in output
    assert "globs: src/auth/**" in output
    assert "commands: test auth" in output
    assert "languages: ts" in output

    # Priority
    assert "Priority:" in output
    assert "severity: high" in output
    assert "weight: 10" in output

    # Provenance
    assert "Provenance:" in output
    assert "adr: ADR-011.md (Primary)" in output

    # Relations
    assert "Relations:" in output
    assert "implements → FR-102 (Auth cache)" in output

  def test_empty_scope_omitted(self) -> None:
    record = _make_record(scope={})
    output = format_memory_details(record)
    assert "Scope:" not in output

  def test_empty_priority_omitted(self) -> None:
    record = _make_record(priority={})
    output = format_memory_details(record)
    assert "Priority:" not in output

  def test_empty_provenance_omitted(self) -> None:
    record = _make_record(provenance={})
    output = format_memory_details(record)
    assert "Provenance:" not in output

  def test_empty_relations_omitted(self) -> None:
    record = _make_record(relations=[])
    output = format_memory_details(record)
    assert "Relations:" not in output

  def test_includes_resolved_links(self) -> None:
    record = _make_record(
      links={
        "out": [
          {"id": "ADR-001", "path": "a.md", "kind": "adr"},
        ],
      },
    )
    output = format_memory_details(record)
    assert "Links:" in output
    assert "ADR-001 (adr)" in output

  def test_includes_link_label(self) -> None:
    record = _make_record(
      links={
        "out": [
          {
            "id": "ADR-001",
            "path": "a.md",
            "kind": "adr",
            "label": "Auth",
          },
        ],
      },
    )
    output = format_memory_details(record)
    assert "[Auth]" in output

  def test_includes_missing_links(self) -> None:
    record = _make_record(
      links={"missing": [{"raw": "ADR-999"}]},
    )
    output = format_memory_details(record)
    assert "Links:" in output
    assert "ADR-999 (unresolved)" in output

  def test_empty_links_omitted(self) -> None:
    record = _make_record(links={})
    output = format_memory_details(record)
    assert "Links:" not in output


# --- format_memory_list_table ---


class TestFormatMemoryListTable:
  """Tests for format_memory_list_table."""

  def test_table_output(self) -> None:
    records = [_make_record(), _make_record(id="mem.fact.other", name="Other")]
    output = format_memory_list_table(records)
    assert "mem.fact.test" in output
    assert "mem.fact.other" in output

  def test_json_format(self) -> None:
    records = [_make_record()]
    output = format_memory_list_table(records, format_type="json")
    parsed = json.loads(output)
    assert "items" in parsed
    assert len(parsed["items"]) == 1
    assert parsed["items"][0]["id"] == "mem.fact.test"

  def test_tsv_format(self) -> None:
    records = [_make_record()]
    output = format_memory_list_table(records, format_type="tsv")
    assert "mem.fact.test" in output
    assert "\t" in output

  def test_empty_list(self) -> None:
    output = format_memory_list_table([])
    # Should not error; table with no rows
    assert isinstance(output, str)

  def test_table_includes_type_column(self) -> None:
    records = [_make_record(memory_type="pattern")]
    output = format_memory_list_table(records)
    assert "pattern" in output

  def test_truncate_table(self) -> None:
    """Table with truncate=True does not error and still renders."""
    records = [_make_record(name="A" * 200, tags=["tag-" + str(i) for i in range(20)])]
    output = format_memory_list_table(records, truncate=True)
    # ID fragments should appear (Rich may wrap across lines in narrow terminals)
    assert "mem.fact" in output
    # Truncated content should not contain the full long name
    assert "A" * 200 not in output

  def test_tsv_column_count(self) -> None:
    """TSV rows have exactly 6 columns: id, status, type, name, confidence, updated."""
    records = [
      _make_record(confidence="high"),
      _make_record(id="mem.fact.other", name="Second", confidence=None),
    ]
    output = format_memory_list_table(records, format_type="tsv")
    rows = output.strip().split("\n")
    assert len(rows) == 2
    for row in rows:
      cols = row.split("\t")
      assert len(cols) == 6, f"Expected 6 TSV columns, got {len(cols)}: {cols}"

  def test_tsv_column_content(self) -> None:
    """TSV columns contain expected values in order."""
    records = [_make_record(confidence="medium")]
    output = format_memory_list_table(records, format_type="tsv")
    cols = output.strip().split("\t")
    assert cols[0] == "mem.fact.test"
    assert cols[1] == "active"
    assert cols[2] == "fact"
    assert cols[3] == "Test Memory"
    assert cols[4] == "medium"
    assert cols[5] == "2026-02-01"

  def test_tsv_no_confidence(self) -> None:
    """TSV renders empty string for missing confidence."""
    records = [_make_record(confidence=None)]
    output = format_memory_list_table(records, format_type="tsv")
    cols = output.strip().split("\t")
    assert cols[4] == ""


# --- format_memory_list_json ---


class TestFormatMemoryListJson:
  """Tests for format_memory_list_json."""

  def test_structure(self) -> None:
    records = [_make_record()]
    output = format_memory_list_json(records)
    parsed = json.loads(output)
    assert "items" in parsed
    item = parsed["items"][0]
    assert item["id"] == "mem.fact.test"
    assert item["name"] == "Test Memory"
    assert item["status"] == "active"
    assert item["memory_type"] == "fact"

  def test_includes_optional_fields(self) -> None:
    records = [
      _make_record(
        tags=["core"],
        confidence="high",
        summary="Brief",
      )
    ]
    output = format_memory_list_json(records)
    item = json.loads(output)["items"][0]
    assert item["tags"] == ["core"]
    assert item["confidence"] == "high"
    assert item["summary"] == "Brief"

  def test_empty_list(self) -> None:
    output = format_memory_list_json([])
    parsed = json.loads(output)
    assert parsed["items"] == []

  def test_date_serialization_iso(self) -> None:
    """JSON serializes dates as ISO-8601 strings, not raw date objects."""
    records = [_make_record(created=date(2026, 1, 15), updated=date(2026, 2, 1))]
    output = format_memory_list_json(records)
    item = json.loads(output)["items"][0]
    assert item["created"] == "2026-01-15"
    assert item["updated"] == "2026-02-01"

  def test_null_dates_in_json(self) -> None:
    """JSON serializes None dates as null."""
    records = [_make_record(created=None, updated=None)]
    output = format_memory_list_json(records)
    item = json.loads(output)["items"][0]
    assert item["created"] is None
    assert item["updated"] is None

  def test_json_includes_links(self) -> None:
    """JSON output includes links when present."""
    links = {
      "out": [
        {"id": "ADR-001", "path": "a.md", "kind": "adr"},
      ],
    }
    records = [_make_record(links=links)]
    output = format_memory_list_json(records)
    item = json.loads(output)["items"][0]
    assert item["links"] == links

  def test_json_omits_empty_links(self) -> None:
    """JSON output omits links when empty."""
    records = [_make_record(links={})]
    output = format_memory_list_json(records)
    item = json.loads(output)["items"][0]
    assert "links" not in item


# --- format_link_graph_table ---


def _sample_nodes() -> list[LinkGraphNode]:
  return [
    LinkGraphNode(id="mem.root", name="Root", depth=0, memory_type="signpost"),
    LinkGraphNode(id="mem.a", name="Node A", depth=1, memory_type="concept"),
    LinkGraphNode(id="mem.b", name="Node B", depth=1, memory_type="fact"),
    LinkGraphNode(id="mem.c", name="Node C", depth=2, memory_type="pattern"),
  ]


class TestFormatLinkGraphTable:
  """Tests for format_link_graph_table."""

  def test_empty(self) -> None:
    assert format_link_graph_table([]) == ""

  def test_single_node(self) -> None:
    nodes = [LinkGraphNode("mem.a", "A", 0, "fact")]
    output = format_link_graph_table(nodes)
    assert "mem.a" in output
    assert "A" in output

  def test_multi_depth_indentation(self) -> None:
    output = format_link_graph_table(_sample_nodes())
    lines = output.split("\n")
    assert lines[0].startswith("0")
    assert "mem.root" in lines[0]
    # Depth 1 nodes have 2-space indent
    assert "  mem.a" in lines[1]
    # Depth 2 has 4-space indent
    assert "    mem.c" in lines[3]

  def test_includes_type(self) -> None:
    output = format_link_graph_table(_sample_nodes())
    assert "signpost" in output
    assert "concept" in output


class TestFormatLinkGraphTree:
  """Tests for format_link_graph_tree."""

  def test_empty(self) -> None:
    assert format_link_graph_tree([]) == ""

  def test_single_node(self) -> None:
    nodes = [LinkGraphNode("mem.a", "A", 0, "fact")]
    output = format_link_graph_tree(nodes)
    assert output == "mem.a — A (fact)"

  def test_multi_depth(self) -> None:
    output = format_link_graph_tree(_sample_nodes())
    lines = output.split("\n")
    assert lines[0] == "mem.root — Root (signpost)"
    assert lines[1] == "  mem.a — Node A (concept)"
    assert lines[3] == "    mem.c — Node C (pattern)"

  def test_empty_type_no_suffix(self) -> None:
    nodes = [LinkGraphNode("mem.a", "A", 0, "")]
    output = format_link_graph_tree(nodes)
    assert output == "mem.a — A"


class TestFormatLinkGraphJson:
  """Tests for format_link_graph_json."""

  def test_empty(self) -> None:
    output = format_link_graph_json([])
    assert json.loads(output) == []

  def test_structure(self) -> None:
    nodes = [LinkGraphNode("mem.a", "A", 0, "fact")]
    parsed = json.loads(format_link_graph_json(nodes))
    assert len(parsed) == 1
    assert parsed[0] == {
      "id": "mem.a",
      "name": "A",
      "depth": 0,
      "memory_type": "fact",
    }

  def test_multi_node(self) -> None:
    parsed = json.loads(format_link_graph_json(_sample_nodes()))
    assert len(parsed) == 4
    assert parsed[2]["depth"] == 1


# --- format_staleness_table ---


from supekku.scripts.lib.formatters.memory_formatters import (  # noqa: E402
  format_staleness_table,
)
from supekku.scripts.lib.memory.staleness import StalenessInfo  # noqa: E402


def _make_staleness(
  memory_id: str = "mem.test",
  verified_sha: str | None = None,
  verified_date: date | None = None,
  scope_paths: list[str] | None = None,
  commits_since: int | None = None,
  days_since: int | None = None,
  has_scope: bool = False,
  confidence: str | None = None,
) -> tuple[StalenessInfo, MemoryRecord]:
  """Build a StalenessInfo + MemoryRecord pair for formatter tests."""
  info = StalenessInfo(
    memory_id=memory_id,
    verified_sha=verified_sha,
    verified_date=verified_date,
    scope_paths=scope_paths or [],
    commits_since=commits_since,
    days_since=days_since,
    has_scope=has_scope,
  )
  record = _make_record(
    id=memory_id,
    confidence=confidence or "medium",
    verified=verified_date,
    verified_sha=verified_sha,
  )
  return info, record


class TestFormatStalenessTable:
  """Tests for format_staleness_table."""

  def test_empty_input(self) -> None:
    output = format_staleness_table([], {})
    assert output == ""

  def test_scoped_attested_tier(self) -> None:
    """Scoped+attested memories appear in tier 1."""
    info, record = _make_staleness(
      memory_id="mem.scoped.attested",
      verified_sha="a" * 40,
      verified_date=date(2026, 3, 1),
      scope_paths=["supekku/cli/"],
      commits_since=5,
      days_since=8,
      has_scope=True,
      confidence="high",
    )
    records = {"mem.scoped.attested": record}
    output = format_staleness_table([info], records)
    assert "scoped, attested" in output
    assert "mem.scoped.attested" in output
    assert "5" in output  # commits_since

  def test_scoped_unattested_tier(self) -> None:
    """Scoped+unattested memories appear in tier 2."""
    info, record = _make_staleness(
      memory_id="mem.scoped.unattested",
      verified_date=date(2026, 3, 1),
      scope_paths=["supekku/tui/"],
      days_since=8,
      has_scope=True,
    )
    records = {"mem.scoped.unattested": record}
    output = format_staleness_table([info], records)
    assert "scoped, unattested" in output
    assert "mem.scoped.unattested" in output

  def test_unscoped_tier(self) -> None:
    """Unscoped memories appear in tier 3."""
    info, record = _make_staleness(
      memory_id="mem.unscoped",
      verified_date=date(2026, 1, 15),
      days_since=53,
      has_scope=False,
    )
    records = {"mem.unscoped": record}
    output = format_staleness_table([info], records)
    assert "unscoped" in output
    assert "mem.unscoped" in output

  def test_tier_ordering(self) -> None:
    """Tiers appear in order: scoped+attested, scoped+unattested, unscoped."""
    attested_info, attested_rec = _make_staleness(
      memory_id="mem.attested",
      verified_sha="a" * 40,
      verified_date=date(2026, 3, 1),
      scope_paths=["supekku/cli/"],
      commits_since=3,
      days_since=8,
      has_scope=True,
    )
    unattested_info, unattested_rec = _make_staleness(
      memory_id="mem.unattested",
      verified_date=date(2026, 3, 1),
      scope_paths=["supekku/tui/"],
      days_since=8,
      has_scope=True,
    )
    unscoped_info, unscoped_rec = _make_staleness(
      memory_id="mem.unscoped",
      days_since=53,
      has_scope=False,
    )
    records = {
      "mem.attested": attested_rec,
      "mem.unattested": unattested_rec,
      "mem.unscoped": unscoped_rec,
    }
    infos = [unscoped_info, attested_info, unattested_info]
    output = format_staleness_table(infos, records)

    # Tier headers should appear in order
    idx_attested = output.find("scoped, attested")
    idx_unattested = output.find("scoped, unattested")
    idx_unscoped = output.find("unscoped")
    assert idx_attested < idx_unattested < idx_unscoped

  def test_sort_within_attested_tier(self) -> None:
    """Attested tier sorts by commits_since descending."""
    info_high, rec_high = _make_staleness(
      memory_id="mem.high",
      verified_sha="a" * 40,
      verified_date=date(2026, 3, 1),
      scope_paths=["a/"],
      commits_since=50,
      has_scope=True,
    )
    info_low, rec_low = _make_staleness(
      memory_id="mem.low",
      verified_sha="b" * 40,
      verified_date=date(2026, 3, 1),
      scope_paths=["b/"],
      commits_since=2,
      has_scope=True,
    )
    records = {"mem.high": rec_high, "mem.low": rec_low}
    output = format_staleness_table(
      [info_low, info_high],
      records,
    )
    idx_high = output.find("mem.high")
    idx_low = output.find("mem.low")
    assert idx_high < idx_low

  def test_empty_tier_omitted(self) -> None:
    """Tiers with no entries are not shown."""
    info, record = _make_staleness(
      memory_id="mem.unscoped",
      days_since=10,
      has_scope=False,
    )
    records = {"mem.unscoped": record}
    output = format_staleness_table([info], records)
    assert "scoped, attested" not in output
    assert "scoped, unattested" not in output
    assert "unscoped" in output
