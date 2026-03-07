{
  description = "A python flake-parts shell for spec-driver";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    devshell.url = "github:numtide/devshell";
  };

  outputs = inputs @ {flake-parts, ...}:
    flake-parts.lib.mkFlake {inherit inputs;} {
      imports = [
        inputs.devshell.flakeModule
      ];

      systems = [
        "x86_64-linux"
        "aarch64-darwin"
      ];

      perSystem = {pkgs, ...}: {
        packages.default = pkgs.python3Packages.buildPythonApplication {
          pname = "spec-driver";
          version = "0.6.2";
          src = ./.;
          pyproject = true;

          build-system = with pkgs.python3Packages; [hatchling];

          dependencies = with pkgs.python3Packages; [
            jinja2
            pyyaml
            python-frontmatter
            typer
          ];

          doCheck = false;
        };

        devshells.default = {
          packages = with pkgs;
            [
              # python
              uv
              python3Packages.python-lsp-server
              python3Packages.python-lsp-ruff
              watchexec

              nodejs_latest
              # bun

              # treesitter
              tree-sitter
              #tree-sitter-grammars.tree-sitter-python
              tree-sitter-grammars.tree-sitter-python
              pyright

              ## language support

              ## go
              go
              gomarkdoc
              # Go
              # go # compiler
              # gopls # language server
              # gomacro
              # gofumpt # strict formatter
              # golangci-lint # linter

              ## zig

              ## diagrams
              d2
              graphviz
            ]
            ++ lib.optionals stdenv.isLinux [];

          commands = [
            {
              name = "sdr";
              help = "uv run spec-driver $@";
              command = ''
                uv run spec-driver $@
              '';
            }
          ];
        };
      };
    };
}
