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
from collections import defaultdict


def _mm_to_dots(x: float):
    return (x / 25.4) * 72


class PDFDocument:
    def __init__(
        self, title=None, language="en-US", tag_content=True, viewer_pref=True
    ):
        self.next_image_no = 0
        self.llpdf = llpdf.PDFDocument()
        self.pages = []
        self.parent_dict = {}
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
            self.parent_tree = self.new_object()
            self.struct_root = self.new_object()
            document_tag = self.new_object(
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
                PDFName("/K"): [document_tag.xref],
            }
            self.struct_root.content = struct_root_content
            self.root_object.content[PDFName("/StructTreeRoot")] = self.struct_root.xref
            self.document_tag = PDFTagObject(
                document_tag.obj, document_tag.pdf, "Document", None
            )
            self.current_tag = self.document_tag

        if viewer_pref:
            self.viewer_pref = self.new_object(
                content={
                    PDFName("/DisplayDocTitle"): True,
                }
            )
            self.root_object.content[PDFName("/ViewerPreferences")] = (
                self.viewer_pref.xref
            )

    def add_to_parent_tree(self, page_no, tag_object):
        index = page_no - 1
        self.parent_dict[index].append(tag_object.xref)

    def set_info(self, key, value):
        self.llpdf.set_info(key, value)

    def new_object(self, content=None, stream=None):
        llpdf_obj = self.llpdf.new_object(content, stream)
        return PDFObject(llpdf_obj, self)

    def new_page(self, width_mm=210, height_mm=297):
        page_no = self.pages_object.content[PDFName("/Count")] + 1
        contents_object = self.new_object()
        page_object = self.new_object(
            {
                PDFName("/Type"): PDFName("/Page"),
                PDFName("/Parent"): self.pages_object.xref,
                PDFName("/Contents"): contents_object.xref,
                PDFName("/StructParents"): page_no - 1,
                PDFName("/MediaBox"): [
                    0,
                    0,
                    # Should this be rounded or not? I found rounded sizes for
                    # e.g. A4 on the internet but it works with exact numbers
                    # too
                    width_mm / 25.4 * 72,
                    height_mm / 25.4 * 72,
                ],
            }
        )
        self.pages_object.content[PDFName("/Count")] = page_no
        self.pages_object.content[PDFName("/Kids")].append(page_object.xref)
        self.parent_dict[page_no - 1] = []
        return PDFPage(
            self,
            page_object,
            contents_object,
            page_no,
        )

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

        parent_array = []
        for page_no, elements in self.parent_dict.items():
            parent_array.append(page_no)
            element_object = self.new_object(content=elements)
            parent_array.append(element_object.xref)
        self.parent_tree.content = {
            PDFName("/Nums"): parent_array,
        }

        llpdf.PDFWriter(
            pretty=True, use_object_streams=False, use_xref_stream=False
        ).write(self.llpdf, path)

    def add_bitmap(self, bitmap, dpi=300):
        llpdf_obj = self.llpdf.new_object()
        resource_name = f"/Img{self.next_image_no}"
        self.next_image_no += 1
        bitmap_obj = PDFBitmapObject(llpdf_obj, self, resource_name, bitmap, dpi)
        return bitmap_obj

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

        result = etree.tostring(xmpmeta, pretty_print=True, encoding="UTF-8")
        return result

    def start_tag(self, tag):
        if not self.current_tag:
            raise ValueError("Document needs to be tagged for start_tag()")
        self.current_tag = self.current_tag.create_child(tag)
        return self.current_tag

    def end_tag(self):
        if not self.current_tag:
            raise ValueError("Document needs to be tagged for end_tag()")
        if self.current_tag is self.document_tag:
            raise ValueError("Cannot end the top level document tag")
        self.current_tag = self.current_tag.parent

    def create_font(self, type: str, name: str):
        font_obj = self.llpdf.new_object()
        return PDFFont(font_obj, self, type, name)


