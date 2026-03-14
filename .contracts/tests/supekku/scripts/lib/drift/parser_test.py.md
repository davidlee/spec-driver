# supekku.scripts.lib.drift.parser_test

Tests for drift ledger parser (VT-065-parser).

Covers DR-065 parser contract table edge cases and normal operation.

## Classes

### TestAnalysisExtraction

Freeform analysis from content outside the YAML fence.

#### Methods

- `test_analysis_after_fence(self)`
- `test_analysis_before_and_after_fence(self)`
- `test_no_analysis(self)`

### TestBasicParsing

Normal entry parsing with fenced YAML.

#### Methods

- `test_affected_artifacts_parsed(self)`
- `test_claims_parsed_as_typed(self)`
- `test_discovered_by_parsed(self)`
- `test_evidence_list_parsed(self)`
- `test_extra_yaml_keys_preserved(self)`
- `test_multiple_entries(self)`
- `test_single_entry(self)`
- `test_sources_parsed_as_typed(self)`

### TestFenceHeadingPrecedence

DEC-065-03: fences processed before headings.

#### Methods

- `test_heading_after_fence_is_split(self)`: ### after a fence closes is a real entry boundary.
- `test_heading_inside_fence_not_split(self)`: ### inside a fenced block is not treated as an entry boundary.

### TestFreeformBodyExtraction

DEC-065-08: freeform body content preserved.

#### Methods

- `test_body_before_entries(self)`
- `test_empty_body(self)`
- `test_no_entries(self)`

### TestParserContractEdgeCases

DR-065 DEC-065-03 parser contract table.

#### Methods

- `test_duplicate_entry_ids(self)`: Duplicate IDs → warning, both entries preserved.
- `test_entry_with_no_yaml_block(self)`: No YAML block → warning, heading-only entry.
- `test_malformed_yaml_block(self)`: Malformed YAML → warning, entry with \_parse_error in extra.
- `test_missing_required_claim_keys(self)`: Missing kind or text → warning, malformed claim skipped.
- `test_missing_required_source_keys(self)`: Missing required nested keys → warning, malformed record skipped.
- `test_multiple_yaml_blocks_first_wins(self)`: Multiple fenced YAML blocks → first parsed, rest is analysis. - no data

### TestProgressiveStrictness

IMPR-007 D13: minimal at creation, stricter at triage.

#### Methods

- `test_discovered_by_missing_kind(self)`: discovered_by without kind → skipped with warning.
- `test_minimal_entry_yaml(self)`: Minimal valid entry: just entry_type.
