from semdoc.reader import bitmap
import utils


def test_bitmap_document():
    path = utils.docpath("simple_text.png")
    doc = bitmap.BitmapDocument(path)
    pages = doc.get_pages()
    assert len(pages) == 1
    page = pages[0]
    assert page.width == 2550
    assert page.height == 3300
