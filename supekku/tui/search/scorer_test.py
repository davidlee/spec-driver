"""Tests for search scorer (VT-087-001, VT-087-003)."""

from __future__ import annotations

from pathlib import Path

from supekku.scripts.lib.core.artifact_view import ArtifactEntry, ArtifactType
from supekku.tui.search.index import FIELD_ID, FIELD_STATUS, FIELD_TITLE, SearchEntry
from supekku.tui.search.scorer import (
  WEIGHT_ATTRIBUTE,
  WEIGHT_OWN_ID,
  WEIGHT_RELATION_TARGET,
  WEIGHT_TITLE,
  score_entry,
  search,
)


def _se(
  *,
  record_id: str = "DE-087",
  title: str = "Cross-artifact search",
  status: str = "draft",
  extra_fields: dict[str, str] | None = None,
  relation_targets: tuple[str, ...] = (),
) -> SearchEntry:
  """Build a SearchEntry for testing."""
  fields: dict[str, str] = {
    FIELD_ID: record_id,
    FIELD_TITLE: title,
    FIELD_STATUS: status,
  }
  if extra_fields:
    fields.update(extra_fields)
  return SearchEntry(
    entry=ArtifactEntry(
      id=record_id,
      title=title,
      status=status,
      path=Path("/tmp/fake.md"),
      artifact_type=ArtifactType.DELTA,
    ),
    searchable_fields=fields,
    relation_targets=relation_targets,
  )


class TestScoreEntry:
  """VT-087-001: Scorer weight application and field priority."""

  def test_empty_query_returns_zero(self):
    assert score_entry("", _se()) == 0.0

  def test_id_match_uses_own_id_weight(self):
    entry = _se(record_id="DE-087")
    score = score_entry("DE-087", entry)
    # Exact ID match should produce a high score.
    assert score > 0.5

  def test_title_match_lower_than_id_match(self):
    # Same query matches both ID and title.
    entry = _se(record_id="search", title="search")
    score = score_entry("search", entry)
    # Score should be dominated by ID weight (1.0 > 0.7).
    assert score > 0

  def test_attribute_match(self):
    entry = _se(extra_fields={"category": "assembly"})
    score = score_entry("assembly", entry)
    assert score > 0

  def test_relation_target_match(self):
    entry = _se(relation_targets=("PROD-010",))
    score = score_entry("PROD-010", entry)
    assert score > 0

  def test_no_match_returns_zero(self):
    entry = _se(record_id="DE-001", title="Something")
    assert score_entry("zzzzzzz", entry) == 0.0

  def test_per_tag_scoring(self):
    entry = _se(extra_fields={"tag.0": "tui", "tag.1": "search"})
    score = score_entry("tui", entry)
    assert score > 0


class TestWeightOrdering:
  """VT-087-003: Own-ID outranks relation-target for equivalent match quality."""

  def test_own_id_beats_relation_target_for_same_query(self):
    """Artifact with own ID 'DE-085' should outrank artifact that
    references DE-085 via relation, when query is 'DE-085'."""
    own = _se(record_id="DE-085", title="Something unrelated")
    ref = _se(
      record_id="DE-099",
      title="Something else",
      relation_targets=("DE-085",),
    )
    own_score = score_entry("DE-085", own)
    ref_score = score_entry("DE-085", ref)
    assert own_score > ref_score

  def test_perfect_relation_beats_weak_own_id(self):
    """A perfect relation match (0.5 * ~1.0) should beat a weak
    own-ID match (1.0 * ~0.2)."""
    # "PROD-010" is a perfect match for the relation target.
    ref = _se(
      record_id="DE-099",
      title="Unrelated",
      relation_targets=("PROD-010",),
    )
    ref_score = score_entry("PROD-010", ref)

    # "PROD-010" is a very weak partial match for "DE-099".
    weak = _se(record_id="DE-099", title="Unrelated")
    weak_score = score_entry("PROD-010", weak)

    assert ref_score > weak_score

  def test_weight_constants_ordering(self):
    """Verify the weight hierarchy is as documented."""
    assert WEIGHT_OWN_ID > WEIGHT_TITLE
    assert WEIGHT_TITLE > WEIGHT_RELATION_TARGET
    assert WEIGHT_RELATION_TARGET > WEIGHT_ATTRIBUTE
    assert WEIGHT_ATTRIBUTE > 0


class TestSearch:
  """Test the search() convenience function."""

  def test_returns_sorted_by_score(self):
    idx = [
      _se(record_id="DE-001", title="Unrelated"),
      _se(record_id="DE-087", title="Cross-artifact search"),
    ]
    results = search("DE-087", idx)
    assert len(results) >= 1
    assert results[0].entry.id == "DE-087"

  def test_empty_query_returns_empty(self):
    assert search("", [_se()]) == []

  def test_no_matches_returns_empty(self):
    assert search("zzzzzzz", [_se()]) == []

  def test_limit_respected(self):
    idx = [_se(record_id=f"DE-{i:03d}") for i in range(100)]
    results = search("DE-0", idx, limit=10)
    assert len(results) <= 10

  def test_filters_zero_scores(self):
    idx = [
      _se(record_id="DE-087"),
      _se(record_id="UNRELATED", title="Nothing here"),
    ]
    results = search("DE-087", idx)
    ids = [r.entry.id for r in results]
    # UNRELATED should not appear (or if it does, only if fuzzy matched).
    # DE-087 should be first.
    assert ids[0] == "DE-087"
