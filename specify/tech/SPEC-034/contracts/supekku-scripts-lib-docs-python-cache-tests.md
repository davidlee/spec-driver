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
- `__init__(self, cache_dir) -> None`: Initialize cache with optional custom directory.
- `_get_cache_file(self, file_path) -> Path`: Get cache file path for given source file.
- `_get_cache_key(self, file_path) -> str`: Generate stable cache key for file.
- `_get_file_info(self, file_path) -> tuple[Tuple[float, str]]`: Get file modification time and content hash.
