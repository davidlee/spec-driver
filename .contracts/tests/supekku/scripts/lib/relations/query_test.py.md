# supekku.scripts.lib.relations.query_test

VT-085-001 / VT-090-P3: Tests for generic relation query functions.

## Constants

- `_KNOWN_OVERLAP_FIELDS` - by source ("domain_field" vs "relation"), not by detail uniqueness.

## Functions

- `_ci(ci_type, ci_id) -> dict[Tuple[str, str]]`
- `_rel(rtype, target) -> dict[Tuple[str, str]]`

## Classes

### CollectFromBacklogFieldsTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_empty_frontmatter(self) -> None`
- `test_empty_string_skipped(self) -> None`
- `test_frontmatter_relations(self) -> None`
- `test_frontmatter_relations_skips_empty_target(self) -> None`
- `test_frontmatter_relations_skips_non_dict(self) -> None`
- `test_linked_deltas(self) -> None`
- `test_mixed_frontmatter(self) -> None`
- `test_no_frontmatter_attribute(self) -> None`
- `test_non_dict_frontmatter(self) -> None`
- `test_related_requirements(self) -> None`
- `test_whitespace_stripped(self) -> None`

### CollectFromDecisionFieldsTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_all_11_fields_yield_hits(self) -> None`
- `test_all_hits_have_domain_field_source(self) -> None`
- `test_bare_artifact_returns_empty(self) -> None`
- `test_detail_is_field_name(self) -> None`
- `test_empty_decision_returns_empty(self) -> None`
- `test_empty_string_skipped(self) -> None`
- `test_multiple_values_in_one_field(self) -> None`
- `test_whitespace_stripped(self) -> None`

### CollectFromDomainFieldsTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_bare_artifact_returns_empty(self) -> None`
- `test_chains_backlog_collector(self) -> None`
- `test_chains_decision_collector(self) -> None`
- `test_chains_governance_collector(self) -> None`
- `test_chains_requirement_collector(self) -> None`

### CollectFromGovernanceFieldsTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_bare_artifact_returns_empty(self) -> None`
- `test_empty_governance_returns_empty(self) -> None`
- `test_policy_fields(self) -> None`
- `test_standard_fields(self) -> None`

### CollectFromRequirementFieldsTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_all_fields_including_primary_spec(self) -> None`
- `test_all_hits_have_domain_field_source(self) -> None`
- `test_empty_primary_spec_skipped(self) -> None`
- `test_no_primary_spec_attribute(self) -> None`
- `test_scalar_primary_spec(self) -> None`

### CollectReferencesDomainFieldsTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_backlog_linked_deltas_via_collect_references(self) -> None`
- `test_decision_audits_via_collect_references(self) -> None`
- `test_domain_fields_combined_with_relations(self) -> None`

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

### CollectReverseReferenceTargetsTest

VT-090-P4-1: Tests for collect_reverse_reference_targets().

**Inherits from:** unittest.TestCase

#### Methods

- `test_applies_to_also_collected(self) -> None`
- `test_duplicates_merged(self) -> None`
- `test_empty_referrers(self) -> None`
- `test_multiple_referrers_aggregated(self) -> None`
- `test_single_referrer_with_relations(self) -> None`
- `test_uppercased(self) -> None`

### DomainFieldSemanticSeparationTest

Domain collectors use source="domain_field"/"backlog_field", not "relation".

**Inherits from:** unittest.TestCase

#### Methods

- `test_backlog_source_is_backlog_field(self) -> None`
- `test_decision_source_is_domain_field(self) -> None`
- `test_governance_source_is_domain_field(self) -> None`
- `test_non_overlap_details_not_in_relation_types(self) -> None`
- `test_requirement_source_is_domain_field(self) -> None`

### FindByRelationTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_does_not_search_other_slots(self) -> None`
- `test_filters_by_both(self) -> None`
- `test_filters_by_target(self) -> None`
- `test_filters_by_type(self) -> None`

### FindRelatedToDomainFieldsTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_match_backlog_linked_deltas(self) -> None`
- `test_match_decision_specs(self) -> None`
- `test_match_requirement_implemented_by(self) -> None`
- `test_no_match_domain_field(self) -> None`

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

### MockBacklogItem

Artifact mimicking BacklogItem with frontmatter dict.

### MockBare

Artifact with no reference slots at all.

### MockDecision

Artifact mimicking DecisionRecord domain fields.

### MockDelta

Artifact with all reference slots (like ChangeArtifact).

### MockPolicy

Artifact mimicking PolicyRecord domain fields.

### MockRequirement

Artifact mimicking RequirementRecord domain fields.

### MockSpec

Artifact with relations and informed_by (like Spec).

### MockStandard

Artifact mimicking StandardRecord domain fields.

### PartitionByReverseReferencesTest

VT-090-P4-2: Tests for partition_by_reverse_references().

**Inherits from:** unittest.TestCase

#### Methods

- `test_basic_partition(self) -> None`
- `test_case_insensitive_matching(self) -> None`
- `test_custom_id_fn(self) -> None`
- `test_empty_referrers_all_unreferenced(self) -> None`
- `test_self_reference_included(self) -> None`

### ProtocolTest

**Inherits from:** unittest.TestCase

#### Methods

- `test_mock_bare_is_not_queryable(self) -> None`
- `test_mock_delta_is_queryable(self) -> None`
- `test_mock_spec_is_queryable(self) -> None`

### ReqLike
