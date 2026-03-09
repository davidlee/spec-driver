"""Tests for MemoryRecord model."""

from __future__ import annotations

import unittest
from datetime import date
from pathlib import Path

from supekku.scripts.lib.memory.models import MemoryRecord


class TestMemoryRecord(unittest.TestCase):
  """Test MemoryRecord dataclass construction and serialization."""

  def test_minimal_construction(self) -> None:
    """Construct with only required fields."""
    record = MemoryRecord(
      id="mem.fact.test",
      name="Test Memory",
      status="active",
      memory_type="fact",
      path="/repo/memory/mem.fact.test.md",
    )
    self.assertEqual(record.id, "mem.fact.test")
    self.assertEqual(record.name, "Test Memory")
    self.assertEqual(record.status, "active")
    self.assertEqual(record.memory_type, "fact")
    self.assertEqual(record.path, "/repo/memory/mem.fact.test.md")

  def test_optional_fields_default(self) -> None:
    """Optional fields have sensible defaults."""
    record = MemoryRecord(
      id="mem.fact.test",
      name="Test",
      status="active",
      memory_type="fact",
      path="",
    )
    self.assertIsNone(record.created)
    self.assertIsNone(record.updated)
    self.assertIsNone(record.confidence)
    self.assertIsNone(record.verified)
    self.assertIsNone(record.verified_sha)
    self.assertIsNone(record.review_by)
    self.assertEqual(record.summary, "")
    self.assertEqual(record.tags, [])
    self.assertEqual(record.owners, [])
    self.assertEqual(record.requires_reading, [])
    self.assertEqual(record.scope, {})
    self.assertEqual(record.priority, {})
    self.assertEqual(record.provenance, {})
    self.assertEqual(record.audience, [])
    self.assertEqual(record.visibility, [])
    self.assertEqual(record.relations, [])

  def test_full_construction(self) -> None:
    """Construct with all fields populated."""
    record = MemoryRecord(
      id="mem.signpost.auth.prereading",
      name="ADR-11 Required Pre-Reading",
      status="active",
      memory_type="signpost",
      path="/repo/memory/mem.signpost.auth.prereading.md",
      created=date(2026, 2, 1),
      updated=date(2026, 3, 1),
      confidence="high",
      verified=date(2026, 3, 1),
      review_by=date(2026, 5, 1),
      summary="Pre-read ADR-11 before auth changes",
      tags=["auth", "pre-read"],
      owners=["platform-team"],
      requires_reading=["specify/decisions/ADR-011-auth-flow.md"],
      scope={"globs": ["src/auth/**"], "commands": ["test auth:integration"]},
      priority={"severity": "high", "weight": 10},
      provenance={
        "sources": [{"kind": "adr", "ref": "specify/decisions/ADR-011-auth-flow.md"}],
      },
      audience=["human", "agent"],
      visibility=["pre"],
      relations=[{"type": "relates_to", "target": "ADR-011"}],
    )
    self.assertEqual(record.confidence, "high")
    self.assertEqual(record.verified, date(2026, 3, 1))
    self.assertEqual(record.review_by, date(2026, 5, 1))
    self.assertEqual(record.scope["globs"], ["src/auth/**"])
    self.assertEqual(record.priority["severity"], "high")
    self.assertEqual(record.audience, ["human", "agent"])

  def test_to_dict_minimal(self) -> None:
    """to_dict with minimal record omits empty optional fields."""
    record = MemoryRecord(
      id="mem.fact.test",
      name="Test",
      status="active",
      memory_type="fact",
      path="/repo/memory/mem.fact.test.md",
    )
    root = Path("/repo")
    d = record.to_dict(root)

    self.assertEqual(d["id"], "mem.fact.test")
    self.assertEqual(d["name"], "Test")
    self.assertEqual(d["status"], "active")
    self.assertEqual(d["memory_type"], "fact")
    self.assertEqual(d["path"], "memory/mem.fact.test.md")
    # Optional fields omitted when empty/None
    self.assertNotIn("created", d)
    self.assertNotIn("tags", d)
    self.assertNotIn("scope", d)
    self.assertNotIn("confidence", d)

  def test_to_dict_full(self) -> None:
    """to_dict includes all populated fields."""
    record = MemoryRecord(
      id="mem.signpost.auth.prereading",
      name="Auth Pre-Reading",
      status="active",
      memory_type="signpost",
      path="/repo/memory/mem.signpost.auth.prereading.md",
      created=date(2026, 2, 1),
      updated=date(2026, 3, 1),
      confidence="high",
      verified=date(2026, 3, 1),
      review_by=date(2026, 5, 1),
      summary="Pre-read ADR-11",
      tags=["auth"],
      owners=["platform-team"],
      requires_reading=["ADR-011"],
      scope={"globs": ["src/auth/**"]},
      priority={"severity": "high", "weight": 10},
      provenance={"sources": [{"kind": "adr", "ref": "ADR-011"}]},
      audience=["agent"],
      visibility=["pre"],
      relations=[{"type": "relates_to", "target": "ADR-011"}],
    )
    root = Path("/repo")
    d = record.to_dict(root)

    self.assertEqual(d["created"], "2026-02-01")
    self.assertEqual(d["updated"], "2026-03-01")
    self.assertEqual(d["confidence"], "high")
    self.assertEqual(d["verified"], "2026-03-01")
    self.assertEqual(d["review_by"], "2026-05-01")
    self.assertEqual(d["summary"], "Pre-read ADR-11")
    self.assertEqual(d["tags"], ["auth"])
    self.assertEqual(d["owners"], ["platform-team"])
    self.assertEqual(d["requires_reading"], ["ADR-011"])
    self.assertEqual(d["scope"], {"globs": ["src/auth/**"]})
    self.assertEqual(d["priority"], {"severity": "high", "weight": 10})
    self.assertEqual(d["provenance"], {"sources": [{"kind": "adr", "ref": "ADR-011"}]})
    self.assertEqual(d["audience"], ["agent"])
    self.assertEqual(d["visibility"], ["pre"])
    self.assertEqual(d["relations"], [{"type": "relates_to", "target": "ADR-011"}])

  def test_to_dict_path_relativization(self) -> None:
    """to_dict relativizes path against root."""
    record = MemoryRecord(
      id="mem.fact.test",
      name="Test",
      status="active",
      memory_type="fact",
      path="/my/project/memory/mem.fact.test.md",
    )
    d = record.to_dict(Path("/my/project"))
    self.assertEqual(d["path"], "memory/mem.fact.test.md")

  def test_to_dict_empty_path(self) -> None:
    """to_dict handles empty path."""
    record = MemoryRecord(
      id="mem.fact.test",
      name="Test",
      status="active",
      memory_type="fact",
      path="",
    )
    d = record.to_dict(Path("/repo"))
    self.assertEqual(d["path"], "")

  def test_from_frontmatter_minimal(self) -> None:
    """from_frontmatter constructs record from minimal frontmatter dict."""
    fm = {
      "id": "mem.fact.test",
      "name": "Test",
      "status": "active",
      "memory_type": "fact",
    }
    record = MemoryRecord.from_frontmatter(
      Path("/repo/memory/mem.fact.test.md"),
      fm,
    )
    self.assertEqual(record.id, "mem.fact.test")
    self.assertEqual(record.memory_type, "fact")
    self.assertEqual(record.path, "/repo/memory/mem.fact.test.md")

  def test_from_frontmatter_with_dates(self) -> None:
    """from_frontmatter parses date strings and date objects."""
    fm = {
      "id": "mem.fact.test",
      "name": "Test",
      "status": "active",
      "memory_type": "fact",
      "created": "2026-03-01",
      "updated": date(2026, 3, 2),  # YAML parser may return date objects
      "verified": "2026-03-01",
      "review_by": "2026-06-01",
    }
    record = MemoryRecord.from_frontmatter(Path("/repo/mem.fact.test.md"), fm)
    self.assertEqual(record.created, date(2026, 3, 1))
    self.assertEqual(record.updated, date(2026, 3, 2))
    self.assertEqual(record.verified, date(2026, 3, 1))
    self.assertEqual(record.review_by, date(2026, 6, 1))

  def test_from_frontmatter_full(self) -> None:
    """from_frontmatter handles all optional fields."""
    fm = {
      "id": "mem.signpost.auth.prereading",
      "name": "Auth Pre-Reading",
      "status": "active",
      "memory_type": "signpost",
      "confidence": "high",
      "summary": "Read ADR-11 first",
      "tags": ["auth"],
      "owners": ["team-a"],
      "requires_reading": ["ADR-011"],
      "scope": {"globs": ["src/**"]},
      "priority": {"severity": "high", "weight": 5},
      "provenance": {"sources": [{"kind": "adr", "ref": "ADR-011"}]},
      "audience": ["agent"],
      "visibility": ["pre", "on_demand"],
      "relations": [{"type": "relates_to", "target": "ADR-011"}],
    }
    path = Path("/repo/mem.signpost.auth.prereading.md")
    record = MemoryRecord.from_frontmatter(path, fm)
    self.assertEqual(record.confidence, "high")
    self.assertEqual(record.requires_reading, ["ADR-011"])
    self.assertEqual(record.scope, {"globs": ["src/**"]})
    self.assertEqual(record.audience, ["agent"])
    self.assertEqual(record.visibility, ["pre", "on_demand"])

  def test_from_frontmatter_bad_date_ignored(self) -> None:
    """from_frontmatter sets None for unparseable dates."""
    fm = {
      "id": "mem.fact.test",
      "name": "Test",
      "status": "active",
      "memory_type": "fact",
      "created": "not-a-date",
      "verified": "March 2026",
    }
    record = MemoryRecord.from_frontmatter(Path("/repo/mem.fact.test.md"), fm)
    self.assertIsNone(record.created)
    self.assertIsNone(record.verified)

  def test_links_defaults_empty(self) -> None:
    """links field defaults to empty dict."""
    record = MemoryRecord(
      id="mem.fact.test",
      name="Test",
      status="active",
      memory_type="fact",
      path="",
    )
    self.assertEqual(record.links, {})

  def test_from_frontmatter_with_links(self) -> None:
    """from_frontmatter parses links object."""
    links = {
      "out": [
        {"id": "ADR-001", "path": "decisions/ADR-001.md", "kind": "adr"},
      ],
      "missing": [{"raw": "ADR-999"}],
    }
    fm = {
      "id": "mem.fact.test",
      "name": "Test",
      "status": "active",
      "memory_type": "fact",
      "links": links,
    }
    record = MemoryRecord.from_frontmatter(
      Path("/repo/mem.fact.test.md"),
      fm,
    )
    self.assertEqual(record.links, links)

  def test_to_dict_with_links(self) -> None:
    """to_dict includes links when non-empty."""
    links = {
      "out": [
        {"id": "ADR-001", "path": "a.md", "kind": "adr"},
      ],
    }
    record = MemoryRecord(
      id="mem.fact.test",
      name="Test",
      status="active",
      memory_type="fact",
      path="/repo/memory/mem.fact.test.md",
      links=links,
    )
    d = record.to_dict(Path("/repo"))
    self.assertEqual(d["links"], links)

  def test_to_dict_omits_empty_links(self) -> None:
    """to_dict omits links when empty."""
    record = MemoryRecord(
      id="mem.fact.test",
      name="Test",
      status="active",
      memory_type="fact",
      path="/repo/memory/mem.fact.test.md",
    )
    d = record.to_dict(Path("/repo"))
    self.assertNotIn("links", d)


