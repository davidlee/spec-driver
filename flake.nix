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
        devshells.default = {
          packages = with pkgs;
            [
              # python
              uv
              python3Packages.python-lsp-server
              python3Packages.python-lsp-ruff
              watchexec

              nodejs_latest
              bun
              go
              pyright

              marksman # for serena

              # treesitter
              tree-sitter
              tree-sitter-grammars.tree-sitter-python
              # tree-sitter-grammars.tree-sitter-yaml

              # nodejs_latest
              # Go
              # go # compiler
              # gopls # language server
              # gomacro
              # gofumpt # strict formatter
              # golangci-lint # linter

              # diagram
              # d2
            ]
            ++ lib.optionals stdenv.isLinux [];

          # shellHook = ''
          #   alias sd="uv run spec-driver"
          # '';
          commands = [
            {
              name = "sd";
              help = "uv spec-driver ...";
              command = ''
                uv run spec-driver $@
              '';
            }
          ];
        };
      };
    };
}
