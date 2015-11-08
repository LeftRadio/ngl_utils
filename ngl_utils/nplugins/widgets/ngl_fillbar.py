#!/usr/bin/env python

import math
from ngl_utils.nplugins.widgets.ngl_base import NGL_Base
from ngl_utils.nplugins.widgets.qstyle_parser import QStyleParser
from ngl_utils.nplugins.widgets.ngl_colors import NGL_Colors

from PyQt5.QtCore import pyqtSlot, pyqtProperty, QRect, QSize, Qt
from PyQt5.QtGui import QPainter, QPen, QColor


class NGL_FillBar(NGL_Base):
    """NGL_FillBar(NGL_Base)
    Provides a embedded NGL library widget.
    """

    # order for NGL library page struct pointers order
    ngl_order = 3

    def __init__(self, parent=None):
        super(NGL_FillBar, self).__init__(parent)

        self._max = 100
        self._min = 0
        self._level = 50
        self._logarithmic = False
        self._fullscale_dB = 120
        self._orientation = Qt.Horizontal
        self._border = True
        self._markers = False
        self._markersColor = QColor(Qt.white)

        self._intLevel = 0
        self._intFullscale = 0


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
        if self._logarithmic:
            self._intFullscale = self._fullscale_dB
            if self._level != 0:
                self._intLevel = self._intFullscale - 20*math.log10( (self._max - self._min) / self._level )
            else:
                self._intLevel = 0
        else:
            self._intFullscale = self._max - self._min
            self._intLevel = self._level

        # calc and draw respect orientation
        if self._orientation == Qt.Horizontal:
            _width = self._intLevel * (rect.width() / self._intFullscale)
            _height = rect.height()
            p.fillRect(0, 0, _width, _height, color)
        else:
            _width = rect.width() - 1
            _height = self._intLevel * (rect.height() / self._intFullscale)
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
    @pyqtProperty(int)
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        self._level = level
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(int)
    def maximum(self):
        return self._max

    @maximum.setter
    def maximum(self, max):
        self._max = max
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(int)
    def minimum(self):
        return self._min

    @minimum.setter
    def minimum(self, min):
        self._min = min
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(bool)
    def logaritmic(self):
        return self._logarithmic

    @logaritmic.setter
    def logaritmic(self, logaritmic):
        self._logarithmic = logaritmic
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(int)
    def fullscale_dB(self):
        return self._fullscale_dB

    @fullscale_dB.setter
    def fullscale_dB(self, fullscale):
        self._fullscale_dB = fullscale
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(Qt.Orientation)
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, orientation):
        self._orientation = orientation
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(bool)
    def border(self):
        return self._border

    @border.setter
    def border(self, border):
        self._border = border
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(bool)
    def markers(self):
        return self._markers

    @markers.setter
    def markers(self, markers):
        self._markers = markers
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(QColor)
    def markersColor(self):
        return self._markersColor

    @markersColor.setter
    def markersColor(self, color):
        self._markersColor = color
        self.update()


    def doNGLCode(self, **kwargs):

        import pkg_resources

        res_path = pkg_resources.resource_filename('ngl_utils', 'templates/fillbar.ntp')
        with open(res_path, 'rt') as f:
            template = f.read()

        # convert coordinates
        g = self._ngl_geometry()

        # orientation
        ori = {1: 'NGL_Horizontal', 2: 'NGL_Vertical'}

        return template.format(
                pageName = self._ngl_parent_obj_name(),
                itemName = self.objectName(),
                x0 = g.x(),
                y0 = g.y(),
                x1 = g.x() + g.width() - 1,
                y1 = g.y() + g.height() - 1,
                VertHoriz = ori[self.orientation],
                Level_MIN = self.minimum,
                Level_MAX = self.maximum,
                Level = self.level,
                sfX1 = g.x(),
                sfY1 = g.y(),
                Logarithmic = self.logaritmic,
                FullScale_dB = self.fullscale_dB,
                Border = self.border,
                Markers = self.markers,
                MarkersColor = hex(NGL_Colors.fromQColor(self.markersColor)),
                Color = self._ngl_color('color: rgb')
        )

    @staticmethod
    def ngl_draw(**kwargs):
        s = 'NGL_GUI_DrawFillBar({objects}[{index}]);'

        return s.format(
            objects = kwargs['name'],
            index = kwargs['index'])


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
