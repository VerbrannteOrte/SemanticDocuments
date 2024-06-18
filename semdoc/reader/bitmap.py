from PIL import Image

from semdoc.structure import Document, Element, ElementType as ET, Region


class BitmapDocument(Document):
    def __init__(self, path):
        self.path = path
        self.image = Image.open(path)
        self.image = self.image.convert("RGB")
        super().__init__()

    def get_region_bitmap(
        self, page_no: int, x: int, y: int, width: int, height: int
    ) -> Image:
        self._check_page_no(page_no)
        box = (x, y, x + width, x + height)
        return self.image.crop(box)

    def get_region_vector(self, x: int, y: int, width: int, height: int):
        raise ValueError("BitmapDocument does not support vector operations")

    def _check_page_no(self, page_no: int):
        if page_no != 0:
            raise ValueError(f"Invalid page number for single page document: {page_no}")

    def get_geometry(self, page_no: int):
        self._check_page_no(page_no)
        width, height = self.image.size
        return {
            "width": width,
            "height": height,
        }

    def physical_structure(self) -> Element:
        doc = Element(ET.Document)
        doc.set_property("page_count", 1, source="loader", confidence=1.0)
        filename = self.path.name
        doc.set_property("file_name", filename, "loader", 1.0)
        page = Element(ET.Page)
        page.set_property("category", "page", "loader", 1.0)
        page.set_property("page_no", 0, "loader", 1.0)
        width, height = self.image.size
        region = Region(self, 0, 0, 0, width, height)
        page.set_property("region", region, "loader", 1.0)
        doc.add(page)
        return doc
