from copy import copy, deepcopy
from semdoc.structure import ElementType as ET, is_page
from semdoc import logging

from rich import pretty

logger = logging.getLogger("semdoc.structure.organizer")


def _element_area(element):
    region = element.region()
    if not region:
        return 0
    area = region.area
    if element.category.is_block:
        area *= 1.05
    return area


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
            children = [
                e for e in regional_elements if region.coverage(e.region()) > 0.95
            ]
            for e in children:
                # make sure that the parent region encompasses the child region
                child_region = e.region()
                x2 = region.x2
                y2 = region.y2
                if child_region.x < region.x:
                    region.x = child_region.x
                    region.width = x2 - region.x
                if child_region.y < region.y:
                    region.y = child_region.y
                    region.height = y2 - region.y
                if child_region.x2 > region.x2:
                    region.width = child_region.x2 - region.x
                if child_region.y2 > region.y2:
                    region.height = child_region.y2 - region.y
                # the child is taken care of, add it to the new parent
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
