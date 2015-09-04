#!/usr/bin/env python3

import sys
import glob
import os
import xml.etree.ElementTree as ET
from ngl_utils.nfont.nfont import NGL_Font
from ngl_utils.nbitmap.converter import NColor

# ------------------------------------------------------------------------------
# simple parser for Qt ui files
# ------------------------------------------------------------------------------
class UIParser(object):
    """ docstring for UIParser """
    def __init__(self, uifile):
        super(UIParser, self).__init__()
        self.uifile = uifile
    
    def set_uifile(self, uifile):
        self._uifile = uifile
    def get_uifile(self):
        return self._uifile

    property = (set_uifile, get_uifile)


    def uiVersion(self):
        try:
            root = self.getroot(self.uifile)
            ver = str( root.attrib['version'] )
        except:
            ver = 'undefined... :( '
        return ver

    def getroot(self, xmlfile):
        """ get root for xml file """
        return ET.parse( xmlfile ).getroot()

    def parse(self):
        """"""                
        # get page and objects    
        page = self.getroot( self.uifile ).find('widget')
        objects = [ obj for obj in page.findall('widget') ]

        # parse ngl page
        self.parsed_page = self._parsePage( page, ['geometry', 'styleSheet'] )

        # parse QLines
        properties = [ 'geometry', 'orientation', 'styleSheet']
        self.parsed_page['lines'] = self._parseObjects( objects, 'Line', properties )
        
        # parse QLabels
        properties = ['geometry', 'orientation', 'styleSheet', 'font', 'text']
        self.parsed_page['labels'] = self._parseObjects( objects, 'QLabel', properties )
        
        # parse QtoolButtons
        properties = ['geometry', 'styleSheet', 'font', 'icon', 'iconSize']
        self.parsed_page['buttons'] = self._parseObjects( objects, 'QToolButton', properties )
        
        # collect all fonts and bitmaps in project objects
        self.parsed_fonts = self._parseResources('font')
        self.parsed_bitmaps = self._parseResources('bitmap')

        return ( self.parsed_page, self.parsed_bitmaps, self.parsed_fonts)
    
    def parsedPage(self):
        """ return parsed page """
        return self.parsed_page

    def parsedObjects(self):
        """ return all parsed objects in page """
        return ( self.parsed_page['lines'] + \
                 self.parsed_page['labels'] + \
                 self.parsed_page['buttons'] )

    def parsedResourses(self):
        """ return parsed bitmaps and font """
        return ( self.parsed_bitmaps, self.parsed_fonts )
    
    def _parseResources(self, name):
        out_objects = []        
        
        for obj in self.parsedObjects():
            if name in obj and obj[ name ] not in out_objects:
                out_objects.append( obj[ name ] )
        
        return out_objects

    def _parsePage(self, page, propertySet):
        parsed_page = { 'class': 'NGL_Page', 'name': page.attrib['name'] }
        self._parseProperties( page, parsed_page, propertySet )
        return parsed_page

    def _initParsedObject(self, className, obj_name):
        return { 'class': 'NGL_' + className,
                 'name': obj_name,
                 'click': obj_name + '_click' }

    def _parseObjects(self, QObjects, className, propertySet):
        ngl_objects = []

        for obj in QObjects:
            if obj.attrib['class'] == className:

                ngl_obj = self._initParsedObject( className, obj.attrib['name'] )
                self._parseProperties( obj, ngl_obj, propertySet )

                if 'font' not in ngl_obj:               
                    ngl_obj['font'] = {}
                    ngl_obj['font']['family'] = 'MS Shell Dlg 2'
                    ngl_obj['font']['pointsize'] = '8'
                    ngl_obj['font']['bold'] = False
                
                ngl_obj['font']['name'] = NGL_Font.formatName( ngl_obj['font']['family'],
                                                               ngl_obj['font']['pointsize'],
                                                               ngl_obj['font']['bold'] )
                ngl_objects.append( ngl_obj )

        return ngl_objects

    def _parseProperties(self, obj, ngl_obj, out_properties):
        namesParse = {
            'geometry': self._geometry,
            'orientation': self._orientation,
            'styleSheet': self._stylesheet,
            'font': self._font,
            'icon': self._bitmap,
            'iconSize': self._bitmap_size,
            'text': self._text
        }
        for prop in obj.findall('property'):
            if prop.attrib['name'] in out_properties:
                namesParse[ prop.attrib['name'] ](ngl_obj, prop)

    def _geometry(self, obj, prop):
        rect = prop.find('rect')
        obj['x'] = rect.find('x').text
        obj['y'] = rect.find('y').text
        obj['width'] = rect.find('width').text
        obj['height'] = rect.find('height').text

    def _orientation(self, obj, prop):
        """ Parse orientation property for object """
        obj['orientation'] = prop.find('enum').text[4:]

    def _convertColor(self, color_str):
        try:
            i0 = color_str.index('(') + 1
            i1 = color_str.index(')')
            _rgb = [ int(val.strip()) for val in color_str[i0:i1].split(',', 3) ]
        except:
            _rgb = [ 0, 0, 0 ]

        return NColor.fromRGB( _rgb )

    def _stylesheet(self, obj, prop):
        colorLines = prop.find('string').text.split('\n')
        for line in colorLines:
            name = line[ :line.index(':') ].replace('-', '_')
            obj[ name ] = self._convertColor( line )

    def _font(self, obj, prop):
        prop = prop.find('font')
        obj['font'] = self._fontProperties(prop)        

    def _fontProperties(self, prop):
        font = {}

        family = prop.find('family')
        if family != None:
            font['family'] = family.text
        else:
            font['family'] = 'MS Shell Dlg 2'

        pointsize = prop.find('pointsize')
        if pointsize != None:
            font['pointsize'] = pointsize.text
        else:
            font['pointsize'] = '8'

        bold = prop.find('bold')
        if bold == 'true':
            font['bold'] = True
        else:
            font['bold'] = False

        return font

    def _bitmap(self, obj, prop):
        p = prop.find('iconset')
        obj['bitmap'] = {}
        text = p.find('normalon').text.split('/', 2)
        obj['bitmap']['prefix'] = text[1]
        obj['bitmap']['path'] = os.path.abspath(text[2])
        basename = os.path.basename( text[2] )
        obj['bitmap']['name'] = os.path.splitext( basename )[0]

    def _bitmap_size(self, obj, prop):
        p = prop.find('size')
        obj['bitmap']['width'] = p.find('width').text
        obj['bitmap']['height'] = p.find('height').text

    def _text(self, obj, prop):
        if prop.find('string') != None:
            obj['text'] = prop.find('string').text

