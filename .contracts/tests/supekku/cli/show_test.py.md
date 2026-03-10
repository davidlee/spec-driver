# supekku.cli.show_test

Tests for show CLI commands.

## Classes

### ShowBacklogTest

Integration tests for show backlog subcommand (DE-088 / ISSUE-045).

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `test_show_backlog_improvement(self) -> None`: show backlog IMPR-001 resolves an improvement.
- `test_show_backlog_in_help(self) -> None`: backlog subcommand appears in show help.
- `test_show_backlog_issue(self) -> None`: show backlog ISSUE-004 resolves an issue.
- `test_show_backlog_json_flag(self) -> None`: show backlog --json returns valid JSON.
- `test_show_backlog_not_found(self) -> None`: show backlog with nonexistent ID fails gracefully.
- `test_show_backlog_path_flag(self) -> None`: show backlog --path returns the file path.
- `test_show_backlog_problem(self) -> None`: show backlog PROB-002 resolves a problem.
- `test_show_backlog_raw_flag(self) -> None`: show backlog --raw returns raw file content.

### ShowBareNumericIdTest

Tests for bare numeric ID normalisation (DE-088 / ISSUE-045).

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `test_show_audit_bare_number(self) -> None`: show audit 1 resolves to AUD-001.
- `test_show_improvement_bare_number(self) -> None`: show improvement 1 resolves to IMPR-001.
- `test_show_issue_bare_number(self) -> None`: show issue 4 resolves to ISSUE-004.
- `test_show_issue_not_found_bare_number(self) -> None`: show issue 999 with nonexistent ID fails gracefully.
- `test_show_issue_zero_padded(self) -> None`: show issue 004 resolves to ISSUE-004.
- `test_show_plan_bare_number(self) -> None`: show plan 41 resolves to IP-041.
- `test_show_problem_bare_number(self) -> None`: show problem 2 resolves to PROB-002.

### ShowCardJsonFlagTest

Test cases for --json flag on show card command.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test environment.
- `test_show_card_json_flag(self) -> None`: Test --json flag on show card.
- `test_show_card_path_flag_alias(self) -> None`: Test -q alias still works for --path flag.

### ShowContentTypeFlagTest

Tests for --content-type/-c flag on show subcommands.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `test_content_type_in_help(self) -> None`: --content-type/-c flag appears in help.
- `test_content_type_overrides_raw_with_warning(self) -> None`: --content-type overrides --raw with a warning.
- `test_show_adr_content_type_markdown(self) -> None`: show adr -c markdown outputs full file content.
- `test_show_delta_content_type_frontmatter(self) -> None`: show delta -c frontmatter outputs formatted metadata.
- `test_show_delta_content_type_markdown(self) -> None`: show delta -c markdown outputs full file content.
- `test_show_delta_content_type_yaml(self) -> None`: show delta -c yaml outputs only YAML frontmatter.
- `test_show_revision_content_type_markdown(self) -> None`: show revision -c markdown via emit_artifact path.
- `test_show_spec_content_type_yaml(self) -> None`: show spec -c yaml outputs YAML frontmatter.

### ShowDeltaCommandTest

Test cases for show delta CLI command.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test environment.
- `test_show_delta_json_flag_in_help(self) -> None`: Test that --json flag is documented in help.
- `test_show_delta_json_includes_applies_to(self) -> None`: Test that JSON output includes applies_to with specs and requirements.
- `test_show_delta_json_includes_other_files(self) -> None`: Test that JSON output includes other files in delta bundle.
- `test_show_delta_json_includes_plan_paths(self) -> None`: Test that JSON output includes plan and phase file paths.
- `test_show_delta_json_includes_task_completion(self) -> None`: Test that JSON output includes task completion stats for phases.
- `test_show_delta_json_output(self) -> None`: Test showing delta in JSON format.
- `test_show_delta_not_found(self) -> None`: Test error when delta ID does not exist.
- `test_show_delta_text_includes_task_completion(self) -> None`: Test that text output includes task completion stats for phases.
- `test_show_delta_text_output(self) -> None`: Test showing delta in text format (default).

### ShowInferredTest

