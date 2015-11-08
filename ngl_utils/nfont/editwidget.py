 #!/usr/bin/env python3

import sys
import os
import pkg_resources

from PyQt5 import uic
from PyQt5.QtCore import ( QAbstractTableModel, QSize, QRect, QRectF, Qt,
                           QPoint, pyqtSignal, pyqtSlot, QSettings )
from PyQt5.QtGui import QFont, QFontMetrics, QImage, QPainter, QBrush, qGray
from PyQt5.QtWidgets import ( QApplication, QWidget, QAbstractItemDelegate,
                              QTableView, QGridLayout, QHBoxLayout, QVBoxLayout,
                              QMessageBox, QLineEdit, QCheckBox, QComboBox,
                              QFontComboBox, QLabel, QPushButton, QToolTip,
                              QSpinBox, QFileDialog, QStyleFactory  )

from ngl_utils.nfont.converter import NFontConverter
from ngl_utils.nfont.cparser import NFontParser

from ngl_utils.ncodegenerator import NFontCodeGen
from ngl_utils.messages import inform, error, newline

# from ngl_fillbar import NGL_FillBar
# from ngl_button import NGL_Button

# ------------------------------------------------------------------------------
# PixelDelegate
# ------------------------------------------------------------------------------
class PixelDelegate(QAbstractItemDelegate):
    """ docString for PixelDelegate """

    defaultPixelSize = 12

    def __init__(self, parent=None):
        super(PixelDelegate, self).__init__(parent)
        self._pixelSize = PixelDelegate.defaultPixelSize

    def paint(self, painter, option, index):
        size = min(option.rect.width(), option.rect.height()) / 2
        brightness = index.model().data(index, Qt.DisplayRole)

        if brightness:
            brush = QBrush(Qt.black)
        else:
            brush = QBrush(Qt.white)

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(brush)
        painter.drawRect(QRectF(
                            option.rect.x() + option.rect.width()/2 - size,
                            option.rect.y() + option.rect.height()/2 - size,
                            2*size, 2*size))
        painter.restore()

    def sizeHint(self, option, index):
        return QSize(self._pixelSize, self._pixelSize)

    def setPixelSize(self, size):
        self._pixelSize = size

    def pixelSize(self):
        return self._pixelSize

# ------------------------------------------------------------------------------
# ImageModel
# ------------------------------------------------------------------------------
class ImageModel(QAbstractTableModel):

    def __init__(self, parent=None):
        super(ImageModel, self).__init__(parent)

        self.modelImage = 0

    def image(self):
        return self.modelImage

    def setImage(self, image):
        self.beginResetModel()
        self.modelImage = image
        self.endResetModel()

    def getChar(self):
        return self.char

    def setChar(self, char):
        self.char = char

    def rowCount(self, parent=None):
        if self.modelImage:
            return self.modelImage.height()
        return 1

    def columnCount(self, parent=None):
        if self.modelImage:
            return self.modelImage.width()
        return 1

    def data(self, index, role):
        if not index.isValid() or role != Qt.DisplayRole or not self.modelImage:
            return None
        return qGray( self.modelImage.pixel(index.column(), index.row()) )

    def setData(self, index, data, role):
        if not index.isValid() or role != Qt.DisplayRole:
           return
        point = QPoint( index.column(), index.row() )
        self.beginResetModel()
        self.modelImage.setPixel( point, data )
        self.endResetModel()

    def invertData(self, index, role):
        if not index.isValid() or role != Qt.DisplayRole:
           return

        if self.data(index, role):
            dta = 0
        else:
            dta = 1
        self.setData(index, dta, role)

    def headerData(self, section, orientation, role):
        if role == Qt.SizeHintRole:
            return QSize(1, 1)
        return None

# ------------------------------------------------------------------------------
# ImageView
# ------------------------------------------------------------------------------
class ImageView(QTableView):
    """ docstring for ImageView """
    def __init__(self, parent=None):
        super(ImageView, self).__init__(parent)

        self.setShowGrid(True)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.horizontalHeader().setMinimumSectionSize(5)
        self.verticalHeader().setMinimumSectionSize(5)
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMinimumSize( 160, 200 )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            index = self.indexAt( QPoint(event.x(), event.y()) )
            self.model().invertData( index, Qt.DisplayRole )

        super(ImageView, self).mousePressEvent(event)

