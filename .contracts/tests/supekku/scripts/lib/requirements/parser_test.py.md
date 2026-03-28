# supekku.scripts.lib.requirements.parser_test

Tests for requirement parsing and extraction.

## Classes

### TestCollisionDetection

DE-129 §1.2: ID collision detection in _records_from_content.

**Inherits from:** unittest.TestCase

#### Methods

- `test_compound_ids_produce_collision_warning(self) -> None`: Two lines parsing to same UID emit collision diagnostic.
- `test_sequential_ids_no_collision(self) -> None`: Normal sequential IDs produce no collision warning.
- `_make_repo(self) -> Path`

### TestCountRequirementLikeLines

DE-129: count_requirement_like_lines public API.

**Inherits from:** unittest.TestCase

#### Methods

- `test_counts_definitions(self) -> None`
- `test_empty_body(self) -> None`
- `test_no_requirements(self) -> None`

### TestFrontmatterDetectionLogging

DE-129 §1.2: Frontmatter warning emitted during extraction.

**Inherits from:** unittest.TestCase

#### Methods

- `test_no_warning_for_clean_spec(self) -> None`: _records_from_frontmatter does not warn when no frontmatter requirements.
- `test_warns_on_frontmatter_requirements(self) -> None`: _records_from_frontmatter logs info when frontmatter has requirement defs.
- `_make_repo(self) -> Path`

### TestHasFrontmatterRequirementDefinitions

DE-129 §1.1: Detect requirement definitions in frontmatter.

**Inherits from:** unittest.TestCase

#### Methods

- `test_list_of_dicts_with_description_only(self) -> None`: Frontmatter with requirements as list of dicts with 'description' only.
- `test_list_of_dicts_with_id(self) -> None`: Frontmatter with requirements as list of dicts with 'id' key.
- `test_list_of_strings(self) -> None`: Frontmatter with requirements as list of plain strings — not matched.
- `test_no_requirements_key(self) -> None`: Frontmatter without requirements key.
- `test_relationships_block_dict(self) -> None`: Relationships block uses a dict with primary/collaborators — not matched.
- `test_requirements_is_string(self) -> None`: Frontmatter with requirements as a string (unlikely but defensive).

### TestInlineRequirementTags

VT-081-003: Inline tag extraction from [tag1, tag2] syntax.

**Inherits from:** unittest.TestCase

#### Methods

- `test_filter_by_tag(self) -> None`: filter(tag=...) returns only tagged requirements.
- `test_tags_extracted_from_inline_syntax(self) -> None`: Tags in [brackets] after category are parsed.
- `test_tags_merged_on_multi_spec_sync(self) -> None`: Tags from multiple specs are unioned during merge.
- `test_tags_populated_in_registry_after_save_load(self) -> None`: Tags survive save/load round-trip.
- `_make_repo(self) -> Path`
- `_write_spec(self, root, spec_id, body) -> Path`

### TestIsRequirementLikeLine

Test _is_requirement_like_line heuristic for false-positive suppression.

The heuristic distinguishes lines that plausibly *define* a requirement
(and may have a format problem) from lines that merely *reference* one.

**Inherits from:** unittest.TestCase

#### Methods

- `test_badly_formatted_definition(self) -> None`: Missing bold markers — still looks like a definition attempt.
- `test_bold_bullet_definition(self) -> None`: Standard bold-bullet definition format is requirement-like. - -- Lines that ARE plausible definition attempts -----------------------
- `test_case_insensitive(self) -> None`: Lowercase fr/nf should still be detected.
- `test_empty_line(self) -> None`: Empty line is not requirement-like.
- `test_heading_definition(self) -> None`: Heading with FR/NF ID as subject is requirement-like.
- `test_heading_with_nf_subject(self) -> None`: Heading where NF-001 is the subject (not a cross-ref).
- `test_mixed_definition_and_crossref(self) -> None`: Line with both a definition-position ID and a parenthetical ref.

If 'per' appears, the whole line is treated as a cross-reference
because the heuristic errs on the side of suppressing false positives. - -- Edge cases ---------------------------------------------------------
- `test_multiple_parenthetical_refs(self) -> None`: Multiple IDs all inside parentheses — still a citation.
- `test_nf_definition(self) -> None`: Non-functional requirement definition is requirement-like.
- `test_no_requirement_id(self) -> None`: Line without any FR/NF ID at all.
- `test_parenthetical_only_mention(self) -> None`: ID only inside parentheses — citation, not definition.
- `test_parenthetical_qualified_mention(self) -> None`: Qualified ID only inside parentheses.
- `test_per_crossref_in_heading(self) -> None`: Heading ending with 'per NF-001' is a cross-reference.
- `test_per_crossref_in_parenthetical(self) -> None`: 'per PROD-004.FR-007' inside parentheses is a cross-reference. - -- Lines that are NOT definitions (cross-references) ------------------
- `test_per_crossref_qualified(self) -> None`: 'per SPEC-003.FR-006' is a cross-reference.
- `test_plain_bullet_definition(self) -> None`: Bullet with bare ID (no bold) is requirement-like.
- `test_plain_prose_mention(self) -> None`: Prose line with bare ID — ambiguous, retained as requirement-like.

Without a clear cross-reference signal (per/parenthetical), the
heuristic conservatively flags this to catch misformatted definitions.
- `test_qualified_bullet_definition(self) -> None`: Qualified ID (SPEC-100.FR-001) in bullet is requirement-like.
- `test_whitespace_only(self) -> None`: Whitespace-only line is not requirement-like.

### TestMismatchThreshold

DE-129 §1.2: Mismatch warning fires when extracted < requirement-like.

**Inherits from:** unittest.TestCase

#### Methods

- `test_all_extracted_no_warning(self) -> None`: 3 requirement-like lines, 3 extracted → no warning.
- `test_partial_extraction_warns(self) -> None`: 19 requirement-like lines but only 1 extracted → warning.
- `_make_repo(self) -> Path`

### TestRecordsFromContentCrossRefSuppression

Integration test: _records_from_content does not warn on cross-references.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_crossref_only_spec_no_warning(self) -> None`: Spec with only cross-references should not trigger extraction warning.
- `_make_repo(self) -> Path`

### TestRequirementHeadingRegex

VT-REGEX-076-001: _REQUIREMENT_HEADING regex matches dotted backlog format.

**Inherits from:** unittest.TestCase

#### Methods

- `test_matches_dash_separator(self) -> None`
- `test_matches_fr_dotted(self) -> None`
- `test_matches_h2(self) -> None`
- `test_matches_nf_dotted(self) -> None`
- `test_rejects_bullet_format(self) -> None`
- `test_rejects_non_dotted(self) -> None`
