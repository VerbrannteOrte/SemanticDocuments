import pytesseract


class Analyzer:
    def __init__(self):
        pass

    def get_text(self, bitmap):
        lang = "deu"
        config = "--psm 3"
        data = pytesseract.image_to_string(bitmap, lang, config)
        return data

    def analyze_children(self, element):
        for region in element.iter_regions():
            bitmap = region.get_bitmap_numpy()
            text = self.get_text(bitmap).strip()
            region.set_text(text, "tesseract")
            self.analyze_children(region)

    def run(self, structure):
        self.analyze_children(structure)
        return structure
