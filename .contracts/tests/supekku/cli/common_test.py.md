# supekku.cli.common_test

Tests for shared CLI helpers: data types, resolve, emit, find.

VT-resolve, VT-emit, VT-find-artifacts verification artifacts.

## Functions

- `_make_ref(content) -> ArtifactRef`: Create a test ArtifactRef with a real temp-ish path.
- `_mock_change_artifact(artifact_id, path) -> SimpleNamespace`
- `_mock_registry_collect(artifacts) -> MagicMock`: Create a mock ChangeRegistry whose collect()/find() return artifacts.

## Classes

### TestAmbiguousArtifactError

AmbiguousArtifactError lists all matching paths for disambiguation.

#### Methods

- `test_attributes(self) -> None`
- `test_is_exception(self) -> None`
- `test_message_contains_paths(self) -> None`

### TestArtifactNotFoundError

ArtifactNotFoundError carries type and id for consistent messaging.

#### Methods

- `test_attributes(self) -> None`
- `test_is_exception(self) -> None`
- `test_message(self) -> None`

### TestArtifactRef

ArtifactRef is a frozen dataclass holding resolved artifact info.

#### Methods

- `test_construction(self) -> None`
- `test_equality(self) -> None` - type: ignore[misc]
- `test_frozen(self) -> None`
- `test_inequality_different_id(self) -> None`

### TestCliJsonEnvelope

Tests for cli_json_success, cli_json_error, emit_json_and_exit.

#### Methods

- `test_emit_json_and_exit_error(self, capsys) -> None`
- `test_emit_json_and_exit_success(self, capsys) -> None`
- `test_error_envelope_guard_violation(self) -> None`
- `test_error_envelope_structure(self) -> None`
- `test_error_envelope_unexpected(self) -> None`
- `test_error_envelope_validation(self) -> None`
- `test_success_envelope_structure(self) -> None`

### TestEmitArtifactBodyOnly

emit_artifact --body-only mode outputs body without frontmatter.

#### Methods

- `test_body_only_strips_frontmatter(self, tmp_path, capsys) -> None`

### TestEmitArtifactContentType

emit_artifact --content-type dispatches correctly.

#### Methods

- `test_content_type_overrides_raw_with_warning(self, tmp_path, capsys) -> None`
- `test_frontmatter_calls_format_fn(self, capsys) -> None`
- `test_markdown_outputs_file_content(self, tmp_path, capsys) -> None`
- `test_yaml_outputs_frontmatter_block(self, tmp_path, capsys) -> None`

### TestEmitArtifactDefault

emit_artifact default output mode uses format_fn.

#### Methods

- `test_default_calls_format_fn(self, capsys) -> None`

### TestEmitArtifactJson

emit_artifact --json mode uses json_fn.

#### Methods

- `test_json_calls_json_fn(self, capsys) -> None`

### TestEmitArtifactMutualExclusivity

emit_artifact rejects multiple output modes.

#### Methods

- `test_all_three_rejected(self, capsys) -> None`
- `test_body_only_and_json_rejected(self, capsys) -> None`
- `test_body_only_and_raw_rejected(self, capsys) -> None`
- `test_json_and_path_rejected(self, capsys) -> None`
- `test_json_and_raw_rejected(self, capsys) -> None`

### TestEmitArtifactPath

emit_artifact --path mode echoes the path.

#### Methods

- `test_path_only(self, capsys) -> None`

### TestEmitArtifactRaw

emit_artifact --raw mode reads the file content.

#### Methods

- `test_raw_reads_file(self, tmp_path, capsys) -> None`

### TestExitCodeConstants

Verify exit code constants are correct and distinct.

#### Methods

- `test_distinct(self) -> None`
- `test_values(self) -> None`

### TestExtractYamlFrontmatter

extract_yaml_frontmatter returns the YAML block between --- fences.

#### Methods

- `test_empty_frontmatter(self, tmp_path) -> None`
- `test_extracts_frontmatter(self, tmp_path) -> None`
- `test_no_frontmatter_returns_empty(self, tmp_path) -> None`

### TestFindArtifactsBacklog

find_artifacts for backlog types uses discover_backlog_items.

#### Methods

- @pytest.mark.parametrize(Tuple[artifact_type, subdir, item_id], List[Tuple[issue, issues, ISSUE-001], Tuple[problem, problems, PROB-001], Tuple[improvement, improvements, IMPR-001], Tuple[risk, risks, RISK-001]]) `test_finds_backlog_items(self, tmp_path, artifact_type, subdir, item_id) -> None`
- `test_no_matches(self, tmp_path) -> None`
- `_create_item(self, root, subdir, item_id) -> None`

