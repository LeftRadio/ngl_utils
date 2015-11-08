#!/usr/bin/env python

from ngl_utils.nplugins.widgets.ngl_base import NGL_Base
from ngl_utils.nplugins.widgets.qstyle_parser import QStyleParser
from PyQt5.QtCore import pyqtSlot, pyqtProperty, QRect
from PyQt5.QtGui import QPainter


class NGL_Rect(NGL_Base):
    """NGL_Rect(NGL_Base)
    Provides a embedded NGL library rect widget.
    """

    def __init__(self, parent=None):
        """ Constructor for ngl widget """
        super(NGL_Rect, self).__init__(parent)

        self._fill = False
        self._static = True

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
        """ Return Qt sizeHint """
        return self.size()


    #
    # Provide getter and setter methods for the property.
    #

    def getFill(self):
        return self._fill

    @pyqtSlot(bool)
    def setFill(self, fill):
        self._fill = fill
        self.update()

    fill = pyqtProperty(bool, getFill, setFill)


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
    widget = NGL_Rect()
    widget.show()
    print(widget.currentIndex())
    sys.exit(app.exec_())
