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
      pythonTk= forAllSystems (system:
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
                #ps.python-lsp-server
                #ruff-lsp
                #ps.tkinter
                #tk
                #xdg
              ]))
              #tk
              poppler_utils
              imagemagick
              ghostscript
              qt6.full
              xorg.xcbutil
              xorg.libxcb
              xorg.libxcb.dev
              xorg.xcbutilimage
              xorg.xcbutilimage.dev
              xorg.xcbutilwm
              xorg.xcbutilwm.dev
              xorg.xcbutilkeysyms
              xorg.xcbutilkeysyms.dev
              xorg.xcbutilrenderutil
              xorg.xcbutilrenderutil.dev
              xorg.libX11
              xorg.libX11.dev
              xcb-util-cursor
              libxkbcommon
              fontconfig
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
                     p.libz
                     p.libGL
                     p.glib
                     p.xorg.libSM
                     p.xorg.libICE
                     p.tk
                     p.libxkbcommon
                     p.fontconfig
                     p.freetype
                     p.dbus
                     p.xorg.libX11
                     p.xorg.libX11.dev
                     p.xorg.xcbutil
                     p.xcb-util-cursor
                     p.xorg.libxcb
                     p.xorg.libxcb.dev
                     p.xorg.xcbutilimage
                     p.xorg.xcbutilimage.dev
                     p.xorg.xcbutilwm
                     p.xorg.xcbutilwm.dev
                     p.xorg.xcbutilrenderutil
                     p.xorg.xcbutilrenderutil.dev
                     p.xorg.xcbutilkeysyms
                     p.xorg.xcbutilkeysyms.dev
                   ]}
            '';
          };
        });
    };
}