### TestFindArtifactsCard

find_artifacts for card type uses rglob.

#### Methods

- `test_finds_matching_cards(self, tmp_path) -> None`
- `test_no_matches(self, tmp_path) -> None`

### TestFindArtifactsMemory

find_artifacts for memory type — auto-prepends mem. prefix.

#### Methods

- @patch(supekku.scripts.lib.memory.registry.MemoryRegistry) `test_finds_with_prefix_normalization(self, mock_cls) -> None`
- @patch(supekku.scripts.lib.memory.registry.MemoryRegistry) `test_pattern_already_prefixed(self, mock_cls) -> None`

### TestFindArtifactsPlan

find_artifacts for plan type scans delta dirs.

#### Methods

- `test_finds_matching_plans(self, tmp_path) -> None`
- `test_no_deltas_dir(self, tmp_path) -> None`
- `test_numeric_shorthand_pattern(self, tmp_path) -> None`

### TestFindArtifactsRequirement

find_artifacts for requirement type.

#### Methods

- @patch(supekku.scripts.lib.requirements.registry.RequirementsRegistry) `test_colon_normalization(self, mock_cls) -> None`: DEC-041-05: colon in pattern normalized to dot.
- @patch(supekku.scripts.lib.requirements.registry.RequirementsRegistry) `test_finds_matching_requirements(self, mock_cls) -> None`

### TestFindArtifactsRevision

find_artifacts for revision type — returns matching ArtifactRefs.

#### Methods

- @patch(supekku.scripts.lib.changes.registry.ChangeRegistry) `test_empty_results(self, mock_cls) -> None`
- @patch(supekku.scripts.lib.changes.registry.ChangeRegistry) `test_finds_matching_revisions(self, mock_cls) -> None`
- @patch(supekku.scripts.lib.changes.registry.ChangeRegistry) `test_numeric_pattern_normalized(self, mock_cls) -> None`

### TestFindArtifactsSpec

find_artifacts for spec type.

#### Methods

- @patch(supekku.scripts.lib.specs.registry.SpecRegistry) `test_finds_matching_specs(self, mock_cls) -> None`

### TestFindArtifactsUnsupportedType

find_artifacts raises ValueError for unknown types.

#### Methods

- `test_raises_value_error(self) -> None`

### TestParsePrefix

_parse_prefix extracts alphabetic prefix from dash-separated IDs.

#### Methods

- `test_lowercase_normalized(self) -> None`
- `test_multi_char_prefix(self) -> None`
- `test_no_dash(self) -> None`
- `test_numeric_only(self) -> None`
- `test_numeric_prefix(self) -> None`
- `test_standard_prefix(self) -> None`

### TestPrefixToType

PREFIX_TO_TYPE mapping covers expected prefixes.

#### Methods

- `test_adr_prefix(self) -> None`
- `test_card_uses_t(self) -> None`
- `test_delta_prefix(self) -> None`
- `test_improvement_uses_impr(self) -> None`
- `test_prod_maps_to_spec(self) -> None`
- `test_risk_included(self) -> None`
- `test_spec_prefix(self) -> None`

### TestResolveArtifactAdr

resolve_artifact for ADR type.

#### Methods

- @patch(supekku.scripts.lib.decisions.registry.DecisionRegistry) `test_raises_not_found_for_missing_adr(self, mock_cls) -> None`
- @patch(supekku.scripts.lib.decisions.registry.DecisionRegistry) `test_resolves_adr(self, mock_cls) -> None`

### TestResolveArtifactAudit

resolve_artifact for audit type.

#### Methods

- @patch(supekku.scripts.lib.changes.registry.ChangeRegistry) `test_resolves_audit(self, mock_cls) -> None`

### TestResolveArtifactBacklog

Tests for backlog resolvers (issue, problem, improvement, risk).

#### Methods

- `test_duplicate_ids_resolves_one(self, tmp_path) -> None`: Duplicate IDs are deduplicated by BacklogRegistry; resolver returns one.
- `test_raises_not_found_for_missing_backlog(self, tmp_path) -> None`
- @pytest.mark.parametrize(Tuple[artifact_type, subdir, item_id], List[Tuple[issue, issues, ISSUE-001], Tuple[problem, problems, PROB-001], Tuple[improvement, improvements, IMPR-001], Tuple[risk, risks, RISK-001]]) `test_resolves_backlog_item(self, tmp_path, artifact_type, subdir, item_id) -> None`
- `_create_backlog_item(self, root, subdir, item_id, slug) -> Path`

### TestResolveArtifactCard

resolve_artifact for card type.

#### Methods

