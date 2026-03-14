# supekku.scripts.lib.formatters.relation_formatters_test

Tests for relation_formatters — VT-085-005 and VT-090-P5.

## Classes

### TestFormatRefsCount

VT-085-005: format_refs_count rendering.

#### Methods

- `test_empty_list(self) -> None`
- `test_multiple_refs(self) -> None`
- `test_single_ref(self) -> None`
- `test_two_refs_plural(self) -> None`

### TestFormatRefsTsv

VT-085-005: format_refs_tsv rendering.

#### Methods

- `test_applies_to_source(self) -> None`
- `test_empty_detail(self) -> None`
- `test_empty_list(self) -> None`
- `test_informed_by_source(self) -> None`
- `test_multiple_refs(self) -> None`
- `test_single_ref(self) -> None`

### TestFormatRelatedSection

VT-090-P5-4/P5-5: format_related_section rendering.

#### Methods

- `test_empty_dict_returns_empty_list(self) -> None`: VT-090-P5-5: No references → no section.
- `test_kind_label_replaces_underscore(self) -> None`
- `test_multiple_kinds_sorted(self) -> None`
- `test_single_kind(self) -> None`
- `test_starts_with_blank_line(self) -> None`
