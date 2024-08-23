{ stdenv, pkgs, fetchurl, fetchFromGitHub, maven, jre, makeWrapper }:

let
  model-integration-zip = fetchurl {
    url = "https://github.com/veraPDF/veraPDF-model/archive/integration.zip";
    sha256 = "sha256-pjs2VzelzG5qB0zEJBnaYJXWMtDGjkMx0wIHbN5FaPc=";
  };
  profiles-integration-zip = fetchurl {
    url = "https://github.com/veraPDF/veraPDF-validation-profiles/archive/integration.zip";
    sha256 = "sha256-D/Ylz4BthOENPB3AVT4vpuIbLMmTGY4FjkG0JrPwFSU=";
  };
in
  maven.buildMavenPackage rec {
    pname = "verapdf";
    version = "1.27.54"; # Change to latest version if needed

    src = fetchFromGitHub {
      owner = "veraPDF";
      repo = "veraPDF-apps";
      rev = "v${version}";
      sha256 = "sha256-Y90r7425r9lLM5NVeVhZVniJj3RXnwPtKDKhNWCJvH8=";
    };

    mvnHash = "sha256-omvk3In/iq9emrDDmC/UReM/LfEr2Di0aN8rylWP1Rk=";
    nativeBuildInputs = [ maven makeWrapper ];

    # preBuild = ''
    #   mkdir -p /build/source/installer/target/staging/model
    #   cp ${model-integration-zip} /build/source/installer/target/staging/model
    #   mkdir -p /build/source/installer/target/staging/profiles
    #   cp ${profiles-integration-zip} /build/source/installer/target/staging/profiles
    # '';

    patchPhase =
    ''
      substituteInPlace greenfield-apps/pom.xml --replace-fail "org.verapdf.apps.GreenfieldGuiWrapper" "org.verapdf.apps.GreenfieldCliWrapper"
    '';

    mvnParameters = "--projects greenfield-apps,gui";

    installPhase = ''
      mkdir -p $out/bin $out/share/verapdf
      install -Dm644 greenfield-apps/target/greenfield-apps-1.27.0-SNAPSHOT.jar $out/share/verapdf/greenfield.jar
      makeWrapper ${jre}/bin/java $out/bin/verapdf \
        --add-flags "-jar $out/share/verapdf/greenfield.jar"
    '';

    meta = {
      description = "VeraPDF is an open-source PDF/A validation tool";
      homepage = "https://verapdf.org/";
      license = pkgs.lib.licenses.gpl3;
      #maintainers = [ stdenv.lib.maintainers.your_handle ];
    };
  }
