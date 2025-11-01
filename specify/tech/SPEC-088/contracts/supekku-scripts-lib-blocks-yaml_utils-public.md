# supekku.scripts.lib.blocks.yaml_utils

Utilities for formatting YAML blocks.

## Functions

- `format_yaml_list(key, values, level) -> str`: Format a YAML list with proper indentation.

Args:
  key: The YAML key for the list.
  values: List of string values (will be sorted).
  level: Indentation level (0 = no indent).

Returns:
  Formatted YAML list as a string.

Example:
  >>> format_yaml_list("items", ["b", "a"], level=0)
  'items:\n  - a\n  - b'
  >>> format_yaml_list("items", [], level=1)
  '  items: []'
