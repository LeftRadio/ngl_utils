#!/usr/bin/env python3

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QFontMetrics, QPainter, QColor
from PyQt5.QtWidgets import QWidget, QTextBrowser, QGridLayout

# ------------------------------------------------------------------------------
# CodeView_Window
# ------------------------------------------------------------------------------
class CodeView_Window(QWidget):

    def __init__(self, parent=None):
        super(CodeView_Window, self).__init__(parent, Qt.Tool)

        self.setWindowTitle("NGL Font Generated Code");

        self.layout = QGridLayout()

        self.txtBrowser = CodeView_TextBrowser()
        self.txtBrowser.setCurrentFont(QFont('Liberation Mono', 9)) #QTextEdit::setCurrentFont(const QFont & f)
        self.txtBrowser.set_LineNumArea()

        self.layout.addWidget(self.txtBrowser, 0, 0)
        self.setLayout(self.layout);

        self.setMinimumSize(700, 500);
        self.setWindowModality(Qt.ApplicationModal)

    def view(self, nfont):
        if nfont:
            self.txtBrowser.clear()
            self.txtBrowser.insertPlainText( nfont.code )
            self.show()

# ------------------------------------------------------------------------------
# TextLineNumArea
# ------------------------------------------------------------------------------
class TextLineNumArea(QWidget):

    def __init__( self,
                  font = QFont('Liberation Mono', 9),
                  location = 'locationLeft',
                  text_align = Qt.AlignRight,
                  max_sym = 4,
                  parent = None ):
        super(TextLineNumArea, self).__init__(parent)

        self._font = font
        self._font.setBold(True)
        self._width = QFontMetrics(self._font).boundingRect(''.join(['0' for x in range(max_sym)])).width() + 8
        self._height = 100
        self.line_interval = 0
        self.v_scroll = None
        self.block_cnt = None

    def sizeHint(self):
        return QSize(self._width, self._height)

    def paintEvent(self, event):
        super(TextLineNumArea, self).paintEvent(event)

        # draw background
        painter = QPainter(self)
        painter.fillRect( self._width - 2, 0, self._width, self._height, QColor.fromRgb(192, 226, 192, 255) )
        painter.fillRect( 0, 0, self._width - 2, self._height, QColor.fromRgb(0, 127, 85, 226) )

        # calc range for blocks
        blck_height = (self._height + self.v_scroll().maximum()) / self.block_cnt()
        blck_start = int( self.v_scroll().value() / blck_height )
        blck_end = blck_start + int( self._height / blck_height ) + 1
        if blck_end > self.block_cnt(): blck_end = self.block_cnt()

        # draw line numbers
        painter.setPen(Qt.white)
        painter.setFont(self._font)
        for line in range(blck_start, blck_end):
            x = 0
            y = (line * self.line_interval) - self.v_scroll().value()
            w = self._width - 4
            h = self.line_interval
            painter.drawText ( x, y + 4, w, h, Qt.AlignRight, str(line) )

    def setHeight(self, val):
        self._height = val
    def height(self):
        return self._height
    def setWidth(self, val):
        self._width = val
    def width(self):
        return self._width

    def setLineInterval(self, line_interval_font):
        self.line_interval = QFontMetrics(line_interval_font).boundingRect('A').height()

    def setBlocksCount(self, block_count):
        self.block_cnt = block_count

    def setVScroll(self, scroll):
        self.v_scroll = scroll

# ------------------------------------------------------------------------------
# CodeView_TextBrowser
# ------------------------------------------------------------------------------
class CodeView_TextBrowser( QTextBrowser ):

    def __init__(self, parent = None):
        super(CodeView_TextBrowser, self).__init__(parent)
        self.lineEdit = None

    def set_LineNumArea(self, font = None, location = 'locationLeft', text_align = Qt.AlignRight, max_sym = 4 ):
        """
            Create and config TextLineNumArea
        """
        _font = font or self.currentFont()
        self.lineEdit = TextLineNumArea( _font, location, text_align, max_sym, self )
        self.lineEdit.setLineInterval( _font )
        self.lineEdit.setHeight( self.height() )
        self.lineEdit.setBlocksCount( self.document().blockCount )
        self.lineEdit.setVScroll( self.verticalScrollBar )

        self.setViewportMargins(self.lineEdit.width() + 4, 0, 0, 0)
        self.update()

    def paintEvent(self, event):
        super(CodeView_TextBrowser, self).paintEvent(event)
        self.lineEdit.repaint()



