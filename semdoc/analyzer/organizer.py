from copy import copy, deepcopy
from semdoc.structure import ElementType as ET, is_page
from semdoc import logging

from rich import pretty

logger = logging.getLogger("semdoc.structure.organizer")


def _element_area(element):
    region = element.region()
    return region.width * region.height


class TreeOrganizer:
    def __init__(self):
        pass

    def organize(self, structure):
        logger.debug(
            "organizing structure of category '%s' with %d children",
            structure.category,
            len(structure.children),
        )
        regional_elements = []
        for element in structure.iter_children():
            if not element.region():
                continue
            element.parent.remove(element)
            regional_elements.append(element)
        regional_elements.sort(key=_element_area, reverse=True)
        logger.debug(
            "collected %d children with region and ignored %d without",
            len(regional_elements),
            len(structure.children),
        )
        while len(regional_elements) > 0:
            largest = regional_elements.pop(0)
            structure.add(largest)
            region = largest.region()
            children = [e for e in regional_elements if region.encompasses(e.region())]
            for e in children:
                largest.add(e)
                regional_elements.remove(e)
            logger.debug(
                "the largest element encompasses %d elements, %d remaining",
                len(children),
                len(regional_elements),
            )
            self.organize(largest)

    def run(self, structure):
        out = deepcopy(structure)
        for page in out.iter_children(filter=is_page):
            self.organize(page)
        return out
