import cv2

from . import Partitioning

class OpenCVPartitioner():
    def __init__(self):
        pass

    def __call__(self, page):
        self.partition(page)

    def partition(self, page):
        rects = []

        image = page.as_bitmap()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply adaptive thresholding to binarize the image
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

        # Use morphology to enhance the blocks, e.g., dilate to make the contours of blocks connect
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
        dilate = cv2.dilate(thresh, kernel, iterations=1)
        #erode = cv2.erode(thresh, kernel, iterations=1)

        # Find contours
        contours, _ = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter and draw bounding boxes around each block
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1:  # Min area threshold to filter insignificant blocks/noise
                x, y, w, h = cv2.boundingRect(contour)
                rects.append((x, y, w, h))
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 1)

        return Partitioning(rects)
