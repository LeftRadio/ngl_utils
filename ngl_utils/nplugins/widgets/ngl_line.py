#!/usr/bin/env python

from ngl_utils.nplugins.widgets import NGL_Base
from PyQt5.QtCore import pyqtProperty, pyqtSignal, QPoint, QLine, QSize
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

        self._line = QLine(0, 0, 100, 0)
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
        width = (self._line.x2() - self._line.x1()) + 1
        height = (self._line.y2() - self._line.y1()) + 1

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


    # Provide getter and setter methods for the property.

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


    def doNGLCode(self):
        template = 'NGL_GP_DrawLine({x0}, {y0}, {x1}, {y1}, {color});\n'

        # convert coordinates
        p1 = self._ngl_point(self.P1)
        p2 = self._ngl_point(self.P2)

        return template.format( x0 = p1.x(),
                                y0 = p1.y(),
                                x1 = p2.x(),
                                y1 = p2.y(),
                                color = self._ngl_color('color: rgb') )


# if run as main program
if __name__ == "__main__":

    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = NGL_Line()
    widget.show()
    sys.exit(app.exec_())
