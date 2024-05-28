from PIL import Image
import numpy as np

from . import document
from . import containers


class Region(containers.Bag):
    def __init__(
        self,
        document: document.Document,
        page_no: int,
        x: int,
        y: int,
        w: int,
        h: int,
    ):
        self.document = document
        self.page_no = page_no
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        super().__init__()

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

    def _box_coord(self):
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def approx(self, other):
        if type(other) is not type(self):
            return False
        if other.document != self.document or self.page_no != other.page_no:
            return False
        x_tollerance = self.document.get_pages()[self.page_no - 1].width / 1000
        y_tollerance = self.document.get_pages()[self.page_no - 1].height / 1000
        close = [
            abs(self.x - other.x) < x_tollerance,
            abs(self.y - other.y) < y_tollerance,
            abs(self.x + self.width - other.x - other.width) < x_tollerance,
            abs(self.y + self.height - other.y - other.height) < y_tollerance,
        ]
        return all(close)

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
        return f"Region({self.document!r}, {self.page_no},{self.x}, {self.y}, {self.width}, {self.height}"

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


class Page(Region):
    pass
