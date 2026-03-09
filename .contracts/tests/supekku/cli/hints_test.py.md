# supekku.cli.hints_test

Tests for schema hint output — VT-077-schema-hints.

## Classes

### FormatSchemaHintsTest

Unit tests for format_schema_hints().

**Inherits from:** unittest.TestCase

#### Methods

- `test_all_mapped_kinds_produce_nonempty_hints(self) -> None`
- `test_audit_hints(self) -> None`
- `test_card_returns_empty(self) -> None`: Card has no meaningful schemas to hint.
- `test_delta_hints_include_frontmatter(self) -> None`
- `test_delta_hints_include_relationships(self) -> None`
- `test_hints_are_runnable_commands(self) -> None`: Each hint should be a spec-driver schema show command.
- `test_memory_hints(self) -> None`
- `test_phase_hints(self) -> None`
- `test_plan_hints(self) -> None`
- `test_policy_hints(self) -> None`
- `test_prod_hints(self) -> None`
- `test_revision_hints(self) -> None`
- `test_spec_hints_include_block_schemas(self) -> None`
- `test_standard_hints(self) -> None`
- `test_unmapped_kind_returns_empty(self) -> None`