# ------------------------------------------------------------------------------
# PixelatorWidget
# ------------------------------------------------------------------------------
class PixelatorWidget(QWidget):
    """ docstring for PixelatorWidget """

    # updateCharBitmap = pyqtSignal( str, QImage )

    def __init__(self, parent=None):
        super(PixelatorWidget, self).__init__(parent)

        self.model = ImageModel( self )
        self.view = ImageView( self )

        self.view.setModel( self.model )
        self.viewDelegate = PixelDelegate( self )
        self.view.setItemDelegate( self.viewDelegate )

        mainLayout = QVBoxLayout()
        mainLayout.addWidget( self.view )
        self.setLayout( mainLayout )

    def openImage(self, char, image):
        self.model.setChar( char )
        self.model.setImage( image )
        self.updateView()

    def updateView(self):
        self.view.resizeColumnsToContents()
        self.view.resizeRowsToContents()

# ------------------------------------------------------------------------------
# CharactersMapWidget
# ------------------------------------------------------------------------------
class CharactersMapWidget(QWidget):
    """ docstring for CharactersMapWidget """

    characterSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super(CharactersMapWidget, self).__init__(parent)

        self.displayFont = QFont()
        self.cellSize = 24
        self.columns = 16
        self.lastKey = -1
        self.charSet = None
        self.setMouseTracking(True)

    def setCharSet(self, charSet):
        self.charSet = charSet
        self.update()

    def updateFont(self, fontFamily):
        self.displayFont.setFamily(fontFamily)
        self.update()

    def sizeHint(self):
        if self.charSet != None:
            ln = len(self.charSet)+1
        else:
            ln = 192
        return QSize( self.columns * self.cellSize, (ln / self.columns) * self.cellSize )

    def mouseMoveEvent(self, event):
        position = self.mapFromGlobal(event.globalPos())
        key = (position.y() // self.cellSize) * self.columns + position.x() // self.cellSize

        text = '<p>Character: <span style="font-size: 24pt; font-family: %s">%s</span><p>code: %d' % (
                self.displayFont.family(), self._chr(key), key+32)
        QToolTip.showText(event.globalPos(), text, self)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.lastKey = (event.y() // self.cellSize) * self.columns + event.x() // self.cellSize
            key_ch = self._chr(self.lastKey)
            self.characterSelected.emit(key_ch)
            self.update()
        else:
            super(CharactersMapWidget, self).mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), Qt.white)
        painter.setFont(self.displayFont)

        redrawRect = event.rect()
        beginRow = redrawRect.top() // self.cellSize
        endRow = redrawRect.bottom() // self.cellSize
        beginColumn = redrawRect.left() // self.cellSize
        endColumn = redrawRect.right() // self.cellSize

        # grid
        painter.setPen(Qt.gray)
        for row in range(beginRow, endRow + 1):
            for column in range(beginColumn, endColumn + 1):
                painter.drawRect(column * self.cellSize,
                        row * self.cellSize, self.cellSize,
                        self.cellSize)


        fontMetrics = QFontMetrics(self.displayFont)
        painter.setPen(Qt.black)

        for row in range(beginRow, endRow + 1):
            for column in range(beginColumn, endColumn + 1):

                key = row * self.columns + column
                painter.setClipRect(column * self.cellSize,
                        row * self.cellSize, self.cellSize,
                        self.cellSize)

                if key == self.lastKey:
                    painter.fillRect(column * self.cellSize + 1,
                            row * self.cellSize + 1, self.cellSize,
                            self.cellSize, Qt.red)

                key_ch = self._chr(key)
                painter.drawText(column * self.cellSize + (self.cellSize / 2) - fontMetrics.width(key_ch) / 2,
                        row * self.cellSize + 4 + fontMetrics.ascent(),
                        key_ch)

    def _chr(self, codepoint):
        if self.charSet != None and codepoint < len(self.charSet):
            return self.charSet[ codepoint ]
        else:
            return None

    def reset(self):
        self.lastKey = None
        self.characterSelected.emit( '' )
        self.update()

