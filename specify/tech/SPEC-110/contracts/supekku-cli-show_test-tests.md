# supekku.cli.show_test

Tests for show CLI commands.

## Classes

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
