#!/usr/bin/env python

from ngl_utils.nplugins.widgets import NGL_Base

from PyQt5.QtCore import pyqtProperty, pyqtSlot, QRect, Qt
from PyQt5.QtGui import QPainter, QFontMetrics, QPen, QColor


class NGL_Meter(NGL_Base):
    """docstring for NGL_Meter"""
    def __init__(self, parent=None):
        super(NGL_Meter, self).__init__(parent)

        self._ch_names = ''

        self._fillbars = [NGL_FillBar(self) for ch in range(2)]
        self._fillbars_height = 10
        self._fillbars_border = True
        self._fillbars_markers = False
        self._fillbars_markers_color = Qt.black

        for fl in self._fillbars:
            fl.setBorder(self._fillbars_border)
            fl.setMarkers(self._fillbars_markers)
            fl.setMarkersColor(self._fillbars_markers_color)

        self._scales_en = {'top': True, 'bottom': True}

        self._graphscale_top = NGL_GraphScale(self)
        self._graphscale_top.setFlip(True)

        self._graphscale_bottom = NGL_GraphScale(self)
        self._graphscale_bottom.setFlip(False)

        self.setGeometry(100, 100, 500, 70)
        self.setStyleSheet('color: rgb(128, 128, 128);')
        self.update()

    def paintEvent(self, event):
        color = QStyleParser.getColor(self.styleSheet(), 'color: rgb' )
        names = self._ch_names.replace(' ', '').split(',')

        pen = QPen(color)
        p = QPainter()
        p.begin(self)
        p.setPen(pen)

        if len(names) != 0:
            x0 = 0
            x1 = self._max_width(self._ch_names)

            for i in range(len(self._fillbars)):
                if i < len(names):

                    y0 = self._fillbars[i].geometry().y()
                    y1 = y0 + self._fillbars[i].geometry().height()

                    rect = QRect(x0, y0, x1, y1)
                    p.drawText(rect, Qt.AlignJustify, names[i])
        p.end()

    def update(self):
        self._widgetsUpdate()
        super(NGL_Meter, self).update()

    def _max_width(self, string):
        fm = QFontMetrics(self.font())
        xs = [fm.boundingRect(x).width() for x in string.replace(' ', '').split(',')]
        xmax = 0
        for x in xs:
            if xmax < x:
                xmax = x

        return xmax

    def _widgetsUpdate(self):

        y = 0
        size = self.size()
        fwidth = size.width()

        if self._ch_names != '':
            x0 = self._max_width(self._ch_names) + 2
            width = size.width() - x0
        else:
            x0 = 0
            width = size.width()

        # top scale
        if self._scales_en['top']:
            self._graphscale_top.setHidden(False)

            y = self._graphscale_top.size().height()
            self._graphscale_top.setGeometry( x0, 0, width, y)
            fwidth = self._graphscale_top._scaleLenght()
        else:
            self._graphscale_top.setHidden(True)

        # bottom scale
        if self._scales_en['bottom']:
            self._graphscale_bottom.setHidden(False)

            h = self._graphscale_bottom.size().height()
            y0 = size.height() - h
            self._graphscale_bottom.setGeometry(x0, y0, width, h)
            fwidth = max(fwidth, self._graphscale_bottom._scaleLenght())
        else:
            self._graphscale_bottom.setHidden(True)

        # fillbars
        for fl in self._fillbars:
            g = fl.geometry()
            fl.setGeometry(x0, y, fwidth+1, self._fillbars_height)
            y += self._fillbars_height + 2

    def resizeEvent(self, event):
        super(NGL_Meter, self).resizeEvent(event)
        self.update()

    def sizeHint(self):
        """ Return Qt sizeHint """
        return self.size()

    def setFont(self, font):
        self.update()
        super(NGL_Meter, self).setFont(font)

    def _fillbarsSetParam(self, func, value):
       for fl in self._fillbars:
            func(fl, value)


    #
    # Provide getter and setter methods for the property.
    #

    def getChannels(self):
        return len(self._fillbars)

    @pyqtSlot(int)
    def setChannels(self, channels):
        self._fillbarsSetParam(NGL_FillBar.setParent, None)
        self._fillbars = None
        self._fillbars = [NGL_FillBar(self) for ch in range(channels)]
        self.update()

    Channels = pyqtProperty(int, getChannels, setChannels)


    #
    # Provide getter and setter methods for the property.
    #

    def getFillBarsHeight(self):
        return self._fillbars_height

    @pyqtSlot(int)
    def setFillBarsHeight(self, fillbarheight):
        self._fillbars_height = fillbarheight
        self.update()

    FillBarsHeight = pyqtProperty(int, getFillBarsHeight, setFillBarsHeight)


    #
    # Provide getter and setter methods for the property.
    #

    def getFillBarsColor(self):
        return QStyleParser.getColor(self._fillbars[0].styleSheet(), 'color: rgb' )

    @pyqtSlot(QColor)
    def setFillBarsColor(self, color):
        s = 'color: rgb({R}, {G}, {B});'.format(
            R = color.red(),
            G = color.green(),
            B = color.blue() )

        self._fillbarsSetParam(NGL_FillBar.setStyleSheet, s)
        self.update()

    FillBarsColor = pyqtProperty(QColor, getFillBarsColor, setFillBarsColor)


    #
    # Provide getter and setter methods for the property.
    #

    def getFillBarsBorder(self):
        return self._fillbars_border

    @pyqtSlot(bool)
    def setFillBarsBorder(self, state):
        self._fillbars_border = state
        self._fillbarsSetParam(NGL_FillBar.setBorder, state)
        self.update()

    FillBarsBorder = pyqtProperty(bool, getFillBarsBorder, setFillBarsBorder)


    #
    # Provide getter and setter methods for the property.
    #

    def getFillBarsMarkers(self):
        return self._fillbars_markers

    @pyqtSlot(bool)
    def setFillBarsMarkers(self, state):
        self._fillbars_markers = state
        self._fillbarsSetParam(NGL_FillBar.setMarkers, state)
        self.update()

    FillBarsMarkers = pyqtProperty(bool, getFillBarsMarkers, setFillBarsMarkers)


    #
    # Provide getter and setter methods for the property.
    #

    def getFillBarsMarkersColor(self):
        return self._fillbars_markers_color

    @pyqtSlot(QColor)
    def setFillBarsMarkersColor(self, color):
        self._fillbars_markers_color = color
        self._fillbarsSetParam(NGL_FillBar.setMarkersColor, color)
        self.update()

    FillBarsMarkersColor = pyqtProperty(QColor, getFillBarsMarkersColor, setFillBarsMarkersColor)


    #
    # Provide getter and setter methods for the property.
    #

    def getScaleTop(self):
        return self._scales_en['top']

    @pyqtSlot(bool)
    def setScaleTop(self, state):
        self._scales_en['top'] = state
        self.update()

    ScaleTop = pyqtProperty(bool, getScaleTop, setScaleTop)

    #
    # Provide getter and setter methods for the property.
    #

    def getScaleTopShowLines(self):
        return self._graphscale_top.getShowLines()

    @pyqtSlot(bool)
    def setScaleTopShowLines(self, state):
        self._graphscale_top.setShowLines(state)
        self.update()

    scaleTopShowLines = pyqtProperty(bool, getScaleTopShowLines, setScaleTopShowLines)

    #
    # Provide getter and setter methods for the property.
    #

    def getScaleTopShowLabels(self):
        return self._graphscale_top.getShowLabels()

    @pyqtSlot(bool)
    def setScaleTopShowLabels(self, state):
        self._graphscale_top.setShowLabels(state)
        self.update()

    scaleTopShowLabels = pyqtProperty(bool, getScaleTopShowLabels, setScaleTopShowLabels)

    #
    # Provide getter and setter methods for the property.
    #

    def getScaleBottom(self):
        return self._scales_en['bottom']

    @pyqtSlot(bool)
    def setScaleBottom(self, state):
        self._scales_en['bottom'] = state
        self.update()

    ScaleBottom = pyqtProperty(bool, getScaleBottom, setScaleBottom)

    #
    # Provide getter and setter methods for the property.
    #

    def getScaleBottomShowLines(self):
        return self._graphscale_bottom.getShowLines()

    @pyqtSlot(bool)
    def setScaleBottomShowLines(self, state):
        self._graphscale_bottom.setShowLines(state)
        self.update()

    scaleBottomShowLines = pyqtProperty(bool, getScaleBottomShowLines, setScaleBottomShowLines)

    #
    # Provide getter and setter methods for the property.
    #

    def getScaleBottomShowLabels(self):
        return self._graphscale_bottom.getShowLabels()

    @pyqtSlot(bool)
    def setScaleBottomShowLabels(self, state):
        self._graphscale_bottom.setShowLabels(state)
        self.update()

    scaleBottomShowLabels = pyqtProperty(bool, getScaleBottomShowLabels, setScaleBottomShowLabels)


    #
    # Provide getter and setter methods for the property.
    #

    def getChNames(self):
        return self._ch_names

    @pyqtSlot(str)
    def setChNames(self, string):
        self._ch_names = string
        self.update()

    chNames = pyqtProperty(str, getChNames, setChNames)



# if run as main program
if __name__ == "__main__":

    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = NGL_Meter()

    widget.setScaleTop(False)
    widget.setScaleBottom(False)
    widget.setChannels(4)
    widget.setScaleTop(True)
    widget.setScaleBottom(True)

    widget.setScaleTop(False)
    widget.setScaleBottom(False)
    widget.setChannels(8)
    widget.setScaleTop(True)
    widget.setScaleBottom(True)

    widget.setFillBarsHeight(15)
    widget.setGeometry(100, 100, 700, 170)

    widget.setChNames('Lf, Rf, Lr, Rr, Sb, Fr')

    widget.setFillBarsColor(QColor(Qt.green))

    widget.setFillBarsBorder(False)
    widget.setFillBarsMarkers(True)
    widget.setFillBarsMarkersColor(Qt.blue)

    widget.show()
    sys.exit(app.exec_())
