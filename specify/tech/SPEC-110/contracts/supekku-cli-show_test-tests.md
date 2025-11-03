# supekku.cli.show_test

Tests for show CLI commands.

## Classes

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
