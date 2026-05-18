"""Tests for `spec_driver.core.yaml_emit` — comment-preserving YAML emitter.

Covers VT-CC-005 (primitive + container types) and VT-CC-006 (deterministic
output). Also asserts CompactDumper-equivalence so the existing
`dump_frontmatter_yaml` callers stay byte-identical after delegation.
"""

from __future__ import annotations

import yaml

from .yaml_emit import emit_yaml_block


class TestEmitPrimitives:
  """VT-CC-005 part 1 — primitive scalar shapes."""

  def test_string_value(self) -> None:
    out = emit_yaml_block({"name": "hello world"})
    assert "name: hello world" in out

  def test_int_value(self) -> None:
    out = emit_yaml_block({"version": 7})
    assert "version: 7" in out

  def test_bool_value(self) -> None:
    out = emit_yaml_block({"flag": True})
    assert "flag: true" in out

  def test_none_value(self) -> None:
    out = emit_yaml_block({"slot": None})
    assert "slot: null" in out

  def test_empty_dict_emits_nothing_meaningful(self) -> None:
    assert emit_yaml_block({}).strip() == "{}"


class TestEmitContainers:
  """VT-CC-005 part 2 — list + nested-dict shapes."""

  def test_short_scalar_list_is_flow(self) -> None:
    out = emit_yaml_block({"tags": ["a", "b", "c"]})
    assert "tags: [a, b, c]" in out

  def test_empty_list_is_flow(self) -> None:
    out = emit_yaml_block({"aliases": []})
    assert "aliases: []" in out

  def test_long_scalar_list_is_block(self) -> None:
    items = [f"item-{i:03d}" for i in range(20)]
    out = emit_yaml_block({"items": items})
    assert "- item-000" in out

  def test_list_of_dicts_is_block(self) -> None:
    out = emit_yaml_block({"relations": [{"type": "implements", "target": "FR-001"}]})
    assert "- type: implements" in out

  def test_nested_dict(self) -> None:
    out = emit_yaml_block({"meta": {"a": 1, "b": 2}})
    assert "meta:" in out
    assert "a: 1" in out
    assert "b: 2" in out


class TestQuotingHeuristic:
  """Prettier-compatible quoting (inherited from CompactDumper)."""

  def test_date_string_quoted(self) -> None:
    out = emit_yaml_block({"created": "2025-01-15"})
    assert 'created: "2025-01-15"' in out

  def test_bool_like_string_double_quoted(self) -> None:
    out = emit_yaml_block({"flag": "true"})
    assert 'flag: "true"' in out

  def test_null_like_string_double_quoted(self) -> None:
    out = emit_yaml_block({"slot": "null"})
    assert 'slot: "null"' in out

  def test_empty_string_double_quoted(self) -> None:
    out = emit_yaml_block({"empty": ""})
    assert 'empty: ""' in out

  def test_colon_containing_string_double_quoted(self) -> None:
    out = emit_yaml_block({"title": "STD-001: use typer"})
    assert 'title: "STD-001: use typer"' in out

  def test_double_quote_containing_string_uses_single_quotes(self) -> None:
    out = emit_yaml_block({"notes": 'value with "quotes" inside: x'})
    assert "notes: 'value with \"quotes\" inside: x'" in out

  def test_plain_string_unquoted(self) -> None:
    out = emit_yaml_block({"name": "hello world"})
    assert "name: hello world" in out


class TestDeterminism:
  """VT-CC-006 — deterministic output across repeated invocations."""

  def test_key_order_preserved(self) -> None:
    data = {"z": 1, "a": 2, "m": 3}
    out = emit_yaml_block(data)
    assert out.index("z:") < out.index("a:") < out.index("m:")

  def test_byte_identical_across_invocations(self) -> None:
    data = {
      "id": "SPEC-100",
      "name": "test",
      "tags": ["auth", "security"],
      "relations": [{"type": "implements", "target": "FR-001"}],
    }
    a = emit_yaml_block(data)
    b = emit_yaml_block(data)
    assert a == b

  def test_round_trip_idempotent(self) -> None:
    data = {
      "id": "SPEC-100",
      "tags": ["auth", "security"],
      "relations": [{"type": "implements", "target": "FR-001"}],
      "aliases": [],
    }
    a = emit_yaml_block(data)
    b = emit_yaml_block(yaml.safe_load(a))
    assert a == b

  def test_unicode_preserved(self) -> None:
    out = emit_yaml_block({"note": "spec ⇄ delta"})
    assert "⇄" in out

  def test_no_trailing_newline(self) -> None:
    out = emit_yaml_block({"id": "DE-001"})
    assert not out.endswith("\n")


class TestCommentInjection:
  """Trailing `# comment` on top-level scalar keys."""

  def test_comment_on_scalar_key(self) -> None:
    out = emit_yaml_block(
      {"status": "draft"},
      comments={"status": "one of: draft | in-progress | completed"},
    )
    assert "status: draft  # one of: draft | in-progress | completed" in out

  def test_comment_only_appended_when_mapped(self) -> None:
    out = emit_yaml_block({"id": "DE-001", "status": "draft"}, comments={"status": "x"})
    lines = out.splitlines()
    [id_line] = [line for line in lines if line.startswith("id:")]
    [status_line] = [line for line in lines if line.startswith("status:")]
    assert "#" not in id_line
    assert status_line.endswith("# x")

  def test_no_comment_on_container_value(self) -> None:
    out = emit_yaml_block(
      {"tags": ["a", "b"]},
      comments={"tags": "list comment - should NOT appear inline"},
    )
    # Container values do not accept inline comments per DR-137 §5.1.
    assert "list comment" not in out

  def test_comment_map_none_emits_no_comments(self) -> None:
    out = emit_yaml_block({"status": "draft"}, comments=None)
    assert "#" not in out

  def test_unmapped_keys_unaffected(self) -> None:
    out = emit_yaml_block({"id": "DE-001", "status": "draft"}, comments={})
    assert "#" not in out

  def test_unicode_in_comment(self) -> None:
    out = emit_yaml_block({"status": "draft"}, comments={"status": "see § 5.2"})
    assert "# see § 5.2" in out


class TestCompactDumperEquivalence:
  """Belt-and-braces: emit_yaml_block matches the legacy `dump_frontmatter_yaml`
  for the no-comments case.

  Critical for the no-regression migration of ~95 test sites and ~33 production
  call sites that round-trip through the existing CompactDumper output today.
  """

  def test_matches_legacy_for_typical_frontmatter(self) -> None:
    from supekku.scripts.lib.core.frontmatter_writer import (  # noqa: PLC0415
      dump_frontmatter_yaml,
    )

    data = {
      "id": "DE-001",
      "name": "Example Delta",
      "status": "draft",
      "kind": "delta",
      "created": "2026-01-01",
      "updated": "2026-01-01",
      "tags": ["a", "b"],
      "relations": [{"type": "implements", "target": "FR-001"}],
      "aliases": [],
    }
    assert emit_yaml_block(data) == dump_frontmatter_yaml(data)
