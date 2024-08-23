from pathlib import Path
from rich import pretty

from semdoc.structure import ElementType as ET
from .document import PDFDocument
from semdoc.structure import Document, Region, ElementType as EType

cat2tag = {
    ET.Heading1: "H1",
    ET.Paragraph: "P",
    ET.Document: "",
    ET.TextLine: "",
}


def _to_mm(pxls):
    return pxls / 300 * 25.4


class PdfExporter:
    def __init__(self, document):
        self.document = document
        self.pdf = PDFDocument()
        page_count = self.document.get_property("page_count") or 1
        self.pages = [self.pdf.new_page() for _ in range(page_count)]
        self.font = self.pdf.create_font(name="Helvetica", type="Type1")
        self.print_element(document)

    def print_element(self, element):
        tag = cat2tag[element.category]
        if tag not in ["artifact", ""]:
            self.pdf.start_tag(tag)

        region = element.region()
        if region and region.primary:
            assert region.page_no < len(self.pages)
            page = self.pages[region.page_no]
            pos = (_to_mm(region.x), _to_mm(region.y))

            text = element.get_text()
            size = 12
            if len(text) > 0:
                page.write_text(pos, self.font, size, text, visible=False)

            bitmap = region.get_bitmap()
            img_obj = self.pdf.add_bitmap(bitmap)
            is_artifact = tag == "artifact" or len(text) > 0
            page.draw_image(pos, img_obj, artifact=is_artifact)

        for child in element.children:  # element.iter_children():
            self.print_element(child)

        if tag not in ["artifact", ""]:
            self.pdf.end_tag()

    def init_pdf(self):
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