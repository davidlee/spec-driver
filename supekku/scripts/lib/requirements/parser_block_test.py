"""Tests for block-first reading pipeline in parser.

Covers VT-140-009 through VT-140-014, VT-140-025, VT-140-026.
"""

from __future__ import annotations

import tempfile
import textwrap
from pathlib import Path

from supekku.scripts.lib.blocks.spec_requirements import REQUIREMENTS_MARKER
from supekku.scripts.lib.requirements.models import SyncStats
from supekku.scripts.lib.requirements.parser import records_from_spec


def _make_repo() -> Path:
  root = Path(tempfile.mkdtemp())
  (root / ".git").mkdir()
  return root


def _write_spec(
  root: Path,
  spec_id: str,
  body: str,
  *,
  subdir: str = "specs/tech",
) -> Path:
  spec_dir = root / ".spec-driver" / subdir / spec_id.lower()
  spec_dir.mkdir(parents=True, exist_ok=True)
  path = spec_dir / f"{spec_id}.md"
  content = textwrap.dedent(f"""\
    ---
    id: {spec_id}
    status: draft
    kind: spec
    ---

    {body}
  """)
  path.write_text(content)
  return path


def _block_body(spec_id: str = "SPEC-100") -> str:
  return textwrap.dedent(f"""\
    # {spec_id}

    ```yaml {REQUIREMENTS_MARKER}
    schema: supekku.spec.requirements
    version: 1
    spec: {spec_id}
    requirements:
      - id: FR-001
        title: Block requirement
        lifecycle: active
        kind: functional
        description: A block requirement.
        acceptance_criteria:
          - Works correctly
        tags: [block]
      - id: NF-001
        title: Performance req
        lifecycle: pending
        kind: non-functional
        description: Must be fast.
        acceptance_criteria:
          - Under 500ms
    ```

    ## More content
  """)


def _prose_body(spec_id: str = "SPEC-100") -> str:
  return textwrap.dedent(f"""\
    # {spec_id}

    ## Requirements

    - **FR-001**: Prose requirement
    - **NF-001**: Another prose req
  """)


# ---------------------------------------------------------------------------
# VT-140-009: Block-first — block present, regex not called
# ---------------------------------------------------------------------------


class TestBlockFirst:
  """VT-140-009: block present → records from block."""

  def test_block_path_used_when_block_present(self) -> None:
    root = _make_repo()
    body = _block_body()
    path = _write_spec(root, "SPEC-100", body)
    fm = {"id": "SPEC-100"}

    records = list(records_from_spec("SPEC-100", fm, body, path, root))
    assert len(records) == 2
    assert records[0].uid == "SPEC-100.FR-001"
    assert records[0].title == "Block requirement"
    assert records[0].source_kind == "block"

  def test_block_records_have_correct_status(self) -> None:
    root = _make_repo()
    body = _block_body()
    path = _write_spec(root, "SPEC-100", body)

    records = list(records_from_spec("SPEC-100", {}, body, path, root))
    assert records[0].status == "active"
    assert records[1].status == "pending"


# ---------------------------------------------------------------------------
# VT-140-010: Regex fallback — no block, records from regex
# ---------------------------------------------------------------------------


class TestRegexFallback:
  """VT-140-010: no block → regex path."""

  def test_regex_path_when_no_block(self) -> None:
    root = _make_repo()
    body = _prose_body()
    path = _write_spec(root, "SPEC-100", body)

    records = list(records_from_spec("SPEC-100", {}, body, path, root))
    assert len(records) == 2
    assert records[0].uid == "SPEC-100.FR-001"
    assert records[0].title == "Prose requirement"
    assert records[0].source_kind == "prose"


# ---------------------------------------------------------------------------
# VT-140-011: Mutual exclusion — never both for same spec
# ---------------------------------------------------------------------------


class TestMutualExclusion:
  """VT-140-011: block and regex never both for same spec."""

  def test_block_present_ignores_prose_requirements(self) -> None:
    """Spec with both block and prose — only block records emitted."""
    root = _make_repo()
    body = textwrap.dedent(f"""\
      # SPEC-100

      ```yaml {REQUIREMENTS_MARKER}
      schema: supekku.spec.requirements
      version: 1
      spec: SPEC-100
      requirements:
        - id: FR-001
          title: Block version
          lifecycle: active
          kind: functional
          description: From block.
          acceptance_criteria:
            - AC1
      ```

      ## Requirements

      - **FR-002**: Prose version that should be ignored
    """)
    path = _write_spec(root, "SPEC-100", body)

    records = list(records_from_spec("SPEC-100", {}, body, path, root))
    assert len(records) == 1
    assert records[0].uid == "SPEC-100.FR-001"
    assert records[0].source_kind == "block"


