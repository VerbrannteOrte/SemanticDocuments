from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QApplication, QLabel
from PIL.ImageQt import ImageQt
from rich import pretty
import sys
import io


class ImageWidget(QtWidgets.QWidget):
    def __init__(self, image, structure, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
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
        pen = QtGui.QPen()
        pen.setColor(QtGui.QColor(255, 0, 0))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
        x_offset, y_offset = x, y
        for element in self.structure.children[0].iter_children():
            region = element.region()
            if region:
                x = x_offset + region.x * scaling
                y = y_offset + region.y * scaling
                w = region.width * scaling
                h = region.height * scaling
                painter.drawRect(x, y, w, h)


def show_boxes(doc, structure):
    first_page = structure.children[0]
    image = first_page.region().get_bitmap()
    app = QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    widget = ImageWidget(image, structure)
    window.setCentralWidget(widget)
    window.show()
    app.exec()
