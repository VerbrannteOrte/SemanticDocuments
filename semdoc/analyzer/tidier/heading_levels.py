from copy import deepcopy
from semdoc.structure import ElementType as ET
from semdoc import logging

logger = logging.getLogger("semdoc.analyzer.tidier.heading-level")


class HeadingLevelTidier:
    def __init__(self):
        self.name = "heading-level-tidier"

    def run(self, structure):
        out = deepcopy(structure)
        levels = [
            ET.Heading6,
            ET.Heading5,
            ET.Heading4,
            ET.Heading3,
            ET.Heading2,
            ET.Heading1,
        ]
        headings = list(out.iter_children(filter=lambda e: e.category.is_heading))
        logger.debug(f"found {len(headings)} headings")
        categories = {heading.category for heading in headings}
        logger.debug(f"with {len(categories)} categories: {categories}")
        catmap = {}
        for category in sorted(categories, key=lambda c: str(c)):
            new_level = levels.pop()
            logger.debug(f"creating mapping for {category}: {new_level}")
            catmap[category] = new_level
        logger.debug(f"rearranging them like this: {catmap}")
        for heading in headings:
            heading.category = catmap[heading.category]
        return out
