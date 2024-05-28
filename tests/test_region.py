import utils


def test_get_bitmap_numpy():
    page = utils.loadpath("simple_text.png").get_pages()[0]
    image = page.get_bitmap()
    image_np = page.get_bitmap_numpy()
    height, width, channels = image_np.shape
    assert height == image.height
    assert width == image.width
    assert channels == 3
