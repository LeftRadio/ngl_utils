#!/usr/bin/env python

from ngl_utils.nplugins.widgets import NGL_Base

from PyQt5.QtCore import pyqtProperty, pyqtSlot, QPoint, QSize, Qt
from PyQt5.QtGui import QPainter, QFont, QFontMetrics, QPen


class NGL_GraphScale(NGL_Base):
    """
    NGL_GraphScale(NGL_Base)
    Provides a embedded NGL library graphics scale widget.
    """

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
            w = fmr.width()+1
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
            self._paintHorisontal(painter)
        else:
            self._paintVertical(painter)



        painter.end()

    def _paintHorisontal(self, painter):
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


    #
    # Provide getter and setter methods for the property.
    #

    def getFont(self):
        return self._font

    @pyqtSlot(QFont)
    def setFont(self, font):
        self._font = font
        self.update()

    Font = pyqtProperty(QFont, getFont, setFont)

    #
    # Provide getter and setter methods for the property.
    #

    def getGradientText(self):
        return self._gradient_text

    @pyqtSlot(bool)
    def setGradientText(self, gradient):
        self._gradient_text = gradient
        self.update()

    GradientText = pyqtProperty(bool, getGradientText, setGradientText)

    #
    # Provide getter and setter methods for the property.
    #

    def getMax(self):
        return self._max

    @pyqtSlot(int)
    def setMax(self, val):
        self._max = val
        self.update()

    Max = pyqtProperty(int, getMax, setMax)

    #
    # Provide getter and setter methods for the property.
    #

    def getMin(self):
        return self._min

    @pyqtSlot(int)
    def setMin(self, val):
        self._min = val
        self.update()

    Min = pyqtProperty(int, getMin, setMin)


    #
    # Provide getter and setter methods for the property.
    #

    def getScaleCent(self):
        return self._scale_cent

    @pyqtSlot(int)
    def setScaleCent(self, val):
        self._scale_cent = val
        self.update()

    ScaleCent = pyqtProperty(int, getScaleCent, setScaleCent)

    #
    # Provide getter and setter methods for the property.
    #

    def getLabels(self):
        return self._labels

    @pyqtSlot(str)
    def setLabels(self, labels):
        self._labels = labels
        self.update()

    Labels = pyqtProperty(str, getLabels, setLabels)

    #
    # Provide getter and setter methods for the property.
    #

    def getUnits(self):
        return self._units

    @pyqtSlot(str)
    def setUnits(self, units):
        self._units = units
        self.update()

    Units = pyqtProperty(str, getUnits, setUnits)

    #
    # Provide getter and setter methods for the property.
    #

    def getShowLabels(self):
        return self._show_labels

    @pyqtSlot(bool)
    def setShowLabels(self, showlabels):
        self._show_labels = showlabels
        self.update()

    ShowLabels = pyqtProperty(bool, getShowLabels, setShowLabels)

    #
    # Provide getter and setter methods for the property.
    #

    def getShowLines(self):
        return self._show_lines

    @pyqtSlot(bool)
    def setShowLines(self, showlines):
        self._show_lines = showlines
        self.update()

    ShowLines = pyqtProperty(bool, getShowLines, setShowLines)

    #
    # Provide getter and setter methods for the property.
    #

    def getOrientation(self):
        return self._orientation

    @pyqtSlot(Qt.Orientation)
    def setOrientation(self, orientation):
        self._orientation = orientation
        self.update()

    Orientation = pyqtProperty(Qt.Orientation, getOrientation, setOrientation)


    #
    # Provide getter and setter methods for the property.
    #

    def getFlip(self):
        return self._flip

    @pyqtSlot(bool)
    def setFlip(self, flip):
        self._flip = flip
        self.update()

    Flip = pyqtProperty(bool, getFlip, setFlip)



# if run as main program
if __name__ == "__main__":

    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = NGL_GraphScale()

    widget.setOrientation(Qt.Vertical)
    widget.setFlip(True)
    widget.setShowLines(True)
    widget.setShowLabels(True)

    widget.show()
    sys.exit(app.exec_())
