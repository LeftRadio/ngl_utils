#!/usr/bin/env python3

from PyQt5.QtCore import Qt, QSize, QRect, QPoint
from PyQt5.QtGui import QFont, QFontMetrics, QImage, QPainter, QPen
from PyQt5.QtWidgets import QApplication
from ngl_utils.ncodegenerator import NFontCodeGen, NBitmapCodeGen

# ------------------------------------------------------------------------------
# NColor
# ------------------------------------------------------------------------------
class NColor(object):
    """docstring for NColor"""
    def __init__(self, arg):
        super(NColor, self).__init__()
        self.arg = arg

    @staticmethod
    def fromARGB(argb_data):
        """ convert 8888_ARGB to 565_RGB """
        R = ((argb_data >> 19) & 0x1F) << 11
        G = ((argb_data >> 10) & 0x3F) << 6
        B = argb_data & 0x1F
        return ( R | G | B )

    @staticmethod
    def fromRGB(rgb):
        """ convert 8888_ARGB to 565_RGB """
        R = (rgb[0] & 0x1F) << 11
        G = (rgb[1] & 0x3F) << 6
        B = rgb[2] & 0x1F
        return ( R | G | B )
        
# ------------------------------------------------------------------------------
# NFontConverter
# ------------------------------------------------------------------------------
class NFontConverter(object):
    """docstring for NFontConverter"""    
    @staticmethod
    def convertParsedQFont(chars_sets, font):
        name = font['name']
        qfont = QFont( font['family'], int(font['pointsize']) )
        qfont.setBold( font['bold'] )

        # if no QApp program crash in QFontMetrics( font ).boundingRect( char ) ???
        app = QApplication([])

        # convert
        return NFontConverter.convertQFont( chars_sets, name, qfont )

    @staticmethod
    def convertQFont(chars_sets, name, font):

        NFontConverter.font = font
        # font.setHintingPreference( QFont.PreferNoHinting )
        # font.setStyleHint( QFont.SansSerif )
        font.setStyleStrategy( QFont.NoAntialias | QFont.PreferQuality )

        # create NGL_Font and generate all chars code
        nfont = NGL_Font(name, font)
        offset = 0
        for char in chars_sets:
            ch_bmp = NFontConverter.font_charBmp( font, char )
            ch_code, ch_offset = NFontConverter.font_bmpCode(ch_bmp)

            nfont.add_char( char, ch_code, offset, ch_bmp )
            offset += ch_offset

        # generate code text out
        nfont.code = NFontCodeGen.font( nfont )

        return nfont

    @staticmethod
    def font_charBmp(font, char):
        metric = QFontMetrics( font ).boundingRect( char )
        char_rect = QRect( 0, 0, metric.width(), metric.height() )
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
                # print( 'bR:%d, px:%d' % (bitsRead, bmp.pixel(col, row) & 0x00FFFFFF) )
                if bmp.pixel(col, row) & 0x00FFFFFF:
                    val |= (1 << (7 - bitsRead))

                bitsRead += 1

                # have we filled a page?
                if bitsRead == 8 or col == bmp.width() - 1:
                    # add byte to page array
                    row_code.append(val)
                    # zero out current value and bits read
                    val = bitsRead = 0

            # print( 'bits %d, val %d' % (bitsRead, val) )
            bitmap_code.append( row_code )

        return bitmap_code, len(row_code) * len(bitmap_code)

