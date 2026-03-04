mod wub

check: format lint test pylint

test:
  uv run pytest supekku

quickcheck: && lint
  uv run pytest -qx

lint:
  uv run ruff check --fix supekku

format:
  uv run ruff format supekku

pylint:
  uv run pylint supekku

pylint-only *args:
  uv run pylint supekku --disable=all --extension-pkg-allow-list=pylint.extensions.mccabe --enable={{args}}


publish: publish-pypi brew-update brew-publish

publish-pypi:
  rm -fr dist/
  uv build
  rm dist/.gitignore
  uv publish

# path to the sibling homebrew tap repo
brew-tap := justfile_directory() / "../homebrew-spec-driver"

# extract version from pyproject.toml
version := `python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])"`

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
