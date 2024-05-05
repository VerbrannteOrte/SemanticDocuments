from pathlib import Path

import cv2


class Document:
    def __init__(self, path: Path):
        self.path = path
        self.page = Page(cv2.imread(path.as_posix()))

    def __repr__(self):
        return "Document()"

    def __str__(self):
        return "Document()"

    def pages(self):
        yield self.page


class Page:
    def __init__(self, image):
        self.image = image

    def as_bitmap(self):
        return self.image


def load_document(path: Path):
    return Document(path)
