import cv2
import copy

class Partitioning():
    def __init__(self, rects):
        self.rects = rects

    def visualize(self, image):
        image = copy.copy(image)
        for rect in self.rects:
            x, y, w, h = rect
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 1)
        return image
