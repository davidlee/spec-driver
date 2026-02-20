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
- `read_python_module_name(contract_path) -> <BinOp>`: Read the dotted module name from a Python contract's first header.
- `ts_mirror_entries(spec_id, contracts_dir, identifier) -> tuple[Tuple[list[MirrorEntry], list[str]]]`: Produce mirror entries for TypeScript contracts.
- `zig_mirror_entries(spec_id, contracts_dir, identifier) -> tuple[Tuple[list[MirrorEntry], list[str]]]`: Produce mirror entries for Zig contracts.

## Classes

### ContractMirrorTreeBuilder

Builds a .contracts/ symlink tree mirroring source paths to contracts.

*pylint: disable=too-few-public-methods*

#### Methods

- `rebuild(self) -> list[str]`: Rebuild the .contracts/ symlink tree. Returns warnings.

### MirrorEntry

A single mirror symlink mapping.

*pylint: disable=too-few-public-methods*
