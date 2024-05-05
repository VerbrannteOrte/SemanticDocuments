class Pipeline:
    def __init__(self):
        self.analyzers = []

    def add(self, analyzer):
        self.analyzers.append(analyzer)

    def run(self, document):
        for analyzer in self.analyzers:
            analyzer.run(document)
