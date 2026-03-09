# supekku.scripts.lib.specs.creation_test

Tests for create_spec module.

## Classes

### BuildFrontmatterTaxonomyTest

VT-030-002: build_frontmatter sets taxonomy defaults correctly.

**Inherits from:** unittest.TestCase

#### Methods

- `test_create_tech_spec_frontmatter_has_assembly(self)`: Integration: create_spec produces a tech spec with category: assembly.
- `test_explicit_category_overrides_default(self)`
- `test_guidance_has_no_category(self)`
- `test_product_spec_has_no_category(self)`
- `test_tech_spec_defaults_to_assembly(self)`

### CreateSpecTest

Test cases for create_spec functionality.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_create_product_spec_without_testing_doc(self) -> None`: Test creating a product spec without testing documentation.
- `test_create_tech_spec_generates_spec_and_testing_doc(self) -> None`: Test creating a tech spec with testing documentation.
- `test_json_output_matches_structure(self) -> None`: Test that JSON output from create_spec has expected structure.
- `test_missing_templates_use_fallback(self) -> None`: Test that missing local templates fall back to package templates.
- `test_repository_root_not_found(self) -> None`: Test that operations outside a repository raise RepositoryRootNotFoundError.
- `_setup_repo(self) -> Path`
