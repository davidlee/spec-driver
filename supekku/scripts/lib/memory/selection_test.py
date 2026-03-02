"""Tests for memory selection — scope matching, specificity, and path normalization."""

from __future__ import annotations

import unittest
from datetime import date
from pathlib import Path

from supekku.scripts.lib.memory.models import MemoryRecord
from supekku.scripts.lib.memory.selection import (
  MatchContext,
  is_surfaceable,
  matches_scope,
  normalize_path,
  scope_specificity,
  select,
  sort_key,
)


def _record(
  *,
  record_id: str = "mem.fact.alpha",
  scope: dict | None = None,
  tags: list[str] | None = None,
  **kwargs,
) -> MemoryRecord:
  """Build a MemoryRecord with defaults for testing."""
  return MemoryRecord(
    id=record_id,
    name=kwargs.get("name", "Test"),
    status=kwargs.get("status", "active"),
    memory_type=kwargs.get("memory_type", "fact"),
    path=kwargs.get("path", ""),
    scope=scope or {},
    tags=tags or [],
    priority=kwargs.get("priority", {}),
    verified=kwargs.get("verified"),
    created=kwargs.get("created"),
    updated=kwargs.get("updated"),
  )


# -- normalize_path -----------------------------------------------------------


class TestNormalizePath(unittest.TestCase):
  """Path normalization to repo-relative POSIX form."""

  def test_already_relative(self) -> None:
    self.assertEqual(
      normalize_path("src/auth/cache.ts"),
      "src/auth/cache.ts",
    )

  def test_strips_leading_dot_slash(self) -> None:
    self.assertEqual(normalize_path("./src/foo.py"), "src/foo.py")

  def test_resolves_parent_refs(self) -> None:
    self.assertEqual(
      normalize_path("src/auth/../common/utils.py"),
      "src/common/utils.py",
    )

  def test_preserves_trailing_slash(self) -> None:
    self.assertEqual(normalize_path("src/auth/"), "src/auth/")

  def test_strips_leading_slash_relative_to_repo(self) -> None:
    self.assertEqual(
      normalize_path(
        "/home/user/repo/src/foo.py",
        repo_root=Path("/home/user/repo"),
      ),
      "src/foo.py",
    )

  def test_no_double_slashes(self) -> None:
    self.assertEqual(
      normalize_path("src//auth//cache.ts"),
      "src/auth/cache.ts",
    )

  def test_dot_only(self) -> None:
    self.assertEqual(normalize_path("."), ".")

  def test_empty_string(self) -> None:
    self.assertEqual(normalize_path(""), ".")


# -- matches_scope: path exact ------------------------------------------------


class TestMatchesScopePathExact(unittest.TestCase):
  """Scope matching via scope.paths (exact and prefix)."""

  def test_exact_match(self) -> None:
    rec = _record(scope={"paths": ["src/auth/cache.ts"]})
    ctx = MatchContext(paths=["src/auth/cache.ts"])
    self.assertTrue(matches_scope(rec, ctx))

  def test_no_match(self) -> None:
    rec = _record(scope={"paths": ["src/auth/cache.ts"]})
    ctx = MatchContext(paths=["src/other/file.ts"])
    self.assertFalse(matches_scope(rec, ctx))

  def test_prefix_match_trailing_slash(self) -> None:
    """scope.paths entry with trailing / matches files under that dir."""
    rec = _record(scope={"paths": ["src/auth/"]})
    ctx = MatchContext(paths=["src/auth/cache.ts"])
    self.assertTrue(matches_scope(rec, ctx))

  def test_prefix_no_match_partial_dirname(self) -> None:
    """'src/auth/' should NOT match 'src/authorization/x.ts'."""
    rec = _record(scope={"paths": ["src/auth/"]})
    ctx = MatchContext(paths=["src/authorization/x.ts"])
    self.assertFalse(matches_scope(rec, ctx))

  def test_multiple_scope_paths(self) -> None:
    rec = _record(scope={"paths": ["src/a.py", "src/b.py"]})
    ctx = MatchContext(paths=["src/b.py"])
    self.assertTrue(matches_scope(rec, ctx))

  def test_multiple_context_paths(self) -> None:
    rec = _record(scope={"paths": ["src/a.py"]})
    ctx = MatchContext(paths=["src/x.py", "src/a.py"])
    self.assertTrue(matches_scope(rec, ctx))


