from pathlib import Path
from typing import Annotated

import typer

from semdoc import input


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
    doc = input.load_document(infile)


def run():
    typer.run(main)
