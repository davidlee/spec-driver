"""Tests for core spec_utils helpers."""

from __future__ import annotations

from supekku.scripts.lib.core.spec_utils import extract_h1_title


class TestExtractH1Title:
  """Tests for extract_h1_title."""

  def test_matches_prefixed_h1(self):
    content = "---\nfrontmatter: yes\n---\n# ADR-001 My Decision\nBody text."
    assert extract_h1_title(content, "ADR-") == "# ADR-001 My Decision"

  def test_no_prefix_matches_any_h1(self):
    content = "# Some Title\nBody."
    assert extract_h1_title(content) == "# Some Title"

  def test_returns_empty_string_when_not_found(self):
    content = "No heading here.\nJust text."
    assert extract_h1_title(content, "ADR-") == ""

  def test_returns_empty_string_on_empty_content(self):
    assert extract_h1_title("", "ADR-") == ""

  def test_ignores_h2_and_deeper(self):
    content = "## Not H1\n### Also not\n# ADR-005 Found\n"
    assert extract_h1_title(content, "ADR-") == "# ADR-005 Found"

  def test_returns_first_match_when_multiple_headings(self):
    content = "# ADR-001 First\n# ADR-002 Second\n"
    assert extract_h1_title(content, "ADR-") == "# ADR-001 First"

  def test_prefix_mismatch_returns_empty(self):
    content = "# POL-001 A Policy\n"
    assert extract_h1_title(content, "ADR-") == ""

  def test_no_prefix_with_multiple_headings_returns_first(self):
    content = "# First\n# Second\n"
    assert extract_h1_title(content) == "# First"
