{ pkgs
, jail
, entrypoint
, projectRoot
, sandboxRoot
, enableNetwork ? true
, extraPermissions ? (_c: [ ])
}:

let
  inherit (pkgs.lib) optional optionals;
in
jail "spec-dev-agent" entrypoint (c:
  with c;
  [
    base
    bind-nix-store-runtime-closure

    # Real repo, writable, including .git
    (rw-bind projectRoot "/workspace/spec-driver")

    # Persistent sandbox state, outside host HOME
    (rw-bind "${sandboxRoot}/home"  "/home/agent")
    (rw-bind "${sandboxRoot}/cache" "/cache")
    (rw-bind "${sandboxRoot}/state" "/state")

    # Minimal runtime shaping
    (add-runtime ''
      bwrap_options+=(
        --tmpfs /tmp
        --chdir /workspace/spec-driver
      )
    '')

    # Stable env inside jail
    (set-env "HOME" "/home/agent")
    (set-env "XDG_CACHE_HOME" "/cache")
    (set-env "XDG_CONFIG_HOME" "/home/agent/.config")
    (set-env "XDG_DATA_HOME" "/state/share")
    (set-env "TMPDIR" "/tmp")

    # Block push-by-default paths
    (set-env "GIT_SSH_COMMAND" "${pkgs.writeShellScript "git-ssh-disabled" ''
      echo "git push over SSH is disabled in this sandbox" >&2
      exit 1
    ''}")
    (set-env "SSH_AUTH_SOCK" "")
    (set-env "GIT_ASKPASS" "")

    # Make sandbox-originated commits obvious
    (set-env "GIT_AUTHOR_NAME" "pi-mono")
    (set-env "GIT_AUTHOR_EMAIL" "pi-mono@local")
    (set-env "GIT_COMMITTER_NAME" "pi-mono")
    (set-env "GIT_COMMITTER_EMAIL" "pi-mono@local")
  ]
  ++ optional enableNetwork network
  ++ extraPermissions c
)
