# spec-driver

Specification-driven agentic development toolkit with multi-language spec sync and documentation generation.

Why? 
- Maintain verifiably accurate, evergreen specs covering your _entire system_
- Use cheap, fast, deterministically generated docs to complement and audit the work of messy, stochastic agents
- The combination of markdown and YAML is a surprisingly powerful platform for structured, legible data 
- Tooling joins related entities through a registry for fast lookup, validation, and relational data propagation
- Stop banging rocks together

![workflow diagram](https://supekku.dev/assets/img/simple.svg)

## Status

**Alpha** - Under active development. API and CLI may change.

## Features

- **Multi-language spec sync**: Automatically sync specifications with Go and Python codebases
- **Architecture Decision Records (ADRs)**: Manage and track architectural decisions
- **Delta/Change tracking**: Track and manage specification changes and revisions
- **Documentation generation**: Generate documentation from code using AST analysis
- **Workspace validation**: Ensure consistency across specification artifacts

## Installation

### From GitHub (Development)

```bash
# Install from latest commit
uv add git+https://github.com/davidlee/spec-driver

# Or use with uvx (no installation)
uvx --from git+https://github.com/davidlee/spec-driver spec-driver-sync --help
```

### From PyPI (Future)

```bash
uv add spec-driver
```

## Usage

spec-driver provides multiple CLI commands:

### Specification Sync

```bash
# Sync specifications with codebase
spec-driver-sync

# Dry run to see what would be synced
spec-driver-sync --dry-run

# Sync specific language
spec-driver-sync --language python
```

### Architecture Decision Records

```bash
# Create new ADR
spec-driver-adr new "Use event sourcing for audit trail"

# List ADRs
spec-driver-adr list

# Show ADR details
spec-driver-adr show ADR-001
```

### Deltas and Changes

```bash
# Create delta
spec-driver-delta

# List deltas
spec-driver-delta-list

# Complete delta
spec-driver-delta-complete DELTA-001
```

### Other Commands

- `spec-driver-spec` - Create new specification
- `spec-driver-spec-list` - List specifications
- `spec-driver-requirement` - Manage requirements
- `spec-driver-revision` - Create revision blocks
- `spec-driver-validate-workspace` - Validate workspace consistency

## Project Integration

spec-driver is designed to be integrated into projects using:

1. **Directory structure**: `specify/` and `change/` directories for artifacts
2. **Justfile module**: Integration with project build tools
3. **Agent instructions**: Claude Code integration via agent files

Installation script (future):
```bash
uvx spec-driver install
```

## Development

This package is under active development and API stability is not yet guaranteed.

Current development happens in the [vice](https://github.com/davidlee/vice) repository.

## License

MIT
