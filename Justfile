check: format lint test pylint

test:
  uv run pytest supekku

lint:
  uv run ruff check --fix supekku

format:
  uv run ruff format supekku

pylint_threshold := "9.63"
pylint:
  uv run pylint supekku \
    --fail-under={{pylint_threshold}} \
    --output-format=colorized --reports y \
    --indent-string "  "

publish:
  rm -fr dist/
  uv build
  rm dist/.gitignore
  uv publish


