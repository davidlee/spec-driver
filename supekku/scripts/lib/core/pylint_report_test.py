"""Tests for pylint report helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from supekku.scripts.lib.core.pylint_report import (
  load_pylint_json,
  render_pylint_summary,
  summarize_pylint_report,
)


def _sample_report() -> dict:
  return {
    "messages": [
      {
        "type": "warning",
        "symbol": "broad-exception-caught",
        "message": "Catching too general exception Exception",
        "path": "supekku/tui/app.py",
        "line": 89,
      },
      {
        "type": "convention",
        "symbol": "missing-function-docstring",
        "message": "Missing function or method docstring",
        "path": "supekku/tui/app.py",
        "line": 62,
      },
      {
        "type": "convention",
        "symbol": "import-outside-toplevel",
        "message": "Import outside toplevel",
        "path": "supekku/tui/widgets/type_selector.py",
        "line": 54,
      },
    ],
    "statistics": {
      "messageTypeCount": {
        "fatal": 0,
        "error": 0,
        "warning": 1,
        "refactor": 0,
        "convention": 2,
        "info": 0,
      },
      "modulesLinted": 2,
      "score": 9.7,
    },
  }


class TestLoadPylintJson:
  """Tests for parsing pylint json2."""

  def test_parses_valid_json(self) -> None:
    report = load_pylint_json('{"messages": [], "statistics": {"score": 10.0}}')
    assert report["statistics"]["score"] == 10.0

  def test_rejects_non_mapping(self) -> None:
    with pytest.raises(ValueError, match="mapping"):
      load_pylint_json("[]")

  def test_rejects_missing_keys(self) -> None:
    with pytest.raises(ValueError, match="required keys"):
      load_pylint_json("{}")


class TestSummarizePylintReport:
  """Tests for compact pylint summaries."""

  def test_counts_symbols_paths_and_score(self) -> None:
    summary = summarize_pylint_report(_sample_report())

    assert summary["score"] == pytest.approx(9.7)
    assert summary["message_count"] == 3
    assert summary["symbol_counts"]["missing-function-docstring"] == 1
    assert summary["path_counts"]["supekku/tui/app.py"] == 2

  def test_sorts_messages_by_severity_then_location(self) -> None:
    summary = summarize_pylint_report(_sample_report())
    first = summary["messages"][0]

    assert first["symbol"] == "broad-exception-caught"
    assert first["path"] == "supekku/tui/app.py"


class TestRenderPylintSummary:
  """Tests for human-readable pylint summaries."""

  def test_renders_key_sections(self) -> None:
    summary = summarize_pylint_report(_sample_report())

    rendered = render_pylint_summary(
      summary,
      targets=["supekku"],
      json_path=None,
      top_n=2,
    )

    assert "Targets: supekku" in rendered
    assert "Score: 9.70/10" in rendered
    assert "Top message symbols:" in rendered
    assert "Files with most messages:" in rendered
    assert "First messages by severity:" in rendered
    assert "broad-exception-caught" in rendered

  def test_includes_json_path_when_present(self) -> None:
    """Rendered summary includes the persisted json path."""
    summary = summarize_pylint_report(_sample_report())

    rendered = render_pylint_summary(
      summary,
      targets=["supekku"],
      json_path=Path("/tmp/pylint.json"),
      top_n=2,
    )

    assert "Full JSON: /tmp/pylint.json" in rendered
