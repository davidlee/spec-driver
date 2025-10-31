# supekku.scripts.cli.ast_doc_generator

CLI wrapper for the Python AST documentation generator.

Provides backward compatibility with the original CLI interface while
using the new modular library API underneath.

## Functions

- `_handle_check_result(result) -> int`: Handle check mode result and return error count.
- `_handle_error_result(result) -> int`: Handle error result and return error count.
- `_handle_normal_result(result) -> tuple`: Handle normal result and return (created, changed, unchanged) counts.
- `_print_summary(results, created_count, changed_count, unchanged_count) -> None`: Print summary if not in check mode.
- `create_parser() -> argparse.ArgumentParser`: Create argument parser matching original CLI interface.
- `format_status_output(results) -> None`: Format and display status output for results.
- `main() -> None`: Main CLI entry point.