# ------------------------------------------------------------------------------
# NFontParse_cFile
# ------------------------------------------------------------------------------
class NFontParse_cFile(object):
    """
        Parse font sourse C file (*.c), return NGL_Font type object
    """
    def __init__(self):
        super(NFontParse_cFile, self).__init__()
        self._code_text = None
        self._ngl_font = None

    def parseFile(self, fontfile):
        if fontfile:
            with open(fontfile, 'r') as f:
                code = f.read()

            _description = self._getFontDescription( code )
            _name = self._parseName( _description ).replace('Info', '')
            _start_char, _end_char = self._parseStartEndChars( _description )
            _pchars = self._parseChars( code )

            # crate NGL Font
            ngl_font = NGL_Font( _name )

            # add chars bitmaps to font
            offset = 0
            for pch in _pchars:
                _, ch_offset = NFontConverter.font_bmpCode( pch['bitmap'] )
                ngl_font.add_char( pch['char'], None, offset, pch['bitmap'] )
                offset += ch_offset

            return ngl_font

    def _getFontDescription(self, codetext):
        start = codetext.find('// Font information')
        return codetext[ start: ]

    def _parseName(self, codetext):
        start = codetext.find('NGL_Font') + len('NGL_Font') + 1
        end = codetext.rfind('= {') - 1
        return codetext[start:end]

    def _parseStartEndChars(self, codetext):
        ptrn = '    \''

        start = codetext.find(ptrn) + len(ptrn)
        startChar = codetext[ start:start+1 ]

        start = codetext.rfind(ptrn) + len(ptrn)
        endChar = codetext[ start:start+1 ]

        return (start, endChar)

    def _parseChars(self, codeText):
        start = codeText.find( 'Character bitmaps' )
        end = codeText.find( 'Character descriptors' )
        code = codeText[ start:end ]

        colums = code.split('\n')
        chars = []

        # parse chars info, data and construct QImage
        for i in range( len(colums) ):
            pchar = self._parseCharInfo( colums[i] )
            if pchar != None:
                pchar['data'] = self._parseCharData(colums, i+1, i+1+pchar['height'])
                pchar['bitmap'] = self._constructQImage( pchar )

                chars.append( pchar )
                i += pchar['height']

        return chars

    def _parseCharInfo(self, codetext):
        char_info = { 'char': None, 'width': 0, 'height': 0 }

        start = codetext.find(' \'') + 2
        end = codetext.rfind('\' ')

        if start > 0 and end > 0:
            char_info['char'] = codetext[ start:end ]

            i = codetext.find('l@')
            if i >= 0:
                i1 = codetext.find(' \'')
                height = codetext[ i+2:i1 ].replace(' ', '')
                char_info['height'] = int( height )

            i = codetext.find(' (')
            i1= codetext.find('bits wide')
            if i > 0 and i1 > 0:
                width = codetext[ i+2:i1-1 ]
                char_info['width'] = int( width )

            return char_info
        else:
            return None

    def _parseCharData(self, colums, starIndex, endIndex):
        data = []
        for j in range( starIndex, endIndex ):
            for b in colums[j].split(','):
                if '0x' in b:
                    data.append( int(b.replace('\t', ''), 16) )
        return data

    def _constructQImage(self, pchar):
        qimage = QImage( pchar['width'], pchar['height'], QImage.Format_Mono )
        qimage.fill(0)

        for col in range(pchar['height']):
            byte_width = (pchar['width'] + 7) // 8
            for row in range( byte_width ):

                byte = pchar['data'][ col * byte_width + row ]
                mask = 0x80

                for i in range( pchar['width'] ):
                    if byte & mask != 0:
                        qimage.setPixel( QPoint((row*8)+i, col), 1 )
                    mask = mask >> 1

        # qimage.save('.\\img\\__%s.bmp' % pchar['char'])
        return qimage

# ------------------------------------------------------------------------------
# NGL_Font
# ------------------------------------------------------------------------------
class NGL_Font(object):

    def __init__(self, name, font = None):
        self.name = name
        self.sysFont = font
        self.nchars = {}
        self.code = ''

    def add_char(self, ch, char_code, offset, bitmap):
        """
        Add new char to font chars list
        """
        self.nchars[ch] = { 'char': ch, 'code': char_code, 'offset': offset, 'bitmap': bitmap }

    def get_char(self, char):
        if char in self.nchars:
            return self.nchars[ char ]

    def get_chars_dict(self):
        return self.nchars

    def get_chars_list(self):
        return [  self.nchars[c] for c in sorted(self.nchars) ]

    def clear_char_set(self):
        self.nchars = {}

    def get_code(self):
        return self._code
    def set_code(self, code):
        self._code = code
        
    code = property( get_code, set_code )

    def code_size_calc(self):
        """
        Calc estimate code size for font
        """
        size = 0
        for char in self.get_chars_list():
            size += len( char['code'] ) * len( char['code'][0] ) + 3
        return size + 40

    @staticmethod
    def formatName(family, pointSize, bold):
        if bold: b = 'bold'
        else: b = 'normal'

        name = '%s_%s_%s' % ( family, pointSize, b )
        return name.replace(' ', '_').lower()


    def getSystemFont(self):
        return self.sysFont

