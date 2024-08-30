from pathlib import Path
import xml.etree.ElementTree as ET
from semdoc.structure import Document, Region, ElementType as EType
from semdoc.structure.element import geometric_sorter


class XMLFormatter:
    def __init__(self, document):
        self.document = document
        root = self.encode_element(document)
        self.tree = ET.ElementTree(root)

    def encode_element(self, element, parent=None):
        attrib = {}
        tag = str(element.category)
        match element.category:
            case EType.Document:
                tag = "Document"
            case EType.Partition:
                tag = "Region"
            case EType.Page:
                tag = "Page"
                page_no = element.get("page_no")
                if page_no:
                    attrib["page_no"] = str(page_no)
            case EType.Heading1:
                tag = "H1"
            case EType.Heading2:
                tag = "H2"
            case EType.Heading3:
                tag = "H3"
            case EType.Heading4:
                tag = "H4"
            case EType.Paragraph:
                tag = "Paragraph"
            case EType.Table:
                tag = "Table"
            case EType.TableRow:
                tag = "TableRow"
            case EType.TableCell:
                tag = "TableCell"
        region = element.region()
        if region:
            attrib["x"] = str(region.x)
            attrib["y"] = str(region.y)
            attrib["width"] = str(region.width)
            attrib["height"] = str(region.height)
        if parent is None:
            node = ET.Element(tag, attrib)
        else:
            node = ET.SubElement(parent, tag, attrib)
        node.text = element.get_text()
        for child in sorted(element.children, key=geometric_sorter):
            self.encode_element(child, node)
        return node

    def write_file(self, path: Path):
        self.tree.write(path)

    def tostring(self):
        return ET.tostring(self.tree.getroot())
