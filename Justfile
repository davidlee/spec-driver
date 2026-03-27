mod wub

check: format lint test pylint-report

test:
  uv run python -m pytest supekku

quickcheck: && lint
  uv run python -m pytest -qx

# ruff - must pass
lint:
  uv run ruff check --fix supekku

format:
  uv run ruff format supekku

pylint-verbose:
  uv run pylint supekku

# use this for whole repo linting
pylint-report:
  uv run python -m supekku.scripts.pylint_report

# lint only specific files - use as you go
pylint-files *args:
  uv run python -m supekku.scripts.pylint_report {{args}}

# lint w/ only specific linter
pylint-only *args:
  uv run pylint supekku --disable=all --extension-pkg-allow-list=pylint.extensions.mccabe --enable={{args}}

ty:
  uv run ty check

lint-imports:
  uvx import-linter

validate:
  uv run spec-driver validate

# run before commits
pre-commit: check format-markdown

format-markdown:
  prettier supekku .spec-driver .contracts --write

## helpers
tech id:
  glow $(spec-driver show spec TECH-{{id}} --path) --pager

prod id:
  glow $(spec-driver show spec PROD-{{id}} --path) --pager

delta id:
  glow $(spec-driver show delta {{id}} --path) --pager

dr id:
  glow $(fd DR-{{id}} .spec-driver/deltas) --pager

plan id:
  glow $(fd IP-{{id}} .spec-driver/deltas) --pager

## Publish
##

publish: publish-pypi brew-update brew-publish

publish-pypi:
  rm -fr dist/
  uv build
  rm dist/.gitignore
  uv publish

# path to the sibling homebrew tap repo
brew-tap := justfile_directory() / "../homebrew-spec-driver"

# extract version from pyproject.toml
version := `cat VERSION`

brew-update:
  #!/usr/bin/env bash
  set -euo pipefail
  if [[ ! -d "{{brew-tap}}" ]]; then
    echo "error: homebrew tap not found at {{brew-tap}}" >&2
    exit 1
  fi
  echo "Updating homebrew formula to {{version}}..."
  python3 "{{brew-tap}}/update-formula.py" "{{version}}"
  cd "{{brew-tap}}"
  git add Formula/spec-driver.rb
  git commit -m "spec-driver {{version}}"
  echo "Tap updated. Run 'cd {{brew-tap}} && git push' to publish."

brew-publish:
  cd /home/david/dev/spec-driver/../homebrew-spec-driver && git push

sort-size:
  @fd '[^_test].py' supekku | xargs wc -l --total=never| tr ' ' 0 | sed -E 's/0s/ s/' | sort | sed -E 's/^0+//'