class TestMemoryRecordVerifiedSha(unittest.TestCase):
  """Tests for verified_sha field on MemoryRecord."""

  SAMPLE_SHA = "a" * 40

  def test_from_frontmatter_with_verified_sha(self) -> None:
    fm = {
      "id": "mem.fact.test",
      "name": "Test",
      "status": "active",
      "memory_type": "fact",
      "verified_sha": self.SAMPLE_SHA,
    }
    record = MemoryRecord.from_frontmatter(Path("/repo/mem.fact.test.md"), fm)
    self.assertEqual(record.verified_sha, self.SAMPLE_SHA)

  def test_from_frontmatter_without_verified_sha(self) -> None:
    fm = {
      "id": "mem.fact.test",
      "name": "Test",
      "status": "active",
      "memory_type": "fact",
    }
    record = MemoryRecord.from_frontmatter(Path("/repo/mem.fact.test.md"), fm)
    self.assertIsNone(record.verified_sha)

  def test_to_dict_includes_verified_sha_when_present(self) -> None:
    record = MemoryRecord(
      id="mem.fact.test",
      name="Test",
      status="active",
      memory_type="fact",
      path="/repo/memory/mem.fact.test.md",
      verified_sha=self.SAMPLE_SHA,
    )
    d = record.to_dict(Path("/repo"))
    self.assertEqual(d["verified_sha"], self.SAMPLE_SHA)

  def test_to_dict_omits_verified_sha_when_none(self) -> None:
    record = MemoryRecord(
      id="mem.fact.test",
      name="Test",
      status="active",
      memory_type="fact",
      path="/repo/memory/mem.fact.test.md",
    )
    d = record.to_dict(Path("/repo"))
    self.assertNotIn("verified_sha", d)


if __name__ == "__main__":
  unittest.main()
