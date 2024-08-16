import subprocess
import xml.etree.ElementTree as ET
import subprocess
import pytest
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


def _rule_to_dict(rule):
    return {child.tag: _text_or_child_dict(child) for child in rule} | rule.attrib


def validate_verapdf(file: Path, flavour="ua2"):
    verapdf_proc = subprocess.run(
        ["verapdf", "--flavour", flavour, file], capture_output=True, text=True
    )
    if len(verapdf_proc.stderr) > 0:
        print(verapdf_proc.stderr)
        raise RuntimeError("verapdf produced output on stderr")
    result = ET.fromstring(verapdf_proc.stdout)
    failed_rules = result.findall("./jobs/job/validationReport/details/rule")
    return [_rule_to_dict(rule) for rule in failed_rules]
