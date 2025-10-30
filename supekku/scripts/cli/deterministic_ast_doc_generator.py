#!/usr/bin/env python3
"""CLI wrapper for deterministic AST-based documentation generator.
Uses the refactored API from supekku.scripts.lib.docs.python package.
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from supekku.scripts.lib.docs.python import (
    DocResult,
    ParseCache,
    VariantCoordinator,
    calculate_content_hash,
    generate_docs,
)

# Re-export classes for backward compatibility with tests


# Backward compatibility functions for tests
def check_mode_comparison(
    existing_file: Path, new_content: str,
) -> tuple[bool, str, str]:
    """Compare existing file with new content. Returns (is_same, existing_hash, new_hash)."""
    new_hash = calculate_content_hash(new_content)

    if not existing_file.exists():
        return False, "", new_hash

    existing_content = existing_file.read_text(encoding="utf-8")
    existing_hash = calculate_content_hash(existing_content)
    return existing_hash == new_hash, existing_hash, new_hash


def write_mode_comparison(output_file: Path, new_content: str) -> tuple[str, str, str]:
    """Write file and return status. Returns (status, old_hash, new_hash)."""
    new_hash = calculate_content_hash(new_content)

    if not output_file.exists():
        # File doesn't exist - will be created
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(new_content, encoding="utf-8")
        return "created", "", new_hash

    # File exists - check if content changed
    existing_content = output_file.read_text(encoding="utf-8")
    existing_hash = calculate_content_hash(existing_content)

    if existing_hash == new_hash:
        # Content unchanged
        return "unchanged", existing_hash, new_hash
    # Content changed - write new content
    output_file.write_text(new_content, encoding="utf-8")
    return "changed", existing_hash, new_hash


def format_results(
    results: list[DocResult], check_mode: bool = False, verbose: bool = False,
) -> str:
    """Format results for CLI output."""
    lines = []

    for result in results:
        filename = result.path.name
        status_symbol = get_status_symbol(result.status, check_mode)

        if verbose:
            hash_info = f" (hash: {result.hash[:8]}...)" if result.hash else ""
            lines.append(f"{status_symbol} {filename}: {result.status}{hash_info}")
            if result.error_message:
                lines.append(f"  Error: {result.error_message}")
        else:
            lines.append(f"{status_symbol} {filename}: {result.status}")
            if result.error_message:
                lines.append(f"  Error: {result.error_message}")

    return "\n".join(lines)


def get_status_symbol(status: str, check_mode: bool = False) -> str:
    """Get symbol for status display."""
    if check_mode:
        symbols = {
            "created": "✗",  # Missing file in check mode
            "changed": "✗",  # Changed file in check mode
            "unchanged": "✓",  # Up to date in check mode
            "error": "✗",
        }
    else:
        symbols = {"created": "+", "changed": "~", "unchanged": "=", "error": "✗"}
    return symbols.get(status, "?")


def print_summary(results: list[DocResult], check_mode: bool = False) -> None:
    """Print summary statistics."""
    if not results:
        return

    status_counts = {}
    for result in results:
        status_counts[result.status] = status_counts.get(result.status, 0) + 1

    total = len(results)

    if check_mode:
        unchanged = status_counts.get("unchanged", 0)
        print(f"\nSummary: {unchanged}/{total} files unchanged")
        if unchanged != total:
            print("Run without --check to update files")
    else:
        summary_parts = []
        for status in ["created", "changed", "unchanged"]:
            count = status_counts.get(status, 0)
            if count > 0:
                summary_parts.append(f"{count} {status}")

        if summary_parts:
            print(f"\nSummary: {', '.join(summary_parts)} ({total} files total)")

    # Show error count if any
    error_count = status_counts.get("error", 0)
    if error_count > 0:
        print(f"Errors: {error_count}")


def main() -> None:
    """Main CLI entry point using the refactored API."""
    parser = argparse.ArgumentParser(
        description="Generate deterministic Python module documentation",
    )
    parser.add_argument("path", help="Path to Python file or package directory")
    parser.add_argument(
        "--type",
        choices=["public", "all", "tests"],
        default="public",
        help="Documentation type",
    )
    parser.add_argument(
        "--output-dir",
        default="supekku/docs/deterministic",
        help="Output directory for generated docs",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check mode: verify that generated docs match existing files",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Verbose output showing file hashes",
    )
    parser.add_argument("--no-cache", action="store_true", help="Disable parsing cache")
    parser.add_argument("--cache-dir", type=Path, help="Custom cache directory")
    parser.add_argument(
        "--cache-stats", action="store_true", help="Show cache performance statistics",
    )

    args = parser.parse_args()
    path = Path(args.path)
    output_dir = Path(args.output_dir)

    # Validate path
    if not path.exists():
        print(f"Error: {path} does not exist")
        sys.exit(1)

    # Create variant spec
    try:
        variant_spec = VariantCoordinator.get_preset(args.type)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Generate documentation using new API
    cache_dir = None if args.no_cache else args.cache_dir
    try:
        results = generate_docs(
            unit=path,
            variants=[variant_spec],
            check=args.check,
            output_root=output_dir,
            cache_dir=cache_dir,
        )
    except Exception as e:
        print(f"Error generating documentation: {e}")
        sys.exit(1)

    # Print results
    output = format_results(results, check_mode=args.check, verbose=args.verbose)
    if output:
        print(output)

    # Print summary
    print_summary(results, check_mode=args.check)

    # Show cache stats if requested
    if args.cache_stats and not args.no_cache:
        cache = ParseCache(cache_dir)
        stats = cache.get_stats()
        print(
            f"\nCache Stats: {stats['hits']} hits, {stats['misses']} misses, "
            f"{stats['invalidations']} invalidations ({stats['hit_rate_percent']}% hit rate)",
        )

    # Exit with error code if any results failed
    exit_code = 1 if any(not result.success for result in results) else 0
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
