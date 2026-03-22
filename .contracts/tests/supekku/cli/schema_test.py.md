# supekku.cli.schema_test

Tests for schema CLI commands (via show schema / list schemas).

## Classes

### EnumIntrospectionTest

Test cases for show schema enums.* commands.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `test_show_enums_bare_lists_all(self) -> None`
- `test_show_enums_command_format(self) -> None`
- `test_show_enums_delta_status(self) -> None`
- `test_show_enums_invalid_path(self) -> None`
- `test_show_enums_requirement_kind(self) -> None`
- `test_show_enums_requirement_status(self) -> None`
- `test_show_enums_spec_kind(self) -> None`
- `test_show_enums_values_match_lifecycle_constants(self) -> None`
- `test_show_enums_verification_kind(self) -> None`
- `test_show_enums_verification_status(self) -> None`

### SchemaCommandsTest

Test cases for schema CLI commands.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `test_list_all_schemas(self) -> None`
- `test_list_blocks_only(self) -> None`
- `test_list_contains_all_expected_schemas(self) -> None`
- `test_list_frontmatter_schemas(self) -> None`
- `test_list_schemas(self) -> None`: Test listing all schemas via 'list schemas'.
- `test_show_all_frontmatter_kinds_json_schema(self) -> None`
- `test_show_all_frontmatter_kinds_yaml_example(self) -> None`
- `test_show_format_short_option(self) -> None`
- `test_show_frontmatter_invalid_format(self) -> None`
- `test_show_frontmatter_json_schema(self) -> None`
- `test_show_frontmatter_yaml_example(self) -> None`
- `test_show_schema_json(self) -> None`
- `test_show_schema_markdown_delta_relationships(self) -> None`
- `test_show_schema_markdown_phase_overview(self) -> None`
- `test_show_schema_markdown_plan_overview(self) -> None`
- `test_show_schema_markdown_revision_change(self) -> None`
- `test_show_schema_markdown_spec_capabilities(self) -> None`
- `test_show_schema_markdown_spec_relationships(self) -> None`
- `test_show_schema_markdown_verification_coverage(self) -> None`
- `test_show_schema_yaml_example(self) -> None`
- `test_show_unknown_block_type(self) -> None`
- `test_show_unknown_format(self) -> None`
- `test_show_unknown_frontmatter_kind(self) -> None`
