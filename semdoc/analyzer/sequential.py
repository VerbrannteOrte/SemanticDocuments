from semdoc.structure import Element


class Sequential:
    def __init__(self):
        self.analyzers = []

    def add(self, analyzer):
        self.analyzers.append(analyzer)

    def run(self, inp: Element) -> Element:
        structure = inp
        for analyzer in self.analyzers:
            structure = analyzer.run(structure)
        return structure
