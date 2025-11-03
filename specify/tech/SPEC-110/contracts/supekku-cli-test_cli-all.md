# supekku.cli.test_cli

Comprehensive test suite for unified CLI.

## Constants

- `runner`

## Classes

### TestCommandStructure

Test command structure follows verb-noun pattern.

#### Methods

- `test_complete_follows_verb_noun(self)`: Test complete commands follow verb-noun pattern.
- `test_create_follows_verb_noun(self)`: Test create commands follow verb-noun pattern.
- `test_list_follows_verb_noun(self)`: Test list commands follow verb-noun pattern.
- `test_show_follows_verb_noun(self)`: Test show commands follow verb-noun pattern.

### TestCommonOptions

Test common options across commands.

#### Methods

- `test_root_option_in_list_specs(self)`: Test --root option is available.
- `test_root_option_in_validate(self)`: Test --root option is available.

### TestCompleteCommands

Test complete command group.

#### Methods

- `test_complete_delta_help(self)`: Test complete delta command help.
- `test_complete_help(self)`: Test complete command group help.

### TestCreateCommands

Test create command group.

#### Methods

- `test_create_adr_help(self)`: Test create adr command help.
- `test_create_delta_help(self)`: Test create delta command help.
- `test_create_help(self)`: Test create command group help.
- `test_create_requirement_help(self)`: Test create requirement command help.
- `test_create_revision_help(self)`: Test create revision command help.
- `test_create_spec_help(self)`: Test create spec command help.

### TestErrorHandling

Test error handling in CLI commands.

#### Methods

- `test_invalid_command(self)`: Test invalid command returns error.
- `test_missing_required_argument(self)`: Test missing required argument returns error.

### TestJSONFlagConsistency

Test --json flag consistency across list and show commands (DE-009).

#### Methods

- `test_list_adrs_json_equals_format_json(self)`: Test --json produces same output as --format=json for adrs.
- `test_list_adrs_json_flag(self)`: Test list adrs accepts --json flag.
- `test_list_adrs_json_help_documents_flag(self)`: Test list adrs help mentions --json flag.
- `test_list_changes_json_equals_format_json(self)`: Test --json produces same output as --format=json for changes.
- `test_list_changes_json_flag(self)`: Test list changes accepts --json flag.
- `test_list_deltas_json_equals_format_json(self)`: Test --json produces same output as --format=json for deltas.
- `test_list_deltas_json_flag(self)`: Test list deltas accepts --json flag.
- `test_list_deltas_json_help_documents_flag(self)`: Test list deltas help mentions --json flag.
- `test_list_requirements_json_equals_format_json(self)`: Test --json produces same output as --format=json for requirements.
- `test_list_requirements_json_flag(self)`: Test list requirements accepts --json flag.
- `test_list_revisions_json_equals_format_json(self)`: Test --json produces same output as --format=json for revisions.
- `test_list_revisions_json_flag(self)`: Test list revisions accepts --json flag.
- `test_list_specs_json_flag_already_exists(self)`: Test list specs --json flag (should already work).
- `test_list_specs_json_help_documents_flag(self)`: Test list specs help mentions --json flag.

### TestJSONSchemaRegression

Test JSON output schema stability (DE-009 backward compatibility).

#### Methods

- `test_list_deltas_json_schema_stable(self)`: Test list deltas JSON output maintains expected structure.
- `test_list_specs_json_schema_stable(self)`: Test list specs JSON output maintains expected structure.

### TestListCommands

Test list command group.

#### Methods

- `test_list_adrs_help(self)`: Test list adrs command help.
- `test_list_changes_help(self)`: Test list changes command help.
- `test_list_deltas_help(self)`: Test list deltas command help.
- `test_list_help(self)`: Test list command group help.
- `test_list_specs_help(self)`: Test list specs command help.

### TestMainApp

Test main application structure and help.

#### Methods

