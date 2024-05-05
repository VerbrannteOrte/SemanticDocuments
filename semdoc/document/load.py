from pathlib import Path

from .document import Document


def load_document(path: Path):
    return Document(path)
