# supekku.scripts.lib.skills.sync_test

Tests for skills install: allowlist, metadata, rendering, prune, symlinks.

## Constants

- `AGENTS_MD_REF`
- `BOOT_MD_REF`

## Functions

- `_make_post_migration(root) -> None`: Post-migration workspace: version stamp present in workflow.toml.
- `_make_pre_migration(root) -> None`: Pre-migration workspace: no version stamp in workflow.toml.
- `_make_skill(skills_dir, name, description) -> None`: Helper to create a SKILL.md with frontmatter.
- `_make_source(tmp_path) -> Path`: Create a package-like skills source directory.
- `_setup_canonical(root) -> Path`: Create canonical skills dir with named skill subdirs.
- `_setup_repo(tmp_path) -> tuple[Tuple[Path, Path]]`: Create a minimal repo with skills source and allowlist.

Returns (repo_root, skills_source_dir).
Post-migration layout: specify/tech is a symlink (not a real dir).

- `_setup_repo_with_config(tmp_path) -> tuple[Tuple[Path, Path]]`: Create repo with workflow.toml integration config.
- `test_config_agents_md_false_skips_reference(tmp_path) -> None`: When integration.agents_md is false, root AGENTS.md is not touched.
- `test_config_claude_md_false_skips_reference(tmp_path) -> None`: When integration.claude_md is false, root CLAUDE.md is not touched.
- `test_config_defaults_enable_both_agents_and_claude_md(tmp_path) -> None`: Without config, both AGENTS.md and CLAUDE.md get references.
- `test_ensure_file_reference_creates_file(tmp_path) -> None`: Creates file with @-reference when it does not exist.
- `test_ensure_file_reference_idempotent(tmp_path) -> None`: Does not duplicate @-reference on repeated calls.
- `test_ensure_file_reference_prepends(tmp_path) -> None`: Prepends @-reference before existing content.
- `test_ensure_symlinks_creates_per_skill(tmp_path) -> None`: Creates per-skill symlinks when target dir is empty.
- `test_ensure_symlinks_custom_post_migration_real_dir(tmp_path) -> None`: Reports 'custom' for real skill dir in post-migration workspace.
- `test_ensure_symlinks_custom_when_wrong_symlink(tmp_path) -> None`: Reports 'custom' when per-skill symlink points elsewhere.
- `test_ensure_symlinks_idempotent(tmp_path) -> None`: Second call returns all 'ok' after initial creation.
- `test_ensure_symlinks_migrates_pre_migration(tmp_path) -> None`: Replaces real skill dirs with symlinks in pre-migration workspace.
- `test_ensure_symlinks_ok_when_correct(tmp_path) -> None`: Reports 'ok' when per-skill symlinks already point correctly.
- `test_ensure_symlinks_preserves_user_skills(tmp_path) -> None`: User-created skills in target dir are untouched.
- `test_get_package_skill_names_empty_dir(tmp_path) -> None`: Returns empty set for non-existent directory.
- `test_get_package_skill_names_ignores_empty_skill_md(tmp_path) -> None`: Ignores dirs where SKILL.md is empty (0 bytes).
- `test_get_package_skill_names_ignores_non_dirs(tmp_path) -> None`: Ignores regular files at top level of source dir.
- `test_get_package_skill_names_valid(tmp_path) -> None`: Returns names of dirs containing non-empty SKILL.md.
- `test_install_skills_to_target_copies(tmp_path) -> None`: Installs allowlisted skills to target dir.
- `test_install_skills_to_target_creates_dir(tmp_path) -> None`: Creates target directory if it doesn't exist.
- `test_install_skills_to_target_idempotent(tmp_path) -> None`: Second run reports up_to_date, not installed.
- `test_install_skills_to_target_skips_missing_source(tmp_path) -> None`: Silently skips skills not in source directory.
- `test_install_skills_to_target_updates_changed(tmp_path) -> None`: Re-installs when source SKILL.md has changed.
- `test_parse_allowlist_basic(tmp_path) -> None`: Reads one skill name per line.
- `test_parse_allowlist_comments_and_blanks(tmp_path) -> None`: Skips comment lines and blank lines.
- `test_parse_allowlist_missing_file(tmp_path) -> None`: Returns empty list when allowlist file does not exist.
- `test_parse_allowlist_strips_whitespace(tmp_path) -> None`: Strips leading/trailing whitespace from skill names.
- `test_pre_migration_layout_no_toml(tmp_path) -> None`: Returns True when workflow.toml does not exist.
- `test_pre_migration_layout_no_version_stamp(tmp_path) -> None`: Returns True when workflow.toml has no version stamp.
- `test_pre_migration_layout_with_version_stamp(tmp_path) -> None`: Returns False when workflow.toml has version stamp.
- `test_prune_ignores_user_skills(tmp_path) -> None`: Does not remove skills that aren't in the package.
- `test_prune_nonexistent_target_dir(tmp_path) -> None`: Returns empty list for non-existent target directory.
- `test_prune_noop_when_all_allowed(tmp_path) -> None`: No pruning when all package skills are in the allowlist.
- `test_prune_removes_delisted_package_skills(tmp_path) -> None`: Removes package skills that are no longer allowlisted.
- `test_read_skill_metadata(tmp_path) -> None`: Reads name and description from SKILL.md frontmatter.
- `test_read_skill_metadata_missing_file(tmp_path) -> None`: Returns None for missing SKILL.md.
- `test_read_skill_metadata_multiline_folded(tmp_path) -> None`: Handles YAML folded block (>) multiline descriptions.
- `test_read_skill_metadata_multiline_literal(tmp_path) -> None`: Handles YAML literal block (|) multiline descriptions.
- `test_read_skill_metadata_no_frontmatter(tmp_path) -> None`: Returns None when SKILL.md has no YAML frontmatter.
- `test_read_skill_metadata_unquoted_colon_in_value(tmp_path) -> None`: Handles description values containing colons (invalid strict YAML).
- `test_render_skills_system_basic() -> None`: Renders a complete skills_system XML block.
- `test_render_skills_system_empty() -> None`: Renders valid block even with no skills.
- `test_render_skills_system_is_deterministic() -> None`: Same input produces identical output.
- `test_skill_dir_matches_different(tmp_path) -> None`: Returns False when SKILL.md content differs.
- `test_skill_dir_matches_identical(tmp_path) -> None`: Returns True when SKILL.md content matches.
- `test_skill_dir_matches_missing_dest(tmp_path) -> None`: Returns False when destination SKILL.md doesn't exist.
- `test_sync_skills_creates_claude_md_by_default(tmp_path) -> None`: By default, CLAUDE.md is created with the boot reference.
- `test_sync_skills_creates_target_symlinks(tmp_path) -> None`: sync_skills creates per-skill symlinks in agent target dirs.
- `test_sync_skills_ensures_root_agents_reference(tmp_path) -> None`: sync_skills ensures root AGENTS.md has skills and boot references.
- `test_sync_skills_idempotent(tmp_path) -> None`: Running sync twice produces identical output.
- `test_sync_skills_installs_to_canonical(tmp_path) -> None`: sync_skills installs skills to .spec-driver/skills/.
- `test_sync_skills_no_allowlist(tmp_path) -> None`: When allowlist is missing, writes empty skills block.
- `test_sync_skills_prunes_from_canonical(tmp_path) -> None`: sync_skills prunes de-listed skills from canonical dir.
- `test_sync_skills_respects_target_config(tmp_path) -> None`: Only installs to targets listed in workflow.toml [skills] section.
- `test_sync_skills_unknown_target_warns(tmp_path) -> None`: Unknown target name emits a warning and is skipped.
- `test_sync_skills_warns_on_missing_skill(tmp_path) -> None`: Warns when allowlisted skill is not in source.
- `test_sync_skills_writes_agents_md(tmp_path) -> None`: sync_skills writes .spec-driver/AGENTS.md with allowlisted skills only.
- `test_sync_skills_writes_claude_md_when_opted_in(tmp_path) -> None`: When integration.claude_md is true, CLAUDE.md gets the boot reference.
