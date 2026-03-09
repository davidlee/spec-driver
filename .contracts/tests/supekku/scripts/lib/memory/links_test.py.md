# supekku.scripts.lib.memory.links_test

Tests for memory link parsing and resolution.

## Constants

- `_SRC`

## Functions

- `_artifact_index() -> dict[Tuple[str, tuple[Tuple[str, str]]]]`: Shared test artifact index.
- `_graph_bodies() -> dict[Tuple[str, str]]`
- `_graph_names() -> dict[Tuple[str, str]]`
- `_graph_types() -> dict[Tuple[str, str]]`
- `_mixed_result() -> LinkResolutionResult`: Helper: result with both resolved and missing links.
- `_resolve(link) -> <BinOp>`: Shorthand for resolve_parsed_link with test defaults.
- `_resolve_body(body) -> LinkResolutionResult`: Shorthand for resolve_all_links with smaller index.

## Classes

### TestComputeBacklinks

compute_backlinks builds reverse edges from forward links.

#### Methods

- `test_deduplicates_per_source(self) -> None`: Same target linked twice from same source appears once.
- `test_empty_corpus(self) -> None`
- `test_hub_node_multiple_backlinks(self) -> None`
- `test_mem_uri_scheme_normalized(self) -> None`
- `test_missing_target_still_tracked(self) -> None`: Backlinks include targets not in the corpus.
- `test_multiple_targets_from_one_source(self) -> None`
- `test_results_sorted(self) -> None`
- `test_self_link_excluded(self) -> None`
- `test_single_link(self) -> None`

### TestExpandLinkGraph

expand_link_graph does BFS expansion from a root node.

#### Methods

- `test_cycle_protection(self) -> None`
- `test_depth_one(self) -> None`
- `test_depth_two(self) -> None`
- `test_depth_zero_returns_root_only(self) -> None`
- `test_max_depth_capped(self) -> None`: Depths above 5 are capped to 5.
- `test_missing_target_included_but_not_expanded(self) -> None`
- `test_preserves_name_and_type(self) -> None`
- `test_root_not_in_bodies(self) -> None`: Root ID with no body returns just root node.
- `test_unknown_node_uses_id_as_name(self) -> None`

### TestLinksToFrontmatter

links_to_frontmatter serializes LinkResolutionResult.

#### Methods

- `test_empty_result(self) -> None`
- `test_missing_only(self) -> None`
- `test_mixed(self) -> None`
- `test_resolved_only(self) -> None`
- `test_resolved_with_label(self) -> None`
- `test_sorted_output(self) -> None`: out entries sorted by id for deterministic YAML.

### TestLinksToFrontmatterModes

links_to_frontmatter mode parameter controls output shape.

#### Methods

- `test_default_mode_is_missing(self) -> None`: Default mode omits out, keeps missing.
- `test_invalid_mode_raises(self) -> None`: Invalid mode raises ValueError.
- `test_mode_compact_includes_ids_only(self) -> None`: Compact mode includes out with id-only entries.
- `test_mode_full_empty_result(self) -> None`: Full mode with empty result returns empty dict.
- `test_mode_full_includes_both(self) -> None`: Full mode includes out and missing.
- `test_mode_full_preserves_sort_order(self) -> None`: Full mode sorts out entries by id.
- `test_mode_missing_empty_missing_returns_empty(self) -> None`: Missing mode with no missing links returns empty dict.
- `test_mode_missing_omits_out(self) -> None`: Missing mode omits out, keeps missing.
- `test_mode_none_returns_empty(self) -> None`: None mode returns empty dict regardless of content.

### TestParseLinks

parse_links extracts [[...]] tokens from body text.

#### Methods

- `test_adjacent_links(self) -> None`
- `test_dedup_by_target(self) -> None`
- `test_dedup_keeps_first_label(self) -> None`
- `test_empty_body(self) -> None`
- `test_empty_brackets_ignored(self) -> None` - --- Edge cases ---
- `test_link_at_end_of_line(self) -> None`
- `test_link_at_start_of_line(self) -> None`
- `test_link_with_label(self) -> None`
- `test_memory_id_link(self) -> None`
- `test_memory_shorthand_link(self) -> None`
- `test_multiline_body(self) -> None`
- `test_multiple_links(self) -> None`
- `test_nested_brackets_not_supported(self) -> None`: Nested [[ inside ]] captures first close.
- `test_no_links(self) -> None`
- `test_single_link(self) -> None`
- `test_skips_double_backtick_inline(self) -> None`
- `test_skips_fenced_code_block(self) -> None` - --- Code fence skipping ---
- `test_skips_fenced_with_language(self) -> None`
- `test_skips_inline_code(self) -> None` - --- Inline code skipping ---
- `test_skips_tilde_fenced_code_block(self) -> None`
- `test_whitespace_only_brackets_ignored(self) -> None`
- `test_whitespace_stripped_from_label(self) -> None`
- `test_whitespace_stripped_from_target(self) -> None`

### TestResolveAllLinks

resolve_all_links processes full body text.

#### Methods

- `test_dedup_in_resolution(self) -> None`
- `test_empty_body(self) -> None`
- `test_mixed_resolved_and_missing(self) -> None`
- `test_self_link_produces_warning(self) -> None`

### TestResolveParsedLink

resolve_parsed_link resolves against known artifact index.

#### Methods

- `test_mem_scheme_missing(self) -> None`: mem: scheme with unknown target produces MissingLink.
- `test_mem_scheme_resolves(self) -> None`: mem: URI scheme stripped and resolved as mem. prefix. - ── mem: URI scheme ──
- `test_mem_scheme_self_link(self) -> None`: mem: scheme that resolves to source_id is a self-link.
- `test_mem_scheme_with_label(self) -> None`
- `test_missing_target(self) -> None`
- `test_resolve_adr(self) -> None`
- `test_resolve_delta(self) -> None`
- `test_resolve_memory_canonical(self) -> None`
- `test_resolve_memory_shorthand(self) -> None`: Shorthand without mem. prefix resolves via normalization.
- `test_resolve_spec(self) -> None`
- `test_resolve_with_label(self) -> None`
- `test_self_link_returns_none(self) -> None`
- `test_self_link_shorthand_returns_none(self) -> None`: Shorthand that normalizes to source_id is a self-link.
- `test_unrecognized_target(self) -> None`: Not a known artifact ID and not memory-like.
