# supekku.cli.skills_test

Tests for skills CLI commands.

## Constants

- `runner`

## Functions

- `_make_skill(skills_dir, name, description) -> None`: Helper to create a SKILL.md with frontmatter.
- `_setup_repo(tmp_path) -> tuple[Tuple[Path, Path]]`: Create minimal repo for skills sync.

Returns (repo_root, skills_source_dir).

- `test_skills_sync_idempotent(tmp_path) -> None`: Second run reports up to date.
- `test_skills_sync_reports_symlink_status(tmp_path) -> None`: CLI reports per-target symlink outcomes.
- `test_skills_sync_warns_missing(tmp_path) -> None`: Warns about missing allowlisted skills.
- `test_skills_sync_writes_output(tmp_path) -> None`: CLI reports skills written to AGENTS.md.
