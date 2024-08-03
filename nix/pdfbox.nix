{ pkgs, maven, fetchFromGitHub, jre, makeWrapper, ... }:

maven.buildMavenPackage rec {
  pname = "pdfbox";
  version = "3.0.2";

  src = fetchFromGitHub {
    rev = "${version}";
    owner = "apache";
    repo = "pdfbox";
    sha256 = "sha256-IJKu4a8+Q7vc8aqn1UavcmNJIb2nnZIqTJUvOLa8W/0=";
  };

  mvnHash = "sha256-/xD4w6UXgd6uSadJfY3Rmz73/kp0a/g9GfEJlJTgfuM";
  mvnParameters = "-Dmaven.test.skip=true";
  nativeBuildInputs = [ maven makeWrapper pkgs.unzip ];
  doChecks = false;

  buildPhase = ''
    runHook preBuild
    mvn --projects app install
    runHook postBuild
  '';

  installPhase = ''
    runHook preInstall
    mkdir -p $out/bin $out/share/pdfbox
    install -Dm644 app/target/pdfbox-app-${version}.jar $out/share/pdfbox/pdfbox-app-${version}.jar
    makeWrapper ${jre}/bin/java $out/bin/pdfbox \
      --add-flags "-jar $out/share/pdfbox/pdfbox-app-${version}.jar"
    runHook postInstall
  '';

  meta = with pkgs.lib; {
    description = "My Java Application";
    homepage = "http://example.com";
    license = licenses.free;
    #maintainers = with maintainers; [ yourself ];
  };
}
