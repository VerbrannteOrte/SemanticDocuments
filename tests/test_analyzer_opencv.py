import pytest

from semdoc.analyzer.opencv import Analyzer
from semdoc.structure import Region
import utils
from documents import simple_text


@pytest.fixture
def analyzer():
    return Analyzer()


def test_boxes_simple_text(analyzer, simple_text):
    doc = simple_text["doc"]
    analyzed = analyzer.run(doc.physical_structure())
    partitions = analyzed.children[0].children
    regions = sorted(map(lambda p: p.region(), partitions), key=lambda r: r.y)
    for a, b in zip(regions, simple_text["boxes"]):
        assert a.approx(b)
