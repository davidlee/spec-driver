"""VTs for the v0_10_0_003_prod_blocks migration step.

Covers:

- ``VT-DE139-MIG-002`` — scope→prose, fields cut, idempotence.
- Block emission from non-empty FM hypotheses/decisions.
- ``preview()`` writes nothing and surfaces drift.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from spec_driver.migrations.v0_10_0_003_prod_blocks import ProdBlocksStep, step
from spec_driver.migrations.v0_10_0_003_prod_blocks.migration import (
  DRIFT_DECISIONS_EMITTED,
  DRIFT_HYPOTHESES_EMITTED,
  DRIFT_SCOPE_MOVED,
  DRIFT_VERIFICATION_STRATEGY_CUT,
  _transform,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_prod(tmp_path: Path, name: str, contents: str) -> Path:
  path = tmp_path / name
  path.write_text(contents, encoding="utf-8")
  return path


def _drift_kinds(drift: list) -> set[str]:
  return {entry.kind for entry in drift}


def _parse_fm(text: str) -> dict:
  lines = text.split("\n")
  assert lines[0] == "---"
  end = lines.index("---", 1)
  return yaml.safe_load("\n".join(lines[1:end]))


# ---------------------------------------------------------------------------
# Module-level step export
# ---------------------------------------------------------------------------


def test_module_exports_step_instance() -> None:
  assert isinstance(step, ProdBlocksStep)
  assert step.applies_to_kind == "prod"


# ---------------------------------------------------------------------------
# applies_to()
# ---------------------------------------------------------------------------


class TestAppliesTo:
  def test_matches_scope(self, tmp_path: Path) -> None:
    p = _write_prod(
      tmp_path,
      "PROD-100.md",
      '---\nid: PROD-100\nkind: prod\nscope: "widgets"\n---\nbody\n',
    )
    assert ProdBlocksStep().applies_to(p)

  def test_matches_each_cut_key(self, tmp_path: Path) -> None:
    for key in ("hypotheses", "decisions", "verification_strategy", "scope"):
      p = _write_prod(
        tmp_path,
        f"PROD-{key}.md",
        f"---\nid: PROD-100\nkind: prod\n{key}: foo\n---\nbody\n",
      )
      assert ProdBlocksStep().applies_to(p), key

  def test_skips_clean_prod(self, tmp_path: Path) -> None:
    p = _write_prod(
      tmp_path,
      "PROD-100.md",
      "---\nid: PROD-100\nkind: prod\n---\nbody\n",
    )
    assert not ProdBlocksStep().applies_to(p)

  def test_skips_non_existent(self, tmp_path: Path) -> None:
    assert not ProdBlocksStep().applies_to(tmp_path / "nope.md")


# ---------------------------------------------------------------------------
# Scope → prose (VT-DE139-MIG-002 primary)
# ---------------------------------------------------------------------------


class TestScopeMoved:
  _PROD_WITH_SCOPE = (
    "---\n"
    "id: PROD-014\n"
    "slug: contract_mirror_tree_index\n"
    "name: Contract Mirror Tree Index\n"
    "kind: prod\n"
    'scope: "Provide a canonical contracts corpus."\n'
    "---\n"
    "\n"
    "# PROD-014 – Contract Mirror Tree Index\n"
    "\n"
    "## 1. Intent & Summary\n"
    "\nSome text.\n"
  )

  def test_scope_moved_to_body(self) -> None:
    result = _transform(self._PROD_WITH_SCOPE)
    assert result.changed
    fm = _parse_fm(result.text)
    assert "scope" not in fm
    assert "> **Scope**: Provide a canonical contracts corpus." in result.text
    assert DRIFT_SCOPE_MOVED in _drift_kinds(result.drift)

  def test_body_heading_preserved(self) -> None:
    result = _transform(self._PROD_WITH_SCOPE)
    assert "## 1. Intent & Summary" in result.text

  def test_idempotent(self) -> None:
    first = _transform(self._PROD_WITH_SCOPE)
    second = _transform(first.text)
    assert not second.changed

  def test_empty_scope_ignored(self) -> None:
    text = '---\nid: PROD-100\nkind: prod\nscope: ""\n---\nbody\n'
    result = _transform(text)
    assert "**Scope**" not in result.text


# ---------------------------------------------------------------------------
# Hypotheses block emission
# ---------------------------------------------------------------------------


class TestHypothesesBlock:
  def test_non_empty_hypotheses_emitted(self) -> None:
    text = (
      "---\nid: PROD-100\nkind: prod\n"
      "hypotheses:\n"
      "  - id: H-001\n"
      "    statement: caching helps\n"
      "    status: open\n"
      "---\nbody\n"
    )
    result = _transform(text)
    assert "supekku:spec.hypotheses@v1" in result.text
    assert DRIFT_HYPOTHESES_EMITTED in _drift_kinds(result.drift)
    fm = _parse_fm(result.text)
    assert "hypotheses" not in fm


# ---------------------------------------------------------------------------
# Decisions block emission
# ---------------------------------------------------------------------------


class TestDecisionsBlock:
  def test_non_empty_decisions_emitted(self) -> None:
    text = (
      "---\nid: PROD-100\nkind: prod\n"
      "decisions:\n"
      "  - id: DEC-001\n"
      "    summary: use blocks\n"
      "---\nbody\n"
    )
    result = _transform(text)
    assert "supekku:spec.decisions@v1" in result.text
    assert DRIFT_DECISIONS_EMITTED in _drift_kinds(result.drift)
    fm = _parse_fm(result.text)
    assert "decisions" not in fm


# ---------------------------------------------------------------------------
# Verification strategy cut
# ---------------------------------------------------------------------------


class TestVerificationStrategyCut:
  def test_verification_strategy_removed(self) -> None:
    text = "---\nid: PROD-100\nkind: prod\nverification_strategy: manual\n---\nbody\n"
    result = _transform(text)
    fm = _parse_fm(result.text)
    assert "verification_strategy" not in fm
    assert DRIFT_VERIFICATION_STRATEGY_CUT in _drift_kinds(result.drift)


# ---------------------------------------------------------------------------
# apply() and preview()
# ---------------------------------------------------------------------------


class TestApplyAndPreview:
  _PROD_TEXT = '---\nid: PROD-100\nkind: prod\nscope: "all"\n---\n# PROD-100\n'

  def test_apply_writes_file(self, tmp_path: Path) -> None:
    p = _write_prod(tmp_path, "PROD-100.md", self._PROD_TEXT)
    result = step.apply(p)
    assert result.touched == [p]
    fm = _parse_fm(p.read_text(encoding="utf-8"))
    assert "scope" not in fm

  def test_apply_idempotent(self, tmp_path: Path) -> None:
    p = _write_prod(tmp_path, "PROD-100.md", self._PROD_TEXT)
    step.apply(p)
    result = step.apply(p)
    assert result.touched == []
    assert result.skipped == [p]

  def test_preview_no_write(self, tmp_path: Path) -> None:
    p = _write_prod(tmp_path, "PROD-100.md", self._PROD_TEXT)
    original = p.read_text(encoding="utf-8")
    preview = step.preview(p)
    assert preview.touched == [p]
    assert p.read_text(encoding="utf-8") == original

  def test_apply_skips_clean(self, tmp_path: Path) -> None:
    p = _write_prod(
      tmp_path,
      "PROD-100.md",
      "---\nid: PROD-100\nkind: prod\n---\nbody\n",
    )
    result = step.apply(p)
    assert result.skipped == [p]


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
  def test_no_frontmatter(self) -> None:
    result = _transform("just body\n")
    assert not result.changed

  def test_multiple_cut_fields(self) -> None:
    text = (
      "---\nid: PROD-100\nkind: prod\n"
      'scope: "all"\nverification_strategy: tdd\n'
      "hypotheses:\n  - id: H-001\n    statement: x\n    status: open\n"
      "---\n## 1. Intent & Summary\n\nText.\n"
    )
    result = _transform(text)
    fm = _parse_fm(result.text)
    for key in ("scope", "verification_strategy", "hypotheses"):
      assert key not in fm
    kinds = _drift_kinds(result.drift)
    assert DRIFT_SCOPE_MOVED in kinds
    assert DRIFT_VERIFICATION_STRATEGY_CUT in kinds
    assert DRIFT_HYPOTHESES_EMITTED in kinds
