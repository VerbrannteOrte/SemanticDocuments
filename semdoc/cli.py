from pathlib import Path

import typer

from semdoc import document
from semdoc import analyzer
from semdoc import output


def main(
    infile: Annotated[
        Path,
        typer.Argument(
            exists=True,
            dir_okay=False,
            readable=True,
        ),
    ],
):
    doc = document.load_document(infile)
