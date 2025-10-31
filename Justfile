check: format lint test pylint

test:
  uv run pytest supekku

lint:
  uv run ruff check --fix supekku

format:
  uv run ruff format supekku

pylint:
  uv run pylint supekku

pylint-only *args:
  uv run pylint supekku --disable=all --extension-pkg-allow-list=pylint.extensions.mccabe --enable={{args}}

publish:
  rm -fr dist/
  uv build
  rm dist/.gitignore
  uv publish

sort-size:
  @fd '[^_test].py' supekku | xargs wc -l --total=never| tr ' ' 0 | sed -E 's/0s/ s/' | sort | sed -E 's/^0+//'
