{
  description = "A python flake-parts shell for spec-driver";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    devshell.url = "github:numtide/devshell";
    pub.url = "github:davidlee/nix-config?dir=/flakes/pub";
    llm-agents.url = "github:numtide/llm-agents.nix";
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
          then inputs.pub.lib.${system}.mkJailedAgents {inherit (inputs) llm-agents;}
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
          meta.mainProgram = "spec-driver";
        };

        projectPkgs = with pkgs; [
          spec-driver

          tree-sitter
          prettier

          uv
          python3
          python3Packages.pylint
          python3Packages.pytest
          pyright
          ruff

          nodejs_latest

          go
          gomarkdoc

          d2
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
          jailed-claude = jailLib.makeJailedClaude {
            profile = "specDev";
            extraPkgs = projectPkgs;
          };
          jailed-codex = jailLib.makeJailedCodex {
            profile = "specDev";
            extraPkgs = projectPkgs;
          };
          jailed-gemini = jailLib.makeJailedGemini {
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
              prettier

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
