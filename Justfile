test:
  uv run pytest supekku

lint:
  uv run ruff check --fix supekku

pylint_threshold := "9.50"
pylint:
  uv run pylint supekku --fail-under={{pylint_threshold}} --output-format=colorized --reports y
