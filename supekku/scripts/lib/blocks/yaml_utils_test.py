"""Tests for blocks yaml_utils."""

from __future__ import annotations

from supekku.scripts.lib.blocks.yaml_utils import make_block_pattern


class TestMakeBlockPattern:
  """Tests for make_block_pattern."""

  MARKER = "supekku:test.marker@v1"

  def test_matches_yaml_fenced_block(self):
    text = f"```yaml {self.MARKER}\nkey: value\n```"
    m = make_block_pattern(self.MARKER).search(text)
    assert m is not None
    assert m.group(1) == "key: value\n"

  def test_matches_yml_fenced_block(self):
    text = f"```yml {self.MARKER}\nkey: value\n```"
    m = make_block_pattern(self.MARKER).search(text)
    assert m is not None

  def test_does_not_match_wrong_marker(self):
    text = "```yaml supekku:other.marker@v1\nkey: value\n```"
    assert make_block_pattern(self.MARKER).search(text) is None

  def test_captures_multiline_body(self):
    body = "a: 1\nb: 2\nc: 3\n"
    text = f"```yaml {self.MARKER}\n{body}```"
    m = make_block_pattern(self.MARKER).search(text)
    assert m is not None
    assert m.group(1) == body

  def test_special_chars_in_marker_are_escaped(self):
    marker = "supekku:spec.relationships@v1"
    text = f"```yaml {marker}\ndata: x\n```"
    m = make_block_pattern(marker).search(text)
    assert m is not None
    assert m.group(1) == "data: x\n"

  def test_different_markers_return_different_patterns(self):
    m1 = make_block_pattern("marker-a")
    m2 = make_block_pattern("marker-b")
    assert m1.pattern != m2.pattern
