# supekku.scripts.lib.specs.creation_test

Tests for create_spec module.

## Classes

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
