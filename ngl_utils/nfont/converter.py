#!/usr/bin/env python3

import sys
import time
import os

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QFont, QFontMetrics, QImage, QPainter, QPen
from PyQt5.QtWidgets import (QWidget, QDesktopWidget,
        QApplication, QStyleFactory)

from ngl_utils.nfont.nfont import NGL_Font
from ngl_utils.ncodegenerator import NFontCodeGen

# ------------------------------------------------------------------------------
# NFontConverter
# ------------------------------------------------------------------------------
class NFontConverter(object):
    """ static converter from QFont or font desc dict,
        example 0:
        chars_to_convert = 'ABCD0123456789'
        font = { 'name': 'tahoma_8_bold',
                 'family': 'Tahoma',
                 'pointsize': '8',
                 'bold': 'true' }
        ngl_font = NFontConverter.convertParsedQFont( chars_to_convert, font )

        example 1:
        qfont = QFont( 'Tahoma', 8 )
        qfont.setBold( True )
        chars_to_convert = 'ABCD0123456789'

        ngl_font = NFontConverter.convertQFont( chars_to_convert, qfont )

    """
    @staticmethod
    def convertParsedQFont(chars_sets, font):
        name = font['name']
        qfont = QFont( font['family'], int(font['pointsize']) )
        qfont.setBold( font['bold'] )

        # convert and return
        return NFontConverter.convertQFont( chars_sets, name, qfont )

    @staticmethod
    def convertQFont(chars_sets, name, font):

        NFontConverter.font = font
        # font.setHintingPreference( QFont.PreferNoHinting )
        # font.setStyleHint( QFont.SansSerif )
        font.setStyleStrategy(QFont.NoAntialias | QFont.PreferQuality)

        # create NGL_Font and generate all chars code
        nfont = NGL_Font(name, font)
        offset = 0
        for char in chars_sets:
            ch_bmp = NFontConverter.font_charBmp(font, char)
            ch_code, ch_offset = NFontConverter.font_bmpCode(ch_bmp)

            nfont.add_char(char, ch_code, offset, ch_bmp)
            offset += ch_offset

        # generate code text out
        nfont.code = NFontCodeGen.font(nfont)

        return nfont

    @staticmethod
    def font_charBmp(font, char):
        metric = QFontMetrics( font ).boundingRect( char )
        char_rect = QRect( 0, 0, metric.width()+1, metric.height() )
        chr_img = QImage( char_rect.width()+1, char_rect.height(), QImage.Format_Mono )
        chr_img.fill(0)

        # set img painter and draw char to bmp
        painter = QPainter( chr_img )
        painter.setPen( QPen(Qt.white) )
        painter.setFont( font )
        painter.drawText( char_rect, Qt.AlignJustify, char )
        painter.end()
        del(painter)

        # crop left / right
        x0 = 0
        x1 = char_rect.width()
        while x0 < x1 - 1:
            data_col = 0
            for col in range( char_rect.height() ):
                data_col += chr_img.pixel(x0, col) & 0x00FFFFFF
            if not data_col:
                x0 += 1
            else: break
        char_rect.setX(x0)

        while x1 > x0 + 1:
            x1 -= 1
            data_col = 0
            for col in range( char_rect.height() ):
                data_col += chr_img.pixel(x1, col) & 0x00FFFFFF
            if not data_col:
                char_rect.setWidth(x1 - x0)
            else: break

        # crop bottom
        y1 = char_rect.height()
        while y1 > 1:
            y1 -= 1
            data_row = 0
            for row in range( char_rect.width() ):
                data_row += chr_img.pixel(row, y1) & 0x00FFFFFF
            if not data_row:
                char_rect.setHeight(y1)
            else: break

        chr_img = chr_img.copy( char_rect )
        # chr_img.save( '.\\img\\0%s.bmp' % char, 'bmp' )
        return chr_img

    @staticmethod
    def font_bmpCode(bmp):
        bitmap_code = []

        # for each row
        for row in range( bmp.height() ):
            row_code = []

            # current byte value
            val = 0
            bitsRead = 0

            # for each column
            for col in range( bmp.width() ):

                # if pixel not 0 set the appropriate bit in the page                
                if bmp.pixel(col, row) & 0x00FFFFFF:
                    val |= (1 << (7 - bitsRead))

                bitsRead += 1

                # have we filled a page?
                if bitsRead == 8 or col == bmp.width() - 1:
                    # add byte to page array
                    row_code.append(val)                    
                    # zero out current value and bits read
                    val = bitsRead = 0
            # append row code byte or code bytes list if char width not fit to one byte - 8 bit
            bitmap_code.append(row_code)

        # return bitmap raw code in 0/1 format bytes, also return full char len in bytes
        return bitmap_code, len(bitmap_code) * ((bmp.width() + 8) // 8)




