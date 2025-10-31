check: format lint test pylint

test:
  uv run pytest supekku

lint:
  uv run ruff check --fix supekku

format:
  uv run ruff format supekku

#pylint_threshold := "9.97"

pylint:
  uv run pylint supekku

pylint-complex:
  uv run pylint supekku --disable=all --extension-pkg-allow-list=pylint.extensions.mccabe --enable=too-complex

pylint-only *args:
  uv run pylint supekku --disable=all --extension-pkg-allow-list=pylint.extensions.mccabe --enable={{args}}

publish:
  rm -fr dist/
  uv build
  rm dist/.gitignore
  uv publish


