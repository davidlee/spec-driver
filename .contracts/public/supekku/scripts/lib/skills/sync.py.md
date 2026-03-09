# supekku.scripts.lib.skills.sync

Allowlist-driven skills install: install, prune, and expose skills in AGENTS.md.

Reads `.spec-driver/skills.allowlist`, installs allowlisted skills from the
package source (`supekku/skills/`) to `.spec-driver/skills/` (the canonical
workspace copy), then ensures agent target dirs (`.claude/skills/`,
`.agents/skills/`) are dir-level symlinks to the canonical location.

Prunes de-listed skills from the canonical dir only.  Writes a
`<skills_system>` block to `.spec-driver/AGENTS.md`.

Root `AGENTS.md` and `CLAUDE.md` are updated with `@`-references to the
managed file, controlled by `[integration]` in `workflow.toml`.

## Constants

- `AGENTS_MD_REFERENCE`
- `ALLOWLIST_FILE`
- `BOOT_MD_REFERENCE`
- `CANONICAL_SKILLS_DIR` - Canonical install location (relative to repo root)
- `MANAGED_AGENTS_FILE`
- `USAGE_BLOCK`

## Functions

- `ensure_file_reference(file_path, reference) -> None`: Ensure a file exists and contains an @-reference line.

Creates the file if missing. Prepends the reference before existing
content if not already present. Idempotent.
- `get_package_skill_names(skills_source_dir) -> set[str]`: List valid skill names in the package source directory.

A valid skill is a subdirectory containing a non-empty SKILL.md.
- `install_skills_to_target(skills_source_dir, target_dir, allowed_names) -> dict[Tuple[str, list[str]]]`: Copy allowlisted skills from package source to a target directory.

Idempotent: skips skills whose SKILL.md already matches the source.
Creates target_dir if it doesn't exist.

Returns dict with 'installed' and 'up_to_date' lists of skill names.
- `parse_allowlist(path) -> list[str]`: Parse a skills allowlist file.

Returns skill names in file order. Skips blank lines and `#` comments.
Returns an empty list if the file does not exist.
- `prune_skills_from_target(target_dir, package_skill_names, allowed_names) -> list[str]`: Remove de-listed package skills from a target directory.

Only prunes skills that exist in the package (by name) but are NOT
in the allowlist. User-created skills (not in package) are never touched.

Returns list of pruned skill names.
- `read_skill_metadata(skill_md_path) -> <BinOp>`: Read name and description from SKILL.md YAML frontmatter.

Returns a dict with `name` and `description` keys, or None if the
file is missing or has no parseable frontmatter.
- `render_skills_system(skills) -> str`: Render a complete `<skills_system>` XML block for AGENTS.md.

Each skill dict must have `name` and `description` keys.
All skills are rendered with `<location>project</location>`.
- `sync_skills(repo_root) -> dict`: Sync skills from package source to canonical dir and update AGENTS.md.

Installs allowlisted skills to ``.spec-driver/skills/`` (once), prunes
de-listed skills (once), then ensures each agent target dir is a
symlink to the canonical location.  Writes the AGENTS.md skills block.

Args:
  repo_root: Workspace root path.
  skills_source_dir: Override package skills dir (for testing).

Returns a summary dict with keys:
  written: number of skills in AGENTS.md
  warnings: list of missing skill names
  agents_md_changed: whether .spec-driver/AGENTS.md was modified
  canonical: install/prune summary for .spec-driver/skills/
  symlinks: per-target symlink outcome
