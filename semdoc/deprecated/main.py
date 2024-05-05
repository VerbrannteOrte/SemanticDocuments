from pathlib import Path

import cv2
from rich import pretty
import typer
from typing_extensions import Annotated

import semdoc.document
from semdoc.deprecated.opencv import OpenCVPartitioner
from semdoc.tesseract import run_tesseract


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
    doc = document.Document(infile)
    partitioner = OpenCVPartitioner()
    for page in doc.pages():
        pretty.pprint(run_tesseract(page.as_bitmap()), expand_all=True)
        parts = partitioner.partition(page)
        img = parts.visualize(page.as_bitmap())
        cv2.imshow("segmented page", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    raise typer.Exit()


def run():
    typer.run(main)


if __name__ == "__main__":
    run()
