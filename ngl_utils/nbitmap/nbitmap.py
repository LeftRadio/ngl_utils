#!/usr/bin/env python3

# ------------------------------------------------------------------------------
# NGL_Bitmap
# ------------------------------------------------------------------------------
class NGL_Bitmap(object):

    def __init__(self, name, width, height, compress):
        self.name = name
        self.width = width
        self.height = height
        self.compressed = compress
        self.color_bit = 16
        self.data_word_size = 16
        self.data_len_in_bytes = 0
        self.datatype = 'uint16_t'
        self.data = []
        self.code = ''
        self.recepients = {}

    def get_name(self):
        return self._name.replace(' ', '_')
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
        return self._compressed
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
            tstr += '0x%x, ' % word
            crop += 1
            if crop >= self.width:
                format_data.append( tstr + '\n' )
                tstr = '\t'
                crop = 0

        if crop != 0:
            format_data.append( tstr + '\n' )

        return ''.join( format_data )

    def codeSize(self):
        """ Calc estimate MCU code size """
        return 0

