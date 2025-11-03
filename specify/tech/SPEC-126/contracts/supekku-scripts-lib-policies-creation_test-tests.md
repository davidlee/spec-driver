# supekku.scripts.lib.policies.creation_test

Tests for policy creation module.

## Classes

### TestBuildPolicyFrontmatter

Tests for build_policy_frontmatter function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_minimal_frontmatter(self) -> None`: Test frontmatter with minimal fields.
- `test_with_author(self) -> None`: Test frontmatter with author.

### TestCreatePolicy

Tests for create_policy function.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test fixtures.
- `test_create_first_policy(self) -> None`: Test creating the first policy.

### TestGenerateNextPolicyId

Tests for generate_next_policy_id function.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`: Set up test fixtures.
- `test_first_policy(self) -> None`: Test ID generation for first policy.
- `test_incremental_ids(self) -> None`: Test ID generation increments correctly.

### TestTitleSlug

Tests for create_title_slug function.

**Inherits from:** unittest.TestCase

#### Methods

- `test_leading_trailing_hyphens(self) -> None`: Test slug strips leading/trailing hyphens.
- `test_multiple_spaces(self) -> None`: Test slug creation with multiple spaces.
- `test_simple_title(self) -> None`: Test slug creation from simple title.
- `test_with_special_chars(self) -> None`: Test slug creation with special characters.