# -- matches_scope: globs -----------------------------------------------------


class TestMatchesScopeGlobs(unittest.TestCase):
  """Scope matching via scope.globs with proper ** support."""

  def test_star_glob(self) -> None:
    rec = _record(scope={"globs": ["src/auth/*.ts"]})
    ctx = MatchContext(paths=["src/auth/cache.ts"])
    self.assertTrue(matches_scope(rec, ctx))

  def test_doublestar_glob(self) -> None:
    rec = _record(scope={"globs": ["src/**"]})
    ctx = MatchContext(paths=["src/auth/deep/file.ts"])
    self.assertTrue(matches_scope(rec, ctx))

  def test_doublestar_universal(self) -> None:
    """scope.globs: ['**'] matches everything."""
    rec = _record(scope={"globs": ["**"]})
    ctx = MatchContext(paths=["any/path/at/all.txt"])
    self.assertTrue(matches_scope(rec, ctx))

  def test_no_glob_match(self) -> None:
    rec = _record(scope={"globs": ["src/auth/*.ts"]})
    ctx = MatchContext(paths=["src/other/file.ts"])
    self.assertFalse(matches_scope(rec, ctx))

  def test_glob_does_not_match_without_context_paths(self) -> None:
    rec = _record(scope={"globs": ["src/**"]})
    ctx = MatchContext(paths=[])
    self.assertFalse(matches_scope(rec, ctx))


# -- matches_scope: commands ---------------------------------------------------


class TestMatchesScopeCommands(unittest.TestCase):
  """Scope matching via scope.commands using token-prefix."""

  def test_single_token_match(self) -> None:
    rec = _record(scope={"commands": ["test"]})
    ctx = MatchContext(command="test auth --verbose")
    self.assertTrue(matches_scope(rec, ctx))

  def test_two_token_prefix_match(self) -> None:
    rec = _record(scope={"commands": ["make lint"]})
    ctx = MatchContext(command="make lint --fix")
    self.assertTrue(matches_scope(rec, ctx))

  def test_no_substring_false_positive(self) -> None:
    """'test' should NOT match 'pytest'."""
    rec = _record(scope={"commands": ["test"]})
    ctx = MatchContext(command="pytest supekku")
    self.assertFalse(matches_scope(rec, ctx))

  def test_no_substring_false_positive_build(self) -> None:
    """'build' should NOT match 'rebuild'."""
    rec = _record(scope={"commands": ["build"]})
    ctx = MatchContext(command="rebuild all")
    self.assertFalse(matches_scope(rec, ctx))

  def test_exact_command_match(self) -> None:
    rec = _record(scope={"commands": ["pytest"]})
    ctx = MatchContext(command="pytest")
    self.assertTrue(matches_scope(rec, ctx))

  def test_no_match_different_command(self) -> None:
    rec = _record(scope={"commands": ["test"]})
    ctx = MatchContext(command="build all")
    self.assertFalse(matches_scope(rec, ctx))

  def test_no_match_without_context_command(self) -> None:
    rec = _record(scope={"commands": ["test"]})
    ctx = MatchContext(command=None)
    self.assertFalse(matches_scope(rec, ctx))

  def test_multiple_scope_commands(self) -> None:
    rec = _record(scope={"commands": ["test", "lint"]})
    ctx = MatchContext(command="lint --fix")
    self.assertTrue(matches_scope(rec, ctx))


# -- matches_scope: tags -------------------------------------------------------