- @patch(supekku.scripts.lib.cards.CardRegistry) `test_raises_not_found_for_missing_card(self, mock_cls) -> None`
- @patch(supekku.scripts.lib.cards.CardRegistry) `test_resolves_card(self, mock_cls) -> None`

### TestResolveArtifactDelta

resolve_artifact for delta type.

#### Methods

- @patch(supekku.scripts.lib.changes.registry.ChangeRegistry) `test_resolves_delta(self, mock_cls) -> None`

### TestResolveArtifactDispatchCoverage

All types in dispatch table are exercised.

#### Methods

- @pytest.mark.parametrize(artifact_type, List[spec, delta, revision, audit, adr, policy, standard, requirement, card, memory, plan, issue, problem, improvement, risk]) `test_known_type_does_not_raise_value_error(self, artifact_type) -> None`: Every registered type should dispatch (may raise NotFound, not ValueError).

### TestResolveArtifactMemory

resolve_artifact for memory type.

#### Methods

- @patch(supekku.scripts.lib.memory.registry.MemoryRegistry) `test_resolves_memory(self, mock_cls) -> None`

### TestResolveArtifactPlan

Tests for plan resolver (VT-plan-resolve).

#### Methods

- `test_raises_not_found_for_missing_plan(self, tmp_path) -> None`
- `test_raises_not_found_when_no_deltas_dir(self, tmp_path) -> None`
- `test_resolves_plan_by_full_id(self, tmp_path) -> None`
- `test_resolves_plan_by_numeric_shorthand(self, tmp_path) -> None`

### TestResolveArtifactPolicy

resolve_artifact for policy type.

#### Methods

- @patch(supekku.scripts.lib.policies.registry.PolicyRegistry) `test_raises_not_found(self, mock_cls) -> None`
- @patch(supekku.scripts.lib.policies.registry.PolicyRegistry) `test_resolves_policy(self, mock_cls) -> None`

### TestResolveArtifactRequirement

resolve_artifact for requirement type.

#### Methods

- @patch(supekku.scripts.lib.core.paths.get_registry_dir) @patch(supekku.scripts.lib.requirements.registry.RequirementsRegistry) `test_normalizes_colon_to_dot(self, mock_cls, mock_dir) -> None`: Colon-separated ID is normalized to dot per DEC-041-05.
- @patch(supekku.scripts.lib.core.paths.get_registry_dir) @patch(supekku.scripts.lib.requirements.registry.RequirementsRegistry) `test_resolves_requirement(self, mock_cls, mock_dir) -> None`

### TestResolveArtifactRevision

resolve_artifact for revision type — PoC migration target.

#### Methods

- @patch(supekku.scripts.lib.changes.registry.ChangeRegistry) `test_raises_not_found_for_missing_revision(self, mock_cls) -> None`
- @patch(supekku.scripts.lib.changes.registry.ChangeRegistry) `test_resolves_revision_by_full_id(self, mock_cls) -> None`
- @patch(supekku.scripts.lib.changes.registry.ChangeRegistry) `test_resolves_revision_by_numeric_shorthand(self, mock_cls) -> None`

### TestResolveArtifactSpec

resolve_artifact for spec type.

#### Methods

- @patch(supekku.scripts.lib.specs.registry.SpecRegistry) `test_raises_not_found_for_missing_spec(self, mock_cls) -> None`
- @patch(supekku.scripts.lib.specs.registry.SpecRegistry) `test_resolves_spec(self, mock_cls) -> None`

### TestResolveArtifactStandard

resolve_artifact for standard type.

#### Methods

- @patch(supekku.scripts.lib.standards.registry.StandardRegistry) `test_raises_not_found(self, mock_cls) -> None`
- @patch(supekku.scripts.lib.standards.registry.StandardRegistry) `test_resolves_standard(self, mock_cls) -> None`

### TestResolveArtifactUnsupportedType

resolve_artifact raises ValueError for unknown types.

#### Methods

- `test_raises_value_error(self) -> None`

### TestResolveById

resolve_by_id resolves bare IDs across registries.

#### Methods

- `test_numeric_id_resolves(self) -> None`: A numeric-only ID resolves to matching artifact(s).
- `test_numeric_no_match_returns_empty(self) -> None`: A numeric ID with no matching artifact returns empty.
- `test_prefixed_adr_resolves(self) -> None`: A prefixed ADR ID resolves correctly.
- `test_prefixed_delta_resolves(self) -> None`: A prefixed ID like DE-063 resolves to the correct delta.
- `test_unknown_id_returns_empty(self) -> None`: An ID with no matching artifact returns empty list.
- `test_unknown_prefix_returns_empty(self) -> None`: An ID with a prefix not in PREFIX_TO_TYPE returns empty.
