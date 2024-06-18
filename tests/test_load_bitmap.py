from semdoc.reader import bitmap
import utils


def test_bitmap_document():
    path = utils.docpath("simple_text.png")
    doc = bitmap.BitmapDocument(path)
    pages = doc.physical_structure().children
    assert len(pages) == 1
    region = pages[0].region()
    assert region.is_simple()
    assert region.width == 2550
    assert region.height == 3300
