
import sys
import time
import os
import pkg_resources

from PyQt5 import uic
from PyQt5.QtCore import Qt, QSettings, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont 
from PyQt5.QtWidgets import ( QWidget, QDesktopWidget,
        QApplication, QStyleFactory, QFontDialog, QFileDialog,
        QMessageBox )

from ngl_utils.nfont.nfont import NGL_Font
from ngl_utils.nfont.converter import NFontConverter

from ngl_utils.nfont.editwidget import NFontEditWidget
from ngl_utils.nfont.codeview import CodeView_Window
from ngl_utils.nfont.consolewidget import ConsoleWidget
import ngl_utils.nfont.nfonts_rc

# ------------------------------------------------------------------------------
# NFontConverterWidget
# ------------------------------------------------------------------------------
class NFontConverterWidget(QWidget):

    data_ready_signal = pyqtSignal(NGL_Font)

    def __init__(self, name, dataSlot=None, parent=None):
        """ Constructor """
        super(NFontConverterWidget, self).__init__(parent)

        self.settings = QSettings('NeilLab', 'NGL Font')

        # load main ui window 
        uifile = pkg_resources.resource_filename( 'ngl_utils.nfont', 'qtres/ngl_font.ui' )
        self.uic = uic.loadUi(uifile, self)

        self.nfont_view = CodeView_Window(self)
        self.sysFont_dialog = QFontDialog(self)

        # def sysfont and font name
        self.font = QFont('Times', 8)
        self.NGL_Font = None
        fname = NGL_Font.formatName( self.font.family(),
                                         self.font.pointSize(),
                                         self.font.bold() )
        self.lineEdit_fontName.setText( fname )

        # generates chars set for combobox
        self._charstersRangesInit()

        # font edit widget
        self.edit_view = NFontEditWidget('__util__')

        # connect signals / slots
        self.tBtn_Font.clicked.connect( self._selectFont_slot )
        self.tBtn_AddChars.clicked.connect( self._add_chars_slot )
        self.tBtn_Convert.clicked.connect( self._convert_slot )
        self.tBtn_Save.clicked.connect( self._saveAs_slot )
        self.tBtn_ViewOut.clicked.connect( self._view_out_slot )
        self.tBtn_Edit.clicked.connect( self._edit_font_slot )

        if name == '__main__':
            self.tBtn_Close.setText('Close')
            self.tBtn_Close.clicked.connect( self._close_slot )
        else:
            self.tBtn_Close.setText('Add')
            self.tBtn_Close.clicked.connect( self._ok_slot )
        self.connectDataReadySlot( dataSlot )

        # set window to center and show
        self.frameGeometry().moveCenter(
                    QDesktopWidget().availableGeometry().center() )

    def connectDataReadySlot(self, dataSlot):
        """ dataSlot is Qt slot for signaling converting ready state """
        if dataSlot:
            self.data_ready_signal.connect( dataSlot )

    def _charstersRangesInit(self):
        """ Init charsters sets ranges """
        
        cm_chr = self.cmBox_chars_sets

        cm_chr.insertItem( 0, 'Full eng', ''.join([ chr(x) for x in range(ord(' '), ord('~')) ]) )
        cm_chr.insertItem( 1, 'Upper eng (A-Z)', ''.join([ chr(x) for x in range(ord('A'), ord('Z')) ]) )
        cm_chr.insertItem( 2, 'Lower eng (a-z)', ''.join([ chr(x) for x in range(ord('a'), ord('z')) ]) )

        cm_chr.insertItem( 3, 'Full rus', ''.join([ chr(x) for x in range(ord(u'А'), ord(u'я')) ]) )
        cm_chr.insertItem( 4, 'Upper rus (А-Я)', ''.join([ chr(x) for x in range(ord(u'А'), ord(u'Я')) ]) )
        cm_chr.insertItem( 5, 'Lower rus (а-я)', ''.join([ chr(x) for x in range(ord('а'), ord('я')) ]) )

        cm_chr.insertItem( 6, 'Full eng+rus', cm_chr.itemData(0) + cm_chr.itemData(3) )
        cm_chr.insertItem( 7, 'Numbers (0-9)', '0123456789' )

    @pyqtSlot()
    def _selectFont_slot(self):
        """
        Select Font slot
        """
        font, font_res = self.sysFont_dialog.getFont(self.font, None, 'Select Font');
        if font_res:
            name = NGL_Font.formatName( font.family(), font.pointSize(), font.bold() )
            self.lineEdit_fontName.setText( name )
            self.font = font

    @pyqtSlot()
    def _add_chars_slot(self):
        """
        Add charsers sets to textBrowser
        """
        self.txtBrowser_chars.clear()
        chars_sets = self.cmBox_chars_sets.currentData()
        self.txtBrowser_chars.insertPlainText( chars_sets )

    @pyqtSlot()
    def _convert_slot(self):
        """
        Start converting slot
        """
        chars_sets = str(self.txtBrowser_chars.toPlainText())

        if chars_sets:
            gtime = time.time()

            # converting to ngl font
            name = self.lineEdit_fontName.text()
            self.NGL_Font = NFontConverter.convertQFont( chars_sets, name, self.font )
            ch_list = self.NGL_Font.get_chars_list()
            
            gtime = time.time() - gtime
            self.lbl_gen_time.setText( 'converted at: %.2f sec  |  estimate code size: ~%0.3fk' % (
                    gtime,
                    self.NGL_Font.code_size_calc() / 1000 ) )
            self.lbl_gen_time.update()

        else:
            QMessageBox.critical(self, 'ERROR', """ Nothing to convert!
                Add singles char or characters set to textbox first""" )

    @pyqtSlot()
    def _view_out_slot(self, nfont=None):
        """ View converting out code """
        if nfont == None:
            self.nfont_view.view( self.NGL_Font )
        else:
            self.nfont_view.view( nfont )

    @pyqtSlot()
    def _edit_font_slot(self):
        odir = self.settings.value('open_last_dir', type=str)
        if not odir:
            odir = './'

        fileName, _ = QFileDialog.getOpenFileName(self,
                "Open NGL Font source for edit", odir,
                "Source ngl font Files (*.c);;All Files (*)",
                options = QFileDialog.DontUseNativeDialog)

        if fileName:
            self.settings.setValue( 'open_last_dir', os.path.dirname(fileName) )
            
            # set parsed ngl font and show edit widget
            self.edit_view.setFontFile( fileName )
            self.edit_view.show()

    def _save(self, filepath, font):
        with open( filepath, 'w' ) as f:
                f.write( font.get_code().replace('\r\n', '\n') )

    @pyqtSlot()
    def _saveAs_slot(self):
        """
        Save out to file
        """
        if self.NGL_Font:
            file_name, sts = QFileDialog.getSaveFileName( self,
                    "QFileDialog.getSaveFileName()",
                    self.NGL_Font.name,
                    "C files (*.c)",
                    options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog )
            if sts:
                self._save( file_name + '.c', self.NGL_Font )

    @pyqtSlot()
    def _ok_slot(self):
        if self.NGL_Font:
            self.data_ready_signal.emit( self.NGL_Font )
        else:
            QMessageBox.critical(self, 'ERROR', 'Font not convert!')

    @pyqtSlot()
    def _close_slot(self):
        self.close()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self._close_slot()

# ------------------------------------------------------------------------------
# NFontConverterWidget
# ------------------------------------------------------------------------------
def nfontConverterGUIStart():    
    app = QApplication(sys.argv)
    ex = NFontConverterWidget(__name__)
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    ex.show()
    sys.exit(app.exec_())

# ------------------------------------------------------------------------------
# __main__
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    nfontConverterGUIStart()