from copy import deepcopy

import pytesseract


class Analyzer:
    def __init__(self):
        pass

    def get_text(self, bitmap):
        lang = "deu"
        config = "--psm 3"
        data = pytesseract.image_to_string(bitmap, lang, config)
        return data

    def analyze_regions(self, element):
        texts = []
        regions = list(element.iter_regions())
        print(f"regions: {regions}")
        for region in element.iter_regions():
            bitmap = region.get_bitmap_numpy()
            text = self.get_text(bitmap).strip()
            texts.append(text)
        text = "\n".join(texts)
        element.set_text(text, "tesseract")

    def analyze_children(self, element):
        print(f"element: {element}")
        self.analyze_regions(element)
        for child in element.children:
            print(f"child: {child}")
            self.analyze_children(child)

    def run(self, structure):
        structure = deepcopy(structure)
        self.analyze_children(structure)
        return structure
