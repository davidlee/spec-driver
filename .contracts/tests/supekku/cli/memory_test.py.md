# supekku.cli.memory_test

Integration tests for memory CLI commands (create, list, show, find).

## Functions

- `_write_memory_file(directory, mem_id, name) -> Path`: Write a minimal valid memory file for testing.

## Classes

### CreateMemoryCommandTest

Test cases for create memory CLI command.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_create_memory(self) -> None`: Create memory writes file and prints ID.
- `test_create_memory_rejects_duplicate(self) -> None`: Creating a memory with an existing ID fails.
- `test_create_memory_requires_type(self) -> None`: Missing --type should error.
- `test_create_memory_shorthand_id(self) -> None`: Shorthand ID (without mem. prefix) is normalized.
- `test_create_memory_with_options(self) -> None`: Create memory respects --status, --tag, --summary.

### FindMemoryCommandTest

Test cases for find memory CLI command.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_find_memory_exact(self) -> None`: Find memory with exact ID.
- `test_find_memory_no_match(self) -> None`: Find memory with no match exits cleanly.
- `test_find_memory_shorthand(self) -> None`: Find memory with shorthand (omitted mem. prefix).
- `test_find_memory_wildcard(self) -> None`: Find memory with mem.* pattern.

### ListMemoriesCommandTest

Test cases for list memories CLI command.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_list_memories_empty(self) -> None`: Empty directory exits cleanly.
- `test_list_memories_filter_status(self) -> None`: --status filters records.
- `test_list_memories_filter_type(self) -> None`: --type filters records.
- `test_list_memories_json(self) -> None`: JSON output parses correctly.
- `test_list_memories_table(self) -> None`: Table output includes record IDs and names.
- `test_list_memories_tsv(self) -> None`: TSV output contains tabs.
- `test_list_memory_singular_alias(self) -> None`: Singular 'memory' alias works.

### ListMemoriesLinksToTest

Integration tests for list memories --links-to.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_links_to_json_output(self) -> None`: --links-to works with --json output.
- `test_links_to_multiple_backlinkers(self) -> None`: --links-to returns all memories that link to the target.
- `test_links_to_no_backlinks(self) -> None`: --links-to with no backlinks exits cleanly.
- `test_links_to_returns_backlinkers(self) -> None`: --links-to shows memories that link to the target.
- `test_links_to_with_shorthand(self) -> None`: --links-to accepts shorthand IDs (without mem. prefix).
- `_write_memory_with_body(self, mem_id, name, body) -> Path`: Write a memory file with custom body content.

### ListMemoriesSelectionTest

Integration tests for list memories selection/filtering options.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_command_filters_by_scope(self) -> None`: --command filters by token-prefix match on scope.commands. - -- --command scope matching --
- `test_deprecated_excluded_by_default(self) -> None`: Deprecated records are excluded without explicit --status. - -- deprecated excluded by default --
- `test_draft_excluded_by_default(self) -> None`: Draft records are excluded without --include-draft. - -- --include-draft --
- `test_explicit_status_bypasses_exclusion(self) -> None`: --status deprecated shows deprecated records (skip_status_filter).
- `test_include_draft_shows_drafts(self) -> None`: --include-draft surfaces draft records.
- `test_limit_caps_output(self) -> None`: --limit restricts the number of results. - -- --limit --
- `test_match_tag_filters_by_tag_intersection(self) -> None`: --match-tag filters records whose tags overlap. - -- --match-tag scope matching --
- `test_match_tag_repeatable(self) -> None`: Multiple --match-tag flags are OR'd.
- `test_ordering_by_severity(self) -> None`: Records ordered by severity (critical before low). - -- deterministic ordering --
- `test_path_combined_with_type_filter(self) -> None`: --path and --type both apply (AND between metadata and scope). - -- combined scope + metadata filter --
- `test_path_filters_by_scope(self) -> None`: --path returns only records whose scope.paths match. - -- --path scope matching --
- `test_path_no_match_empty_output(self) -> None`: --path with no matching records exits cleanly.
- `test_path_repeatable(self) -> None`: Multiple --path flags are OR'd.

### ShowMemoryBodyOnlyTest

Integration tests for show memory --body-only.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_body_only_mutually_exclusive_with_json(self) -> None`: --body-only and --json are mutually exclusive.
- `test_body_only_short_flag(self) -> None`: -b is shorthand for --body-only.
- `test_body_only_strips_frontmatter(self) -> None`: --body-only outputs body without frontmatter.

### ShowMemoryCommandTest

Test cases for show memory CLI command.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_show_memory_details(self) -> None`: Show memory displays record details.
- `test_show_memory_json(self) -> None`: Show memory --json outputs valid JSON.
- `test_show_memory_mutually_exclusive(self) -> None`: --json and --path are mutually exclusive.
- `test_show_memory_not_found(self) -> None`: Show memory with bad ID errors.
- `test_show_memory_path(self) -> None`: Show memory --path outputs file path.
- `test_show_memory_raw(self) -> None`: Show memory --raw outputs raw file content.
- `test_show_memory_shorthand(self) -> None`: Show memory 'fact.alpha' normalizes to mem.fact.alpha.

### ShowMemoryLinksDepthTest

Integration tests for show memory --links-depth.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_links_depth_json_format(self) -> None`: --links-depth with --json outputs structured JSON.
- `test_links_depth_not_found(self) -> None`: --links-depth on nonexistent memory errors.
- `test_links_depth_shows_graph_table(self) -> None`: --links-depth 1 shows outgoing links as table.
- `test_links_depth_tree_format(self) -> None`: --links-depth with --tree shows indented tree.
- `test_links_depth_zero(self) -> None`: --links-depth 0 shows only root node.
- `_write_memory_with_body(self, mem_id, name, body) -> Path`: Write a memory file with custom body content.
