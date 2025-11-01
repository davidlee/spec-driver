"""YAML code block parsers and validators.

This package contains INFRASTRUCTURE for parsing YAML code blocks from markdown files.
These are technical utilities concerned with data format extraction, NOT domain logic.

IMPORTANT SEPARATION OF CONCERNS:
- This package: Parsing, extraction, validation of YAML structure
- Domain packages (changes/, specs/, requirements/): Business logic that USES the blocks

Domain logic (what the data means) stays in domain packages.
Format logic (how to extract the data) lives here.

When factoring out shared utilities, keep them focused on FORMAT concerns:
- Regex extraction patterns
- YAML parsing
- Structural validation (required fields, types)
- NOT: Business rules (what IDs are valid, cross-references, etc.)

Available block types:
- revision: supekku:revision.change@v1
- delta: supekku:delta.relationships@v1
- plan/phase: supekku:plan.overview@v1, supekku:phase.overview@v1
- relationships: supekku:spec.relationships@v1
- verification: supekku:verification.coverage@v1
"""

# Re-export block handlers for convenience
# TODO: Add imports as files are moved/created
