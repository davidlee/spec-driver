# supekku.cli.schema_test

Tests for schema CLI commands.

## Classes

### SchemaCommandsTest

Test cases for schema CLI commands.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test environment.
- `test_list_contains_all_expected_schemas(self) -> None`: Test that list contains all 7 expected schemas.
- `test_list_schemas(self) -> None`: Test listing all schemas.
- `test_show_format_short_option(self) -> None`: Test using -f short option for format.
- `test_show_schema_json(self) -> None`: Test showing schema in JSON format.
- `test_show_schema_markdown_delta_relationships(self) -> None`: Test showing delta.relationships schema in markdown format.
- `test_show_schema_markdown_phase_overview(self) -> None`: Test showing phase.overview schema in markdown format.
- `test_show_schema_markdown_plan_overview(self) -> None`: Test showing plan.overview schema in markdown format.
- `test_show_schema_markdown_revision_change(self) -> None`: Test showing revision.change schema in markdown format.
- `test_show_schema_markdown_spec_capabilities(self) -> None`: Test showing spec.capabilities schema in markdown format.
- `test_show_schema_markdown_spec_relationships(self) -> None`: Test showing spec.relationships schema in markdown format.
- `test_show_schema_markdown_verification_coverage(self) -> None`: Test showing verification.coverage schema in markdown format.
- `test_show_schema_yaml_example(self) -> None`: Test showing schema as YAML example.
- `test_show_unknown_block_type(self) -> None`: Test error for unknown block type.
- `test_show_unknown_format(self) -> None`: Test error for unknown format type.
