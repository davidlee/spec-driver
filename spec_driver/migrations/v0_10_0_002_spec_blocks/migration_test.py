"""VTs for the v0_10_0_002_spec_blocks migration step.

Covers:

- ``VT-DE139-MIG-001`` — packages cut, taxonomy defaulted, idempotence.
- Block emission from non-empty FM concerns/hypotheses/decisions.
- Scope FM→prose body insertion.
- verification_strategy cut.
- ``preview()`` writes nothing and surfaces drift.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from spec_driver.migrations.v0_10_0_002_spec_blocks import SpecBlocksStep, step
from spec_driver.migrations.v0_10_0_002_spec_blocks.migration import (
  DRIFT_CONCERNS_EMITTED,
  DRIFT_DECISIONS_EMITTED,
  DRIFT_HYPOTHESES_EMITTED,
  DRIFT_PACKAGES_CUT,
  DRIFT_SCOPE_MOVED,
  DRIFT_TAXONOMY_DEFAULTED,
  DRIFT_VERIFICATION_STRATEGY_CUT,
  _transform,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_spec(tmp_path: Path, name: str, contents: str) -> Path:
  path = tmp_path / name
  path.write_text(contents, encoding="utf-8")
  return path


def _drift_kinds(drift: list) -> set[str]:
  return {entry.kind for entry in drift}


def _parse_fm(text: str) -> dict:
  """Extract and parse frontmatter from text."""
  lines = text.split("\n")
  assert lines[0] == "---"
  end = lines.index("---", 1)
  return yaml.safe_load("\n".join(lines[1:end]))


# ---------------------------------------------------------------------------
# Module-level step export
# ---------------------------------------------------------------------------


def test_module_exports_step_instance() -> None:
  assert isinstance(step, SpecBlocksStep)
  assert step.applies_to_kind == "spec"


# ---------------------------------------------------------------------------
# applies_to() (VT-DE139-MIG-001 prelude)
# ---------------------------------------------------------------------------


class TestAppliesTo:
  def test_matches_packages_key(self, tmp_path: Path) -> None:
    p = _write_spec(
      tmp_path,
      "SPEC-100.md",
      "---\nid: SPEC-100\nkind: spec\ncategory: unit\nc4_level: code\n"
      "packages: [foo]\n---\nbody\n",
    )
    assert SpecBlocksStep().applies_to(p)

  def test_matches_each_cut_key(self, tmp_path: Path) -> None:
    for key in (
      "packages",
      "concerns",
      "hypotheses",
      "decisions",
      "verification_strategy",
      "scope",
    ):
      p = _write_spec(
        tmp_path,
        f"SPEC-{key}.md",
        f"---\nid: SPEC-100\nkind: spec\ncategory: unit\nc4_level: code\n"
        f"{key}: foo\n---\nbody\n",
      )
      assert SpecBlocksStep().applies_to(p), key

  def test_matches_missing_taxonomy(self, tmp_path: Path) -> None:
    p = _write_spec(
      tmp_path,
      "SPEC-100.md",
      "---\nid: SPEC-100\nkind: spec\n---\nbody\n",
    )
    assert SpecBlocksStep().applies_to(p)

  def test_skips_clean_spec(self, tmp_path: Path) -> None:
    p = _write_spec(
      tmp_path,
      "SPEC-100.md",
      "---\nid: SPEC-100\nkind: spec\ncategory: unit\nc4_level: code\n---\nbody\n",
    )
    assert not SpecBlocksStep().applies_to(p)

  def test_skips_non_existent(self, tmp_path: Path) -> None:
    assert not SpecBlocksStep().applies_to(tmp_path / "nope.md")

  def test_skips_no_frontmatter(self, tmp_path: Path) -> None:
    p = _write_spec(tmp_path, "plain.md", "just body text\n")
    assert not SpecBlocksStep().applies_to(p)


# ---------------------------------------------------------------------------
# packages cut (VT-DE139-MIG-001)
# ---------------------------------------------------------------------------


class TestPackagesCut:
  _SPEC_WITH_PACKAGES = (
    "---\n"
    "id: SPEC-141\n"
    "slug: supekku-scripts-lib-contracts\n"
    "name: contracts Specification\n"
    "created: '2026-03-07'\n"
    "updated: '2026-03-07'\n"
    "status: stub\n"
    "kind: spec\n"
    "category: unit\n"
    "c4_level: code\n"
    "responsibilities: []\n"
    "aliases: []\n"
    "packages: [supekku/scripts/lib/contracts]\n"
    "sources:\n"
    "  - language: python\n"
    "    identifier: supekku/scripts/lib/contracts\n"
    "---\n"
    "\n"
    "# SPEC-141 – contracts\n"
  )

  def test_packages_removed_from_fm(self) -> None:
    result = _transform(self._SPEC_WITH_PACKAGES)
    assert result.changed
    fm = _parse_fm(result.text)
    assert "packages" not in fm

  def test_packages_drift_recorded(self) -> None:
    result = _transform(self._SPEC_WITH_PACKAGES)
    assert DRIFT_PACKAGES_CUT in _drift_kinds(result.drift)

  def test_other_keys_preserved(self) -> None:
    result = _transform(self._SPEC_WITH_PACKAGES)
    fm = _parse_fm(result.text)
    assert fm["id"] == "SPEC-141"
    assert fm["category"] == "unit"
    assert fm["c4_level"] == "code"
    assert fm["sources"] == [
      {"language": "python", "identifier": "supekku/scripts/lib/contracts"}
    ]

  def test_body_preserved(self) -> None:
    result = _transform(self._SPEC_WITH_PACKAGES)
    assert "# SPEC-141 – contracts" in result.text

  def test_idempotent(self) -> None:
    first = _transform(self._SPEC_WITH_PACKAGES)
    second = _transform(first.text)
    assert not second.changed
    assert second.text == first.text


# ---------------------------------------------------------------------------
# Taxonomy defaults (VT-DE139-MIG-001)
# ---------------------------------------------------------------------------


class TestTaxonomyDefaults:
  def test_category_defaulted(self) -> None:
    text = "---\nid: SPEC-100\nkind: spec\nc4_level: code\n---\nbody\n"
    result = _transform(text)
    assert result.changed
    fm = _parse_fm(result.text)
    assert fm["category"] == "unknown"

  def test_c4_level_defaulted(self) -> None:
    text = "---\nid: SPEC-100\nkind: spec\ncategory: unit\n---\nbody\n"
    result = _transform(text)
    assert result.changed
    fm = _parse_fm(result.text)
    assert fm["c4_level"] == "unknown"

  def test_both_defaulted(self) -> None:
    text = "---\nid: SPEC-100\nkind: spec\n---\nbody\n"
    result = _transform(text)
    fm = _parse_fm(result.text)
    assert fm["category"] == "unknown"
    assert fm["c4_level"] == "unknown"
    kinds = _drift_kinds(result.drift)
    assert DRIFT_TAXONOMY_DEFAULTED in kinds

  def test_existing_taxonomy_untouched(self) -> None:
    text = (
      "---\nid: SPEC-100\nkind: spec\ncategory: assembly\n"
      "c4_level: component\npackages: [x]\n---\nbody\n"
    )
    result = _transform(text)
    fm = _parse_fm(result.text)
    assert fm["category"] == "assembly"
    assert fm["c4_level"] == "component"


# ---------------------------------------------------------------------------
# Concerns block emission
# ---------------------------------------------------------------------------


class TestConcernsBlock:
  def test_non_empty_concerns_emitted(self) -> None:
    text = (
      "---\nid: SPEC-100\nkind: spec\ncategory: unit\nc4_level: code\n"
      "concerns:\n"
      "  - name: perf\n"
      "    description: latency matters\n"
      "---\nbody\n"
    )
    result = _transform(text)
    assert "supekku:spec.concerns@v1" in result.text
    assert "perf" in result.text
    assert DRIFT_CONCERNS_EMITTED in _drift_kinds(result.drift)
    fm = _parse_fm(result.text)
    assert "concerns" not in fm

  def test_empty_concerns_not_emitted(self) -> None:
    text = (
      "---\nid: SPEC-100\nkind: spec\ncategory: unit\nc4_level: code\n"
      "concerns: []\n---\nbody\n"
    )
    result = _transform(text)
    assert "supekku:spec.concerns@v1" not in result.text

  def test_existing_block_not_duplicated(self) -> None:
    text = (
      "---\nid: SPEC-100\nkind: spec\ncategory: unit\nc4_level: code\n"
      "concerns:\n"
      "  - name: perf\n"
      "    description: latency matters\n"
      "---\n"
      "```yaml supekku:spec.concerns@v1\nschema: supekku.spec.concerns\n"
      "version: 1\nspec: SPEC-100\nconcerns: []\n```\n"
    )
    result = _transform(text)
    assert result.text.count("supekku:spec.concerns@v1") == 1


# ---------------------------------------------------------------------------
# Hypotheses block emission
# ---------------------------------------------------------------------------


class TestHypothesesBlock:
  def test_non_empty_hypotheses_emitted(self) -> None:
    text = (
      "---\nid: SPEC-100\nkind: spec\ncategory: unit\nc4_level: code\n"
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
      "---\nid: SPEC-100\nkind: spec\ncategory: unit\nc4_level: code\n"
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
# Scope → prose
# ---------------------------------------------------------------------------


class TestScopeMoved:
  def test_scope_moved_to_body(self) -> None:
    text = (
      "---\nid: SPEC-100\nkind: spec\ncategory: unit\nc4_level: code\n"
      'scope: "handles widget parsing"\n'
      "---\n\n## 1. Intent & Summary\n\nSome text.\n"
    )
    result = _transform(text)
    assert result.changed
    fm = _parse_fm(result.text)
    assert "scope" not in fm
    assert "> **Scope**: handles widget parsing" in result.text
    assert DRIFT_SCOPE_MOVED in _drift_kinds(result.drift)

  def test_empty_scope_ignored(self) -> None:
    text = (
      "---\nid: SPEC-100\nkind: spec\ncategory: unit\nc4_level: code\n"
      'scope: ""\n---\nbody\n'
    )
    result = _transform(text)
    assert "**Scope**" not in result.text


# ---------------------------------------------------------------------------
# Verification strategy cut
# ---------------------------------------------------------------------------


class TestVerificationStrategyCut:
  def test_verification_strategy_removed(self) -> None:
    text = (
      "---\nid: SPEC-100\nkind: spec\ncategory: unit\nc4_level: code\n"
      "verification_strategy: manual\n---\nbody\n"
    )
    result = _transform(text)
    fm = _parse_fm(result.text)
    assert "verification_strategy" not in fm
    assert DRIFT_VERIFICATION_STRATEGY_CUT in _drift_kinds(result.drift)


# ---------------------------------------------------------------------------
# apply() and preview() (VT-DE139-MIG-001)
# ---------------------------------------------------------------------------


class TestApplyAndPreview:
  _SPEC_TEXT = (
    "---\nid: SPEC-100\nkind: spec\ncategory: unit\nc4_level: code\n"
    "packages: [foo/bar]\n---\n# SPEC-100\n"
  )

  def test_apply_writes_file(self, tmp_path: Path) -> None:
    p = _write_spec(tmp_path, "SPEC-100.md", self._SPEC_TEXT)
    result = step.apply(p)
    assert result.touched == [p]
    assert result.skipped == []
    content = p.read_text(encoding="utf-8")
    fm = _parse_fm(content)
    assert "packages" not in fm

  def test_apply_idempotent(self, tmp_path: Path) -> None:
    p = _write_spec(tmp_path, "SPEC-100.md", self._SPEC_TEXT)
    step.apply(p)
    result = step.apply(p)
    assert result.touched == []
    assert result.skipped == [p]

  def test_preview_no_write(self, tmp_path: Path) -> None:
    p = _write_spec(tmp_path, "SPEC-100.md", self._SPEC_TEXT)
    original = p.read_text(encoding="utf-8")
    preview = step.preview(p)
    assert preview.touched == [p]
    assert p.read_text(encoding="utf-8") == original

  def test_apply_skips_clean(self, tmp_path: Path) -> None:
    clean = "---\nid: SPEC-100\nkind: spec\ncategory: unit\nc4_level: code\n---\nbody\n"
    p = _write_spec(tmp_path, "SPEC-100.md", clean)
    result = step.apply(p)
    assert result.touched == []
    assert result.skipped == [p]

  def test_preview_surfaces_drift(self, tmp_path: Path) -> None:
    p = _write_spec(tmp_path, "SPEC-100.md", self._SPEC_TEXT)
    preview = step.preview(p)
    assert any("packages_cut" in d for d in preview.drift)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
  def test_no_frontmatter(self) -> None:
    result = _transform("just body text\n")
    assert not result.changed

  def test_non_dict_frontmatter(self) -> None:
    result = _transform("---\n- item\n---\nbody\n")
    assert not result.changed

  def test_empty_packages_list(self) -> None:
    text = (
      "---\nid: SPEC-100\nkind: spec\ncategory: unit\nc4_level: code\n"
      "packages: []\n---\nbody\n"
    )
    result = _transform(text)
    assert result.changed
    fm = _parse_fm(result.text)
    assert "packages" not in fm
    assert DRIFT_PACKAGES_CUT not in _drift_kinds(result.drift)

  def test_multiple_cut_fields(self) -> None:
    text = (
      "---\nid: SPEC-100\nkind: spec\ncategory: unit\nc4_level: code\n"
      'packages: [x]\nverification_strategy: tdd\nscope: "all widgets"\n'
      "concerns:\n  - name: a\n    description: b\n"
      "---\n## 1. Intent & Summary\n\nText.\n"
    )
    result = _transform(text)
    fm = _parse_fm(result.text)
    for key in ("packages", "verification_strategy", "scope", "concerns"):
      assert key not in fm
    kinds = _drift_kinds(result.drift)
    assert DRIFT_PACKAGES_CUT in kinds
    assert DRIFT_VERIFICATION_STRATEGY_CUT in kinds
    assert DRIFT_SCOPE_MOVED in kinds
    assert DRIFT_CONCERNS_EMITTED in kinds
