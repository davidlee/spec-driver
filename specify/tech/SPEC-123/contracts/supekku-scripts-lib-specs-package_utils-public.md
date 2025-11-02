# supekku.scripts.lib.specs.package_utils

Utilities for Python package detection and identification.

Provides functions to identify leaf packages, validate package paths,
and resolve files to their containing packages. Used for package-level
tech spec granularity (PROD-005).

## Functions

- `find_all_leaf_packages(root) -> list[Path]`: Find all leaf packages under a root directory.

Recursively searches for all directories that are leaf packages
(have __init__.py and no child packages).

Args:
    root: Root directory to search from

Returns:
    Sorted list of paths to leaf packages

Examples:
    >>> packages = find_all_leaf_packages(Path("supekku"))
    >>> len(packages)
    16
    >>> Path("supekku/scripts/lib/formatters") in packages
    True
- `find_package_for_file(file_path) -> <BinOp>`: Find the containing Python package for a given file.

Traverses up from the file path to find the nearest directory
containing an __init__.py file (a Python package).

Args:
    file_path: Path to a Python file

Returns:
    Path to the containing package directory, or None if not in a package

Examples:
    >>> file_path = Path("supekku/scripts/lib/formatters/change_formatters.py")
    >>> find_package_for_file(file_path)
    Path("supekku/scripts/lib/formatters")
    >>> find_package_for_file(Path("some_script.py"))
    None
- `is_leaf_package(path) -> bool`: Check if path is a leaf Python package.

A leaf package is a directory that:
1. Contains an __init__.py file (is a Python package)
2. Has no child directories that are also packages

Args:
    path: Directory path to check

Returns:
    True if path is a leaf package, False otherwise

Examples:
    >>> is_leaf_package(Path("supekku/scripts/lib/formatters"))
    True
    >>> is_leaf_package(Path("supekku/scripts/lib"))  # Has child packages
    False
- `validate_package_path(path) -> None`: Validate that a path is a valid Python package.

Args:
    path: Directory path to validate

Raises:
    FileNotFoundError: If path doesn't exist
    ValueError: If path is not a directory
    ValueError: If path doesn't contain __init__.py

Examples:
    >>> validate_package_path(Path("supekku/cli"))  # OK
    >>> validate_package_path(Path("nonexistent"))
    FileNotFoundError: Package path does not exist: nonexistent
    >>> validate_package_path(Path("some_file.py"))
    ValueError: Package path must be a directory: some_file.py