class TestMatchesScopeTags(unittest.TestCase):
  """Scope matching via tag intersection."""

  def test_tag_match(self) -> None:
    rec = _record(tags=["auth", "security"])
    ctx = MatchContext(tags=["auth"])
    self.assertTrue(matches_scope(rec, ctx))

  def test_no_tag_match(self) -> None:
    rec = _record(tags=["auth"])
    ctx = MatchContext(tags=["database"])
    self.assertFalse(matches_scope(rec, ctx))

  def test_empty_context_tags_no_match(self) -> None:
    """Empty context.tags should not match even if record has tags."""
    rec = _record(tags=["auth"])
    ctx = MatchContext(tags=[])
    self.assertFalse(matches_scope(rec, ctx))

  def test_empty_record_tags_no_match(self) -> None:
    rec = _record(tags=[])
    ctx = MatchContext(tags=["auth"])
    self.assertFalse(matches_scope(rec, ctx))


# -- matches_scope: OR composition --------------------------------------------


class TestMatchesScopeComposition(unittest.TestCase):
  """OR logic across match dimensions."""

  def test_path_match_suffices(self) -> None:
    rec = _record(scope={"paths": ["src/a.py"]}, tags=["unrelated"])
    ctx = MatchContext(paths=["src/a.py"], tags=["other"])
    self.assertTrue(matches_scope(rec, ctx))

  def test_tag_match_suffices(self) -> None:
    rec = _record(scope={"paths": ["src/a.py"]}, tags=["auth"])
    ctx = MatchContext(paths=["src/other.py"], tags=["auth"])
    self.assertTrue(matches_scope(rec, ctx))

  def test_no_scope_no_tags_no_match(self) -> None:
    """Records with no scope and no tags never match via context."""
    rec = _record(scope={}, tags=[])
    ctx = MatchContext(paths=["src/a.py"], tags=["auth"])
    self.assertFalse(matches_scope(rec, ctx))

  def test_command_match_suffices(self) -> None:
    rec = _record(scope={"commands": ["test"]})
    ctx = MatchContext(command="test auth")
    self.assertTrue(matches_scope(rec, ctx))


# -- scope_specificity ---------------------------------------------------------


class TestScopeSpecificity(unittest.TestCase):
  """Specificity scoring: paths=3 > globs=2 > commands=1 > tags=0."""

  def test_path_exact_specificity(self) -> None:
    rec = _record(scope={"paths": ["src/a.py"]})
    ctx = MatchContext(paths=["src/a.py"])
    self.assertEqual(scope_specificity(rec, ctx), 3)

  def test_path_prefix_specificity(self) -> None:
    rec = _record(scope={"paths": ["src/auth/"]})
    ctx = MatchContext(paths=["src/auth/cache.ts"])
    self.assertEqual(scope_specificity(rec, ctx), 3)

  def test_glob_specificity(self) -> None:
    rec = _record(scope={"globs": ["src/**"]})
    ctx = MatchContext(paths=["src/auth/file.ts"])
    self.assertEqual(scope_specificity(rec, ctx), 2)

  def test_command_specificity(self) -> None:
    rec = _record(scope={"commands": ["test"]})
    ctx = MatchContext(command="test auth")
    self.assertEqual(scope_specificity(rec, ctx), 1)

  def test_tag_only_specificity(self) -> None:
    rec = _record(tags=["auth"])
    ctx = MatchContext(tags=["auth"])
    self.assertEqual(scope_specificity(rec, ctx), 0)

  def test_max_across_dimensions(self) -> None:
    """When multiple dimensions match, take the highest."""
    rec = _record(
      scope={"paths": ["src/a.py"], "commands": ["test"]},
      tags=["auth"],
    )
    ctx = MatchContext(
      paths=["src/a.py"],
      command="test auth",
      tags=["auth"],
    )
    self.assertEqual(scope_specificity(rec, ctx), 3)

  def test_no_context_specificity_zero(self) -> None:
    rec = _record(scope={"paths": ["src/a.py"]})
    ctx = MatchContext()
    self.assertEqual(scope_specificity(rec, ctx), 0)

  def test_no_match_specificity_zero(self) -> None:
    rec = _record(scope={"paths": ["src/a.py"]})
    ctx = MatchContext(paths=["src/other.py"])
    self.assertEqual(scope_specificity(rec, ctx), 0)


# -- sort_key ------------------------------------------------------------------


