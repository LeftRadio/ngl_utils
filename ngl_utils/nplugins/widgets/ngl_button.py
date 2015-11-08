#!/usr/bin/env python

from ngl_utils.nplugins.widgets.ngl_base import NGL_Base
from ngl_utils.nplugins.widgets.qstyle_parser import QStyleParser

from PyQt5.QtCore import pyqtProperty, QRect, QSize, Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QIcon


class NGL_Button(NGL_Base):
    """NGL_Button(QWidget)
    Provides a embedded NGL library button widget.

    NGL_Button types:
        NGL_Button.text = 'text'
            simple text button with transparent background

        NGL_Button.fill = 'fill'
            filled button with or without gradient background

        NGL_Button.ico = 'ico'
            only icon button

        NGL_Button.ico_text = 'ico_text'
            icon and text button type
    """
    text = 'text'
    fill = 'fill'
    ico = 'ico'
    ico_text = 'ico_text'

    # order for NGL library page struct pointers order
    ngl_order = 1

    def __init__(self, parent=None):
        """ NGL_Button widget constructor """
        super(NGL_Button, self).__init__(parent)

        # self._rect = QRect(0, 0, 70, 25)
        self._gradient = True
        self._font = QFont()
        self._text = self.__class__.__name__
        self._sx = 0
        self._sy = 0
        self._ico = QIcon()
        self._ico_size = QSize(32, 32)

        self._eventsEnabled = True

        self.setGeometry(100, 100, 70, 25)
        self.styleType = NGL_Button.fill
        self.setStyleSheet('background-color: rgb(192, 0, 0);\n'
                           'color: rgb(64, 64, 64);')
        self.update()

    def paintEvent(self, event):
        """ Paint ngl widget event """
        p = QPainter()
        p.begin(self)

        backcolor, text_color = self._getColors()

        if self._type == self.fill:
            self._drawFill(p, backcolor)
            self._drawText(p, text_color, Qt.AlignCenter)

        elif self._type == self.ico:
            self._drawICO(p)

        elif self._type == self.ico_text:
            self._drawICO(p)
            self._drawText(p, text_color, Qt.AlignHCenter | Qt.AlignBottom)

        else:
            self._drawText(p, text_color)

        p.end()

    def _drawFill(self, painter, backcolor):
        """ draw background for fill type button """
        if self._gradient:
            pen = QPen(backcolor)

            for y in range( self._rect().height() ):
                pen.setColor( backcolor.lighter(100 + (y*2)) )

                painter.setPen( pen )
                painter.drawLine( 0, y, self._rect().width(), y )
        else:
            painter.fillRect(self._rect(), backcolor )

    def _drawICO(self, painter, align = Qt.AlignHCenter | Qt.AlignTop):
        """
        Draw button icon.
        Icon rescaled if button.rect() < ico.rect() but in the
        NGL library is not the case.
        Not recommended to do button.rect() < ico.rect().
        """
        ico_size = self._ico_size
        x = (self.size().width() - ico_size.width()) // 2
        y = 0
        rect = QRect(x, y, ico_size.width(), ico_size.height())

        self._ico.paint( painter, rect, align)

    def _drawText(self, painter, color, align = Qt.AlignCenter):
        """ Draw btn text, same as in NGL library """
        painter.setFont(self._font)
        painter.setPen(color)
        painter.drawText(self._rect(), align , self._text)

    def _getColors(self):
        """ Get back and text QColor vars from styleSheet, used QStyleParser """
        style = self.styleSheet()

        backcolor = QStyleParser.getColor( style, 'background-color: rgb' )
        if backcolor == None:
            self.setStyleSheet( style + '\nbackground-color: rgb(168, 0, 0);')
            backcolor = QColor(168, 0, 0)

        color = QStyleParser.getColor( style, 'color: rgb' )
        if color == None:
            self.setStyleSheet( style + '\ncolor: rgb(0, 0, 0);')
            color = Qt.black

        return (backcolor, color)

    def _rect(self):
        return QRect( 0,
                      0,
                      self.geometry().width(),
                      self.geometry().height() )

    def _size(self):
        return QSize( self.geometry().width(),
                      self.geometry().height() )

    def sizeHint(self):
        """ return sizeHint """
        return self._size()


    # Provide getter and setter methods for the property.
    @pyqtProperty(str)
    def styleType(self):
        return self._type

    @styleType.setter
    def styleType(self, ntype):
        self._type = ntype
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(QFont)
    def font(self):
        return self._font

    @font.setter
    def font(self, font):
        self._font = font
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(str)
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(int)
    def text_sx(self):
        return self._sx

    @text_sx.setter
    def text_sx(self, sx):
        self._sx = sx
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(int)
    def text_sy(self):
        return self._sy

    @text_sy.setter
    def text_sy(self, sy):
        self._sy = sy
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(bool)
    def gradient(self):
        return self._gradient

    @gradient.setter
    def gradient(self, gradient):
        self._gradient = gradient
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(QIcon)
    def icon(self):
        return self._ico

    @icon.setter
    def icon(self, icon):
        self._ico = icon
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(QSize)
    def iconSize(self):
        return self._ico_size

    @iconSize.setter
    def iconSize(self, size):
        self._ico_size = size
        self.update()


    def doNGLCode(self, **kwargs):

        import pkg_resources

        res_path = pkg_resources.resource_filename('ngl_utils', 'templates/button.ntp')
        with open(res_path, 'rt') as f:
            template = f.read()

        icon_name = '(void*)0'
        font_pointer_name = '(void*)0'
        backcolor, color = self._getColors()

        if 'iconame' in kwargs and kwargs['iconame'] is not None:
            icon_name = '(NGL_Bitmap*)&' + kwargs['iconame']
        else:
            icon_name = '(void*)0'

        # convert coordinates
        g = self._ngl_geometry()

        __style = {
            'text': 'TextButton',
            'fill': 'ColorFillButton',
            'ico': 'IconButton',
            'ico_text': 'IconButton'}

        return template.format(
            pageName    = self._ngl_parent_obj_name(),
            itemName    = self.objectName(),
            x           = g.x(),
            y           = g.y(),
            width       = g.width(),
            height      = g.height(),
            type        = __style[self.styleType],
            color       = self._ngl_color('background-color: rgb'),
            backColor   = self._ngl_color('background-color: rgb'),
            colorShift  = 'TRUE',
            bitmapName  = icon_name,
            fontName    = self._ngl_font_pointer(),
            text_X_shift = '0',
            text_Y_shift = '0',
            textColor   = self._ngl_color('color: rgb'),
            text        = self.text,
            visible     = 'TRUE',
            status      = 'ENABLE',
            eventName   = self.clickEventName
        )

    @staticmethod
    def ngl_draw(**kwargs):
        s = 'NGL_GUI_DrawButton({objects}[{index}], ResetButton);'

        return s.format(
            objects = kwargs['name'],
            index = kwargs['index'])



# if run as main program
if __name__ == "__main__":

    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = NGL_Button()
    widget.show()

    sys.exit(app.exec_())
