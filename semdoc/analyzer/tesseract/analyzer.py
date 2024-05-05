class Analyzer:
    def __init__(self):
        pass

    def run(self, document):
        partitioning = document.get_partitioning()
        for region in partitioning.base_regions():
            bitmap = document.get_region_image(region)
            region.set_text("hello world")