class TestSortKey(unittest.TestCase):
  """Deterministic sort key per JAMMS §5.4."""

  def test_severity_ordering(self) -> None:
    """critical < high < medium < low < none in sort order."""
    records = [
      _record(record_id="mem.thread.epsilon", priority={"severity": "none"}),
      _record(record_id="mem.fact.alpha", priority={"severity": "critical"}),
      _record(record_id="mem.fact.gamma", priority={"severity": "medium"}),
      _record(record_id="mem.fact.beta", priority={"severity": "high"}),
      _record(record_id="mem.concept.delta", priority={"severity": "low"}),
    ]
    sorted_recs = sorted(records, key=lambda r: sort_key(r))
    ids = [r.id for r in sorted_recs]
    self.assertEqual(
      ids,
      [
        "mem.fact.alpha",
        "mem.fact.beta",
        "mem.fact.gamma",
        "mem.concept.delta",
        "mem.thread.epsilon",
      ],
    )

  def test_weight_tiebreak_descending(self) -> None:
    """Higher weight sorts first within same severity."""
    records = [
      _record(
        record_id="mem.fact.alpha",
        priority={"severity": "high", "weight": 5},
      ),
      _record(
        record_id="mem.fact.beta",
        priority={"severity": "high", "weight": 10},
      ),
    ]
    sorted_recs = sorted(records, key=lambda r: sort_key(r))
    self.assertEqual(sorted_recs[0].id, "mem.fact.beta")

  def test_specificity_tiebreak(self) -> None:
    """Higher specificity sorts first within same severity/weight."""
    ctx = MatchContext(
      paths=["src/a.py"],
      command="test auth",
    )
    rec_path = _record(
      record_id="mem.fact.alpha",
      scope={"paths": ["src/a.py"]},
    )
    rec_cmd = _record(
      record_id="mem.fact.beta",
      scope={"commands": ["test"]},
    )
    sorted_recs = sorted(
      [rec_cmd, rec_path],
      key=lambda r: sort_key(r, ctx),
    )
    self.assertEqual(sorted_recs[0].id, "mem.fact.alpha")  # paths=3 > commands=1

  def test_verified_recency_tiebreak(self) -> None:
    """More recently verified sorts first; null last."""
    today = date(2026, 3, 2)
    rec_recent = _record(
      record_id="mem.fact.alpha",
      verified=date(2026, 3, 1),
    )
    rec_old = _record(
      record_id="mem.fact.beta",
      verified=date(2026, 1, 1),
    )
    rec_null = _record(record_id="mem.fact.gamma")
    sorted_recs = sorted(
      [rec_null, rec_old, rec_recent],
      key=lambda r: sort_key(r, today=today),
    )
    self.assertEqual(
      [r.id for r in sorted_recs],
      ["mem.fact.alpha", "mem.fact.beta", "mem.fact.gamma"],
    )

  def test_id_tiebreak(self) -> None:
    """Lexicographic ID as final tie-breaker."""
    records = [
      _record(record_id="mem.fact.gamma"),
      _record(record_id="mem.fact.alpha"),
      _record(record_id="mem.fact.beta"),
    ]
    sorted_recs = sorted(records, key=lambda r: sort_key(r))
    self.assertEqual(
      [r.id for r in sorted_recs],
      ["mem.fact.alpha", "mem.fact.beta", "mem.fact.gamma"],
    )

  def test_missing_severity_defaults_to_none(self) -> None:
    rec = _record(priority={})
    key = sort_key(rec)
    rec_none = _record(priority={"severity": "none"})
    self.assertEqual(key, sort_key(rec_none))

  def test_missing_weight_defaults_to_zero(self) -> None:
    rec = _record(priority={"severity": "high"})
    key = sort_key(rec)
    rec_zero = _record(priority={"severity": "high", "weight": 0})
    self.assertEqual(key, sort_key(rec_zero))

  def test_unknown_severity_treated_as_none(self) -> None:
    rec = _record(priority={"severity": "bogus"})
    key = sort_key(rec)
    rec_none = _record(priority={"severity": "none"})
    self.assertEqual(key[0], sort_key(rec_none)[0])

  def test_deterministic_across_runs(self) -> None:
    """Same input set always produces same sort order."""
    records = [
      _record(
        record_id="mem.fact.alpha",
        priority={"severity": "high", "weight": 5},
        verified=date(2026, 3, 1),
      ),
      _record(
        record_id="mem.fact.beta",
        priority={"severity": "high", "weight": 5},
        verified=date(2026, 2, 1),
      ),
      _record(
        record_id="mem.fact.gamma",
        priority={"severity": "critical"},
      ),
    ]
    today = date(2026, 3, 2)
    for _ in range(10):
      sorted_recs = sorted(
        records,
        key=lambda r: sort_key(r, today=today),
      )
      self.assertEqual(
        [r.id for r in sorted_recs],
        ["mem.fact.gamma", "mem.fact.alpha", "mem.fact.beta"],
      )


