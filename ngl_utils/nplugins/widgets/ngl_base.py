#!/usr/bin/env python

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor

from ngl_utils.nbitmap.converter import NColor
from ngl_utils.nfont.nfont import NGL_Font
from ngl_utils.nplugins.widgets.qstyle_parser import QStyleParser


class NGL_Base(QWidget):
    """ """

    def _ngl_geometry(self):
        return self.geometry()

    def _ngl_point(self, point):
        return point

    def _ngl_x(self, x):
        return x

    def _ngl_y(self, y):
        return y

    def _ngl_color(self, id):
        if self.styleSheet() != '':
            qcolor = QStyleParser.getColor(self.styleSheet(), id)
        else:
            qcolor = QColor(Qt.black)

        # return string in hex format
        return hex(NColor.fromQColor(qcolor))

    def _ngl_parent_obj_name(self):
        if self.parent() is not None:
            return self.parent().objectName()
        else:
            return ''

    def _ngl_font_name(self):
        if self.font:
            return NGL_Font.formatName(self.font.family(),
                                       self.font.pointSize(),
                                       self.font.bold())
        else:
            return ''

    def _ngl_font_pointer(self):
        if self.font:
            return NGL_Font.formatPointerName(self._ngl_font_name())

    def doNGLCode(self, **kwargs):
        return '/* NGL_Base default code string */'
