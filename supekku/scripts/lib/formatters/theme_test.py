"""Tests for theme style resolution API (VT-053-styled-text)."""

from __future__ import annotations

import pytest
from rich.style import Style
from rich.text import Text

from supekku.scripts.lib.formatters.theme import (
  SPEC_DRIVER_THEME,
  resolve_style,
  styled_text,
)


class TestResolveStyle:
  """Tests for resolve_style()."""

  def test_resolves_known_style(self):
    style = resolve_style("adr.status.accepted")
    assert style is not None
    assert isinstance(style, Style)

  def test_resolves_to_correct_color(self):
    style = resolve_style("adr.status.accepted")
    assert style is not None
    assert style.color is not None
    r, g, b = style.color.get_truecolor()
    assert (r, g, b) == (142, 192, 124)  # #8ec07c

  def test_returns_none_for_unknown_style(self):
    assert resolve_style("nonexistent.style.name") is None

  def test_returns_none_for_empty_string(self):
    assert resolve_style("") is None

  @pytest.mark.parametrize(
    "style_name",
    [
      "adr.id",
      "spec.id",
      "change.id",
      "adr.status.accepted",
      "change.status.completed",
      "spec.status.active",
      "requirement.status.active",
      "memory.status.active",
      "policy.status.active",
      "standard.status.required",
      "backlog.issue.open",
      "backlog.improvement.idea",
      "artifact.group.governance",
      "artifact.group.change",
      "artifact.group.domain",
      "artifact.group.operational",
    ],
  )
  def test_all_core_styles_resolve(self, style_name: str):
    """Regression: all style keys consumed by TUI must resolve."""
    style = resolve_style(style_name)
    assert style is not None, f"Style '{style_name}' should resolve"


class TestStyledText:
  """Tests for styled_text()."""

  def test_returns_text_object(self):
    result = styled_text("SPEC-001", "spec.id")
    assert isinstance(result, Text)
    assert str(result) == "SPEC-001"

  def test_applies_resolved_style(self):
    result = styled_text("accepted", "adr.status.accepted")
    assert len(result._spans) == 1
    span = result._spans[0]
    assert span.style is not None
    assert isinstance(span.style, Style)

  def test_missing_style_returns_unstyled_text(self):
    result = styled_text("hello", "nonexistent.style")
    assert isinstance(result, Text)
    assert str(result) == "hello"
    assert len(result._spans) == 0

  def test_empty_value(self):
    result = styled_text("", "spec.id")
    assert isinstance(result, Text)
    assert str(result) == ""

  def test_style_color_matches_theme(self):
    result = styled_text("DE-050", "change.id")
    expected_style = SPEC_DRIVER_THEME.styles.get("change.id")
    assert expected_style is not None
    span = result._spans[0]
    assert span.style.color == expected_style.color
