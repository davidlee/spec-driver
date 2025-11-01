# supekku.scripts.cli.deterministic_ast_doc_generator

CLI wrapper for deterministic AST-based documentation generator.
Uses the refactored API from supekku.scripts.lib.docs.python package.

## Functions

- `check_mode_comparison(existing_file, new_content) -> tuple[Tuple[bool, str, str]]`: Compare existing file with new content.

Returns (is_same, existing_hash, new_hash). - Backward compatibility functions for tests
- `format_results(results, check_mode, verbose) -> str`: Format results for CLI output.
- `get_status_symbol(status, check_mode) -> str`: Get symbol for status display.
- `main() -> None`: Main CLI entry point using the refactored API.
- `print_summary(results, check_mode) -> None`: Print summary statistics.
- `write_mode_comparison(output_file, new_content) -> tuple[Tuple[str, str, str]]`: Write file and return status. Returns (status, old_hash, new_hash).
