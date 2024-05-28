from pathlib import Path

from .bitmap import BitmapDocument
from semdoc.structure import Document


def load_path(path: Path) -> Document:
    return BitmapDocument(path)
