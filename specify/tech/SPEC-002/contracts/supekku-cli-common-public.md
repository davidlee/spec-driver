# supekku.cli.common

Common utilities, options, and callbacks for CLI commands.

## Constants

- `EXIT_FAILURE` - Exit codes
- `EXIT_SUCCESS` - Exit codes
- `RootOption` - Common option definitions for reuse
- `VersionOption` - Version option for main app

## Functions

- `root_option_callback(value) -> Path`: Callback to process root directory option with auto-detection.

Args:
    value: The provided root path, or None to auto-detect

Returns:
    Resolved root path
- `version_callback(value) -> None`: Print version and exit if --version flag is provided.

Args:
    value: Whether --version was specified
