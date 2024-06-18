from typing import Iterable, Optional
import utils
from pathlib import Path
from semdoc import output
import xml.etree.ElementTree as ET
from semdoc.structure import Element, ElementType, Document


class Processor:
    def process_element(element: Element):
        pass

    def __call__(self, inputs: Iterable[Element]):
        return Element(ElementType.Document)


def recognition_pipeline():
    return Processor()


def logicalization_pipeline():
    return Processor()


def test_system(tmp_path):
    doc = utils.loadpath("simple_text.png")
    pages = doc.physical_structure()

    recognizer = recognition_pipeline()
    logicalizer = logicalization_pipeline()

    physical_structure = recognizer(pages)
    logical_structure = logicalizer(physical_structure)

    dest = tmp_path / Path("simple_text.xml")
    xml_output = output.get_formatter("xml")(logical_structure)
    xml_output.write_file(dest)
    xml_string = xml_output.tostring()

    result = ET.fromstring(dest.read_text())
    heading = result.findtext("./Page/Region[1]")
    # assert heading == "Hello, world!"
