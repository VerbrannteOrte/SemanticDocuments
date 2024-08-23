{ python3Packages, fetchFromGitHub, ... }:
with python3Packages; buildPythonApplication {
  pname = "taggedpdf";
  version = "0.1";
  src = fetchFromGitHub {
    owner = "mibifuzzi";
    repo = "taggedpdf";
    rev = "1c0fda9";
    hash = "sha256-SZs/xnWOevIl7Iv+9lYxLmBe0Fb71+Cpbz1ehsy+30w=";
  };
  doCheck = false;
  doInstallCheck = false;
  dependencies = [ pikepdf pdfminer pypdf2 reportlab ];
  preBuild = ''
    cat > setup.py << EOF
    from setuptools import setup

    setup(
      name='taggedpdf',
      #packages=['someprogram'],
      version='0.1.0',
      #author='...',
      #description='...',
      install_requires=['pikepdf', 'pdfminer', 'pypdf2', 'reportlab'],
      scripts=[
        'pdfstruct.py', 'annotate.py'
      ],
      entry_points={
        # example: file some_module.py -> function main
        #'console_scripts': ['someprogram=some_module:main']
      },
    )
    EOF
  '';
  postInstall = ''
    mv -v $out/bin/pdfstruct.py $out/bin/pdfstruct
    mv -v $out/bin/annotate.py $out/bin/annotate
    echo hello
  '';
}
