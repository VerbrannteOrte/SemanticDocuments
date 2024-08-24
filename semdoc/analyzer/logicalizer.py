from copy import deepcopy
from semdoc.structure.element import geometric_sorter, is_logical
from semdoc import logging

logger = logging.getLogger("semdoc.analyzer.logicalizer")


class Logicalizer:
    def __init__(self):
        self.name = "logicalizer"

    def collect_text(self, elements):
        texts = []
        for element in elements:
            if element.category.is_block:
                continue
            texts.append(element.get_text())
            child_texts = self.collect_text(
                sorted(element.children, key=geometric_sorter)
            )
            texts.extend(child_texts)
        texts = [t for t in texts if t != ""]
        logger.debug("finished collecting texts: %s", texts)
        return " ".join(texts)

    def logicalize(self, element):
        if element.category.is_block:
            own_text = element.get_text()
            child_texts = self.collect_text(
                sorted(element.children, key=geometric_sorter)
            )
            text = " ".join((t for t in (own_text, child_texts) if t != ""))
            element.set_property("content_text", text, self.name, 1)
        future_children = []
        for child in sorted(element.children, key=geometric_sorter):
            element.remove(child)
            next_logical_children = self.logicalize(child)
            future_children.extend(next_logical_children)
        if is_logical(element):
            for c in future_children:
                element.add(c)
            return [element]
        return future_children

    def run(self, structure):
        out = deepcopy(structure)
        return self.logicalize(out)[0]
