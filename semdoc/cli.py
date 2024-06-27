from pathlib import Path
from typing import Annotated

import typer
from rich import pretty

from semdoc.reader import load_path
from semdoc.analyzer import Sequential, TreeOrganizer, Logicalizer
from semdoc.analyzer import surya
from semdoc.gui import show_boxes
from semdoc.output import get_formatter


def main(
    infile: Annotated[
        Path,
        typer.Argument(
            exists=True,
            dir_okay=False,
            readable=True,
        ),
    ],
    outfile: Annotated[
        Path,
        typer.Argument(
            dir_okay=False,
            writable=True,
        ),
    ],
    print_result: Annotated[bool, typer.Option()] = False,
    visualize_result: Annotated[bool, typer.Option()] = False,
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

    logical_pipeline = Sequential()
    organizer = TreeOrganizer()
    logical_pipeline.add(organizer)
    logicalizer = Logicalizer()
    logical_pipeline.add(logicalizer)

    ocr_result = ocr_pipeline.run(physical)
    if visualize_result:
        tree_structure = organizer.run(ocr_result)
        show_boxes(doc, tree_structure)

    logical_result = logical_pipeline.run(ocr_result)
    writer = get_formatter("xml")(logical_result)
    writer.write_file(outfile)

    if print_result:
        pretty.pprint(logical_result.to_dict())


def run():
    typer.run(main)
