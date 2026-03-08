"""Package version utilities."""

from __future__ import annotations


def get_package_version() -> str:
  """Get the installed spec-driver package version.

  Prefers ``importlib.metadata`` (installed package), falls back to
  ``supekku.__version__`` for editable/dev installs.
  """
  from importlib.metadata import PackageNotFoundError, version  # noqa: PLC0415

  try:
    return version("spec-driver")
  except PackageNotFoundError:
    from supekku import __version__  # noqa: PLC0415

    return __version__
