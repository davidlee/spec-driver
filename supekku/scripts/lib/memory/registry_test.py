"""Tests for MemoryRegistry."""

from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

from supekku.scripts.lib.core.paths import MEMORY_DIR, SPECS_DIR
from supekku.scripts.lib.memory.registry import MemoryRegistry

# ── Fixture content ─────────────────────────────────────────────

MINIMAL_MEM = """\
---
id: mem.fact.test
name: Test Fact
slug: test-fact
kind: memory
status: active
created: 2026-03-01
updated: 2026-03-01
memory_type: fact
---

A simple fact for testing.
"""

FULL_MEM = """\
---
id: mem.signpost.auth.prereading
name: Auth Pre-Reading
slug: auth-prereading
kind: memory
status: active
created: 2026-02-01
updated: 2026-03-01
memory_type: signpost
confidence: high
verified: 2026-03-01
review_by: 2026-05-01
summary: Pre-read ADR-11 before auth changes
tags: [auth, pre-read]
owners: [platform-team]
requires_reading:
  - specify/decisions/ADR-011-auth-flow.md
scope:
  globs: ["src/auth/**"]
  commands: ["test auth:integration"]
priority:
  severity: high
  weight: 10
provenance:
  sources:
    - kind: adr
      ref: specify/decisions/ADR-011-auth-flow.md
audience: [human, agent]
visibility: [pre]
relations:
  - type: relates_to
    target: ADR-011
---

Detailed body content for this memory record.
"""

PATTERN_MEM = """\
---
id: mem.pattern.python.naming
name: Python Naming Convention
slug: python-naming
kind: memory
status: draft
created: 2026-03-02
updated: 2026-03-02
memory_type: pattern
confidence: medium
tags: [python, naming]
scope:
  languages: [py]
---

Use snake_case for everything except class names.
"""

ARCHIVED_MEM = """\
---
id: mem.concept.old-guideline
name: Old Guideline
slug: old-guideline
kind: memory
status: archived
created: 2025-01-01
updated: 2025-06-01
memory_type: concept
---

This is no longer relevant.
"""


def _setup_repo(tmpdir: str, files: dict[str, str] | None = None) -> Path:
  """Set up a test repo with .git marker and optional memory files.

  Args:
    tmpdir: Temporary directory path.
    files: Mapping of filename to content for memory/ directory.

  Returns:
    Root path of the test repo.
  """
  root = Path(tmpdir)
  (root / ".git").mkdir()
  if files:
    mem_dir = root / MEMORY_DIR
    mem_dir.mkdir()
    for name, content in files.items():
      (mem_dir / name).write_text(content, encoding="utf-8")
  return root