# ---------------------------------------------------------------------------
# VT-140-012: RequirementRecord field mapping
# ---------------------------------------------------------------------------


class TestFieldMapping:
  """VT-140-012: lifecycle→status, kind canonicalized, UID derived."""

  def test_lifecycle_maps_to_status(self) -> None:
    root = _make_repo()
    body = _block_body()
    path = _write_spec(root, "SPEC-100", body)

    records = list(records_from_spec("SPEC-100", {}, body, path, root))
    fr = records[0]
    assert fr.status == "active"

  def test_uid_derived_from_spec_and_id(self) -> None:
    root = _make_repo()
    body = _block_body("PROD-004")
    path = _write_spec(root, "PROD-004", body, subdir="product")

    records = list(records_from_spec("PROD-004", {}, body, path, root))
    assert records[0].uid == "PROD-004.FR-001"
    assert records[0].label == "FR-001"

  def test_kind_canonicalized(self) -> None:
    root = _make_repo()
    body = _block_body()
    path = _write_spec(root, "SPEC-100", body)

    records = list(records_from_spec("SPEC-100", {}, body, path, root))
    assert records[0].kind == "functional"
    assert records[1].kind == "non-functional"

  def test_category_from_block(self) -> None:
    root = _make_repo()
    body = textwrap.dedent(f"""\
      ```yaml {REQUIREMENTS_MARKER}
      schema: supekku.spec.requirements
      version: 1
      spec: SPEC-100
      requirements:
        - id: FR-001
          title: Categorized
          lifecycle: active
          kind: functional
          category: core
          description: Has category.
          acceptance_criteria:
            - AC
      ```
    """)
    path = _write_spec(root, "SPEC-100", body)

    records = list(records_from_spec("SPEC-100", {}, body, path, root))
    assert records[0].category == "core"

  def test_tags_from_block(self) -> None:
    root = _make_repo()
    body = _block_body()
    path = _write_spec(root, "SPEC-100", body)

    records = list(records_from_spec("SPEC-100", {}, body, path, root))
    assert "block" in records[0].tags


# ---------------------------------------------------------------------------
# VT-140-013: Breakout metadata merge for both sources
# ---------------------------------------------------------------------------


class TestBreakoutMerge:
  """VT-140-013: breakout metadata merges for both block and prose."""

  def _write_breakout(self, spec_path: Path, req_id: str, ext_id: str) -> None:
    req_dir = spec_path.parent / "requirements"
    req_dir.mkdir(parents=True, exist_ok=True)
    content = textwrap.dedent(f"""\
      ---
      id: {req_id}
      ext_id: {ext_id}
      tags: [external]
      ---

      # {req_id}
    """)
    slug = req_id.replace(".", "-").lower()
    (req_dir / f"{slug}.md").write_text(content)

  def test_breakout_merges_with_block_source(self) -> None:
    root = _make_repo()
    body = _block_body()
    path = _write_spec(root, "SPEC-100", body)
    self._write_breakout(path, "SPEC-100.FR-001", "EXT-42")

    records = list(records_from_spec("SPEC-100", {}, body, path, root))
    fr = next(r for r in records if r.uid == "SPEC-100.FR-001")
    assert fr.ext_id == "EXT-42"
    assert "external" in fr.tags
    assert "block" in fr.tags

  def test_breakout_merges_with_prose_source(self) -> None:
    root = _make_repo()
    body = _prose_body()
    path = _write_spec(root, "SPEC-100", body)
    self._write_breakout(path, "SPEC-100.FR-001", "EXT-99")

    records = list(records_from_spec("SPEC-100", {}, body, path, root))
    fr = next(r for r in records if r.uid == "SPEC-100.FR-001")
    assert fr.ext_id == "EXT-99"
    assert "external" in fr.tags


# ---------------------------------------------------------------------------
# VT-140-014: source_kind tracking — block vs prose
# ---------------------------------------------------------------------------


class TestSourceKindTracking:
  """VT-140-014: source_kind set correctly per path."""

  def test_block_source_kind(self) -> None:
    root = _make_repo()
    body = _block_body()
    path = _write_spec(root, "SPEC-100", body)

    records = list(records_from_spec("SPEC-100", {}, body, path, root))
    for r in records:
      assert r.source_kind == "block"
      assert r.source_type == "spec"

  def test_prose_source_kind(self) -> None:
    root = _make_repo()
    body = _prose_body()
    path = _write_spec(root, "SPEC-100", body)

    records = list(records_from_spec("SPEC-100", {}, body, path, root))
    for r in records:
      assert r.source_kind == "prose"
      assert r.source_type == "spec"


