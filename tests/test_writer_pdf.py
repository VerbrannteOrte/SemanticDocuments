import llpdf
import tempfile
from rich import pretty
from pytest import approx

from semdoc.writer import get_writer
from semdoc.writer.pdf import PDFDocument

from documents import simple_text
from utils import dummy_image, validate_verapdf, get_tag_structure, mupdf_open


def test_llpdf(dummy_image, tmp_path):
    pdf = llpdf.PDFDocument()
    hlpdf = llpdf.HighlevelPDFFunctions(pdf)

    hlpdf.initialize_pages(
        author="Johannes Bauer", title="This is the title (with special chars äöü)"
    )

    with tempfile.NamedTemporaryFile(delete_on_close=False) as tmp:
        dummy_image.save(tmp, format="jpeg", dpi=(300, 300))
        tmp.close()
        img = llpdf.PDFExtImage.from_file(tmp.name)

    page = llpdf.HighlevelPDFImageFunctions(hlpdf.new_page())
    page.put_image(img)

    outfile = tmp_path / "out.pdf"
    llpdf.PDFWriter(pretty=True, use_object_streams=False, use_xref_stream=False).write(
        pdf, outfile
    )

    # this checks for valid structure:
    _ = mupdf_open(outfile)


def test_document_empty(tmp_path):
    pdf = PDFDocument(title="Empty world")
    _ = pdf.new_page()
    file = tmp_path / "out.pdf"
    pdf.write_file(file)
    mupdf = mupdf_open(file)
    assert mupdf.page_count == 1

    validation_results = validate_verapdf(file, flavour="ua1")
    pretty.pprint(validation_results)
    assert len(validation_results) == 0


def test_document_text(tmp_path):
    pdf = PDFDocument(title="Hello world")
    page = pdf.new_page()
    font = pdf.create_font(name="Helvetica", type="Type1")
    pos = (40, 10)
    size = 24
    pdf.start_tag("H1")
    page.write_text(pos, font, size, "Hello, world")
    pdf.end_tag()
    pdf.start_tag("P")
    size = 14.0
    pos = (10, 50)
    page.write_text(pos, font, size, "How are you doing.")
    pos = (10, 55)
    page.write_text(
        pos, font, size, "Just checking in with some unicode characters äöüß"
    )
    page.write_text((180, 270), font, 12, "Page 1", artifact=True)
    pdf.end_tag()

    file = tmp_path / "out.pdf"
    pdf.write_file(file)
    mupdf = mupdf_open(file)
    assert mupdf.page_count == 1

    validation_results = validate_verapdf(file, flavour="ua1")
    pretty.pprint(validation_results)
    assert len(validation_results) == 1
    failed_rule = validation_results[0]
    assert failed_rule["specification"] == "ISO 14289-1:2014"
    assert failed_rule["clause"] == "7.21.4.1"


def test_document_bitmap(dummy_image, tmp_path):
    pdf = PDFDocument()
    page = pdf.new_page()
    img_obj = pdf.add_bitmap(dummy_image)
    page.draw_image((0, 0), img_obj, artifact=True)
    half_x = 210 / 2
    half_y = 297 / 2
    page.draw_image((half_x, half_y), img_obj, artifact=True)
    file = tmp_path / "out.pdf"
    pdf.write_file(file)

    mupdf = mupdf_open(file)
    assert mupdf.page_count == 1
    mupdf_page = mupdf[0]
    images = mupdf_page.get_images()
    rects = []
    for image in images:
        rects.extend(mupdf_page.get_image_rects(image))
    assert len(rects) == 2
    dummy_width_units = dummy_image.width / 300 * 72
    dummy_height_units = dummy_image.height / 300 * 72
    assert rects[0].width == dummy_width_units
    assert rects[0].height == dummy_height_units
    assert rects[0].x0 == approx(0)
    assert rects[0].y0 == approx(0)
    assert rects[1].x0 == approx(half_x / 25.4 * 72)
    assert rects[1].y0 == approx(half_y / 25.4 * 72)


def test_simple_text(simple_text, tmp_path):
    doc = simple_text["logical"]
    exporter = get_writer("pdf")(doc)
    outfile = tmp_path / "out.pdf"
    exporter.write_file(outfile)

    validation_results = validate_verapdf(outfile, flavour="ua1")
    pretty.pprint(validation_results)
    assert len(validation_results) == 0

    structure = get_tag_structure(outfile)
    headings = structure.findall("./Document/H1/MCID")
    assert len(headings) == 1
    assert headings[0].text == "Hello, world!"
    paragraphs = structure.findall("./Document/P")
    assert len(paragraphs) == 2
    mcids = structure.findall(".//MCID")
    text_lines = list(map(lambda elem: elem.text, mcids))
    assert text_lines == simple_text["text_lines"]
