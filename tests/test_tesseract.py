from semdoc.analyzer.tesseract import Analyzer

import utils


def test_string_recognition():
    doc = utils.loadpath("simple_text.png")
    tesseract = Analyzer()
    struct = doc.physical_structure()
    res = tesseract.run(struct)
    text = res.children[0].get_text()
    assert text.startswith("Hello, world!")
