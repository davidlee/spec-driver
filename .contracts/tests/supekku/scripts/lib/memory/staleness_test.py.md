# supekku.scripts.lib.memory.staleness_test

Tests for memory staleness computation.

## Functions

- `_make_record(memory_id, verified, verified_sha, scope_paths, scope_globs, updated) -> MemoryRecord`: Build a minimal MemoryRecord for staleness tests.

## Classes

### TestComputeBatchStaleness

Tests for batched staleness computation.

#### Methods

- `test_empty_records(self) -> None`
- `test_git_failure_degrades_gracefully(self) -> None`: When git fails, scoped+attested memories degrade to days_since.
- `test_glob_scope_included(self) -> None`: Memories with only scope.globs are treated as scoped.
- `test_multiple_records_single_git_call(self) -> None`: Multiple scoped+attested records use a single git invocation.
- `test_no_attested_records_skips_git(self) -> None`: When no records are attested, git is not called.
- `test_scoped_attested_counts_commits(self) -> None`: Scoped+attested memory counts commits from git log.
- `test_scoped_unattested_has_no_commits_since(self) -> None`: Scoped but unattested memory has commits_since=None.
- `test_unscoped_memory_uses_days_since(self) -> None`: Unscoped memory falls back to days_since from verified date.
- `test_unscoped_uses_updated_when_no_verified(self) -> None`: Unscoped memory without verified date uses updated.

### TestGlobToPathspec

Tests for glob-to-pathspec conversion.

#### Methods

- `test_passes_through_plain_path(self) -> None`
- `test_passes_through_simple_glob(self) -> None`
- `test_strips_leading_dot_slash(self) -> None`
- `test_strips_trailing_double_star(self) -> None`
- `test_strips_trailing_slash_double_star(self) -> None`

### TestStalenessInfo

Tests for StalenessInfo dataclass.

#### Methods

- `test_scoped_attested(self) -> None`
- `test_scoped_unattested(self) -> None`
- `test_unscoped(self) -> None`
