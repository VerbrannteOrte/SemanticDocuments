from PIL import Image
import numpy as np
from typing import Self

from . import document


class Region:
    def __init__(
        self,
        document: document.Document,
        page_no: int,
        x: int,
        y: int,
        w: int,
        h: int,
        primary: bool = True,
    ):
        self.document = document
        self.page_no = page_no
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.primary = primary

    def is_simple(self):
        return True

    def __members(self):
        return (self.document, self.page_no, self.x, self.y, self.width, self.height)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__members() == other.__members()
        else:
            return False

    def __hash__(self):
        """TODO This is maybe wrong. Not sure if Region should be mutable or not"""
        return hash(self.__members())

    def __deepcopy__(self, memo):
        """Do not copy the document"""
        return Region(
            self.document,
            self.page_no,
            self.x,
            self.y,
            self.width,
            self.height,
            self.primary,
        )

    def _box_coord(self):
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def approx(self, other):
        if type(other) is not type(self):
            return False
        if other.document is not self.document:
            return False
        if self.page_no != other.page_no:
            return False
        x_tollerance = self.document.get_geometry(self.page_no)["width"] / 500
        y_tollerance = self.document.get_geometry(self.page_no)["height"] / 500
        similar = [
            abs(self.x - other.x) < x_tollerance,
            abs(self.y - other.y) < y_tollerance,
            abs(self.x + self.width - other.x - other.width) < x_tollerance,
            abs(self.y + self.height - other.y - other.height) < y_tollerance,
        ]
        return all(similar)

    @property
    def x2(self):
        return self.x + self.width

    @property
    def y2(self):
        return self.y + self.height

    def incorporate(self, other: Self):
        """Expand the region to fully cover other"""
        self.x = min(self.x, other.x)
        self.y = min(self.y, other.y)
        x2 = max(self.x2, other.x2)
        y2 = max(self.y2, other.y2)
        self.width = x2 - self.x
        self.height = y2 - self.y

    def encompasses(self, other: Self) -> bool:
        if type(other) is not type(self):
            return False
        if other.document is not self.document:
            return False
        if other.page_no != self.page_no:
            return False
        x_tollerance = self.document.get_geometry(self.page_no)["width"] / 1000
        y_tollerance = self.document.get_geometry(self.page_no)["height"] / 1000
        x, y = self.x - x_tollerance, self.y - y_tollerance
        w, h = self.width + 2 * x_tollerance, self.height + 2 * y_tollerance
        return all(
            [
                x < other.x,
                y < other.y,
                x + w > other.x + other.width,
                y + h > other.y + other.height,
            ]
        )

    @property
    def area(self):
        return self.width * self.height

    def coverage(self, other: Self) -> float:
        """Percentage of other region covered by this region"""
        if self.page_no != other.page_no:
            return 0
        if not self.overlaps(other):
            return 0
        intersection = self.intersection(other, False)
        return intersection.area / other.area

    def coverage_y(self, other: Self) -> float:
        """Percentage of the vertical size of the other region that is covered by this region"""
        overlap_top = max(self.y, other.y)
        overlap_bottom = min(self.y + self.height, other.y + other.height)
        overlap_height = overlap_bottom - overlap_top
        return overlap_height / other.height

    def coverage_x(self, other: Self) -> float:
        """Percentage of the horizontal size of the other region that is covered by this region"""
        overlap_top = max(self.x, other.x)
        overlap_bottom = min(self.x + self.width, other.x + other.width)
        overlap_width = overlap_bottom - overlap_top
        return overlap_width / other.width

    def overlaps(self, other: Self) -> bool:
        return self.overlaps_x(other) and self.overlaps_y(other)

    def overlaps_x(self, other: Self) -> bool:
        if self.page_no != other.page_no:
            return False
        return other.x <= self.x <= other.x2 or self.x <= other.x <= self.x2

    def overlaps_y(self, other: Self) -> bool:
        if self.page_no != other.page_no:
            return False
        return other.y <= self.y <= other.y2 or self.y <= other.y <= self.y2

    def intersection(self, other: Self, primary: bool = False) -> Self:
        """Return the intersection of self and other as new region"""
        if self.page_no != other.page_no:
            return None
        if not self.overlaps(other):
            return None
        x = max(self.x, other.x)
        y = max(self.y, other.y)
        x2 = min(self.x2, other.x2)
        y2 = min(self.y2, other.y2)
        w = x2 - x
        h = y2 - y
        intersection = Region(self.document, self.page_no, x, y, w, h, primary)
        return intersection

    def get_bitmap(self) -> Image:
        return self.document.get_region_bitmap(
            self.page_no, self.x, self.y, self.width, self.height
        )

    def get_bitmap_numpy(self):
        channels = {
            "1": 1,
            "L": 1,
            "P": 1,
            "RGB": 3,
            "RGBA": 4,
            "CMYK": 4,
            "YCbCr": 3,
            "LAB": 3,
            "HSV": 3,
            "I": 1,
            "F": 1,
            "LA": 2,
        }
        pil = self.get_bitmap()
        # np_bitmap = np.array(pil.getdata(), dtype=np.uint8).reshape(
        #     self.height, self.width, channels[pil.mode]
        # )
        return np.copy(np.asarray(pil))

    def create_partition(self, x, y, w, h):
        new_x = self.x + x
        new_y = self.y + y
        return Region(self.document, self.page_no, new_x, new_y, w, h)

    def __repr__(self):
        return f"Region({self.document!r}, {self.page_no}, {self.x}, {self.y}, {self.width}, {self.height}, {self.primary})"

    def to_dict(self):
        dict = super().to_dict()
        dict.update(
            page_no=self.page_no,
            x=self.x,
            y=self.y,
            width=self.width,
            height=self.height,
        )
        return dict
