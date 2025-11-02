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

### TestShowCommands

Test show command group.

#### Methods

- `test_show_adr_help(self)`: Test show adr command help.
- `test_show_help(self)`: Test show command group help.

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
