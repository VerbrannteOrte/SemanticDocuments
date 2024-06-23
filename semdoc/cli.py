from pathlib import Path
from typing import Annotated

import typer
from rich import pretty

from semdoc.reader import load_path
from semdoc.analyzer import Sequential
from semdoc.analyzer import surya
from semdoc.gui import show_boxes


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
    doc = load_path(infile)
    physical = doc.physical_structure()

    ocr_pipeline = Sequential()
    text_detector = surya.TextLines()
    ocr_pipeline.add(text_detector)
    text_recognizer = surya.OCR()
    ocr_pipeline.add(text_recognizer)
    layout_recognizer = surya.Layout()
    ocr_pipeline.add(layout_recognizer)

    result = ocr_pipeline.run(physical)
    show_boxes(doc, result)


def run():
    typer.run(main)
