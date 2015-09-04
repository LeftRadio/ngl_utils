#!/usr/bin/env python3

import os
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QImage

from ngl_utils.ncodegenerator import NBitmapCodeGen
from ngl_utils.messages import inform, error
from ngl_utils.nbitmap.nbitmap import NGL_Bitmap
from ngl_utils.rle import rlem_encode

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
        ngl_bitmap = NGL_Bitmap( name, image.width(), image.height(), compress )
        
        for x in range( image.width() ):
            for y in range( image.height() ):
                argb_pixel = image.pixel( x, y )
                data = NColor.fromARGB( argb_pixel )
                ngl_bitmap.data.append( data )

        # comress data if needed
        ngl_bitmap.data = NBitmapsConverter.compressData( image, ngl_bitmap, compress )                  
        
        # code len in words and bytes
        ngl_bitmap.data_len_in_words = len( ngl_bitmap.data )
        ngl_bitmap.data_len_in_bytes = ngl_bitmap.data_len_in_words
        if True in [ True for x in ngl_bitmap.data if x > 0xFF ]:
            ngl_bitmap.data_len_in_bytes *= 2
        
        # generate data code
        ngl_bitmap.code = NBitmapCodeGen.bitmap( ngl_bitmap )
        
        return ngl_bitmap

    @staticmethod
    def compressData(image, bitmap, compress):
        """ compress data RLE or convert to JPG """
        if compress == 'RLE':
            data = rlem_encode( bitmap.data )
            return data
        
        elif compress == 'JPG':
            #  crete temp path and save image as jpg
            path = './tmp_cnv.jpg'
            image.save( path )

            # open file, read data
            with open(path, 'rb') as f:
                data = [ byte for byte in f.read() ]            
            
            # delete temp file
            os.remove( path )

            bitmap.data_word_size = 8
            bitmap.color_bit = 0
            return data        
        
        else:
            return bitmap.data