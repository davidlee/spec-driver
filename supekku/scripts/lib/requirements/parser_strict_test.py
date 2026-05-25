"""Tests for strict-mode parser behavior (DE-140 P05).

Covers VT-140-021, VT-140-023, VT-140-024.
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


def _malformed_block_body(spec_id: str = "SPEC-100") -> str:
  return textwrap.dedent(f"""\
    # {spec_id}

    ```yaml {REQUIREMENTS_MARKER}
    schema: [
      broken yaml
    ```

    ## Requirements

    - **FR-001**: Prose fallback requirement
  """)


# ---------------------------------------------------------------------------
# VT-140-021: Post-flip — no block yields zero records, no regex fallback
# ---------------------------------------------------------------------------


class TestPostFlipNoBlock:
  """VT-140-021: strict mode, no block → zero records."""

  def test_strict_no_block_yields_zero_records(self) -> None:
    root = _make_repo()
    body = _prose_body()
    path = _write_spec(root, "SPEC-100", body)

    records = list(
      records_from_spec("SPEC-100", {}, body, path, root, strict=True)
    )
    assert len(records) == 0

  def test_strict_no_block_does_not_fall_back_to_regex(self) -> None:
    """Prose requirements exist but strict mode ignores them."""
    root = _make_repo()
    body = _prose_body()
    path = _write_spec(root, "SPEC-100", body)

    records = list(
      records_from_spec("SPEC-100", {}, body, path, root, strict=True)
    )
    assert len(records) == 0

  def test_non_strict_no_block_falls_back(self) -> None:
    """Confirm non-strict still produces regex records (baseline)."""
    root = _make_repo()
    body = _prose_body()
    path = _write_spec(root, "SPEC-100", body)

    records = list(
      records_from_spec("SPEC-100", {}, body, path, root, strict=False)
    )
    assert len(records) == 2
    assert records[0].source_kind == "prose"

  def test_strict_with_block_still_works(self) -> None:
    """Strict mode with valid block produces normal records."""
    root = _make_repo()
    body = _block_body()
    path = _write_spec(root, "SPEC-100", body)

    records = list(
      records_from_spec("SPEC-100", {}, body, path, root, strict=True)
    )
    assert len(records) == 1
    assert records[0].uid == "SPEC-100.FR-001"
    assert records[0].source_kind == "block"


# ---------------------------------------------------------------------------
# VT-140-023: Pre-flip extraction failure → regex fallback
# ---------------------------------------------------------------------------


class TestPreFlipExtractionFailure:
  """VT-140-023: tolerant mode, extraction failure → regex fallback."""

  def test_malformed_block_falls_back_to_regex(self) -> None:
    root = _make_repo()
    body = _malformed_block_body()
    path = _write_spec(root, "SPEC-100", body)
    stats = SyncStats()

    records = list(
      records_from_spec(
        "SPEC-100", {}, body, path, root, stats=stats, strict=False,
      )
    )
    assert len(records) >= 1
    assert records[0].source_kind == "prose"
    assert stats.warnings >= 1

  def test_default_strict_is_false(self) -> None:
    """Default behavior (no strict kwarg) falls back on extraction failure."""
    root = _make_repo()
    body = _malformed_block_body()
    path = _write_spec(root, "SPEC-100", body)

    records = list(
      records_from_spec("SPEC-100", {}, body, path, root)
    )
    assert len(records) >= 1


# ---------------------------------------------------------------------------
# VT-140-024: Post-flip extraction failure → error, no fallback
# ---------------------------------------------------------------------------


class TestPostFlipExtractionFailure:
  """VT-140-024: strict mode, extraction failure → zero records."""

  def test_malformed_block_strict_yields_zero_records(self) -> None:
    root = _make_repo()
    body = _malformed_block_body()
    path = _write_spec(root, "SPEC-100", body)
    stats = SyncStats()

    records = list(
      records_from_spec(
        "SPEC-100", {}, body, path, root, stats=stats, strict=True,
      )
    )
    assert len(records) == 0

  def test_malformed_block_strict_increments_stats(self) -> None:
    root = _make_repo()
    body = _malformed_block_body()
    path = _write_spec(root, "SPEC-100", body)
    stats = SyncStats()

    list(
      records_from_spec(
        "SPEC-100", {}, body, path, root, stats=stats, strict=True,
      )
    )
    assert stats.warnings >= 1
