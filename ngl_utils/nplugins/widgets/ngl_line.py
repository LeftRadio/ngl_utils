#!/usr/bin/env python

from ngl_utils.nplugins.widgets.ngl_base import NGL_Base
from PyQt5.QtCore import pyqtProperty, pyqtSignal, QPoint, QLine, QSize, QRect
from PyQt5.QtGui import QPainter


class NGL_Line(NGL_Base):
    """
    NGL_Line(NGL_Base)
    Provides a embedded NGL library line widget.
    """

    # Signal used to indicate changes to the status of the widget.
    valueChanged = pyqtSignal(QLine)

    def __init__(self, parent=None):
        """ Constructor for ngl widget """
        super(NGL_Line, self).__init__(parent)

        self._line = QLine(0, 0, 150, 150)
        self._static = True
        self.update()

    def paintEvent(self, event):
        """ Paint ngl widget event """
        p = QPainter()
        p.begin(self)
        p.drawLine(self._line)
        p.end()

    def sizeHint(self):
        """ Return Qt sizeHint """
        return self._size()

    def _size(self):
        width = abs(self._line.x2() - self._line.x1()) + 1
        height = abs(self._line.y2() - self._line.y1()) + 1
        return QSize(width, height)

    def update(self):
        self._size_update()
        super(NGL_Line, self).update()

    def _size_update(self):
        """ Size update for widget """
        w = self._size().width()
        h = self._size().height()

        self.setMinimumSize(w, h)
        self.setMaximumSize(w, h)

    # # Provide getter and setter methods for the property.
    @pyqtProperty(QPoint)
    def P1(self):
        return self._line.p1()

    @P1.setter
    def P1(self, point):
        self._line.setP1(point)
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(QPoint)
    def P2(self):
        return self._line.p2()

    @P2.setter
    def P2(self, point):
        self._line.setP2(point)
        self.update()

    def doNGLCode(self, **kwargs):
        template = 'NGL_GP_DrawLine({x0}, {y0}, {x1}, {y1}, {color});'

        # convert coordinates
        g = self._ngl_geometry()

        y1 = self._ngl_y(self.P1.y(), g.height() - 1)
        y2 = self._ngl_y(self.P2.y(), g.height() - 1)

        return template.format(
            x0 = g.x(),
            y0 = g.y() + y1,
            x1 = g.x() + g.width() - 1,
            y1 = g.y() + y2,
            color = self._ngl_color('color: rgb'))


# if run as main program
if __name__ == "__main__":

    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = NGL_Line()
    widget.show()
    widget.doNGLCode()
    sys.exit(app.exec_())
