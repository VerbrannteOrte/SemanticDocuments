from dataclasses import dataclass
from typing import Any, Optional, Iterable, List


@dataclass
class BoundingBox:
    page_no: int
    x: int
    y: int
    width: int
    height: int


@dataclass
class Property:
    key: str
    value: Any
    confidence: float
    source: str


class Region:
    def __init__(self, boxes: Optional[Iterable[BoundingBox]] = None):
        self.boxes = list()
        if boxes:
            self.boxes.extend(boxes)

    def is_simple(self) -> bool:
        return len(self.boxes) == 1

    def get_boxes(self) -> List[BoundingBox]:
        return self.boxes


class Document:
    pass


class Element:
    def __init__(
        self,
        document: Document,
        region: Region,
        properties: Optional[Iterable[Property]] = None,
    ):
        self.document = document
        self.region = region
        self.properties = list(properties)


class Document:
    def __init__(self):
        super().__init__()

    def __repr__(self):
        return f"Document({id(self)})"

    def __str__(self):
        return "Document()"

    def get_region_image(self, region):
        raise NotImplementedError()

    def get_region_vector(self, region):
        raise NotImplementedError()