class PDFPage:
    def __init__(self, pdf, page_dict, contents, page_no):
        self.next_mcid = 0
        self.pdf = pdf
        self.page_dict = page_dict
        self.contents = contents
        self.page_no = page_no
        self._font_dict = {}
        if PDFName("/Resources") not in self.page_dict.content:
            self.page_dict.content[PDFName("/Resources")] = {}
        self._resources = self.page_dict.content[PDFName("/Resources")]

    def get_next_mcid(self):
        mcid = self.next_mcid
        self.next_mcid += 1
        return mcid

    def add_xobject(self, resource):
        if PDFName("/XObject") not in self._resources:
            self._resources[PDFName("/XObject")] = {}
        self._resources[PDFName("/XObject")][PDFName(resource.name)] = resource.xref

    def ensure_font(self, font):
        if font.xref in self._font_dict:
            return self._font_dict[font.xref]
        if PDFName("/Font") not in self._resources:
            self._resources[PDFName("/Font")] = {}
        fontobj = self._resources[PDFName("/Font")]
        next_id = len(fontobj) + 1
        font_name = f"/F{next_id}"
        fontobj[PDFName(font_name)] = font.xref
        return font_name

    def _get_tag_line(self, artifact: bool):
        if artifact:
            tag_line = "/Artifact BMC"
        else:
            mcid = self.get_next_mcid()
            tag = self.pdf.current_tag.tag
            tag_line = f"/{tag} <</MCID {mcid} >>BDC"

            self.pdf.current_tag.obj.content[PDFName("/K")].append(mcid)
            self.pdf.add_to_parent_tree(self.page_no, self.pdf.current_tag)
            pages_in_tag = set(self.pdf.current_tag.obj.content[PDFName("/Pg")])
            pages_in_tag.add(self.page_dict.xref)
            self.pdf.current_tag.obj.content[PDFName("/Pg")] = list(pages_in_tag)

        return tag_line

    def draw_image(self, pos, image, artifact: bool = False):
        tag_line = self._get_tag_line(artifact)
        x, y = map(_mm_to_dots, pos)
        width, height = map(_mm_to_dots, image.size)
        y = self.height - height - y
        instructions = f"""
        {tag_line}
          q
            {width:.3f} 0 0 {height:.3f} {x:.3f} {y:.3f} cm
            {image.name} Do
          Q
        EMC
        """
        self.add_xobject(image)
        self.contents.append_stream(textwrap.dedent(instructions))

    @property
    def height(self):
        media_box = self.page_dict.content[PDFName("/MediaBox")]
        height = media_box[3]
        return height

    @property
    def width(self):
        media_box = self.page_dict.content[PDFName("/MediaBox")]
        width = media_box[2]
        return width

    def write_text(
        self, pos: tuple, font, size: float, text: str, artifact: bool = False
    ):
        tag_line = self._get_tag_line(artifact)
        font_name = self.ensure_font(font)
        x, y = map(_mm_to_dots, pos)
        y = self.height - y - size
        instructions = f"""
        {tag_line}
        q
        BT
        1 0 0 1 {x:.4f} {y:.4f} Tm
        {font_name} {size} Tf
          [({text})] TJ
        ET
        Q
        EMC
        """
        self.contents.append_stream(textwrap.dedent(instructions))


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

    @content.setter
    def content(self, content):
        return self.obj.set_content(content)

    def append_stream(self, text):
        new_data = text.encode("utf-8")
        if self.obj.stream is not None:
            prev_data = self.obj.stream.decode()
            new_data = prev_data + b"\n" + new_data
        self.obj.set_stream(EncodedObject.create(new_data))


class PDFFont(PDFObject):
    def __init__(self, obj, pdf, type, name):
        super().__init__(obj, pdf)
        if not type in ["Type1", "TrueType"]:
            raise ValueError(f"Invalid font type: {type}")
        self.obj.set_content(
            {
                PDFName("/Type"): PDFName("/Font"),
                PDFName("/Subtype"): PDFName(f"/{type}"),
                PDFName("/BaseFont"): PDFName(f"/{name}"),
            }
        )


class PDFBitmapObject(PDFObject):
    def __init__(self, obj, pdf, name, bitmap, dpi=300):
        super().__init__(obj, pdf)
        self._name = name
        self.dpi = dpi
        self.width, self.height = bitmap.size

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

    @property
    def size(self):
        width_mm = (self.width / self.dpi) * 25.4
        height_mm = (self.height / self.dpi) * 25.4
        return (width_mm, height_mm)

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
    def __init__(self, obj, pdf, tag, parent):
        super().__init__(obj, pdf)
        self.tag = tag
        self.parent = parent

    def __repr__(self):
        return f'PDFTagObject("{self.tag}", {self.parent!r})'

    def _pages(self, page_nos: [int]):
        if len(page_nos) == 0:
            return []
        elif len(page_nos) == 1:
            return [self.pdf.pages[page_nos[0]].xref]
        else:
            return [page.xref for page in itemgetter(*page_nos)(self.pdf.pages)]

    def create_child(self, tag: str):
        child_object = self.pdf.llpdf.new_object(
            content={
                PDFName("/Type"): PDFName("/StructElem"),
                PDFName("/S"): PDFName(f"/{tag}"),
                PDFName("/P"): self.xref,
                PDFName("/K"): [],
                PDFName("/Pg"): [],
            }
        )
        self.obj.content[PDFName("/K")].append(child_object.xref)

        return PDFTagObject(child_object, self.pdf, tag, self)
