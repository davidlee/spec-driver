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

### CreateSpecBlocksTest

VT-DE139-CREATE-001: created spec emits all block placeholders.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_created_spec_contains_all_blocks(self)`
- `test_created_spec_contains_requirements_block(self)`: VT-140-019: spec creation emits empty requirements block (DEC-140-14).
- `test_created_spec_has_no_packages(self)`
- `_setup_repo_with_blocks_template(self) -> Path`

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

### SpecRequirementsEmptyBlockTest

VT-140-030: scaffolded spec with empty block creates no registry entries.

**Inherits from:** unittest.TestCase

#### Methods

- `setUp(self) -> None`
- `tearDown(self) -> None`
- `test_empty_requirements_block_produces_no_records(self)`: Empty requirements block in created spec yields zero registry entries.

### TemplateBlockVariablesTest

VT-DE139-TPL-001: template contains all block template variables.

**Inherits from:** unittest.TestCase

#### Methods

- `test_spec_template_has_block_variables(self)`
- `test_spec_template_has_requirements_block_variable(self)`: VT-140-020: template includes spec_requirements_block placeholder.
