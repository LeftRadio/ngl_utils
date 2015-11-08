#!/usr/bin/env python

from ngl_utils.nplugins.widgets.ngl_base import NGL_Base
from ngl_utils.nplugins.widgets.ngl_colors import NGL_Colors
from ngl_utils.nfont.nfont import NGL_Font
from ngl_utils.nplugins.widgets.qstyle_parser import QStyleParser

from PyQt5.QtCore import Qt, pyqtSlot, pyqtProperty, QRect, QSize
from PyQt5.QtGui import QPainter, QFont, QFontMetrics, QColor


class NGL_CheckBox(NGL_Base):
    """NGL_CheckBox(NGL_Base)
    Provides a embedded NGL library rect widget.
    """
    _text_indent_px = 4

    def __init__(self, parent=None):
        """ Constructor for ngl widget """
        super(NGL_CheckBox, self).__init__(parent)

        self._checked = True
        self._text = 'CheckBox'
        self._font = QFont()
        self._box_sqsize = 14
        self._color = QColor(143, 143, 143)

        _width = self._box_sqsize + 2 + self.textSize().width()
        _height = self._box_sqsize

        self._eventsEnabled = True

        self.setGeometry(100, 100, _width, _height)
        self.setStyleSheet('color: rgb(128, 128, 128);')
        self.update()

    def paintEvent(self, event):
        """ Paint ngl widget event """
        self._box_sqsize = self.size().height()

        p = QPainter()
        p.begin(self)

        self.drawBox(p)
        self.drawText(p)

        p.end()

    def drawBox(self, painter):
        """ Paint box """
        color = self._color
        rect = QRect(0, 0, self._box_sqsize, self._box_sqsize)

        for sz in range(3):
            painter.setPen(color.lighter(200 // (sz+1)))
            painter.drawRect( rect.x()+sz, rect.y()+sz, rect.width()-(sz*2), rect.height()-(sz*2) )

        painter.fillRect(rect.x()+3, rect.y()+3, rect.width()-6, rect.height()-6, color.lighter(200))

        if self._checked:
            painter.setPen(QColor(0, 0, 0))
            painter.drawLine(
                rect.x()+2,
                rect.y() + (rect.height()//2),
                rect.width()//2,
                rect.y() + (rect.height()-2))

            painter.drawLine(
                rect.width()//2,
                rect.y() + (rect.height()-2),
                rect.width()-1,
                rect.y() + 2)

    def drawText(self, painter):
        """ Paint checkbox text """

        color = QStyleParser.getColor(self.styleSheet(), 'color: rgb')

        x = self._box_sqsize + NGL_CheckBox._text_indent_px
        y = ((self._box_sqsize + self.textSize().height()) // 2) - self.font_metric().descent()

        # lbl.draw(x, y, painter, pdevice)
        painter.setPen(color)
        painter.setFont(self._font)
        painter.drawText(x, y, self._text)

    def font_metric(self):
        return QFontMetrics(self._font)

    def textSize(self):
        rect = self.font_metric().boundingRect(self._text)
        return QSize(rect.width()+1, rect.height()+1)

    def sizeHint(self):
        """ Return Qt sizeHint """
        return self.size()


    # Provide getter and setter methods for the property.
    @pyqtProperty(bool)
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, state):
        self._checked = state
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(QColor)
    def boxcolor(self):
        return self._color

    @boxcolor.setter
    def boxcolor(self, bcolor):
        self._color = bcolor
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(str)
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text
        self.update()

    # Provide getter and setter methods for the property
    @pyqtProperty(QFont)
    def font(self):
        return self._font

    @font.setter
    def font(self, font):
        self._font = font
        self.update()


    def doNGLCode(self, **kwargs):

        import pkg_resources

        res_path = pkg_resources.resource_filename('ngl_utils', 'templates/checkbox.ntp')
        with open(res_path, 'rt') as f:
            template = f.read()

        # convert coordinates
        g = self._ngl_geometry()

        # get font pointer name
        _, fontPointerName = NGL_Font.formatQFontName(self.font)

        # text var
        __text_var_name = self.objectName().lower() + '_text'
        __text_var = 'static const char {0}[{1}] = "{2}";'.format(__text_var_name,
                                                                  len(self._text)+1,
                                                                  self._text)
        __text_pointer = __text_var_name

        return template.format(
            pageName = self._ngl_parent_obj_name(),
            itemName = self.objectName(),
            text_var = __text_var,
            x0 = g.x(),
            y0 = g.y(),
            x1 = g.x() + g.width() - 1,
            y1 = g.y() + g.height() - 1,
            checked = self._checked,
            font_pointer = fontPointerName.replace('(NGL_Font*)', ''),
            text_pointer = __text_pointer,
            color = hex(NGL_Colors.fromQColor(self._color)),
            text_color = self._ngl_color('color: rgb'),
            p_event = self.clickEventName
        )

    @staticmethod
    def ngl_draw(**kwargs):
        s = 'NGL_GUI_DrawCheckBox({objects}[{index}]);'

        return s.format(
            objects = kwargs['name'],
            index = kwargs['index'])




# if run as main program
if __name__ == "__main__":

    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = NGL_CheckBox()
    widget.show()

    sys.exit(app.exec_())
