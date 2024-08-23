{ lib,
  mupdf,
  python3,
  freetype,
  harfbuzz,
  openjpeg,
  jbig2dec,
  libjpeg_turbo,
  gumbo,
  pkg-config,
  swig,
  psutils,
  libclang,
  mkPoetryApplication,
  defaultPoetryOverrides,
  python312Packages,
  ... }:
let
  addBuildInputs = buildInputs:
    (old: {
      buildInputs = (old.buildInputs or []) ++ buildInputs;
    });
in mkPoetryApplication {
  projectDir = ./..;
  #preferWheels = true;
  overrides = defaultPoetryOverrides.extend
    (final: prev: {
      llpdf = prev.llpdf.overridePythonAttrs (addBuildInputs [ prev.setuptools ]);
      fsspec = prev.fsspec.overridePythonAttrs (addBuildInputs [ prev.hatchling prev.hatch-vcs ]);
      pymupdf = python312Packages.pymupdf;
      pyside6 = python312Packages.pyside6;
        # let
        #   mupdf-cxx = mupdf.overrideAttrs (final: prev:
        #     {
        #       enableOcr = true;
        #       enableCxx = true;
        #       enablePython = true;
        #       #python3 = python3;
        #     });
        # in
        #   prev.pymupdf.overrideAttrs
        #     (old: {
        #       buildInputs =
        #         (old.buildInputs or []) ++ [
        #           prev.setuptools
        #           freetype
        #           harfbuzz
        #           openjpeg
        #           jbig2dec
        #           libjpeg_turbo
        #           gumbo
        #         ];
        #       nativeBuildInputs =
        #         (old.nativeBuildInputs or []) ++ [
        #           pkg-config
        #           swig
        #           psutils
        #           libclang
        #         ];
        #       propagatedBuildInputs = [ mupdf-cxx ];
        #       env = (old.env or {}) // {
        #         # force using system MuPDF (must be defined in environment and empty)
        #         PYMUPDF_SETUP_MUPDF_BUILD = "";
        #         # provide MuPDF paths
        #         PYMUPDF_MUPDF_LIB = "${lib.getLib mupdf-cxx}/lib";
        #         PYMUPDF_MUPDF_INCLUDE = "${lib.getDev mupdf-cxx}/include";
        #       };
        #       # postPatch = ''
        #       #   substituteInPlace pyproject.toml \
        #       #   --replace-fail '"swig",' "" \
        #       #   --replace-fail "libclang" "clang"
        #       #   '';
        #     });
      # pymupdfb = prev.pymupdfb.overridePythonAttrs (addBuildInputs [ prev.setuptools ]);
      pypdfium2 = prev.pymupdfb.overridePythonAttrs (addBuildInputs [ prev.setuptools ]);
      safetensors = prev.pymupdfb.overridePythonAttrs (addBuildInputs [ prev.maturin ]);
      iopath = prev.iopath.overridePythonAttrs (addBuildInputs [ prev.setuptools ]);
      pytoolconfig = prev.pytoolconfig.overridePythonAttrs (addBuildInputs [ prev.pdm-backend ]);
});
}
