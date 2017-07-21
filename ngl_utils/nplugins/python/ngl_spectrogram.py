#!/usr/bin/env python

from ngl_utils.nplugins.widgets.ngl_base import NGL_Base
from ngl_utils.nplugins.widgets.qstyle_parser import QStyleParser
from PyQt5.QtCore import pyqtSlot, pyqtProperty, QRect
from PyQt5.QtGui import QPainter


class NGL_Spectrogram(NGL_Base):
    """NGL_Spectrogram(NGL_Base)
    Provides a embedded NGL library spectrogram widget.
    """

    # order for NGL library page struct pointers order
    ngl_order = 7

    def __init__(self, parent=None):
        """ Constructor for ngl widget """
        super(NGL_Spectrogram, self).__init__(parent)

        self._bands_cnt = 16
        self._bands_freq = '50, 100, 200, 400, 600, 1000, 2000, 3000,' + \
            '4000, 6000, 8000, 10000, 12000, 15000, 18000, 20000'

        self._max = 100
        self._min = 0
        self._logarithmic = False
        self._fullscale_dB = 60

        self._show_labels = True
        self._labels = '50, 100, 200, 400, 600, 1k, 2k, 3k,' + \
            '4k, 6k, 8k, 10k, 12k, 15k, 18k, 20k'

        self._markers = True
        self._markersColor = QColor(Qt.white)

        self.setGeometry(100, 100, 100, 100)
        self.setStyleSheet('color: rgb(64, 64, 64);')
        self.update()

    def paintEvent(self, event):
        """ Paint ngl widget event """
        gw = self.geometry().width()
        gh = self.geometry().height()
        rect = QRect(0, 0, gw-1, gh-1)

        p = QPainter()
        p.begin(self)

        p.drawRect(rect)

        if self._fill:
            color = QStyleParser.getColor(self.styleSheet(), 'color: rgb')
            if color != None:
                p.fillRect( rect, color )

        p.end()

    def sizeHint(self):
        return self.size()


    @pyqtProperty(int)
    def bands_cnt(self):
        return self._bands_cnt

    @bands.setter
    def bands_cnt(self, val):
        self._bands_cnt = val
        self.update()

    @pyqtProperty(str)
    def bands_freq(self):
        return self._bands_freq

    @bands.setter
    def bands_freq(self, val):
        self._bands_freq = val
        self.update()

    @pyqtProperty(int)
    def maximum(self):
        return self._max

    @maximum.setter
    def maximum(self, val):
        self._max = val
        self.update()

    @pyqtProperty(bool)
    def logaritmic(self):
        return self._logarithmic

    @logaritmic.setter
    def logaritmic(self, logaritmic):
        self._logarithmic = logaritmic
        self.update()

    @pyqtProperty(int)
    def fullscale_dB(self):
        return self._fullscale_dB

    @fullscale_dB.setter
    def fullscale_dB(self, fullscale):
        self._fullscale_dB = fullscale
        self.update()

    @pyqtProperty(bool)
    def showLabels(self):
        return self._show_labels

    @showLabels.setter
    def showLabels(self, state):
        self._show_labels = state
        self.update()

    @pyqtProperty(str)
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, labels):
        self._labels = labels
        self.update()

    @pyqtProperty(bool)
    def markers(self):
        return self._markers

    @markers.setter
    def markers(self, markers):
        self._markers = markers
        self.update()

    @pyqtProperty(QColor)
    def markersColor(self):
        return self._markersColor

    @markersColor.setter
    def markersColor(self, color):
        self._markersColor = color
        self.update()





    def doNGLCode(self, **kwargs):
        func = "NGL_GP_DrawRect({x0}, {y0}, {x1}, {y1}, {color}{fill});"
        color = self._ngl_color('color: rgb')
        fill = ''

        if self.fill:
            func = func.replace('NGL_GP_DrawRect', 'NGL_GP_DrawFillRect')
            fill = ', {border}, {border_color}'
            fill = fill.format(border = 'DRAW',
                               border_color = color)

        # convert coordinates
        g = self._ngl_geometry()

        template = func.format(
                x0 = g.x(),
                y0 = g.y(),
                x1 = g.x() + g.width() - 1,
                y1 = g.y() + g.height() - 1,
                color = color,
                fill = fill)

        return template



# if run as main program
if __name__ == "__main__":

    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = NGL_Spectrogram()
    widget.show()
    print(widget.currentIndex())
    sys.exit(app.exec_())
