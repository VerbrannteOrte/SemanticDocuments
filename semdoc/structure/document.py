from . import containers


class Document(containers.Sequence):
    def __init__(self):
        super().__init__()

    def __repr__(self):
        return "Document()"

    def __str__(self):
        return "Document()"

    def get_pages(self):
        pass

    def get_region_image(self, region):
        raise NotImplementedError()


class Page:
    def __init__(self, image):
        self.image = image

    def as_bitmap(self):
        return self.image
