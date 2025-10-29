# print the revision block json-schema
[group('schema')]
print-revision-block-schema:
    @uv run python supekku/scripts/validate_revision_blocks.py --print-schema

[group('validation')]
validate-workspace-revision-blocks:
    @uv run python supekku/scripts/validate_revision_blocks.py --all --strict --format