from documents import simple_text

from semdoc.output import get_formatter


def test_write_pages(simple_text):
    doc = simple_text["logical"]
    exporter = get_formatter("pdf")(doc)
    exporter.write_file("text.pdf")
    assert False
