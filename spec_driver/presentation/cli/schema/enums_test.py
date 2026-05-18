"""VT-CC-015 + VA-CC-001 — ``schema enums`` CLI surfaces.

VT-CC-015: output shape parity with DR-137 §5.3 across three invocation
forms.

VA-CC-001: parametric smoke across every Category A controlled-vocab
field. Implemented as a parameterised pytest sweep to satisfy the
"agent-generated" intent without a manual report.
"""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from supekku.cli.main import app
from spec_driver.presentation.cli.schema.enums import (
  _controlled_fields,
  _kinds_with_controlled_vocab,
)
from supekku.scripts.lib.core.frontmatter_metadata import (
  FRONTMATTER_METADATA_REGISTRY,
)

runner = CliRunner()


class TestThreeInvocationForms:
  """VT-CC-015 — DR-137 §5.3 output shape parity."""

  def test_bare_enums_lists_every_kind(self) -> None:
    result = runner.invoke(app, ["schema", "enums"])
    assert result.exit_code == 0
    out = result.output
    # Every kind with controlled vocab appears in the table.
    catalogue = _kinds_with_controlled_vocab()
    for kind in catalogue:
      assert kind in out, kind

  def test_enums_for_kind_lists_controlled_fields(self) -> None:
    result = runner.invoke(app, ["schema", "enums", "delta"])
    assert result.exit_code == 0
    out = result.output
    assert "status" in out
    # canonical values mentioned
    assert "completed" in out
    assert "draft" in out

  def test_enums_for_field_shows_canonical_aliases_tolerated_sections(
    self,
  ) -> None:
    result = runner.invoke(app, ["schema", "enums", "delta.status"])
    assert result.exit_code == 0
    out = result.output
    assert "delta.status" in out
    assert "Canonical values" in out
    assert "completed" in out
    # delta.status has permanent aliases per P01: complete ⇒ completed
    assert "Permanent aliases" in out
    assert "complete" in out
    # Tolerated section is rendered (either entries or '(none)')
    assert "Tolerated aliases" in out

  def test_unknown_kind_exits_nonzero(self) -> None:
    result = runner.invoke(app, ["schema", "enums", "this-kind-does-not-exist"])
    assert result.exit_code != 0

  def test_unknown_field_exits_nonzero(self) -> None:
    result = runner.invoke(app, ["schema", "enums", "delta.this-field-does-not-exist"])
    assert result.exit_code != 0


def _parametrise_controlled_fields() -> list[tuple[str, str]]:
  """Build the ``(kind, field)`` matrix for VA-CC-001."""
  pairs: list[tuple[str, str]] = []
  for kind, metadata in FRONTMATTER_METADATA_REGISTRY.items():
    for field_name in _controlled_fields(metadata):
      pairs.append((kind, field_name))
  return pairs


class TestParametricCoverageVACC001:
  """VA-CC-001 — parametric smoke across every Category A controlled-vocab field."""

  @pytest.mark.parametrize(
    ("kind", "field"), _parametrise_controlled_fields()
  )
  def test_every_field_renders_cleanly(self, kind: str, field: str) -> None:
    result = runner.invoke(app, ["schema", "enums", f"{kind}.{field}"])
    assert result.exit_code == 0, (
      f"{kind}.{field}: exit {result.exit_code}: {result.output} "
      f"{result.stderr or ''}"
    )
    assert f"{kind}.{field}" in result.output
    assert "Canonical values" in result.output

  @pytest.mark.parametrize(
    "kind",
    sorted(_kinds_with_controlled_vocab().keys()),
  )
  def test_every_kind_renders_cleanly(self, kind: str) -> None:
    result = runner.invoke(app, ["schema", "enums", kind])
    assert result.exit_code == 0
