{
  description = "A python flake-parts shell for spec-driver";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    devshell.url = "github:numtide/devshell";
    jailed-agents.url = "github:davidlee/nix-config?dir=flakes/pub";
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

      perSystem = {
        pkgs,
        system,
        ...
      }: let
        inherit (pkgs) lib stdenv;
        isLinux = stdenv.isLinux;

        jailLib =
          if isLinux
          then inputs.jailed-agents.lib.${system}.jailed-agents
          else {};

        spec-driver = pkgs.python3Packages.buildPythonApplication {
          pname = "spec-driver";
          version = builtins.replaceStrings ["\n"] [""] (builtins.readFile ./VERSION);
          src = ./.;
          pyproject = true;

          build-system = with pkgs.python3Packages; [hatchling];

          dependencies = with pkgs.python3Packages; [
            jinja2
            pyyaml
            python-frontmatter
            textual
            tomlkit
            typer
            watchfiles
          ];

          doCheck = false;
        };

        projectPkgs = with pkgs; [
          spec-driver
          uv
          ruff
          python3Packages.pylint
          python3Packages.pytest
          pyright
          gomarkdoc
          go
          d2
          tree-sitter
        ];

        jailPkgs = lib.optionalAttrs isLinux {
          jailed-pi = jailLib.makeJailedPi {
            profile = "specDev";
            extraPkgs = projectPkgs;
          };
          jailed-pi-research = jailLib.makeJailedPi {
            name = "pi-research";
            profile = "research";
            extraPkgs = projectPkgs;
          };
          jailed-opencode = jailLib.makeJailedOpencode {
            profile = "specDev";
            extraPkgs = projectPkgs;
          };
        };
      in {
        packages =
          jailPkgs
          // {
            default = spec-driver;
          };

        devshells.default = {
          packages =
            (with pkgs; [
              # python
              uv
              python3Packages.python-lsp-server
              python3Packages.python-lsp-ruff
              python3Packages.pytest

              watchexec

              nodejs_latest
              bun

              # treesitter
              tree-sitter
              tree-sitter-grammars.tree-sitter-python
              pyright

              ## go
              go
              gomarkdoc

              ## diagrams
              d2
              graphviz
            ])
            ++ lib.optionals isLinux (lib.attrValues jailPkgs);

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
