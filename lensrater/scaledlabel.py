#!env python3

from PyQt5 import QtGui, QtCore, QtWidgets
# from PyQt5.QtGui import QIcon, QColor
# from PyQt5.QtCore import Qt
# from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QMainWindow, QDesktopWidget

class ScaledLabel(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        QtWidgets.QLabel.__init__(self)
        self._pixmap = QtGui.QPixmap(self.pixmap())

    # def resizeEvent(self, event):
        # self
        # self.setPixmap(self._pixmap.scaled(
            # self.width(), self.height(),
            # QtCore.Qt.KeepAspectRatio))
