# uv sync, lock, pytest
[group('test')]
all: uv-sync uv-lock format pytest lint-ruff-fix lint-pylint test

# uv sync
[group('uv')]
uv-sync:
    uv sync

# uv lock
[group('uv')]
uv-lock:
    uv lock

# run pytest (all tests, pretty)
[group('test')]
pytest:
    uv run pytest -v

# run py unittest (all tests, fast)
[group('test')]
test:
    uv run python -m \
    unittest supekku.scripts.lib.spec_utils_test \
    supekku.scripts.lib.sync_engine_test \
    supekku.scripts.lib.create_spec_test \
    supekku.scripts.lib.create_change_test \
    supekku.scripts.lib.backlog_test \
    supekku.scripts.lib.requirements_test \
    supekku.scripts.lib.relations_test \
    supekku.scripts.lib.spec_registry_test \
    supekku.scripts.lib.change_registry_test \
    supekku.scripts.lib.workspace_test \
    supekku.scripts.lib.validator_test \
    supekku.scripts.lib.deterministic_ast_doc_generator_test \
    supekku.scripts.lib.ast_doc_integration_test \
    supekku.scripts.lib.ast_doc_edge_case_test

# AST-based per-module documentation generation (like gomarkdoc for Go)

# python deterministic doc generation (like gomarkdoc)
[group('docs')]
supekku-docs *args:
    uv run python -m supekku.scripts.cli.ast_doc_generator {{args}}

# # Convenience aliases for common operations
# [group('docs')]
# supekku-docs-public:
#     uv run python -m supekku.scripts.cli.ast_doc_generator supekku/scripts/lib --type public

# [group('docs')]
# supekku-docs-all:
#     uv run python -m supekku.scripts.cli.ast_doc_generator supekku/scripts/lib --type all

# [group('docs')]
# supekku-docs-tests:
#     uv run python -m supekku.scripts.cli.ast_doc_generator supekku/scripts/lib --type tests

[group('docs')]
supekku-docs-complete:
    uv run python -m supekku.scripts.cli.ast_doc_generator supekku/scripts/lib --type public
    uv run python -m supekku.scripts.cli.ast_doc_generator supekku/scripts/lib --type all
    uv run python -m supekku.scripts.cli.ast_doc_generator supekku/scripts/lib --type tests

# [group('docs')]
# supekku-docs-check-complete:
#     uv run python -m supekku.scripts.cli.ast_doc_generator supekku/scripts/lib --type public --check
#     uv run python -m supekku.scripts.cli.ast_doc_generator supekku/scripts/lib --type all --check
#     uv run python -m supekku.scripts.cli.ast_doc_generator supekku/scripts/lib --type tests --check

# LINTING: Code quality and style checks
[group('lint')]
lint-ruff:
    uv run ruff check supekku/

[group('lint')]
lint-ruff-fix:
    uv run ruff check --fix supekku/

[group('lint')]
lint-pylint:
    uv run pylint supekku/ --fail-under=9.50

[group('lint')]
format:
    uv run ruff format supekku/

[group('lint')]
lint: lint-ruff-fix lint-pylint
