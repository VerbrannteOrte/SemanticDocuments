from pathlib import Path

from semdoc.reader.bitmap import BitmapDocument
from semdoc.structure import Document


def docpath(path: str) -> Path:
    base = Path("tests/documents")
    file = Path(path)
    return base / file


def loadpath(filename: str) -> Document:
    path = docpath(filename)
    doc = BitmapDocument(path)
    return doc
