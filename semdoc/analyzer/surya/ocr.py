from copy import deepcopy
import math

from semdoc.structure import ElementType as ET

from . import inference


class OCR:
    def __init__(self):
        self.name = "surya_ocr"

    def run(self, structure):
        out = deepcopy(structure)
        for element in out.iter_children(filter=lambda e: e.category == ET.TextLine):
            region = element.region()
            image = region.get_bitmap()
            text, confidence = inference.text_recognition(image, ["de"])
            if math.isnan(confidence):
                confidence = 0
            element.set_text(text, self.name, confidence)
        return out
