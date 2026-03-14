# DE-032 Implementation Brief (for Opus)

## Goal

Make OpenSkills-based distribution compatible with conditional, config-driven exposure to agents.

- OpenSkills universal install: `.agent/skills/<skill>/SKILL.md` exists but is not agent-discoverable by default.
- Agent discovery happens via the `<skills_system>` XML block in `AGENTS.md`.

This delta adds `spec-driver skills sync` which:

- reads `.spec-driver/skills.allowlist`
- reads project skill metadata from `.agent/skills/*/SKILL.md` frontmatter
- rewrites only the `AGENTS.md` skills table region (between `SKILLS_TABLE_START/END`)
- preserves any existing `<location>global</location>` entries

## File contracts

- Allowlist: `.spec-driver/skills.allowlist` (one skill name per line, `#` comments allowed)
- Skill cache: `.agent/skills/<name>/SKILL.md` (frontmatter has `description`)
- Output: `AGENTS.md` (skills table region)

## Notes on format (pinned)

Reference format captured from `/tmp/pooper/AGENTS.md`:

- `<!-- SKILLS_TABLE_START -->` / `<!-- SKILLS_TABLE_END -->` markers
- `<available_skills>` with repeated `<skill>` blocks:
  - `<name>folder-name</name>`
  - `<description>from SKILL frontmatter</description>`
  - `<location>project|global</location>`

## Bugfix: multiline YAML frontmatter in SKILL.md (2026-03-03)

`read_skill_metadata()` used a naive line-by-line `key: value` parser that
failed on two categories of SKILL.md frontmatter:

1. **Multiline block scalars** (`|` / `>`): stored the literal `|` character
   as the description. Affected: `capturing-memory`, `maintaining-memory`,
   `retrieving-memory`, `reviewing-memory`.
2. **Unquoted values containing `: `**: `yaml.safe_load` rejects these as
   ambiguous mappings. Affected: `preflight` (`... something new: understand ...`).

**Fix**: try `yaml.safe_load` first (handles multiline blocks correctly),
fall back to naive first-colon-split parser (handles unquoted colons).
Multiline descriptions are collapsed to a single line for the XML output.

Extracted `_extract_frontmatter_lines()` and `_parse_frontmatter_naive()` helpers
to keep return-statement count under pylint threshold.

Added 3 test cases: `test_read_skill_metadata_unquoted_colon_in_value`,
`test_read_skill_metadata_multiline_literal`, `test_read_skill_metadata_multiline_folded`.

## Suggested test strategy

- Create temp repo with:
  - `.agent/skills/template/SKILL.md` (frontmatter description)
  - `.spec-driver/skills.allowlist` containing `template`
  - `AGENTS.md` containing a global skill entry
- Run `skills sync` and assert:
  - allowlisted project skill appears
  - global skill preserved
  - second run yields no diff
