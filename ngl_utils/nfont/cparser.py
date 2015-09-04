#!/usr/bin/env python3

from PyQt5.QtGui import QImage
from ngl_utils.nfont.nfont import NGL_Font
from ngl_utils.nfont.converter import NFontConverter

# ------------------------------------------------------------------------------
# NFontParse_cFile
# ------------------------------------------------------------------------------
class NFontParser(object):
    """
        Parse font sourse C file (*.c), return NGL_Font type object
    """
    def __init__(self):
        super(NFontParser, self).__init__()
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

        for y in range(pchar['height']):
            byte_width = (pchar['width'] + 7) // 8
            for x in range( byte_width ):

                byte = pchar['data'][ y * byte_width + x ]
                mask = 0x80

                for i in range( pchar['width'] ):
                    if byte & mask != 0:
                        qimage.setPixel( (x*8)+i, y, 1 )
                    mask = mask >> 1

        # qimage.save('.\\img\\__%s.bmp' % pchar['char'])
        return qimage
    
