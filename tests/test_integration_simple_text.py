from rich.pretty import pprint
from pathlib import Path
import xml.etree.ElementTree as ET

from semdoc import reader
from semdoc import analyzer
from semdoc.analyzer import opencv
from semdoc.analyzer import tesseract
from semdoc.writer import get_writer

import utils


def test_bitmap_xml(tmp_path):
    src = utils.docpath("simple_text.png")
    doc = reader.load_path(src)
    physical = doc.physical_structure()

    pipeline = analyzer.Sequential()
    segmentizer = opencv.Analyzer()
    pipeline.add(segmentizer)
    ocr = tesseract.Analyzer()
    pipeline.add(ocr)
    result = pipeline.run(physical)

    dest = tmp_path / Path("simple_text.xml")
    xml_output = get_writer("xml")(result)
    string = xml_output.tostring()
    xml_output.write_file(dest)

    result = ET.fromstring(dest.read_text())
    heading = result.findtext("./Page/Region[1]")
    assert heading == "Hello, world!"
