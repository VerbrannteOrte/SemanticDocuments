import pytest

from semdoc.analyzer.opencv import Analyzer
from semdoc.structure import Region
import utils


@pytest.fixture
def analyzer():
    return Analyzer()


@pytest.fixture
def simple_text():
    doc = utils.loadpath("simple_text.png")
    boxes = [
        Region(doc, 1, 544, 508, 401, 76),
        Region(doc, 1, 544, 636, 1460, 260),
        Region(doc, 1, 544, 910, 1460, 551),
    ]
    return {
        "doc": doc,
        "boxes": boxes,
    }


def test_analyzer():
    doc = utils.loadpath("simple_text.png")
    analyzer = Analyzer()
    structure = analyzer.run(doc)
    dict = structure.to_dict()
    boxes = structure.children[0].children
    assert len(boxes) == 3


def test_boxes_simple_text(analyzer, simple_text):
    doc = simple_text["doc"]
    page = doc.children[0]
    analyzed = analyzer.run(doc)
    boxes = sorted(list(analyzed.children[0].children), key=lambda r: r.y)
    for a, b in zip(boxes, simple_text["boxes"]):
        assert a.approx(b)