- `test_main_help(self)`: Test main help command.
- `test_main_no_args(self)`: Test invoking with no arguments shows help.
- `test_main_shows_all_commands(self)`: Test that all major commands are listed.

### TestMultiValueFilters

Test multi-value filter support in list commands.

These tests verify that comma-separated filter values work correctly
and maintain backward compatibility with single values.

#### Methods

- `test_backward_compat_single_value_kind_filter(self)`: Test that single-value kind filters still work (backward compatibility).
- `test_backward_compat_single_value_status_filter(self)`: Test that single-value status filters still work (backward compatibility). - TODO: Task 1.4 - verify multi-value status filtering works
- `test_list_adrs_multi_value_status_not_yet_implemented(self)`: Test multi-value status filter for ADRs (TDD placeholder). - TODO: Task 1.4 - verify multi-value kind filtering works
- `test_list_deltas_multi_value_status_not_yet_implemented(self)`: Test multi-value status filter for deltas (TDD placeholder).
- `test_list_requirements_multi_value_kind_not_yet_implemented(self)`: Test multi-value kind filter for requirements (TDD placeholder). - TODO: Task 1.4 - change to: assert result.exit_code == 0
- `test_list_specs_multi_value_kind_works(self)`: Test multi-value kind filter for specs returns union. - TODO: Task 1.4 - verify multi-value filtering works correctly

### TestPolicyCommands

Test policy-related CLI commands.

#### Methods

- `test_create_policy_help(self)`: Test create policy command help.
- `test_list_policies_empty_succeeds(self)`: Test list policies with no policies exits successfully.
- `test_list_policies_help(self)`: Test list policies command help.
- `test_list_policies_json_flag(self)`: Test list policies supports --json flag.
- `test_show_policy_help(self)`: Test show policy command help.

### TestRegexpFiltering

Test regexp filtering utility and CLI flags.

#### Methods

- `test_list_adrs_regexp_flag(self)`: Test list adrs command has --regexp flag.
- `test_list_changes_regexp_flag(self)`: Test list changes command has --regexp flag.
- `test_list_deltas_regexp_flag(self)`: Test list deltas command has --regexp flag.
- `test_list_specs_regexp_flag(self)`: Test list specs command has --regexp flag.
- `test_matches_regexp_basic_match(self)`: Test basic pattern matching.
- `test_matches_regexp_case_insensitive(self)`: Test case-insensitive matching.
- `test_matches_regexp_case_sensitive(self)`: Test case-sensitive matching.
- `test_matches_regexp_complex_patterns(self)`: Test complex regexp patterns.
- `test_matches_regexp_empty_fields(self)`: Test handling of empty/None fields.
- `test_matches_regexp_invalid_pattern(self)`: Test invalid regexp pattern raises error.
- `test_matches_regexp_multiple_fields(self)`: Test matching across multiple fields.
- `test_matches_regexp_none_pattern(self)`: Test that None pattern matches everything.
- `test_matches_regexp_partial_match(self)`: Test that patterns match substrings.

### TestReverseRelationshipQueries

Test reverse relationship query flags for list commands.

These tests verify the --implements, --verified-by, and --informed-by flags
that enable native reverse traversal of relationships in registries.

#### Methods

