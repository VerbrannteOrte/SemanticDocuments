from semdoc.document import region


class Analyzer:
    def run(self, document):
        partitioning = document.get_partitioning()
        region1 = region.Region(
            x=100,
            y=100,
            w=200,
            h=400,
        )
        partitioning.add(region1)
        region2 = region.Region(
            x=650,
            y=100,
            w=200,
            h=500,
        )
        partitioning.add(region2)
