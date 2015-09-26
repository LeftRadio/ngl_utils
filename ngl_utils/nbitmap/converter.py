#!/usr/bin/env python3

import os
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QImage

from ngl_utils.ncodegenerator import NBitmapCodeGen
from ngl_utils.nbitmap.nbitmap import NGL_Bitmap
from ngl_utils.rle import rlem_encode


class NColor(object):
    """docstring for NColor"""

    @staticmethod
    def fromARGB(argb_data):
        """ convert 8888_ARGB to 565_RGB """
        R = ((argb_data >> 19) & 0x1F) << 11
        G = ((argb_data >> 10) & 0x3F) << 6
        B = argb_data & 0x1F
        return (R | G | B)

    @staticmethod
    def fromRGB(rgb):
        """ convert 8888_ARGB to 565_RGB """
        R = (rgb[0] & 0x1F) << 11
        G = (rgb[1] & 0x3F) << 6
        B = rgb[2] & 0x1F
        return (R | G | B)

    @staticmethod
    def fromQColor(qcolor):
        rgba = qcolor.rgba()
        return NColor.fromARGB(rgba >> 8)



class NBitmapsConverter(object):
    """docstring for NBitmapsConverter"""

    @staticmethod
    def convertParsedBitmap(bitmap, nformat, compress):
        image = QImage(bitmap['path'])
        # image = image.scaled(QSize(int(bitmap['width']),
        #                            int(bitmap['height'])),
        #                      Qt.IgnoreAspectRatio,
        #                      Qt.SmoothTransformation)

        return NBitmapsConverter.convertQImage(image,
                                               bitmap['name'],
                                               nformat,
                                               compress)

    @staticmethod
    def convertQImage(image, name, nformat, compress):
        compressType, _ = compress

        ngl_bitmap = NGL_Bitmap(name,
                                image.width(),
                                image.height(),
                                compressType)
        # conbert/comress data
        ngl_bitmap.data, ngl_bitmap.compressed = NBitmapsConverter.compressData(image, compress)

        # code len in words and bytes
        ngl_bitmap.data_len_in_words = len(ngl_bitmap.data)
        ngl_bitmap.data_len_in_bytes = ngl_bitmap.data_len_in_words

        if True in [True for x in ngl_bitmap.data if x > 0xFF]:
            ngl_bitmap.data_len_in_bytes *= 2
            ngl_bitmap.data_word_size = 16
        else:
            ngl_bitmap.data_word_size = 8

        # generate data code
        ngl_bitmap.code = NBitmapCodeGen.bitmap(ngl_bitmap)

        return ngl_bitmap

    @staticmethod
    def compressData(image, compress):
        """ compress data None/RLE/JPG/AutoSize """
        compressType, compressQuality = compress

        if compressType == 'Auto':
            dataNone, nk = NBitmapsConverter.compressData(image, ('None', None))
            dataRLE, rk = NBitmapsConverter.compressData(image, ('RLE', None))
            dataJPG, jk = NBitmapsConverter.compressData(image, ('JPG', compressQuality))

            min_len = 2**32
            for key, dt in [(nk, dataNone), (rk, dataRLE), (jk, dataJPG)]:
                if len(dt) < min_len:
                    min_len = len(dt)
                    data = dt
                    compressType = key

        elif compressType == 'JPG':
            #  crete temp path and save image as jpg
            path = './tmp.jpg'

            image.save(path, 'JPG', compressQuality)

            # open file, read data
            with open(path, 'rb') as f:
                data = [byte for byte in f.read()]

            # delete temp file
            os.remove(path)

        else:
            data = []
            for x in range(image.width()):
                for y in range(image.height()):
                    argb_pixel = image.pixel(x, y)
                    pixelData = NColor.fromARGB(argb_pixel)
                    data.append(pixelData)

            if compressType == 'RLE':
                data = rlem_encode(data)

        return (data, compressType)
