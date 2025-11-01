# spec-driver

Specification-driven development toolkit with multi-language spec sync and documentation generation.

**Why?**
- Maintain verifiably accurate, evergreen specs covering your _entire system_
- Use cheap, fast, deterministically generated docs to complement and audit the work of messy, stochastic agents
- The combination of markdown and YAML is a surprisingly powerful platform for structured, legible data
- Tooling joins related entities through a registry for fast lookup, validation, and relational data propagation
- Stop banging rocks together

![workflow diagram](https://supekku.dev/assets/img/simple.svg)

## Status

**Alpha** - Under active development. API and CLI may change.

## Features

- **Multi-language spec sync**: Automatically sync specifications with Go, Python & TypeScript/JS codebases
- **Architecture Decision Records (ADRs)**: Manage and track architectural decisions
- **Delta/Change tracking**: Relate specification changes, requirements, deltas, implementation plans and revisions
- **Documentation generation**: Generate compact, legible, deterministic markdown documentation from code 
- **Workspace validation**: Ensure consistency across specification artifacts
- **Orphan detection**: Safely remove specs for deleted source files

## Installation

### PyPi package

```bash
# try before you buy (no install)
uvx spec-driver --help

# Or settle in with it 
uv init
uv add speec-driver
uv run spec-driver --help
```

### From GitHub (Development)

```bash
# Install from latest commit
uv init 
uv add git+https://github.com/davidlee/spec-driver
uv run spec-driver --help

# Or use it right off the tubes
uvx --from git+https://github.com/davidlee/spec-driver spec-driver --help
```

## Quick Start

```bash
# Initialize workspace in your project
spec-driver install

# Sync specs with your codebase
spec-driver sync

# List all specs
spec-driver list specs

# Create a new spec
spec-driver create spec --kind tech

# Create a new delta
spec-driver create delta 
```

## Usage

All commands are accessed through the unified `spec-driver` CLI.

### Installation & Setup

```bash
# Initialize spec-driver workspace structure
spec-driver install

# This creates:
# - specify/ directory (for specs, ADRs)
# - change/ directory (for deltas, revisions)
# - .spec-driver/registry/ (for YAML registries)
# - Templates and configuration files
```

### Synchronization

```bash
# Sync all specs with source code (auto-discovery)
spec-driver sync

# Sync only existing registered specs
spec-driver sync --existing

# Sync specific language
spec-driver sync --language python

# Sync specific targets
spec-driver sync go:internal/foo python:module.py

# Dry run to preview changes
spec-driver sync --dry-run

# Check if docs are up-to-date (CI-friendly)
spec-driver sync --check

# Remove specs for deleted source files
spec-driver sync --existing --prune

# Sync ADR registry
spec-driver sync --adr
```

### Creating Artifacts

```bash
# Create a new technical spec
spec-driver create spec --kind tech

# Create a new product spec
spec-driver create spec --kind product

# Create a new delta (change proposal)
spec-driver create delta

# Create a requirement breakout
spec-driver create requirement

# Create a spec revision
spec-driver create revision

# Create an ADR
spec-driver create adr
```

### Listing Artifacts

```bash
# List all specs
spec-driver list specs

# List specs for specific package
spec-driver list specs --package internal/foo

# List specs with package details
spec-driver list specs --packages

# List deltas
spec-driver list deltas

# List deltas by status
spec-driver list deltas --status active

# List all changes (deltas, revisions, audits)
spec-driver list changes

# List changes by kind
spec-driver list changes --kind delta
```

### Architecture Decision Records

```bash
# Create new ADR
spec-driver create adr

# List ADRs
spec-driver list adrs

# List ADRs by status
spec-driver list adrs --status accepted

# Show ADR details
spec-driver show adr ADR-001

# Sync ADR registry
spec-driver sync --adr
```

### Validation

```bash
# Validate workspace consistency
spec-driver validate
```

### Completing Work

```bash
# Mark delta as completed
spec-driver complete delta DE-001
```

## Project Integration

spec-driver integrates into your project using:

1. **Directory structure**: `specify/` and `change/` directories
2. **Registry files**: `.spec-driver/registry/*.yaml` for cross-references
3. **Templates**: `.spec-driver/templates/` for consistent artifact creation
4. **Agent instructions**: `.claude/commands` for AI-assisted development

## Common Workflows

### Daily Development

```bash
# 1. Create a delta for your change
spec-driver create delta

# 2. Write code, update specs as needed

# 3. Sync specs with code
spec-driver sync

# 4. Validate consistency
spec-driver validate

# 5. Mark delta complete
spec-driver complete delta DE-XXX
```

### Onboarding New Code

```bash
# Auto-discover and create specs for existing code
spec-driver sync --language python

# Review what would be created first
spec-driver sync --dry-run
```

### Cleaning Up

```bash
# Find orphaned specs (source files deleted)
spec-driver sync --existing --prune --dry-run

# Remove them
spec-driver sync --existing --prune
```

### Continuous Integration

```bash
# Verify specs are up-to-date
spec-driver sync --check

# Validate workspace
spec-driver validate
```

## Development

This package is under active development and cli API stability is not even hinted at. 

I'll aim not to make breaking changes to data formats, though.

## Related
- [PyPi project](https://pypi.org/project/spec-driver/)
- [npm dependency for TS doc gen](https://www.npmjs.com/package/ts-doc-extract)
- [sort of a website](https://supekku.dev)


## License

MIT