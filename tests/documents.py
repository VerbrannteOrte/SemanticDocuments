import pytest

from semdoc.structure import Region

import utils


@pytest.fixture
def simple_text():
    doc = utils.loadpath("simple_text.png")
    boxes = [
        Region(doc, 0, 544, 508, 401, 76),
        Region(doc, 0, 544, 636, 1460, 260),
        Region(doc, 0, 544, 910, 1460, 551),
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
    return {
        "doc": doc,
        "boxes": boxes,
        "text_lines": text_lines,
    }
