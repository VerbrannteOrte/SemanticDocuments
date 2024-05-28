from PIL import Image

from semdoc import structure


class BitmapDocument(structure.Document):
    def __init__(self, path):
        self.path = path
        self.image = Image.open(path)
        self.image = self.image.convert("RGB")
        super().__init__()
        width, height = self.image.size
        page = structure.Page(self, 1, 0, 0, width, height)
        self.add(page)

    def get_region_bitmap(
        self, page_no: int, x: int, y: int, width: int, height: int
    ) -> Image:
        if page_no != 1:
            raise ValueError(f"Invalid page number for single page document: {page_no}")
        box = (x, y, x + width, x + height)
        return self.image.crop(box)

    def get_pages(self):
        return structure.Sequence(self.children[0])

    def get_region_vector(self, x: int, y: int, width: int, height: int):
        raise ValueError("BitmapDocument does not support vector operations")
