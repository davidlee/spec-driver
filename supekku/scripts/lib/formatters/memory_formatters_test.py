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
    assert "mem.fact.test" in output
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
