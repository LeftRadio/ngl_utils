#!/usr/bin/env python

import math
from ngl_utils.nplugins.widgets import NGL_Base

from PyQt5.QtCore import pyqtSlot, pyqtProperty, QRect, QSize, Qt
from PyQt5.QtGui import QPainter, QPen, QColor
# from PyQt5.QtWidgets import QWidget
# from qstyle_parser import QStyleParser


class NGL_FillBar(NGL_Base):
    """NGL_FillBar(NGL_Base)
    Provides a embedded NGL library rect widget.
    """

    def __init__(self, parent=None):
        super(NGL_FillBar, self).__init__(parent)

        self._max = 100
        self._min = 0
        self._level = 50
        self._logarithmic = False
        self._fullscale_dB = 120
        self._orientation = Qt.Horizontal
        self._border = True
        # self._gradient = True
        self._markers = False
        self._markersColor = Qt.white

        self.setGeometry(50, 50, 150, 15)
        self.setStyleSheet('color: rgb(0, 0, 0);')
        self.update()

    def _paintMarkers(self, rect, painter):
        painter.save()
        painter.setPen(QPen(self._markersColor))

        if self._orientation == Qt.Horizontal:
            painter.drawLine(0, 0, 0, rect.height()-1)
            painter.drawLine(rect.width()-1, 0, rect.width()-1, rect.height()-1)
        else:
            painter.drawLine(0, 0, rect.width()-2, 0)
            painter.drawLine(0, rect.height()-1, rect.width()-2, rect.height()-1)

        painter.restore()

    def paintEvent(self, event):
        p = QPainter()

        color = QStyleParser.getColor(self.styleSheet(), 'color: rgb')
        pen = QPen(color.lighter(75))
        rect = self.geometry()

        p.begin(self)

        # if log type fillbar
        if self._level != 0 and self._logarithmic:
            fullscale = self._fullscale_dB
            level = fullscale - 20*math.log10( (self._max - self._min) / self._level )
        else:
            fullscale = self._max - self._min
            level = self._level

        # calc and draw respect orientation
        if self._orientation == Qt.Horizontal:
            _width = level * (rect.width() / fullscale)
            _height = rect.height()
            p.fillRect(0, 0, _width, _height, color)
        else:
            _width = rect.width() - 1
            _height = level * (rect.height() / fullscale)
            p.fillRect(0, (rect.height() - _height) + 1, _width, _height, color)

        # draw border
        if self._border:
            p.setPen(pen)
            p.drawRect(QRect(0, 0, rect.width()-1, rect.height()-1))

        # draw markers
        if self._markers:
            self._paintMarkers(rect, p)

        p.end()

    def sizeHint(self):
        """ return sizeHint """
        w = self.geometry().width()
        h = self.geometry().height()
        return QSize(w, h)


    # Provide getter and setter methods for the property

    def getLevel(self):
        return self._level

    @pyqtSlot(int)
    def setLevel(self, level):
        self._level = level
        self.update()

    level = pyqtProperty(int, getLevel, setLevel)


    # Provide getter and setter methods for the property.

    def getMax(self):
        return self._max

    @pyqtSlot(int)
    def setMax(self, max):
        self._max = max
        self.update()

    maximum = pyqtProperty(int, getMax, setMax)


    # Provide getter and setter methods for the property.

    def getMin(self):
        return self._min

    @pyqtSlot(int)
    def setMin(self, min):
        self._min = min
        self.update()

    minimum = pyqtProperty(int, getMin, setMin)


    # Provide getter and setter methods for the property.

    def getLogaritmic(self):
        return self._logarithmic

    @pyqtSlot(bool)
    def setLogaritmic(self, logaritmic):
        self._logarithmic = logaritmic
        self.update()

    logaritmic = pyqtProperty(bool, getLogaritmic, setLogaritmic)


    # Provide getter and setter methods for the property.

    def getFullScale_dB(self):
        return self._fullscale_dB

    @pyqtSlot(int)
    def setFullScale_dB(self, fullscale):
        self._fullscale_dB = fullscale
        self.update()

    fullscale_dB = pyqtProperty(int, getFullScale_dB, setFullScale_dB)


    # Provide getter and setter methods for the property.

    def getOrientation(self):
        return self._orientation

    @pyqtSlot(Qt.Orientation)
    def setOrientation(self, orientation):
        self._orientation = orientation
        self.update()

    orientation = pyqtProperty(Qt.Orientation, getOrientation, setOrientation)


    # Provide getter and setter methods for the property.

    def getBorder(self):
        return self._border

    @pyqtSlot(bool)
    def setBorder(self, border):
        self._border = border
        self.update()

    border = pyqtProperty(bool, getBorder, setBorder)


    # Provide getter and setter methods for the property.

    def getMarkers(self):
        return self._markers

    @pyqtSlot(bool)
    def setMarkers(self, markers):
        self._markers = markers
        self.update()

    markers = pyqtProperty(bool, getMarkers, setMarkers)


    # Provide getter and setter methods for the property.

    def getMarkersColor(self):
        return self._markersColor

    @pyqtSlot(QColor)
    def setMarkersColor(self, color):
        self._markersColor = color
        self.update()

    markersColor = pyqtProperty(QColor, getMarkersColor, setMarkersColor)


    def doNGLCode(self):
        # template = ''

        # convert coordinates
        # p1 = self._ngl_point(self.P1)
        # p2 = self._ngl_point(self.P2)

        # return template.format( x0 = p1.x(),
        #                         y0 = p1.y(),
        #                         x1 = p2.x(),
        #                         y1 = p2.y(),
        #                         color = self._ngl_color('color: rgb') )
        return ''


# if run as main program
if __name__ == "__main__":

    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = NGL_FillBar()

    widget.setStyleSheet('color: rgb(0, 255, 0);')
    widget.setOrientation(Qt.Vertical)
    widget.setBorder(True)
    widget.setMarkers(True)
    widget.setMarkersColor(Qt.black)

    # print(help(pyqtProperty))
    o = [w for w in NGL_FillBar.__dict__.keys() if type(NGL_FillBar.__dict__[w]) == pyqtProperty]
    print(o)
    print(type(NGL_FillBar.markers))
    sys.exit(True)

    widget.show()
    sys.exit(app.exec_())
