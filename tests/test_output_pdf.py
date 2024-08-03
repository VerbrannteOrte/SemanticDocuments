from pathlib import Path
import pymupdf
import llpdf
import io
import tempfile
from rich import pretty

from semdoc.output import get_formatter
from semdoc.output.pdf import PDFDocument

from documents import simple_text
from utils import dummy_image, validate_verapdf


def _mupdf_open(path: Path) -> pymupdf.Document:
    pymupdf.TOOLS.mupdf_warnings(reset=True)
    document = pymupdf.open(path)
    warnings = pymupdf.TOOLS.mupdf_warnings()
    assert warnings == ""
    return document


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
    _ = _mupdf_open(outfile)


def test_document_empty(tmp_path):
    pdf = PDFDocument(title="Empty world")
    _ = pdf.new_page()
    file = tmp_path / "out.pdf"
    pdf.write_file(file)
    mupdf = _mupdf_open(file)
    assert mupdf.page_count == 1

    validation_results = validate_verapdf(file, flavour="ua1")
    pretty.pprint(validation_results)
    print(file)
    assert len(validation_results) == 0


def test_document_bitmap(dummy_image, tmp_path):
    pdf = PDFDocument()
    page = pdf.new_page()
    img_obj = pdf.add_bitmap(dummy_image)
    img_obj.draw(page, 100, 100, 400, 300, None, 1)
    file = tmp_path / "out.pdf"
    pdf.write_file(file)

    mupdf = _mupdf_open(file)
    assert mupdf.page_count == 1
    mupdf_page = mupdf[0]
    images = mupdf_page.get_images()
    rects = 0
    for image in images:
        rects += len(mupdf_page.get_image_rects(image))
    assert rects == 1


def test_simple_text(simple_text):
    doc = simple_text["logical"]
    exporter = get_formatter("pdf")(doc)
    exporter.write_file("text.pdf")
