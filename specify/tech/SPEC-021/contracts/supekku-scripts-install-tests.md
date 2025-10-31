# supekku.scripts.install

Install spec-driver workspace structure and initial files.

This script sets up the necessary directory structure and registry files
for a new spec-driver workspace.

## Functions

- `get_package_root() -> Path`: Find the root directory of the installed spec-driver package.
- `initialize_workspace(target_root, dry_run, auto_yes) -> None`: Initialize spec-driver workspace structure and files.

Args:
  target_root: Root directory where workspace should be initialized
  dry_run: If True, show what would be done without making changes
  auto_yes: If True, automatically confirm all prompts
- `main() -> None`: Main entry point for spec-driver-install command.
- `prompt_for_category(category_name, changes, dest_dir, auto_yes) -> bool`: Prompt user for confirmation to proceed with changes in a category.

Args:
  category_name: Name of the category (e.g., "Templates", "About docs")
  changes: FileChanges object with scan results
  dest_dir: Destination directory to show full paths
  auto_yes: If True, automatically approve without prompting

Returns:
  True if user wants to proceed, False otherwise
