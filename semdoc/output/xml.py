from pathlib import Path
import xml.etree.ElementTree as ET
from semdoc.structure import Document, Region, Page


class XMLFormatter:
    def __init__(self, document):
        self.document = document
        root = self.encode_element(document)
        self.tree = ET.ElementTree(root)

    def encode_element(self, element, parent=None):
        attrib = {}
        tag = "Element"
        if type(element) is Document:
            tag = "Document"
        elif type(element) is Page:
            tag = "Page"
            attrib["page_no"] = str(element.page_no)
        elif type(element) is Region:
            tag = "Region"
            attrib["x"] = str(element.x)
            attrib["y"] = str(element.y)
            attrib["width"] = str(element.width)
            attrib["height"] = str(element.height)
        if parent is None:
            node = ET.Element(tag, attrib)
        else:
            node = ET.SubElement(parent, tag, attrib)
        node.text = element.get_text()
        for child in element.children_ordered():
            self.encode_element(child, node)
        return node

    def write_file(self, path: Path):
        self.tree.write(path)

    def tostring(self):
        return ET.tostring(self.tree.getroot())
