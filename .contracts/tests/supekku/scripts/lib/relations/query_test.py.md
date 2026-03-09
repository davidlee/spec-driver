# supekku.scripts.lib.relations.query_test

VT-085-001: Tests for generic relation query functions.

## Functions

- `_ci(ci_type, ci_id) -> dict[Tuple[str, str]]`
- `_rel(rtype, target) -> dict[Tuple[str, str]]`

## Classes

### CollectReferencesTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_all_slots_combined(self) -> None`
- `test_applies_to_non_list_values_skipped(self) -> None`
- `test_applies_to_slot(self) -> None`
- `test_bare_artifact_returns_empty(self) -> None`
- `test_context_input_missing_id_skipped(self) -> None`
- `test_context_inputs_slot(self) -> None`
- `test_empty_artifact(self) -> None`
- `test_informed_by_slot(self) -> None`
- `test_non_dict_context_input_skipped(self) -> None`
- `test_non_dict_relation_skipped(self) -> None`
- `test_relation_empty_target_skipped(self) -> None`
- `test_relation_missing_target_skipped(self) -> None`
- `test_relations_slot(self) -> None`
- `test_whitespace_stripped(self) -> None`

### FindByRelationTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_does_not_search_other_slots(self) -> None`
- `test_filters_by_both(self) -> None`
- `test_filters_by_target(self) -> None`
- `test_filters_by_type(self) -> None`

### FindRelatedToTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_empty_input(self) -> None`
- `test_filters_matching(self) -> None`
- `test_no_matches(self) -> None`

### MatchesRelatedToTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_bare_artifact_no_match(self) -> None`
- `test_case_insensitive(self) -> None`
- `test_empty_target_id(self) -> None`
- `test_match_in_applies_to(self) -> None`
- `test_match_in_context_inputs(self) -> None`
- `test_match_in_informed_by(self) -> None`
- `test_match_in_relations(self) -> None`
- `test_no_match(self) -> None`

### MatchesRelationTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_bare_artifact_returns_false(self) -> None`
- `test_case_insensitive_target(self) -> None`
- `test_case_insensitive_type(self) -> None`
- `test_does_not_search_applies_to(self) -> None`
- `test_match_by_both(self) -> None`
- `test_match_by_target(self) -> None`
- `test_match_by_type(self) -> None`
- `test_no_criteria_returns_false(self) -> None`
- `test_no_match_wrong_target(self) -> None`
- `test_no_match_wrong_type(self) -> None`

### MockBare

Artifact with no reference slots at all.

### MockDelta

Artifact with all reference slots (like ChangeArtifact).

### MockSpec

Artifact with relations and informed_by (like Spec).

### ProtocolTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_mock_bare_is_not_queryable(self) -> None`
- `test_mock_delta_is_queryable(self) -> None`
- `test_mock_spec_is_queryable(self) -> None`