- `test_list_deltas_implements_filters_correctly(self)`: Test that --implements returns only deltas implementing specific requirement. - Placeholder assertion for TDD
- `test_list_deltas_implements_flag_exists(self)`: Test that list deltas accepts --implements flag (TDD placeholder).
- `test_list_deltas_implements_nonexistent_requirement(self)`: Test --implements with non-existent requirement returns empty list. - Placeholder for TDD
- `test_list_deltas_implements_with_status_filter(self)`: Test combining --implements with --status filter.
- `test_list_requirements_verified_by_exact_match(self)`: Test --verified-by with exact artifact ID. - Placeholder for TDD
- `test_list_requirements_verified_by_flag_exists(self)`: Test that list requirements accepts --verified-by flag (TDD placeholder). - Empty output is also acceptable (current CLI behavior)
- `test_list_requirements_verified_by_glob_pattern(self)`: Test --verified-by with glob pattern matching.
- `test_list_requirements_verified_by_nonexistent_artifact(self)`: Test --verified-by with non-existent artifact returns empty list. - Placeholder for TDD
- `test_list_requirements_verified_by_va_pattern(self)`: Test --verified-by with VA (agent validation) pattern.
- `test_list_requirements_verified_by_with_spec_filter(self)`: Test combining --verified-by with --spec filter. - Placeholder for TDD
- `test_list_specs_informed_by_filters_correctly(self)`: Test that --informed-by returns only specs referencing specific ADR. - Placeholder for TDD
- `test_list_specs_informed_by_flag_exists(self)`: Test that list specs accepts --informed-by flag (TDD placeholder). - Empty output is also acceptable (current CLI behavior)
- `test_list_specs_informed_by_nonexistent_adr(self)`: Test --informed-by with non-existent ADR returns empty list. - Placeholder for TDD
- `test_list_specs_informed_by_with_kind_filter(self)`: Test combining --informed-by with --kind filter. - Empty output is also acceptable (current CLI behavior for no matches)

### TestShowCommandJSON

Test --json flag on show commands (DE-009).

#### Methods

- `test_show_adr_json_complete_output(self)`: Test show adr --json returns complete decision data without crashing.
- `test_show_adr_json_flag(self)`: Test show adr accepts --json flag.
- `test_show_adr_json_help_documents_flag(self)`: Test show adr help mentions --json flag.
- `test_show_delta_json_flag_already_exists(self)`: Test show delta --json flag (should already work).
- `test_show_requirement_json_flag(self)`: Test show requirement accepts --json flag.
- `test_show_revision_json_flag(self)`: Test show revision accepts --json flag.
- `test_show_spec_json_complete_output(self)`: Test show spec --json returns complete spec data, not just id.
- `test_show_spec_json_flag(self)`: Test show spec accepts --json flag.
- `test_show_spec_json_help_documents_flag(self)`: Test show spec help mentions --json flag.

### TestShowCommands

Test show command group.

#### Methods

- `test_show_adr_help(self)`: Test show adr command help.
- `test_show_help(self)`: Test show command group help.

### TestStandardCommands

Test standard-related CLI commands.

#### Methods

- `test_create_standard_help(self)`: Test create standard command help.
- `test_list_standards_empty_succeeds(self)`: Test list standards with no standards exits successfully.
- `test_list_standards_help(self)`: Test list standards command help.
- `test_list_standards_json_flag(self)`: Test list standards supports --json flag.
- `test_show_standard_help(self)`: Test show standard command help.

### TestStatusFilterParity

Test status filter consistency across list commands (DE-009).

#### Methods

- `test_list_specs_status_filter_active(self)`: Test list specs filters by active status.
- `test_list_specs_status_filter_deprecated(self)`: Test list specs filters by deprecated status.
- `test_list_specs_status_filter_flag(self)`: Test list specs accepts --status/-s flag.
- `test_list_specs_status_filter_short_flag(self)`: Test list specs accepts -s short flag.
- `test_list_specs_status_filter_superseded(self)`: Test list specs filters by superseded status.
- `test_list_specs_status_filter_with_json(self)`: Test status filter works with JSON output.
- `test_list_specs_status_help_documents_flag(self)`: Test list specs help mentions --status/-s flag.

### TestSyncCommand

Test sync command.

#### Methods

- `test_sync_help(self)`: Test sync command help.
- `test_sync_prune_flag_in_help(self)`: Test that --prune flag is documented in help.

### TestWorkspaceCommands

Test workspace management commands.

#### Methods

- `test_install_creates_workspace(self)`: Test install command creates workspace structure.
- `test_install_help(self)`: Test install command help.
- `test_validate_help(self)`: Test validate command help.
