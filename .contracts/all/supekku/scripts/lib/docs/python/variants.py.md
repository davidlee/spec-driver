# supekku.scripts.lib.docs.python.variants

Variant coordination for different documentation types.

## Classes

### VariantCoordinator

Coordinates different documentation variants (PUBLIC, ALL, TESTS).

#### Methods

- @classmethod `filter_analysis_for_variant(cls, analysis, variant_spec) -> dict`: Filter analysis results based on variant specification.
- @classmethod `get_files_for_variant(cls, path, variant_spec) -> list[Path]`: Get list of files to process for a given variant.
- @classmethod `get_preset(cls, name) -> VariantSpec`: Get a predefined variant preset by name.
- @classmethod `should_include_symbol(cls, symbol_info, variant_spec) -> bool`: Determine if a symbol should be included based on variant rules.
