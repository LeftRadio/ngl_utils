#!/usr/bin/env python3

import os
import xml.etree.ElementTree as ET
from PyQt5 import uic
from PyQt5.QtCore import Qt
from ngl_utils.nbitmap.converter import NColor
from ngl_utils.nplugins.widgets.qstyle_parser import QStyleParser


class UIParser(object):
    """ simple parser for Qt ui files """
    def __init__(self, uifile):
        super(UIParser, self).__init__()
        self._uifile = uifile

    @property
    def uifile(self):
        return self._uifile

    @uifile.setter
    def uifile(self, uifile):
        self._uifile = uifile

    def uiVersion(self):
        try:
            root = self.getroot(self.uifile)
            ver = str(root.attrib['version'])
        except:
            ver = 'undefined... :( '
        return ver

    def getroot(self, xmlfile):
        """ get root for xml file """
        return ET.parse(xmlfile).getroot()

    def parse(self):
        """
        """
        # load ui file provide pyqt uic module
        self.uic = uic.loadUi(self.uifile,
                              package='ngl_utils.nplugins.widgets')

        # parse ngl page
        self.ppage = self._parsePage(self.uic)

        # parse ngl page object
        self.ppage['objects'] = self._parseObjects(self.uic)

        # # collect all fonts and bitmaps in project objects
        self.ppage['fonts'] = self._collectResource('font',
                                                    self.ppage['objects'])
        self.ppage['bitmaps'] = self._parseBitmaps('icon', self.uifile)

        return self.ppage

    def parsedPage(self):
        """ return parsed page """
        return self.ppage

    def getParsedObjects(self):
        """ return all parsed objects in page """
        return self.ppage['objects']

    def getParsedResourses(self):
        """ return parsed bitmaps and font """
        return (self.ppage['bitmaps'], self.ppage['fonts'])

    def _collectResource(self, name, objects):
        # collect all resources
        resources = []
        for class_key in objects.keys():
            # iterate objects in this objects class
            for obj_key in objects[class_key]:
                # iterate properties
                obj = objects[class_key][obj_key]

                # if nedeed resource in object
                if name in dir(obj):
                    attr = getattr(obj, name)
                    # if resource not method
                    if attr.__class__.__name__ not in 'builtin_function_or_method':
                        # if not duplicate resources
                        if attr not in resources:
                            resources.append(attr)

        return resources

    def _parseBitmaps(self, name, uifile):
        root = self.getroot(uifile)
        paths = []
        bitmaps = {}

        for p in root.iter('property'):

            if p.attrib['name'] == 'icon':
                path = p.find('iconset').find('normaloff').text
                path = os.path.abspath(path)

                if path not in paths:
                    paths.append(path)

        for path in paths:
            bitmaps[path] = []

            main = root.find('widget')
            for w in main.findall('widget'):
                for p in w.findall('property'):
                    if p.attrib['name'] == 'icon':
                        bitmaps[path].append(w.attrib['name'])

        return bitmaps

    def _parsePage(self, uic_page):
        page = {
            'class': 'NGL_Page',
            'name': uic_page.objectName(),
            'width': uic_page.size().width(),
            'height': uic_page.size().height()}

        color = QStyleParser.getColor(uic_page.styleSheet(),
                                      'background-color: rgb')
        if color is None:
            color = Qt.black

        page['background_color'] = NColor.fromQColor(color)

        return page

    def _parseObjects(self, page):
        # get page dictionary objects
        pdict = page.__dict__

        # filter NGL objects
        qobjects = [pdict[w] for w in pdict.keys() if 'NGL' in pdict[w].__class__.__name__]

        # create out objects dictionary
        out_objects = {
            'NGL_Line': {},
            'NGL_Rect': {},
            'NGL_Bitmap': {},
            'NGL_Button': {}
        }

        # parse all objects
        for qobj in qobjects:
            name = qobj.__class__.__name__

            # create dict key if object class type not in out_objects
            if name not in out_objects:
                out_objects[name] = {}

            # get object name and use name as tag, store object
            out_objects[name][qobj.objectName()] = qobj

        return out_objects
