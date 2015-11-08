#!/usr/bin/env python

from PyQt5.QtCore import Qt, QRect, pyqtProperty, pyqtSlot
from PyQt5.QtWidgets import QWidget, QStackedWidget
from PyQt5.QtGui import QColor

from ngl_utils.nplugins.widgets.ngl_colors import NGL_Colors
from ngl_utils.nfont.nfont import NGL_Font
from ngl_utils.nplugins.widgets.qstyle_parser import QStyleParser


class NGL_Base(QWidget):
    """ """

    # order for NGL library page struct pointers order
    ngl_order = 2**32

    def __init__(self, parent=None):
        """ Constructor for NGL_Base """
        super(NGL_Base, self).__init__(parent)

        self.setStyleSheet('color: rgb(128, 128, 128);\n')
        self._static = False
        self._layer = 0

        self._clickEventName = ''
        self._eventsEnabled = False

        self.objectNameChanged.connect(self.nameChanged)

    def _ngl_geometry(self):
        g = self.geometry()
        pg = self.parent().geometry()

        ny = pg.height() - (g.y() + g.height() - 1)
        ng = QRect(g.x(), ny, g.width(), g.height())

        return ng

    def _ngl_point(self, point):
        return point

    def _ngl_x(self, x):
        return x

    def _ngl_y(self, y, height):
        return (height-1) - y

    def _ngl_color(self, id):
        if self.styleSheet() != '':
            qcolor = QStyleParser.getColor(self.styleSheet(), id)
        else:
            qcolor = QColor(Qt.black)

        # return string in hex format
        return hex(NGL_Colors.fromQColor(qcolor))

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

    def getStatic(self):
        return self._static



    # ---------- common ngl_objects properties ----------
    @pyqtProperty(int)
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, layer):
        self._layer = layer

    @pyqtProperty(bool)
    def eventsEnabled(self):
        return self._eventsEnabled

    @eventsEnabled.setter
    def eventsEnabled(self, eventsEnabled):
        self._eventsEnabled = eventsEnabled

    @pyqtProperty(str)
    def clickEventName(self):
        return self._clickEventName

    @clickEventName.setter
    def clickEventName(self, clickEventName):
        self._clickEventName = clickEventName

    @pyqtSlot(str)
    def nameChanged(self, name):
        if self._eventsEnabled is True:
            self.clickEventName = name + '_click'


    # ---------- default object code gen ----------
    def doNGLCode(self, **kwargs):
        return ('/* NGL_Base default code string */'
                '/* Please define this method in NGL object widget */')

    @staticmethod
    def ngl_draw(**kwargs):
        return ('/* NGL_Base default code string */\n'
                '/* Please define this static method in NGL object widget */')



# if run as main program
if __name__ == "__main__":

    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = NGL_Base()
    widget.show()

    sys.exit(app.exec_())
