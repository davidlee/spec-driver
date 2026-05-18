"""Tests for `spec_driver.orchestration.templates`.

Covers:
- VT-CC-001 — regenerated template carries enum-comment string for ≥1 field per kind.
- VT-CC-002 — regenerator idempotency (second invocation returns False).
- VT-CC-007 — malformed user template fails loudly with path + parse error.
- VT-CC-024 — comment-map invariance: `data=None` vs `data=sample_fm` produces
  identical comment ordering + content (the comments come from BlockMetadata,
  not from data shape).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from .templates import (
  TEMPLATE_PLACEHOLDERS,
  UnknownKindError,
  _build_comment_map,
  _split_frontmatter,
  regenerate_template,
  render_frontmatter_for_kind,
  validate_templates,
)

_KIND_FILE_MAP = {
  "adr": "ADR.md",
  "audit": "audit.md",
  "delta": "delta.md",
  "design_revision": "design_revision.md",
  "phase": "phase.md",
  "plan": "plan.md",
  "policy": "policy-template.md",
  "revision": "revision.md",
  "spec": "spec.md",
  "standard": "standard-template.md",
}


@pytest.fixture
def repo_root() -> Path:
  here = Path(__file__).resolve()
  for parent in here.parents:
    if (parent / "supekku" / "templates").is_dir():
      return parent
  msg = "Could not locate repo root for templates fixture"
  raise RuntimeError(msg)


class TestRenderReference:
  """Reference-mode (data=None) render shape per kind."""

  @pytest.mark.parametrize("kind", sorted(TEMPLATE_PLACEHOLDERS.keys()))
  def test_renders_required_fields(self, kind: str) -> None:
    out = render_frontmatter_for_kind(kind, data=None)
    assert "id:" in out
    assert "kind:" in out
    assert "status:" in out
    assert "created:" in out
    assert "updated:" in out

  def test_uses_jinja_style_placeholders(self) -> None:
    out = render_frontmatter_for_kind("delta", data=None)
    assert "{{ delta_id }}" in out
    assert "{{ today }}" in out

  def test_unknown_kind_raises(self) -> None:
    with pytest.raises(UnknownKindError):
      render_frontmatter_for_kind("does_not_exist", data=None)

  def test_kind_field_uses_literal(self) -> None:
    out = render_frontmatter_for_kind("delta", data=None)
    assert "kind: delta" in out


class TestEnumCommentHints:
  """VT-CC-001 — every renderable kind carries ≥1 enum-comment hint."""

  @pytest.mark.parametrize("kind", sorted(TEMPLATE_PLACEHOLDERS.keys()))
  def test_status_enum_comment_present(self, kind: str) -> None:
    out = render_frontmatter_for_kind(kind, data=None)
    # Every kind in our metadata registry promotes status to enum during P01.
    assert "# one of:" in out, f"missing enum-comment hint for kind={kind}"

  def test_delta_status_lists_canonical_values(self) -> None:
    out = render_frontmatter_for_kind("delta", data=None)
    assert "status: draft" in out
    # Delta status enum includes draft/in-progress/completed/pending/deferred.
    [status_line] = [ln for ln in out.splitlines() if ln.startswith("status:")]
    assert "draft" in status_line
    assert "in-progress" in status_line
    assert "completed" in status_line


class TestConcreteMode:
  """Data-mode render reuses the same comment map."""

  def test_concrete_data_emitted_verbatim(self) -> None:
    data = {
      "id": "DE-999",
      "name": "concrete",
      "slug": "concrete",
      "kind": "delta",
      "status": "in-progress",
      "created": "2026-01-01",
      "updated": "2026-01-01",
    }
    out = render_frontmatter_for_kind("delta", data=data)
    assert "id: DE-999" in out
    assert "status: in-progress  # one of:" in out

  def test_concrete_no_placeholder_leakage(self) -> None:
    data = {"id": "DE-1", "name": "x", "kind": "delta", "status": "draft"}
    out = render_frontmatter_for_kind("delta", data=data)
    assert "{{" not in out
    assert "}}" not in out


class TestCommentMapInvariance:
  """VT-CC-024 — comment map is identical across reference and concrete modes."""

  @pytest.mark.parametrize("kind", sorted(TEMPLATE_PLACEHOLDERS.keys()))
  def test_comment_map_only_depends_on_metadata(self, kind: str) -> None:
    from supekku.scripts.lib.core.frontmatter_metadata import (  # noqa: PLC0415
      FRONTMATTER_METADATA_REGISTRY,
    )

    metadata = FRONTMATTER_METADATA_REGISTRY[kind]
    map_a = _build_comment_map(metadata)
    map_b = _build_comment_map(metadata)
    assert map_a == map_b
    assert list(map_a.keys()) == list(map_b.keys())

  def test_comment_lines_byte_identical_across_modes(self) -> None:
    kind = "delta"
    reference = render_frontmatter_for_kind(kind, data=None)
    sample = {
      "id": "DE-1",
      "name": "x",
      "slug": "x",
      "kind": "delta",
      "status": "draft",
      "created": "2026-01-01",
      "updated": "2026-01-01",
    }
    concrete = render_frontmatter_for_kind(kind, data=sample)
    ref_comments = sorted(
      ln.split("#", 1)[1].strip() for ln in reference.splitlines() if "#" in ln
    )
    conc_comments = sorted(
      ln.split("#", 1)[1].strip() for ln in concrete.splitlines() if "#" in ln
    )
    assert ref_comments == conc_comments


class TestSplitFrontmatter:
  """Lexer covers happy + malformed paths."""

  def test_template_without_frontmatter(self) -> None:
    fm, body = _split_frontmatter("# heading\n\nbody\n")
    assert fm == ""
    assert body == "# heading\n\nbody\n"

  def test_template_with_frontmatter(self) -> None:
    text = "---\nid: DE-1\nkind: delta\n---\n\n# body\n"
    fm, body = _split_frontmatter(text)
    assert "id: DE-1" in fm
    assert body == "# body\n"

  def test_unterminated_frontmatter_raises(self) -> None:
    with pytest.raises(ValueError, match="closing `---`"):
      _split_frontmatter("---\nid: oops\n")


class TestRegenerateTemplate:
  """VT-CC-002 — idempotency. VT-CC-007 — malformed fail-loud."""

  def test_inserts_frontmatter_when_absent(self, tmp_path: Path) -> None:
    p = tmp_path / "delta.md"
    p.write_text("# {{ delta_id }}\n\nBody.\n", encoding="utf-8")
    assert regenerate_template("delta", p) is True
    text = p.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert "kind: delta" in text
    assert "# {{ delta_id }}" in text  # body preserved
    assert "Body." in text

  def test_idempotent_second_run_no_op(self, tmp_path: Path) -> None:
    p = tmp_path / "delta.md"
    p.write_text("# {{ delta_id }}\n\nBody.\n", encoding="utf-8")
    regenerate_template("delta", p)
    first = p.read_text(encoding="utf-8")
    assert regenerate_template("delta", p) is False
    assert p.read_text(encoding="utf-8") == first

  def test_body_byte_preserved(self, tmp_path: Path) -> None:
    body = "# {{ delta_id }}\n\n{{ delta_relationships_block }}\n\nlast line\n"
    p = tmp_path / "delta.md"
    p.write_text(body, encoding="utf-8")
    regenerate_template("delta", p)
    text = p.read_text(encoding="utf-8")
    _, after_body = _split_frontmatter(text)
    assert after_body == body

  def test_malformed_template_raises(self, tmp_path: Path) -> None:
    p = tmp_path / "broken.md"
    p.write_text("---\nid: oops\nno-closer-line\n", encoding="utf-8")
    with pytest.raises(ValueError, match="closing `---`"):
      regenerate_template("delta", p)

  def test_unknown_kind_raises(self, tmp_path: Path) -> None:
    p = tmp_path / "any.md"
    p.write_text("# body\n", encoding="utf-8")
    with pytest.raises(UnknownKindError):
      regenerate_template("does_not_exist", p)


class TestValidateTemplates:
  """VT-CC-003 dry-run validator behaviour against synthetic templates."""

  def test_clean_after_regeneration(self, tmp_path: Path) -> None:
    templates_dir = tmp_path / "supekku" / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "delta.md").write_text("# body\n", encoding="utf-8")
    # Round-trip: regenerate, then validate ⇒ no drift.
    regenerate_template("delta", templates_dir / "delta.md")
    drifts = validate_templates(tmp_path, kinds=("delta",))
    assert drifts == []

  def test_drift_detected_on_unregenerated_template(self, tmp_path: Path) -> None:
    templates_dir = tmp_path / "supekku" / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "delta.md").write_text("# bare body\n", encoding="utf-8")
    drifts = validate_templates(tmp_path, kinds=("delta",))
    assert len(drifts) == 1
    assert drifts[0].kind == "delta"
    assert "kind: delta" in drifts[0].diff

  def test_missing_template_file_skipped(self, tmp_path: Path) -> None:
    (tmp_path / "supekku" / "templates").mkdir(parents=True)
    drifts = validate_templates(tmp_path, kinds=("delta",))
    assert drifts == []
