# supekku.scripts.lib.blocks.metadata.validator_alias_test

Validator tests for the two-axis alias mechanism (DE-137 IP-137-P01).

Covers:
- VT-CC-008: field-NAME alias canonicalisation + ``fix_kind='rename_key'``.
- VT-CC-009: tolerated_aliases accepted by default; rejected under
  ``accept_tolerated=False``; warning under strict.
- VT-CC-030: field-VALUE alias canonicalisation +
  ``fix_kind='rewrite_value'``.
- VT-CC-034: field-NAME alias collision -> error severity, no merge.

## Functions

- `_enum_block_with_field_alias() -> BlockMetadata`
- `_status_block() -> BlockMetadata`
- `test_field_name_alias_collision_is_error_severity() -> None`
- `test_field_name_alias_does_not_mutate_input() -> None`
- `test_field_name_alias_strict_emits_warning_with_rename_fix() -> None`
- `test_field_name_alias_tolerant_is_silent() -> None`
- `test_field_value_alias_strict_emits_warning_with_rewrite_fix() -> None`
- `test_field_value_alias_tolerant_is_silent() -> None`
- `test_nested_relations_item_field_aliases_strict_emits_warning() -> None`
- `test_tolerated_alias_accepted_silently_by_default() -> None`
- `test_tolerated_alias_under_no_tolerated_is_error() -> None`
- `test_tolerated_alias_under_strict_emits_warning() -> None`
- @pytest.mark.parametrize(Tuple[typo, expected_hint], List[Tuple[draaft, draft], Tuple[in_progres, in-progress], Tuple[complte, completed]]) `test_unknown_enum_under_strict_populates_did_you_mean(typo, expected_hint) -> None`
- `test_unknown_enum_under_tolerant_is_silent() -> None`
