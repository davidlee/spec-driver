# supekku.cli.hints

Schema hint output for create commands.

After creating an artifact, suggest relevant `schema show` commands
so users can inspect the YAML block and frontmatter schemas embedded
in the generated template.

## Functions

- `format_schema_hints(artifact_kind) -> list[str]`: Return schema inspection commands relevant to an artifact kind.

Pure function: artifact_kind -> list of hint strings.
Returns empty list for kinds with no registered schemas.
- `print_schema_hints(artifact_kind) -> None`: Print schema inspection hints to stderr for a created artifact.

No-op for kinds with no registered schemas.
