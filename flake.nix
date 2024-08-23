{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    poetry2nix.url = "github:nix-community/poetry2nix";
  };
  outputs = { self, nixpkgs, poetry2nix }:
    let
      supportedSystems = [ "x86_64-linux" "x86_64-darwin" "aarch64-linux" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      pkgs = forAllSystems (system: nixpkgs.legacyPackages.${system});
    in
    {
      packages = forAllSystems (system:
        { default = pkgs.${system}.hello;
          pdfbox = pkgs.${system}.callPackage nix/pdfbox.nix {};
          verapdf = pkgs.${system}.callPackage nix/verapdf.nix {};
          pdfuaanalyze = pkgs.${system}.callPackage nix/pdfuaanalyze.nix {};
          taggedpdf = pkgs.${system}.callPackage nix/taggedpdf.nix {};
        });
      apps = forAllSystems (system:
        let
          packages = self.outputs.packages.${system};
        in {
          pdfuaanalyze = {
            type = "app";
            program = "${packages.pdfuaanalyze}/bin/pdfuaanalyze";
          };
          pdfstruct = {
            type = "app";
            program = "${packages.taggedpdf}/bin/pdfstruct";
          };
          annotate = {
            type = "app";
            program = "${packages.taggedpdf}/bin/annotate";
          };
      });
      devShells = forAllSystems (system:
        { default = import nix/devshell.nix {
            pkgs = pkgs.${system};
            packages = self.outputs.packages.${system};
          };
        });
    };
}
