from copy import deepcopy

from semdoc.structure import is_page, Element, ElementType as ET

from . import inference


class TextLines:
    def __init__(self):
        self.name = "surya_textlines"

    def run(self, structure):
        out = deepcopy(structure)
        for element in out.iter_children(filter=is_page):
            region = element.region()
            image = region.get_bitmap()
            predictions = inference.text_detection(image)
            for box in predictions.bboxes:
                x1, y1, x2, y2 = box.bbox
                w, h = x2 - x1, y2 - y1
                line = Element(ET.TextLine)
                line_region = region.create_partition(x1, y1, w, h)
                line.set_property("region", line_region, self.name, box.confidence)
                element.add(line)
        return out
