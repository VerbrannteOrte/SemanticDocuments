from semdoc.reader import mupdf
import utils


def test_load_simple_text():
    path = utils.docpath("simple_text.pdf")
    doc = mupdf.MupdfDocument(path)
    pstruct = doc.physical_structure()
    assert len(pstruct.children) == 1
