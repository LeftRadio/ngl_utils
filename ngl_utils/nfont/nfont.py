

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