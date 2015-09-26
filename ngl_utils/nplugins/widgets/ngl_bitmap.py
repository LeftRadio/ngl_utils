#!/usr/bin/env python

from ngl_utils.nplugins.widgets import NGL_Base

from PyQt5.QtCore import pyqtProperty, QRect, QSize, Qt
from PyQt5.QtGui import QPainter, QIcon


class NGL_Bitmap(NGL_Base):
    """NGL_Bitmap(QWidget)
    Provides a embedded NGL library rect widget.
    """

    def __init__(self, parent=None):
        """ Constructor for ngl widget """
        super(NGL_Bitmap, self).__init__(parent)

        self._ico = QIcon()
        self.setGeometry(100, 100, 100, 100)
        self.update()

    def paintEvent(self, event):
        """ Paint ngl widget event """

        painter = QPainter()
        painter.begin(self)

        # get rect and flags for paint
        rect = QRect(0, 0, self.size().width(), self.size().height())
        flags = Qt.AlignJustify #Qt.AlignHCenter | Qt.AlignVCenter

        # paint ico image
        self._ico.paint(painter, rect, flags)

        painter.end()

    def sizeHint(self):
        """ Return Qt sizeHint """
        return self.size()


    # Provide getter and setter methods for the property.
    @pyqtProperty(QIcon)
    def icon(self):
        return self._ico

    @icon.setter
    def icon(self, ico):
        self._ico = ico
        actualsize = self._ico.actualSize(QSize(16**2,16**2))
        self.setMaximumSize(actualsize)
        self.setMinimumSize(actualsize)
        self.update()


    def doNGLCode(self, **kwargs):
        template = ''
        return template


# if run as main program
if __name__ == "__main__":

    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = NGL_Bitmap()
    widget.show()
    sys.exit(app.exec_())
