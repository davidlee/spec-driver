"""Comment extraction from Python source code."""


class CommentExtractor:
  """Extract comments from Python source code."""

  def __init__(self, source_code: str) -> None:
    self.lines = source_code.splitlines()
    self.comments = self._extract_comments()

  def _extract_comments(self) -> dict[int, str]:
    """Extract comments mapped by line number."""
    comments = {}

    for i, line in enumerate(self.lines, 1):
      stripped = line.strip()

      if stripped.startswith("#") and not stripped.startswith("#!/"):
        comment = stripped[1:].strip()
        comments[i] = comment
      elif "#" in line and not stripped.startswith("#"):
        # Handle inline comments - find the rightmost # that's outside quotes
        comment_pos = self._find_comment_start(line)
        if comment_pos is not None:
          comment = line[comment_pos + 1 :].strip()
          if comment:  # Only store non-empty comments
            comments[i] = comment
    return comments

  def _find_comment_start(self, line: str) -> int | None:
    """Find the position of # that starts a comment (not inside quotes)."""
    in_single_quote = False
    in_double_quote = False
    escaped = False

    for i, char in enumerate(line):
      if escaped:
        escaped = False
        continue

      if char == "\\":
        escaped = True
        continue

      if char == "'" and not in_double_quote:
        in_single_quote = not in_single_quote
      elif char == '"' and not in_single_quote:
        in_double_quote = not in_double_quote
      elif char == "#" and not in_single_quote and not in_double_quote:
        return i

    return None

  def get_comment_for_line(self, line_num: int, context: int = 2) -> str | None:
    """Get comment for a specific line, checking nearby lines."""
    if line_num in self.comments:
      return self.comments[line_num]

    for i in range(1, context + 1):
      if (line_num - i) in self.comments:
        return self.comments[line_num - i]

    return None
