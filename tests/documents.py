import pytest
from copy import copy

from semdoc.structure import Region, Element, ElementType as ET

import utils


@pytest.fixture
def simple_text():
    path_png = utils.docpath("simple_text.png")
    path_pdf = utils.docpath("simple_text.pdf")
    doc = utils.loadpath("simple_text.png")
    boxes = [
        Region(doc, 0, 506, 519, 404, 76),
        Region(doc, 0, 508, 641, 1456, 260, primary=False),
        Region(doc, 0, 508, 921, 1456, 540, primary=False),
    ]
    text_lines = [
        "Hello, world!",
        "Auch gibt es niemanden, der den Schmerz an sich liebt, sucht oder wünscht,",
        "nur, weil er Schmerz ist, es sei denn, es kommt zu zufälligen Umständen, in",
        "denen Mühen und Schmerz ihm große Freude bereiten können. Um ein triviales",
        "Beispiel zu nehmen, wer von uns unterzieht sich je anstrengender körperlicher",
        "Betätigung, außer um Vorteile daraus zu ziehen?",
        "Aber wer hat irgend ein Recht, einen Menschen zu tadeln, der die Entscheidung",
        "trifft, eine Freude zu genießen, die keine unangenehmen Folgen hat, oder einen,",
        "der Schmerz vermeidet, welcher keine daraus resultierende Freude nach sich",
        "zieht? Auch gibt es niemanden, der den Schmerz an sich liebt, sucht oder wün-",
        "scht, nur, weil er Schmerz ist, es sei denn, es kommt zu zufälligen Umständen, in",
        "denen Mühen und Schmerz ihm große Freude bereiten können. Um ein triviales",
        "Beispiel zu nehmen, wer von uns unterzieht sich je anstrengender körperlicher",
        "Betätigung, außer um Vorteile daraus zu ziehen?  Aber wer hat irgend ein Recht,",
        "einen Menschen zu tadeln, der die Entscheidung trifft, eine Freude zu genießen,",
        "die keine unangenehmen Folgen hat, oder einen, der Schmerz vermeidet, welcher",
        "keine daraus resultierende Freude nach sich zieht?",
    ]

    logical = Element(ET.Document)
    logical.set_property("page_count", 1, "manual")
    logical.set_property("file_name", "simple_text.png", "manual")
    heading = Element(ET.Heading1)
    heading.set_property("region", boxes[0], "manual")
    heading.set_text("Hello, world!", source="manual")
    logical.add(heading)
    par1 = Element(ET.Paragraph)
    par1.set_property("region", boxes[1], "manual")
    region = copy(boxes[1])
    region.height = region.height / 5
    region.primary = True
    for text_line in text_lines[1:6]:
        line = Element(ET.TextLine)
        line.set_text(text_line, "manual")
        line.set_property("region", region, "manual")
        par1.add(line)
        region = copy(region)
        region.y += region.height
    logical.add(par1)
    par2 = Element(ET.Paragraph)
    par2.set_property("region", boxes[2], "manual")
    region = copy(boxes[2])
    region.height = region.height / 11
    region.primary = True
    for text_line in text_lines[6:17]:
        line = Element(ET.TextLine)
        line.set_text(text_line, "manual")
        line.set_property("region", region, "manual")
        par2.add(line)
        region = copy(region)
        region.y += region.height
    logical.add(par2)

    return {
        "path_png": path_png,
        "path_pdf": path_pdf,
        "doc": doc,
        "boxes": boxes,
        "text_lines": text_lines,
        "logical": logical,
    }