# ------------------------------------------------------------------------------
# NBitmapsConverter
# ------------------------------------------------------------------------------
class NBitmapsConverter(object):
    """docstring for NBitmapsConverter"""    
    @staticmethod
    def convertParsedBitmap(bitmap, nformat, compress):        
        image = QImage( bitmap['path'] )
        image = image.scaled( QSize( int(bitmap['width']),
                                     int(bitmap['height']) ),
                              Qt.IgnoreAspectRatio,
                              Qt.SmoothTransformation )

        return NBitmapsConverter.convertQImage( image, bitmap['name'], nformat, compress )

    @staticmethod
    def convertQImage(image, name, nformat, compress):
        ngl_bitmap = NGL_Bitmap( name, image.width(), image.height() )

        for x in range( image.width() ):
            for y in range( image.height() ):
                argb_pixel = image.pixel( x, y )
                data = NColor.fromARGB( argb_pixel )
                ngl_bitmap.data.append( data )

        if compress != 'compressed_None':
            ngl_bitmap.data = NBitmapsConverter.compressData( ngl_bitmap.data )
            ngl_bitmap.compressed = compress.replace( 'compressed_', '' )        
        
        ngl_bitmap.code = NBitmapCodeGen.bitmap( ngl_bitmap )
        
        return ngl_bitmap

    @staticmethod
    def compressData(bitmap_data):
        """ compress data RLE or JPG algs """
        pass

# ------------------------------------------------------------------------------
# NGL_Font
# ------------------------------------------------------------------------------
class NGL_Bitmap(object):

    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height
        self.compressed = 'None'
        self.color_bit = 16
        self.data_word_size = 16
        self.data_len_bytes = 0
        self.datatype = 'uint16_t'
        self.data = []
        self.code = ''
    
    def get_name(self):
        return self._name
    def set_name(self, name):
        self._name = name

    def get_width(self):
        return self._width
    def set_width(self, width):
        self._width = width

    def get_height(self):
        return self._height
    def set_height(self, height):
        self._height = height

    def get_compressed(self):
        return self._compressed.replace('None', '0').replace('RLE', '1').replace('JPG', '2')
    def set_compressed(self, compressed):
        self._compressed = compressed

    def get_color_bit(self):
        return self._color_bit
    def set_color_bit(self, color_bit):
        self._color_bit = color_bit

    def get_data_word_size(self):
        return self._data_word_size
    def set_data_word_size(self, data_word_size):
        self._data_word_size = data_word_size

    def get_data_len_bytes(self):
        return self._data_len_bytes
    def set_data_len_bytes(self, data_len_bytes):
        self._data_len_bytes = data_len_bytes

    def get_datatype(self):
        return self._datatype
    def set_datatype(self, datatype):
        self._datatype = datatype    
    
    def get_data(self):        
        return self._data        
    def set_data(self, data):
        self._data = data

    def get_code(self):
        return self._code
    def set_code(self, code):
        self._code = code

    name = property( get_name, set_name )
    width = property( get_width, set_width )
    height = property( get_height, set_height )
    compressed = property( get_compressed, set_compressed )    
    color_bit = property( get_color_bit, set_color_bit )
    data_word_size = property( get_data_word_size, set_data_word_size )
    data_len_bytes = property( get_data_len_bytes, set_data_len_bytes )
    datatype = property( get_datatype, set_datatype )
    data = property( get_data, set_data )
    code = property( get_code, set_code )


    def formatedData(self):        
        crop = 0
        tstr = '\t'
        data = self.data
        format_data = []
        
        for word in data:
            tstr += '0x%04x, ' % word
            crop += 1            
            if crop >= 20:                
                format_data.append( tstr + '\n' )
                tstr = '\t'
                crop = 0

        return ''.join( format_data )

    def codeSize(self):
        """ Calc estimate MCU code size """
        return 0
