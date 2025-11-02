# supekku.cli.schema_test

Tests for schema CLI commands.

## Classes

### SchemaCommandsTest

Test cases for schema CLI commands.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test environment.
- `test_list_all_schemas(self) -> None`: Test listing both block and frontmatter schemas.
- `test_list_blocks_only(self) -> None`: Test listing only block schemas.
- `test_list_contains_all_expected_schemas(self) -> None`: Test that list contains all 7 expected schemas.
- `test_list_frontmatter_schemas(self) -> None`: Test listing only frontmatter schemas.
- `test_list_schemas(self) -> None`: Test listing all schemas.
- `test_show_all_frontmatter_kinds_json_schema(self) -> None`: Test that all frontmatter kinds can be shown as JSON Schema.
- `test_show_all_frontmatter_kinds_yaml_example(self) -> None`: Test that all frontmatter kinds can be shown as YAML example.
- `test_show_format_short_option(self) -> None`: Test using -f short option for format.
- `test_show_frontmatter_invalid_format(self) -> None`: Test error for invalid format with frontmatter.
- `test_show_frontmatter_json_schema(self) -> None`: Test showing frontmatter prod schema as JSON Schema.
- `test_show_frontmatter_yaml_example(self) -> None`: Test showing frontmatter delta schema as YAML example.
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
- `test_show_unknown_frontmatter_kind(self) -> None`: Test error for unknown frontmatter kind.
