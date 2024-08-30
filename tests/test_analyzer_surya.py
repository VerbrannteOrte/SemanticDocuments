from semdoc.analyzer.surya import TextLines, OCR, Layout
from semdoc import analyzer
from semdoc.structure import ElementType as ET

from utils import assert_similar
from documents import simple_text


def test_textlines_simple(simple_text):
    doc = simple_text["doc"]
    analyzer = TextLines()
    output = analyzer.run(doc.physical_structure())
    lines = output.children[0].children
    assert len(lines) == len(simple_text["text_lines"])


def test_ocr_simple(simple_text):
    doc = simple_text["doc"]
    pipeline = analyzer.Sequential()
    find_lines = TextLines()
    pipeline.add(find_lines)
    ocr = OCR()
    pipeline.add(ocr)

    output = pipeline.run(doc.physical_structure())
    lines = output.children[0].children
    texts = [line.get_text() for line in lines]
    assert_similar(texts, simple_text["text_lines"])


def test_layout_simple(simple_text):
    doc = simple_text["doc"]
    analyzer = Layout()

    output = analyzer.run(doc.physical_structure())
    paragraphs = [p for p in output.children[0].children if p.category == ET.Paragraph]
    headings = [h for h in output.children[0].children if h.category.is_heading]
    assert len(paragraphs) == 2
    assert len(headings) == 1
