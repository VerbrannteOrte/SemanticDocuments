import pymupdf
from PIL import Image

from semdoc.structure import Document, Element, ElementType as ET, Region


class MupdfDocument(Document):
    def __init__(self, path, dpi=300):
        self.path = path
        self.mupdf_doc = pymupdf.open(path)
        self.dpi = dpi
        super().__init__()

    def _check_page_no(self, page_no: int):
        if page_no + 1 > self.mupdf_doc.page_count or page_no < 0:
            raise ValueError(
                f"Invalid page number: {page_no}. Document has {self.mupdf_doc.page_count} pages."
            )

    def __repr__(self):
        return f"MupdfDocument({self.path!r})"

    def get_region_bitmap(
        self, page_no: int, x: int, y: int, width: int, height: int
    ) -> Image:
        self._check_page_no(page_no)
        page = self.mupdf_doc[page_no]
        x1, y1 = x + width, y + height
        x0, y0, x1, y1 = map(self._to_unit, (x, y, x1, y1))
        rect = pymupdf.IRect(x0, y0, x1, y1)
        pixmap = page.get_pixmap(clip=rect, dpi=self.dpi)
        img = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
        return img

    def _to_pixel(self, pdfunit: float) -> int:
        return round(pdfunit / 72 * self.dpi)

    def _to_unit(self, pixel: int) -> float:
        return pixel / self.dpi * 72

    def get_geometry(self, page_no: int):
        self._check_page_no(page_no)
        page = self.mupdf_doc[page_no]
        rect = page.rect
        width, height = self._to_pixel(rect.width), self._to_pixel(rect.height)
        return {
            "width": width,
            "height": height,
        }

    def physical_structure(self) -> Element:
        doc = Element(ET.Document)
        doc.set_property("page_count", self.mupdf_doc.page_count, "loader")
        doc.set_property("file_name", self.path.name, "loader")
        for page_no, page in enumerate(self.mupdf_doc):
            page_elmnt = Element(ET.Page)
            page_elmnt.set_property("page_no", page_no, "loader")
            width = self._to_pixel(page.rect.width)
            height = self._to_pixel(page.rect.height)
            region = Region(self, page_no, 0, 0, width, height)
            page_elmnt.set_property("region", region, "loader")
            doc.add(page_elmnt)
        return doc
