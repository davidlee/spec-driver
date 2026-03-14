# supekku.scripts.lib.contracts.mirror

Contract mirror tree builder.

Builds a .contracts/ symlink tree at the repo root that mirrors source paths
to generated contract artefacts, enabling intuitive navigation and search.

## Constants

- `PYTHON_KNOWN_VARIANTS` - Python contract variants map 1:1 to canonical view names

## Functions

- `extract_python_variant(filename) -> <BinOp>`: Extract variant from Python contract filename suffix.

Returns None if the suffix isn't a known variant.

- `go_mirror_entries(spec_id, contracts_dir, identifier) -> tuple[Tuple[list[MirrorEntry], list[str]]]`: Produce mirror entries for Go contracts.
- `python_mirror_entries(spec_id, contracts_dir) -> tuple[Tuple[list[MirrorEntry], list[str]]]`: Produce mirror entries for all Python contracts in a SPEC bundle.
- `python_module_to_path(dotted_name) -> str`: Convert dotted module name to file path: 'foo.bar' -> 'foo/bar.py'.
- `python_staging_dir(identifier, contracts_root) -> Path`: Compute the Python staging directory path.

Staging key: python/<identifier-slug> (not spec-id).

- `read_python_module_name(contract_path) -> <BinOp>`: Read the dotted module name from a Python contract's first header.
- `resolve_go_variant_outputs(identifier, contracts_root) -> dict[Tuple[str, Path]]`: Compute per-variant canonical output paths for Go.

Go preserves adapter filenames (interfaces.md, internals.md).
Canonical path: .contracts/<view>/<identifier>/<contract_name>
Root package '.' maps to **root**/ with original filenames preserved.

- `resolve_ts_variant_outputs(identifier, contracts_root) -> dict[Tuple[str, Path]]`: Compute per-variant canonical output paths for TypeScript.

TS discards adapter filenames; canonical leaf is {identifier}.md.
Keys use the adapter's own variant names (api, internal).

- `resolve_zig_variant_outputs(identifier, contracts_root) -> dict[Tuple[str, Path]]`: Compute per-variant canonical output paths for Zig.

Zig discards adapter filenames; canonical leaf is {identifier}.md.
Root package '.' maps to **root**/ with original filenames preserved.

- `ts_mirror_entries(spec_id, contracts_dir, identifier) -> tuple[Tuple[list[MirrorEntry], list[str]]]`: Produce mirror entries for TypeScript contracts.
- `zig_mirror_entries(spec_id, contracts_dir, identifier) -> tuple[Tuple[list[MirrorEntry], list[str]]]`: Produce mirror entries for Zig contracts.

## Classes

### ContractMirrorTreeBuilder

Builds a .contracts/ symlink tree mirroring source paths to contracts.

_pylint: disable=too-few-public-methods_

#### Methods

- `rebuild(self) -> list[str]`: Rebuild compat symlinks: SPEC-\*/contracts/ → .contracts/.

Canonical contract files live in .contracts/<view>/<path>.
For each registered spec, create compat symlinks from
SPEC-\*/contracts/<view>/<path> pointing into .contracts/.

### MirrorEntry

A single mirror symlink mapping.

_pylint: disable=too-few-public-methods_
