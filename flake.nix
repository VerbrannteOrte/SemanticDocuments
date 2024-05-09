{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };
  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "x86_64-darwin" "aarch64-linux" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      pkgs = forAllSystems (system: nixpkgs.legacyPackages.${system});
      tex = forAllSystems (system:
        (pkgs.${system}.texlive.combine {
          inherit (pkgs.${system}.texlive)
            scheme-basic
            blindtext
            koma-script
            xcolor
          ;
        })
      );
      pythonTk = forAllSystems (system:
        (pkgs.${system}.python3.override {
          x11Support = true;
          tk = true;
          stripTkinter = false;
        }));
    in
    {
      packages = forAllSystems (system:
        { default = pkgs.${system}.hello; });
      devShells = forAllSystems (system:
        { default = pkgs.${system}.mkShellNoCC {
            packages = with pkgs.${system}; [
              ruff
              pandoc
              poetry
              (pythonTk.${system}.withPackages (ps: [
                ps.python-lsp-server
                ruff-lsp
                ps.tkinter
                tk
              ]))
              tk
              poppler_utils
              imagemagick
              ghostscript
              tesseract
              tex.${system}
            ];
            shellHook = let
              p = pkgs.${system};
            in
              ''
              export TK_LIBRARY="${p.tk}/lib/${p.tk.libPrefix}"
              export LD_LIBRARY_PATH=${p.lib.makeLibraryPath [
                     p.stdenv.cc.cc
#                     p.libz
                     p.libGL
                     p.glib
                     p.xorg.libSM
                     p.xorg.libICE
                     p.tk
                   ]}
            '';
          };
        });
    };
}
