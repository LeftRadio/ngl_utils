#!/usr/bin/env python3

import os
import xml.etree.ElementTree as ET
from PyQt5 import uic
from PyQt5.QtCore import Qt
from ngl_utils.nplugins.widgets.ngl_colors import NGL_Colors
from ngl_utils.nplugins.widgets.qstyle_parser import QStyleParser
from ngl_utils.messages import inform


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
        """ Parse Qt ui file provide pyqt uic module
        """
        #
        self.uic = uic.loadUi(self.uifile,
                              package='ngl_utils.nplugins.widgets')

        # parse ngl page
        self.ppage = self._parsePage(self.uic)

        # parse ngl page object
        self.ppage['objects'] = self._parseObjects(self.uic)

        # collect all fonts and bitmaps in project objects
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

    def _qSortedObjects(self):
        """ return objects from pyqt uic module, sorted by QtDesigner order """
        return [obj.objectName() for obj in self.uic.children()]

    def _collectResource(self, name, objects):
        """ collect all Font/Bitmap resources
        """
        resources = []
        for class_key in objects.keys():
            # iterate objects in this objects class
            for obj_key in objects[class_key]:
                # iterate properties
                obj = objects[class_key][obj_key]
                # if nedeed resource in object
                if name in dir(obj):
                    attr = getattr(obj, name)
                    # if attribute is not method
                    if attr.__class__.__name__ not in 'builtin_function_or_method':
                        # if not duplicate resources
                        if attr not in resources:
                            resources.append(attr)

        return resources

    def _parseBitmaps(self, name, uifile):
        """ Parse all bitmaps from ui file used xml.etree parser
        """
        root = self.getroot(uifile)
        paths = []
        bitmaps = {}

        main = root.find('widget')
        for w in main.findall('widget'):
            for p in w.findall('property'):

                if p.attrib['name'] == 'icon':
                    path = p.find('iconset').find('normaloff').text
                    path = os.path.abspath(path)

                    if path not in bitmaps:
                        bitmaps[path] = [w.attrib['name']]
                    else:
                        bitmaps[path].append(w.attrib['name'])

        return bitmaps

    def _parsePage(self, uic_page):
        """ Parse page
        """
        page = {
            'class': 'NGL_Page',
            'name': uic_page.objectName(),
            'width': uic_page.size().width(),
            'height': uic_page.size().height()}

        color = QStyleParser.getColor(uic_page.styleSheet(),
                                      'background-color: rgb')
        page['background_color'] = NGL_Colors.fromQColor(color)

        return page

    def _parseObjects(self, page):
        """ Parse NGL objects for gived page,
            return objects dict, like -
            {'NGL_Label': {dict of ngl labels objects},
             'NGL_Button': {dict of ngl labels objects},
             ...
            }
        """
        # filter NGL objects
        qobjects = [obj for obj in self.uic.children() if 'NGL' in obj.__class__.__name__]

        # parse all objects
        out_objects = {}
        for qobj in qobjects:

            classname = qobj.__class__.__name__
            objectname = qobj.objectName()

            # create dict key if object class type not in out_objects
            if classname not in out_objects:
                out_objects[classname] = {}

            # get object name and use as key, store object
            qobj.orderIndex = self._qSortedObjects().index(qobj.objectName())
            out_objects[classname][objectname] = qobj

        return out_objects
