import cv2
import copy


class Partitioning:
    def __init__(self):
        self.areas = []

    def add(self, partition):
        self.areas.append(partition)

    def base_regions(self):
        return iter(self.areas)

    def visualize(self, image):
        image = copy.copy(image)
        for rect in self.rects:
            x, y, w, h = rect
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)
        return image
