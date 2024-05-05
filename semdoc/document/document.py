from pathlib import Path

import cv2

from .partitioning import Partitioning


class Document:
    def __init__(self, path: Path):
        self.path = path
        self.page = Page(cv2.imread(path.as_posix()))
        self.partitioning = Partitioning()

    def __repr__(self):
        return "Document()"

    def __str__(self):
        return "Document()"

    def pages(self):
        yield self.page

    def get_region_image(self, region):
        pass

    def get_partitioning(self):
        return self.partitioning


class Page:
    def __init__(self, image):
        self.image = image

    def as_bitmap(self):
        return self.image
