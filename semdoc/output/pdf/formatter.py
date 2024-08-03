from pathlib import Path

from semdoc.structure import ElementType as ET
from .document import PDFDocument

cat2tag = {
    ET.Heading1: "H1",
    ET.Paragraph: "P",
}


class PdfExporter:
    def __init__(self, document):
        self.document = document
        self.pdf = PDFDocument()

    def init_pdf(self):
        page_count = self.document.get_property("page_count") or 1
        self.pages = [self.pdf.new_page() for _ in range(page_count)]

        for element in self.document.iter_children():
            self.add_element(self.pdf.document_tag, element)

        # args = namedtuple("filterargs", "color_profile")(None)
        # pdfafilter = llpdf.filters.PDFAFilter(self.pdf, args)
        # pdfafilter.run()

    def add_element(self, parent, element):
        region = element.region()
        if not region:
            return
        assert region.page_no < len(self.pages)
        page = self.pages[region.page_no]
        bitmap = region.get_bitmap()
        tag = parent.create_child(
            tag=cat2tag[element.category], page_nos=[region.page_no]
        )
        img_obj = self.pdf.add_bitmap(bitmap)
        img_obj.draw(
            page,
            region.x,
            region.y,
            bitmap.width,
            bitmap.height,
            tag,
        )

    def write_file(self, path: Path):
        self.pdf.write_file(path)
