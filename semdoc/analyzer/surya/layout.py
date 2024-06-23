from copy import deepcopy

from semdoc.structure import Element, ElementType as ET

from . import inference


class Layout:
    def __init__(self):
        self.name = "surya_layout"

    def run(self, structure):
        out = deepcopy(structure)
        for element in out.iter_children(filter=lambda e: e.category == ET.Page):
            region = element.region()
            image = region.get_bitmap()
            predictions = inference.layout_detection(image)
            for box in predictions.bboxes:
                x1, y1, x2, y2 = box.bbox
                w, h = x2 - x1, y2 - y1
                category = {
                    "Text": ET.Paragraph,
                    "Section-header": ET.Heading1,
                }
                area = Element(category[box.label])
                area_region = region.create_partition(x1, y1, w, h)
                area.set_property("region", area_region, self.name, box.confidence)
                element.add(area)
        return out
