"""Cross-platform path normalization utilities."""

from pathlib import Path, PurePath


class PathNormalizer:
    """Handles cross-platform path normalization for stable identifiers."""

    @staticmethod
    def normalize_path_for_id(file_path: Path, base_path: Path | None = None) -> str:
        """Convert file path to a stable, cross-platform identifier.

        Uses forward slashes and relative paths to ensure consistency
        across Windows/Unix and different Python versions.
        """
        try:
            if base_path:
                # Make relative to base path
                rel_path = file_path.resolve().relative_to(base_path.resolve())
            else:
                # Try to make relative to current working directory
                try:
                    rel_path = file_path.resolve().relative_to(Path.cwd().resolve())
                except ValueError:
                    # If not under CWD, use the path as-is but resolve it
                    rel_path = file_path.resolve()

            # Convert to PurePath to ensure consistent separator handling
            pure_path = PurePath(rel_path)
            # Always use forward slashes for consistency
            return str(pure_path).replace("\\", "/")

        except (ValueError, OSError):
            # Fallback: use the stem if path operations fail
            return file_path.stem

    @staticmethod
    def get_module_name(file_path: Path, base_path: Path | None = None) -> str:
        """Convert file path to Python module name with cross-platform stability."""
        normalized = PathNormalizer.normalize_path_for_id(file_path, base_path)

        # Remove .py extension if present
        normalized = normalized.removesuffix(".py")

        # Convert path separators to dots for module name
        return normalized.replace("/", ".")

    @staticmethod
    def get_output_filename(
        file_path: Path, doc_type: str, base_path: Path | None = None,
    ) -> str:
        """Generate stable output filename for documentation."""
        module_name = PathNormalizer.get_module_name(file_path, base_path)
        # Replace dots with hyphens for filename
        safe_name = module_name.replace(".", "-")
        return f"{safe_name}-{doc_type}.md"
