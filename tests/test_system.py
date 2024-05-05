from pathlib import Path

from semdoc import document
from semdoc import analyzer
from semdoc.analyzer import opencv
from semdoc.analyzer import tesseract
from semdoc import output


def test_multi_object():
    src = Path("test.pdf")
    doc = document.load_document(src)

    pipeline = analyzer.Pipeline()
    segmentizer = opencv.Analyzer()
    pipeline.add(segmentizer)
    ocr = tesseract.Analyzer()
    pipeline.add(ocr)
    pipeline.run(doc)

    dest = "test.xml"
    xml_output = output.get_formatter("xml")(doc)
    xml_output.write_file(dest)
    print(xml_output.pretty())
