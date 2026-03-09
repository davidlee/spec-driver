# supekku.scripts.lib.diagnostics.checks.config

Configuration validity checks.

Validates workflow.toml, CLAUDE.md, skills allowlist, and agent
skill exposure.

## Constants

- `CATEGORY`

## Functions

- `_check_agents_dir(sd_root) -> DiagnosticResult`
- `_check_claude_md(root) -> DiagnosticResult`
- `_check_skills_allowlist(sd_root) -> DiagnosticResult`
- `_check_skills_exposure(root, sd_root) -> list[DiagnosticResult]`: Check skill symlinks for each agent target.
- `_check_version_staleness(sd_root) -> DiagnosticResult`: Warn when workflow.toml version stamp differs from the running package.
- `_check_workflow_toml(sd_root) -> DiagnosticResult`
- `check_config(ws) -> list[DiagnosticResult]`: Check configuration files and skills exposure.
