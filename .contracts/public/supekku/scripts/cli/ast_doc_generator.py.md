# supekku.scripts.cli.ast_doc_generator

CLI wrapper for the Python AST documentation generator.

Provides backward compatibility with the original CLI interface while
using the new modular library API underneath.

## Functions

- `create_parser() -> argparse.ArgumentParser`: Create argument parser matching original CLI interface.
- `format_status_output(results) -> None`: Format and display status output for results.
- `main() -> None`: Main CLI entry point.
