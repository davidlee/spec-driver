{
  description = "A python flake-parts shell for spec-driver";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    llm-agents.url = "github:numtide/llm-agents.nix";
    devshell.url = "github:numtide/devshell";
    jail-nix.url = "sourcehut:~alexdavid/jail.nix";
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
        self',
        ...
      }: let
        inherit (pkgs) lib stdenv;
        isLinux = stdenv.isLinux;

        # jail-nix (bubblewrap) is Linux-only
        jailPkgs = lib.optionalAttrs isLinux (let
          jail = inputs.jail-nix.lib.init pkgs;

          pi = inputs.llm-agents.packages.${stdenv.system}.pi;
          crush = inputs.llm-agents.packages.${stdenv.system}.crush;
          opencode = inputs.llm-agents.packages.${stdenv.system}.opencode;

          # Packages referenced here are automatically available in the jail
          # via bind-nix-store-runtime-closure.
          agentEntrypoint = pkgs.writeShellScriptBin "agent-shell" ''
            export PATH="${lib.makeBinPath [
              pkgs.zsh
              pkgs.coreutils
              pkgs.git
              # agents
              pi
              crush
              opencode

              pkgs.ripgrep
              pkgs.jq
              pkgs.fd
              pkgs.findutils
              pkgs.curl
              pkgs.which
              pkgs.gnugrep
              pkgs.gawkInteractive
              pkgs.sd
              pkgs.diffutils
              pkgs.gzip
              pkgs.unzip
              pkgs.gnutar
              pkgs.tree
              pkgs.gnused
              pkgs.ps
              pkgs.wget
              pkgs.helix
              pkgs.less
              pkgs.ov
              pkgs.glow
              pkgs.ncurses
            ]}:$PATH"
            export TERMINFO_DIRS="${pkgs.ncurses}/share/terminfo"
            exec ${pkgs.zsh}/bin/zsh
          '';
        in {
          spec-dev-agent = import ./nix/spec-dev-jail.nix {
            inherit pkgs jail;
            entrypoint = agentEntrypoint;
            projectRoot = builtins.getEnv "PROJECT_ROOT";
            sandboxRoot = builtins.getEnv "SANDBOX_ROOT";
          };
        });

        jailApps = lib.optionalAttrs isLinux {
          spec-dev-agent = {
            type = "app";
            program = lib.getExe self'.packages.spec-dev-agent;
          };
        };
      in {
        packages =
          jailPkgs
          // {
            default = pkgs.python3Packages.buildPythonApplication {
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
          };

        apps = jailApps;

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
