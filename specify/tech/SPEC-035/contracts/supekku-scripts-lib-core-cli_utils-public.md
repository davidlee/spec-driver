# supekku.scripts.lib.core.cli_utils

Common utilities for CLI argument parsing and YAML processing.

## Functions

- `add_root_argument(parser, help_text) -> None`: Add a standard --root argument to an argument parser.

Args:
    parser: The ArgumentParser to add the argument to
    help_text: Custom help text for the --root argument
- `create_parser_with_root(description, help_text) -> argparse.ArgumentParser`: Create an ArgumentParser with standard --root argument.

Args:
    description: Description for the parser
    help_text: Custom help text for the --root argument

Returns:
    ArgumentParser with --root argument added
- `parse_yaml_block(match, block_name) -> dict[Tuple[str, Any]]`: Parse YAML from a regex match, with consistent error handling.

Args:
    match: Regex match containing YAML in group 1
    block_name: Name of the block type for error messages

Returns:
    Parsed YAML data as dictionary

Raises:
    ValueError: If YAML parsing fails or result is not a dict