# ---------------------------------------------------------------------------
# VT-140-025: Orphaned breakout files tolerated
# ---------------------------------------------------------------------------


class TestOrphanedBreakout:
  """VT-140-025: breakout files for missing requirements tolerated."""

  def test_orphaned_breakout_does_not_create_record(self) -> None:
    root = _make_repo()
    body = _block_body()
    path = _write_spec(root, "SPEC-100", body)

    req_dir = path.parent / "requirements"
    req_dir.mkdir(parents=True, exist_ok=True)
    orphan = textwrap.dedent("""\
      ---
      id: SPEC-100.FR-999
      ext_id: ORPHAN
      ---

      # FR-999 (not in block)
    """)
    (req_dir / "fr-999.md").write_text(orphan)

    records = list(records_from_spec("SPEC-100", {}, body, path, root))
    uids = {r.uid for r in records}
    assert "SPEC-100.FR-999" not in uids
    assert len(records) == 2


# ---------------------------------------------------------------------------
# VT-140-026: Block-only fields absent from registry
# ---------------------------------------------------------------------------


class TestBlockOnlyFields:
  """VT-140-026: description/acceptance_criteria not on record."""

  def test_no_description_on_record(self) -> None:
    root = _make_repo()
    body = _block_body()
    path = _write_spec(root, "SPEC-100", body)

    records = list(records_from_spec("SPEC-100", {}, body, path, root))
    fr = records[0]
    assert not hasattr(fr, "description")
    assert not hasattr(fr, "acceptance_criteria")
    serialized = fr.to_dict()
    assert "description" not in serialized
    assert "acceptance_criteria" not in serialized


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
  """Extraction failure and stats tracking."""

  def test_malformed_block_falls_back_to_regex(self) -> None:
    root = _make_repo()
    body = textwrap.dedent(f"""\
      # SPEC-100

      ```yaml {REQUIREMENTS_MARKER}
      invalid: yaml: :
      ```

      ## Requirements

      - **FR-001**: Fallback requirement
    """)
    path = _write_spec(root, "SPEC-100", body)
    stats = SyncStats()

    records = list(records_from_spec("SPEC-100", {}, body, path, root, stats=stats))
    assert len(records) == 1
    assert records[0].uid == "SPEC-100.FR-001"
    assert records[0].source_kind == "prose"
    assert stats.warnings >= 1

  def test_empty_requirements_block_yields_nothing(self) -> None:
    root = _make_repo()
    body = textwrap.dedent(f"""\
      ```yaml {REQUIREMENTS_MARKER}
      schema: supekku.spec.requirements
      version: 1
      spec: SPEC-100
      requirements: []
      ```
    """)
    path = _write_spec(root, "SPEC-100", body)

    records = list(records_from_spec("SPEC-100", {}, body, path, root))
    assert records == []

  def test_stats_tracks_validation_warnings(self) -> None:
    root = _make_repo()
    body = textwrap.dedent(f"""\
      ```yaml {REQUIREMENTS_MARKER}
      schema: supekku.spec.requirements
      version: 1
      spec: SPEC-100
      requirements:
        - id: FR-001
          title: Test
          lifecycle: active
          kind: functional
          description: D
          acceptance_criteria:
            - AC
        - id: FR-001
          title: Duplicate
          lifecycle: pending
          kind: functional
          description: D
          acceptance_criteria:
            - AC
      ```
    """)
    path = _write_spec(root, "SPEC-100", body)
    stats = SyncStats()

    list(records_from_spec("SPEC-100", {}, body, path, root, stats=stats))
    assert stats.warnings >= 1

  def test_tolerated_kind_alias_canonicalized(self) -> None:
    root = _make_repo()
    body = textwrap.dedent(f"""\
      ```yaml {REQUIREMENTS_MARKER}
      schema: supekku.spec.requirements
      version: 1
      spec: SPEC-100
      requirements:
        - id: FR-001
          title: Alias test
          lifecycle: pending
          kind: FR
          description: Uses alias.
          acceptance_criteria:
            - AC
      ```
    """)
    path = _write_spec(root, "SPEC-100", body)

    records = list(records_from_spec("SPEC-100", {}, body, path, root))
    assert records[0].kind == "functional"
