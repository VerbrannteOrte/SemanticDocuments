from pathlib import Path
from llpdf import PDFName, PDFString
from llpdf.EncodeDecode import Filter, EncodedObject
from llpdf.types.Timestamp import Timestamp
import llpdf
import tempfile
import json
import textwrap
from lxml import etree
from operator import itemgetter
from rich import pretty


class PDFDocument:
    def __init__(
        self, title=None, language="en-US", tag_content=True, viewer_pref=True
    ):
        self.next_image_no = 0
        self.next_mcid = 0
        self.llpdf = llpdf.PDFDocument()
        self.pages = []
        self.parent_array = []
        self.metadata = {"title": title}
        self.pages_object = self.llpdf.new_object(
            {
                PDFName("/Type"): PDFName("/Pages"),
                PDFName("/Count"): 0,
                PDFName("/Kids"): [],
            }
        )
        self.root_object = self.llpdf.new_object(
            {
                PDFName("/Type"): PDFName("/Catalog"),
                PDFName("/Pages"): self.pages_object.xref,
            }
        )
        if language:
            self.root_object.content[PDFName("/Lang")] = PDFString(language)
        self.info_object = self.llpdf.new_object(
            {
                PDFName("/Producer"): b"semdoc",
                PDFName("/CreationDate"): Timestamp.localnow()
                .format_pdf()
                .encode("ascii"),
            }
        )
        self.llpdf.trailer[PDFName("/Root")] = self.root_object.xref
        self.llpdf.trailer[PDFName("/Info")] = self.info_object.xref

        if tag_content:
            # number tree that groups structural elements per page
            self.parent_tree = self.new_object(
                content={
                    PDFName("/Nums"): self.parent_array,
                }
            )
            self.struct_root = self.new_object()
            self.document_tag = self.new_object(
                content={
                    PDFName("/Type"): PDFName("/StructElem"),
                    PDFName("/S"): PDFName("/Document"),
                    PDFName("/P"): self.struct_root.xref,
                    PDFName("/K"): [],
                    PDFName("/Lang"): PDFString(language),
                }
            )
            struct_root_content = {
                PDFName("/Type"): PDFName("/StructTreeRoot"),
                PDFName("/ParentTree"): self.parent_tree.xref,
                PDFName("/K"): self.document_tag.xref,
            }
            self.struct_root.set_content(struct_root_content)
            self.root_object.content[PDFName("/StructTreeRoot")] = self.struct_root.xref

        if viewer_pref:
            self.viewer_pref = self.new_object(
                content={
                    PDFName("/DisplayDocTitle"): True,
                }
            )
            self.root_object.content[PDFName("/ViewerPreferences")] = (
                self.viewer_pref.xref
            )

    def set_info(self, key, value):
        self.llpdf.set_info(key, value)

    def new_object(self, content=None, stream=None):
        llpdf_obj = self.llpdf.new_object(content, stream)
        return PDFObject(llpdf_obj, self)

    def new_page(self, width_mm=210, height_mm=297):
        contents_object = self.new_object()
        page_object = self.new_object(
            {
                PDFName("/Type"): PDFName("/Page"),
                PDFName("/Parent"): self.pages_object.xref,
                PDFName("/Contents"): contents_object.xref,
                PDFName("/MediaBox"): [
                    0,
                    0,
                    width_mm / 25.4 * 72,
                    height_mm / 25.4 * 72,
                ],
            }
        )
        self.pages_object.content[PDFName("/Count")] += 1
        self.pages_object.content[PDFName("/Kids")].append(page_object.xref)
        return PDFPage(self, page_object, contents_object)

    def write_file(self, path: Path):
        xml = self._get_metadata()
        stream = EncodedObject.create(xml, compress=False)
        metadata_obj = self.llpdf.new_object(
            content={
                PDFName("/Type"): PDFName("/Metadata"),
                PDFName("/Subtype"): PDFName("/XML"),
            },
            stream=stream,
        )
        self.root_object.content[PDFName("/Metadata")] = metadata_obj.xref
        llpdf.PDFWriter(
            pretty=True, use_object_streams=False, use_xref_stream=False
        ).write(self.llpdf, path)

    def add_bitmap(self, bitmap, dpi=300):
        llpdf_obj = self.llpdf.new_object()
        resource_name = f"/Img{self.next_image_no}"
        self.next_image_no += 1
        bitmap_obj = PDFBitmapObject(llpdf_obj, self, resource_name, bitmap, dpi)
        return bitmap_obj

    def get_next_mcid(self):
        mcid = self.next_mcid
        self.next_mcid += 1
        return mcid

    def _get_metadata(self):
        def ns(ns, tag):
            return f"{{{ns}}}{tag}"

        DC = "http://purl.org/dc/elements/1.1/"
        XMP = "http://ns.adobe.com/xap/1.0/"
        RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        PDFUAID = "http://www.aiim.org/pdfua/ns/id/"
        META = "adobe:ns:meta/"
        XML = "http://www.w3.org/XML/1998/namespace"

        xmpmeta = etree.Element(
            ns(META, "xmpmeta"),
            nsmap={"x": "adobe:ns:meta/", "xml": XML},
        )
        xmpmeta.attrib[ns(META, "xmptk")] = "SemDoc 0.1"

        rdf = etree.SubElement(
            xmpmeta,
            ns(RDF, "RDF"),
            nsmap={
                "rdf": RDF,
            },
            attrib={
                ns(RDF, "about"): "",
            },
        )
        rdf_desc = etree.SubElement(
            rdf,
            ns(RDF, "Description"),
            nsmap={
                "xmp": XMP,
                "dc": DC,
                "pdfuaid": PDFUAID,
            },
        )
        modDate = etree.SubElement(rdf_desc, ns(XMP, "ModifyDate"))
        modDate.text = "2023-07-24T10:59:05Z"

        format = etree.SubElement(rdf_desc, ns(DC, "format"))
        format.text = "application/pdf"

        title = etree.SubElement(rdf_desc, ns(DC, "title"))
        title_alt = etree.SubElement(title, ns(RDF, "Alt"))
        title_li = etree.SubElement(
            title_alt,
            ns(RDF, "li"),
            attrib={ns(XML, "lang"): "x-default"},
        )
        title_li.text = "Hello, world"

        pdfuaid = etree.SubElement(rdf_desc, ns(PDFUAID, "part"))
        pdfuaid.text = "1"

        with open("etree.xml", "rb") as f:
            result = f.read()
        result = etree.tostring(xmpmeta, pretty_print=True, encoding="UTF-8")
        print(result.decode())
        with open("etree.xml", "wb") as f:
            f.write(result)
        return result


