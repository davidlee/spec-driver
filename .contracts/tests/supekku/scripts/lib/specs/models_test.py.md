# supekku.scripts.lib.specs.models_test

Tests for Spec model taxonomy properties (VT-030-001).

## Classes

### SpecExternalRefTest

VT-067-001: Spec model exposes ext_id and ext_url from frontmatter.

**Inherits from:** RepoTestCase

#### Methods

- `test_ext_id_property(self)`
- `test_ext_url_property(self)`
- `test_missing_ext_fields_return_empty_string(self)`
- `test_to_dict_includes_ext_fields_when_present(self)`
- `test_to_dict_omits_ext_fields_when_absent(self)`
- `_make_repo_with_external_spec(self)`

### SpecRelationsTest

VT-085-006: Spec model exposes .relations property from frontmatter.

**Inherits from:** RepoTestCase

#### Methods

- `test_relations_absent_returns_empty(self)`
- `test_relations_are_dicts(self)`
- `test_relations_present(self)`
- `test_to_dict_includes_relations_when_present(self)`
- `test_to_dict_omits_relations_when_absent(self)`
- `_make_repo_with_relations_spec(self)`

### SpecTaxonomyTest

VT-030-001: Spec model exposes category and c4_level from frontmatter.

**Inherits from:** RepoTestCase

#### Methods

- `test_c4_level_property(self)`
- `test_category_property(self)`
- `test_missing_taxonomy_returns_empty_string(self)`
- `test_to_dict_includes_taxonomy_when_present(self)`
- `test_to_dict_omits_taxonomy_when_absent(self)`
- `_make_repo_with_specs(self)`