Integration tests for show with bare ID inference (InferringGroup).

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `test_bare_adr_id_resolves(self) -> None`: show ADR-001 resolves without specifying 'adr'.
- `test_bare_id_with_path_flag(self) -> None`: show DE-063 --path returns the file path.
- `test_bare_id_with_raw_flag(self) -> None`: show DE-063 --raw returns raw file content.
- `test_bare_prefixed_id_resolves(self) -> None`: show DE-063 resolves without specifying 'delta'.
- `test_existing_subcommand_passthrough(self) -> None`: Existing show <type> <id> still works.
- `test_hidden_command_not_in_help(self) -> None`: The 'inferred' command does not appear in --help output.
- `test_no_args_shows_help(self) -> None`: show with no arguments prints help.
- `test_numeric_id_resolves(self) -> None`: show 63 resolves to DE-063 (or disambiguates).
- `test_unknown_id_gives_error(self) -> None`: show NONEXISTENT-999 gives clear error.

### ShowNewSubcommandsTest

Integration tests for Phase 2 show subcommands.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `test_show_audit_default(self) -> None`
- `test_show_audit_not_found(self) -> None`
- `test_show_improvement_default(self) -> None`
- `test_show_improvement_not_found(self) -> None`
- `test_show_issue_default(self) -> None`
- `test_show_issue_not_found(self) -> None`
- `test_show_plan_default(self) -> None`
- `test_show_plan_not_found(self) -> None`
- `test_show_plan_path(self) -> None`
- `test_show_problem_default(self) -> None`

### ShowPathFlagTest

Test cases for --path flag on show commands.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test environment.
- `test_path_and_json_mutually_exclusive(self) -> None`: Test that --path and --json are mutually exclusive.
- `test_show_adr_path_flag(self) -> None`: Test --path flag on show adr. - Single line
- `test_show_delta_path_flag(self) -> None`: Test --path flag returns only the path.
- `test_show_spec_path_flag(self) -> None`: Test --path flag on show spec.

### ShowRawFlagTest

Test cases for --raw flag on show commands.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test environment.
- `test_all_three_flags_mutually_exclusive(self) -> None`: Test that --raw, --json, and --path together fail.
- `test_raw_and_json_mutually_exclusive(self) -> None`: Test that --raw and --json are mutually exclusive.
- `test_raw_and_path_mutually_exclusive(self) -> None`: Test that --raw and --path are mutually exclusive.
- `test_show_adr_raw_flag(self) -> None`: Test --raw flag on show adr.
- `test_show_delta_raw_flag(self) -> None`: Test --raw flag outputs raw file content.
- `test_show_raw_flag_in_help(self) -> None`: Test that --raw flag is documented in help.
- `test_show_spec_raw_flag(self) -> None`: Test --raw flag on show spec.

### ShowRevisionRegressionTest

Regression tests for show revision — must pass before AND after migration.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `test_show_revision_default(self) -> None`: show revision RE-001 outputs formatted details.
- `test_show_revision_json(self) -> None`: show revision --json outputs valid JSON with expected fields. - frontmatter
- `test_show_revision_mutual_exclusivity(self) -> None`: show revision --json --path fails with mutual exclusivity error.
- `test_show_revision_not_found(self) -> None`: show revision with nonexistent ID fails gracefully.
- `test_show_revision_numeric_shorthand(self) -> None`: show revision 1 resolves to RE-001.
- `test_show_revision_path(self) -> None`: show revision --path outputs file path.
- `test_show_revision_raw(self) -> None`: show revision --raw outputs raw file content.

### ShowTemplateCommandTest

Test cases for show template CLI command.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test environment.
- `test_show_template_contains_all_sections(self) -> None`: Test that template contains all expected sections.
- `test_show_template_contains_requirements_format(self) -> None`: Test that template shows proper requirements format.
- `test_show_template_has_no_empty_yaml_blocks(self) -> None`: Test that YAML block placeholders are empty (not filled).
- `test_show_template_invalid_kind(self) -> None`: Test that invalid kind produces error.
- `test_show_template_json_output_product(self) -> None`: Test JSON output format for product template.
- `test_show_template_json_output_tech(self) -> None`: Test JSON output format for tech template.
- `test_show_template_product(self) -> None`: Test showing product specification template.
- `test_show_template_tech(self) -> None`: Test showing tech specification template.