class PDFPage:
    def __init__(self, pdf, page_dict, contents):
        self.pdf = pdf
        self.page_dict = page_dict
        self.contents = contents

    def add_resource(self, resource):
        if PDFName("/Resources") not in self.page_dict.content:
            self.page_dict.content[PDFName("/Resources")] = {}
        if PDFName("/XObject") not in self.page_dict.content[PDFName("/Resources")]:
            self.page_dict.content[PDFName("/Resources")][PDFName("/XObject")] = {}
        self.page_dict.content[PDFName("/Resources")][PDFName("/XObject")][
            PDFName(resource.name)
        ] = resource.xref


class PDFObject:
    def __init__(self, obj, pdf):
        self.obj = obj
        self.pdf = pdf

    @property
    def xref(self):
        return self.obj.xref

    @property
    def content(self):
        return self.obj.content

    def append_stream(self, text):
        new_data = text.encode("utf-8")
        if self.obj.stream is not None:
            prev_data = self.obj.stream.decode()
            new_data = prev_data + b"\n" + new_data
        self.obj.set_stream(EncodedObject.create(new_data))

    def set_content(self, content):
        return self.obj.set_content(content)


class PDFBitmapObject(PDFObject):
    def __init__(self, obj, pdf, name, bitmap, dpi=300):
        super().__init__(obj, pdf)
        self._name = name

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            bitmap.save(tmp, format="jpeg", dpi=(dpi, dpi))
            tmp.close()
            pdfimg = llpdf.PDFExtImage.from_file(tmp.name)
        custom_metadata = {
            "resolution_dpi": [dpi, dpi],
            "comment": pdfimg.comment,
        }
        self.obj.set_content(
            {
                PDFName("/Type"): PDFName("/XObject"),
                PDFName("/Subtype"): PDFName("/Image"),
                PDFName("/Interpolate"): True,
                PDFName("/Width"): pdfimg.dimensions.width,
                PDFName("/Height"): pdfimg.dimensions.height,
                PDFName("/CustomMetadata"): PDFString(json.dumps(custom_metadata)),
            }
        )
        self.obj.set_stream(
            EncodedObject(encoded_data=pdfimg.data, filtering=Filter.DCTDecode)
        )
        self.obj.content[PDFName("/ColorSpace")] = PDFName("/DeviceRGB")
        self.obj.content[PDFName("/BitsPerComponent")] = 8

    @property
    def name(self):
        return self._name

    def draw(self, page, x, y, width, height, tag, mcid):
        page_height = 3300
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
            {self._name} Do
          Q
        EMC"""
        page.add_resource(self)
        page_contents = page.contents
        page_contents.append_stream(textwrap.dedent(stream))


class PDFTagObject(PDFObject):
    def __init__(self, obj, pdf):
        super().__init__(obj, pdf)

    def _pages(page_nos: [int]):
        if len(page_nos) == 0:
            return []
        elif len(page_nos) == 1:
            return [self.pdf.pages[page_nos[0]].xref]
        else:
            return [page.xref for page in itemgetter(*page_nos)(self.pdf.pages)]

    def create_child(self, tag: str, page_nos: [int]):
        child_object = self.pdf.llpdf.new_object(
            content={
                PDFName("/Type"): PDFName("/StructElem"),
                PDFName("/S"): PDFName(f"/{tag}"),
                PDFName("/P"): self.xref,
                PDFName("/K"): self.pdf.next_mcid(),
                PDFName("/Pg"): self._pages(page_nos),
            }
        )
        for page_no in page_nos:
            self.pdf.parent_array.append(page_no)
            self.pdf.parent_array.append(child_object.xref)
        self.obj.content[PDFName("/K")].append(child_object.xref)

        return PDFTagObject(child_object, self.pdf)