# -- is_surfaceable ------------------------------------------------------------


class TestIsSurfaceable(unittest.TestCase):
  """Status filtering and thread recency rules."""

  def test_active_is_surfaceable(self) -> None:
    rec = _record(status="active")
    self.assertTrue(is_surfaceable(rec))

  def test_deprecated_excluded(self) -> None:
    rec = _record(status="deprecated")
    self.assertFalse(is_surfaceable(rec))

  def test_superseded_excluded(self) -> None:
    rec = _record(status="superseded")
    self.assertFalse(is_surfaceable(rec))

  def test_obsolete_excluded(self) -> None:
    rec = _record(status="obsolete")
    self.assertFalse(is_surfaceable(rec))

  def test_draft_excluded_by_default(self) -> None:
    rec = _record(status="draft")
    self.assertFalse(is_surfaceable(rec))

  def test_draft_included_when_opted_in(self) -> None:
    rec = _record(status="draft")
    self.assertTrue(is_surfaceable(rec, include_draft=True))

  def test_thread_excluded_without_context(self) -> None:
    rec = _record(memory_type="thread", verified=date(2026, 3, 1))
    self.assertFalse(is_surfaceable(rec, today=date(2026, 3, 2)))

  def test_thread_included_with_matching_scope_and_recent(self) -> None:
    rec = _record(
      memory_type="thread",
      scope={"paths": ["src/a.py"]},
      verified=date(2026, 2, 20),
    )
    ctx = MatchContext(paths=["src/a.py"])
    self.assertTrue(
      is_surfaceable(rec, context=ctx, today=date(2026, 3, 2)),
    )

  def test_thread_excluded_when_scope_matches_but_stale(self) -> None:
    rec = _record(
      memory_type="thread",
      scope={"paths": ["src/a.py"]},
      verified=date(2025, 1, 1),
    )
    ctx = MatchContext(paths=["src/a.py"])
    self.assertFalse(
      is_surfaceable(
        rec,
        context=ctx,
        thread_recency_days=14,
        today=date(2026, 3, 2),
      ),
    )

  def test_thread_excluded_when_not_scope_matched(self) -> None:
    rec = _record(
      memory_type="thread",
      scope={"paths": ["src/a.py"]},
      verified=date(2026, 3, 1),
    )
    ctx = MatchContext(paths=["src/other.py"])
    self.assertFalse(
      is_surfaceable(rec, context=ctx, today=date(2026, 3, 2)),
    )

  def test_thread_excluded_when_no_verified_date(self) -> None:
    rec = _record(
      memory_type="thread",
      scope={"paths": ["src/a.py"]},
    )
    ctx = MatchContext(paths=["src/a.py"])
    self.assertFalse(
      is_surfaceable(rec, context=ctx, today=date(2026, 3, 2)),
    )

  def test_skip_status_filter_includes_deprecated(self) -> None:
    rec = _record(status="deprecated")
    self.assertTrue(is_surfaceable(rec, skip_status_filter=True))

  def test_skip_status_filter_includes_draft(self) -> None:
    rec = _record(status="draft")
    self.assertTrue(is_surfaceable(rec, skip_status_filter=True))

  def test_skip_status_filter_still_checks_threads(self) -> None:
    """Thread recency check applies even with skip_status_filter."""
    rec = _record(
      memory_type="thread",
      status="active",
      scope={"paths": ["src/a.py"]},
    )
    self.assertFalse(
      is_surfaceable(
        rec,
        skip_status_filter=True,
        today=date(2026, 3, 2),
      ),
    )


