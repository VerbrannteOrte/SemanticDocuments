import pytest

from semdoc.analyzer.opencv import Analyzer
from semdoc.structure import Region
import utils
from documents import simple_text


@pytest.fixture
def analyzer():
    return Analyzer()


def test_analyzer():
    doc = utils.loadpath("simple_text.png")
    analyzer = Analyzer()
    structure = analyzer.run(doc.physical_structure())
    dict = structure.to_dict()
    boxes = structure.children[0].children
    assert len(boxes) == 3


def test_boxes_simple_text(analyzer, simple_text):
    doc = simple_text["doc"]
    analyzed = analyzer.run(doc.physical_structure())
    partitions = analyzed.children[0].children
    regions = sorted(map(lambda p: p.region(), partitions), key=lambda r: r.y)
    box_doc = simple_text["boxes"][0].document
    assert box_doc == doc
    assert box_doc is doc
    for a, b in zip(regions, simple_text["boxes"]):
        assert a.document == b.document
        assert a.document is b.document
        assert a.approx(b)
