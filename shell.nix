{pkgs ? import <nixpkgs> {}}:
let
  spec-driver = builtins.getFlake "github:davidlee/spec-driver";
in
  pkgs.mkShell {
    packages = [spec-driver.packages.${pkgs.system}.default];
  }
