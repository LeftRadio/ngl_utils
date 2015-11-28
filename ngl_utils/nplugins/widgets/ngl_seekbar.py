#!/usr/bin/env python

import math
from ngl_utils.nplugins.widgets.ngl_base import NGL_Base
from ngl_utils.nplugins.widgets.qstyle_parser import QStyleParser
from ngl_utils.nplugins.widgets.ngl_colors import NGL_Colors

from PyQt5.QtCore import pyqtSlot, pyqtProperty, QRect, QSize, Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor


class NGL_SeekBar(NGL_Base):
    """NGL_SeekBar(NGL_Base)
    Provides a embedded NGL library widget.
    """

    # order for NGL library page struct pointers order
    ngl_order = 4

    def __init__(self, parent=None):
        super(NGL_SeekBar, self).__init__(parent)

        self._max = 100
        self._min = 0
        self._level = 50
        self._orientation = Qt.Horizontal
        self._show_progress = True
        self._slider_size = QSize(8,8)
        self._slider_color = QColor(Qt.blue)

        self._eventsEnabled = True

        self.setGeometry(50, 50, 150, 15)
        self.setStyleSheet('color: rgb(64, 128, 64);')
        self.update()

    def paintEvent(self, event):
        p = QPainter()

        color = QStyleParser.getColor(self.styleSheet(), 'color: rgb')
        rect = self.geometry()

        # calc and draw respect orientation
        fullscale = self._max - self._min
        slider_size = self._slider_size

        p.begin(self)

        # calc slider respect orientation
        if self._orientation == Qt.Horizontal:
            posX = self._level * (rect.width() / fullscale)
            posY = rect.height() / 2

        else:
            posX = rect.width() / 2
            posY = rect.height() - ((self._level * rect.height()) / fullscale)

        # calc coordinates respect orientation
        rect_0, rect_1, color_0, color_1 = self._calcCoordinates(posX, posY, slider_size)

        # draw seekbar
        p.fillRect(rect_0, color_0)
        p.setPen(color_0)
        p.drawRect(rect_0)

        p.fillRect(rect_1, color_1)
        p.setPen(color_1)
        p.drawRect(rect_1)

        # draw slider
        for i in range(min(slider_size.width(), slider_size.height())):
            p.setPen(self._slider_color.lighter(100 + (i * 10)))
            p.drawRect(posX - (slider_size.width() - i) // 2,
                       posY - (slider_size.height() - i) // 2,
                       slider_size.width() - i,
                       slider_size.height() - i)

        p.end()

    def _calcCoordinates(self, posX, posY, slider_size):

        rect = self.geometry()
        color = QStyleParser.getColor(self.styleSheet(), 'color: rgb')
        color_0 = color.lighter(125)
        color_1 = color.lighter(125)

        if self._orientation == Qt.Horizontal:
            x0 = 0
            y0 = (rect.height() // 2) - 2
            w0 = (posX - slider_size.width() // 2) - 1
            h0 = 4

            x1 = (posX + slider_size.width() // 2) + 1
            y1 = y0
            w1 = rect.width() - x1
            h1 = 4

            if self._show_progress:
                color_0 = color.lighter(175)

        else:
            x0 = (rect.width() // 2) - 2
            y0 = 0
            w0 = 4
            h0 = (posY - slider_size.height() // 2) - 1

            x1 = x0
            y1 = (posY + slider_size.height() // 2) + 1
            w1 = 4
            h1 = rect.height() - y1

            if self._show_progress:
                color_1 = color.lighter(175)


        rect0 = QRect(x0, y0, w0, h0)
        rect1 = QRect(x1, y1, w1, h1)

        return (rect0, rect1, color_0, color_1)

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
    @pyqtProperty(Qt.Orientation)
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, _orientation):
        self._orientation = _orientation
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(bool)
    def show_progress(self):
        return self._show_progress

    @show_progress.setter
    def show_progress(self, state):
        self._show_progress = state
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(QSize)
    def slidersize(self):
        return self._slider_size

    @slidersize.setter
    def slidersize(self, size):

        if self.orientation == Qt.Horizontal:
            _size = QSize( size.width(), min( self.size().height(), size.height() ) )
        else:
            _size = QSize( min( self.size().width(), size.width() ), size.height() )

        self._slider_size = _size
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(QColor)
    def slidercolor(self):
        return self._slider_color

    @slidercolor.setter
    def slidercolor(self, newcolor):
        self._slider_color = newcolor
        self.update()


    def doNGLCode(self, **kwargs):

        import pkg_resources

        res_path = pkg_resources.resource_filename('ngl_utils', 'templates/seekbar.ntp')
        with open(res_path, 'rt') as f:
            template = f.read()

        # convert coordinates
        g = self._ngl_geometry()

        # orientation
        ori = {1: 'NGL_Horizontal', 2: 'NGL_Vertical'}

        # slider
        if self.orientation == Qt.Horizontal:
            slider_size = self._slider_size.width()
        else:
            slider_size = self._slider_size.height()

        return template.format(
            pageName = self._ngl_parent_obj_name(),
            itemName = self.objectName(),
            x0 = g.x(),
            y0 = g.y(),
            x1 = g.x() + g.width() - 1,
            y1 = g.y() + g.height() - 1,
            slider_size = slider_size,
            old_posX = '(uint16_t)(65535)',
            old_posY = '(uint16_t)(65535)',
            VertHoriz = ori[self.orientation],
            Level_MIN = self.minimum,
            Level_MAX = self.maximum,
            Level = self.level,
            ShowProgress = self._show_progress,
            Color = self._ngl_color('color: rgb'),
            SliderColor = hex(NGL_Colors.fromQColor(self._slider_color)),
            p_event = self.clickEventName)

    @staticmethod
    def ngl_draw(**kwargs):
        s = 'NGL_GUI_DrawSeekBar({objects}[{index}]);'

        return s.format(
            objects = kwargs['name'],
            index = kwargs['index'])


# if run as main program
if __name__ == "__main__":

    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = NGL_SeekBar()
    # widget.orientation = Qt.Vertical
    widget.show()

    sys.exit(app.exec_())
