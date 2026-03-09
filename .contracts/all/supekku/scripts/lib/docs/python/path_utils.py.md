# supekku.scripts.lib.docs.python.path_utils

Cross-platform path normalization utilities.

## Classes

### PathNormalizer

Handles cross-platform path normalization for stable identifiers.

#### Methods

- @staticmethod `get_module_name(file_path, base_path) -> str`: Convert file path to Python module name with cross-platform stability.
- @staticmethod `get_output_filename(file_path, doc_type, base_path) -> str`: Generate stable output filename for documentation.
- @staticmethod `normalize_path_for_id(file_path, base_path) -> str`: Convert file path to a stable, cross-platform identifier.

Uses forward slashes and relative paths to ensure consistency
across Windows/Unix and different Python versions.
