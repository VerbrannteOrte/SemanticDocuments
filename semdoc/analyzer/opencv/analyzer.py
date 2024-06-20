import cv2
import copy

from semdoc.structure import Region, is_page
from semdoc.structure.element import Element, ElementType


class Analyzer:
    def partition_region(self, region: Region) -> [Region]:
        partitions = []

        image = region.get_bitmap_numpy()

        print(f"image: {image.shape}")
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        print(f"gray {gray.shape}")

        # Apply adaptive thresholding to binarize the image
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )

        # Use morphology to enhance the blocks, e.g., dilate to make the contours of blocks connect
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 23))
        dilate = cv2.dilate(thresh, kernel, iterations=1)
        erode = cv2.erode(thresh, kernel, iterations=1)

        # Find contours
        contours, _ = cv2.findContours(
            dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Filter and draw bounding boxes around each block
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1:  # Min area threshold to filter insignificant blocks/noise
                x, y, w, h = cv2.boundingRect(contour)
                partition = region.create_partition(x, y, w, h)
                partitions.append(partition)
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)

        # cv2.imshow("Boxes", image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        return partitions

    def run(self, structure):
        out = copy.deepcopy(structure)
        for element in out.iter_children(filter=is_page):
            region = element.region()
            for partition in self.partition_region(region):
                e = Element(ElementType.Partition)
                e.set_property("region", partition, "opencv")
                element.add(e)
        return out
