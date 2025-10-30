test:
  uv run pytest supekku

lint:
  uv run ruff check --fix supekku

pylint:
  uv run pylint supekku
