import pytest

from semdoc.structure import Region

import utils


@pytest.fixture
def simple_text():
    doc = utils.loadpath("simple_text.png")
    boxes = (
        [
            Region(doc, 0, 544, 508, 401, 76),
            Region(doc, 0, 544, 636, 1460, 260),
            Region(doc, 0, 544, 910, 1460, 551),
        ],
    )
    return {
        "doc": doc,
        "boxes": boxes,
        "num_lines": 17,
    }