# -- select --------------------------------------------------------------------


class TestSelect(unittest.TestCase):
  """End-to-end selection pipeline."""

  def _make_records(self) -> list[MemoryRecord]:
    return [
      _record(
        record_id="mem.fact.alpha",
        status="active",
        memory_type="fact",
        priority={"severity": "high", "weight": 10},
        scope={"paths": ["src/auth/cache.ts"]},
        verified=date(2026, 3, 1),
      ),
      _record(
        record_id="mem.fact.beta",
        status="active",
        memory_type="signpost",
        priority={"severity": "critical"},
        scope={"globs": ["src/**"]},
        verified=date(2026, 2, 15),
      ),
      _record(
        record_id="mem.fact.gamma",
        status="deprecated",
        memory_type="fact",
      ),
      _record(
        record_id="mem.concept.delta",
        status="draft",
        memory_type="concept",
        scope={"globs": ["**"]},
      ),
      _record(
        record_id="mem.thread.epsilon",
        status="active",
        memory_type="thread",
        scope={"paths": ["src/auth/cache.ts"]},
        verified=date(2026, 3, 1),
      ),
      _record(
        record_id="mem.pattern.zeta",
        status="active",
        memory_type="pattern",
        tags=["auth"],
      ),
    ]

  def test_no_context_returns_non_excluded(self) -> None:
    """Without context, all non-excluded records returned."""
    records = self._make_records()
    result = select(records, today=date(2026, 3, 2))
    ids = [r.id for r in result]
    # gamma excluded (deprecated), delta (draft), epsilon (thread, no ctx)
    self.assertIn("mem.fact.alpha", ids)
    self.assertIn("mem.fact.beta", ids)
    self.assertIn("mem.pattern.zeta", ids)
    self.assertNotIn("mem.fact.gamma", ids)
    self.assertNotIn("mem.concept.delta", ids)
    self.assertNotIn("mem.thread.epsilon", ids)

  def test_context_filters_by_scope(self) -> None:
    """With context, only scope-matched records returned."""
    records = self._make_records()
    ctx = MatchContext(paths=["src/auth/cache.ts"])
    result = select(records, ctx, today=date(2026, 3, 2))
    ids = [r.id for r in result]
    self.assertIn("mem.fact.alpha", ids)  # path match
    self.assertIn("mem.fact.beta", ids)  # glob match
    self.assertIn("mem.thread.epsilon", ids)  # thread, scoped + recent
    self.assertNotIn("mem.pattern.zeta", ids)  # tags only, no --match-tag

  def test_ordering_is_deterministic(self) -> None:
    """Records sorted by severity > weight > specificity > verified."""
    records = self._make_records()
    ctx = MatchContext(paths=["src/auth/cache.ts"])
    result = select(records, ctx, today=date(2026, 3, 2))
    ids = [r.id for r in result]
    # beta: critical, glob(2)
    # alpha: high, weight=10, path(3)
    # epsilon: no severity(none), path(3), verified recent
    self.assertEqual(ids[0], "mem.fact.beta")  # critical first
    self.assertEqual(ids[1], "mem.fact.alpha")  # high second

  def test_include_draft(self) -> None:
    records = self._make_records()
    result = select(records, include_draft=True, today=date(2026, 3, 2))
    ids = [r.id for r in result]
    self.assertIn("mem.concept.delta", ids)

  def test_limit(self) -> None:
    records = self._make_records()
    result = select(records, limit=2, today=date(2026, 3, 2))
    self.assertEqual(len(result), 2)

  def test_empty_input(self) -> None:
    self.assertEqual(select([]), [])

  def test_determinism_multiple_runs(self) -> None:
    """Same input set produces identical output every run."""
    records = self._make_records()
    ctx = MatchContext(paths=["src/auth/cache.ts"])
    today = date(2026, 3, 2)
    first = [r.id for r in select(records, ctx, today=today)]
    for _ in range(10):
      result = [r.id for r in select(records, ctx, today=today)]
      self.assertEqual(result, first)


if __name__ == "__main__":
  unittest.main()
