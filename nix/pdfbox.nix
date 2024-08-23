{ pkgs, maven, fetchFromGitHub, jre, makeWrapper, ... }:

maven.buildMavenPackage rec {
  pname = "pdfbox";
  version = "3.0.3";

  src = fetchFromGitHub {
    rev = "${version}";
    owner = "apache";
    repo = "pdfbox";
    sha256 = "sha256-fXmyVYJIghXpB1BfYw3qAF1f42d8Y9jX1jx//r+jC7k=";
  };

  mvnHash = "sha256-w0p7zGojm76uxJqoZX6FUb7PwG492gF4UnI/Hn9ijqE=";
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
