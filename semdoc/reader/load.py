from pathlib import Path

from .bitmap import BitmapDocument
from .mupdf import MupdfDocument
from semdoc.structure import Document


def load_path(path: Path) -> Document:
    ext = path.suffix
    if ext == ".pdf":
        return MupdfDocument(path)
    return BitmapDocument(path)
