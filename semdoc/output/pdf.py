from pathlib import Path
from pikepdf import Pdf, Page
from llpdf import PDFName, PDFString
from llpdf.EncodeDecode import Filter, EncodedObject
from llpdf.img.PDFExtImage import PixelFormat
import llpdf
import tempfile
import json
import textwrap

from semdoc.structure import ElementType as ET

cat2tag = {
    ET.Heading1: "H1",
    ET.Paragraph: "P",
}


class PdfExporter:
    def __init__(self, document):
        self.document = document
        self.next_image_no = 0
        self.next_mcid = 0
        self.pdf = llpdf.PDFDocument()
        self.hlpdf = llpdf.HighlevelPDFFunctions(self.pdf)
        self.hlpdf.initialize_pages(author="Michael Volz", title="Test-Titel")
        self.pdf.set_info("Creator", "semdoc1")
        self.pages = []
        self.parent_array = []

        page_count = self.document.get_property("page_count") or 1
        for _ in range(page_count):
            self.pages.append(self.hlpdf.new_page())

        # number tree that groups structural elements per page
        parent_tree = self.pdf.new_object(
            content={
                PDFName("/Nums"): self.parent_array,
            }
        )

        struct_root = self.pdf.new_object()
        document_tag = self.pdf.new_object(
            content={
                PDFName("/Type"): PDFName("/StructElem"),
                PDFName("/S"): PDFName("/Document"),
                PDFName("/P"): struct_root.xref,
                PDFName("/K"): [],
                PDFName("/Lang"): PDFString("(en-US)"),
            }
        )

        for element in self.document.iter_children():
            self.add_element(document_tag, element)

        struct_root_content = {
            PDFName("/Type"): PDFName("/StructTreeRoot"),
            PDFName("/ParentTree"): parent_tree.xref,
            PDFName("/K"): document_tag.xref,
        }
        struct_root.set_content(struct_root_content)

    def add_element(self, parent, element):
        region = element.region()
        if not region:
            return
        assert region.page_no < len(self.pages)
        page = self.pages[region.page_no]
        bitmap = region.get_bitmap()
        img_name = self.add_bitmap(page, bitmap)
        mcid = self.next_mcid
        self.next_mcid += 1
        tag = cat2tag[element.category]
        self.draw_bitmap(
            page, img_name, region.x, region.y, bitmap.width, bitmap.height, tag, mcid
        )
        tag_object = self.pdf.new_object(
            content={
                PDFName("/Type"): PDFName("/StructElem"),
                PDFName("/S"): PDFName(f"/{tag}"),
                PDFName("/P"): parent.xref,
                PDFName("/K"): mcid,
                PDFName("/Pg"): page.page_obj.xref,
            }
        )
        self.parent_array.append(region.page_no)
        self.parent_array.append(tag_object.xref)
        parent.content[PDFName("/K")].append(tag_object.xref)

    def draw_bitmap(self, page, img_name, x, y, width, height, tag, mcid):
        page_height = 3300
        page_width = 2550
        offset_x = x
        offset_y = page_height - y - height
        offset_x_dots = offset_x / 300 * 72
        offset_y_dots = offset_y / 300 * 72
        width_dots = width / 300 * 72
        height_dots = height / 300 * 72
        stream = f"""
        /{tag} <</MCID {mcid:d} >>BDC
          q
            {width_dots:f} 0 0 {height_dots:f} {offset_x_dots:f} {offset_y_dots:f} cm
            {img_name} Do
          Q
        EMC"""
        page.append_stream(textwrap.dedent(stream))
        # assert False

    def add_bitmap(self, page, bitmap):
        dpi = 300
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            bitmap.save(tmp, format="jpeg", dpi=(dpi, dpi))
            tmp.close()
            pdfimg = llpdf.PDFExtImage.from_file(tmp.name)
        custom_metadata = {
            "resolution_dpi": [dpi, dpi],
            "comment": pdfimg.comment,
        }
        image = self.pdf.new_object(
            {
                PDFName("/Type"): PDFName("/XObject"),
                PDFName("/Subtype"): PDFName("/Image"),
                PDFName("/Interpolate"): True,
                PDFName("/Width"): pdfimg.dimensions.width,
                PDFName("/Height"): pdfimg.dimensions.height,
                PDFName("/CustomMetadata"): PDFString(json.dumps(custom_metadata)),
            }
        )
        image.set_stream(
            EncodedObject(encoded_data=pdfimg.data, filtering=Filter.DCTDecode)
        )
        image.content[PDFName("/ColorSpace")] = PDFName("/DeviceRGB")
        image.content[PDFName("/BitsPerComponent")] = 8

        page_obj = page.page_obj
        if PDFName("/Resources") not in page_obj.content:
            page_obj.content[PDFName("/Resources")] = {}
        if PDFName("/XObject") not in page_obj.content[PDFName("/Resources")]:
            page_obj.content[PDFName("/Resources")][PDFName("/XObject")] = {}
        image_name = f"/Img{self.next_image_no}"
        self.next_image_no += 1
        page_obj.content[PDFName("/Resources")][PDFName("/XObject")][
            PDFName(image_name)
        ] = image.xref
        return image_name

    def write_file(self, path: Path):
        # pdf = Pdf.new()
        # page_count = self.document.get_property("page_count") or 1
        # for _ in range(page_count):
        #     pdf.add_blank_page()
        # for element in self.document.iter_children():
        #     self.add_element(pdf, element)
        # pdf.save(path)

        llpdf.PDFWriter().write(self.pdf, path)
