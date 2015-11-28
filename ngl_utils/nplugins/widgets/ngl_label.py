#!/usr/bin/env python

from ngl_utils.nplugins.widgets.ngl_base import NGL_Base
from ngl_utils.nfont.nfont import NGL_Font

from PyQt5.QtCore import pyqtProperty, pyqtSignal, pyqtSlot, QSize, Qt
from PyQt5.QtGui import QFont, QFontMetrics, QPainter, QTransform, QImage, QPen
from PyQt5.QtWidgets import QApplication


class NGL_Label(NGL_Base):
    """ Provide NGL label widget. """

    # order for NGL library page struct pointers order
    ngl_order = 2

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

        x = (self.size().width()-self.textSize().width())//2
        y = (self.size().height()+self.textSize().height())//2 - self.font_metric().descent()

        self.draw(x, y, p, self)

    def draw(self, x, y, painter, pdevice):

        painter.begin(pdevice)

        painter.setFont(self._font)
        print('lbl 41: ', self.size(), self.textSize(), x, y)
        painter.drawText(x, y, self._text)

        painter.end()

        # QFont.StyleStrategy(QFont.NoAntialias)

        # self.img = QImage(100, 100, QImage.Format_Mono)
        # self.img.fill(0)

        # painter = QPainter(self.img)
        # painter.setPen(QPen(Qt.white))

        # painter.setFont(self._font)
        # painter.setTransform( QTransform(2.0, 0, 0, 1.0, 0, 0) )
        # self._font.StyleStrategy(QFont.NoAntialias)

        # painter.drawText(self.rect(), Qt.AlignJustify, self._text)
        # painter.end()
        # del(painter)

        # self.img.save('.\\i.bmp')

    def sizeHint(self):
        """ return sizeHint """
        return self.size()

    def update(self):
        # self.size_update()
        super(NGL_Label, self).update()

    def font_metric(self):
        return QFontMetrics(self._font)

    def textSize(self):
        rect = self.font_metric().boundingRect(self._text)
        return QSize(rect.width()+1, rect.height()+1)


    # def size_update(self):
    #     size = self._textSize()
    #     self.setMinimumSize(size)
    #     self.setMaximumSize(size)

    #     self._ypos = size.height() - self.font_metric().descent()

    # def reposition(self, x, y):
    #     self._xpos = x
    #     self._ypos = y
    #     self.update()


    # Provide getter and setter methods for the property
    @pyqtProperty(QFont)
    def font(self):
        return self._font

    @font.setter
    def font(self, font):
        self._font = font
        self.update()

    # Provide getter and setter methods for the property
    @pyqtProperty(str)
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text
        self.update()

    # Provide getter and setter methods for the property
    @pyqtProperty(bool)
    def static(self):
        return self._static

    @static.setter
    def static(self, static):
        self._static = static

    def doNGLCode(self, **kwargs):
        """ Generate code for NGL_Label """

        # convert coordinates
        g = self._ngl_geometry()

        # get font pointer name
        _, fontPointerName = NGL_Font.formatQFontName(self.font)

        # if label is a static
        if self.static is True:
            template = 'NGL_Font_DrawString({x}, {y}, {color}, {font}, {transparent}, {text});'

            return template.format(
                x = g.x(),
                y = g.y(),
                color = self._ngl_color('color: rgb'),
                font = fontPointerName,
                transparent = 'Transparent',
                text = '"%s"' % self.text)

        # else return label sctruct code
        else:
            import pkg_resources

            res_path = pkg_resources.resource_filename('ngl_utils', 'templates/label.ntp')
            with open(res_path, 'rt') as f:
                template = f.read()

            textVar = 'static char {0}_text[{1}] = "{2}";'.format(
                self.objectName(),
                len(self.text)+1,
                self.text)

            return template.format(
                pageName = self._ngl_parent_obj_name(),
                itemName = self.objectName(),
                x = g.x(),
                y = g.y(),
                color = self._ngl_color('color: rgb'),
                transparent = 'Transparent',
                textVar = textVar,
                text = '(char*)%s_text' % self.objectName(),
                fontName = fontPointerName
            )

    @staticmethod
    def ngl_draw(**kwargs):
        s = 'NGL_GUI_DrawLabel({objects}[{index}]);'

        return s.format(
            objects = kwargs['name'],
            index = kwargs['index'])


# if run as main program
if __name__ == "__main__":

    import sys

    app = QApplication(sys.argv)
    widget = NGL_Label()
    widget.show()
    sys.exit(app.exec_())
