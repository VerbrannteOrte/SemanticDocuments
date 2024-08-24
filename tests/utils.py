import pymupdf
import subprocess
import xml.etree.ElementTree as ET
import subprocess
import pytest
import Levenshtein
from collections.abc import Sequence
from copy import copy
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from semdoc.reader.bitmap import BitmapDocument
from semdoc.structure import Document


def docpath(path: str) -> Path:
    base = Path("tests/documents")
    file = Path(path)
    return base / file


def loadpath(filename: str) -> Document:
    path = docpath(filename)
    doc = BitmapDocument(path)
    return doc


@pytest.fixture
def dummy_image() -> Image:
    fc_list = subprocess.run(
        ["fc-list", ':family="Liberation Sans":style=Regular file'],
        capture_output=True,
        text=True,
    )
    if fc_list.stdout:
        libsans_path = fc_list.stdout.split(":")[0]
        libsans = ImageFont.truetype(libsans_path)
    else:
        libsans = None

    image_with_background = Image.new("RGB", (400, 300), "blue")

    draw = ImageDraw.Draw(image_with_background)

    draw.rectangle([(50, 50), (100, 100)], fill="yellow", outline="black")

    draw.text((50, 125), "Hello World!", fill="white", font=libsans, font_size=48)

    return image_with_background


def _text_or_child_dict(element):
    if len(element) > 0:
        return {child.tag: _text_or_child_dict(child) for child in element}
    else:
        return element.text


def subprocess_get_xml(executable: str, file: Path, additional_params=None):
    cmd = [executable]
    if additional_params:
        cmd.extend(additional_params)
    cmd.append(file)
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )
    if len(proc.stderr) > 0:
        print(proc.stderr)
        raise RuntimeError(f"{executable} produced output on stderr")
    result = ET.fromstring(proc.stdout)
    return result


def _rule_to_dict(rule):
    return {child.tag: _text_or_child_dict(child) for child in rule} | rule.attrib


def validate_verapdf(file: Path, flavour="ua2"):
    output = subprocess_get_xml("verapdf", file, ["--flavour", flavour])
    failed_rules = output.findall("./jobs/job/validationReport/details/rule")
    return [_rule_to_dict(rule) for rule in failed_rules]


def get_tag_structure(file: Path):
    output = subprocess_get_xml("pdfstruct", file, ["--format", "xml"])
    return output


def mupdf_open(path: Path) -> pymupdf.Document:
    """Load the file and return a mupdf document. Assert that no warings are
    emmited by mupdf. This is a indication whether the document is well formed."""
    pymupdf.TOOLS.mupdf_warnings(reset=True)
    document = pymupdf.open(path)
    warnings = pymupdf.TOOLS.mupdf_warnings()
    assert warnings == ""
    return document


def assert_similar(left, right, avg_distance=0.5):
    """Assert that the Levenshtein distance between left and right is less than
    avg_distance * len(left). Accepts either two strings or two sequences of
    strings."""
    if isinstance(left, str):
        left = [left]
    else:
        left = list(left)
    if isinstance(right, str):
        right = [right]
    else:
        right = list(right)
    assert len(left) == len(right)
    max_distance = max(1, avg_distance * len(left))
    distances = [
        Levenshtein.distance(l, r, score_cutoff=max_distance)
        for (l, r) in zip(left, right, strict=True)
    ]
    assert sum(distances) <= max_distance
