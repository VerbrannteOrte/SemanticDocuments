from semdoc.structure import Region

import utils


def test_get_bitmap_numpy():
    page = utils.loadpath("simple_text.png").physical_structure().children[0]
    image = page.region().get_bitmap()
    image_np = page.region().get_bitmap_numpy()
    height, width, channels = image_np.shape
    assert height == image.height
    assert width == image.width
    assert channels == 3


class MyDocument:
    def get_geometry(self, page_no):
        return {
            "width": 2550,
            "height": 3300,
        }


def test_approx():
    doc = MyDocument()
    a = Region(doc, 0, 100, 100, 200, 200)
    b = Region(doc, 0, 100, 100, 200, 200)
    assert a.approx(b)
    assert b.approx(a)
    a = Region(doc, 0, 545, 508, 401, 76)
    b = Region(doc, 0, 544, 508, 401, 76)
    assert a.approx(b)
    assert b.approx(a)
