# supekku.cli.resolve_test

Tests for resolve CLI commands.

VT-073-03: resolve links --verbose/--path/--id.

## Constants

- `runner`

## Functions

- `_init_repo(tmp_path) -> Path`: Initialize minimal repo structure for testing.

Creates .spec-driver dir so find_repo_root succeeds,
and memory/ for mem files. Returns memory dir.
- `_write_memory(mem_dir, mem_id, name, body, memory_type) -> None`: Write a minimal memory file to disk.

## Classes

### TestBuildArtifactIndex

Tests for build_artifact_index.

#### Methods

- `test_empty_repo(self, tmp_path) -> None`: Index is empty for a repo with no artifacts.
- `test_includes_backlog_items(self, tmp_path) -> None`: Index includes backlog items from BacklogRegistry. - -- VT-057-link-resolver --
- `test_includes_memory_records(self, tmp_path) -> None`: Index includes memory records from registry.
- `test_includes_multiple_backlog_kinds(self, tmp_path) -> None`: Index includes issues, problems, improvements, risks.
- `test_unknown_backlog_id_not_in_index(self, tmp_path) -> None`: Unknown backlog IDs are not in the index.

### TestMissingDetail

_resolve_memory_links tracks missing targets per source file.

#### Methods

- `test_no_missing_detail_when_all_resolved(self, tmp_path) -> None`
- `test_tracks_missing_targets_with_sources(self, tmp_path) -> None`: missing_detail maps target → list of source file paths.

### TestResolveLinksById

CLI --id flag scopes resolution to a single memory record.

#### Methods

- `test_id_and_path_mutually_exclusive(self, tmp_path, monkeypatch) -> None`
- `test_id_not_found(self, tmp_path, monkeypatch) -> None`
- `test_id_scopes_to_one_record(self, tmp_path, monkeypatch) -> None`

### TestResolveLinksVerbose

CLI --verbose flag reports missing targets with file locations.

#### Methods

- `test_no_verbose_hides_detail(self, tmp_path, monkeypatch) -> None`
- `test_verbose_shows_missing_targets(self, tmp_path, monkeypatch) -> None`

### TestResolveMemoryLinks

Tests for _resolve_memory_links.

#### Methods

- `test_clears_stale_links(self, tmp_path) -> None`: Links removed when body no longer contains them.
- `test_default_mode_omits_out(self, tmp_path) -> None`: Default mode (missing) omits resolved links from frontmatter.
- `test_dry_run_skips_writes(self, tmp_path) -> None`: Dry-run does not modify files.
- `test_missing_targets_tracked(self, tmp_path) -> None`: Missing targets counted in stats.
- `test_no_op_empty_directory(self, tmp_path) -> None`: No-op when memory directory is empty.
- `test_no_op_missing_directory(self, tmp_path) -> None`: No-op when memory directory doesn't exist.
- `test_resolves_and_writes_frontmatter(self, tmp_path) -> None`: Resolution writes full links to frontmatter in full mode.

### TestScopePath

_resolve_memory_links with scope_path resolves a single file.

#### Methods

- `test_scoped_dry_run(self, tmp_path) -> None`
- `test_scoped_processes_one_file(self, tmp_path) -> None`
