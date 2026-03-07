"""VT-053-tcss-lint — scan theme.tcss for colour literals (POL-002)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

TCSS_PATH = Path(__file__).parent / "theme.tcss"

# Patterns that indicate colour literals in .tcss
_HEX_PATTERN = re.compile(r"#[0-9a-fA-F]{3,8}\b")
_RGB_PATTERN = re.compile(r"rgba?\s*\(")


class TestTcssNoColourLiterals:
  """POL-002: no hex/rgb colour literals in theme.tcss."""

  @pytest.fixture()
  def tcss_content(self) -> str:
    return TCSS_PATH.read_text(encoding="utf-8")

  def test_tcss_exists(self):
    assert TCSS_PATH.exists(), f"theme.tcss not found at {TCSS_PATH}"

  def test_no_hex_colours(self, tcss_content: str):
    for i, line in enumerate(tcss_content.splitlines(), 1):
      stripped = line.split("/*")[0]  # ignore comments
      match = _HEX_PATTERN.search(stripped)
      assert match is None, f"Hex colour literal at line {i}: {match.group()!r}"

  def test_no_rgb_colours(self, tcss_content: str):
    for i, line in enumerate(tcss_content.splitlines(), 1):
      stripped = line.split("/*")[0]
      match = _RGB_PATTERN.search(stripped)
      assert match is None, f"RGB colour literal at line {i}: {match.group()!r}"
