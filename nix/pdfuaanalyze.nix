{ pkgs, buildGoModule, fetchFromGitHub, ... }:

buildGoModule {
  pname = "pdfuaanalyze";
  version = "0.1";
  vendorHash = "sha256-yPVj5Y3Dur2nmg1cU/95cu8F1dHQGpolZ6gxVS1oMnU=";
  src = fetchFromGitHub {
    owner = "speedata";
    repo = "pdfuaanalyze";
    rev = "main";
    hash = "sha256-+hlRjG5XVX3EEOAasR4fH06Qaj57P8Ca4rQoVcqU/tw=";
  };
}
