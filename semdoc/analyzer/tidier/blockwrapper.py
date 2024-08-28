from copy import deepcopy

from semdoc.structure import Element, ElementType as ET
from semdoc import logging

logger = logging.getLogger("semdoc.tidier.nonblock")


class NonBlockWrapper:
    def __init__(self, wrap_category=ET.Paragraph):
        self.name = "textline-tidier"
        self.wrap_category = wrap_category

    def run(self, structure):
        out = deepcopy(structure)
        for child in out.children.copy():
            if not child.category.is_block:
                logger.warning(f"Found top level non-block element {child}")
                wrap = Element(self.wrap_category)
                region = child.region()
                if region:
                    wrap.set_property("region", deepcopy(region), self.name)
                wrap.add(child)
                out.add(wrap)
                out.children.remove(child)
        return out
