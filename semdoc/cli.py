from pathlib import Path
from typing import Annotated

import typer
from rich import pretty

from semdoc.reader import load_path
from semdoc.gui import show_boxes
from semdoc.writer import get_writer
from semdoc.pipeline import semdoc_pipeline


def main(
    input: Annotated[
        Path,
        typer.Argument(
            exists=True,
            dir_okay=False,
            readable=True,
            help="Input document",
        ),
    ],
    output: Annotated[
        Path,
        typer.Argument(
            dir_okay=False,
            writable=True,
            help="Output document",
        ),
    ],
    print_result: Annotated[
        bool,
        typer.Option(help="Pretty print the semantic tree of the document"),
    ] = False,
    visualize_result: Annotated[
        bool, typer.Option(help="Show the document annotated with detected boxes")
    ] = False,
):
    doc = load_path(input)
    physical = doc.physical_structure()

    pipeline = semdoc_pipeline()
    logical = pipeline.run(physical)

    format = output.suffix[1:]
    writer = get_writer(format)(logical)
    writer.write_file(output)
    if visualize_result:
        show_boxes(doc, logical)
    if print_result:
        pretty.pprint(logical.to_dict())


def run():
    typer.run(main)
