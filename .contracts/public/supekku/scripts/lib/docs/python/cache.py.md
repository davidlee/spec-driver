# supekku.scripts.lib.docs.python.cache

File-based caching for AST parsing with mtime and hash validation.

## Classes

### ParseCache

File-based caching for AST parsing with mtime and hash validation.

#### Methods

- `clear(self) -> None`: Clear all cached data.
- `get(self, file_path) -> <BinOp>`: Get cached analysis if valid, None otherwise.
- `get_stats(self) -> dict[Tuple[str, int]]`: Get cache performance statistics.
- `put(self, file_path, analysis) -> None`: Store analysis in cache with metadata.
