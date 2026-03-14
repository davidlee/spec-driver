# supekku.cli.main

Main CLI entry point for spec-driver unified interface.

## Constants

- `_original_command_invoke` - Groups (click.Group) are excluded so help/no-args paths don't trigger emission.
- `app` - Main Typer application

## Functions

- @app.callback `_app_callback(_version) -> None`: Process global options and initialize path configuration.
- `_emit(argv, exit_code) -> None`: Emit event if a leaf command was invoked and events are enabled.
- `_init_paths_from_config() -> <BinOp>`: Initialize path constants from workflow.toml if in a repo.

Silently skips if not in a repo — commands like --help and install
must work without a workspace.

Returns the loaded config dict, or `None` if not in a workspace.

- `_tracking_invoke(self, ctx)` - type: ignore[no-untyped-def]
- `_warn_if_version_stale(config) -> None`: Emit a stderr warning when the installed version has drifted.

Compares `spec_driver_installed_version` in _config_ (from
`workflow.toml`) against the running package version. Skipped
when the active command is `install` (which will stamp the version
itself).

- `main() -> None`: Spec-driver CLI main entry point.
- @app.command(tui, help=Launch the TUI artifact browser) `tui_command() -> None`: Launch the interactive TUI artifact browser.
