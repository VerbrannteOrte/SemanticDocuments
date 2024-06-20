from surya.detection import batch_text_detection
from surya.model.detection.segformer import load_model, load_processor
from copy import deepcopy

from semdoc.cache import cache_for
from semdoc.structure import is_page, Element, ElementType as ET


class TextLines:
    def __init__(self):
        self.name = "surya_textlines"
        self.model = load_model()
        self.processor = load_processor()

    @cache_for("image", "model_config")
    def _run_model(self, image, model_config):
        print("running model")
        result = batch_text_detection([image], self.model, self.processor)[0]
        return result

    def run(self, structure):
        out = deepcopy(structure)
        for element in out.iter_children(filter=is_page):
            region = element.region()
            image = region.get_bitmap()
            predictions = self._run_model(image, self.model.generation_config)
            for box in predictions.bboxes:
                x1, y1, x2, y2 = box.bbox
                w, h = x2 - x1, y2 - y1
                line = Element(ET.TextLine)
                line_region = region.create_partition(x1, y1, w, h)
                line.set_property("region", line_region, self.name, box.confidence)
                element.add(line)
        return out