class TestMemoryRegistry(unittest.TestCase):
  """Test MemoryRegistry discovery, parsing, and filtering."""

  def test_init_default_directory(self) -> None:
    """Registry defaults to memory/ under repo root."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(tmpdir)
      registry = MemoryRegistry(root=root)
      self.assertEqual(registry.directory, root / MEMORY_DIR)

  def test_collect_empty_directory(self) -> None:
    """collect returns empty dict when no memory directory exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(tmpdir)
      registry = MemoryRegistry(root=root)
      records = registry.collect()
      self.assertEqual(records, {})

  def test_collect_empty_directory_exists(self) -> None:
    """collect returns empty dict when memory dir has no mem.* files."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(tmpdir, files={})
      (root / MEMORY_DIR).mkdir(exist_ok=True)
      (root / MEMORY_DIR / "README.md").write_text(
        "# Memory\n",
        encoding="utf-8",
      )
      registry = MemoryRegistry(root=root)
      records = registry.collect()
      self.assertEqual(records, {})

  def test_collect_discovers_mem_files(self) -> None:
    """collect finds mem.*.md files and parses them."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(
        tmpdir,
        files={
          "mem.fact.test.md": MINIMAL_MEM,
          "mem.signpost.auth.prereading.md": FULL_MEM,
        },
      )
      registry = MemoryRegistry(root=root)
      records = registry.collect()

      self.assertEqual(len(records), 2)
      self.assertIn("mem.fact.test", records)
      self.assertIn("mem.signpost.auth.prereading", records)

  def test_collect_parses_minimal_correctly(self) -> None:
    """collect parses minimal memory file fields."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(
        tmpdir,
        files={
          "mem.fact.test.md": MINIMAL_MEM,
        },
      )
      registry = MemoryRegistry(root=root)
      records = registry.collect()
      rec = records["mem.fact.test"]

      self.assertEqual(rec.name, "Test Fact")
      self.assertEqual(rec.status, "active")
      self.assertEqual(rec.memory_type, "fact")
      self.assertEqual(rec.created, date(2026, 3, 1))

  def test_collect_parses_full_correctly(self) -> None:
    """collect parses full memory file with all fields."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(
        tmpdir,
        files={
          "mem.signpost.auth.prereading.md": FULL_MEM,
        },
      )
      registry = MemoryRegistry(root=root)
      records = registry.collect()
      rec = records["mem.signpost.auth.prereading"]

      self.assertEqual(rec.memory_type, "signpost")
      self.assertEqual(rec.confidence, "high")
      self.assertEqual(rec.verified, date(2026, 3, 1))
      self.assertEqual(rec.review_by, date(2026, 5, 1))
      self.assertEqual(rec.tags, ["auth", "pre-read"])
      self.assertEqual(
        rec.requires_reading,
        ["specify/decisions/ADR-011-auth-flow.md"],
      )
      self.assertEqual(rec.scope["globs"], ["src/auth/**"])
      self.assertEqual(rec.priority["severity"], "high")
      self.assertEqual(rec.audience, ["human", "agent"])
      self.assertEqual(rec.visibility, ["pre"])

  def test_collect_ignores_non_mem_files(self) -> None:
    """collect skips files that don't match mem.*.md pattern."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(
        tmpdir,
        files={
          "mem.fact.test.md": MINIMAL_MEM,
          "README.md": "# Not a memory\n",
          "ADR-001-decision.md": "---\nid: ADR-001\n---\n",
        },
      )
      registry = MemoryRegistry(root=root)
      records = registry.collect()
      self.assertEqual(len(records), 1)
      self.assertIn("mem.fact.test", records)

  def test_collect_skips_malformed_files(self) -> None:
    """collect skips files with missing/broken frontmatter."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(
        tmpdir,
        files={
          "mem.fact.test.md": MINIMAL_MEM,
          "mem.bad.nofront.md": "No frontmatter here\n",
        },
      )
      registry = MemoryRegistry(root=root)
      records = registry.collect()
      self.assertEqual(len(records), 1)
      self.assertIn("mem.fact.test", records)

  def test_collect_uses_frontmatter_id_over_filename(self) -> None:
    """Frontmatter id takes precedence over filename stem."""
    content = """\
---
id: mem.fact.override
name: Override Test
kind: memory
status: active
memory_type: fact
---
"""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(
        tmpdir,
        files={
          "mem.fact.something-else.md": content,
        },
      )
      registry = MemoryRegistry(root=root)
      records = registry.collect()
      self.assertIn("mem.fact.override", records)

  def test_collect_falls_back_to_filename_stem(self) -> None:
    """When frontmatter has no id, filename stem is used."""
    content = """\
---
name: No ID
kind: memory
status: active
memory_type: fact
---
"""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(
        tmpdir,
        files={
          "mem.fact.fallback.md": content,
        },
      )
      registry = MemoryRegistry(root=root)
      records = registry.collect()
      self.assertIn("mem.fact.fallback", records)

  def test_find_existing(self) -> None:
    """find returns the record for a known ID."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(
        tmpdir,
        files={
          "mem.fact.test.md": MINIMAL_MEM,
          "mem.signpost.auth.prereading.md": FULL_MEM,
        },
      )
      registry = MemoryRegistry(root=root)
      rec = registry.find("mem.signpost.auth.prereading")
      self.assertIsNotNone(rec)
      assert rec is not None
      self.assertEqual(rec.name, "Auth Pre-Reading")

  def test_find_missing(self) -> None:
    """find returns None for unknown ID."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(
        tmpdir,
        files={
          "mem.fact.test.md": MINIMAL_MEM,
        },
      )
      registry = MemoryRegistry(root=root)
      self.assertIsNone(registry.find("mem.fact.missing"))

  def test_iter_all(self) -> None:
    """iter without filters yields all records."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(
        tmpdir,
        files={
          "mem.fact.test.md": MINIMAL_MEM,
          "mem.signpost.auth.prereading.md": FULL_MEM,
          "mem.pattern.python.naming.md": PATTERN_MEM,
        },
      )
      registry = MemoryRegistry(root=root)
      all_records = list(registry.iter())
      self.assertEqual(len(all_records), 3)

  def test_iter_by_status(self) -> None:
    """iter with status filter yields only matching records."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(
        tmpdir,
        files={
          "mem.fact.test.md": MINIMAL_MEM,
          "mem.pattern.python.naming.md": PATTERN_MEM,
          "mem.concept.old-guideline.md": ARCHIVED_MEM,
        },
      )
      registry = MemoryRegistry(root=root)

      active = list(registry.iter(status="active"))
      self.assertEqual(len(active), 1)
      self.assertEqual(active[0].id, "mem.fact.test")

      drafts = list(registry.iter(status="draft"))
      self.assertEqual(len(drafts), 1)
      self.assertEqual(drafts[0].id, "mem.pattern.python.naming")

  def test_filter_by_memory_type(self) -> None:
    """filter by memory_type returns matching records."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(
        tmpdir,
        files={
          "mem.fact.test.md": MINIMAL_MEM,
          "mem.signpost.auth.prereading.md": FULL_MEM,
          "mem.pattern.python.naming.md": PATTERN_MEM,
        },
      )
      registry = MemoryRegistry(root=root)

      facts = registry.filter(memory_type="fact")
      self.assertEqual(len(facts), 1)
      self.assertEqual(facts[0].id, "mem.fact.test")

      signposts = registry.filter(memory_type="signpost")
      self.assertEqual(len(signposts), 1)
      self.assertEqual(
        signposts[0].id,
        "mem.signpost.auth.prereading",
      )

  def test_filter_by_tag(self) -> None:
    """filter by tag returns records containing that tag."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(
        tmpdir,
        files={
          "mem.fact.test.md": MINIMAL_MEM,
          "mem.signpost.auth.prereading.md": FULL_MEM,
          "mem.pattern.python.naming.md": PATTERN_MEM,
        },
      )
      registry = MemoryRegistry(root=root)

      auth_records = registry.filter(tag="auth")
      ids = {r.id for r in auth_records}
      self.assertEqual(ids, {"mem.signpost.auth.prereading"})

      python_records = registry.filter(tag="python")
      ids = {r.id for r in python_records}
      self.assertEqual(ids, {"mem.pattern.python.naming"})

  def test_filter_by_status(self) -> None:
    """filter by status returns matching records."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(
        tmpdir,
        files={
          "mem.fact.test.md": MINIMAL_MEM,
          "mem.concept.old-guideline.md": ARCHIVED_MEM,
        },
      )
      registry = MemoryRegistry(root=root)

      archived = registry.filter(status="archived")
      self.assertEqual(len(archived), 1)
      self.assertEqual(archived[0].id, "mem.concept.old-guideline")

  def test_filter_combined(self) -> None:
    """filter with multiple criteria ANDs them together."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(
        tmpdir,
        files={
          "mem.fact.test.md": MINIMAL_MEM,
          "mem.signpost.auth.prereading.md": FULL_MEM,
          "mem.pattern.python.naming.md": PATTERN_MEM,
        },
      )
      registry = MemoryRegistry(root=root)

      results = registry.filter(
        status="active",
        memory_type="signpost",
        tag="auth",
      )
      self.assertEqual(len(results), 1)
      self.assertEqual(
        results[0].id,
        "mem.signpost.auth.prereading",
      )

      results = registry.filter(
        status="active",
        memory_type="pattern",
      )
      self.assertEqual(len(results), 0)

  def test_filter_no_criteria(self) -> None:
    """filter with no criteria returns all records."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(
        tmpdir,
        files={
          "mem.fact.test.md": MINIMAL_MEM,
          "mem.signpost.auth.prereading.md": FULL_MEM,
        },
      )
      registry = MemoryRegistry(root=root)
      results = registry.filter()
      self.assertEqual(len(results), 2)

  def test_custom_directory(self) -> None:
    """Registry accepts a custom memory directory path."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(tmpdir)
      custom = root / SPECS_DIR / MEMORY_DIR
      custom.mkdir(parents=True)
      (custom / "mem.fact.test.md").write_text(
        MINIMAL_MEM,
        encoding="utf-8",
      )

      registry = MemoryRegistry(root=root, directory=custom)
      self.assertEqual(registry.directory, custom)
      records = registry.collect()
      self.assertEqual(len(records), 1)

  def test_collect_bodies_returns_body_text(self) -> None:
    """collect_bodies returns {id: body_text} for all memories."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(
        tmpdir,
        files={
          "mem.fact.test.md": MINIMAL_MEM,
          "mem.signpost.auth.prereading.md": FULL_MEM,
        },
      )
      registry = MemoryRegistry(root=root)
      bodies = registry.collect_bodies()

      self.assertEqual(len(bodies), 2)
      self.assertIn("mem.fact.test", bodies)
      self.assertIn("mem.signpost.auth.prereading", bodies)
      self.assertIn("A simple fact for testing.", bodies["mem.fact.test"])
      self.assertIn("Detailed body content", bodies["mem.signpost.auth.prereading"])

  def test_collect_bodies_empty_directory(self) -> None:
    """collect_bodies returns empty dict when no memories exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(tmpdir)
      registry = MemoryRegistry(root=root)
      self.assertEqual(registry.collect_bodies(), {})

  def test_collect_bodies_strips_frontmatter(self) -> None:
    """collect_bodies does not include frontmatter delimiters or content."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(
        tmpdir,
        files={"mem.fact.test.md": MINIMAL_MEM},
      )
      registry = MemoryRegistry(root=root)
      bodies = registry.collect_bodies()
      body = bodies["mem.fact.test"]
      self.assertNotIn("---", body)
      self.assertNotIn("id:", body)

  def test_to_dict_integration(self) -> None:
    """Records produced by collect serialize correctly via to_dict."""
    with tempfile.TemporaryDirectory() as tmpdir:
      root = _setup_repo(
        tmpdir,
        files={
          "mem.fact.test.md": MINIMAL_MEM,
        },
      )
      registry = MemoryRegistry(root=root)
      records = registry.collect()
      rec = records["mem.fact.test"]
      d = rec.to_dict(root)

      self.assertEqual(d["id"], "mem.fact.test")
      self.assertEqual(d["memory_type"], "fact")
      self.assertTrue(d["path"].startswith("memory/"))


if __name__ == "__main__":
  unittest.main()