# ------------------------------------------------------------------------------
# BitmapManipulator
# ------------------------------------------------------------------------------
class BitmapManipulator(object):
    """ docstring for BitmapManipulator """
    def __init__(self, arg):
        super(BitmapManipulator, self).__init__()

    @staticmethod
    def addX(bitmap, direction):
        if direction == 'left':
            x0 = 1
        else:
            x0 = 0

        size = QSize( bitmap.width() + 1, bitmap.height() )
        new_bmp = QImage( size, bitmap.format() )
        new_bmp.fill(0)

        for y in range( bitmap.height() ):
            for x in range( bitmap.width() ):
                data = qGray( bitmap.pixel( x, y ) )
                if data:
                    new_bmp.setPixel( x0 + x, y, 1 )
        return new_bmp

    @staticmethod
    def removeX(bitmap, direction):
        if direction == 'left':
            x0 = 1
        else:
            x0 = 0

        if bitmap.width() > 1:
            return bitmap.copy( x0, 0, bitmap.width() - 1, bitmap.height() )

    @staticmethod
    def addY(bitmap):
        nbmp = QImage( bitmap.width(), bitmap.height() + 1, bitmap.format() )
        nbmp.fill(0)

        for y in range( bitmap.height() ):
            for x in range( bitmap.width() ):
                data = qGray( bitmap.pixel( x, y ) )
                if data:
                    nbmp.setPixel( x, y, 1 )
        return nbmp

    @staticmethod
    def removeY(bitmap):
        return bitmap.copy( 0, 0, bitmap.width(), bitmap.height() - 1 )

    @staticmethod
    def shift(bitmap, direction):
        new_bmp = QImage( bitmap )
        new_bmp.fill(0)

        if direction not in [ 'left', 'right', 'up', 'down' ]:
            error('direction for shift char not valid, exit.' )

        for y in range( bitmap.height() ):
            for x in range( bitmap.width() ):
                if qGray( bitmap.pixel( x, y ) ): col = 1
                else: col = 0

                if direction == 'left' and x > 0:
                    new_bmp.setPixel( x - 1, y, col)
                elif direction == 'right' and x < bitmap.width() - 1:
                    new_bmp.setPixel( x + 1, y, col )
                elif direction == 'up' and y > 0:
                    new_bmp.setPixel( x, y - 1, col)
                elif direction == 'down' and y < bitmap.height() - 1:
                    new_bmp.setPixel( x, y + 1, col )
        return new_bmp

