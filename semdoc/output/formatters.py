class UniversalFormatter:
    def __init__(self, document):
        self.document = document

    def write_file(self, path):
        pass

    def tostring(self):
        pass

    def pretty(self):
        pass


def get_formatter(format):
    return UniversalFormatter
