#!/usr/bin/env python

from ngl_utils.nplugins.widgets.ngl_base import NGL_Base
from ngl_utils.nplugins.widgets.qstyle_parser import QStyleParser

from PyQt5.QtCore import pyqtProperty, pyqtSlot, QPoint, QSize, Qt
from PyQt5.QtGui import QPainter, QFont, QFontMetrics, QPen
from ngl_utils.nfont.nfont import NGL_Font


class NGL_GraphScale(NGL_Base):
    """
    NGL_GraphScale(NGL_Base)
    Provides a embedded NGL library graphics scale widget.
    """

    # order for NGL library page struct pointers order
    ngl_order = 5

    def __init__(self, parent=None):
        """ Constructor for ngl widget """
        super(NGL_GraphScale, self).__init__(parent)

        self._font = QFont()
        self._gradient_text = True
        self._max = 0
        self._min = -90
        self._scale_cent = -3
        self._labels = '-90, -60, -42, -30, -24, -18, -12, -6,  -0'
        self._units = 'dB'
        self._show_labels = True
        self._show_lines = True
        self._flip = False
        self._orientation = Qt.Horizontal
        self._old_orientation = None

        self.setGeometry(100, 100, 150, 25)
        self.setStyleSheet('color: rgb(128, 128, 128);')
        self.update()

    def _scaleLenght(self):
        fmr = QFontMetrics(self._font).boundingRect(self._units)

        if self._orientation == Qt.Horizontal:
            w = fmr.width()+2
            lenght = self.geometry().width() - w
        else:
            h = fmr.height()+1
            lenght = self.geometry().height() - h

        return lenght

    def _calcPos(self, level):
        """ return coordinate respect scale level """

        max_level = self._scaleLenght()
        level = int(level)

        pos = (max_level * abs(level)) / (self._max - self._min)

        if self._min < 0:
            pos = max_level - pos

        if pos > max_level:
            pos = max_level
        elif pos < 0:
            pos = 0

        return int(pos)

    def update(self):
        width = self.size().width()
        height = self.size().height()

        if self._show_labels:
            if self._orientation == Qt.Horizontal:
                height = QFontMetrics(self._font).height()
            else:
                width = 45

        if self._show_lines:
            if self._orientation == Qt.Horizontal:
                if self._show_labels:
                    height += 5
                else:
                    height = 5
            else:
                if self._show_labels:
                    width += 5
                else:
                    width = 5

        g = self.geometry()
        g.setSize(QSize(width, height))
        self.setGeometry(g)

        super(NGL_GraphScale, self).update()

    def paintEvent(self, event):
        """ Paint ngl widget event """

        color = QStyleParser.getColor( self.styleSheet(), 'color: rgb' )

        painter = QPainter()
        painter.begin(self)

        painter.setPen(QPen(color))
        painter.setFont(self._font)

        if self._orientation == Qt.Horizontal:
            self._paintHorizontal(painter)
        else:
            self._paintVertical(painter)

        painter.end()

    def _paintHorizontal(self, painter):
        """ Paint horizontal scale """
        if self._show_labels:
            fm = QFontMetrics(self._font)
            fheight = fm.height() - fm.descent()
        else:
            fheight = 0

        if self._flip:
            y0 = fheight
            y1 = y0+3
            y11 = y0+5
            y12 = y0-1
        else:
            y0 = self.geometry().height() - fheight
            y1 = y0-3
            y11 = y0-5
            y12 = self.geometry().height()

        x0 = 0
        x1 = self._scaleLenght()
        lbls = self._labels.replace(' ', '').split(',')

        if self._show_lines:
            # base line
            painter.drawLine(x0, y0, x1, y0)

            # cent lines
            for i in range(0, self._scaleLenght() + 1):
                pos = self._calcPos(self._scale_cent * i)
                painter.drawLine(pos, y0, pos, y1)

            for lbl in lbls:
                pos = self._calcPos(int(lbl))
                painter.drawLine(pos, y0, pos, y11)

        # labels
        if self._show_labels:
            for lbl in lbls:
                pos = self._calcPos(int(lbl))
                self._paintLabel(lbl, pos, y12, painter)

            # draw units label
            x = self._scaleLenght()+1
            pen = painter.pen()
            pen.setColor(pen.color().lighter(120))
            painter.setPen(pen)
            painter.drawText( QPoint(x, y12), self._units )

    def _paintVertical(self, painter):
        """ Paint vertical scale """

        fm = QFontMetrics(self._font)
        fwidth = 25

        if self._flip:
            x0 = fwidth
            x1 = x0 + 3
            x11 = x0 + 5
            # x12 = 10
        else:
            x0 = self.geometry().width() - fwidth
            x1 = x0 - 3
            x11 = x0 - 5
            x12 = x0

        y0 = 0
        y1 = self._scaleLenght()
        lbls = self._labels.replace(' ', '').split(',')

        if self._show_lines:
            # base line
            painter.drawLine(x0, y0, x0, y1)

            # cent lines
            for i in range(0, self._scaleLenght() + 1):
                pos = self._calcPos(self._scale_cent * i)
                painter.drawLine(x1, pos, x0, pos)

                for lbl in lbls:
                    pos = self._calcPos(int(lbl))
                    painter.drawLine(x11, pos, x0, pos)

        # labels
        if self._show_labels:
            for lbl in self._labels.replace(' ', '').split(','):
                pos = self._calcPos(int(lbl))

                if self._flip:
                    x12 = (x0 - fm.boundingRect(lbl).width()) - 4

                self._paintLabel(lbl, x12, pos, painter)

            # draw units label
            y = self._scaleLenght() + fm.height() + 1
            pen = painter.pen()
            pen.setColor(pen.color().lighter(120))
            painter.setPen(pen)
            painter.drawText( QPoint(x12, y), self._units )

    def _paintLabel(self, label, xpos, ypos, painter):
        """  """

        fm = QFontMetrics(self._font)
        frect = fm.boundingRect(label)

        if self._orientation == Qt.Horizontal:
            pos = xpos
            lenght = frect.width() / 2 + frect.width() / 10
        else:
            pos = ypos
            lenght = (frect.height() / 2) - fm.descent()

        if pos > self._scaleLenght() - lenght:
            pos = self._scaleLenght() - lenght
        elif pos <= 0:
            pos = 0

        if self._orientation == Qt.Horizontal:
            if pos >= lenght:
                pos = pos - lenght
            painter.drawText( QPoint(pos, ypos), label )
        else:
            if pos == 0:
                pos = lenght*2
            else:
                pos = pos + lenght
            painter.drawText( QPoint(xpos+2, pos), label )

    def sizeHint(self):
        """ Return Qt sizeHint """
        return QSize( self.geometry().width(),
                      self.geometry().height() )


    # Provide getter and setter methods for the property.
    @pyqtProperty(QFont)
    def font(self):
        return self._font

    @font.setter
    def font(self, font):
        self._font = font
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(bool)
    def gradientText(self):
        return self._gradient_text

    @gradientText.setter
    def gradientText(self, gradient):
        self._gradient_text = gradient
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(int)
    def maximum(self):
        return self._max

    @maximum.setter
    def maximum(self, val):
        self._max = val
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(int)
    def minimum(self):
        return self._min

    @minimum.setter
    def minimum(self, val):
        self._min = val
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(int)
    def scaleCent(self):
        return self._scale_cent

    @scaleCent.setter
    def scaleCent(self, val):
        self._scale_cent = val
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(str)
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, labels):
        self._labels = labels
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(str)
    def units(self):
        return self._units

    @units.setter
    def units(self, units):
        self._units = units
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(bool)
    def showLabels(self):
        return self._show_labels

    @showLabels.setter
    def showLabels(self, showlabels):
        self._show_labels = showlabels
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(bool)
    def showLines(self):
        return self._show_lines

    @showLines.setter
    def showLines(self, showlines):
        self._show_lines = showlines
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(Qt.Orientation)
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, orientation):
        self._orientation = orientation
        self.update()

    # Provide getter and setter methods for the property.
    @pyqtProperty(bool)
    def flip(self):
        return self._flip

    @flip.setter
    def flip(self, flip):
        self._flip = flip
        self.update()


    def doNGLCode(self, **kwargs):

        import pkg_resources

        res_path = pkg_resources.resource_filename('ngl_utils', 'templates/graphscale.ntp')
        with open(res_path, 'rt') as f:
            template = f.read()

        # convert coordinates
        g = self._ngl_geometry()

        # orientation
        ori = {1: 'NGL_Horizontal', 2: 'NGL_Vertical'}

        # get font pointer name
        _, fontPointerName = NGL_Font.formatQFontName(self.font)

        return template.format(
                pageName = self._ngl_parent_obj_name(),
                itemName = self.objectName(),
                x0 = g.x(),
                y0 = g.y(),
                x1 = g.x() + g.width() - 1,
                y1 = g.y() + g.height() - 1,
                minimum = self.minimum,
                maximum = self.maximum,
                scalecent = self.scaleCent,
                labels = '{%s}' % self.labels,
                labels_cnt = len(self.labels.split(',')),
                units = '"%s"' % self.units,
                showlabels = self.showLabels,
                showlines = self.showLines,
                flip = self.flip,
                orientation = ori[self.orientation],
                font = fontPointerName,
                color = self._ngl_color('color: rgb'))

    @staticmethod
    def ngl_draw(**kwargs):
        s = 'NGL_GUI_DrawGraphScale({objects}[{index}]);'

        return s.format(
            objects = kwargs['name'],
            index = kwargs['index'])


# if run as main program
if __name__ == "__main__":

    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = NGL_GraphScale()

    # widget.orientation = Qt.Vertical
    # widget.flip = True
    widget.setStyleSheet('color: rgb(255, 0, 0)')
    widget.showLines = True
    widget.showLabels = True

    widget.show()
    sys.exit(app.exec_())
