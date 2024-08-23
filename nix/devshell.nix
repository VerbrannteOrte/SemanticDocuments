{ pkgs, packages, ... }:
let
  tex = pkgs.texlive.combine {
    inherit (pkgs.texlive)
      scheme-basic
      blindtext
      koma-script
      xcolor;
  };
in pkgs.mkShellNoCC {
  packages = with pkgs; [
    ruff
    pandoc
    poetry
    poppler_utils
    imagemagick
    ghostscript
    python312Packages.snakeviz
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
    ocrmypdf
    tesseract
  ] ++
  [
    packages.verapdf
    packages.pdfbox
    packages.taggedpdf
    packages.pdfuaanalyze
    tex
  ];
  shellHook = with pkgs;
    ''
    export TK_LIBRARY="${tk}/lib/${tk.libPrefix}"
    export LD_LIBRARY_PATH=${lib.makeLibraryPath [
      stdenv.cc.cc
      libz
      libGL
      glib
      xorg.libSM
      xorg.libICE
      tk
      libxkbcommon
      fontconfig
      freetype
      dbus
      xorg.libX11
      xorg.libX11.dev
      xorg.xcbutil
      xcb-util-cursor
      xorg.libxcb
      xorg.libxcb.dev
      xorg.xcbutilimage
      xorg.xcbutilimage.dev
      xorg.xcbutilwm
      xorg.xcbutilwm.dev
      xorg.xcbutilrenderutil
      xorg.xcbutilrenderutil.dev
      xorg.xcbutilkeysyms
      xorg.xcbutilkeysyms.dev
    ]}
    '';
}
