#!/usr/bin/env python

from ngl_utils.nplugins.widgets import NGL_Base

from random import randint
from PyQt5.QtCore import pyqtProperty, pyqtSlot, Qt
from PyQt5.QtGui import QColor

# from ngl_utils.nplugins.widgets.ngl_fillbar import NGL_FillBar
# from ngl_utils.nplugins.widgets.ngl_graph_scale import NGL_GraphScale
# from ngl_utils.nplugins.widgets.qstyle_parser import QStyleParser
# from ngl_utils.nplugins.widgets.ngl_colors import NGL_Colors


class NGL_Spectrum(NGL_Base):
    """docstring for NGL_Spectrum"""
    def __init__(self, parent=None):
        super(NGL_Spectrum, self).__init__(parent)

        self._logarithmic = True
        self._bands_count = 16
        self._fillbars = []
        self._markers = True
        self._markers_color = Qt.black

        self.setGeometry(100, 100, 500, 70)
        self.setStyleSheet('color: rgb(128, 128, 128);')

        self._setBandsCount()

    def update(self):
        self._updateBandsGeometry()
        super(NGL_Spectrum, self).update()

    def resizeEvent(self, event):
        super(NGL_Spectrum, self).resizeEvent(event)
        self.update()

    def sizeHint(self):
        """ Return Qt sizeHint """
        return self.size()

    def _updateBandsGeometry(self):
        g = self.size()
        cnt = 0

        for fl in self._fillbars:
            width = g.width() / len(self._fillbars)
            fl.setGeometry(1 + width * cnt, 0, width, g.height())
            cnt += 1

    def _bandColor(self, bandnum):
        index = (256 * bandnum) // self._bands_count
        color = NGL_Colors.getColor(index)
        return QColor(color)

    def _setBandsCount(self):

        for bn in self._fillbars:
            bn.setParent(None)
            del(bn)

        self._fillbars = []
        for x in range(self._bands_count):
            fillbar = NGL_FillBar(self)

            styleSheet = QStyleParser.getColorStyleSheet(self._bandColor(x), 'color')
            fillbar.setStyleSheet(styleSheet)
            fillbar.setOrientation(Qt.Vertical)
            fillbar.setBorder(False)
            fillbar.setMarkers(True)
            self._randLevel(fillbar)
            self._fillbars.append(fillbar)

        self.update()

    def _randLevel(self, bund):
        lvl = randint(bund.getMin(), bund.getMax())
        bund.setLevel(lvl)

    def mousePressEvent(self, event):
        for fl in self._fillbars:
            self._randLevel(fl)

    def _bundsSetParam(self, func, value):
       for fl in self._fillbars:
            func(fl, value)



    #
    # Provide getter and setter methods for the property.
    #

    def getLog(self):
        return self._logarithmic

    @pyqtSlot(bool)
    def setLog(self, state):
        self._logarithmic = state
        self._bundsSetParam(NGL_FillBar.setLogaritmic, state)
        self.update()

    Log = pyqtProperty(bool, getLog, setLog)


    #
    # Provide getter and setter methods for the property.
    #

    def getBandsNum(self):
        return self._bands_count

    @pyqtSlot(int)
    def setBandsNum(self, band_num):
        self._bands_count = band_num
        self._setBandsCount()
        self.update()

    BandsNum = pyqtProperty(int, getBandsNum, setBandsNum)


    #
    # Provide getter and setter methods for the property.
    #

    def getMarkers(self):
        return self._markers

    @pyqtSlot(bool)
    def setMarkers(self, state):
        self._markers = state
        self._bundsSetParam(NGL_FillBar.setMarkers, state)
        self.update()

    markers = pyqtProperty(bool, getMarkers, setMarkers)


    #
    # Provide getter and setter methods for the property.
    #

    def getMarkersColor(self):
        return self._markers_color

    @pyqtSlot(QColor)
    def setMarkersColor(self, color):
        self._markers_color = color
        self._bundsSetParam(NGL_FillBar.setMarkersColor, color)
        self.update()

    markersColor = pyqtProperty(QColor, getMarkersColor, setMarkersColor)




# if run as main program
if __name__ == "__main__":

    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = NGL_Spectrum()

    widget.setMarkersColor(Qt.black)
    widget.setMarkers(True)
    widget.setLog(False)

    widget.show()
    sys.exit(app.exec_())
