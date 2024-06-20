from semdoc.analyzer.surya import TextLines
from documents import simple_text


def test_textlines_simple(simple_text):
    doc = simple_text["doc"]
    analyzer = TextLines()
    output = analyzer.run(doc.physical_structure())
    lines = output.children[0].children
    assert len(lines) == simple_text["num_lines"]
