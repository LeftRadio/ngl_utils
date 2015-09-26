#!/usr/bin/env python

from ngl_utils.nplugins.widgets import NGL_Base

from PyQt5.QtCore import pyqtProperty, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QFont, QFontMetrics, QPainter
from PyQt5.QtWidgets import QApplication
from ngl_utils.nfont.nfont import NGL_Font


class NGL_Label(NGL_Base):
    """ Provide NGL label widget. """

    # Signal used to indicate changes to the status of the widget.
    valueChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super(NGL_Label, self).__init__(parent)

        self._xpos = 0
        self._ypos = 0

        self._font = QFont()
        self._text = self.__class__.__name__

        self.setStyleSheet('color: rgb(64, 64, 64);')
        self.update()

    def paintEvent(self, event):
        p = QPainter()
        p.begin(self)

        # QFont.StyleStrategy(QFont.NoAntialias)
        p.setFont(self._font)
        p.drawText(self._xpos, self._ypos, self._text)

        p.end()

    def sizeHint(self):
        """ return sizeHint """
        return self._textSize()

    def update(self):
        self.size_update()
        super(NGL_Label, self).update()

    def _font_metric(self):
        return QFontMetrics(self._font)

    def _textSize(self):
        rect = self._font_metric().boundingRect(self._text)
        print(rect)
        return QSize(rect.width()+1, rect.height()+1)

    def size_update(self):
        size = self._textSize()
        self.setMinimumSize(size)
        self.setMaximumSize(size)

        ypos = size.height() - self._font_metric().descent()
        self.reposition(0, ypos)

    def reposition(self, x, y):
        self._xpos = x
        self._ypos = y


    #
    # Provide getter and setter methods for the property.
    #

    def getFont(self):
        return self._font

    @pyqtSlot(QFont)
    def setFont(self, font):
        self._font = font
        self.update()

    font = pyqtProperty(QFont, getFont, setFont)


    #
    # Provide getter and setter methods for the property.
    #

    def getText(self):
        return self._text

    @pyqtSlot(str)
    def setText(self, text):
        self._text = text
        self.update()

    text = pyqtProperty(str, getText, setText)


    def doNGLCode(self):
        """ Generate struct code for NGL_Label """

        template = ("""
/* {pageName} {itemName} item */
    NGL_Label {itemName} = {{
    {x},
    {y},
    {color},
    {visible},
    {text},
    {fontName},
}};""")

        # convert coordinates
        g = self._ngl_geometry()

        # get font pointer name
        _, fontPointerName = NGL_Font.formatQFontName(self.font)

        return template.format( pageName = self._ngl_parent_obj_name(),
                                itemName = self.objectName(),
                                x = g.x(),
                                y = g.y(),
                                color = self._ngl_color('color: rgb'),
                                visible = True,
                                text = '&%s_text' % self.objectName(),
                                fontName = fontPointerName
        ).replace('True', 'ENABLE').replace('False', 'DISABLE')



# if run as main program
if __name__ == "__main__":

    import sys

    app = QApplication(sys.argv)
    widget = NGL_Label()
    widget.show()
    sys.exit(app.exec_())
