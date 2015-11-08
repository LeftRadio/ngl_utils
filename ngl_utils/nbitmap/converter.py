#!/usr/bin/env python3

import os
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QImage, QColor, QPainter

from ngl_utils.ncodegenerator import NBitmapCodeGen
from ngl_utils.nbitmap.nbitmap import NGL_Bitmap
from ngl_utils.nplugins.widgets.ngl_colors import NGL_Colors
from ngl_utils.rle import rlem_encode, rlem_decode


class NBitmapsConverter(object):
    """docstring for NBitmapsConverter"""

    @staticmethod
    def convertQImage(image, name, nformat, compress, backcolor):
        compressType, _ = compress

        nbmp = NGL_Bitmap(name, image.width(), image.height(), compressType)

        # convert/compress data
        nbmp.data, nbmp.compressed = NBitmapsConverter.compressData(image, compress, nformat, name, backcolor)

        # code len in words and bytes
        nbmp.data_len_in_words = len(nbmp.data)

        if nformat == 'format8' or nbmp.compressed == 'JPG':
            nbmp.data_len_in_bytes = nbmp.data_len_in_words
            nbmp.data_word_size = 8
            nbmp.datatype = 'uint8_t'
        elif nformat == 'format16':
            nbmp.data_len_in_bytes = nbmp.data_len_in_words * 2
            nbmp.data_word_size = 16
            nbmp.datatype = 'uint16_t'

        # generate data code
        nbmp.code = NBitmapCodeGen.bitmap(nbmp)

        return nbmp

    @staticmethod
    def compressData(image, compress, nformat, name, backcolor):
        """ compress data NONE, RLE, JPG, AUTO(minimum size) """
        compressType, compressQuality = compress
        data = []

        if compressType == 'AUTO':
            dataNone, nk = NBitmapsConverter.compressData(image, ('None', None), nformat, name, backcolor)
            dataRLE, rk = NBitmapsConverter.compressData(image, ('RLE', None), nformat, name, backcolor)
            dataJPG, jk = NBitmapsConverter.compressData(image, ('JPG', compressQuality), nformat, name, backcolor)

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
            r, g, b = NGL_Colors.getRGB(backcolor)
            Qbackcolor = QColor(r, g, b)

            # 1px image and painter for images with alfa
            img = QImage(1,1, QImage.Format_ARGB32)
            painter = QPainter()

            for y in range(image.height()-1, -1, -1):
                for x in range(image.width()):
                    argb_pixel = image.pixel(x, y)
                    alfa = (argb_pixel >> 24)

                    alfa = (argb_pixel >> 24) & 0xFF
                    if alfa == 0xFF:
                         pixelData = NGL_Colors.fromARGB(argb_pixel)
                    else:
                        color = QColor(argb_pixel)
                        color.setAlpha(alfa)
                        pixelData = NBitmapsConverter.mixColors(img, Qbackcolor, color, painter)

                    data.append(pixelData)

            if compressType == 'RLE':
                data = rlem_encode(data)

        return (data, compressType)

    @staticmethod
    def mixColors(img, backcolor, color, painter):
        img.setPixel(0, 0, backcolor.rgb())

        painter.begin(img)
        painter.setPen(color)
        painter.drawPoint(0, 0)
        painter.end()

        return NGL_Colors.fromARGB(img.pixel(0, 0))