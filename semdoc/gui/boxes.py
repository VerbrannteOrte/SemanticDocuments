from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QApplication, QLabel
from PIL.ImageQt import ImageQt
from rich import pretty
import sys
import seaborn
import io


class ImageWidget(QtWidgets.QWidget):
    def __init__(self, image, structure, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self.colormap = seaborn.color_palette()
        self.image = image
        self.qtimage = QtGui.QPixmap.fromImage(ImageQt(image))
        self.structure = structure

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        painter.setBrush(QtGui.QBrush(QtCore.Qt.black, QtCore.Qt.SolidPattern))
        painter.drawRect(self.rect())
        x, y, w, h = self.rect().getRect()
        ratio = w / h
        image_ratio = self.image.size[0] / self.image.size[1]
        if ratio > image_ratio:
            x = x + (w - image_ratio * h) / 2
            w = image_ratio * h
            scaling = w / self.image.size[0]
        else:
            y = y + (h - w / image_ratio) / 2
            h = w / image_ratio
            scaling = h / self.image.size[1]
        painter.drawPixmap(x, y, w, h, self.qtimage)
        painter.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
        x_offset, y_offset = x, y
        self.draw_boxes(painter, self.structure, 0, x_offset, y_offset, scaling)

    def draw_boxes(self, painter, structure, level, x_offset, y_offset, scaling):
        for element in structure.children:
            self.draw_boxes(painter, element, level + 1, x_offset, y_offset, scaling)
        region = structure.region()
        if region:
            pen = QtGui.QPen()
            color = [round(c * 255) for c in self.colormap[level]]
            pen.setColor(QtGui.QColor(*color))
            pen.setWidth(1)
            painter.setPen(pen)
            x = x_offset + region.x * scaling
            y = y_offset + region.y * scaling
            w = region.width * scaling
            h = region.height * scaling
            painter.drawRect(x, y, w, h)


def show_boxes(doc, structure):
    first_page = doc.physical_structure().children[0]
    image = first_page.region().get_bitmap()
    app = QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    widget = ImageWidget(image, structure)
    window.setCentralWidget(widget)
    window.show()
    app.exec()