# ------------------------------------------------------------------------------
# NFontEditWidget
# ------------------------------------------------------------------------------
class NFontEditWidget(QWidget):
    """ docstring for NFontEditWidget """

    def __init__(self, arg, parent=None):
        super(NFontEditWidget, self).__init__(parent, Qt.Tool)

        self.arg = arg
        self.settings = QSettings('NeilLab', 'nfont_edit')

        self.filepath = None
        self.ngl_font = None
        self._select_char = None

        # load main ui window
        uifile = pkg_resources.resource_filename( 'ngl_utils.nfont', 'qtres/ngl_font_edit.ui' )
        # uifile = 'untitled.ui'
        self.uic = uic.loadUi(uifile, self)
        # uic_objects = self.__dict__
        # objects = [uic_objects[w] for w in uic_objects.keys() if 'NGL' in uic_objects[w].__class__.__name__]
        # pobj = [{w: uic_objects[w]} for w in uic_objects.keys() if 'NGL' in uic_objects[w].__class__.__name__]
        # print('objects:', pobj)

        # ngl_obj = {}
        # for obj in objects:
        #     print('name : ', obj.__class__.__name__)
        #     if obj.__class__.__name__ == 'NGL_Button':
        #         fill_prop = [w for w in NGL_Button.__dict__.keys() if type(NGL_Button.__dict__[w]) == pyqtProperty]
        #         for prop in fill_prop:
        #             val = getattr(obj, prop)
        #             ngl_obj[prop] = val
        #             print(type(val), prop, val)
        #         print(getattr(obj, 'styleSheet')())

        # print('ngl_obj:', ngl_obj)

        # sys.exit(True)

        # ngl font char set widget
        self.characterWidget = CharactersMapWidget()
        self.uic.scrollArea.setWidget( self.characterWidget )
        self.characterWidget.characterSelected.connect( self.selectCharacter )

        # char pixel map view widget
        self.charPixelView = PixelatorWidget()
        self.uic.pixelViewVLayout.addWidget( self.charPixelView )

        # pixelator pixel size view slots
        self.uic.pixelSizeSpinBox.setValue( PixelDelegate.defaultPixelSize )
        self.uic.pixelSizeSpinBox.valueChanged.connect( self.charPixelView.viewDelegate.setPixelSize )
        self.uic.pixelSizeSpinBox.valueChanged.connect( self.charPixelView.updateView )

        # char bitmap X add/remove
        self.uic.btnAddLeft.clicked.connect( self._charAddRemoveX )
        self.uic.btnRemoveLeft.clicked.connect( self._charAddRemoveX )
        self.uic.btnAddRight.clicked.connect( self._charAddRemoveX )
        self.uic.btnRemoveRight.clicked.connect( self._charAddRemoveX )

        # char bitmap Y add/remove
        self.uic.btnAddHeight.clicked.connect( self._charAddRemoveY )
        self.uic.btnRemoveHeight.clicked.connect( self._charAddRemoveY )

        # char bitmap shift X/Y
        self.uic.btnShiftLeft.clicked.connect( self._charShiftXY )
        self.uic.btnShiftRight.clicked.connect( self._charShiftXY )
        self.uic.btnShiftDown.clicked.connect( self._charShiftXY )
        self.uic.btnShiftUp.clicked.connect( self._charShiftXY )

        # open, save, hide
        self.uic.btnOpenFont.clicked.connect( self.openFile )
        self.uic.btnSaveFont.clicked.connect( self._save )
        self.uic.btnSaveAsFont.clicked.connect( self._saveAs )
        self.uic.btnClose.clicked.connect( self.hide )

        # window modality
        self.setWindowModality(Qt.ApplicationModal)

    def _selectChar(self, char, bitmap):

        if self.ngl_font != None:

            chardict = self.ngl_font.get_chars_dict()

            if char in chardict.keys():

                self._select_char = char
                self.charPixelView.openImage( char, bitmap)

                lblInfoText = "char: '{0}', width: {1}, height: {2} ".format(
                                    char,
                                    chardict[char]['bitmap'].width(),
                                    chardict[char]['bitmap'].height() )
                self.uic.lblCharInfo.setText( lblInfoText )

    def selectCharacter(self, char):
        if char:
            chardict = self.ngl_font.get_chars_dict()
            self._selectChar( char, chardict[ char ][ 'bitmap' ]  )

    @pyqtSlot()
    def _charAddRemoveX(self):
        name = self.sender().objectName()
        selectchar = self.ngl_font.get_chars_dict() [ self._select_char ]

        if name == 'btnAddLeft' or name == 'btnAddRight':

            manipulate = BitmapManipulator.addX
            direction = name[ len('btnAdd'): ].lower()

        elif name == 'btnRemoveLeft' or name == 'btnRemoveRight':

            manipulate = BitmapManipulator.removeX
            direction = name[ len('btnRemove'): ].lower()

        if self.uic.chBoxAllChars.checkState():
            charlist = self.ngl_font.get_chars_list()
        else:
            charlist = [ selectchar ]

        for char in charlist:
            char[ 'bitmap' ] = manipulate( char[ 'bitmap' ], direction )

        self._selectChar( selectchar[ 'char' ], selectchar[ 'bitmap' ] )

    @pyqtSlot()
    def _charAddRemoveY(self):
        name = self.sender().objectName()
        selectchar = self.ngl_font.get_chars_dict() [ self._select_char ]

        if self.uic.chBoxAllChars.checkState():
            charlist = self.ngl_font.get_chars_list()
        else:
            charlist = [ selectchar ]

        if 'add' in name.lower():
            manipulate = BitmapManipulator.addY
        elif 'remove' in name.lower():
            manipulate = BitmapManipulator.removeY

        for ch in charlist:
            ch[ 'bitmap' ] = manipulate( ch[ 'bitmap' ] )

        self._selectChar( selectchar[ 'char' ], selectchar[ 'bitmap' ] )

    @pyqtSlot()
    def _charShiftXY(self):

        name = self.sender().objectName()
        selectchar = self.ngl_font.get_chars_dict() [ self._select_char ]
        direction = name[ len('btnShift'): ].lower()

        if self.uic.chBoxAllChars.checkState():
            charlist = self.ngl_font.get_chars_list()
        else:
            charlist = [ selectchar ]

        for char in charlist:
            char[ 'bitmap' ] = BitmapManipulator.shift( char[ 'bitmap' ], direction )

        self._selectChar( selectchar[ 'char' ], selectchar[ 'bitmap' ] )

    @pyqtSlot()
    def openFile(self):

        last_dir = self.settings.value('open_last_dir', type=str)
        if not last_dir:
            last_dir = './'

        fileName, _ = QFileDialog.getOpenFileName( self,
                                "Open NGL Font source for edit", last_dir,
                                "Source ngl font Files (*.c);;All Files (*)",
                                options = QFileDialog.DontUseNativeDialog )
        if fileName:
            self.setFontFile( fileName )
            self.selectCharacter( self._select_char )
        else:
            error('File name incorect, exit.')

    def setFontFile(self, filepath):

        if filepath:
            self.filepath = filepath
            self.settings.setValue( 'open_last_dir', os.path.dirname(filepath) )

            # parse sourse file
            parser = NFontParser()
            ngl_font = parser.parseFile( filepath )
            self._openNGLFont( ngl_font )

    def _openNGLFont(self, font):

        self.ngl_font = font
        font_charlist = self.ngl_font.get_chars_list()
        charset = ''.join( [ ch['char'] for ch in font_charlist ] )

        self.characterWidget.setCharSet( charset )
        self.setWindowTitle( "Character Map for - '%s'" % font.name )

    def _reGenerateFont(self):
        # regenerate  'code' and 'offset' fo chars
        offset = 0
        for ch in self.ngl_font.get_chars_list():
            ch['code'], _offset = NFontConverter.font_bmpCode(ch['bitmap'])
            ch['offset'] = offset
            offset += _offset

        # generate code for font, return result font
        self.ngl_font.code = NFontCodeGen.font( self.ngl_font )
        return self.ngl_font

    def closeEvent(self, event):
        if self.arg == '__main__':
            sys.exit(True)

    def hideEvent(self, event):
        super(NFontEditWidget, self).hideEvent(event)

        self.ngl_font = None
        self.characterWidget.setCharSet(None)
        self.charPixelView.openImage(None, None)

        if self.arg == '__main__':
            self.close()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.hide()

    @pyqtSlot()
    def _hide(self):
        self.hide()

    @pyqtSlot()
    def _save(self):
        if self.filepath != None:
                self.ngl_font = self._reGenerateFont()
                with open(self.filepath, 'wt') as f:
                    f.write( self.ngl_font.get_code() )
                QMessageBox.information(self, '', 'NGL Font file saved')
        else:
            QMessageBox.critical(self, 'ERROR', 'No opened any font file!' )

    @pyqtSlot()
    def _saveAs(self):
        filepath, status = QFileDialog.getSaveFileName( self,
                'Save NGL font file',
                self.ngl_font.name,
                "C files (*.c)",
                options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog )
        if status:
            self.filepath = filepath + '.c'
            self._save()

# ------------------------------------------------------------------------------
# NFontConverterWidget
# ------------------------------------------------------------------------------
def nfontEditGUIStart():
    app = QApplication(sys.argv)
    ex = NFontEditWidget('__main__')
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    ex.openFile()
    ex.show()
    sys.exit(app.exec_())

# ------------------------------------------------------------------------------
# __main__
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    nfontEditGUIStart()
