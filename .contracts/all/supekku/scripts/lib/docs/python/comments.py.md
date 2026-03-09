# supekku.scripts.lib.docs.python.comments

Comment extraction from Python source code.

## Classes

### CommentExtractor

Extract comments from Python source code.

#### Methods

- `get_comment_for_line(self, line_num, context) -> <BinOp>`: Get comment for a specific line, checking nearby lines.
- `__init__(self, source_code) -> None`
- `_extract_comments(self) -> dict[Tuple[int, str]]`: Extract comments mapped by line number.
- `_find_comment_start(self, line) -> <BinOp>`: Find the position of # that starts a comment (not inside quotes).
